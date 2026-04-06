from __future__ import annotations

import math
import os
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import quote

import httpx
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors


HTTP_TIMEOUT = 90.0


def _auth_headers(api_key: str | None) -> Dict[str, str]:
    if not api_key:
        return {}
    return {"Authorization": f"Bearer {api_key}"}


def build_mock_pdb(protein_sequence: str, chain_id: str = "A") -> str:
    lines: List[str] = []
    for index, amino_acid in enumerate(protein_sequence[:220], start=1):
        angle = index * 1.8
        x_coord = 6.0 * math.cos(angle)
        y_coord = 6.0 * math.sin(angle)
        z_coord = index * 1.5
        residue_name = amino_acid if len(amino_acid) == 3 else "GLY"
        lines.append(
            f"ATOM  {index:5d}  CA  GLY {chain_id}{index:4d}    "
            f"{x_coord:8.3f}{y_coord:8.3f}{z_coord:8.3f}  1.00 50.00           C"
        )
    lines.append("END")
    return "\n".join(lines) + "\n"


def generate_rdkit_sdf(smiles: str) -> str:
    molecule = Chem.MolFromSmiles(smiles)
    if molecule is None:
        raise ValueError("Invalid SMILES input.")
    molecule = Chem.AddHs(molecule)
    AllChem.EmbedMolecule(molecule, randomSeed=42)
    AllChem.UFFOptimizeMolecule(molecule, maxIters=200)
    return Chem.MolToMolBlock(molecule)


def predict_structure_with_esmfold(protein_sequence: str) -> Dict[str, Any]:
    endpoint = os.getenv("ESMFOLD_API_URL")
    api_key = os.getenv("ESMFOLD_API_KEY")
    inferred_message = (
        "BioNeMo/ESMFold endpoint is deployment-specific, so this client expects the full URL in "
        "ESMFOLD_API_URL and falls back locally if unavailable."
    )

    if endpoint:
        try:
            with httpx.Client(timeout=HTTP_TIMEOUT, headers=_auth_headers(api_key)) as client:
                response = client.post(endpoint, json={"sequence": protein_sequence})
                response.raise_for_status()

            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                payload = response.json()
                pdb_text = (
                    payload.get("pdb")
                    or payload.get("pdb_text")
                    or payload.get("structure")
                    or payload.get("output_pdb")
                )
                if pdb_text:
                    return {
                        "pdb_text": pdb_text,
                        "source": "esmfold_api",
                        "used_mock": False,
                        "note": "Live ESMFold-compatible response used.",
                    }
            else:
                text = response.text.strip()
                if text.startswith("ATOM") or text.startswith("HEADER"):
                    return {
                        "pdb_text": text,
                        "source": "esmfold_api",
                        "used_mock": False,
                        "note": "Live ESMFold-compatible PDB used.",
                    }
        except Exception as exc:
            return {
                "pdb_text": build_mock_pdb(protein_sequence),
                "source": "mock_structure",
                "used_mock": True,
                "note": f"Structure API failed, using local mock PDB. Reason: {exc}",
            }

    return {
        "pdb_text": build_mock_pdb(protein_sequence),
        "source": "mock_structure",
        "used_mock": True,
        "note": inferred_message,
    }


def fetch_pubchem_sdf(smiles: str) -> Dict[str, Any]:
    cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{quote(smiles, safe='')}/cids/JSON"
    try:
        with httpx.Client(timeout=HTTP_TIMEOUT) as client:
            cid_response = client.get(cid_url)
            cid_response.raise_for_status()
            cid_payload = cid_response.json()
            cid_list = cid_payload["IdentifierList"]["CID"]
            cid = cid_list[0]
            sdf_url = (
                f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/record/SDF/?record_type=3d"
            )
            sdf_response = client.get(sdf_url)
            sdf_response.raise_for_status()
        return {
            "cid": cid,
            "sdf_text": sdf_response.text,
            "source": "pubchem",
            "note": "Ligand fetched from PubChem PUG REST.",
        }
    except Exception as exc:
        return {
            "cid": None,
            "sdf_text": generate_rdkit_sdf(smiles),
            "source": "rdkit_fallback",
            "note": f"PubChem fetch failed, using RDKit-generated SDF. Reason: {exc}",
        }


def _pick_float(payload: Dict[str, Any], keys: List[str], default: float) -> float:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return default


def simulate_local_docking(
    protein_sequence: str,
    smiles: str,
    gene: str,
    mutation_count: int,
    structure_features: np.ndarray,
    env_vector: np.ndarray,
) -> Dict[str, Any]:
    molecule = Chem.MolFromSmiles(smiles)
    if molecule is None:
        raise ValueError("Invalid SMILES input.")

    logp = float(Descriptors.MolLogP(molecule))
    tpsa = float(Descriptors.TPSA(molecule))
    heavy_atoms = float(molecule.GetNumHeavyAtoms())
    gene_bonus = {"gyrA": 1.0, "parC": 0.8, "blaTEM": 0.9, "tetA": 0.75}.get(gene, 0.55)
    structure_signal = float(structure_features[0] + structure_features[4] + structure_features[6])
    env_signal = float(env_vector[0] + env_vector[1] + np.max(env_vector[2:]))

    affinity_strength = 0.9 + 0.18 * logp + 0.012 * tpsa + 0.02 * heavy_atoms
    affinity_strength += 0.65 * gene_bonus + 0.35 * structure_signal + 0.16 * mutation_count + 0.14 * env_signal
    binding_score = round(-3.8 - affinity_strength, 2)

    confidence_raw = -0.3 + 0.24 * structure_signal + 0.20 * gene_bonus + 0.09 * mutation_count + 0.06 * env_signal
    docking_confidence = round(float(1.0 / (1.0 + math.exp(-confidence_raw))), 4)
    pose_preview = f"{gene}-pose::{molecule.GetNumAtoms()}atoms::{len(protein_sequence)}aa"

    return {
        "binding_score": binding_score,
        "docking_confidence": docking_confidence,
        "binding_pose_preview": pose_preview,
        "source": "mock_diffdock",
        "used_mock": True,
        "note": "Local docking heuristic used because DiffDock API was unavailable.",
    }


def run_diffdock_docking(
    protein_pdb_text: str,
    protein_sequence: str,
    sdf_text: str,
    smiles: str,
    gene: str,
    mutation_count: int,
    structure_features: np.ndarray,
    env_vector: np.ndarray,
) -> Dict[str, Any]:
    endpoint = os.getenv("DIFFDOCK_API_URL")
    api_key = os.getenv("DIFFDOCK_API_KEY")

    if endpoint:
        try:
            files = {
                "protein_file": ("protein.pdb", protein_pdb_text, "chemical/x-pdb"),
                "ligand_file": ("ligand.sdf", sdf_text, "chemical/x-mdl-sdfile"),
            }
            data = {"metadata": f"gene={gene}"}
            with httpx.Client(timeout=HTTP_TIMEOUT, headers=_auth_headers(api_key)) as client:
                response = client.post(endpoint, files=files, data=data)
                response.raise_for_status()
                payload = response.json()

            return {
                "binding_score": _pick_float(payload, ["binding_score", "affinity", "score"], -6.0),
                "docking_confidence": _pick_float(payload, ["confidence", "confidence_score"], 0.8),
                "binding_pose_preview": str(
                    payload.get("binding_pose")
                    or payload.get("pose")
                    or payload.get("pose_id")
                    or "live_pose"
                )[:220],
                "source": "diffdock_api",
                "used_mock": False,
                "note": "Live DiffDock-compatible response used.",
            }
        except Exception as exc:
            local = simulate_local_docking(
                protein_sequence=protein_sequence,
                smiles=smiles,
                gene=gene,
                mutation_count=mutation_count,
                structure_features=structure_features,
                env_vector=env_vector,
            )
            local["note"] = f"DiffDock API failed, using local docking fallback. Reason: {exc}"
            return local

    return simulate_local_docking(
        protein_sequence=protein_sequence,
        smiles=smiles,
        gene=gene,
        mutation_count=mutation_count,
        structure_features=structure_features,
        env_vector=env_vector,
    )


def save_text_artifact(target_path: Path, contents: str) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(contents, encoding="utf-8")
