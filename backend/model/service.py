from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from backend.model.ai_pipeline import (
    build_sequence_context,
    load_reference_bundle,
    predict_resistance,
    train_or_load_model,
)
from backend.utils.fasta_utils import gc_content, parse_fasta_contents, to_fasta_text


class ResistancePredictionService:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.upload_dir = self.project_root / "backend" / "uploads"
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.reference_bundle = load_reference_bundle(self.project_root)
        train_or_load_model(self.project_root)

    def store_fasta(self, file_name: str, contents: bytes) -> dict:
        sequence_id, sequence = parse_fasta_contents(contents)
        upload_id = uuid4().hex
        fasta_path = self.upload_dir / f"{upload_id}.fasta"
        meta_path = self.upload_dir / f"{upload_id}.json"

        fasta_path.write_text(to_fasta_text(sequence_id, sequence), encoding="utf-8")
        context = build_sequence_context(
            base_dir=self.project_root,
            sequence=sequence,
            reference_bundle=self.reference_bundle,
        )
        metadata = {
            "upload_id": upload_id,
            "file_name": file_name,
            "sequence_id": sequence_id,
            "sequence_length": len(sequence),
            "gc_content": gc_content(sequence),
            "primary_gene": context["primary_gene"],
            "protein_length": context["protein_length"],
            "protein_sequence_preview": context["protein_sequence_preview"],
            "mapped_genes": context["mapped_genes"],
            "mutations": context["mutations"],
            "translated_protein_preview": context["translated_protein_preview"],
            "structure_features": context["structure_features"],
        }
        meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        return metadata

    def load_upload(self, upload_id: str) -> dict:
        fasta_path = self.upload_dir / f"{upload_id}.fasta"
        meta_path = self.upload_dir / f"{upload_id}.json"
        if not fasta_path.exists() or not meta_path.exists():
            raise FileNotFoundError("Upload ID not found. Please upload the FASTA file again.")

        metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        fasta_lines = fasta_path.read_text(encoding="utf-8").splitlines()
        metadata["sequence"] = "".join(line.strip() for line in fasta_lines if not line.startswith(">"))
        return metadata

    def predict(self, upload_id: str, smiles: str, temperature: float, ph: float, medium: str) -> dict:
        upload = self.load_upload(upload_id)
        result = predict_resistance(
            base_dir=self.project_root,
            sequence=upload["sequence"],
            smiles=smiles,
            temperature=temperature,
            ph=ph,
            medium=medium,
        )
        
        # Store PDB data for visualization
        structure_path = self.upload_dir / f"{upload_id}_structure.pdb"
        docking_path = self.upload_dir / f"{upload_id}_docking.pdb"
        structure_path.write_text(result["protein_pdb"], encoding="utf-8")
        docking_path.write_text(result["docked_complex_pdb"], encoding="utf-8")
        
        return {
            "prediction": result["prediction"],
            "confidence": result["confidence"],
            "upload_id": upload_id,
            "gene": result["gene"],
            "sequence_length": result["sequence_length"],
            "protein_length": result["protein_length"],
            "mapped_genes": result["mapped_genes"],
            "mutations": result["mutations"],
            "translated_protein_preview": result["translated_protein_preview"],
            "structure_features": result["structure_features"],
            "structure_source": result["structure_source"],
            "ligand_source": result["ligand_source"],
            "docking_source": result["docking_source"],
            "binding_score": result["binding_score"],
            "docking_confidence": result["docking_confidence"],
            "binding_pose_preview": result["binding_pose_preview"],
            "probability_breakdown": result["probability_breakdown"],
            "message": result["message"],
            "protein_pdb": result["protein_pdb"],
            "docked_complex_pdb": result["docked_complex_pdb"],
        }

    def get_structure_pdb(self, upload_id: str) -> str:
        structure_path = self.upload_dir / f"{upload_id}_structure.pdb"
        if not structure_path.exists():
            raise FileNotFoundError(f"Structure PDB not found for upload ID: {upload_id}")
        return structure_path.read_text(encoding="utf-8")

    def get_docking_pdb(self, upload_id: str) -> str:
        docking_path = self.upload_dir / f"{upload_id}_docking.pdb"
        if not docking_path.exists():
            raise FileNotFoundError(f"Docking PDB not found for upload ID: {upload_id}")
        return docking_path.read_text(encoding="utf-8")
