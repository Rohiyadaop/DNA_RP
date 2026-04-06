from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import joblib
import numpy as np
import pandas as pd
from Bio.Seq import Seq
from rdkit import Chem
from rdkit.Chem import Descriptors
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

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
MODEL_FILE = ARTIFACT_DIR / "amr_web_model.joblib"
METRICS_FILE = ARTIFACT_DIR / "training_metrics.json"
FEATURE_MANIFEST_FILE = ARTIFACT_DIR / "feature_manifest.csv"
CONFUSION_MATRIX_FILE = ARTIFACT_DIR / "confusion_matrix.csv"

HYDROPHOBIC = set("AILMFWVYV")
POLAR = set("STNQCY")
POSITIVE = set("KRH")
NEGATIVE = set("DE")
AROMATIC = set("FWY")
FLEXIBLE = set("GPSND")


def sigmoid(value: float) -> float:
    return 1.0 / (1.0 + np.exp(-value))


def load_reference_bundle(base_dir: Path) -> Dict[str, Any]:
    reference_genes, coordinates, _ = generate_reference_assets(base_dir)
    return {
        "reference_genes": reference_genes,
        "coordinates": coordinates,
        "gene_kmers": build_gene_kmer_sets(reference_genes),
    }


def translate_detected_genes(
    sequence: str,
    coordinates: Dict[str, tuple[int, int]],
    gene_scores: Dict[str, float],
) -> Dict[str, str]:
    translated: Dict[str, str] = {}
    for gene_name in GENE_DEFINITIONS:
        if gene_scores[gene_name] < GENE_PRESENCE_THRESHOLD:
            continue
        start, end = coordinates[gene_name]
        protein = str(Seq(sequence[start:end]).translate())
        cleaned = protein.split("*")[0].strip()
        candidate = cleaned or protein.replace("*", "")
        if len(candidate) < 15:
            continue
        translated[gene_name] = candidate
    return translated


def protein_preview(proteins: Dict[str, str], width: int = 24) -> Dict[str, str]:
    preview: Dict[str, str] = {}
    for gene_name, protein in proteins.items():
        preview[gene_name] = protein if len(protein) <= width else f"{protein[:width]}..."
    return preview


def residue_fraction(sequence: str, residues: set[str]) -> float:
    if not sequence:
        return 0.0
    return sum(1 for amino_acid in sequence if amino_acid in residues) / len(sequence)


def protein_structure_vector(proteins: Dict[str, str]) -> np.ndarray:
    if not proteins:
        return np.zeros(8, dtype=float)

    merged = "".join(proteins.values())
    protein_lengths = [len(protein) for protein in proteins.values()]
    return np.array(
        [
            residue_fraction(merged, HYDROPHOBIC),
            residue_fraction(merged, POLAR),
            residue_fraction(merged, POSITIVE),
            residue_fraction(merged, NEGATIVE),
            residue_fraction(merged, AROMATIC),
            residue_fraction(merged, FLEXIBLE),
            float(np.mean(protein_lengths) / 120.0),
            float(len(proteins) / max(1, len(GENE_DEFINITIONS))),
        ],
        dtype=float,
    )


def infer_drug_class(smiles: str) -> str:
    input_fp = smiles_to_fingerprint(smiles)
    best_score = -1.0
    best_class = DRUG_LIBRARY[0]["drug_class"]
    for drug in DRUG_LIBRARY:
        candidate_fp = smiles_to_fingerprint(drug["smiles"])
        score = float(np.mean(input_fp == candidate_fp))
        if score > best_score:
            best_score = score
            best_class = str(drug["drug_class"])
    return best_class


def simulate_docking_score(
    gene_scores: Dict[str, float],
    mutations: List[str],
    smiles: str,
    drug_class: str,
    structure_vector: np.ndarray,
    temperature: float,
    ph: float,
    medium: str,
) -> float:
    drug_fp = smiles_to_fingerprint(smiles)
    molecule = Chem.MolFromSmiles(smiles)
    if molecule is None:
        raise ValueError("SMILES parsing failed during docking simulation.")

    fingerprint_density = float(np.mean(drug_fp))
    logp = float(Descriptors.MolLogP(molecule))
    tpsa = float(Descriptors.TPSA(molecule) / 150.0)
    donors = float(Descriptors.NumHDonors(molecule) / 8.0)
    mutation_burden = float(len(mutations) / 4.0)

    target_support = 0.0
    class_alignment = 0.0
    if drug_class == "fluoroquinolone":
        target_support += 0.35 * gene_scores["gyrA"] + 0.30 * gene_scores["parC"]
        class_alignment += 0.18 if "gyrA_S83L" in mutations else 0.0
        class_alignment += 0.12 if "gyrA_D87N" in mutations else 0.0
        class_alignment += 0.10 if "parC_S80I" in mutations else 0.0
        class_alignment += 0.08 if "parC_E84K" in mutations else 0.0
    elif drug_class == "beta_lactam":
        target_support += 0.75 * gene_scores["blaTEM"]
    elif drug_class == "tetracycline":
        target_support += 0.72 * gene_scores["tetA"]

    env_component = abs(temperature - 37.0) / 7.0
    env_component += abs(ph - 7.0) / 2.2
    env_component += {"LB": 0.08, "MHB": 0.12, "Minimal": 0.22, "Blood": 0.18}[medium]

    structure_component = 0.24 * structure_vector[0] + 0.18 * structure_vector[4]
    structure_component += 0.12 * structure_vector[5] + 0.10 * structure_vector[7]

    raw_score = -0.95
    raw_score += 0.28 * fingerprint_density
    raw_score += 0.18 * logp
    raw_score += 0.22 * tpsa
    raw_score += 0.12 * donors
    raw_score += structure_component
    raw_score += target_support
    raw_score += class_alignment
    raw_score += 0.16 * mutation_burden
    raw_score += 0.10 * env_component
    return float(sigmoid(raw_score))


def fuse_feature_blocks(
    dna_vector_values: np.ndarray,
    mutation_vector_values: np.ndarray,
    structure_vector_values: np.ndarray,
    drug_vector_values: np.ndarray,
    env_vector_values: np.ndarray,
    docking_score: float,
    interaction_proxy: float,
) -> np.ndarray:
    return np.concatenate(
        [
            dna_vector_values,
            mutation_vector_values,
            structure_vector_values,
            drug_vector_values,
            env_vector_values,
            np.array([docking_score, interaction_proxy], dtype=float),
        ]
    )


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
    structure_vector_values = protein_structure_vector(proteins)
    mapped_genes = list(proteins.keys())

    return {
        "sequence": sequence,
        "sequence_length": len(sequence),
        "gene_scores": gene_scores,
        "mapped_genes": mapped_genes,
        "mutations": mutations,
        "proteins": proteins,
        "protein_preview": protein_preview(proteins),
        "structure_vector": structure_vector_values,
        "dna_vector": dna_kmer_vector(sequence),
        "mutation_vector": mutation_vector(mutations, gene_scores),
    }


def build_feature_payload(
    base_dir: Path,
    sequence: str,
    smiles: str,
    temperature: float,
    ph: float,
    medium: str,
    drug_class: str | None = None,
    reference_bundle: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    context = build_sequence_context(base_dir, sequence, reference_bundle=reference_bundle)
    resolved_drug_class = drug_class or infer_drug_class(smiles)
    drug_vector_values = smiles_to_fingerprint(smiles)
    env_vector_values = environmental_vector(temperature, ph, medium)
    docking_score = simulate_docking_score(
        gene_scores=context["gene_scores"],
        mutations=context["mutations"],
        smiles=smiles,
        drug_class=resolved_drug_class,
        structure_vector=context["structure_vector"],
        temperature=temperature,
        ph=ph,
        medium=medium,
    )
    interaction_proxy = simulate_interaction_feature(
        gene_scores=context["gene_scores"],
        mutations=context["mutations"],
        smiles=smiles,
        drug_class=resolved_drug_class,
        temperature=temperature,
        ph=ph,
        medium=medium,
    )
    fused = fuse_feature_blocks(
        dna_vector_values=context["dna_vector"],
        mutation_vector_values=context["mutation_vector"],
        structure_vector_values=context["structure_vector"],
        drug_vector_values=drug_vector_values,
        env_vector_values=env_vector_values,
        docking_score=docking_score,
        interaction_proxy=interaction_proxy,
    )
    context.update(
        {
            "drug_class": resolved_drug_class,
            "docking_score": docking_score,
            "interaction_proxy": interaction_proxy,
            "feature_vector": fused,
            "feature_length": int(len(fused)),
            "structure_features": [round(float(value), 4) for value in context["structure_vector"]],
        }
    )
    return context


def build_training_matrix(base_dir: Path, metadata: pd.DataFrame) -> tuple[np.ndarray, pd.DataFrame]:
    reference_bundle = load_reference_bundle(base_dir)
    isolate_cache: Dict[str, Dict[str, Any]] = {}
    feature_rows: List[Dict[str, Any]] = []
    feature_matrix: List[np.ndarray] = []

    for isolate_id, isolate_rows in metadata.groupby("isolate_id"):
        fasta_path = base_dir / isolate_rows.iloc[0]["fasta_path"]
        sequence = fasta_path.read_text(encoding="utf-8").splitlines()[-1].strip().upper()
        isolate_cache[isolate_id] = build_sequence_context(
            base_dir=base_dir,
            sequence=sequence,
            reference_bundle=reference_bundle,
        )

    for row in metadata.itertuples(index=False):
        isolate_context = isolate_cache[row.isolate_id]
        payload = build_feature_payload(
            base_dir=base_dir,
            sequence=isolate_context["sequence"],
            smiles=row.smiles,
            temperature=row.temperature_c,
            ph=row.ph,
            medium=row.medium,
            drug_class=row.drug_class,
            reference_bundle=reference_bundle,
        )
        feature_matrix.append(payload["feature_vector"])
        feature_rows.append(
            {
                "sample_id": row.sample_id,
                "isolate_id": row.isolate_id,
                "drug_name": row.drug_name,
                "drug_class": payload["drug_class"],
                "temperature_c": row.temperature_c,
                "ph": row.ph,
                "medium": row.medium,
                "label": row.label,
                "mapped_genes": ",".join(payload["mapped_genes"]),
                "mutations": ",".join(payload["mutations"]) or "No_mutation",
                "docking_score": round(payload["docking_score"], 4),
                "feature_length": payload["feature_length"],
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

    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "mlp",
                MLPClassifier(
                    hidden_layer_sizes=(160, 80),
                    activation="relu",
                    solver="adam",
                    max_iter=450,
                    early_stopping=True,
                    n_iter_no_change=25,
                    random_state=seed,
                ),
            ),
        ]
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

    confusion = confusion_matrix(y_test, y_pred, labels=LABELS)
    pd.DataFrame(confusion, index=LABELS, columns=LABELS).to_csv(CONFUSION_MATRIX_FILE)

    report = classification_report(y_test, y_pred, labels=LABELS, output_dict=True, zero_division=0)
    (ARTIFACT_DIR / "classification_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    predictions = feature_manifest.iloc[test_idx].copy()
    predictions["predicted_label"] = y_pred
    predictions["confidence"] = np.max(y_proba, axis=1)
    predictions.to_csv(ARTIFACT_DIR / "sample_predictions.csv", index=False)

    bundle = {"model": model, "metrics": metrics}
    joblib.dump(bundle, MODEL_FILE)
    return bundle


def predict_resistance(
    base_dir: Path,
    sequence: str,
    smiles: str,
    temperature: float,
    ph: float,
    medium: str,
) -> Dict[str, Any]:
    bundle = train_or_load_model(base_dir)
    payload = build_feature_payload(
        base_dir=base_dir,
        sequence=sequence,
        smiles=smiles,
        temperature=temperature,
        ph=ph,
        medium=medium,
    )
    model: Pipeline = bundle["model"]
    probabilities = model.predict_proba(payload["feature_vector"].reshape(1, -1))[0]
    prediction = str(model.predict(payload["feature_vector"].reshape(1, -1))[0])
    probability_breakdown = {
        label: round(float(score), 4) for label, score in zip(model.classes_, probabilities)
    }
    confidence = float(np.max(probabilities))

    return {
        "prediction_label": prediction,
        "prediction_text": "Sensitive" if prediction == "Sensitive" else f"{prediction} Resistance",
        "confidence": round(confidence, 4),
        "probability_breakdown": probability_breakdown,
        "mapped_genes": payload["mapped_genes"],
        "mutations": payload["mutations"],
        "translated_protein_preview": payload["protein_preview"],
        "structure_features": payload["structure_features"],
        "docking_score": round(float(payload["docking_score"]), 4),
        "sequence_length": payload["sequence_length"],
        "drug_class": payload["drug_class"],
        "feature_length": payload["feature_length"],
    }
