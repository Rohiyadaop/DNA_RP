import os
import json
import sys
import time
import requests
from pathlib import Path
from dotenv import load_dotenv
from pubchem import run_phase4


load_dotenv()
NVIDIA_API_KEY = os.getenv("ESMFOLD_API_KEY")



ESMFOLD_URL    = "https://health.api.nvidia.com/v1/biology/nvidia/esmfold"
MAX_SEQ_LENGTH = 1024  

INPUT_FILE     = "../fasta/phase1_output.json"
OUTPUT_FILE    = "phase3_output.json"
PDB_FILE       = "protein_structure.pdb"


def prepare_sequence(protein_seq: str) -> dict:
    """
    Prepare protein sequence for ESMFold submission.

    Handles the 1024 aa limit by truncating if needed.

    Args:
        protein_seq (str): Full amino acid sequence

    Returns:
        dict: {
            "sequence":         str,   # Final sequence to submit
            "original_length":  int,
            "final_length":     int,
            "was_truncated":    bool,
            "warnings":         list
        }
    """
    warnings = []
    original_length = len(protein_seq)

    if original_length > MAX_SEQ_LENGTH:
        protein_seq = protein_seq[:MAX_SEQ_LENGTH]
        warnings.append(
            f"Sequence truncated: {original_length} → {MAX_SEQ_LENGTH} aa "
            f"(NVIDIA ESMFold hard limit). "
            f"For full prediction, self-host ESMFold with no length limit."
        )
        print(f"  ⚠ Sequence truncated to {MAX_SEQ_LENGTH} aa (ESMFold limit)")
    else:
        print(f"  → Sequence length: {original_length} aa (within limit)")

    if 700 <= len(protein_seq) <= MAX_SEQ_LENGTH:
        warnings.append("Long sequence (700+ aa) — prediction may take 90-180 seconds.")
        print(f"  ⚠ Long sequence — may take 2-3 minutes")

    return {
        "sequence":        protein_seq,
        "original_length": original_length,
        "final_length":    len(protein_seq),
        "was_truncated":   original_length > MAX_SEQ_LENGTH,
        "warnings":        warnings,
    }


def call_esmfold_api(protein_seq: str, max_retries: int = 3) -> str:
    """
    Call NVIDIA NIM ESMFold API and return PDB content.

    Verified API details (docs.api.nvidia.com/nim/reference/meta-esmfold-infer):
      URL:     POST https://health.api.nvidia.com/v1/biology/nvidia/esmfold
      Headers: Authorization: Bearer <API_KEY>
               Content-Type: application/json
      Body:    { "sequence": "<amino_acid_string>" }
      Response: PDB format plain text (not JSON)

    Error handling:
      - 401 → Invalid API key
      - 422 → Invalid sequence
      - 429 → Rate limited (retry after wait)
      - 503 → Service down (retry)
      - Timeout → Retry with longer timeout

    Args:
        protein_seq  (str): Amino acid sequence
        max_retries  (int): Retry attempts on recoverable errors

    Returns:
        str: PDB format structure text

    Raises:
        ValueError:   Invalid API key or sequence
        RuntimeError: API failed after all retries
    """
    if not NVIDIA_API_KEY or NVIDIA_API_KEY == "your_nvidia_api_key_here":
        raise ValueError(
            "\n  NVIDIA API key not configured!\n"
            "  Steps to get a FREE key:\n"
            "    1. Go to: https://developer.nvidia.com/nim\n"
            "    2. Click 'Join NVIDIA Developer Program' (free)\n"
            "    3. Go to API Catalog → Healthcare → ESMFold\n"
            "    4. Click 'Get API Key'\n"
            "    5. Copy the key (starts with 'nvapi-...')\n"
            "    6. Paste it in this file: NVIDIA_API_KEY = 'nvapi-xxx...'"
        )

    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type":  "application/json",
        "Accept":        "application/json",
    }

    payload = {"sequence": protein_seq}

    print(f"  → Sending to NVIDIA NIM ESMFold API...")
    print(f"  → Sequence: {len(protein_seq)} amino acids")
    print(f"  → Estimated time: {max(30, len(protein_seq) // 10)}s...")

    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            start = time.time()

            response = requests.post(
                ESMFOLD_URL,
                headers=headers,
                json=payload,
                timeout=240,  
            )

            elapsed = round(time.time() - start, 1)


            if response.status_code == 200:
                pdb_text = response.text
                _validate_pdb(pdb_text)
                print(f"  ✅ ESMFold response received in {elapsed}s")
                return pdb_text

            elif response.status_code == 401:
                raise ValueError(
                    "API key rejected (401 Unauthorized).\n"
                    "  → Check your key at: https://developer.nvidia.com/nim\n"
                    "  → Make sure the key has Healthcare API access enabled."
                )

            elif response.status_code == 422:
                try:
                    detail = response.json().get("detail", response.text)
                except Exception:
                    detail = response.text
                raise ValueError(
                    f"Sequence rejected by ESMFold (422):\n  {detail}\n"
                    "  → Check for invalid amino acid characters in sequence."
                )

            elif response.status_code == 429:
                wait = 30 * attempt
                print(f"  ⚠ Rate limited (429). Waiting {wait}s before retry {attempt}/{max_retries}...")
                time.sleep(wait)
                last_error = RuntimeError("Rate limited — exceeded NVIDIA API free tier limits")
                continue

            elif response.status_code == 503:
                wait = 15 * attempt
                print(f"  ⚠ Service unavailable (503). Retrying in {wait}s ({attempt}/{max_retries})...")
                time.sleep(wait)
                last_error = RuntimeError("NVIDIA ESMFold service temporarily unavailable")
                continue

            else:
                raise RuntimeError(
                    f"Unexpected response (HTTP {response.status_code}):\n  {response.text[:300]}"
                )

        except (ValueError, RuntimeError):
            raise   # Don't retry on these

        except requests.exceptions.Timeout:
            print(f"  ⚠ Request timed out (attempt {attempt}/{max_retries})")
            last_error = RuntimeError(
                "ESMFold request timed out.\n"
                "  → Very long sequences (800+ aa) can take 3-4 minutes.\n"
                "  → Try again or truncate sequence further."
            )
            if attempt < max_retries:
                time.sleep(10)

        except requests.exceptions.ConnectionError as e:
            print(f"  ⚠ Connection error (attempt {attempt}/{max_retries}): {e}")
            last_error = RuntimeError(f"Cannot connect to NVIDIA API: {e}")
            if attempt < max_retries:
                time.sleep(10)

    raise last_error or RuntimeError("ESMFold API call failed after all retries")


def _validate_pdb(pdb_text: str) -> None:
    """
    Basic validation that response is actually a PDB file.

    Args:
        pdb_text (str): Response text from API

    Raises:
        RuntimeError: If response doesn't look like a valid PDB file
    """
    if not pdb_text or len(pdb_text) < 50:
        raise RuntimeError("ESMFold returned empty or very short response")

    lines = pdb_text.strip().split("\n")
    pdb_record_types = {"ATOM", "MODEL", "HEADER", "REMARK", "SEQRES", "END"}
    has_pdb_records = any(
        line[:6].strip() in pdb_record_types
        for line in lines[:30]
    )

    if not has_pdb_records:
        raise RuntimeError(
            f"Response doesn't look like a PDB file.\n"
            f"First 200 chars: {pdb_text[:200]}"
        )

def save_pdb(pdb_content: str, filepath: str = PDB_FILE) -> str:
    """
    Save PDB content to a .pdb file.

    Args:
        pdb_content (str): PDB format text
        filepath    (str): Output file path

    Returns:
        str: Absolute path to saved file
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(pdb_content)
    print(f"  → PDB file saved: {path.resolve()}")
    return str(path.resolve())


def analyze_pdb_structure(pdb_content: str) -> dict:
    """
    Extract structural statistics from a PDB file.

    What we extract:
      - Residue count (number of amino acids in structure)
      - Chain list
      - Atom count
      - pLDDT scores (stored in B-factor column by ESMFold)

    pLDDT (predicted Local Distance Difference Test):
      - ESMFold stores its confidence per-residue in the B-factor column
      - Range: 0 to 100
      - > 90  → Very High confidence (well-folded region)
      - 70-90 → High confidence
      - 50-70 → Low confidence (flexible/disordered region)
      - < 50  → Very Low (intrinsically disordered — no fixed structure)

    Args:
        pdb_content (str): PDB format text

    Returns:
        dict: Structural summary statistics
    """
    lines      = pdb_content.strip().split("\n")
    atom_lines = [l for l in lines if l.startswith("ATOM")]

    if not atom_lines:
        return {"error": "No ATOM records found in PDB — structure may be empty"}

    residues  = set()   
    chains    = set()
    b_factors = []      

    for line in atom_lines:
        try:
            chain    = line[21]
            res_num  = line[22:26].strip()
            b_factor = float(line[60:66].strip())

            residues.add((chain, res_num))
            chains.add(chain)
            b_factors.append(b_factor)

        except (ValueError, IndexError):
            continue

    if not b_factors:
        return {"error": "Could not extract B-factor (pLDDT) values from PDB"}

    avg_plddt = round(sum(b_factors) / len(b_factors), 2)
    min_plddt = round(min(b_factors), 2)
    max_plddt = round(max(b_factors), 2)

    very_high = sum(1 for b in b_factors if b >= 90) / len(b_factors) * 100
    high      = sum(1 for b in b_factors if 70 <= b < 90) / len(b_factors) * 100
    low       = sum(1 for b in b_factors if 50 <= b < 70) / len(b_factors) * 100
    very_low  = sum(1 for b in b_factors if b < 50) / len(b_factors) * 100

    if avg_plddt >= 90:
        confidence_level = "Very High"
        confidence_note  = "Excellent prediction — highly reliable structure"
    elif avg_plddt >= 70:
        confidence_level = "High"
        confidence_note  = "Good prediction — generally reliable"
    elif avg_plddt >= 50:
        confidence_level = "Low"
        confidence_note  = "Uncertain — protein may have disordered regions"
    else:
        confidence_level = "Very Low"
        confidence_note  = "Unreliable — protein likely intrinsically disordered"

    return {
        "num_residues":        len(residues),
        "num_chains":          len(chains),
        "chain_ids":           sorted(list(chains)),
        "num_atoms":           len(atom_lines),
        "avg_plddt":           avg_plddt,
        "min_plddt":           min_plddt,
        "max_plddt":           max_plddt,
        "confidence_level":    confidence_level,
        "confidence_note":     confidence_note,
        "plddt_breakdown": {
            "very_high_pct": round(very_high, 1),
            "high_pct":      round(high, 1),
            "low_pct":       round(low, 1),
            "very_low_pct":  round(very_low, 1),
        },
    }


def run_phase3() -> dict:
    """
    Run Phase 3: Predict 3D protein structure using ESMFold.

    Reads from phase1_output.json.
    Writes protein_structure.pdb and phase3_output.json.

    Returns:
        dict: Phase 3 results
    """
    print("\n" + "═" * 55)
    print("  PHASE 3 — ESMFold Protein Structure Prediction")
    print("═" * 55)

    if not Path(INPUT_FILE).exists():
        raise FileNotFoundError(
            f"'{INPUT_FILE}' not found!\n"
            f"Run Phase 1 first: python phase1_fasta_parser.py"
        )

    with open(INPUT_FILE) as f:
        phase1 = json.load(f)

    protein_seq = phase1["sequence"]["protein_seq"]
    seq_id      = phase1["sequence"]["sequence_id"]

    print(f"\n  Loaded: {seq_id} ({len(protein_seq)} aa)")

    print("\n  Preparing sequence...")
    prep = prepare_sequence(protein_seq)

    print("\n  Calling NVIDIA NIM ESMFold API...")
    pdb_content = call_esmfold_api(prep["sequence"])

    print("\n  Saving structure...")
    pdb_path = save_pdb(pdb_content)

    print("  Analyzing structure quality...")
    structure_stats = analyze_pdb_structure(pdb_content)

    output = {
        "phase":            3,
        "status":           "success",
        "sequence_id":      seq_id,
        "pdb_file":         pdb_path,
        "sequence_prep":    prep,
        "structure_stats":  structure_stats,
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print("\n" + "─" * 55)
    print("  PHASE 3 RESULTS")
    print("─" * 55)
    print(f"  Sequence ID       : {seq_id}")
    print(f"  Residues          : {structure_stats.get('num_residues', 'N/A')}")
    print(f"  Chains            : {structure_stats.get('chain_ids', 'N/A')}")
    print(f"  Total Atoms       : {structure_stats.get('num_atoms', 'N/A')}")
    print(f"  Avg pLDDT         : {structure_stats.get('avg_plddt', 'N/A')}")
    print(f"  Confidence        : {structure_stats.get('confidence_level', 'N/A')}")
    print(f"  Note              : {structure_stats.get('confidence_note', '')}")

    breakdown = structure_stats.get("plddt_breakdown", {})
    if breakdown:
        print(f"  pLDDT Breakdown   : VeryHigh={breakdown.get('very_high_pct')}%  "
              f"High={breakdown.get('high_pct')}%  "
              f"Low={breakdown.get('low_pct')}%  "
              f"VeryLow={breakdown.get('very_low_pct')}%")

    print(f"\n  PDB File          : {pdb_path}")
    print(f"  JSON Output       : {OUTPUT_FILE}")
    print(f"\n  View 3D structure :")
    print(f"    → Browser : https://molstar.org/viewer  (drag & drop the .pdb file)")
    print(f"    → Desktop : PyMOL or UCSF ChimeraX (free for academic use)")
    print("─" * 55)
    run_phase4()
    return output


if __name__ == "__main__":
    try:
        result = run_phase3()
        print("\n✅ Phase 3 complete! Run Phase 4 next:")
        print("   python phase4_pubchem.py <drug_name>")
        print("   Example: python phase4_pubchem.py ciprofloxacin")
        
    except FileNotFoundError as e:
        print(f"\n❌ File Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"\n❌ Config/Input Error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"\n❌ API Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise