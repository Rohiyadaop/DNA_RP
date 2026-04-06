from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from model.service import ResistancePredictionService
from backend.utils.schemas import PredictionRequest, PredictionResponse, UploadFastaResponse


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.prediction_service = ResistancePredictionService(PROJECT_ROOT)
    yield


app = FastAPI(
    title="AI Antibiotic Resistance Prediction API",
    description="Upload FASTA, run structure+docking-aware resistance prediction, and receive JSON output.",
    version="1.0.0",
    lifespan=lifespan,
)


def get_service() -> ResistancePredictionService:
    service = getattr(app.state, "prediction_service", None)
    if service is None:
        service = ResistancePredictionService(PROJECT_ROOT)
        app.state.prediction_service = service
    return service

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root() -> dict:
    return {
        "message": "Context-Aware Antibiotic Resistance Prediction API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/upload-fasta", response_model=UploadFastaResponse)
async def upload_fasta(file: UploadFile = File(...)) -> UploadFastaResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing FASTA file name.")

    try:
        contents = await file.read()
        result = get_service().store_fasta(file.filename, contents)
        return UploadFastaResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest) -> PredictionResponse:
    try:
        result = get_service().predict(
            upload_id=request.upload_id,
            smiles=request.smiles,
            temperature=request.temperature,
            ph=request.ph,
            medium=request.medium,
        )
        return PredictionResponse(**result)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
