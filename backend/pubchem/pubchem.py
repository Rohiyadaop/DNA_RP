import json
import sys
import requests
from pathlib import Path
from urllib.parse import quote
from diffdock import run_phase5
from utils import drug_name

INPUT_FILE  = "../fasta/phase1_output.json"
OUTPUT_FILE = "phase4_output.json"
SDF_FILE    = "antibiotic_structure.sdf"

PUBCHEM_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

DRUG_ALIASES = {
    "cipro":        "ciprofloxacin",
    "amox":         "amoxicillin",
    "augmentin":    "amoxicillin",
    "pen":          "penicillin",
    "tmp-smx":      "trimethoprim",
    "bactrim":      "sulfamethoxazole",
    "zithromax":    "azithromycin",
    "z-pak":        "azithromycin",
    "flagyl":       "metronidazole",
    "vanco":        "vancomycin",
    "genta":        "gentamicin",
    "tobra":        "tobramycin",
    "levo":         "levofloxacin",
    "moxi":         "moxifloxacin",
    "doxy":         "doxycycline",
    "minocin":      "minocycline",
    "erythro":      "erythromycin",
    "azithro":      "azithromycin",
    "clarithro":    "clarithromycin",
    "rifampin":     "rifampicin",
    "colistin":     "polymyxin e",
    "tmp":          "trimethoprim",
}

def resolve_drug_name(drug_name: str) -> str:
    """
    Resolve common aliases and abbreviations to standard names.

    Args:
        drug_name (str): User-provided drug name

    Returns:
        str: Resolved drug name for PubChem query
    """
    normalized = drug_name.strip().lower()
    resolved   = DRUG_ALIASES.get(normalized, normalized)

    if resolved != normalized:
        print(f"  → Resolved '{drug_name}' → '{resolved}'")

    return resolved


def get_compound_cid(drug_name: str) -> int:
    """
    Get PubChem Compound ID (CID) for a drug name.

    Searches by:
      1. Exact name match
      2. Synonym search

    Args:
        drug_name (str): Drug name to search

    Returns:
        int: PubChem CID

    Raises:
        ValueError: If compound not found in PubChem
    """
    print(f"  → Searching PubChem for: '{drug_name}'")

    url = f"{PUBCHEM_BASE}/compound/name/{quote(drug_name)}/cids/JSON"

    try:
        response = requests.get(url, timeout=30)

        if response.status_code == 200:
            data = response.json()
            cids = data.get("IdentifierList", {}).get("CID", [])
            if cids:
                cid = cids[0]
                print(f"  → Found CID: {cid}")
                return cid

        print(f"  → Exact match failed — trying synonym search...")
        url2 = f"{PUBCHEM_BASE}/compound/name/{quote(drug_name)}/cids/JSON?name_type=word"
        response2 = requests.get(url2, timeout=30)

        if response2.status_code == 200:
            data2 = response2.json()
            cids2 = data2.get("IdentifierList", {}).get("CID", [])
            if cids2:
                cid = cids2[0]
                print(f"  → Found via synonym: CID {cid}")
                return cid

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"PubChem search failed: {e}")

    raise ValueError(
        f"Drug '{drug_name}' not found in PubChem.\n"
        f"  Try:\n"
        f"    - Full generic name (e.g. 'ciprofloxacin' not 'cipro')\n"
        f"    - Chemical name (e.g. '1-cyclopropyl-6-fluoro...')\n"
        f"    - SMILES string\n"
        f"    - Check spelling at: https://pubchem.ncbi.nlm.nih.gov"
    )


def get_compound_properties(cid: int) -> dict:
    """
    Fetch compound properties from PubChem.

    Properties retrieved:
      - Molecular formula  (e.g. C17H18FN3O3)
      - Molecular weight   (e.g. 331.3 g/mol)
      - IUPAC name         (official chemical name)
      - SMILES             (2D structure string)
      - InChI              (standard identifier)
      - InChIKey           (short hash identifier)
      - XLogP              (lipophilicity — affects membrane penetration)
      - H-bond donors/acceptors

    Args:
        cid (int): PubChem CID

    Returns:
        dict: Compound properties
    """
    properties = [
        "MolecularFormula",
        "MolecularWeight",
        "IUPACName",
        "IsomericSMILES",
        "InChI",
        "InChIKey",
        "XLogP",
        "HBondDonorCount",
        "HBondAcceptorCount",
        "RotatableBondCount",
        "TPSA",
    ]

    url = (
        f"{PUBCHEM_BASE}/compound/cid/{cid}/property/"
        f"{','.join(properties)}/JSON"
    )

    response = requests.get(url, timeout=30)

    if response.status_code == 200:
        data = response.json()
        props = data.get("PropertyTable", {}).get("Properties", [{}])[0]
        return props
    else:
        print(f"  ⚠ Could not fetch properties (HTTP {response.status_code})")
        return {}


def get_compound_name(cid: int) -> str:
    """
    Get the preferred IUPAC name of a compound from its CID.

    Args:
        cid (int): PubChem CID

    Returns:
        str: Preferred name
    """
    url = f"{PUBCHEM_BASE}/compound/cid/{cid}/property/IUPACName/JSON"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            props = r.json().get("PropertyTable", {}).get("Properties", [{}])[0]
            return props.get("IUPACName", f"CID_{cid}")
    except Exception:
        pass
    return f"CID_{cid}"


def fetch_sdf_3d(cid: int) -> str:
    """
    Fetch 3D SDF structure from PubChem.

    PubChem provides pre-computed 3D conformers for most compounds.
    SDF (Structure Data File) format is required by DiffDock.

    Args:
        cid (int): PubChem CID

    Returns:
        str: SDF format 3D structure text

    Raises:
        ValueError: If 3D structure not available
    """
    print(f"  → Fetching 3D SDF for CID {cid}...")
    url = f"{PUBCHEM_BASE}/compound/cid/{cid}/SDF?record_type=3d"

    response = requests.get(url, timeout=30)

    if response.status_code == 200:
        sdf = response.text
        if len(sdf) > 100 and "V2000" in sdf or "V3000" in sdf:
            print(f"  ✅ 3D SDF retrieved ({len(sdf)} chars)")
            return sdf
        else:
            raise ValueError("Retrieved SDF doesn't appear valid")

    elif response.status_code == 404:
        raise ValueError(
            f"No 3D conformer available for CID {cid}.\n"
            "  → Will attempt 2D → 3D fallback"
        )
    else:
        raise RuntimeError(
            f"PubChem SDF fetch failed (HTTP {response.status_code}): {response.text[:200]}"
        )


def fetch_sdf_2d_fallback(cid: int) -> str:
    """
    Fallback: Fetch 2D SDF when 3D is not available.

    Some less common compounds only have 2D structures in PubChem.
    DiffDock can still use 2D SDF but results may be less accurate.

    Args:
        cid (int): PubChem CID

    Returns:
        str: SDF format 2D structure text
    """
    print(f"  → Falling back to 2D SDF for CID {cid}...")
    url = f"{PUBCHEM_BASE}/compound/cid/{cid}/SDF"

    response = requests.get(url, timeout=30)

    if response.status_code == 200:
        sdf = response.text
        print(f"  ✅ 2D SDF retrieved ({len(sdf)} chars)")
        print(f"  ⚠ Note: 2D structure used — DiffDock may give less accurate docking")
        return sdf
    else:
        raise RuntimeError(
            f"2D SDF also unavailable (HTTP {response.status_code})"
        )


def save_sdf(sdf_content: str, filepath: str = SDF_FILE) -> str:
    """
    Save SDF content to file.

    Args:
        sdf_content (str): SDF format text
        filepath    (str): Output path

    Returns:
        str: Absolute path to saved file
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(sdf_content)
    print(f"  → SDF file saved: {path.resolve()}")
    return str(path.resolve())


def interpret_properties(props: dict) -> dict:
    """
    Add clinical interpretation to compound properties.

    Checks Lipinski's Rule of Five for drug-likeness:
      - MW <= 500 Da
      - XLogP <= 5
      - H-bond donors <= 5
      - H-bond acceptors <= 10

    Args:
        props (dict): PubChem properties dict

    Returns:
        dict: Properties with interpretation added
    """
    mw       = props.get("MolecularWeight", 0)
    xlogp    = props.get("XLogP", 0)
    hbd      = props.get("HBondDonorCount", 0)
    hba      = props.get("HBondAcceptorCount", 0)

    try:
        mw    = float(mw)
        xlogp = float(xlogp)
        hbd   = int(hbd)
        hba   = int(hba)
    except (TypeError, ValueError):
        pass

    lipinski_pass = (
        isinstance(mw, float) and mw <= 500 and
        isinstance(xlogp, float) and xlogp <= 5 and
        isinstance(hbd, int) and hbd <= 5 and
        isinstance(hba, int) and hba <= 10
    )

    return {
        **props,
        "lipinski_rule_of_5": lipinski_pass,
        "lipinski_note": (
            "Passes Lipinski RO5 — good oral bioavailability predicted"
            if lipinski_pass else
            "Fails Lipinski RO5 — may have poor oral absorption (e.g. large antibiotics like vancomycin are IV only)"
        ),
    }


# ══════════════════════════════════════════════════════════════════
# MAIN PHASE FUNCTION
# ══════════════════════════════════════════════════════════════════

def run_phase4() -> dict:
    """
    Run Phase 4: Fetch antibiotic 3D structure from PubChem.

    Args:
        drug_name (str): Antibiotic name (e.g. "ciprofloxacin")

    Returns:
        dict: Phase 4 results
    """
    print("\n" + "═" * 55)
    print("  PHASE 4 — Antibiotic 3D Structure (PubChem)")
    print("═" * 55)

    seq_id = "unknown"
    if Path(INPUT_FILE).exists():
        with open(INPUT_FILE) as f:
            phase1 = json.load(f)
            seq_id = phase1["sequence"]["sequence_id"]
        print(f"\n  Bacterial sequence: {seq_id}")

    print(f"  Antibiotic target : {drug_name}")

    resolved_name = resolve_drug_name(drug_name)

    print("\n  Looking up compound in PubChem...")
    cid = get_compound_cid(resolved_name)

    print("  Fetching compound properties...")
    raw_props = get_compound_properties(cid)
    properties = interpret_properties(raw_props)

    print("  Fetching 3D structure...")
    sdf_content = None
    structure_type = "3D"

    try:
        sdf_content = fetch_sdf_3d(cid)
    except ValueError:
        print(f"  ⚠ 3D structure not available, trying 2D fallback...")
        sdf_content = fetch_sdf_2d_fallback(cid)
        structure_type = "2D"

    sdf_path = save_sdf(sdf_content)

    output = {
        "phase":           4,
        "status":          "success",
        "sequence_id":     seq_id,
        "drug_name":       drug_name,
        "resolved_name":   resolved_name,
        "pubchem_cid":     cid,
        "structure_type":  structure_type,
        "sdf_file":        sdf_path,
        "properties":      properties,
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print("\n" + "─" * 55)
    print("  PHASE 4 RESULTS")
    print("─" * 55)
    print(f"  Drug Name         : {drug_name}")
    print(f"  PubChem CID       : {cid}")
    print(f"  Molecular Formula : {properties.get('MolecularFormula', 'N/A')}")
    print(f"  Molecular Weight  : {properties.get('MolecularWeight', 'N/A')} g/mol")
    print(f"  Structure Type    : {structure_type}")
    print(f"  Lipinski RO5      : {'✅ Pass' if properties.get('lipinski_rule_of_5') else '⚠ Fail'}")
    print(f"  Note              : {properties.get('lipinski_note', '')}")
    print(f"\n  SDF File          : {sdf_path}")
    print(f"  JSON Output       : {OUTPUT_FILE}")
    print("─" * 55)
    
    return output


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("  Usage: python phase4_pubchem.py <drug_name>")
        print("  Example: python phase4_pubchem.py ciprofloxacin")
        print("\n  Common antibiotics you can try:")
        print("    ciprofloxacin, ampicillin, tetracycline, vancomycin,")
        print("    erythromycin, rifampicin, gentamicin, doxycycline")
        print("\n  Using default: ciprofloxacin")
        drug_name = "ciprofloxacin"
    else:
        drug_name = " ".join(sys.argv[1:])

    try:
        result = run_phase4(drug_name)
        print("\n✅ Phase 4 complete! Run Phase 5 next:")
        print("   python phase5_diffdock.py")
        run_phase5()
    except ValueError as e:
        print(f"\n❌ Drug Error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"\n❌ API Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise