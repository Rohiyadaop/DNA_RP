# 🚀 3D Visualization - Quick Start Guide

## Installation (5 minutes)

### 1. Install Frontend Dependencies

```bash
cd frontend
npm install
```

This installs 3Dmol.js and all required packages.

### 2. Run Development Servers

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - (Optional) Python Environment:**
```bash
# Make sure you have the right Python environment
conda activate .venv  # or your env setup
```

### 3. Open Browser

```
http://localhost:5173
```

---

## Testing the 3D Visualization (10 minutes)

### Step-by-Step Guide

**Step 1: Upload FASTA**
1. Go to "Upload" page
2. Click file upload
3. Select any `.fasta` file from `data/generated/isolate_fastas/`
4. Click submit
5. Wait for processing (~5 seconds)

**Step 2: Enter Prediction Parameters**
1. Go to "Dock" page
2. Keep default SMILES: `C1CC1N2C=C(C(=O)C3=CC(=C(C=C32)N4CCNCC4)F)C(=O)O`
3. Temperature: 37.0°C
4. pH: 7.0
5. Medium: MHB
6. Click "Predict"

**Step 3: View Results**
1. Go to "Result" page
2. See overview with binding scores

**Step 4: View 3D Protein Structure**
1. Click tab: "🧬 Protein Structure"
2. Wait for PDB to load (~2 seconds)
3. 3D structure appears
4. Interact:
   - 🖱️ Click + drag = Rotate
   - 📜 Scroll = Zoom
   - 🎨 Buttons = Change style (Cartoon/Stick/Sphere)

**Step 5: View Docked Complex**
1. Click tab: "💊 Docked Complex"
2. See protein + drug molecule
3. Binding score shown
4. Interact same as above

---

## API Endpoints Reference

### 1. **GET /structure**

**Purpose:** Retrieve protein structure PDB

**Request:**
```
GET http://localhost:8000/structure?upload_id=abc123xyz
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| upload_id | string | Yes | UUID from upload |

**Response (200 OK):**
```json
{
  "pdb": "HEADER    SAMPLE PROTEIN...\nATOM  1  N   ALA...\n..."
}
```

**Error (404):**
```json
{
  "detail": "Structure PDB not found for upload ID: abc123xyz"
}
```

**Example with curl:**
```bash
curl "http://localhost:8000/structure?upload_id=2b279c5d495d417fa97b41b1b3df71c6"
```

---

### 2. **GET /docking**

**Purpose:** Retrieve docked complex PDB

**Request:**
```
GET http://localhost:8000/docking?upload_id=abc123xyz
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| upload_id | string | Yes | UUID from upload |

**Response (200 OK):**
```json
{
  "pdb": "HEADER    DOCKED COMPLEX...\nATOM  1  N   ALA...\n..."
}
```

**Error (404):**
```json
{
  "detail": "Docking PDB not found for upload ID: abc123xyz"
}
```

**Example with curl:**
```bash
curl "http://localhost:8000/docking?upload_id=2b279c5d495d417fa97b41b1b3df71c6"
```

---

### 3. **POST /predict** (Modified)

**Purpose:** Run resistance prediction and generate 3D structures

**Request:**
```
POST http://localhost:8000/predict
Content-Type: application/json

{
  "upload_id": "abc123xyz",
  "smiles": "C1CC1N2C=C(C(=O)C3=CC(=C(C=C32)N4CCNCC4)F)C(=O)O",
  "temperature": 37.0,
  "ph": 7.0,
  "medium": "MHB"
}
```

**Response (200 OK):**
```json
{
  "prediction": "XDR Resistance",
  "confidence": 0.95,
  "upload_id": "abc123xyz",
  "gene": "gyrA",
  "binding_score": -7.2,
  "docking_confidence": 0.85,
  "protein_pdb": "ATOM  1  N   ALA...",
  "docked_complex_pdb": "ATOM  1  N   ALA...",
  ...other fields...
}
```

---

## File Structure After Prediction

When a prediction is made, these files are created:

```
backend/uploads/
├── {upload_id}.fasta              # Input FASTA
├── {upload_id}.json               # Metadata
├── {upload_id}_structure.pdb      # ← Protein structure (NEW)
└── {upload_id}_docking.pdb        # ← Docked complex (NEW)
```

**Example:**
```
backend/uploads/
├── 2b279c5d495d417fa97b41b1b3df71c6.fasta
├── 2b279c5d495d417fa97b41b1b3df71c6.json
├── 2b279c5d495d417fa97b41b1b3df71c6_structure.pdb
└── 2b279c5d495d417fa97b41b1b3df71c6_docking.pdb
```

---

## Component Architecture

### Frontend Components

```
App.jsx
├── TopNav.jsx
└── AppRoutes.jsx
    ├── HomePage.jsx
    ├── UploadPage.jsx
    │   └── Handles file upload
    ├── DockPage.jsx
    │   └── Handles prediction input
    ├── ResultPage.jsx ← MODIFIED
    │   ├── Tab: Overview
    │   ├── Tab: Structure
    │   │   └── Viewer3D.jsx ← NEW
    │   │       └── Uses 3Dmol.js
    │   └── Tab: Docking
    │       └── Viewer3D.jsx ← NEW
    └── LearnPage.jsx
```

### Backend Modules

```
backend/
├── main.py ← MODIFIED
│   ├── GET /structure ← NEW
│   └── GET /docking ← NEW
├── model/
│   ├── ai_pipeline.py ← MODIFIED
│   │   └── Returns protein_pdb
│   ├── service.py ← MODIFIED
│   │   ├── Stores PDB files
│   │   ├── get_structure_pdb() ← NEW
│   │   └── get_docking_pdb() ← NEW
│   ├── external_clients.py
│   │   ├── predict_structure_with_esmfold()
│   │   └── run_diffdock_docking()
│   └── pipeline.py
└── utils/
    └── schemas.py ← MODIFIED
        └── PredictionResponse
```

---

## Troubleshooting Guide

### Problem: "Structure PDB not found"

**Cause:** PDB file wasn't generated during prediction

**Solution:**
1. Check if prediction ran successfully
2. Verify upload_id is correct
3. Check browser console for errors
4. Restart backend and try again

### Problem: 3D Viewer Not Displaying

**Cause 1:** PDB data is invalid

**Solution:**
```javascript
// Check in browser console
fetch('/structure?upload_id=xxx')
  .then(r => r.json())
  .then(d => console.log(d.pdb))  // Should see ATOM lines
```

**Cause 2:** WebGL not supported

**Solution:**
1. Use modern browser (Chrome, Firefox, Safari)
2. Check GPU settings
3. Enable hardware acceleration in browser

**Cause 3:** 3Dmol.js not loaded

**Solution:**
```bash
# Verify installation
npm list 3dmol
# Should show: 3dmol@2.0.6

# Reinstall if needed
npm install 3dmol --save
```

### Problem: Slow PDB Loading

**Cause:** Large proteins or network issues

**Solution:**
1. Check network tab (should be < 500KB)
2. Verify backend is running
3. Try smaller protein first
4. Clear browser cache

### Problem: API Returns 404

**Cause:** Wrong endpoint or upload_id

**Solution:**
```bash
# Test endpoint
curl "http://localhost:8000/structure?upload_id=test123"

# Check backend logs for error messages
# Verify upload_id exists in backend/uploads/
ls backend/uploads/ | grep test123
```

---

## Debug Tips

### Enable Console Logging

Add to `Viewer3D.jsx`:

```javascript
console.log("PDB Data:", pdbData);
console.log("Container:", containerRef.current);
console.log("Viewer:", viewerRef.current);
```

### Test API Directly

```bash
# Test structure endpoint
curl -s "http://localhost:8000/structure?upload_id=xxx" | head -20

# Test with Python
python -c "
import requests
r = requests.get('http://localhost:8000/structure?upload_id=xxx')
print(r.json()['pdb'][:200])
"
```

### Check File System

```bash
# List all PDB files
find backend/uploads -name "*.pdb"

# Check file size
ls -lah backend/uploads/*.pdb

# View first few lines
head -5 backend/uploads/{upload_id}_structure.pdb
```

---

## Performance Optimization

### Frontend Caching

PDB data is cached in React state:
```javascript
const [structurePdb, setStructurePdb] = useState(null);

// Only fetch if not already loaded
if (structurePdb) {
  setActiveTab("structure");
  return;
}
```

### Backend Caching

PDB files are stored on disk, not regenerated.

### Network Optimization

- PDB files: 10-500 KB (typical)
- API response time: 100-500 ms
- Browser rendering: 200-1000 ms

---

## Testing Scenarios

### Scenario 1: Basic Visualization

1. Upload small FASTA (< 100 BP)
2. Run prediction
3. View structure
4. Verify cartoon renders
5. Test rotation/zoom

**Expected:** Structure displays, interactive works

### Scenario 2: Large Protein

1. Upload large FASTA (> 1000 BP)
2. Run prediction
3. View structure
4. Check rendering time

**Expected:** May take 1-2 seconds to render

### Scenario 3: Docking Complex

1. Complete prediction
2. Switch to docking tab
3. Check binding score displayed
4. Interact with molecule

**Expected:** Two entities visible (protein + drug)

### Scenario 4: Style Switching

1. View structure
2. Click "Stick" button
3. Click "Sphere" button
4. Click "Cartoon" button

**Expected:** Style changes smoothly

---

## Environment Variables (Optional)

For live services, set in `.env`:

```bash
# ESMFold API (if using live)
ESMFOLD_API_URL="https://your-esmfold-api.com/predict"
ESMFOLD_API_KEY="your-api-key"

# DiffDock API (if using live)
DIFFDOCK_API_URL="https://your-diffdock-api.com/dock"
DIFFDOCK_API_KEY="your-api-key"
```

If not set, app uses mock data (perfect for demo).

---

## Browser Compatibility

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 90+ | ✅ Fully supported |
| Firefox | 88+ | ✅ Fully supported |
| Safari | 14+ | ✅ Fully supported |
| Edge | 90+ | ✅ Fully supported |
| IE | All | ❌ Not supported |

**Note:** Requires WebGL support

---

## Next Steps

1. ✅ Run the application locally
2. ✅ Test with sample FASTA files
3. ✅ Verify 3D visualization works
4. ✅ Try different visualization styles
5. ✅ Review code in `Viewer3D.jsx` and `ResultPage.jsx`
6. ✅ Experiment with different proteins
7. ✅ Customize colors/styles as needed

---

## Support & References

**Documentation:**
- See: `docs/3D_VISUALIZATION_GUIDE.md` (full technical details)
- See: `docs/VIVA_HINDI_EXPLANATION.md` (Hindi explanation)

**Code Files:**
- `/frontend/src/components/Viewer3D.jsx` (visualization component)
- `/frontend/src/pages/ResultPage.jsx` (integration)
- `/backend/main.py` (API endpoints)
- `/backend/model/service.py` (data handling)

**External Resources:**
- 3Dmol.js: https://3Dmol.org
- PDB Format: https://www.wwpdb.org/

---

**Happy 3D Visualization! 🧬💊**
