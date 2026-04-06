from __future__ import annotations

from typing import Dict, List, Literal

from pydantic import BaseModel, Field


MediumType = Literal["LB", "MHB", "Minimal", "Blood"]


class UploadFastaResponse(BaseModel):
    upload_id: str
    file_name: str
    sequence_id: str
    sequence_length: int
    gc_content: float
    primary_gene: str
    protein_length: int
    protein_sequence_preview: str
    mapped_genes: List[str]
    mutations: List[str]
    translated_protein_preview: Dict[str, str]
    structure_features: List[float]


class PredictionRequest(BaseModel):
    upload_id: str = Field(..., description="Upload identifier returned by /upload-fasta")
    smiles: str = Field(..., min_length=3, description="Antibiotic SMILES string")
    temperature: float = Field(..., ge=20.0, le=50.0)
    ph: float = Field(..., ge=3.0, le=10.0)
    medium: MediumType


class PredictionResponse(BaseModel):
    prediction: str
    confidence: float
    upload_id: str
    gene: str
    sequence_length: int
    protein_length: int
    mapped_genes: List[str]
    mutations: List[str]
    translated_protein_preview: Dict[str, str]
    structure_features: List[float]
    structure_source: str
    ligand_source: str
    docking_source: str
    binding_score: float
    docking_confidence: float
    binding_pose_preview: str
    probability_breakdown: Dict[str, float]
    message: str
