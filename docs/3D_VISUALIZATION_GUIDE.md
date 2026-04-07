# 🔬 Interactive 3D Molecular Visualization - Complete Guide

## 📋 Overview

This document provides a complete explanation of the Interactive 3D Molecular Visualization feature added to the Antibiotic Resistance Prediction Web App. It includes technical implementation, usage instructions, and conceptual explanations.

---

## 🎯 What Is 3D Molecular Visualization?

### Simple English Explanation

**3D Protein Visualization** is the process of rendering a protein's 3D structure in a web browser so users can:
- **Rotate** the protein to see all angles
- **Zoom** in and out to inspect specific regions
- **Change visualization style** (cartoon, stick, sphere)
- **Identify binding sites** where antibiotics attach

**Docking Visualization** shows how an antibiotic drug molecule binds to a bacterial protein. This is important because:
1. **Binding affinity** determines if the drug can work
2. **Binding site** indicates which part of the protein the drug attacks
3. **Drug-protein interaction** explains resistance mechanisms

### How It Works in Our Pipeline

```
DNA Sequence (FASTA)
         ↓
    [ESMFold AI]  ← Predicts 3D protein structure
         ↓
   Protein PDB File (3D coordinates of atoms)
         ↓
   [3D Viewer Renders] ← Uses 3Dmol.js to display
         ↓
   Interactive 3D Model (rotate, zoom, style)
```

---

## 🏗️ Technical Architecture

### Backend Components (FastAPI)

#### 1. **Modified AI Pipeline** (`ai_pipeline.py`)

**What it does:**
- Uses ESMFold neural network to predict protein 3D structure from amino acid sequence
- Returns PDB format (Protein Data Bank) - standard format for molecular structures

**Code Flow:**
```python
protein_sequence → predict_structure_with_esmfold() → PDB text
```

**Key Code:**
```python
# In build_live_feature_payload()
structure_result = predict_structure_with_esmfold(context["primary_protein"])
# Returns: {"pdb_text": "ATOM  1  N   ALA A   1...", "source": "esmfold_api", ...}
```

#### 2. **Service Layer** (`service.py`)

**What it does:**
- Stores PDB data as files for later retrieval
- Provides methods to fetch stored PDB data

**Key Methods:**
```python
# Stores PDB when prediction is made
structure_path.write_text(result["protein_pdb"], encoding="utf-8")
docking_path.write_text(result["docked_complex_pdb"], encoding="utf-8")

# Retrieves PDB for visualization
def get_structure_pdb(upload_id):
    return structure_path.read_text(encoding="utf-8")
```

#### 3. **FastAPI Endpoints** (`main.py`)

**New Endpoints:**

```
GET /structure?upload_id=<uuid>
Response: { "pdb": "<PDB text data>" }
Description: Returns protein structure PDB

GET /docking?upload_id=<uuid>
Response: { "pdb": "<PDB text data>" }
Description: Returns docked complex PDB
```

**How They Work:**
```python
@app.get("/structure")
async def get_structure(upload_id: str) -> dict:
    pdb_text = get_service().get_structure_pdb(upload_id)
    return {"pdb": pdb_text}
```

---

### Frontend Components (React)

#### 1. **Viewer3D Component** (`Viewer3D.jsx`)

**What it does:**
- Renders PDB data using 3Dmol.js library
- Provides interactive controls (rotate, zoom, style switching)
- Handles both protein structure and docked complex visualization

**Key Features:**
```javascript
// Initialize 3Dmol viewer
const viewer = $3Dmol.createViewer(containerRef.current, config);

// Add PDB model
viewer.addModel(pdbData, "pdb");

// Apply style (cartoon, stick, sphere)
viewer.setStyle({}, { cartoon: { color: "spectrum" } });

// Zoom to fit
viewer.zoomTo();
```

**Visualization Styles:**
- **Cartoon**: Shows protein backbone as ribbon (good for overall structure)
- **Stick**: Shows individual bonds between atoms (good for details)
- **Sphere**: Shows van der Waals surface (good for 3D shape)

#### 2. **Enhanced ResultPage** (`ResultPage.jsx`)

**What it does:**
- Provides tabbed interface for viewing predictions
- Manages state for 3D visualization
- Fetches PDB data from backend on demand

**Tabs:**
1. **Overview** - Summary stats and biology details
2. **Protein Structure** - 3D visualization of predicted protein
3. **Docked Complex** - 3D visualization with drug molecule

**How It Works:**
```javascript
// When user clicks "View Structure" button
handleViewStructure = async () => {
  const response = await fetch(`/structure?upload_id=${uploadData.upload_id}`);
  const data = await response.json();
  setStructurePdb(data.pdb);  // Pass to Viewer3D component
};
```

---

## 🔧 Data Flow Diagram

```
User uploads FASTA
      ↓
Backend processes sequence
      ↓
ESMFold predicts structure → PDB text
      ↓
DiffDock predicts docking → Docking score
      ↓
Service stores PDB files:
  - {upload_id}_structure.pdb
  - {upload_id}_docking.pdb
      ↓
Frontend receives prediction with upload_id
      ↓
User clicks "View Structure" or "View Docking"
      ↓
Frontend fetches: /structure?upload_id={id}
      ↓
3Dmol.js renders PDB in browser
      ↓
User interacts: rotate, zoom, style change
```

---

## 📁 What is PDB Format?

**PDB (Protein Data Bank) Format** is the standard format for storing protein structure:

### Example PDB Content:
```
HEADER    SAMPLE PROTEIN STRUCTURE
ATOM      1  N   ALA A   1       0.000   0.000   0.000  1.00  0.00           N
ATOM      2  CA  ALA A   1       1.458   0.000   0.000  1.00  0.00           C
ATOM      3  C   ALA A   1       2.009   1.420   0.000  1.00  0.00           C
ATOM      4  O   ALA A   1       1.231   2.370   0.000  1.00  0.00           O
...
END
```

### What Each Column Means:
- **ATOM** = Atom record
- **1** = Atom number
- **N, CA, C, O** = Atom type
- **ALA** = Residue type (Alanine)
- **0.000, 0.000, 0.000** = X, Y, Z coordinates (Angstroms)
- **1.00** = Occupancy
- **0.00** = B-factor (temperature factor)
- **N, C** = Element symbol

---

## 🚀 How 3Dmol.js Works

**3Dmol.js** is a JavaScript library for visualizing molecular structures in web browsers.

### Why 3Dmol.js?
- ✅ **Lightweight** - Works in browser without plugins
- ✅ **Fast** - WebGL rendering
- ✅ **Interactive** - Rotate, zoom, style changes
- ✅ **Cross-platform** - Works on all modern browsers
- ✅ **No installation** - NPM package, just import

### Usage Example:
```javascript
import $3Dmol from "3dmol";

// Create viewer in a container
const viewer = $3Dmol.createViewer(document.getElementById("viewer"), {
  backgroundColor: "white"
});

// Add PDB model
viewer.addModel(pdbString, "pdb");

// Set style
viewer.setStyle({}, { cartoon: { color: "spectrum" } });

// Zoom to molecule
viewer.zoomTo();

// Render
viewer.render();
```

---

## 💻 Installation & Setup

### Backend Installation

1. **Add PDB storage methods** - Already done in `service.py`
2. **Add new endpoints** - Already done in `main.py`
3. **No new dependencies** - Uses existing libraries

### Frontend Installation

```bash
cd frontend
npm install 3dmol
npm install  # Install all dependencies
npm run dev  # Start development server
```

---

## 📊 Integration with Existing System

### Prediction Response Structure

The `/predict` endpoint now returns:

```json
{
  "prediction": "XDR Resistance",
  "confidence": 0.95,
  "gene": "gyrA",
  "binding_score": -7.2,
  "docking_confidence": 0.85,
  "protein_pdb": "<PDB data>",
  "docked_complex_pdb": "<PDB data>",
  ...other fields...
}
```

### How Frontend Uses It

```javascript
// ResultPage receives prediction
const { uploadData, prediction } = props;

// When user clicks visualization button
const response = await fetch(`/structure?upload_id=${uploadData.upload_id}`);
const { pdb } = await response.json();

// Pass to Viewer3D
<Viewer3D pdbData={pdb} />
```

---

## 🎮 User Interaction Guide

### How Users See It

1. **Upload FASTA** → Regular upload process
2. **Run Prediction** → Regular prediction
3. **View Results** → New tabbed interface
4. **Click "View Structure"** → 3D protein appears
5. **Interact**:
   - 🖱️ Left-click + drag = Rotate
   - 📜 Scroll = Zoom
   - 🖱️ Middle-click + drag = Pan
   - 🎨 Style buttons = Change visualization

### Example Interaction Sequence

```
Result Page
├── Tab 1: Overview (default)
│   ├── Binding score
│   ├── Docking confidence
│   └── Mutation list
│
├── Tab 2: 🧬 Protein Structure (click button)
│   ├── 3Dmol viewer loads
│   ├── Shows cartoon by default
│   ├── Style buttons: Cartoon | Stick | Sphere
│   └── Interactive rotate/zoom
│
└── Tab 3: 💊 Docked Complex (click button)
    ├── 3Dmol viewer loads
    ├── Shows protein + drug
    ├── Binding score displayed
    └── Interactive rotate/zoom
```

---

## 🧪 Testing the Feature

### Manual Testing

1. **Start Backend**:
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test Flow**:
   - Upload a FASTA file
   - Enter SMILES and parameters
   - Run prediction
   - Click "View Structure" tab
   - Interact with 3D viewer

### API Testing

**Test Structure Endpoint:**
```bash
curl "http://localhost:8000/structure?upload_id=<uuid>"
# Should return JSON with "pdb" field containing PDB data
```

**Test Docking Endpoint:**
```bash
curl "http://localhost:8000/docking?upload_id=<uuid>"
# Should return JSON with "pdb" field containing PDB data
```

---

## 🔬 Behind the Scenes: Algorithm Details

### ESMFold (Protein Structure Prediction)

**What it is:**
- AI model trained on millions of protein sequences
- Predicts 3D structure from amino acid sequence
- Based on transformer neural networks

**Why it works:**
- Capture long-range dependencies between residues
- Learn evolutionary patterns from multiple sequence alignments
- Faster than traditional structure prediction (seconds, not months)

**Our Implementation:**
```python
def predict_structure_with_esmfold(protein_sequence: str) -> Dict[str, Any]:
    # If API available, use live ESMFold
    if endpoint:
        response = client.post(endpoint, json={"sequence": protein_sequence})
        return {"pdb_text": response["pdb"], "source": "esmfold_api"}
    
    # Fallback to mock PDB (for demo)
    return {"pdb_text": build_mock_pdb(protein_sequence), "source": "mock_structure"}
```

### DiffDock (Molecular Docking)

**What it is:**
- AI model for predicting drug-protein binding
- Predicts binding affinity and pose
- Based on diffusion models

**Binding Score Interpretation:**
- Negative values = Stable binding (good)
- More negative = Stronger binding
- -6.0 to -8.0 = Usually effective
- Example: -7.2 = Strong binding

**Our Implementation:**
```python
# If DiffDock API available
docking_result = run_diffdock_docking(
    protein_pdb_text=structure_result["pdb_text"],
    sdf_text=ligand_result["sdf_text"],
    ...
)

# Returns binding_score and docking_confidence
```

---

## 📦 Sample Files and Data

### Sample PDB Data for Testing

Located in: `docs/sample_pdbs/`

1. **sample_protein_structure.pdb** - Simple α-helix
2. **sample_docking_complex.pdb** - Protein + drug

### How to Use Samples

1. Import into test database
2. Use in development without running ESMFold
3. Demonstrate feature without API dependencies

---

## 🐛 Troubleshooting

### Issue: 3D Viewer Not Loading

**Solutions:**
1. Check browser console for errors
2. Verify PDB data is valid (starts with ATOM)
3. Check network tab - confirm API returns data
4. Clear browser cache

### Issue: Rotation Not Working

**Solutions:**
1. Click inside viewer to focus
2. Use left mouse button
3. Ensure WebGL is supported

### Issue: API Endpoints Return 404

**Solutions:**
1. Verify upload_id is correct
2. Check PDB files exist in `backend/uploads/`
3. Ensure backend is running

---

## 🚀 Future Enhancements

### Possible Additions:

1. **Distance Measurement**
   - Measure distances between atoms
   - Highlight binding pocket

2. **Surface Visualization**
   - Show van der Waals surface
   - Color by property (hydrophobic, charged, etc.)

3. **Animation**
   - Animate protein folding process
   - Show ligand binding trajectory

4. **Export Features**
   - Download PDB file
   - Export visualization as image
   - Export as 3D model

5. **Advanced Analysis**
   - Highlight predicted mutation sites
   - Show residue information on click
   - Color by residue type

---

## 📚 References

### External Resources:
- [3Dmol.js Documentation](https://3Dmol.org)
- [PDB Format Specification](https://www.wwpdb.org/documentation/file-format)
- [ESMFold Paper](https://www.biorxiv.org/content/10.1101/2022.07.20.500902v1)
- [DiffDock Paper](https://arxiv.org/abs/2210.01776)

### Code References:
- `/backend/model/ai_pipeline.py` - Structure prediction
- `/backend/model/external_clients.py` - ESMFold API calls
- `/frontend/src/components/Viewer3D.jsx` - 3D visualization
- `/frontend/src/pages/ResultPage.jsx` - Integration

---

## ✅ Checklist for Implementation

- [x] Modify AI pipeline to return PDB data
- [x] Add service methods for storing/retrieving PDB
- [x] Create FastAPI endpoints (/structure, /docking)
- [x] Create Viewer3D React component
- [x] Integrate Viewer3D into ResultPage
- [x] Install 3Dmol.js library
- [x] Update schemas to include PDB fields
- [x] Add comprehensive documentation
- [x] Create test samples

---

## 📝 Version History

### v1.0 (Current)
- Initial 3D visualization feature
- Protein structure visualization
- Docked complex visualization
- Interactive style switching

### Future versions
- Enhanced controls and analysis
- Export capabilities
- Advanced visualization modes

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review error messages in browser console
3. Check backend logs
4. Refer to API documentation

---

**Happy molecular visualization! 🧬💊**
