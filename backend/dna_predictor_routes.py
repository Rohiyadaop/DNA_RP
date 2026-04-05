"""
API routes for the DNA Mutation Resistance Predictor.
"""
from __future__ import annotations

import os
from typing import Literal

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from ml_models.resistance_predictor import (
    GENE_LIBRARY,
    get_known_mutation_catalog,
    get_model,
)

router = APIRouter(prefix="/api/dna-predictor", tags=["DNA Mutation Resistance Predictor"])


class PredictionRequest(BaseModel):
    input: str = Field(..., min_length=3, max_length=6000)
    input_type: Literal["mutation", "sequence"] = "mutation"

    @field_validator("input")
    @classmethod
    def clean_input(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Input cannot be empty.")
        return cleaned


class GeneInfo(BaseModel):
    gene: str
    protein: str
    antibiotic_class: str
    mechanism: str


class EncodingSummary(BaseModel):
    strategy: str
    input_length: int
    gc_content: float
    top_kmers: list[str]
    detected_markers: list[str]
    vector_dimensions: int


class PipelineStep(BaseModel):
    name: str
    detail: str


class VisualizationSummary(BaseModel):
    helix_length: int
    highlight_positions: list[int]
    focus_label: str
    prediction_tone: str


class PredictionResponse(BaseModel):
    resistant: bool
    prediction: str
    confidence: float
    probability_resistant: float
    probability_not_resistant: float
    input_type: str
    normalized_input: str
    model_name: str
    reasoning_source: str
    explanation: str
    mutation_label: str | None = None
    gene_info: GeneInfo | None = None
    scientific_rationale: list[str]
    encoding: EncodingSummary
    pipeline: list[PipelineStep]
    visualization: VisualizationSummary


def build_fallback_explanation(analysis: dict[str, object]) -> str:
    gene_info = analysis.get("gene_info") or {}
    prediction = str(analysis["prediction"])
    resistant_probability = float(analysis["probability_resistant"])
    confidence = float(analysis["confidence"])
    mutation_label = analysis.get("mutation_label")
    encoding = analysis.get("encoding") or {}
    markers = encoding.get("detected_markers") or []
    top_kmers = encoding.get("top_kmers") or []

    if gene_info and mutation_label:
        if analysis["resistant"]:
            lead = (
                f"{gene_info['gene']} {mutation_label} is predicted to be antibiotic resistant because "
                f"it likely {gene_info['mechanism']}."
            )
        else:
            lead = (
                f"{gene_info['gene']} {mutation_label} is predicted as not resistant because the substitution "
                "does not produce a dominant high-risk signature in this prototype model."
            )
    else:
        if analysis["resistant"]:
            lead = (
                "The submitted DNA sequence contains resistance-like molecular signatures, suggesting the bacterium "
                "could tolerate the antibiotic more effectively."
            )
        else:
            lead = (
                "The submitted DNA sequence stays closer to lower-risk reference patterns, so the model does not flag "
                "a strong resistance phenotype."
            )

    evidence = (
        f"The classifier assigned resistant probability {resistant_probability:.2f} "
        f"with confidence {confidence:.2f}."
    )

    if markers:
        evidence += f" Key evidence markers included {', '.join(markers[:3])}."
    elif top_kmers:
        evidence += f" Dominant encoded signatures were {', '.join(top_kmers[:3])}."

    return f"{lead} {evidence}"


async def generate_evo2_explanation(analysis: dict[str, object]) -> tuple[str, str]:
    """
    Optional external reasoning hook.

    If EVO2_REASONING_URL is configured, the prototype will try to call it.
    Otherwise it falls back to a local scientific reasoning template so the
    app remains fully runnable offline.
    """
    fallback = build_fallback_explanation(analysis)
    reasoning_url = os.getenv("EVO2_REASONING_URL", "").strip()
    reasoning_api_key = (
        os.getenv("EVO2_REASONING_API_KEY", "").strip()
        or os.getenv("NVIDIA_API_KEY", "").strip()
    )

    if not reasoning_url or not reasoning_api_key:
        return fallback, "Local reasoning fallback"

    prompt_payload = {
        "task": "antibiotic_resistance_reasoning",
        "input": analysis["normalized_input"],
        "input_type": analysis["input_type"],
        "prediction": analysis["prediction"],
        "confidence": analysis["confidence"],
        "probability_resistant": analysis["probability_resistant"],
        "gene_info": analysis.get("gene_info"),
        "scientific_rationale": analysis["scientific_rationale"],
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                reasoning_url,
                headers={
                    "Authorization": f"Bearer {reasoning_api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                json=prompt_payload,
            )
    except httpx.RequestError:
        return fallback, "Local reasoning fallback"

    if response.is_error:
        return fallback, "Local reasoning fallback"

    try:
        payload = response.json()
    except ValueError:
        return fallback, "Local reasoning fallback"

    explanation = ""
    if isinstance(payload, dict):
        for key in ("explanation", "output", "text", "message"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                explanation = value.strip()
                break

    if not explanation:
        return fallback, "Local reasoning fallback"

    return explanation, "Evo 2 API"


@router.post("/predict", response_model=PredictionResponse)
async def predict_resistance(request: PredictionRequest) -> PredictionResponse:
    try:
        analysis = get_model().predict(request.input, request.input_type)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction error: {exc}") from exc

    explanation, reasoning_source = await generate_evo2_explanation(analysis)

    return PredictionResponse(
        resistant=analysis["resistant"],
        prediction=analysis["prediction"],
        confidence=analysis["confidence"],
        probability_resistant=analysis["probability_resistant"],
        probability_not_resistant=analysis["probability_not_resistant"],
        input_type=analysis["input_type"],
        normalized_input=analysis["normalized_input"],
        model_name=analysis["model_name"],
        reasoning_source=reasoning_source,
        explanation=explanation,
        mutation_label=analysis["mutation_label"],
        gene_info=analysis["gene_info"],
        scientific_rationale=analysis["scientific_rationale"],
        encoding=analysis["encoding"],
        pipeline=analysis["pipeline"],
        visualization=analysis["visualization"],
    )


@router.get("/mutations/known")
async def get_known_mutations() -> dict[str, list[dict[str, object]]]:
    return {"mutations": get_known_mutation_catalog()}


@router.get("/genes/info")
async def get_gene_info() -> dict[str, dict[str, object]]:
    return {
        info["display_gene"]: {
            "protein": info["protein"],
            "antibiotic_class": info["antibiotic_class"],
            "mechanism": info["mechanism"],
            "hotspots": info["hotspots"],
        }
        for info in GENE_LIBRARY.values()
    }
