from __future__ import annotations

import argparse
import json
import math
import random
from collections import Counter
from itertools import product
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import joblib
import numpy as np
import pandas as pd
from Bio import SeqIO
from Bio.Seq import Seq
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem, Descriptors
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler


LABELS = ["Sensitive", "Low", "Medium", "High"]
MEDIA = ["LB", "MHB", "Minimal", "Blood"]
KMER_SIZE = 3
GENE_ORDER = ["gyrA", "parC", "blaTEM", "tetA"]
GENE_PRESENCE_THRESHOLD = 0.55
RANDOM_SEED = 42

CODON_TABLE = {
    "A": "GCT",
    "C": "TGT",
    "D": "GAT",
    "E": "GAA",
    "F": "TTT",
    "G": "GGT",
    "H": "CAT",
    "I": "ATT",
    "K": "AAA",
    "L": "CTG",
    "M": "ATG",
    "N": "AAT",
    "P": "CCT",
    "Q": "CAA",
    "R": "CGT",
    "S": "TCT",
    "T": "ACT",
    "V": "GTG",
    "W": "TGG",
    "Y": "TAT",
}

AA_ALPHABET = "ACDEFGHIKLMNPQRSTVWY"
DNA_ALPHABET = "ATGC"
ALL_KMERS = ["".join(kmer) for kmer in product(DNA_ALPHABET, repeat=KMER_SIZE)]
MUTATION_FEATURES = [
    "gyrA_S83L",
    "gyrA_D87N",
    "parC_S80I",
    "parC_E84K",
    "blaTEM_present",
    "tetA_present",
    "mutation_count",
]

GENE_DEFINITIONS = {
    "gyrA": {
        "length_aa": 120,
        "always_present": True,
        "description": "DNA gyrase subunit A, fluoroquinolone target",
        "origin": "NCBI FASTA inspired reference fragment; CARD-style resistance target annotation",
        "url": "https://www.ncbi.nlm.nih.gov/gene/",
        "mutations": {83: "S", 87: "D"},
        "protein_offset": 3,
    },
    "parC": {
        "length_aa": 110,
        "always_present": True,
        "description": "Topoisomerase IV subunit A, fluoroquinolone target",
        "origin": "NCBI FASTA inspired reference fragment; CARD-style resistance target annotation",
        "url": "https://www.ncbi.nlm.nih.gov/gene/",
        "mutations": {80: "S", 84: "E"},
        "protein_offset": 7,
    },
    "blaTEM": {
        "length_aa": 100,
        "always_present": False,
        "description": "Beta-lactamase family gene used as a CARD-mapped resistance determinant",
        "origin": "CARD-inspired local gene catalog",
        "url": "https://card.mcmaster.ca/",
        "mutations": {},
        "protein_offset": 11,
    },
    "tetA": {
        "length_aa": 110,
        "always_present": False,
        "description": "Tetracycline efflux transporter family gene used as a CARD-mapped determinant",
        "origin": "CARD-inspired local gene catalog",
        "url": "https://card.mcmaster.ca/",
        "mutations": {},
        "protein_offset": 13,
    },
}

DRUG_LIBRARY = [
    {
        "drug_name": "Ciprofloxacin",
        "drug_class": "fluoroquinolone",
        "pubchem_cid": 2764,
        "smiles": "C1CC1N2C=C(C(=O)C3=CC(=C(C=C32)N4CCNCC4)F)C(=O)O",
        "pubchem_url": "https://pubchem.ncbi.nlm.nih.gov/compound/2764",
    },
    {
        "drug_name": "Levofloxacin",
        "drug_class": "fluoroquinolone",
        "pubchem_cid": 149096,
        "smiles": "C[C@H]1COC2=C3N1C=C(C(=O)C3=CC(=C2N4CCN(CC4)C)F)C(=O)O",
        "pubchem_url": "https://pubchem.ncbi.nlm.nih.gov/compound/149096",
    },
    {
        "drug_name": "Ampicillin",
        "drug_class": "beta_lactam",
        "pubchem_cid": 6249,
        "smiles": "CC1([C@@H](N2[C@H](S1)[C@@H](C2=O)NC(=O)[C@@H](C3=CC=CC=C3)N)C(=O)O)C",
        "pubchem_url": "https://pubchem.ncbi.nlm.nih.gov/compound/6249",
    },
    {
        "drug_name": "Tetracycline",
        "drug_class": "tetracycline",
        "pubchem_cid": 54675776,
        "smiles": "CC1(C2CC3C(C(=O)C(=C(C3(C(=O)C2=C(C4=C1C=CC=C4O)O)O)O)C(=O)N)N(C)C)O",
        "pubchem_url": "https://pubchem.ncbi.nlm.nih.gov/compound/54675776",
    },
]

CARD_GENE_CATALOG = [
    {
        "gene_name": "gyrA",
        "aro_family": "quinolone resistance-determining region target",
        "mechanism": "target alteration",
        "card_url": "https://card.mcmaster.ca/",
        "preferred_drug_class": "fluoroquinolone",
    },
    {
        "gene_name": "parC",
        "aro_family": "quinolone resistance-determining region target",
        "mechanism": "target alteration",
        "card_url": "https://card.mcmaster.ca/",
        "preferred_drug_class": "fluoroquinolone",
    },
    {
        "gene_name": "blaTEM",
        "aro_family": "beta-lactamase family",
        "mechanism": "antibiotic inactivation",
        "card_url": "https://card.mcmaster.ca/ontology/36010",
        "preferred_drug_class": "beta_lactam",
    },
    {
        "gene_name": "tetA",
        "aro_family": "MFS antibiotic efflux pump",
        "mechanism": "antibiotic efflux",
        "card_url": "https://card.mcmaster.ca/ontology/36708",
        "preferred_drug_class": "tetracycline",
    },
]


def build_reference_protein(length: int, offset: int, forced_positions: Dict[int, str]) -> str:
    protein = [AA_ALPHABET[(index * 7 + offset) % len(AA_ALPHABET)] for index in range(length)]
    for position, amino_acid in forced_positions.items():
        protein[position - 1] = amino_acid
    return "".join(protein)


def protein_to_dna(protein: str) -> str:
    return "".join(CODON_TABLE[amino_acid] for amino_acid in protein)


def apply_amino_acid_mutation(gene_dna: str, position: int, mutated_aa: str) -> str:
    codons = [gene_dna[index : index + 3] for index in range(0, len(gene_dna), 3)]
    codons[position - 1] = CODON_TABLE[mutated_aa]
    return "".join(codons)


def random_dna(length: int, rng: random.Random) -> str:
    return "".join(rng.choice(DNA_ALPHABET) for _ in range(length))


def generate_reference_assets(base_dir: Path) -> Tuple[Dict[str, str], Dict[str, Tuple[int, int]], str]:
    reference_dir = base_dir / "data" / "reference"
    reference_dir.mkdir(parents=True, exist_ok=True)

    gene_sequences: Dict[str, str] = {}
    for gene_name, gene_info in GENE_DEFINITIONS.items():
        protein = build_reference_protein(
            length=gene_info["length_aa"],
            offset=gene_info["protein_offset"],
            forced_positions=gene_info["mutations"],
        )
        gene_sequences[gene_name] = protein_to_dna(protein)

    spacer_rng = random.Random(101)
    genome_parts: List[str] = [random_dna(75, spacer_rng)]
    coordinates: Dict[str, Tuple[int, int]] = {}
    current_position = len(genome_parts[0])
    for gene_name in GENE_ORDER:
        gene_sequence = gene_sequences[gene_name]
        start = current_position
        genome_parts.append(gene_sequence)
        current_position += len(gene_sequence)
        end = current_position
        coordinates[gene_name] = (start, end)
        spacer = random_dna(48, spacer_rng)
        genome_parts.append(spacer)
        current_position += len(spacer)

    reference_genome = "".join(genome_parts)

    reference_fasta = reference_dir / "ncbi_reference_genes.fasta"
    with reference_fasta.open("w", encoding="utf-8") as handle:
        for gene_name, gene_sequence in gene_sequences.items():
            handle.write(
                f">{gene_name}|source=NCBI-inspired|description={GENE_DEFINITIONS[gene_name]['description']}\n"
            )
            handle.write(f"{gene_sequence}\n")

    reference_genome_fasta = reference_dir / "reference_genome.fasta"
    with reference_genome_fasta.open("w", encoding="utf-8") as handle:
        handle.write(">synthetic_reference_genome|source=NCBI-inspired_local_reference\n")
        handle.write(f"{reference_genome}\n")

    pd.DataFrame(CARD_GENE_CATALOG).to_csv(reference_dir / "card_gene_catalog.csv", index=False)
    pd.DataFrame(DRUG_LIBRARY).to_csv(reference_dir / "pubchem_drugs.csv", index=False)

    source_catalog = pd.DataFrame(
        [
            {
                "database": "NCBI",
                "entity": "Reference FASTA fragments for gyrA/parC-like bacterial targets",
                "identifier": "Local curated subset",
                "url": "https://www.ncbi.nlm.nih.gov/",
                "usage": "Reference genes and reference genome template",
                "notes": "Project ships a local, deterministic FASTA inspired by NCBI gene entries for offline execution.",
            },
            {
                "database": "CARD",
                "entity": "Resistance gene ontology subset",
                "identifier": "gyrA, parC, blaTEM, tetA",
                "url": "https://card.mcmaster.ca/",
                "usage": "Gene mapping and mechanism labels",
                "notes": "Small simulated CARD-style catalog for offline gene identification.",
            },
            {
                "database": "PubChem",
                "entity": "Antibiotic structures",
                "identifier": "CID 2764, 149096, 6249, 54675776",
                "url": "https://pubchem.ncbi.nlm.nih.gov/",
                "usage": "SMILES strings converted to Morgan fingerprints by RDKit",
                "notes": "Curated SMILES and CID references embedded locally for reproducible runs.",
            },
            {
                "database": "Experimental conditions",
                "entity": "Temperature, pH, growth medium",
                "identifier": "Simulated lab metadata",
                "url": "local://simulated_experiments",
                "usage": "Environmental feature vector",
                "notes": "Controlled synthetic metadata designed to mimic CPU-friendly in vitro experiments.",
            },
        ]
    )
    source_catalog.to_csv(reference_dir / "source_catalog.csv", index=False)
    (reference_dir / "gene_coordinates.json").write_text(json.dumps(coordinates, indent=2), encoding="utf-8")
    return gene_sequences, coordinates, reference_genome


def mutation_combo_for_isolate(rng: random.Random) -> List[str]:
    roll = rng.random()
    if roll < 0.36:
        return []
    if roll < 0.56:
        return ["gyrA_S83L"]
    if roll < 0.70:
        return ["gyrA_S83L", "parC_S80I"]
    if roll < 0.82:
        return ["gyrA_S83L", "gyrA_D87N", "parC_S80I"]
    if roll < 0.91:
        return ["gyrA_S83L", "parC_S80I", "parC_E84K"]
    return ["gyrA_S83L", "gyrA_D87N", "parC_S80I", "parC_E84K"]


def apply_mutation_labels_to_gene_sequences(
    reference_genes: Dict[str, str], mutation_labels: Iterable[str]
) -> Dict[str, str]:
    mutated = dict(reference_genes)
    for label in mutation_labels:
        gene_name, mutation = label.split("_", maxsplit=1)
        reference_aa = mutation[0]
        position = int(mutation[1:-1])
        mutated_aa = mutation[-1]
        current_gene = mutated[gene_name]
        protein = str(Seq(current_gene).translate())
        if protein[position - 1] != reference_aa:
            raise ValueError(f"Reference amino acid mismatch for {label}")
        mutated[gene_name] = apply_amino_acid_mutation(current_gene, position, mutated_aa)
    return mutated


def choose_environment(rng: random.Random) -> Tuple[float, float, str]:
    temperature = round(rng.uniform(30.0, 42.0), 2)
    ph = round(rng.uniform(5.6, 8.6), 2)
    medium = rng.choice(MEDIA)
    return temperature, ph, medium


def sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def compute_latent_interaction(
    drug_class: str,
    mutation_labels: Iterable[str],
    has_blaTEM: bool,
    has_tetA: bool,
    temperature: float,
    ph: float,
    medium: str,
    drug_bias: float,
) -> float:
    mutation_labels = set(mutation_labels)
    relevance = 0.0
    if drug_class == "fluoroquinolone":
        relevance += 0.70 if "gyrA_S83L" in mutation_labels else 0.0
        relevance += 0.45 if "gyrA_D87N" in mutation_labels else 0.0
        relevance += 0.40 if "parC_S80I" in mutation_labels else 0.0
        relevance += 0.28 if "parC_E84K" in mutation_labels else 0.0
    if drug_class == "beta_lactam":
        relevance += 1.15 if has_blaTEM else 0.0
    if drug_class == "tetracycline":
        relevance += 1.05 if has_tetA else 0.0

    env_pressure = abs(temperature - 37.0) / 5.0
    env_pressure += abs(ph - 7.0) / 1.4
    env_pressure += {"LB": 0.10, "MHB": 0.15, "Minimal": 0.28, "Blood": 0.22}[medium]
    return sigmoid(-1.1 + relevance + 0.22 * env_pressure + drug_bias)


def assign_label(score: float) -> str:
    if score < 0.33:
        return "Sensitive"
    if score < 0.47:
        return "Low"
    if score < 0.62:
        return "Medium"
    return "High"


def generate_dataset(base_dir: Path, num_isolates: int, seed: int) -> pd.DataFrame:
    rng = random.Random(seed)
    reference_genes, coordinates, reference_genome = generate_reference_assets(base_dir)

    generated_dir = base_dir / "data" / "generated"
    fasta_dir = generated_dir / "isolate_fastas"
    generated_dir.mkdir(parents=True, exist_ok=True)
    fasta_dir.mkdir(parents=True, exist_ok=True)

    samples: List[Dict[str, object]] = []
    genome_records: List[Dict[str, object]] = []

    for isolate_index in range(1, num_isolates + 1):
        isolate_id = f"ISO_{isolate_index:04d}"
        isolate_rng = random.Random(seed * 1000 + isolate_index)

        mutation_labels = mutation_combo_for_isolate(isolate_rng)
        has_blaTEM = isolate_rng.random() < 0.42
        has_tetA = isolate_rng.random() < 0.38
        mutated_genes = apply_mutation_labels_to_gene_sequences(reference_genes, mutation_labels)
        genome_chars = list(reference_genome)

        if not has_blaTEM:
            start, end = coordinates["blaTEM"]
            genome_chars[start:end] = list(random_dna(end - start, isolate_rng))
        else:
            start, end = coordinates["blaTEM"]
            genome_chars[start:end] = list(mutated_genes["blaTEM"])

        if not has_tetA:
            start, end = coordinates["tetA"]
            genome_chars[start:end] = list(random_dna(end - start, isolate_rng))
        else:
            start, end = coordinates["tetA"]
            genome_chars[start:end] = list(mutated_genes["tetA"])

        for core_gene in ("gyrA", "parC"):
            start, end = coordinates[core_gene]
            genome_chars[start:end] = list(mutated_genes[core_gene])

        genome_sequence = "".join(genome_chars)
        fasta_path = fasta_dir / f"{isolate_id}.fasta"
        with fasta_path.open("w", encoding="utf-8") as handle:
            handle.write(f">{isolate_id}|species=synthetic_bacterium|origin=simulated_from_reference\n")
            handle.write(f"{genome_sequence}\n")

        genome_records.append(
            {
                "isolate_id": isolate_id,
                "fasta_path": str(fasta_path.relative_to(base_dir)),
                "gyrA_S83L": int("gyrA_S83L" in mutation_labels),
                "gyrA_D87N": int("gyrA_D87N" in mutation_labels),
                "parC_S80I": int("parC_S80I" in mutation_labels),
                "parC_E84K": int("parC_E84K" in mutation_labels),
                "blaTEM_present": int(has_blaTEM),
                "tetA_present": int(has_tetA),
            }
        )

        for drug in DRUG_LIBRARY:
            temperature, ph, medium = choose_environment(isolate_rng)
            base_interaction = compute_latent_interaction(
                drug_class=drug["drug_class"],
                mutation_labels=mutation_labels,
                has_blaTEM=has_blaTEM,
                has_tetA=has_tetA,
                temperature=temperature,
                ph=ph,
                medium=medium,
                drug_bias={
                    "Ciprofloxacin": 0.12,
                    "Levofloxacin": 0.05,
                    "Ampicillin": 0.08,
                    "Tetracycline": 0.10,
                }[drug["drug_name"]],
            )

            score = base_interaction + isolate_rng.uniform(-0.04, 0.04)
            if drug["drug_name"] == "Levofloxacin":
                score -= 0.03
            if medium == "Minimal":
                score += 0.03
            if temperature > 39:
                score += 0.02
            score = max(0.0, min(1.0, score))

            samples.append(
                {
                    "sample_id": f"{isolate_id}_{drug['drug_name'].replace(' ', '_')}",
                    "isolate_id": isolate_id,
                    "fasta_path": str(fasta_path.relative_to(base_dir)),
                    "drug_name": drug["drug_name"],
                    "drug_class": drug["drug_class"],
                    "pubchem_cid": drug["pubchem_cid"],
                    "smiles": drug["smiles"],
                    "temperature_c": temperature,
                    "ph": ph,
                    "medium": medium,
                    "latent_interaction_score": round(base_interaction, 4),
                    "resistance_score": round(score, 4),
                    "label": assign_label(score),
                }
            )

    pd.DataFrame(samples).to_csv(generated_dir / "metadata.csv", index=False)
    pd.DataFrame(genome_records).to_csv(generated_dir / "genotype_manifest.csv", index=False)
    return pd.DataFrame(samples)


def read_fasta_sequence(fasta_path: Path) -> str:
    records = list(SeqIO.parse(str(fasta_path), "fasta"))
    if not records:
        raise ValueError(f"No FASTA records found in {fasta_path}")
    sequence = str(records[0].seq).upper()
    invalid = sorted(set(sequence) - set(DNA_ALPHABET))
    if invalid:
        raise ValueError(f"Invalid DNA symbols in {fasta_path}: {invalid}")
    return sequence


def build_gene_kmer_sets(reference_genes: Dict[str, str], k: int = 11) -> Dict[str, set]:
    return {
        gene_name: {gene_seq[index : index + k] for index in range(0, len(gene_seq) - k + 1)}
        for gene_name, gene_seq in reference_genes.items()
    }


def map_genes_to_card(sequence: str, gene_kmers: Dict[str, set]) -> Dict[str, float]:
    genome_kmers = {sequence[index : index + 11] for index in range(0, len(sequence) - 10)}
    scores = {}
    for gene_name, reference_kmers in gene_kmers.items():
        overlap = len(reference_kmers & genome_kmers)
        scores[gene_name] = overlap / max(1, len(reference_kmers))
    return scores


def detect_mutations(
    sequence: str,
    reference_genes: Dict[str, str],
    coordinates: Dict[str, Tuple[int, int]],
    gene_scores: Dict[str, float],
) -> List[str]:
    detected: List[str] = []
    for gene_name, gene_info in GENE_DEFINITIONS.items():
        if gene_scores[gene_name] < GENE_PRESENCE_THRESHOLD:
            continue
        start, end = coordinates[gene_name]
        sample_gene = sequence[start:end]
        reference_gene = reference_genes[gene_name]
        sample_protein = str(Seq(sample_gene).translate())
        reference_protein = str(Seq(reference_gene).translate())
        for position, reference_aa in gene_info["mutations"].items():
            sample_aa = sample_protein[position - 1]
            if sample_aa != reference_aa:
                detected.append(f"{gene_name}_{reference_aa}{position}{sample_aa}")
    return detected


def dna_kmer_vector(sequence: str, k: int = KMER_SIZE) -> np.ndarray:
    counts = Counter(sequence[index : index + k] for index in range(0, len(sequence) - k + 1))
    total = sum(counts.values())
    return np.array([counts[kmer] / total for kmer in ALL_KMERS], dtype=float)


def mutation_vector(mutations: List[str], gene_scores: Dict[str, float]) -> np.ndarray:
    mutation_set = set(mutations)
    return np.array(
        [
            int("gyrA_S83L" in mutation_set),
            int("gyrA_D87N" in mutation_set),
            int("parC_S80I" in mutation_set),
            int("parC_E84K" in mutation_set),
            int(gene_scores["blaTEM"] >= GENE_PRESENCE_THRESHOLD),
            int(gene_scores["tetA"] >= GENE_PRESENCE_THRESHOLD),
            len(mutations),
        ],
        dtype=float,
    )


def smiles_to_fingerprint(smiles: str, n_bits: int = 128) -> np.ndarray:
    molecule = Chem.MolFromSmiles(smiles)
    if molecule is None:
        raise ValueError(f"Invalid SMILES: {smiles}")
    fingerprint = AllChem.GetMorganFingerprintAsBitVect(molecule, radius=2, nBits=n_bits)
    array = np.zeros((n_bits,), dtype=float)
    DataStructs.ConvertToNumpyArray(fingerprint, array)
    return array


def environmental_vector(temperature: float, ph: float, medium: str) -> np.ndarray:
    medium_one_hot = np.array([1.0 if medium == medium_name else 0.0 for medium_name in MEDIA], dtype=float)
    scaled = np.array([(temperature - 30.0) / 12.0, (ph - 5.5) / 3.5], dtype=float)
    return np.concatenate([scaled, medium_one_hot])


def simulate_interaction_feature(
    gene_scores: Dict[str, float],
    mutations: List[str],
    smiles: str,
    drug_class: str,
    temperature: float,
    ph: float,
    medium: str,
) -> float:
    mutation_set = set(mutations)
    drug_fp = smiles_to_fingerprint(smiles)
    structure_density = float(np.mean(drug_fp))
    molecule = Chem.MolFromSmiles(smiles)
    logp = Descriptors.MolLogP(molecule)

    relevance = 0.0
    if drug_class == "fluoroquinolone":
        relevance += 0.35 * gene_scores["gyrA"] + 0.25 * gene_scores["parC"]
        relevance += 0.35 if "gyrA_S83L" in mutation_set else 0.0
        relevance += 0.20 if "gyrA_D87N" in mutation_set else 0.0
        relevance += 0.22 if "parC_S80I" in mutation_set else 0.0
        relevance += 0.12 if "parC_E84K" in mutation_set else 0.0
    elif drug_class == "beta_lactam":
        relevance += 0.85 * gene_scores["blaTEM"]
    elif drug_class == "tetracycline":
        relevance += 0.80 * gene_scores["tetA"]

    env_stress = abs(temperature - 37.0) / 6.0
    env_stress += abs(ph - 7.0) / 2.0
    env_stress += {"LB": 0.10, "MHB": 0.14, "Minimal": 0.26, "Blood": 0.20}[medium]
    return sigmoid(-0.9 + relevance + 0.18 * env_stress + 0.22 * structure_density + 0.03 * logp)


def fuse_features(
    dna_vector_values: np.ndarray,
    mutation_vector_values: np.ndarray,
    drug_vector_values: np.ndarray,
    env_vector_values: np.ndarray,
    interaction_score: float,
) -> np.ndarray:
    return np.concatenate(
        [
            dna_vector_values,
            mutation_vector_values,
            drug_vector_values,
            env_vector_values,
            np.array([interaction_score], dtype=float),
        ]
    )


def build_feature_table(base_dir: Path, metadata: pd.DataFrame) -> Tuple[np.ndarray, pd.DataFrame]:
    reference_genes, coordinates, _ = generate_reference_assets(base_dir)
    gene_kmers = build_gene_kmer_sets(reference_genes)

    isolate_cache: Dict[str, Dict[str, object]] = {}
    feature_rows: List[Dict[str, object]] = []
    feature_matrix: List[np.ndarray] = []

    for isolate_id, isolate_rows in metadata.groupby("isolate_id"):
        fasta_path = base_dir / isolate_rows.iloc[0]["fasta_path"]
        sequence = read_fasta_sequence(fasta_path)
        gene_scores = map_genes_to_card(sequence, gene_kmers)
        detected_mutations = detect_mutations(sequence, reference_genes, coordinates, gene_scores)
        isolate_cache[isolate_id] = {
            "gene_scores": gene_scores,
            "detected_mutations": detected_mutations,
            "dna_vector": dna_kmer_vector(sequence),
            "mutation_vector": mutation_vector(detected_mutations, gene_scores),
        }

    for row in metadata.itertuples(index=False):
        isolate_features = isolate_cache[row.isolate_id]
        drug_vector = smiles_to_fingerprint(row.smiles)
        env_vector = environmental_vector(row.temperature_c, row.ph, row.medium)
        interaction_score = simulate_interaction_feature(
            gene_scores=isolate_features["gene_scores"],
            mutations=isolate_features["detected_mutations"],
            smiles=row.smiles,
            drug_class=row.drug_class,
            temperature=row.temperature_c,
            ph=row.ph,
            medium=row.medium,
        )
        fused = fuse_features(
            dna_vector_values=isolate_features["dna_vector"],
            mutation_vector_values=isolate_features["mutation_vector"],
            drug_vector_values=drug_vector,
            env_vector_values=env_vector,
            interaction_score=interaction_score,
        )
        feature_matrix.append(fused)
        feature_rows.append(
            {
                "sample_id": row.sample_id,
                "isolate_id": row.isolate_id,
                "drug_name": row.drug_name,
                "temperature_c": row.temperature_c,
                "ph": row.ph,
                "medium": row.medium,
                "label": row.label,
                "mapped_genes": ",".join(
                    gene_name
                    for gene_name, score in isolate_features["gene_scores"].items()
                    if score >= GENE_PRESENCE_THRESHOLD
                ),
                "mutations": ",".join(isolate_features["detected_mutations"]) or "No_mutation",
                "interaction_score": round(interaction_score, 4),
                "feature_length": len(fused),
            }
        )

    return np.vstack(feature_matrix), pd.DataFrame(feature_rows)


def train_and_evaluate(
    feature_matrix: np.ndarray,
    feature_manifest: pd.DataFrame,
    outputs_dir: Path,
    seed: int,
) -> Dict[str, object]:
    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(feature_manifest["label"])
    groups = feature_manifest["isolate_id"].values

    splitter = GroupShuffleSplit(n_splits=1, train_size=0.75, random_state=seed)
    train_idx, test_idx = next(splitter.split(feature_matrix, encoded_labels, groups=groups))

    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "mlp",
                MLPClassifier(
                    hidden_layer_sizes=(128, 64),
                    activation="relu",
                    solver="adam",
                    max_iter=400,
                    early_stopping=True,
                    n_iter_no_change=20,
                    random_state=seed,
                ),
            ),
        ]
    )
    model.fit(feature_matrix[train_idx], encoded_labels[train_idx])

    y_test = encoded_labels[test_idx]
    y_pred = model.predict(feature_matrix[test_idx])
    y_proba = model.predict_proba(feature_matrix[test_idx])

    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")
    labels_in_order = [label_encoder.transform([label])[0] for label in LABELS]
    matrix = confusion_matrix(y_test, y_pred, labels=labels_in_order)
    pd.DataFrame(matrix, index=LABELS, columns=LABELS).to_csv(outputs_dir / "confusion_matrix.csv")

    report = classification_report(
        y_test,
        y_pred,
        target_names=label_encoder.classes_,
        output_dict=True,
        zero_division=0,
    )
    (outputs_dir / "classification_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    predictions_df = feature_manifest.iloc[test_idx].copy()
    predictions_df["predicted_label"] = label_encoder.inverse_transform(y_pred)
    predictions_df["true_label"] = label_encoder.inverse_transform(y_test)
    predictions_df["max_probability"] = np.max(y_proba, axis=1)
    predictions_df.to_csv(outputs_dir / "sample_predictions.csv", index=False)
    joblib.dump(model, outputs_dir / "multimodal_resistance_model.joblib")

    summary = {
        "accuracy": round(float(accuracy), 4),
        "weighted_f1": round(float(f1), 4),
        "train_samples": int(len(train_idx)),
        "test_samples": int(len(test_idx)),
        "feature_length": int(feature_matrix.shape[1]),
        "class_distribution": feature_manifest["label"].value_counts().to_dict(),
        "cross_entropy_note": "MLPClassifier optimizes multiclass log-loss, i.e. cross-entropy for classification.",
        "loss_curve_tail": model.named_steps["mlp"].loss_curve_[-10:],
    }
    (outputs_dir / "metrics.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def save_feature_manifest(feature_manifest: pd.DataFrame, outputs_dir: Path) -> None:
    feature_manifest.to_csv(outputs_dir / "feature_manifest.csv", index=False)


def bootstrap_and_run(base_dir: Path, num_isolates: int, regenerate: bool, seed: int) -> Dict[str, object]:
    outputs_dir = base_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    metadata_path = base_dir / "data" / "generated" / "metadata.csv"
    if regenerate or not metadata_path.exists():
        metadata = generate_dataset(base_dir=base_dir, num_isolates=num_isolates, seed=seed)
    else:
        metadata = pd.read_csv(metadata_path)

    feature_matrix, feature_manifest = build_feature_table(base_dir, metadata)
    save_feature_manifest(feature_manifest, outputs_dir)
    metrics = train_and_evaluate(feature_matrix, feature_manifest, outputs_dir, seed)

    summary = {
        "project": "Context-Aware Multi-Modal Antibiotic Resistance Prediction",
        "samples": int(len(metadata)),
        "isolates": int(metadata["isolate_id"].nunique()),
        "outputs_dir": str(outputs_dir),
        "metrics": metrics,
        "example_predictions_file": str(outputs_dir / "sample_predictions.csv"),
        "feature_manifest_file": str(outputs_dir / "feature_manifest.csv"),
        "dataset_file": str(metadata_path),
    }
    (outputs_dir / "run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def print_human_readable_summary(summary: Dict[str, object]) -> None:
    metrics = summary["metrics"]
    print("\n=== Project Overview ===")
    print(summary["project"])
    print(f"Isolates: {summary['isolates']}")
    print(f"Samples: {summary['samples']}")
    print("\n=== Training Results ===")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Weighted F1: {metrics['weighted_f1']:.4f}")
    print(f"Feature length: {metrics['feature_length']}")
    print(f"Train/Test: {metrics['train_samples']}/{metrics['test_samples']}")
    print("\n=== Label Distribution ===")
    for label_name, count in metrics["class_distribution"].items():
        print(f"{label_name}: {count}")
    print("\n=== Notes ===")
    print(metrics["cross_entropy_note"])
    print(f"Outputs saved to: {summary['outputs_dir']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Context-aware multi-modal antibiotic resistance prediction pipeline"
    )
    parser.add_argument("--num-isolates", type=int, default=180, help="Number of synthetic isolates")
    parser.add_argument("--seed", type=int, default=RANDOM_SEED, help="Random seed")
    parser.add_argument(
        "--regenerate",
        action="store_true",
        help="Regenerate reference assets and synthetic dataset before training",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_dir = Path(__file__).resolve().parent
    summary = bootstrap_and_run(
        base_dir=base_dir,
        num_isolates=args.num_isolates,
        regenerate=args.regenerate,
        seed=args.seed,
    )
    print_human_readable_summary(summary)


if __name__ == "__main__":
    main()
