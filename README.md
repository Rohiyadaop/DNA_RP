# 🧬 BioGPT - DNA AI Web Application using NVIDIA Evo2

> **Production-ready full-stack web application** for generating DNA sequences using NVIDIA's Evo2 AI model. Input raw DNA sequences or natural language prompts, and receive generated DNA sequences via a modern web interface.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen)
![Tech Stack](https://img.shields.io/badge/stack-FastAPI%20%7C%20Next.js%20%7C%20Tailwind-blueviolet)

---

## ✨ Features

- **Dual Input Modes**
  - DNA: Direct DNA sequence input with FASTA format support
  - Prompt: Natural language descriptions converted to Evo2-compatible DNA seeds
  
- **Advanced AI Integration**
  - NVIDIA Evo2 40B model via official API
  - Configurable generation parameters (temperature, top-k, top-p, num_tokens)
  - Optional deterministic generation with random seed control
  
- **Beautiful UI/UX**
  - Modern glassmorphism design with Tailwind CSS
  - DNA color coding (A, T, G, C in distinct colors)
  - Responsive layout for mobile, tablet, and desktop
  - Real-time loading indicators
  
- **Data Management**
  - Copy-to-clipboard functionality
  - Download generated sequences as `.txt` files
  - Local browser history of last 8 generations (persisted with localStorage)
  - One-click history restore
  
- **Production-Ready**
  - Full error handling and user feedback
  - CORS configuration for secure cross-origin requests
  - Environment-based configuration
  - Deployment-ready for Vercel (frontend) and Render (backend)

---

## 📁 Project Structure

```
biogpt-evo2/
├── backend/
│   ├── .env.example              # Environment variables template
│   ├── .env                       # Local configuration (gitignored)
│   ├── app.py                     # FastAPI application with /generate endpoint
│   ├── requirements.txt           # Python dependencies
│   └── README.md                  # Backend-specific documentation
│
├── frontend/
│   ├── .env.example               # Frontend config template
│   ├── .env.local.example         # Development env template
│   ├── next.config.js             # Next.js configuration
│   ├── package.json               # Node dependencies
│   ├── postcss.config.js          # PostCSS configuration
│   ├── tailwind.config.js         # Tailwind CSS theme config
│   ├── app/
│   │   ├── globals.css            # Global styles & Tailwind imports
│   │   ├── layout.js              # Root layout with metadata
│   │   └── page.js                # Home page with state management
│   ├── components/
│   │   ├── InputBox.js            # DNA/Prompt input interface
│   │   └── OutputBox.js           # Generated output display
│   └── public/                    # Static assets
│
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm/yarn
- Python 3.9+
- NVIDIA API key (get from [NVIDIA API Console](https://build.nvidia.com/))

### Backend Setup (FastAPI)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv .venv

# Activate environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your NVIDIA_API_KEY

# Start development server
uvicorn app:app --reload --host 127.0.0.1 --port 8000

# API will be available at http://127.0.0.1:8000
# Interactive docs at http://127.0.0.1:8000/docs
```

### Frontend Setup (Next.js)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install
# or
yarn install

# Configure environment
cp .env.example .env.local
# Edit .env.local - API URL should point to your backend

# Start development server
npm run dev
# or
yarn dev

# App will be available at http://localhost:3000
```

---

## 📖 API Documentation

### POST `/generate`

Generate DNA sequences using either a DNA seed or natural language prompt.

**Request:**
```json
{
  "input": "ATGCGTACGTTAGCCTAGGCTAACCGTTA",
  "input_type": "dna",
  "num_tokens": 120,
  "temperature": 0.7,
  "top_k": 4,
  "top_p": 0.0,
  "random_seed": null
}
```

**Response:**
```json
{
  "generated_sequence": "ATGCGTACGTTAGCCTAGGCTAACCGTTAATGCGTACGTTAGCCTAGGCTAACCGTTA...",
  "submitted_sequence": "ATGCGTACGTTAGCCTAGGCTAACCGTTA",
  "input_type": "dna",
  "upstream_elapsed_ms": 1234,
  "model_endpoint": "https://health.api.nvidia.com/v1/biology/arc/evo2-40b/generate"
}
```

**Parameters:**
| Parameter | Type | Range | Description |
|-----------|------|-------|-------------|
| `input` | string | 2-5000 chars | DNA sequence (FASTA or plain) OR natural language prompt |
| `input_type` | enum | "dna", "prompt" | Type of input provided |
| `num_tokens` | integer | 16-1024 | Number of bases to generate |
| `temperature` | float | 0.0-2.0 | Sampling randomness (lower = deterministic) |
| `top_k` | integer | 1-6 | Top-k sampling parameter |
| `top_p` | float | 0.0-1.0 | Nucleus sampling parameter |
| `random_seed` | integer | 0-2147483647 | Optional seed for reproducible results |

---

## 🌐 Deployment

### Deploy Backend on Render

1. **Prepare Repository**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Create Render Service**
   - Go to [render.com](https://render.com)
   - Sign in with GitHub
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name:** `biogpt-backend`
     - **Environment:** `Python 3.11`
     - **Build Command:** `pip install -r backend/requirements.txt`
     - **Start Command:** `cd backend && gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app`
     - **Root Directory:** `/` (or leave empty)

3. **Set Environment Variables**
   - Add in Render Dashboard under "Environment":
     - `NVIDIA_API_KEY`: Your NVIDIA API key
     - `FRONTEND_URLS`: Your Vercel frontend URL (e.g., `https://biogpt.vercel.app`)

4. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy
   - Your backend URL will be: `https://biogpt-backend.onrender.com`

### Deploy Frontend on Vercel

1. **Prepare Code**
   ```bash
   cd frontend
   npm run build  # Test local build
   ```

2. **Deploy to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Configure:
     - **Project Name:** `biogpt-frontend`
     - **Framework:** `Next.js`
     - **Root Directory:** `./frontend`

3. **Set Environment Variables**
   - Add in Vercel Project Settings:
     - `NEXT_PUBLIC_API_URL`: Your Render backend URL (e.g., `https://biogpt-backend.onrender.com`)

4. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy automatically
   - Your frontend URL will be: `https://biogpt.vercel.app`

5. **Update Backend CORS**
   - Update `FRONTEND_URLS` in Render to include your Vercel URL

---

## 🔧 Environment Variables

### Backend (`.env`)
```
# NVIDIA API Configuration
NVIDIA_API_KEY=nvapi-your-key-here
NVIDIA_EVO2_URL=https://health.api.nvidia.com/v1/biology/arc/evo2-40b/generate

# CORS Configuration (comma-separated URLs)
FRONTEND_URLS=http://localhost:3000,https://biogpt.vercel.app

# Request Configuration
REQUEST_TIMEOUT_SECONDS=60
```

### Frontend (`.env.local`)
```
# API Configuration
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000  # Development
# NEXT_PUBLIC_API_URL=https://biogpt-backend.onrender.com  # Production
```

---

## 💻 Development

### Backend Development

```bash
cd backend

# Activate environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Run with auto-reload
uvicorn app:app --reload

# Run tests (if added)
pytest

# Type checking
mypy app.py

# Code formatting
black app.py
```

### Frontend Development

```bash
cd frontend

# Start dev server with hot reload
npm run dev

# Build for production
npm run build

# Start production server
npm run start

# Lint code
npm run lint
```

---

## 📝 Resume Summary

**BioGPT** is a full-stack web application demonstrating:

- **Backend**: FastAPI with async/await patterns, API integration, error handling, and CORS security
- **Frontend**: Next.js with React hooks, state management, localStorage, and modern CSS (Tailwind)
- **Integration**: Frontend-backend communication via REST API with proper error handling
- **UI/UX**: Responsive design with glassmorphism effects and DNA color coding
- **Deployment**: Production-ready deployment on Render and Vercel with environment management

**Technologies**: FastAPI, Python 3.9+, Next.js 14, React 18, Tailwind CSS 3, NVIDIA Evo2 API, Render, Vercel

---

## 🎯 How It Works

1. **User Input** → Enters DNA sequence or natural language prompt
2. **Frontend** → Sends request to FastAPI backend with configuration
3. **Backend Processing**:
   - If prompt: Converts to DNA seed using keyword matching, hashing, and encoding
   - If DNA: Validates and normalizes the sequence
4. **NVIDIA Evo2 API** → Generates DNA bases using the seed
5. **Response** → Generated sequence, timing, and metadata sent to frontend
6. **Display** → Color-coded output with history saving and download options

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check port 8000 isn't in use
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows
```

### Frontend won't connect to backend
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify backend is running at that URL
- Check browser console for CORS errors
- Ensure `FRONTEND_URLS` in backend includes your frontend URL

### NVIDIA API errors
- Verify `NVIDIA_API_KEY` is set correctly
- Check API key has required permissions
- Ensure account has API access enabled
- Check NVIDIA service status

---

## 📄 License

This project is provided as-is for educational purposes.

---

## 🤝 Contributing

To improve this project:
1. Test thoroughly before commits
2. Follow PEP 8 (Python) and Airbnb style (JavaScript)
3. Update documentation for new features
4. Ensure backward compatibility

---

## ✅ Checklist for Deployment

- [ ] Backend `.env` configured with NVIDIA_API_KEY
- [ ] Frontend `.env.local` points to correct backend URL
- [ ] Backend deployed to Render
- [ ] Frontend deployed to Vercel
- [ ] CORS configured correctly (FRONTEND_URLS in backend)
- [ ] All environment variables set in deployment services
- [ ] Tested end-to-end in production
- [ ] Git repository clean and pushed

---

**Ready to generate DNA sequences with AI? Start with the Quick Start section above!
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## Frontend Setup

1. Install Node.js dependencies inside `frontend`.
2. Copy `frontend/.env.example` to `frontend/.env.local`.
3. Set `NEXT_PUBLIC_API_URL` to your backend URL.
4. Start the Next.js development server.

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Windows PowerShell:

```powershell
cd frontend
npm install
Copy-Item .env.example .env.local
npm run dev
```

The frontend will run at `http://localhost:3000` and the backend will run at `http://127.0.0.1:8000`.

## Environment Variables

### Backend

```env
NVIDIA_API_KEY=nvapi-your-key-here
NVIDIA_EVO2_URL=https://health.api.nvidia.com/v1/biology/arc/evo2-40b/generate
FRONTEND_URLS=http://localhost:3000,https://your-project.vercel.app
REQUEST_TIMEOUT_SECONDS=60
```

### Frontend

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

## Deployment Guide

### Deploy Backend on Render

1. Push the repository to GitHub.
2. Create a new **Web Service** on Render.
3. Select the repository and set the root directory to `backend`.
4. Use Python as the environment.
5. Set the build command to `pip install -r requirements.txt`.
6. Set the start command to `uvicorn app:app --host 0.0.0.0 --port $PORT`.
7. Add `NVIDIA_API_KEY`, `NVIDIA_EVO2_URL`, `FRONTEND_URLS`, and `REQUEST_TIMEOUT_SECONDS` in Render.
8. Deploy and copy the generated Render URL.

### Deploy Frontend on Vercel

1. Import the same GitHub repository into Vercel.
2. Set the root directory to `frontend`.
3. Keep the framework preset as **Next.js**.
4. Add `NEXT_PUBLIC_API_URL` with the deployed Render backend URL.
5. Deploy the project.
6. Update Render `FRONTEND_URLS` so it includes your final Vercel domain.

## Screenshots Placeholder

Add your screenshots here after deployment:

- `docs/screenshots/home.png`
- `docs/screenshots/generated-output.png`

## Resume-Ready Project Description

Built a production-ready DNA generation web application using Next.js, Tailwind CSS, FastAPI, and NVIDIA Evo2. Implemented prompt-to-seed adaptation, responsive UX, local history, clipboard and export tools, and cloud deployment on Vercel and Render.
#   h a c k a t h o n _ 2 0 2 6  
 