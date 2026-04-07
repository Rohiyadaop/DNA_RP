from __future__ import annotations
import io
from typing import Tuple
from Bio import SeqIO
from Bio.Seq import Seq


DNA_ALPHABET = {"A", "T", "G", "C"}


def parse_fasta_contents(contents: bytes) -> Tuple[str, str]:
    try:
        text = contents.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("FASTA file must be UTF-8 encoded text.") from exc

    records = list(SeqIO.parse(io.StringIO(text), "fasta"))
    if not records:
        raise ValueError("No FASTA records were found in the uploaded file.")

    record = records[0]
    sequence = str(record.seq).upper().strip()
    invalid = sorted(set(sequence) - DNA_ALPHABET)
    if invalid:
        raise ValueError(f"Sequence contains invalid DNA symbols: {invalid}")
    return record.id or "uploaded_sequence", sequence


def gc_content(sequence: str) -> float:
    gc_count = sequence.count("G") + sequence.count("C")
    return round(gc_count / max(1, len(sequence)), 4)


def to_fasta_text(sequence_id: str, sequence: str) -> str:
    return f">{sequence_id}\n{sequence}\n"


def translate_dna_frame(sequence: str, frame: int = 0) -> str:
    frame = frame % 3
    trimmed = sequence[frame : len(sequence) - ((len(sequence) - frame) % 3)]
    if not trimmed:
        return ""
    return str(Seq(trimmed).translate())


def longest_protein_from_dna(sequence: str) -> str:
    best = ""
    for frame in range(3):
        translated = translate_dna_frame(sequence, frame=frame)
        for fragment in translated.split("*"):
            fragment = fragment.strip()
            if len(fragment) > len(best):
                best = fragment
    return best
