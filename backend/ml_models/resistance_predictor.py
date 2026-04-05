"""
ML backbone for the DNA Mutation Resistance Predictor prototype.

The model intentionally stays lightweight for hackathon use:
- char / k-mer style vectorization
- logistic regression classifier
- curated biological knowledge for calibration and explanation grounding
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

DNA_PATTERN = re.compile(r"^[ACGT]+$", re.IGNORECASE)
MUTATION_PATTERN = re.compile(
    r"(?i)^(?P<gene>[A-Z0-9]+)\s*(?P<from>[A-Z\*])(?P<position>\d{1,4})(?P<to>[A-Z\*])$"
)
HELIX_LENGTH = 48

AMINO_ACID_CODONS = {
    "A": ["GCT", "GCC", "GCA", "GCG"],
    "C": ["TGT", "TGC"],
    "D": ["GAT", "GAC"],
    "E": ["GAA", "GAG"],
    "F": ["TTT", "TTC"],
    "G": ["GGT", "GGC", "GGA", "GGG"],
    "H": ["CAT", "CAC"],
    "I": ["ATT", "ATC", "ATA"],
    "K": ["AAA", "AAG"],
    "L": ["TTA", "TTG", "CTT", "CTC", "CTA", "CTG"],
    "M": ["ATG"],
    "N": ["AAT", "AAC"],
    "P": ["CCT", "CCC", "CCA", "CCG"],
    "Q": ["CAA", "CAG"],
    "R": ["CGT", "CGC", "CGA", "CGG", "AGA", "AGG"],
    "S": ["TCT", "TCC", "TCA", "TCG", "AGT", "AGC"],
    "T": ["ACT", "ACC", "ACA", "ACG"],
    "V": ["GTT", "GTC", "GTA", "GTG"],
    "W": ["TGG"],
    "Y": ["TAT", "TAC"],
    "*": ["TAA"],
}

GENE_LIBRARY = {
    "gyra": {
        "display_gene": "gyrA",
        "protein": "DNA gyrase subunit A",
        "antibiotic_class": "Fluoroquinolones",
        "mechanism": "alters the quinolone-resistance determining region of DNA gyrase and weakens antibiotic binding",
        "hotspots": [83, 87, 90, 94],
        "resistant_profiles": {
            "S83L": 0.93,
            "D87N": 0.88,
            "D87G": 0.86,
            "A90V": 0.79,
            "D94G": 0.84,
        },
        "not_resistant_profiles": {
            "S95T": 0.27,
            "G81A": 0.31,
            "A119S": 0.22,
        },
        "gc_bias": 0.56,
    },
    "parc": {
        "display_gene": "parC",
        "protein": "Topoisomerase IV subunit A",
        "antibiotic_class": "Fluoroquinolones",
        "mechanism": "reshapes topoisomerase IV at the drug-contact surface, preserving DNA replication under quinolone pressure",
        "hotspots": [79, 80, 83, 84],
        "resistant_profiles": {
            "S80I": 0.9,
            "E84K": 0.85,
            "S83L": 0.82,
        },
        "not_resistant_profiles": {
            "A56T": 0.25,
            "E88Q": 0.29,
            "T66A": 0.23,
        },
        "gc_bias": 0.55,
    },
    "katg": {
        "display_gene": "katG",
        "protein": "Catalase-peroxidase",
        "antibiotic_class": "Isoniazid",
        "mechanism": "reduces pro-drug activation, so isoniazid is less able to block mycolic-acid synthesis",
        "hotspots": [138, 315, 328],
        "resistant_profiles": {
            "S315T": 0.95,
            "W328G": 0.82,
            "S315N": 0.88,
        },
        "not_resistant_profiles": {
            "R463L": 0.24,
            "R176C": 0.28,
            "A110V": 0.21,
        },
        "gc_bias": 0.64,
    },
    "rpob": {
        "display_gene": "rpoB",
        "protein": "RNA polymerase beta subunit",
        "antibiotic_class": "Rifampicin",
        "mechanism": "changes the rifampicin-binding pocket in RNA polymerase and allows transcription to continue",
        "hotspots": [435, 445, 450],
        "resistant_profiles": {
            "S450L": 0.96,
            "H445Y": 0.89,
            "D435V": 0.87,
        },
        "not_resistant_profiles": {
            "Q432R": 0.3,
            "S456C": 0.34,
            "A381V": 0.19,
        },
        "gc_bias": 0.62,
    },
    "rpsl": {
        "display_gene": "rpsL",
        "protein": "Ribosomal protein S12",
        "antibiotic_class": "Streptomycin",
        "mechanism": "modifies the streptomycin-contact region of the ribosome and prevents translational arrest",
        "hotspots": [43, 88],
        "resistant_profiles": {
            "K43R": 0.94,
            "K88R": 0.86,
        },
        "not_resistant_profiles": {
            "R24C": 0.29,
            "K42N": 0.33,
            "A87V": 0.21,
        },
        "gc_bias": 0.58,
    },
    "embb": {
        "display_gene": "embB",
        "protein": "Arabinosyl transferase",
        "antibiotic_class": "Ethambutol",
        "mechanism": "perturbs arabinan biosynthesis and reduces ethambutol inhibition of cell-wall assembly",
        "hotspots": [306, 406],
        "resistant_profiles": {
            "M306V": 0.87,
            "M306I": 0.85,
            "A306D": 0.81,
        },
        "not_resistant_profiles": {
            "H49Y": 0.27,
            "G406A": 0.31,
            "A234T": 0.2,
        },
        "gc_bias": 0.61,
    },
    "pnca": {
        "display_gene": "pncA",
        "protein": "Pyrazinamidase",
        "antibiotic_class": "Pyrazinamide",
        "mechanism": "reduces pyrazinamidase activity, limiting conversion of pyrazinamide into its active form",
        "hotspots": [14, 57, 138],
        "resistant_profiles": {
            "S14P": 0.88,
            "C138Y": 0.84,
            "Q10P": 0.79,
        },
        "not_resistant_profiles": {
            "F134V": 0.24,
            "A46V": 0.2,
            "G97S": 0.28,
        },
        "gc_bias": 0.54,
    },
}


@dataclass(frozen=True)
class SequenceMarker:
    gene: str
    motif: str
    effect: str
    label: str
    weight: float


def clamp(value: float, low: float = 0.01, high: float = 0.99) -> float:
    return float(max(low, min(high, value)))


def canonical_gene_label(gene_key: str) -> str:
    gene_info = GENE_LIBRARY.get(gene_key.lower())
    return gene_info["display_gene"] if gene_info else gene_key


def canonical_codon(residue: str) -> str:
    codons = AMINO_ACID_CODONS.get(residue.upper())
    return codons[0] if codons else "NNN"


def mutation_to_motif(change: str) -> str:
    from_residue = change[0]
    to_residue = change[-1]
    return f"{canonical_codon(from_residue)}{canonical_codon(to_residue)}"


SEQUENCE_MARKERS = [
    SequenceMarker(
        gene=gene_key,
        motif=mutation_to_motif(change),
        effect="resistant",
        label=f"{info['display_gene']} {change} motif",
        weight=0.14,
    )
    for gene_key, info in GENE_LIBRARY.items()
    for change in info["resistant_profiles"]
] + [
    SequenceMarker(
        gene=gene_key,
        motif=mutation_to_motif(change),
        effect="not_resistant",
        label=f"{info['display_gene']} {change} motif",
        weight=0.12,
    )
    for gene_key, info in GENE_LIBRARY.items()
    for change in info["not_resistant_profiles"]
]


def parse_mutation(mutation_input: str) -> dict[str, object] | None:
    compact = re.sub(r"\s+", "", mutation_input or "").upper()
    match = MUTATION_PATTERN.match(compact)
    if not match:
        return None

    gene_key = match.group("gene").lower()
    return {
        "gene_key": gene_key,
        "gene": canonical_gene_label(gene_key),
        "from_residue": match.group("from").upper(),
        "to_residue": match.group("to").upper(),
        "position": int(match.group("position")),
        "change": (
            f"{match.group('from').upper()}{int(match.group('position'))}{match.group('to').upper()}"
        ),
    }


def top_kmers(sequence: str, k: int = 3, top_n: int = 5) -> list[str]:
    normalized = re.sub(r"[^A-Z0-9]", "", sequence.upper())
    if not normalized:
        return []
    if len(normalized) <= k:
        return [normalized]

    counts = Counter(
        normalized[index : index + k] for index in range(len(normalized) - k + 1)
    )
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [token for token, _ in ranked[:top_n]]


def compute_gc_content(sequence: str) -> float:
    if not sequence:
        return 0.0
    uppercase = sequence.upper()
    gc_count = uppercase.count("G") + uppercase.count("C")
    return round(gc_count / len(uppercase), 3)


def normalize_sequence(sequence: str) -> str:
    lines = [line.strip() for line in sequence.splitlines() if line.strip()]
    cleaned = "".join(line for line in lines if not line.startswith(">"))
    cleaned = re.sub(r"\s+", "", cleaned).upper()
    if not cleaned or not DNA_PATTERN.fullmatch(cleaned):
        raise ValueError("DNA sequence inputs must contain only A, T, G, and C bases.")
    return cleaned


def resolve_input_type(raw_input: str, requested_type: str | None = None) -> str:
    compact = re.sub(r"\s+", "", raw_input or "").upper()
    if compact and DNA_PATTERN.fullmatch(compact):
        return "sequence"
    if parse_mutation(raw_input):
        return "mutation"
    return requested_type or "mutation"


def random_dna_sequence(length: int, gc_bias: float, rng: np.random.Generator) -> str:
    gc_weight = gc_bias / 2
    at_weight = (1 - gc_bias) / 2
    bases = np.array(["A", "C", "G", "T"])
    probabilities = np.array([at_weight, gc_weight, gc_weight, at_weight])
    return "".join(rng.choice(bases, size=length, p=probabilities))


def embed_motif(
    motif: str,
    length: int,
    gc_bias: float,
    rng: np.random.Generator,
) -> str:
    sequence = list(random_dna_sequence(length, gc_bias, rng))
    start = int(rng.integers(6, max(7, length - len(motif) - 5)))
    sequence[start : start + len(motif)] = list(motif)
    return "".join(sequence)


def marker_positions(sequence: str) -> list[dict[str, object]]:
    matches: list[dict[str, object]] = []
    if not sequence:
        return matches

    sequence_upper = sequence.upper()
    for marker in SEQUENCE_MARKERS:
        start = sequence_upper.find(marker.motif)
        if start < 0:
            continue
        center = start + (len(marker.motif) / 2)
        helix_index = min(
            HELIX_LENGTH - 1,
            max(0, int(round((center / len(sequence_upper)) * (HELIX_LENGTH - 1)))),
        )
        matches.append(
            {
                "index": helix_index,
                "label": marker.label,
                "effect": marker.effect,
                "gene": canonical_gene_label(marker.gene),
            }
        )
    return matches


class ResistancePredictorModel:
    """Lightweight classifier and biological signal encoder."""

    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            lowercase=True,
            sublinear_tf=True,
        )
        self.model = LogisticRegression(
            max_iter=1600,
            solver="liblinear",
            class_weight="balanced",
            random_state=42,
        )
        self._train_model()

    def _train_model(self) -> None:
        samples, labels = self._build_training_corpus()
        encoded = self.vectorizer.fit_transform(samples)
        self.model.fit(encoded, labels)

    def _build_training_corpus(self) -> tuple[list[str], list[int]]:
        rng = np.random.default_rng(42)
        samples: list[str] = []
        labels: list[int] = []

        for gene_key, info in GENE_LIBRARY.items():
            display_gene = info["display_gene"]

            for change in info["resistant_profiles"]:
                mutation_variants = [
                    f"{display_gene} {change}",
                    f"{display_gene.lower()} {change}",
                    f"{display_gene}{change}",
                    f"  {display_gene}   {change}  ",
                ]
                for variant in mutation_variants:
                    samples.append(self._feature_text(variant, forced_type="mutation"))
                    labels.append(1)

                motif = mutation_to_motif(change)
                for _ in range(10):
                    sequence = embed_motif(
                        motif=motif,
                        length=int(rng.integers(54, 78)),
                        gc_bias=info["gc_bias"],
                        rng=rng,
                    )
                    samples.append(self._feature_text(sequence, forced_type="sequence"))
                    labels.append(1)

            for change in info["not_resistant_profiles"]:
                mutation_variants = [
                    f"{display_gene} {change}",
                    f"{display_gene.lower()} {change}",
                    f"{display_gene}{change}",
                    f"  {display_gene}   {change}  ",
                ]
                for variant in mutation_variants:
                    samples.append(self._feature_text(variant, forced_type="mutation"))
                    labels.append(0)

                motif = mutation_to_motif(change)
                for _ in range(10):
                    sequence = embed_motif(
                        motif=motif,
                        length=int(rng.integers(54, 78)),
                        gc_bias=max(0.45, info["gc_bias"] - 0.03),
                        rng=rng,
                    )
                    samples.append(self._feature_text(sequence, forced_type="sequence"))
                    labels.append(0)

        for _ in range(60):
            gc_bias = float(rng.uniform(0.42, 0.66))
            sequence = random_dna_sequence(int(rng.integers(48, 82)), gc_bias, rng)
            samples.append(self._feature_text(sequence, forced_type="sequence"))
            labels.append(1 if gc_bias > 0.6 else 0)

        return samples, labels

    def _feature_text(self, raw_input: str, forced_type: str | None = None) -> str:
        summary = self.summarize_input(raw_input, forced_type)
        normalized_compact = re.sub(r"\s+", "", summary["normalized_input"])

        tokens = [
            f"type:{summary['input_type']}",
            f"raw:{normalized_compact.lower()}",
            f"length_bucket:{min(16, max(1, int(summary['input_length'] / 4)))}",
            f"gc_bucket:{int(round(summary['gc_content'] * 10))}",
        ]

        for kmer in summary["top_kmers"]:
            tokens.append(f"kmer:{kmer.lower()}")

        if summary["gene_info"]:
            tokens.extend(
                [
                    f"gene:{summary['gene_info']['gene']}",
                    f"antibiotic:{summary['gene_info']['antibiotic_class'].lower()}",
                ]
            )

        if summary["mutation_label"]:
            tokens.extend(
                [
                    f"change:{summary['mutation_label']}",
                    f"position_bucket:{min(20, max(1, int(summary['position'] / 25)))}",
                    f"hotspot:{int(bool(summary['is_hotspot']))}",
                ]
            )

        for marker in summary["detected_markers"][:4]:
            tokens.append(f"marker:{marker.lower().replace(' ', '_')}")

        return " ".join(tokens)

    def summarize_input(
        self,
        raw_input: str,
        requested_type: str | None = None,
    ) -> dict[str, object]:
        resolved_input_type = resolve_input_type(raw_input, requested_type)

        if resolved_input_type == "sequence":
            normalized_input = normalize_sequence(raw_input)
            mutation = None
        else:
            normalized_input = " ".join(raw_input.strip().split())
            mutation = parse_mutation(normalized_input)
            if not mutation:
                raise ValueError(
                    "Mutation inputs should look like 'gyrA S83L' or 'rpoB S450L'."
                )

        gene_key = mutation["gene_key"] if mutation else None
        gene_info = GENE_LIBRARY.get(gene_key) if gene_key else None
        gc_content = (
            compute_gc_content(normalized_input) if resolved_input_type == "sequence" else 0.0
        )
        kmers = top_kmers(
            normalized_input if resolved_input_type == "sequence" else normalized_input.replace(" ", ""),
            k=3,
            top_n=5,
        )

        resistant_target = None
        not_resistant_target = None
        detected_markers: list[str] = []
        highlight_positions: list[int] = []
        heuristics = 0.0
        hotspot = False

        if mutation:
            change = mutation["change"]
            position = int(mutation["position"])
            highlight_positions = [(position - 1) % HELIX_LENGTH]

            if gene_info:
                resistant_target = gene_info["resistant_profiles"].get(change)
                not_resistant_target = gene_info["not_resistant_profiles"].get(change)
                hotspot = position in gene_info["hotspots"]

                if hotspot:
                    heuristics += 0.08
                    detected_markers.append(f"{gene_info['display_gene']} hotspot {position}")
                if resistant_target is not None:
                    heuristics += 0.24
                    detected_markers.append(f"{gene_info['display_gene']} curated resistance mutation")
                if not_resistant_target is not None:
                    heuristics -= 0.22
                    detected_markers.append(f"{gene_info['display_gene']} lower-risk substitution")

            if mutation["from_residue"] == mutation["to_residue"]:
                heuristics -= 0.08

        else:
            sequence_matches = marker_positions(normalized_input)
            highlight_positions = list(
                dict.fromkeys(match["index"] for match in sequence_matches)
            )[:4]
            if not highlight_positions:
                highlight_positions = [
                    min(
                        HELIX_LENGTH - 1,
                        max(0, int(round((len(normalized_input) / 2 / len(normalized_input)) * (HELIX_LENGTH - 1)))),
                    )
                ]

            for match in sequence_matches:
                label = str(match["label"])
                if label not in detected_markers:
                    detected_markers.append(label)
                heuristics += 0.14 if match["effect"] == "resistant" else -0.12

            if gc_content >= 0.62:
                heuristics += 0.05
                detected_markers.append("elevated GC signal")
            elif gc_content <= 0.44:
                heuristics -= 0.03

        return {
            "input_type": resolved_input_type,
            "normalized_input": normalized_input,
            "input_length": len(normalized_input),
            "gc_content": gc_content,
            "top_kmers": kmers,
            "gene_info": (
                {
                    "gene": gene_info["display_gene"],
                    "protein": gene_info["protein"],
                    "antibiotic_class": gene_info["antibiotic_class"],
                    "mechanism": gene_info["mechanism"],
                }
                if gene_info
                else None
            ),
            "mutation_label": mutation["change"] if mutation else None,
            "position": mutation["position"] if mutation else None,
            "from_residue": mutation["from_residue"] if mutation else None,
            "to_residue": mutation["to_residue"] if mutation else None,
            "is_hotspot": hotspot,
            "detected_markers": detected_markers,
            "highlight_positions": highlight_positions,
            "heuristics": heuristics,
            "resistant_target": resistant_target,
            "not_resistant_target": not_resistant_target,
        }

    def _build_rationale(
        self,
        summary: dict[str, object],
        raw_model_probability: float,
        blended_probability: float,
    ) -> list[str]:
        rationale: list[str] = []
        gene_info = summary["gene_info"]
        mutation_label = summary["mutation_label"]
        markers = summary["detected_markers"]

        if gene_info and mutation_label:
            gene_name = gene_info["gene"]
            if summary["resistant_target"] is not None:
                rationale.append(
                    f"{gene_name} {mutation_label} matches a curated resistance-associated substitution."
                )
            elif summary["not_resistant_target"] is not None:
                rationale.append(
                    f"{gene_name} {mutation_label} is not in the high-risk resistance set for this prototype knowledge base."
                )
            elif summary["is_hotspot"]:
                rationale.append(
                    f"Residue {summary['position']} sits inside a known resistance hot spot for {gene_info['protein']}."
                )
            else:
                rationale.append(
                    f"The mutation was encoded as residue-level k-mers around {gene_name} {mutation_label}."
                )

        if summary["input_type"] == "sequence":
            rationale.append(
                f"3-mer vectorization found dominant signatures {', '.join(summary['top_kmers'][:3]) or 'N/A'} with GC content {summary['gc_content']:.2f}."
            )
        else:
            rationale.append(
                f"Mutation tokenization emphasized the signature pattern {', '.join(summary['top_kmers'][:3]) or 'N/A'}."
            )

        if markers:
            rationale.append(
                f"Biological evidence markers detected: {', '.join(markers[:3])}."
            )

        rationale.append(
            f"The logistic regression classifier assigned resistant probability {raw_model_probability:.2f}, which was then calibrated with curated biological priors to {blended_probability:.2f}."
        )
        return rationale[:4]

    def predict(
        self,
        raw_input: str,
        requested_type: str | None = None,
    ) -> dict[str, object]:
        summary = self.summarize_input(raw_input, requested_type)
        encoded = self.vectorizer.transform([self._feature_text(raw_input, requested_type)])
        model_probability = float(self.model.predict_proba(encoded)[0][1])
        biological_probability = clamp(0.5 + float(summary["heuristics"]))

        resistant_probability = (0.72 * model_probability) + (0.28 * biological_probability)

        if summary["resistant_target"] is not None:
            resistant_probability = max(
                resistant_probability, float(summary["resistant_target"])
            )
        if summary["not_resistant_target"] is not None:
            resistant_probability = min(
                resistant_probability, float(summary["not_resistant_target"])
            )

        resistant_probability = round(clamp(resistant_probability), 3)
        not_resistant_probability = round(1 - resistant_probability, 3)
        resistant = resistant_probability >= 0.5
        confidence = resistant_probability if resistant else not_resistant_probability

        prediction = "Resistant" if resistant else "Not Resistant"
        rationale = self._build_rationale(
            summary=summary,
            raw_model_probability=model_probability,
            blended_probability=resistant_probability,
        )

        gene_info = summary["gene_info"] or {}
        encoding_summary = {
            "strategy": "3-mer / residue-signature vectorization",
            "input_length": summary["input_length"],
            "gc_content": summary["gc_content"],
            "top_kmers": summary["top_kmers"],
            "detected_markers": summary["detected_markers"],
            "vector_dimensions": int(len(self.vectorizer.vocabulary_)),
        }
        pipeline = [
            {
                "name": "DNA Input",
                "detail": (
                    f"Normalized {summary['input_type']} input and prepared it for downstream encoding."
                ),
            },
            {
                "name": "Encoding",
                "detail": (
                    f"Generated {encoding_summary['strategy']} features with top signatures "
                    f"{', '.join(summary['top_kmers'][:3]) or 'N/A'}."
                ),
            },
            {
                "name": "ML Model Prediction",
                "detail": (
                    f"Logistic regression estimated resistant probability {model_probability:.2f}."
                ),
            },
            {
                "name": "LLM Reasoning (Evo 2)",
                "detail": (
                    "Curated mutation biology, antibiotic mechanism, and model signals were assembled for explanation synthesis."
                ),
            },
            {
                "name": "Final Output",
                "detail": f"Returned {prediction} with confidence {confidence:.2f}.",
            },
        ]

        return {
            "resistant": resistant,
            "prediction": prediction,
            "confidence": round(confidence, 3),
            "probability_resistant": resistant_probability,
            "probability_not_resistant": not_resistant_probability,
            "input_type": summary["input_type"],
            "normalized_input": summary["normalized_input"],
            "model_name": "Logistic Regression",
            "gene_info": gene_info or None,
            "mutation_label": summary["mutation_label"],
            "scientific_rationale": rationale,
            "encoding": encoding_summary,
            "pipeline": pipeline,
            "visualization": {
                "helix_length": HELIX_LENGTH,
                "highlight_positions": summary["highlight_positions"],
                "focus_label": summary["mutation_label"] or "Sequence anomaly scan",
                "prediction_tone": "resistant" if resistant else "not_resistant",
            },
        }


def get_known_mutation_catalog() -> list[dict[str, object]]:
    catalog: list[dict[str, object]] = []
    for info in GENE_LIBRARY.values():
        for change, resistant_probability in info["resistant_profiles"].items():
            catalog.append(
                {
                    "gene": info["display_gene"],
                    "mutation": change,
                    "antibiotic": info["antibiotic_class"],
                    "expected_prediction": "Resistant",
                    "resistant_probability_hint": resistant_probability,
                }
            )
    return catalog


_model_instance: ResistancePredictorModel | None = None


def get_model() -> ResistancePredictorModel:
    global _model_instance
    if _model_instance is None:
        _model_instance = ResistancePredictorModel()
    return _model_instance
