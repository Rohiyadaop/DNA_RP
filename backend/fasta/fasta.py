import io
import json
import sys
from pathlib import Path
from Bio import SeqIO
from Bio.Seq import Seq
from card import run_phase2



OUTPUT_FILE = "phase1_output.json"

VALID_AA_CHARS = set("ACDEFGHIKLMNPQRSTVWYXBZUO*-")

DNA_CHARS = set("ATGCNU")

def detect_sequence_type(sequence: str) -> str:
    """
    Detect whether sequence is DNA or Protein.

    Logic:
      - If >= 90% of characters are in {A, T, G, C, N, U} → DNA
      - Otherwise → Protein

    Args:
        sequence (str): Raw sequence string (uppercase)

    Returns:
        str: "dna" or "protein"
    """
    if not sequence:
        raise ValueError("Cannot detect type of empty sequence")

    dna_count = sum(1 for c in sequence if c in DNA_CHARS)
    dna_ratio = dna_count / len(sequence)

    return "dna" if dna_ratio >= 0.90 else "protein"


def translate_dna_to_protein(dna_sequence: str) -> str:
    """
    Translate a DNA sequence to a protein sequence.

    Uses BioPython's standard codon table (table 1).
    Translation stops at the first stop codon (*).

    Args:
        dna_sequence (str): DNA string (only ATGCN allowed)

    Returns:
        str: Amino acid sequence

    Raises:
        ValueError: If translation produces empty result
    """
    clean_dna = "".join(c for c in dna_sequence.upper() if c in "ATGCN")

    bio_seq = Seq(clean_dna)
    protein = str(bio_seq.translate(to_stop=True))

    if not protein:
        raise ValueError(
            "DNA translation produced an empty protein sequence.\n"
            "Possible reasons:\n"
            "  1. Sequence starts with a stop codon (wrong reading frame)\n"
            "  2. Sequence is too short (< 3 nucleotides)\n"
            "  3. Sequence contains only stop codons\n"
            "Try shifting the reading frame (+1 or +2 bases from start)."
        )

    return protein


def validate_protein_sequence(protein_seq: str) -> dict:
    """
    Validate a protein sequence.

    Checks:
      - Not empty
      - No completely invalid characters
      - Minimum length (>= 10 aa for meaningful prediction)

    Args:
        protein_seq (str): Amino acid sequence

    Returns:
        dict: {
            "valid": bool,
            "length": int,
            "warnings": list[str],
            "cleaned_seq": str
        }
    """
    warnings = []

    cleaned = protein_seq.replace("*", "").replace(" ", "").replace("\n", "").upper()

    if not cleaned:
        raise ValueError("Protein sequence is empty after cleaning")

    invalid_chars = set(cleaned) - VALID_AA_CHARS
    if invalid_chars:
        warnings.append(f"Unusual characters found: {invalid_chars} — these will be kept but may affect predictions")

    if len(cleaned) < 10:
        raise ValueError(
            f"Protein too short ({len(cleaned)} aa). "
            f"Need at least 10 amino acids for reliable structure prediction."
        )

    if len(cleaned) < 30:
        warnings.append(
            f"Short sequence ({len(cleaned)} aa). "
            f"Predictions may be less reliable. Typical proteins are 100-500+ aa."
        )

    return {
        "valid": True,
        "length": len(cleaned),
        "warnings": warnings,
        "cleaned_seq": cleaned,
    }


def parse_fasta_text(fasta_text: str) -> list:
    """
    Parse a FASTA-formatted string into a list of records.

    Handles:
      - Single sequence
      - Multi-sequence FASTA (returns all records)
      - Missing header (adds a default one)

    Args:
        fasta_text (str): Raw FASTA text

    Returns:
        list[dict]: List of parsed sequence records
    """
    fasta_text = fasta_text.strip()

    if not fasta_text:
        raise ValueError("Empty input provided")

    if not fasta_text.startswith(">"):
        fasta_text = ">unknown_sequence\n" + fasta_text

    fasta_io = io.StringIO(fasta_text)

    try:
        records = list(SeqIO.parse(fasta_io, "fasta"))
    except Exception as e:
        raise ValueError(f"Failed to parse FASTA format: {e}")

    if not records:
        raise ValueError(
            "No sequences found in input. "
            "Make sure the format is: >header_line\\nSEQUENCE"
        )

    return records


def process_sequence(record) -> dict:
    """
    Process a single BioPython SeqRecord.

    Automatically detects type (DNA/protein) and translates if needed.

    Args:
        record: BioPython SeqRecord object

    Returns:
        dict: Complete processed sequence info
    """
    seq_str = str(record.seq).upper().strip()

    if not seq_str:
        raise ValueError(f"Sequence '{record.id}' is empty")

    seq_type = detect_sequence_type(seq_str)

    if seq_type == "dna":
        print(f"  → DNA detected ({len(seq_str)} bp) — translating to protein...")
        protein_seq = translate_dna_to_protein(seq_str)
        print(f"  → Translation complete: {len(protein_seq)} amino acids")
    else:
        protein_seq = seq_str
        print(f"  → Protein sequence detected ({len(protein_seq)} aa)")

    validation = validate_protein_sequence(protein_seq)

    if validation["warnings"]:
        for w in validation["warnings"]:
            print(f"  ⚠ Warning: {w}")

    return {
        "sequence_id":    record.id,
        "description":    record.description,
        "sequence_type":  seq_type,
        "original_seq":   seq_str,
        "protein_seq":    validation["cleaned_seq"],
        "protein_length": validation["length"],
        "is_dna":         seq_type == "dna",
        "warnings":       validation["warnings"],
    }
def run_phase1(fasta_input: str) -> dict:
    """
    Run Phase 1: Parse FASTA and prepare sequence for downstream analysis.

    Args:
        fasta_input (str): Raw FASTA text or path to .fasta file

    Returns:
        dict: Phase 1 results with all sequence info
    """
    print("\n" + "═" * 55)
    print("  PHASE 1 — FASTA Parser & Sequence Preparation")
    print("═" * 55)

    fasta_path = Path(fasta_input.strip())
    if fasta_path.exists() and fasta_path.suffix in (".fasta", ".fa", ".fna", ".faa"):
        print(f"\n  Loading FASTA file: {fasta_path}")
        fasta_text = fasta_path.read_text()
    else:
        fasta_text = fasta_input

    print("\n  Parsing FASTA...")
    records = parse_fasta_text(fasta_text)
    print(f"  Found {len(records)} sequence(s)")

    print(f"\n  Processing sequence 1 of {len(records)}...")
    processed = process_sequence(records[0])

    output = {
        "phase": 1,
        "status": "success",
        "total_sequences_in_file": len(records),
        "sequence": processed,
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print("\n" + "─" * 55)
    print("  PHASE 1 RESULTS")
    print("─" * 55)
    print(f"  Sequence ID    : {processed['sequence_id']}")
    print(f"  Input Type     : {'DNA (translated)' if processed['is_dna'] else 'Protein'}")
    print(f"  Protein Length : {processed['protein_length']} amino acids")
    if processed['warnings']:
        for w in processed['warnings']:
            print(f"  ⚠ {w}")
    print(f"\n  Output saved   : {OUTPUT_FILE}")
    print("─" * 55)
    return output


EXAMPLE_DNA_FASTA = """>E_coli_gyrA_Ser83Leu_quinolone_resistance
ATGAGCGACCTTGCGAGAGAAATTACACCGGTAACATTGAGCGAAATCGACCGCATCCGG
CAAATCGATCCCTACGTCGGCGAAAACATCGTCGGCATTGCCATGCAGCAGGTGCTGGAA
AAGCAGGGCATGAGCGAGCTGGAAGAGCAGTTCCAGCAGCAGTTCACCCGCTTCAAGCAG
ATCAACGACATGGTGCGCAACGACGAAGTCGTCACCATCGACCCGCAGGAAGTGGTCAAC"""

EXAMPLE_PROTEIN_FASTA = """>TEM1_beta_lactamase
MSIQHFRVALIPFFAAFCLPVFAHPETLVKVKDAEDQLGARVGYIELDLNSGKILESFRPE
ERFPMMSTFKVLLCGAVLSRVDAGQEQLGRRIHYSQNDLVEYSPVTEKHLTDGMTVRELCS
AAITMSDNTAANLLLTTIGGPKELTAFLHNMGDHVTRLDRWEPELNEAIPNDERDTTMPVAM"""


if __name__ == "__main__":
    if len(sys.argv) > 1:
        fasta_input = sys.argv[1]
    else:
        print("  No input provided — using example DNA sequence")
        print("  Usage: python phase1_fasta_parser.py <fasta_file_or_sequence>")
        fasta_input = EXAMPLE_DNA_FASTA

    try:
        result = run_phase1(fasta_input)
        print("\n✅ Phase 1 complete! Run Phase 2 next:")
        print("   python phase2_card_lookup.py")
        run_phase2()
    except ValueError as e:
        print(f"\n❌ Input Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise