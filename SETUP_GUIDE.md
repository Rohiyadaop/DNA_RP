# BioGPT Evo2 Platform - Complete Setup Guide

This guide provides step-by-step instructions to set up, run, and deploy the BioGPT Evo2 Platform with both DNA Sequence Generator and Mutation Resistance Predictor applications.

## 🎯 Quick Start (5 minutes)

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate
# OR (Mac/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
# Copy the template and add your NVIDIA API key
echo NVIDIA_API_KEY=your_api_key_here > .env
echo NVIDIA_EVO2_URL=https://health.api.nvidia.com/v1/biology/arc/evo2-40b/generate >> .env
echo FRONTEND_URLS=http://localhost:3000 >> .env

# Start the API server
uvicorn app:app --reload
```

The backend will start on `http://localhost:8000`

### 2. Frontend Setup

In a new terminal:

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env.local file
echo NEXT_PUBLIC_API_URL=http://127.0.0.1:8000 > .env.local

# Start development server
npm run dev
```

The frontend will start on `http://localhost:3000`

### 3. Access the Platform

Open your browser and navigate to:
- **Home**: http://localhost:3000
- **DNA Generator**: http://localhost:3000/dna-generator
- **Resistance Predictor**: http://localhost:3000/dna-predictor
- **API Docs**: http://localhost:8000/docs

---

## 📦 Detailed Setup Instructions

### Backend Setup (Detailed)

#### Step 1: Environment Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

#### Step 2: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Required packages:**
- fastapi==0.115.0
- uvicorn[standard]==0.30.6
- httpx==0.27.2
- python-dotenv==1.0.1
- scikit-learn==1.6.1
- numpy==1.24.3

#### Step 3: Configure Environment

Create a `.env` file in the `backend` directory:

```env
# NVIDIA API Configuration
NVIDIA_API_KEY=<your_nvidia_api_key_here>
NVIDIA_EVO2_URL=https://health.api.nvidia.com/v1/biology/arc/evo2-40b/generate

# Frontend Configuration
FRONTEND_URLS=http://localhost:3000,http://127.0.0.1:3000

# Request Timeout (optional)
REQUEST_TIMEOUT_SECONDS=60
```

**Getting your NVIDIA API Key:**
1. Visit [build.nvidia.com](https://build.nvidia.com)
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key for Evo2 API
5. Copy the key to your `.env` file

#### Step 4: Start the Server

```bash
uvicorn app:app --reload
```

Or with specific host/port:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**Console output:**
```
Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

#### Step 5: Verify API Setup

Open your browser to: `http://localhost:8000/docs`

You should see the interactive API documentation (Swagger UI).

---

### Frontend Setup (Detailed)

#### Step 1: Install Node Dependencies

```bash
cd frontend

# Using npm
npm install

# OR using yarn
yarn install
```

#### Step 2: Configure Environment

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

#### Step 3: Start Development Server

```bash
npm run dev
# OR
yarn dev
```

**Console output:**
```
> ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

#### Step 4: Access the Application

- Home page: http://localhost:3000
- DNA Generator: http://localhost:3000/dna-generator
- Resistance Predictor: http://localhost:3000/dna-predictor

---

## 🧪 Testing the Applications

### Test DNA Sequence Generator

1. Navigate to http://localhost:3000/dna-generator
2. Click the "DNA" tab
3. Paste or load an example DNA sequence
4. Adjust generation parameters (optional)
5. Click "Generate DNA Sequence"
6. Observe the output with performance metrics

**Example Input:**
```
ATGCGTACGTTAGCCTAGGCTAACCGTTA
```

### Test Mutation Resistance Predictor

1. Navigate to http://localhost:3000/dna-predictor
2. Review the UI components:
   - Input panel on the left
   - 3D DNA helix visualization
   - Prediction card on the right
   - Data flow pipeline

3. Click one of the example mutations (e.g., "gyrA S83L")
4. Click "Predict Resistance"
5. Observe:
   - 3D helix animation with highlighted mutation
   - Pipeline steps completing
   - Prediction result with confidence score
   - Scientific explanation

**Example Mutations to Try:**
- gyrA S83L (Fluoroquinolone resistance)
- katG S315T (Isoniazid resistance)
- rpoB S450L (Rifampicin resistance)
- rpsL K43R (Streptomycin resistance)

---

## 📊 API Endpoints Reference

### DNA Sequence Generation

```bash
# Generate DNA from prompt or sequence
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "input": "ATGCGTACGTTAGCC",
    "input_type": "dna",
    "num_tokens": 120,
    "temperature": 0.7,
    "top_k": 4,
    "top_p": 0.0
  }'
```

### Mutation Resistance Prediction

```bash
# Predict antibiotic resistance
curl -X POST http://localhost:8000/api/dna-predictor/predict \
  -H "Content-Type: application/json" \
  -d '{"mutation": "gyrA S83L"}'

# Get known mutations
curl http://localhost:8000/api/dna-predictor/mutations/known

# Get gene information
curl http://localhost:8000/api/dna-predictor/genes/info
```

---

## 🚀 Production Deployment

### Backend Deployment (Heroku)

```bash
cd backend

# Create Procfile
echo "web: uvicorn app:app --host 0.0.0.0 --port \$PORT" > Procfile

# Create runtime.txt
echo "python-3.10.13" > runtime.txt

# Deploy to Heroku
heroku login
heroku create your-app-name
git push heroku main

# Set environment variables
heroku config:set NVIDIA_API_KEY=your_key
heroku config:set FRONTEND_URLS=https://your-frontend.com
```

### Frontend Deployment (Vercel)

```bash
cd frontend

# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Set environment variables in Vercel dashboard
# NEXT_PUBLIC_API_URL=https://your-backend.com
```

---

## 🐛 Troubleshooting

### Backend Issues

**Problem:** Port 8000 already in use
```bash
# Find and kill process on port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

**Problem:** NVIDIA API Key Error
```
Error: NVIDIA_API_KEY is missing
```
- Verify `.env` file exists in backend folder
- Check API key is valid at build.nvidia.com
- Restart the server after updating `.env`

**Problem:** Module not found
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Frontend Issues

**Problem:** Port 3000 already in use
```bash
# Kill process on port 3000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:3000 | xargs kill -9
```

**Problem:** Three.js not rendering
- Clear browser cache (Ctrl+Shift+Delete)
- Check browser console for errors (F12)
- Verify WebGL support in browser

**Problem:** API connection errors
- Verify backend is running on port 8000
- Check `.env.local` has correct API URL
- Verify CORS is properly configured

---

## 📝 Environment Variables Summary

### Backend (.env)
| Variable | Example | Required |
|----------|---------|----------|
| NVIDIA_API_KEY | abc123... | ✅ Yes |
| NVIDIA_EVO2_URL | https://health.api.nvidia.com/... | ✅ Yes |
| FRONTEND_URLS | http://localhost:3000 | ✅ Yes |
| REQUEST_TIMEOUT_SECONDS | 60 | ❌ No |

### Frontend (.env.local)
| Variable | Example | Required |
|----------|---------|----------|
| NEXT_PUBLIC_API_URL | http://127.0.0.1:8000 | ✅ Yes |

---

## 📚 Project Structure

```
hack/
├── frontend/
│   ├── app/
│   │   ├── dna-generator/      # DNA Generator app
│   │   ├── dna-predictor/      # Resistance Predictor app
│   │   ├── page.js             # Home page
│   │   └── layout.js           # Root layout
│   ├── components/
│   │   ├── Navigation.js       # App navigation
│   │   ├── InputBox.js         # DNA input component
│   │   ├── OutputBox.js        # DNA output component
│   │   └── dna-predictor/      # Predictor components
│   │       ├── DNAHelix3D.js   # 3D visualization
│   │       ├── MutationInput.js
│   │       ├── PredictionCard.js
│   │       └── DataFlowPipeline.js
│   ├── package.json
│   └── tailwind.config.js
│
├── backend/
│   ├── app.py                  # Main FastAPI app
│   ├── dna_predictor_routes.py # Predictor API routes
│   ├── ml_models/
│   │   └── resistance_predictor.py  # ML model
│   ├── requirements.txt
│   └── .env                    # Configuration (not in git)
│
└── README.md, DNA_PREDICTOR_README.md
```

---

## 🤝 Contributing

To add features or fix bugs:

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and test
3. Push to branch: `git push origin feature/your-feature`
4. Create Pull Request

---

## 📄 License

MIT License - See LICENSE file

---

## 🎓 Learning Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Guide](https://fastapi.tiangolo.com/)
- [Three.js Tutorial](https://threejs.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [NVIDIA Evo2 Docs](https://docs.nvidia.com/)

---

##  ✨ Features Checklist

- ✅ DNA Sequence Generation with Evo2
- ✅ Antibiotic Resistance Prediction
- ✅ 3D DNA Helix Visualization
- ✅ Animated Data Pipeline
- ✅ ML Model with scikit-learn
- ✅ LLM Integration Ready
- ✅ Responsive UI
- ✅ History Management
- ✅ API Documentation
- ✅ Error Handling

---

Built with ❤️ for GSOC Hackathon
