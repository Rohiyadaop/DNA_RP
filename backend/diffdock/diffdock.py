import os
import json
import sys
import time
import requests
from pathlib import Path
from dotenv import load_dotenv
 
 
load_dotenv()
NVIDIA_API_KEY = os.getenv("DIFFDOCK_API_KEY")
 
DIFFDOCK_URL = "https://health.api.nvidia.com/v1/biology/mit/diffdock"
 
DEFAULT_NUM_POSES      = 10    
DEFAULT_TIME_DIVISIONS = 20    
DEFAULT_STEPS          = 18    
DEFAULT_SAVE_TRAJECTORY = False
DEFAULT_IS_STAGED       = False
 
INPUT_FILE_P3  = "../esmfold/phase3_output.json"
INPUT_FILE_P4  = "../pubchem/phase4_output.json"
OUTPUT_FILE    = "phase5_output.json"
RAW_RESULT_FILE = "diffdock_raw_result.json"  
BEST_POSE_FILE = "docking_best_pose.sdf"
 
 
def load_inputs() -> dict:
    """
    Load PDB and SDF files from Phase 3 and Phase 4 outputs.
 
    Returns:
        dict: {
            "pdb_content": str,    # Protein structure (PDB format)
            "sdf_content": str,    # Antibiotic structure (SDF format)
            "protein_id":  str,
            "drug_name":   str,
            "pdb_file":    str,
            "sdf_file":    str,
        }
 
    Raises:
        FileNotFoundError: If phase outputs missing
    """
    for f in [INPUT_FILE_P3, INPUT_FILE_P4]:
        if not Path(f).exists():
            raise FileNotFoundError(
                f"'{f}' not found!\n"
                f"Make sure Phase 3 and Phase 4 have completed successfully."
            )
 
    with open(INPUT_FILE_P3) as f:
        phase3 = json.load(f)
    with open(INPUT_FILE_P4) as f:
        phase4 = json.load(f)
 
    pdb_file = phase3.get("pdb_file", "protein_structure.pdb")
    sdf_file = phase4.get("sdf_file", "antibiotic_structure.sdf")
 
    if not Path(pdb_file).exists():
        raise FileNotFoundError(
            f"PDB file not found: {pdb_file}\n"
            "Re-run Phase 3 to regenerate the protein structure."
        )
 
    if not Path(sdf_file).exists():
        raise FileNotFoundError(
            f"SDF file not found: {sdf_file}\n"
            "Re-run Phase 4 to regenerate the antibiotic structure."
        )
 
    pdb_content = Path(pdb_file).read_text()
    sdf_content = Path(sdf_file).read_text()
 
    print(f"  → Protein PDB    : {pdb_file} ({len(pdb_content)} chars)")
    print(f"  → Antibiotic SDF : {sdf_file} ({len(sdf_content)} chars)")
 
    return {
        "pdb_content": pdb_content,
        "sdf_content": sdf_content,
        "protein_id":  phase3.get("sequence_id", "unknown"),
        "drug_name":   phase4.get("drug_name", "unknown"),
        "drug_cid":    phase4.get("pubchem_cid"),
        "pdb_file":    pdb_file,
        "sdf_file":    sdf_file,
    }
 
 
def call_diffdock_api(
    pdb_content:    str,
    sdf_content:    str,
    num_poses:      int = DEFAULT_NUM_POSES,
    time_divisions: int = DEFAULT_TIME_DIVISIONS,
    steps:          int = DEFAULT_STEPS,
    max_retries:    int = 3,
) -> dict:
    """
    Call NVIDIA NIM DiffDock API for molecular docking.
 
    Args:
        pdb_content    (str): Protein structure in PDB format
        sdf_content    (str): Ligand structure in SDF format
        num_poses      (int): Number of docking poses to generate
        time_divisions (int): Diffusion time divisions (accuracy vs speed)
        steps          (int): Reverse diffusion steps
        max_retries    (int): Retry attempts
 
    Returns:
        dict: Raw DiffDock response JSON
 
    Raises:
        ValueError:   Invalid API key or input
        RuntimeError: API failure after all retries
    """
    if not NVIDIA_API_KEY or NVIDIA_API_KEY == "your_nvidia_api_key_here":
        raise ValueError(
            "\n  NVIDIA API key not set!\n"
            "  Get free key from: https://developer.nvidia.com/nim\n"
            "  Then set NVIDIA_API_KEY in .env file."
        )
 
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type":  "application/json",
        "Accept":        "application/json",
    }
 
    protein_escaped = pdb_content.replace("\n", "\\n")
    ligand_escaped  = sdf_content.replace("\n", "\\n")
 
    payload = {
        "ligand":           ligand_escaped,
        "ligand_file_type": "sdf",
        "protein":          protein_escaped,
        "num_poses":        num_poses,
        "time_divisions":   time_divisions,
        "steps":            steps,
        "save_trajectory":  DEFAULT_SAVE_TRAJECTORY,
        "is_staged":        DEFAULT_IS_STAGED,
    }
 
    print(f"  → Sending to NVIDIA NIM DiffDock...")
    print(f"  → Requesting {num_poses} binding poses")
    print(f"  → This may take 60-300 seconds...")
 
    last_error = None
 
    for attempt in range(1, max_retries + 1):
        try:
            start = time.time()
 
            response = requests.post(
                DIFFDOCK_URL,
                headers=headers,
                json=payload,
                timeout=360,   
            )
 
            elapsed = round(time.time() - start, 1)
 
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ DiffDock completed in {elapsed}s")
                
                # NEW: Save raw result for frontend visualization
                with open(RAW_RESULT_FILE, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"  → Raw result saved to {RAW_RESULT_FILE}")
                
                return result
 
            elif response.status_code == 401:
                raise ValueError(
                    "API key rejected (401). "
                    "Check key at: developer.nvidia.com/nim"
                )
 
            elif response.status_code == 422:
                try:
                    detail = response.json().get("detail", response.text)
                except Exception:
                    detail = response.text
                raise ValueError(
                    f"DiffDock rejected input (422):\n  {detail}\n"
                    "  → Check that PDB and SDF files are valid format."
                )
 
            elif response.status_code == 429:
                wait = 60 * attempt
                print(f"  ⚠ Rate limited. Waiting {wait}s (attempt {attempt}/{max_retries})...")
                time.sleep(wait)
                last_error = RuntimeError("Rate limited by NVIDIA API")
                continue
 
            elif response.status_code == 503:
                wait = 30 * attempt
                print(f"  ⚠ Service unavailable. Retrying in {wait}s ({attempt}/{max_retries})...")
                time.sleep(wait)
                last_error = RuntimeError("DiffDock service unavailable")
                continue
 
            else:
                raise RuntimeError(
                    f"DiffDock API error (HTTP {response.status_code}): {response.text[:300]}"
                )
 
        except (ValueError, RuntimeError):
            raise
 
        except requests.exceptions.Timeout:
            print(f"  ⚠ Timeout on attempt {attempt}/{max_retries}")
            last_error = RuntimeError("DiffDock timed out — the protein may be too large")
            if attempt < max_retries:
                time.sleep(15)
 
        except requests.exceptions.ConnectionError as e:
            print(f"  ⚠ Connection error: {e}")
            last_error = RuntimeError(f"Cannot connect to NVIDIA API: {e}")
            if attempt < max_retries:
                time.sleep(10)
 
    raise last_error or RuntimeError("DiffDock API call failed after all retries")
 
 
def parse_docking_results(raw_result: dict) -> dict:
    """
    Parse raw DiffDock JSON response into structured results.
 
    Args:
        raw_result (dict): Raw JSON from DiffDock API
 
    Returns:
        dict: Parsed and scored results with ligand_positions included
    """
    scores    = raw_result.get("position_confidence", [])
    positions = raw_result.get("ligand_positions", [])
    best_pose = raw_result.get("best_pose", "")
 
    if not scores:
        print("  ⚠ No scores returned from DiffDock")
        return {
            "num_poses":        0,
            "scores":           [],
            "best_score":       None,
            "avg_score":        None,
            "best_pose_sdf":    best_pose,
            "ligand_positions": positions,  # NEW: Include positions
            "pose_details":     [],
            "binding_summary":  "No docking results",
            "resistance_likely": True,
        }
 
    num_poses  = len(scores)
    best_score = min(scores)       
    avg_score  = sum(scores) / num_poses
    best_idx   = scores.index(best_score)
 
    pose_details = []
    for i, score in enumerate(scores):
        pose_details.append({
            "pose_number":    i + 1,
            "score":          round(score, 4),
            "is_best":        (i == best_idx),
            "interpretation": _interpret_score(score),
            "num_atoms":      len(positions[i]) if i < len(positions) else 0,  # NEW
        })
 
    pose_details.sort(key=lambda x: x["score"])
 
    binding_assessment, resistance_likely = _assess_binding(best_score)
 
    print(f"  → {num_poses} poses generated")
    print(f"  → Best score: {round(best_score, 4)} ({binding_assessment})")
 
    return {
        "num_poses":         num_poses,
        "scores":            [round(s, 4) for s in scores],
        "best_score":        round(best_score, 4),
        "avg_score":         round(avg_score, 4),
        "best_pose_idx":     best_idx,
        "best_pose_sdf":     best_pose,
        "ligand_positions":  positions,  # NEW: Include for 3D visualization
        "pose_details":      pose_details,
        "binding_assessment": binding_assessment,
        "resistance_likely":  resistance_likely,
    }
 
 
def _interpret_score(score: float) -> str:
    """Return human-readable interpretation for a single DiffDock score."""
    if score < -5:
        return "Strong binding"
    elif score < -2:
        return "Moderate binding"
    elif score < 0:
        return "Weak binding"
    else:
        return "Very poor binding"
 
 
def _assess_binding(best_score: float) -> tuple:
    """
    Return (assessment_string, resistance_likely_bool) from best score.
 
    Returns:
        tuple: (str, bool)
    """
    if best_score < -5:
        return (
            "Strong binding predicted — antibiotic likely EFFECTIVE against this target",
            False,
        )
    elif best_score < -2:
        return (
            "Moderate binding — antibiotic may be PARTIALLY effective",
            True,
        )
    elif best_score < 0:
        return (
            "Weak binding — RESISTANCE likely present, antibiotic may fail",
            True,
        )
    else:
        return (
            "Very poor binding — STRONG RESISTANCE predicted, antibiotic will likely fail",
            True,
        )
 
 
def save_best_pose(best_pose_sdf: str, filepath: str = BEST_POSE_FILE) -> str:
    """
    Save the best docking pose SDF to file.
 
    Args:
        best_pose_sdf (str): SDF content of best pose
        filepath      (str): Output path
 
    Returns:
        str: Absolute path
    """
    if not best_pose_sdf:
        print("  ⚠ No best pose SDF to save")
        return ""
 
    path = Path(filepath)
    path.write_text(best_pose_sdf)
    print(f"  → Best pose saved: {path.resolve()}")
    return str(path.resolve())
 
 
def run_phase5(num_poses: int = DEFAULT_NUM_POSES) -> dict:
    """
    Run Phase 5: DiffDock molecular docking.
 
    Reads from phase3_output.json and phase4_output.json.
    Writes phase5_output.json, diffdock_raw_result.json, and docking_best_pose.sdf.
 
    Args:
        num_poses (int): Number of binding poses to generate
 
    Returns:
        dict: Phase 5 results
    """
    print("\n" + "═" * 55)
    print("  PHASE 5 — DiffDock Molecular Docking")
    print("═" * 55)
 
    print("\n  Loading protein and antibiotic structures...")
    inputs = load_inputs()
 
    print(f"\n  Protein  : {inputs['protein_id']}")
    print(f"  Antibiotic: {inputs['drug_name']}")
 
    print("\n  Calling NVIDIA NIM DiffDock API...")
    raw_result = call_diffdock_api(
        pdb_content=inputs["pdb_content"],
        sdf_content=inputs["sdf_content"],
        num_poses=num_poses,
    )
 
    print("\n  Parsing docking results...")
    docking = parse_docking_results(raw_result)
 
    best_pose_path = save_best_pose(docking.get("best_pose_sdf", ""))
 
    output = {
        "phase":          5,
        "status":         "success",
        "protein_id":     inputs["protein_id"],
        "drug_name":      inputs["drug_name"],
        "drug_cid":       inputs.get("drug_cid"),
        "docking_results": docking,
        "best_pose_file": best_pose_path,
    }
 
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)
 
    print("\n" + "─" * 55)
    print("  PHASE 5 RESULTS")
    print("─" * 55)
    print(f"  Protein           : {inputs['protein_id']}")
    print(f"  Antibiotic        : {inputs['drug_name']}")
    print(f"  Poses Generated   : {docking['num_poses']}")
    print(f"  Best Score        : {docking.get('best_score', 'N/A')}")
    print(f"  Avg Score         : {docking.get('avg_score', 'N/A')}")
    print(f"  Binding           : {docking.get('binding_assessment', 'N/A')}")
    print(f"  Resistance Likely : {'YES ⚠' if docking.get('resistance_likely') else 'NO ✅'}")
    print(f"\n  All Scores        : {docking.get('scores', [])}")
    print(f"\n  Best Pose File    : {best_pose_path}")
    print(f"  Raw Result File   : {RAW_RESULT_FILE}")
    print(f"  JSON Output       : {OUTPUT_FILE}")
    print("─" * 55)
 
    return output
 
 
if __name__ == "__main__":
    # Optional: pass number of poses as argument
    num_poses = DEFAULT_NUM_POSES
    if len(sys.argv) > 1:
        try:
            num_poses = int(sys.argv[1])
        except ValueError:
            print(f"  ⚠ Invalid num_poses '{sys.argv[1]}' — using default {DEFAULT_NUM_POSES}")
 
    try:
        result = run_phase5(num_poses=num_poses)
        print("\n✅ Phase 5 complete! Run Phase 6 next:")
        print("   python phase6_score_analysis.py")
        print("\n💡 For frontend visualization:")
        print("   python api_server.py")
    except FileNotFoundError as e:
        print(f"\n❌ File Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"\n❌ Config Error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"\n❌ API Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise
 