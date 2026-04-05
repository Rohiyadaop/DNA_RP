# 🚀 BioGPT Deployment Guide

Complete step-by-step guide for deploying BioGPT to production using Render (backend) and Vercel (frontend).

---

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Backend Deployment (Render)](#backend-deployment-render)
3. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
4. [Connecting Frontend & Backend](#connecting-frontend--backend)
5. [Troubleshooting](#troubleshooting)
6. [Post-Deployment Verification](#post-deployment-verification)

---

## Local Development Setup

### Prerequisites

- **Node.js 18+** - [Download](https://nodejs.org/)
- **Python 3.9+** - [Download](https://www.python.org/)
- **Git** - [Download](https://git-scm.com/)
- **NVIDIA API Key** - [Get Here](https://build.nvidia.com/)
- **GitHub Account** - For version control

### 1. Clone & Setup Repository

```bash
# Clone your repository
git clone https://github.com/yourusername/biogpt.git
cd biogpt

# Initialize Git (if not already done)
git init
git add .
git commit -m "Initial commit: BioGPT full-stack project"
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create Python virtual environment
python -m venv .venv

# Activate environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env

# Edit .env and add your NVIDIA API key
# NVIDIA_API_KEY=nvapi-YOUR-KEY-HERE
```

**Verify Backend Setup:**
```bash
# Test API startup
uvicorn app:app --reload

# Should see output like:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete

# Visit http://127.0.0.1:8000/docs to see interactive API docs
```

### 3. Frontend Setup

```bash
# Navigate to frontend
cd ../frontend

# Install Node dependencies
npm install
# or with yarn
yarn install

# Create .env.local file
cp .env.example .env.local

# Default settings (for local development):
# NEXT_PUBLIC_API_URL=http://127.0.0.1:8000

# Start development server
npm run dev
# or with yarn
yarn dev

# App will be available at http://localhost:3000
```

### 4. Test Locally

1. Open http://localhost:3000 in your browser
2. Try the DNA example (use the "Load example" button)
3. Click "Generate DNA Sequence"
4. You should see a generated DNA sequence colored by base (A, T, G, C)

---

## Backend Deployment (Render)

### Step 1: Push Code to GitHub

```bash
# From project root
git add .
git commit -m "Production-ready BioGPT with deployment configs"
git branch -M main
git remote add origin https://github.com/yourusername/biogpt.git
git push -u origin main

# Verify on GitHub that all files are pushed
```

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New" → "Web Service"
4. Select "Connect to GitHub"

### Step 3: Configure Render Service

**Select Repository:**
- Choose your `biogpt` repository
- Keep default settings, click "Continue"

**Configure Build & Deploy:**
- **Name**: `biogpt-backend`
- **Environment**: `Python 3.11`
- **Build Command**:
  ```bash
  pip install -r backend/requirements.txt
  ```
- **Start Command**:
  ```bash
  cd backend && gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app
  ```
- **Root Directory**: Leave empty (or `/`)
- **Instance Type**: Free tier (or Pay-as-you-go if you prefer)
- **Auto-deploy**: Enable

### Step 4: Add Environment Variables

In Render Dashboard → your service → "Environment":

```
NVIDIA_API_KEY=nvapi-YOUR-ACTUAL-KEY
NVIDIA_EVO2_URL=https://health.api.nvidia.com/v1/biology/arc/evo2-40b/generate
FRONTEND_URLS=http://localhost:3000
REQUEST_TIMEOUT_SECONDS=60
```

Note: After Vercel frontend is deployed, update `FRONTEND_URLS` to include your Vercel URL.

### Step 5: Deploy

1. Click "Create Web Service"
2. Render will build and deploy automatically
3. Wait for the build to complete (~5-10 minutes)
4. You'll see a URL like: `https://biogpt-backend.onrender.com`

**Note**: Render free tier instances spin down after 15 minutes of inactivity. For production use, upgrade to a paid tier.

### Verify Backend Deployment

```bash
# Test the health endpoint
curl https://biogpt-backend.onrender.com/health

# Should return:
# {"status":"ok","model_endpoint":"https://health.api.nvidia.com/v1/biology/arc/evo2-40b/generate","nvidia_key_configured":true}

# Check interactive docs
# Visit https://biogpt-backend.onrender.com/docs
```

---

## Frontend Deployment (Vercel)

### Step 1: Deploy to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New..." → "Project"
3. Select "Import Git Repository"
4. Connect your GitHub account if needed
5. Select your `biogpt` repository
6. Click "Import"

### Step 2: Configure Project Settings

**Framework Preset**: Next.js (auto-detected)

**Build & Output Settings**:
- **Build Command**: `npm run build` (auto)
- **Output Directory**: `.next` (auto)  
- **Root Directory**: `./frontend`

### Step 3: Add Environment Variables

Before deploying, add environment variables:

Click "Environment Variables" and add:

```
Name: NEXT_PUBLIC_API_URL
Value: https://biogpt-backend.onrender.com
```

(Replace with your actual Render backend URL)

### Step 4: Deploy

Click "Deploy"

Vercel will build and deploy automatically (~2-5 minutes)

Your frontend URL will be: `https://biogpt.vercel.app` (or custom domain)

### Step 5: Update Backend CORS

Go back to Render → BioGPT Backend → Environment Variables

Update `FRONTEND_URLS`:
```
FRONTEND_URLS=http://localhost:3000,https://biogpt.vercel.app
```

Click "Save" (backend redeploys automatically)

---

## Connecting Frontend & Backend

### Verify Connection

1. Open your Vercel frontend URL: `https://biogpt.vercel.app`
2. Load an example DNA sequence
3. Click "Generate DNA Sequence"
4. Should work without errors

### If Connection Fails

**Check Vercel Environment Variables:**
```bash
# In Vercel Dashboard → Settings → Environment Variables
# Ensure NEXT_PUBLIC_API_URL points to your Render backend
```

**Check Render CORS:**
```bash
# In Render Dashboard → your service → Environment
# Ensure FRONTEND_URLS includes your Vercel URL
```

**Debug Browser Console:**
1. Open `https://biogpt.vercel.app` in browser
2. Press F12 (Developer Tools)
3. Go to Console tab
4. Try to generate a sequence
5. Look for error messages (usually CORS or 404 errors)

---

## Troubleshooting

### Backend Issues

**Service won't start on Render:**
```
1. Check build command in Render dashboard
2. Verify all dependencies in requirements.txt
3. Check that Python 3.9+ is being used
4. Review build logs in Render dashboard
```

**"NVIDIA_API_KEY is missing" error:**
```
1. Go to Render dashboard
2. Check Environment Variables section
3. Ensure NVIDIA_API_KEY is set correctly
4. Click "Save" to redeploy
5. Wait 1-2 minutes for service to restart
```

**Timeout errors from NVIDIA API:**
```
1. Your API key might have usage limits
2. Check NVIDIA account for quota/billing issues
3. Ensure REQUEST_TIMEOUT_SECONDS is >= 60
```

### Frontend Issues

**"Failed to fetch" or CORS errors:**
```
1. Verify NEXT_PUBLIC_API_URL in Vercel environment variables
2. Check that the URL doesn't have trailing slash
3. Ensure backend FRONTEND_URLS includes your Vercel URL
4. Wait 1-2 minutes after changing environment variables
```

**API URL wrong after deployment:**
```bash
# In Vercel dashboard:
1. Settings → Environment Variables
2. Edit NEXT_PUBLIC_API_URL
3. Change value if needed
4. Trigger new deployment: Deployments → "..." → "Redeploy"
```

**Styling looks broken (no colors):**
```
This means Tailwind CSS isn't working:
1. Check that tailwind.config.js exists in frontend/
2. Run: npm run build locally to test
3. Ensure postcss.config.js is correct
```

---

## Post-Deployment Verification

### 1. API Health Check

```bash
curl https://your-backend.onrender.com/health
```

Expected response:
```json
{
  "status": "ok",
  "model_endpoint": "https://health.api.nvidia.com/v1/biology/arc/evo2-40b/generate",
  "nvidia_key_configured": true
}
```

### 2. Test Generation Endpoint

```bash
curl -X POST https://your-backend.onrender.com/generate \
  -H "Content-Type: application/json" \
  -d '{
    "input": "ATGCGTACGTTAGCCTAGGCTAACCGTTA",
    "input_type": "dna",
    "num_tokens": 100,
    "temperature": 0.7,
    "top_k": 4,
    "top_p": 0.0
  }'
```

Expected response includes:
```json
{
  "generated_sequence": "ATGCGTACGTTAGCCTAGGCTAACCGTTA...",
  "submitted_sequence": "ATGCGTACGTTAGCCTAGGCTAACCGTTA",
  "input_type": "dna",
  "upstream_elapsed_ms": 1234,
  "model_endpoint": "..."
}
```

### 3. Full End-to-End Test

1. Visit your Vercel frontend URL
2. Test DNA mode:
   - Click "Load example" in DNA mode
   - Click "Generate DNA Sequence"
   - Should see colored output in ~10-30 seconds
3. Test Prompt mode:
   - Switch to "Prompt" mode
   - Enter: "GC-rich bacterial promoter"
   - Click "Generate DNA Sequence"
   - Should see derived seed and generated sequence
4. Test History:
   - Should see 1-2 items in history at bottom
   - Click on history item to reload

### 4. Monitor Performance

**Render Console:**
- Go to Render dashboard → Logs
- Look for any Python errors or warnings

**Vercel Analytics:**
- Vercel → Analytics or Web Vitals tab
- Check for any deployment errors

---

## Cost Optimization

### Render Options:
- **Free tier**: Spins down after 15 min inactivity, free but slow on first request
- **Starter**: $7/month - Always running, recommended for demo
- **Production**: $12+/month - For serious use

### Vercel Options:
- **Free tier**: 100 GB bandwidth/month - Fine for most projects
- **Pro**: $20/month - For higher traffic

### NVIDIA API:
- Check free tier credits (usually $5/month)
- Monitor usage in NVIDIA account dashboard
- Set spending limits to avoid surprises

---

## Custom Domain Setup

### Vercel Custom Domain

1. Vercel Dashboard → Select project
2. Settings → Domains
3. Add custom domain (e.g., `biogpt.your-domain.com`)
4. Update DNS records (instructions in Vercel)
5. Wait 24-48 hours for DNS propagation

### Render Custom Domain

1. Render Dashboard → Select service
2. Settings → Custom Domain
3. Add domain
4. Update DNS records
5. Wait for verification

---

## Maintenance & Updates

### Roll Out Code Updates

```bash
# Locally, after making changes:
git add .
git commit -m "Feature: Add DNA validation"
git push origin main

# Both Render and Vercel auto-deploy from main branch
# Wait 2-5 minutes for deployment to complete
```

### Update NVIDIA Credentials

If you change your API key:

1. Generate new key from [build.nvidia.com](https://build.nvidia.com/)
2. Update in Render dashboard → Environment Variables
3. Change `NVIDIA_API_KEY` value
4. Service auto-redeploys (takes 1-2 minutes)

### Monitor Usage

- **NVIDIA**: Monthly API usage at build.nvidia.com
- **Render**: Check active request logs
- **Vercel**: Built-in analytics dashboard

---

## Rollback Plan

If something breaks in production:

```bash
# Find last working commit
git log --oneline

# Revert to previous version
git revert <commit-hash>
git push origin main

# Both services auto-redeploy
# Takes 2-5 minutes to go live again
```

Or in service dashboards:
- **Render**: Deployments tab → select previous build → click "Redeploy"
- **Vercel**: Deployments → click three dots → Redeploy

---

## Final Checklist

- [ ] NVIDIA API key obtained and tested locally
- [ ] GitHub repository created and code pushed
- [ ] Backend deployed to Render with environment variables
- [ ] Frontend deployed to Vercel with environment variables
- [ ] Frontend `NEXT_PUBLIC_API_URL` points to Render backend
- [ ] Backend `FRONTEND_URLS` includes Vercel frontend URL
- [ ] Tested end-to-end generation (DNA and Prompt modes)
- [ ] Verified history saving works
- [ ] Checked browser console for errors
- [ ] Verified Render logs for Python errors
- [ ] Tested copy and download functionality

---

**Congratulations! 🎉 Your BioGPT is now live in production!**

For production support, consider:
- Upgrading to Render's paid tier for always-on service
- Setting up error monitoring (e.g., Sentry)
- Adding analytics (e.g., Vercel Analytics)
- Setting up automated backups if you add a database
