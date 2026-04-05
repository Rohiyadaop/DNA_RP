import hashlib
import json
import os
import re
from typing import Literal

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

# Import DNA Predictor routes
from dna_predictor_routes import router as dna_predictor_router

load_dotenv()

app = FastAPI(
    title="BioGPT Evo2 + DNA Mutation Resistance Predictor API",
    description=(
        "Generate DNA sequences with NVIDIA Evo2 and run a lightweight "
        "DNA mutation resistance prediction pipeline with scientific explanations."
    ),
    version="1.0.0",
)

DEFAULT_EVO2_URL = "https://health.api.nvidia.com/v1/biology/arc/evo2-40b/generate"
DEFAULT_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000"
DNA_PATTERN = re.compile(r"^[ATGC]+$")
BASE_MAP = ("A", "C", "G", "T")
MOTIF_HINTS = {
    "promoter": "TATAAT",
    "gc-rich": "GCGCGC",
    "stable": "GCGCGC",
    "at-rich": "ATATAT",
    "flexible": "ATATAT",
    "bacteria": "AGGAGG",
    "ribosome": "AGGAGG",
    "human": "GCCACC",
    "kozak": "GCCACC",
    "yeast": "TATAAA",
    "palindrome": "GAATTC",
    "start codon": "ATG",
    "stop codon": "TAA",
}


def get_allowed_origins() -> list[str]:
    raw = os.getenv("FRONTEND_URLS", DEFAULT_ORIGINS)
    origins = [value.strip() for value in raw.split(",") if value.strip()]
    return origins or DEFAULT_ORIGINS.split(",")


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    input: str = Field(..., min_length=2, max_length=5000)
    input_type: Literal["dna", "prompt"] = "dna"
    num_tokens: int = Field(default=120, ge=16, le=1024)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_k: int = Field(default=4, ge=1, le=6)
    top_p: float = Field(default=0.0, ge=0.0, le=1.0)
    random_seed: int | None = Field(default=None, ge=0, le=2_147_483_647)

    @field_validator("input")
    @classmethod
    def clean_input(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Input cannot be empty.")
        return cleaned


class GenerateResponse(BaseModel):
    generated_sequence: str
    submitted_sequence: str
    input_type: Literal["dna", "prompt"]
    upstream_elapsed_ms: int | None = None
    model_endpoint: str


def parse_fasta_or_plain_dna(raw_input: str) -> str:
    lines = [line.strip() for line in raw_input.splitlines() if line.strip()]
    filtered = [line for line in lines if not line.startswith(">")]
    normalized = "".join(filtered).replace(" ", "").upper()
    if not normalized:
        raise HTTPException(status_code=422, detail="No DNA content was found in the provided input.")
    if not DNA_PATTERN.fullmatch(normalized):
        raise HTTPException(
            status_code=422,
            detail="DNA input must contain only A, T, G, and C characters.",
        )
    return normalized


def bytes_to_dna(text: str) -> str:
    dna: list[str] = []
    for byte in text.encode("utf-8"):
        for shift in (6, 4, 2, 0):
            dna.append(BASE_MAP[(byte >> shift) & 0b11])
    return "".join(dna)


def keyword_motifs(prompt: str) -> str:
    lowered = prompt.lower()
    motifs = [sequence for keyword, sequence in MOTIF_HINTS.items() if keyword in lowered]
    return "".join(motifs)


def ensure_seed_length(sequence: str, minimum: int = 48, maximum: int = 640) -> str:
    if len(sequence) < minimum:
        repeat_count = (minimum // max(1, len(sequence))) + 1
        sequence = (sequence * repeat_count)[:minimum]
    return sequence[:maximum]


def prompt_to_dna_seed(prompt: str) -> str:
    compact_prompt = " ".join(prompt.lower().split())
    motif_prefix = keyword_motifs(compact_prompt)
    semantic_seed = bytes_to_dna(compact_prompt)
    digest_seed = bytes_to_dna(hashlib.sha256(compact_prompt.encode("utf-8")).hexdigest())
    combined = f"{motif_prefix}ATG{semantic_seed}{digest_seed}TAA"
    return ensure_seed_length(combined)


def sanitize_generated_sequence(sequence: str) -> str:
    normalized = re.sub(r"[^ATGC]", "", sequence.upper())
    if not normalized:
        raise HTTPException(
            status_code=502,
            detail="NVIDIA Evo2 returned an empty DNA sequence.",
        )
    return normalized


def build_nvidia_headers() -> dict[str, str]:
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="NVIDIA_API_KEY is missing. Add it to backend/.env before starting the API.",
        )
    return {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def get_evo2_url() -> str:
    return os.getenv("NVIDIA_EVO2_URL", DEFAULT_EVO2_URL)


def get_timeout_seconds() -> float:
    value = os.getenv("REQUEST_TIMEOUT_SECONDS", "60")
    try:
        return float(value)
    except ValueError:
        return 60.0


def upstream_error_message(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.text.strip() or "Unknown NVIDIA API error."

    if isinstance(payload, dict):
        for key in ("detail", "message", "error"):
            if key in payload:
                value = payload[key]
                return value if isinstance(value, str) else json.dumps(value)
        return json.dumps(payload)

    return str(payload)


async def invoke_evo2(payload: dict[str, object]) -> dict[str, object]:
    try:
        async with httpx.AsyncClient(timeout=get_timeout_seconds()) as client:
            response = await client.post(
                get_evo2_url(),
                headers=build_nvidia_headers(),
                json=payload,
            )
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="The request to NVIDIA Evo2 timed out. Try again with fewer tokens.",
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to reach NVIDIA Evo2: {exc}",
        ) from exc

    if response.is_error:
        raise HTTPException(
            status_code=502,
            detail=upstream_error_message(response),
        )

    try:
        return response.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail="NVIDIA Evo2 returned a non-JSON response.",
        ) from exc


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "service": "BioGPT Evo2 + DNA Mutation Resistance Predictor API",
        "status": "ok",
        "generate_endpoint": "/generate",
        "health_endpoint": "/health",
        "dna_predictor": "/api/dna-predictor",
    }

# Include DNA Predictor routes
app.include_router(dna_predictor_router)


@app.get("/health")
async def health() -> dict[str, object]:
    return {
        "status": "ok",
        "model_endpoint": get_evo2_url(),
        "nvidia_key_configured": bool(os.getenv("NVIDIA_API_KEY")),
        "evo2_reasoning_url_configured": bool(os.getenv("EVO2_REASONING_URL")),
        "predictor_ready": True,
    }


@app.post("/generate", response_model=GenerateResponse)
async def generate_sequence(request: GenerateRequest) -> GenerateResponse:
    submitted_sequence = (
        parse_fasta_or_plain_dna(request.input)
        if request.input_type == "dna"
        else prompt_to_dna_seed(request.input)
    )

    evo2_payload = {
        "sequence": submitted_sequence,
        "num_tokens": request.num_tokens,
        "temperature": request.temperature,
        "top_k": request.top_k,
        "top_p": request.top_p,
    }

    if request.random_seed is not None:
        evo2_payload["random_seed"] = request.random_seed

    upstream_data = await invoke_evo2(evo2_payload)
    generated_sequence = sanitize_generated_sequence(str(upstream_data.get("sequence", "")))

    return GenerateResponse(
        generated_sequence=generated_sequence,
        submitted_sequence=submitted_sequence,
        input_type=request.input_type,
        upstream_elapsed_ms=upstream_data.get("elapsed_ms"),
        model_endpoint=get_evo2_url(),
    )
