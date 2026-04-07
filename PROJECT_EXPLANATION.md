# Exact Project Explanation

## 1. What Exactly Is This Project?

This project is a local full-stack web application for **AI-based antibiotic resistance prediction**.

It tries to answer this question:

> Given a bacterial DNA sequence, an antibiotic molecule, and lab conditions, how likely is the bacterium to be resistant?

The application combines:

1. `FASTA DNA sequence`
2. `Protein translation from DNA`
3. `Protein structure prediction or fallback structure generation`
4. `Drug structure processing from SMILES`
5. `Docking score estimation`
6. `Resistance gene / mutation mapping`
7. `Machine learning prediction`

The final output is a resistance category such as:

- `Sensitive`
- `Low Resistance`
- `Medium Resistance`
- `High Resistance`

along with:

- `binding_score`
- `confidence`
- `gene`
- structure/docking source information

---

## 2. What Problem Does It Solve?

Antibiotic resistance is not determined only by one factor.

A bacterium may become resistant because:

- its DNA contains resistance genes
- its target protein has mutations
- the antibiotic binds weakly to the protein
- the environmental condition changes the response

This project tries to model that combined biological context in a practical local application.

---

## 3. Main Idea of the Project

The project workflow is:

1. User uploads a `FASTA` file
2. Backend reads the DNA sequence
3. DNA is translated into protein sequence
4. Important resistance-related genes and mutations are detected
5. Protein structure is predicted using an external API if available
6. If structure API is not available, a local mock PDB structure is generated
7. User enters an antibiotic `SMILES`
8. Backend tries to fetch ligand data from `PubChem`
9. If PubChem is not available, RDKit generates a fallback ligand structure
10. Backend tries docking through a `DiffDock-compatible API`
11. If docking API is not available, a local docking heuristic is used
12. All biological and chemical features are fused
13. A machine learning model predicts resistance
14. Frontend shows the result

---

## 4. Full Technical Architecture

### Frontend

Technology:

- `React`
- `Vite`
- `Tailwind CSS`
- `Axios`
- `React Router`

Frontend pages:

- `Home`
- `Upload`
- `Dock`
- `Result`
- `Learn`

Frontend responsibility:

- upload FASTA file
- collect SMILES and environment input
- call backend APIs
- display prediction result, docking score, confidence, gene, and biology summary

### Backend

Technology:

- `FastAPI`
- `BioPython`
- `RDKit`
- `scikit-learn`

Backend responsibility:

- parse FASTA
- validate DNA
- translate DNA to protein
- map genes and mutations
- call structure and docking services
- generate fallbacks if services fail
- create ML features
- return JSON prediction

---

## 5. Exact Backend Pipeline

## Step 1: FASTA Processing

Implemented in:

- `backend/utils/fasta_utils.py`

What happens:

- uploaded FASTA file is decoded
- first FASTA record is read using `Bio.SeqIO`
- DNA sequence is validated for only `A`, `T`, `G`, `C`
- GC content is computed

Why this step matters:

- bad FASTA input should fail early
- the model depends on a clean DNA sequence

---

## Step 2: DNA to Protein Conversion

Implemented in:

- `backend/utils/fasta_utils.py`
- `backend/model/ai_pipeline.py`

What happens:

- DNA is translated to amino acid sequence
- mapped genes are translated
- if no good mapped protein is found, the longest translated ORF is used as fallback

Why this step matters:

- docking works on protein-ligand interaction
- docking needs protein sequence and eventually structure

---

## Step 3: CARD-style Gene and Mutation Mapping

Implemented in:

- `run_pipeline.py`
- `backend/model/ai_pipeline.py`

What happens:

- sequence is compared against local reference resistance genes
- genes like `gyrA`, `parC`, `blaTEM`, `tetA` are checked
- important mutations are detected, for example:
  - `gyrA_S83L`
  - `gyrA_D87N`
  - `parC_S80I`
  - `parC_E84K`

How it is implemented:

- local gene k-mer mapping
- local reference coordinates
- mutation comparison at amino acid positions

Why this step matters:

- resistance is often linked to known resistance genes and target mutations

---

## Step 4: Protein Structure Prediction

Implemented in:

- `backend/model/external_clients.py`

Main function:

- `predict_structure_with_esmfold(...)`

What happens:

- if `ESMFOLD_API_URL` is set, backend tries to call an ESMFold-compatible endpoint
- if response contains PDB text, it uses that structure
- if API fails or is absent, the backend builds a local mock PDB

Why fallback is used:

- the app must remain runnable locally
- many users will not have external API access all the time

Current behavior:

- real endpoint supported through env vars
- fallback mock structure used when live endpoint is unavailable

---

## Step 5: Drug Processing

Implemented in:

- `backend/model/external_clients.py`

Main function:

- `fetch_pubchem_sdf(...)`

What happens:

- user provides `SMILES`
- backend tries to fetch compound CID and 3D SDF from `PubChem PUG REST`
- if PubChem fails, RDKit generates a ligand structure locally

Why this step matters:

- docking requires a ligand structure
- SMILES alone is not directly enough for all docking pipelines

---

## Step 6: Molecular Docking

Implemented in:

- `backend/model/external_clients.py`

Main function:

- `run_diffdock_docking(...)`

What happens:

- if `DIFFDOCK_API_URL` is set, backend sends:
  - protein PDB
  - ligand SDF
- if docking response succeeds, backend reads:
  - binding score
  - confidence
  - pose info
- if docking fails, backend uses a local docking heuristic

Fallback docking uses:

- gene identity
- mutation count
- structure features
- environment features
- drug chemical properties

Why this step matters:

- docking gives a protein-drug interaction signal
- weaker binding can indicate possible resistance

---

## Step 7: Feature Engineering

Implemented in:

- `backend/model/ai_pipeline.py`

Feature blocks used:

### DNA features

- normalized k-mer vector from DNA sequence

### Mutation features

- mutation presence indicators
- gene presence indicators

### Protein structure features

Derived from amino acid composition:

- hydrophobic fraction
- polar fraction
- positive charge fraction
- negative charge fraction
- aromatic fraction
- flexibility proxy
- normalized protein length
- mapped-gene coverage proxy

### Drug features

- RDKit fingerprint from SMILES

### Environmental features

- scaled temperature
- scaled pH
- one-hot medium encoding

### Docking features

- normalized binding strength
- docking confidence
- interaction proxy

---

## Step 8: Machine Learning Model

Implemented in:

- `backend/model/ai_pipeline.py`

Current model:

- `RandomForestClassifier`

Why this model was chosen:

- lightweight on CPU
- stable on mixed feature types
- easier to use locally than a heavy deep model

What it predicts:

- `Sensitive`
- `Low`
- `Medium`
- `High`

How training is done:

- synthetic dataset generated locally
- group-aware train/test split using isolate IDs
- metrics saved in backend artifacts

Current saved metrics:

- accuracy around `0.6556`
- weighted F1 around `0.6532`

---

## 6. API Layer

Implemented in:

- `backend/main.py`

Endpoints:

### `POST /upload-fasta`

Input:

- FASTA file

Output:

- upload id
- sequence metadata
- primary gene
- protein length
- protein preview
- mapped genes
- mutations

### `POST /predict`

Input:

- upload id
- SMILES
- temperature
- pH
- medium

Output:

- prediction
- confidence
- gene
- binding score
- docking confidence
- source labels:
  - structure source
  - ligand source
  - docking source

---

## 7. Frontend Implementation

Implemented in:

- `frontend/src/App.jsx`
- `frontend/src/pages/*.jsx`
- `frontend/src/components/TopNav.jsx`

Design decision:

The previous UI was too text-heavy and felt artificial.

So the new UI was changed into:

- short text
- one main task per page
- more human-looking navigation
- simpler responsive layout

Current UI flow:

### Home page

- quick intro
- start button

### Upload page

- FASTA file upload
- gene + protein summary after upload

### Dock page

- SMILES input
- environment input
- run prediction button

### Result page

- prediction
- binding score
- confidence
- source labels
- mutation summary
- probability bars

### Learn page

- short explanation of structure, docking, and prediction

---

## 8. What Is Real and What Is Simulated?

This is very important.

### Real / supported

- FASTA parsing with BioPython
- DNA validation
- DNA to protein translation
- RDKit SMILES fingerprinting
- PubChem SDF fetching support
- external ESMFold-compatible endpoint support
- external DiffDock-compatible endpoint support
- FastAPI + React integration

### Simulated / fallback

- local mock PDB if structure API is unavailable
- local docking heuristic if docking API is unavailable
- local CARD-style mapping subset
- local synthetic training dataset

Reason:

- the project must remain runnable locally
- external APIs can fail or be rate-limited

---

## 9. Why Docking Visualization Is Not Fully Present Yet

Right now the app shows:

- binding score
- docking confidence
- pose preview text
- source labels

But it does **not yet show a full 3D docking viewer**.

Why:

- the frontend currently does not render protein + ligand in 3D
- backend returns summary text, not a full visualization payload to the browser
- fallback docking produces scores and pose labels, not a full physically docked 3D scene

If needed, the next upgrade would be:

1. return PDB + ligand structure files to frontend
2. add a viewer like `3Dmol.js` or `Mol*`
3. render protein and ligand together in the Result page

---

## 10. Exact Files Responsible for the Main Logic

Core files:

- `backend/main.py`
- `backend/model/ai_pipeline.py`
- `backend/model/external_clients.py`
- `backend/model/service.py`
- `backend/utils/fasta_utils.py`
- `backend/utils/schemas.py`
- `frontend/src/App.jsx`
- `frontend/src/pages/UploadPage.jsx`
- `frontend/src/pages/DockPage.jsx`
- `frontend/src/pages/ResultPage.jsx`

---

## 11. In One Line

This project is a **full-stack AI-driven antibiotic resistance prediction app** that combines **DNA sequence, protein translation, protein structure, docking, gene mapping, and machine learning** to estimate bacterial resistance against antibiotics.

---

## 12. Simple English Explanation

The user uploads a DNA sequence and gives an antibiotic molecule.
The system finds the important protein, predicts or approximates its structure, estimates how the drug binds to it, combines that with mutation and gene information, and finally predicts the resistance level.

---

## 13. Hindi Explanation

Ye project ek full-stack web app hai jo FASTA DNA sequence aur antibiotic SMILES se resistance predict karta hai.

Pehle DNA read hota hai, phir protein sequence nikali jati hai.
Us protein ka structure API se lane ki koshish hoti hai.
Agar API available na ho to fallback structure ban jata hai.
Phir drug ke saath docking score nikala jata hai.
Gene aur mutation mapping ke saath sab features ML model ko diye jaate hain.
Phir final resistance category predict hoti hai.

---

## 14. Current Status

Project currently:

- runs locally
- frontend and backend connected
- supports external APIs through env vars
- gracefully falls back when APIs fail
- uses a trained CPU-friendly ML model

So this is a **working hybrid system**:

- real engineering structure
- partial real external integration
- reliable local fallback

