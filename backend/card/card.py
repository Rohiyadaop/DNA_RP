import json
import sys
import requests
from pathlib import Path
from esmfold import run_phase3


INPUT_FILE  = "../fasta/phase1_output.json"
OUTPUT_FILE = "phase2_output.json"

CARD_RGI_URL = "https://card.mcmaster.ca/analyze/rgi"

# CARD ARO (Antibiotic Resistance Ontology) categories
# Used for fallback keyword detection
RESISTANCE_MARKERS = {
    "Beta-Lactam": {
        "genes": ["TEM", "SHV", "CTX-M", "KPC", "NDM", "OXA", "VIM", "IMP", "CMY", "AmpC"],
        "antibiotics": ["Penicillin", "Ampicillin", "Amoxicillin", "Cephalosporin", "Carbapenem"],
        "mechanism": "Beta-lactamase enzyme — hydrolyzes beta-lactam ring",
    },
    "Tetracycline": {
        "genes": ["tetA", "tetB", "tetC", "tetM", "tetO", "tetW", "tetX"],
        "antibiotics": ["Tetracycline", "Doxycycline", "Minocycline"],
        "mechanism": "Efflux pump or ribosomal protection",
    },
    "Aminoglycoside": {
        "genes": ["aac", "ant", "aph", "armA", "rmtA", "rmtB", "npmA"],
        "antibiotics": ["Gentamicin", "Amikacin", "Tobramycin", "Streptomycin"],
        "mechanism": "Aminoglycoside-modifying enzymes or 16S rRNA methylation",
    },
    "Fluoroquinolone": {
        "genes": ["gyrA", "gyrB", "parC", "parE", "qnrA", "qnrB", "qnrS", "qepA", "oqxA"],
        "antibiotics": ["Ciprofloxacin", "Levofloxacin", "Moxifloxacin", "Norfloxacin"],
        "mechanism": "Target site mutation or efflux pump",
    },
    "Vancomycin": {
        "genes": ["vanA", "vanB", "vanC", "vanD", "vanE", "vanG", "vanH", "vanX"],
        "antibiotics": ["Vancomycin", "Teicoplanin"],
        "mechanism": "Altered peptidoglycan precursor target",
    },
    "Macrolide": {
        "genes": ["ermA", "ermB", "ermC", "mefA", "mefE", "msrA", "oleC"],
        "antibiotics": ["Erythromycin", "Azithromycin", "Clarithromycin"],
        "mechanism": "Ribosomal methylation or efflux pump",
    },
    "Sulfonamide": {
        "genes": ["sul1", "sul2", "sul3", "dhps"],
        "antibiotics": ["Sulfamethoxazole", "Trimethoprim-Sulfamethoxazole"],
        "mechanism": "Altered dihydropteroate synthase",
    },
    "Chloramphenicol": {
        "genes": ["cat", "cmlA", "floR", "cfrA"],
        "antibiotics": ["Chloramphenicol", "Florfenicol"],
        "mechanism": "Acetyltransferase enzyme or efflux pump",
    },
    "Colistin": {
        "genes": ["mcr-1", "mcr-2", "mcr-3", "mcr-4", "mcr-5", "pmrA", "pmrB", "mgrB"],
        "antibiotics": ["Colistin", "Polymyxin B"],
        "mechanism": "Lipid A modification",
    },
    "Rifampicin": {
        "genes": ["rpoB", "arr", "iri"],
        "antibiotics": ["Rifampicin", "Rifampin"],
        "mechanism": "RNA polymerase beta subunit mutation or ADP-ribosylation",
    },
}


def query_card_api(protein_seq: str) -> dict:
    """
    Submit protein sequence to CARD RGI (Resistance Gene Identifier) API.

    CARD RGI matches sequences against:
      - Perfect matches to known AMR genes
      - BLAST-based homology matches
      - Protein variant models

    API: https://card.mcmaster.ca/analyze/rgi
    Method: POST form-data
    Fields:
      - data:       FASTA sequence text
      - input_type: "protein"

    Args:
        protein_seq (str): Amino acid sequence

    Returns:
        dict: CARD API result or raises on failure
    """
    print("  → Submitting to CARD RGI API...")

    fasta_payload = f">query_sequence\n{protein_seq}"

    try:
        response = requests.post(
            CARD_RGI_URL,
            data={
                "data": fasta_payload,
                "input_type": "protein",
            },
            timeout=90,
        )

        if response.status_code == 200:
            try:
                data = response.json()
                return {"status": "success", "raw": data}
            except json.JSONDecodeError:
                return {"status": "error", "message": "CARD returned non-JSON response"}

        elif response.status_code == 429:
            return {"status": "rate_limited", "message": "CARD API rate limit hit. Try again in 60s."}

        elif response.status_code == 503:
            return {"status": "unavailable", "message": "CARD API temporarily unavailable"}

        else:
            return {
                "status": "error",
                "message": f"CARD returned HTTP {response.status_code}: {response.text[:200]}"
            }

    except requests.exceptions.Timeout:
        return {"status": "timeout", "message": "CARD API timed out after 90 seconds"}

    except requests.exceptions.ConnectionError as e:
        return {"status": "connection_error", "message": f"Cannot reach CARD API: {e}"}


def parse_card_response(card_raw: list) -> list:
    """
    Parse raw CARD API response into clean hit records.

    CARD returns a list of hit objects. Each hit has:
      - Model_Name: Gene/model name
      - ARO_name: Antibiotic Resistance Ontology term
      - Drug_Class: Antibiotic class
      - Resistance_Mechanism: How resistance works
      - Identity: % sequence identity
      - Bit-score: BLAST bit score

    Args:
        card_raw: Raw list from CARD JSON response

    Returns:
        list[dict]: Cleaned hit records
    """
    if not isinstance(card_raw, list):
        return []

    hits = []
    for item in card_raw:
        if not isinstance(item, dict):
            continue

        hit = {
            "gene":      item.get("Model_Name", "Unknown"),
            "aro_name":  item.get("ARO_name", ""),
            "drug_class": item.get("Drug_Class", "Unknown"),
            "mechanism": item.get("Resistance_Mechanism", "Unknown"),
            "identity":  item.get("Identity", 0),
            "bitscore":  item.get("Bit-score", 0),
            "evalue":    item.get("E-value", "N/A"),
            "source":    "CARD_RGI",
        }
        hits.append(hit)

    hits.sort(key=lambda x: x.get("identity", 0), reverse=True)
    return hits


def keyword_resistance_scan(protein_seq: str) -> list:
    """
    Fallback resistance detection using known gene name markers.

    This is a simple keyword match — not as accurate as CARD RGI.
    Used when CARD API is unavailable.

    Args:
        protein_seq (str): Amino acid sequence (uppercase)

    Returns:
        list[dict]: Detected resistance markers
    """
    print("  → Running keyword-based fallback scan...")

    seq_upper = protein_seq.upper()
    detected = []

    for drug_class, info in RESISTANCE_MARKERS.items():
        for gene in info["genes"]:
            if gene.upper() in seq_upper:
                detected.append({
                    "gene":      gene,
                    "aro_name":  f"{gene} (keyword match)",
                    "drug_class": drug_class,
                    "mechanism": info["mechanism"],
                    "antibiotics_affected": info["antibiotics"],
                    "identity":  None,
                    "bitscore":  None,
                    "source":    "keyword_fallback",
                    "note":      "Keyword match only — low confidence. Run CARD RGI locally for validation."
                })

    return detected


def summarize_resistance(hits: list) -> dict:
    """
    Summarize resistance profile from detected hits.

    Args:
        hits (list): List of resistance gene hits

    Returns:
        dict: Resistance summary
    """
    if not hits:
        return {
            "resistance_found": False,
            "drug_classes_affected": [],
            "num_genes": 0,
            "risk_level": "Low",
            "summary": "No known resistance genes detected",
        }

    drug_classes = list(set(h["drug_class"] for h in hits if h.get("drug_class")))
    genes        = list(set(h["gene"] for h in hits if h.get("gene")))

    if len(drug_classes) >= 3:
        risk_level = "Critical — Multi-Drug Resistant (MDR)"
    elif len(drug_classes) == 2:
        risk_level = "High — Resistant to multiple drug classes"
    elif len(drug_classes) == 1:
        risk_level = "Moderate — Resistant to one drug class"
    else:
        risk_level = "Low"

    return {
        "resistance_found":      True,
        "drug_classes_affected": drug_classes,
        "genes_detected":        genes,
        "num_genes":             len(genes),
        "num_drug_classes":      len(drug_classes),
        "risk_level":            risk_level,
        "summary":               f"{len(genes)} resistance gene(s) found affecting {len(drug_classes)} drug class(es)",
    }


# ══════════════════════════════════════════════════════════════════
# MAIN PHASE FUNCTION
# ══════════════════════════════════════════════════════════════════

def run_phase2() -> dict:
    """
    Run Phase 2: CARD database lookup for resistance genes.

    Reads from phase1_output.json.
    Writes to phase2_output.json.

    Returns:
        dict: Phase 2 results
    """
    print("\n" + "═" * 55)
    print("  PHASE 2 — CARD Database AMR Gene Lookup")
    print("═" * 55)

    if not Path(INPUT_FILE).exists():
        raise FileNotFoundError(
            f"'{INPUT_FILE}' not found!\n"
            f"Please run Phase 1 first: python phase1_fasta_parser.py"
        )

    with open(INPUT_FILE) as f:
        phase1 = json.load(f)

    protein_seq = phase1["sequence"]["protein_seq"]
    seq_id      = phase1["sequence"]["sequence_id"]

    print(f"\n  Loaded: {seq_id} ({len(protein_seq)} aa)")
    print("\n  Querying CARD Resistance Gene Identifier...")

    api_result = query_card_api(protein_seq)
    hits = []
    data_source = ""

    if api_result["status"] == "success":
        raw_hits = api_result.get("raw", [])
        hits = parse_card_response(raw_hits)
        data_source = "CARD_RGI_API"
        print(f"  ✅ CARD API responded — {len(hits)} resistance gene(s) found")
    else:
        print(f"  ⚠ CARD API unavailable ({api_result['status']}): {api_result.get('message', '')}")
        print("  → Using keyword-based fallback detection...")
        hits = keyword_resistance_scan(protein_seq)
        data_source = "keyword_fallback"
        print(f"  → {len(hits)} potential resistance marker(s) found via keywords")

    summary = summarize_resistance(hits)

    output = {
        "phase":        2,
        "status":       "success",
        "sequence_id":  seq_id,
        "data_source":  data_source,
        "hits":         hits,
        "summary":      summary,
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print("\n" + "─" * 55)
    print("  PHASE 2 RESULTS")
    print("─" * 55)
    print(f"  Resistance Found   : {summary['resistance_found']}")
    print(f"  Genes Detected     : {summary.get('num_genes', 0)}")
    print(f"  Drug Classes       : {', '.join(summary.get('drug_classes_affected', [])) or 'None'}")
    print(f"  Risk Level         : {summary['risk_level']}")
    print(f"  Data Source        : {data_source}")
    print(f"\n  Output saved       : {OUTPUT_FILE}")
    print("─" * 55)
    run_phase3()
    return output


if __name__ == "__main__":
    try:
        result = run_phase2()
        print("\n✅ Phase 2 complete! Run Phase 3 next:")
        print("   python phase3_esmfold.py")
        
    except FileNotFoundError as e:
        print(f"\n❌ File Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise