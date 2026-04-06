from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import joblib
import numpy as np
import pandas as pd
from Bio.Seq import Seq
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import GroupShuffleSplit

from backend.model.external_clients import fetch_pubchem_sdf, predict_structure_with_esmfold, run_diffdock_docking
from backend.utils.fasta_utils import longest_protein_from_dna
from run_pipeline import (
    DRUG_LIBRARY,
    GENE_DEFINITIONS,
    GENE_PRESENCE_THRESHOLD,
    LABELS,
    RANDOM_SEED,
    build_gene_kmer_sets,
    detect_mutations,
    dna_kmer_vector,
    environmental_vector,
    generate_dataset,
    generate_reference_assets,
    map_genes_to_card,
    mutation_vector,
    simulate_interaction_feature,
    smiles_to_fingerprint,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = PROJECT_ROOT / "backend" / "model" / "artifacts"
MODEL_FILE = ARTIFACT_DIR / "structure_docking_model.joblib"
METRICS_FILE = ARTIFACT_DIR / "training_metrics.json"
CONFUSION_MATRIX_FILE = ARTIFACT_DIR / "confusion_matrix.csv"
FEATURE_MANIFEST_FILE = ARTIFACT_DIR / "feature_manifest.csv"
CLASS_REPORT_FILE = ARTIFACT_DIR / "classification_report.json"
SAMPLE_PREDICTIONS_FILE = ARTIFACT_DIR / "sample_predictions.csv"

HYDROPHOBIC = set("AILMFWVYV")
POLAR = set("STNQCY")
POSITIVE = set("KRH")
NEGATIVE = set("DE")
AROMATIC = set("FWY")
FLEXIBLE = set("GPSND")
GENE_PRIORITY = ["gyrA", "parC", "blaTEM", "tetA"]


def load_reference_bundle(base_dir: Path) -> Dict[str, Any]:
    reference_genes, coordinates, _ = generate_reference_assets(base_dir)
    return {
        "reference_genes": reference_genes,
        "coordinates": coordinates,
        "gene_kmers": build_gene_kmer_sets(reference_genes),
    }


def residue_fraction(sequence: str, residues: set[str]) -> float:
    if not sequence:
        return 0.0
    return sum(1 for amino_acid in sequence if amino_acid in residues) / len(sequence)


def protein_structure_vector(proteins: Dict[str, str], primary_protein: str) -> np.ndarray:
    sequence = primary_protein or "".join(proteins.values())
    if not sequence:
        return np.zeros(8, dtype=float)

    return np.array(
        [
            residue_fraction(sequence, HYDROPHOBIC),
            residue_fraction(sequence, POLAR),
            residue_fraction(sequence, POSITIVE),
            residue_fraction(sequence, NEGATIVE),
            residue_fraction(sequence, AROMATIC),
            residue_fraction(sequence, FLEXIBLE),
            float(len(sequence) / 140.0),
            float(max(1, len(proteins)) / max(1, len(GENE_DEFINITIONS))),
        ],
        dtype=float,
    )


def protein_preview(sequence: str, width: int = 32) -> str:
    if len(sequence) <= width:
        return sequence
    return f"{sequence[:width]}..."


def infer_drug_class(smiles: str) -> str:
    input_fp = smiles_to_fingerprint(smiles)
    best_score = -1.0
    best_class = DRUG_LIBRARY[0]["drug_class"]
    for drug in DRUG_LIBRARY:
        score = float(np.mean(input_fp == smiles_to_fingerprint(drug["smiles"])))
        if score > best_score:
            best_score = score
            best_class = str(drug["drug_class"])
    return best_class


def translate_detected_genes(
    sequence: str,
    coordinates: Dict[str, tuple[int, int]],
    gene_scores: Dict[str, float],
) -> Dict[str, str]:
    proteins: Dict[str, str] = {}
    for gene_name in GENE_DEFINITIONS:
        if gene_scores[gene_name] < GENE_PRESENCE_THRESHOLD:
            continue
        start, end = coordinates[gene_name]
        protein = str(Seq(sequence[start:end]).translate())
        cleaned = protein.split("*")[0].strip().replace("*", "")
        if len(cleaned) >= 15:
            proteins[gene_name] = cleaned
    return proteins


def select_primary_gene(mutations: List[str], proteins: Dict[str, str]) -> str:
    for gene_name in GENE_PRIORITY:
        if any(mutation.startswith(f"{gene_name}_") for mutation in mutations):
            return gene_name
    for gene_name in GENE_PRIORITY:
        if gene_name in proteins:
            return gene_name
    return next(iter(proteins), "unknown")


def build_sequence_context(
    base_dir: Path,
    sequence: str,
    reference_bundle: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    if reference_bundle is None:
        reference_bundle = load_reference_bundle(base_dir)

    gene_scores = map_genes_to_card(sequence, reference_bundle["gene_kmers"])
    mutations = detect_mutations(
        sequence=sequence,
        reference_genes=reference_bundle["reference_genes"],
        coordinates=reference_bundle["coordinates"],
        gene_scores=gene_scores,
    )
    proteins = translate_detected_genes(sequence, reference_bundle["coordinates"], gene_scores)
    primary_gene = select_primary_gene(mutations, proteins)
    primary_protein = proteins.get(primary_gene) or longest_protein_from_dna(sequence)
    structure_features = protein_structure_vector(proteins, primary_protein)

    return {
        "sequence": sequence,
        "sequence_length": len(sequence),
        "gene_scores": gene_scores,
        "mutations": mutations,
        "proteins": proteins,
        "mapped_genes": list(proteins.keys()),
        "primary_gene": primary_gene,
        "primary_protein": primary_protein,
        "protein_length": len(primary_protein),
        "protein_sequence_preview": protein_preview(primary_protein),
        "translated_protein_preview": {gene: protein_preview(value) for gene, value in proteins.items()},
        "structure_features": [round(float(value), 4) for value in structure_features],
        "structure_vector": structure_features,
        "dna_vector": dna_kmer_vector(sequence),
        "mutation_vector": mutation_vector(mutations, gene_scores),
    }


def normalize_binding_score(binding_score: float) -> float:
    normalized = (-binding_score - 3.0) / 7.0
    return float(np.clip(normalized, 0.0, 1.0))


def simulate_training_binding(
    context: Dict[str, Any],
    smiles: str,
    temperature: float,
    ph: float,
    medium: str,
    drug_class: str,
) -> Dict[str, float]:
    env_vector = environmental_vector(temperature, ph, medium)
    interaction = simulate_interaction_feature(
        gene_scores=context["gene_scores"],
        mutations=context["mutations"],
        smiles=smiles,
        drug_class=drug_class,
        temperature=temperature,
        ph=ph,
        medium=medium,
    )
    mutation_bonus = 0.3 * len(context["mutations"])
    structure_bonus = 0.8 * float(context["structure_vector"][0] + context["structure_vector"][4])
    gene_bonus = {"gyrA": 1.0, "parC": 0.8, "blaTEM": 0.9, "tetA": 0.75}.get(context["primary_gene"], 0.55)
    binding_score = round(-4.1 - 3.3 * interaction - 0.25 * mutation_bonus - 0.2 * structure_bonus - 0.35 * gene_bonus, 2)
    docking_confidence = round(float(np.clip(0.38 + 0.48 * interaction + 0.04 * len(context["mutations"]), 0.05, 0.99)), 4)
    return {"binding_score": binding_score, "docking_confidence": docking_confidence, "interaction_proxy": interaction, "env_vector": env_vector}


def fuse_feature_blocks(
    dna_vector_values: np.ndarray,
    mutation_vector_values: np.ndarray,
    structure_vector_values: np.ndarray,
    drug_vector_values: np.ndarray,
    env_vector_values: np.ndarray,
    binding_strength: float,
    docking_confidence: float,
    interaction_proxy: float,
) -> np.ndarray:
    return np.concatenate(
        [
            dna_vector_values,
            mutation_vector_values,
            structure_vector_values,
            drug_vector_values,
            env_vector_values,
            np.array([binding_strength, docking_confidence, interaction_proxy], dtype=float),
        ]
    )


def build_training_matrix(base_dir: Path, metadata: pd.DataFrame) -> tuple[np.ndarray, pd.DataFrame]:
    reference_bundle = load_reference_bundle(base_dir)
    isolate_cache: Dict[str, Dict[str, Any]] = {}
    feature_rows: List[Dict[str, Any]] = []
    feature_matrix: List[np.ndarray] = []

    for isolate_id, isolate_rows in metadata.groupby("isolate_id"):
        fasta_path = base_dir / isolate_rows.iloc[0]["fasta_path"]
        lines = fasta_path.read_text(encoding="utf-8").splitlines()
        sequence = "".join(line.strip() for line in lines if not line.startswith(">"))
        isolate_cache[isolate_id] = build_sequence_context(base_dir, sequence, reference_bundle=reference_bundle)

    for row in metadata.itertuples(index=False):
        context = isolate_cache[row.isolate_id]
        docking_bundle = simulate_training_binding(
            context=context,
            smiles=row.smiles,
            temperature=row.temperature_c,
            ph=row.ph,
            medium=row.medium,
            drug_class=row.drug_class,
        )
        drug_vector = smiles_to_fingerprint(row.smiles)
        fused = fuse_feature_blocks(
            dna_vector_values=context["dna_vector"],
            mutation_vector_values=context["mutation_vector"],
            structure_vector_values=context["structure_vector"],
            drug_vector_values=drug_vector,
            env_vector_values=docking_bundle["env_vector"],
            binding_strength=normalize_binding_score(docking_bundle["binding_score"]),
            docking_confidence=docking_bundle["docking_confidence"],
            interaction_proxy=docking_bundle["interaction_proxy"],
        )
        feature_matrix.append(fused)
        feature_rows.append(
            {
                "sample_id": row.sample_id,
                "isolate_id": row.isolate_id,
                "label": row.label,
                "primary_gene": context["primary_gene"],
                "binding_score": docking_bundle["binding_score"],
                "docking_confidence": docking_bundle["docking_confidence"],
                "mapped_genes": ",".join(context["mapped_genes"]),
                "mutations": ",".join(context["mutations"]) or "No_mutation",
                "feature_length": len(fused),
            }
        )

    return np.vstack(feature_matrix), pd.DataFrame(feature_rows)


def train_or_load_model(
    base_dir: Path,
    regenerate_model: bool = False,
    regenerate_dataset: bool = False,
    num_isolates: int = 220,
    seed: int = RANDOM_SEED,
) -> Dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    if MODEL_FILE.exists() and not regenerate_model and not regenerate_dataset:
        return joblib.load(MODEL_FILE)

    metadata_path = base_dir / "data" / "generated" / "metadata.csv"
    if regenerate_dataset or not metadata_path.exists():
        metadata = generate_dataset(base_dir=base_dir, num_isolates=num_isolates, seed=seed)
    else:
        metadata = pd.read_csv(metadata_path)

    feature_matrix, feature_manifest = build_training_matrix(base_dir, metadata)
    feature_manifest.to_csv(FEATURE_MANIFEST_FILE, index=False)
    y = feature_manifest["label"].values
    groups = feature_manifest["isolate_id"].values

    splitter = GroupShuffleSplit(n_splits=1, train_size=0.75, random_state=seed)
    train_idx, test_idx = next(splitter.split(feature_matrix, y, groups=groups))

    model = RandomForestClassifier(
        n_estimators=500,
        min_samples_leaf=2,
        class_weight="balanced_subsample",
        random_state=seed,
        n_jobs=1,
    )
    model.fit(feature_matrix[train_idx], y[train_idx])

    y_test = y[test_idx]
    y_pred = model.predict(feature_matrix[test_idx])
    y_proba = model.predict_proba(feature_matrix[test_idx])

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "weighted_f1": round(float(f1_score(y_test, y_pred, average="weighted")), 4),
        "train_samples": int(len(train_idx)),
        "test_samples": int(len(test_idx)),
        "feature_length": int(feature_matrix.shape[1]),
        "class_distribution": feature_manifest["label"].value_counts().to_dict(),
        "classes": list(model.classes_),
    }
    METRICS_FILE.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    pd.DataFrame(confusion_matrix(y_test, y_pred, labels=LABELS), index=LABELS, columns=LABELS).to_csv(CONFUSION_MATRIX_FILE)
    CLASS_REPORT_FILE.write_text(
        json.dumps(classification_report(y_test, y_pred, labels=LABELS, output_dict=True, zero_division=0), indent=2),
        encoding="utf-8",
    )

    predictions_df = feature_manifest.iloc[test_idx].copy()
    predictions_df["predicted_label"] = y_pred
    predictions_df["confidence"] = np.max(y_proba, axis=1)
    predictions_df.to_csv(SAMPLE_PREDICTIONS_FILE, index=False)

    bundle = {"model": model, "metrics": metrics}
    joblib.dump(bundle, MODEL_FILE)
    return bundle


def build_live_feature_payload(
    base_dir: Path,
    sequence: str,
    smiles: str,
    temperature: float,
    ph: float,
    medium: str,
    reference_bundle: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    context = build_sequence_context(base_dir, sequence, reference_bundle=reference_bundle)
    drug_class = infer_drug_class(smiles)
    env_vector = environmental_vector(temperature, ph, medium)

    structure_result = predict_structure_with_esmfold(context["primary_protein"])
    ligand_result = fetch_pubchem_sdf(smiles)
    docking_result = run_diffdock_docking(
        protein_pdb_text=structure_result["pdb_text"],
        protein_sequence=context["primary_protein"],
        sdf_text=ligand_result["sdf_text"],
        smiles=smiles,
        gene=context["primary_gene"],
        mutation_count=len(context["mutations"]),
        structure_features=context["structure_vector"],
        env_vector=env_vector,
    )
    interaction_proxy = simulate_interaction_feature(
        gene_scores=context["gene_scores"],
        mutations=context["mutations"],
        smiles=smiles,
        drug_class=drug_class,
        temperature=temperature,
        ph=ph,
        medium=medium,
    )
    feature_vector = fuse_feature_blocks(
        dna_vector_values=context["dna_vector"],
        mutation_vector_values=context["mutation_vector"],
        structure_vector_values=context["structure_vector"],
        drug_vector_values=smiles_to_fingerprint(smiles),
        env_vector_values=env_vector,
        binding_strength=normalize_binding_score(docking_result["binding_score"]),
        docking_confidence=docking_result["docking_confidence"],
        interaction_proxy=interaction_proxy,
    )

    context.update(
        {
            "drug_class": drug_class,
            "feature_vector": feature_vector,
            "feature_length": int(len(feature_vector)),
            "binding_score": docking_result["binding_score"],
            "docking_confidence": docking_result["docking_confidence"],
            "binding_pose_preview": docking_result["binding_pose_preview"],
            "structure_source": structure_result["source"],
            "ligand_source": ligand_result["source"],
            "docking_source": docking_result["source"],
            "service_notes": [structure_result["note"], ligand_result["note"], docking_result["note"]],
            "protein_pdb_text": structure_result["pdb_text"],
        }
    )
    return context


def predict_resistance(
    base_dir: Path,
    sequence: str,
    smiles: str,
    temperature: float,
    ph: float,
    medium: str,
) -> Dict[str, Any]:
    bundle = train_or_load_model(base_dir)
    payload = build_live_feature_payload(base_dir, sequence, smiles, temperature, ph, medium)
    model: Pipeline = bundle["model"]
    probabilities = model.predict_proba(payload["feature_vector"].reshape(1, -1))[0]
    prediction = str(model.predict(payload["feature_vector"].reshape(1, -1))[0])
    breakdown = {label: round(float(score), 4) for label, score in zip(model.classes_, probabilities)}

    return {
        "prediction": "Sensitive" if prediction == "Sensitive" else f"{prediction} Resistance",
        "prediction_label": prediction,
        "confidence": round(float(np.max(probabilities)), 4),
        "gene": payload["primary_gene"],
        "sequence_length": payload["sequence_length"],
        "protein_length": payload["protein_length"],
        "mapped_genes": payload["mapped_genes"],
        "mutations": payload["mutations"],
        "protein_sequence_preview": payload["protein_sequence_preview"],
        "translated_protein_preview": payload["translated_protein_preview"],
        "structure_features": payload["structure_features"],
        "structure_source": payload["structure_source"],
        "ligand_source": payload["ligand_source"],
        "docking_source": payload["docking_source"],
        "binding_score": round(float(payload["binding_score"]), 2),
        "docking_confidence": round(float(payload["docking_confidence"]), 4),
        "binding_pose_preview": payload["binding_pose_preview"],
        "probability_breakdown": breakdown,
        "message": "Live services are used when configured; otherwise the app falls back to local structure and docking mocks.",
        "service_notes": payload["service_notes"],
    }
