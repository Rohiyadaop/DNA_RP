# 📖 BioGPT Quick Reference

Fast lookup for common commands, configurations, and troubleshooting.

---

## ⚡ Essential Commands

### Backend Startup
```bash
cd backend
python -m venv .venv           # Create environment once
.venv\Scripts\activate         # Windows
source .venv/bin/activate      # macOS/Linux
pip install -r requirements.txt # Install once
uvicorn app:app --reload       # Start server
```

**Access:** http://127.0.0.1:8000 (docs: /docs)

### Frontend Startup
```bash
cd frontend
npm install                    # Install once
npm run dev                    # Start server
```

**Access:** http://localhost:3000

### Production Build & Test
```bash
# Backend
cd backend
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app

# Frontend
cd frontend
npm run build
npm run start
```

---

## 🔧 Environment Setup

### Backend .env
```
NVIDIA_API_KEY=nvapi-YOUR-KEY
NVIDIA_EVO2_URL=https://health.api.nvidia.com/v1/biology/arc/evo2-40b/generate
FRONTEND_URLS=http://localhost:3000,https://biogpt.vercel.app
REQUEST_TIMEOUT_SECONDS=60
```

### Frontend .env.local
```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000    # Development
# NEXT_PUBLIC_API_URL=https://backend-url.onrender.com  # Production
```

---

## 🌐 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Service info |
| GET | `/health` | Health check |
| POST | `/generate` | Generate DNA |

### /generate Request
```json
{
  "input": "ATGCGTACGTTA...",
  "input_type": "dna",
  "num_tokens": 120,
  "temperature": 0.7,
  "top_k": 4,
  "top_p": 0.0,
  "random_seed": null
}
```

### /generate Response
```json
{
  "generated_sequence": "ATGCGTACGTTA...",
  "submitted_sequence": "ATGCGTACGTTA...",
  "input_type": "dna",
  "upstream_elapsed_ms": 1234,
  "model_endpoint": "https://..."
}
```

---

## 📂 File Structure Quick Map

```
biogpt/
├── README.md              ← Start here
├── DEPLOYMENT.md          ← Production deploy
├── FEATURES.md           ← Feature guide
├── QUICK_REFERENCE.md    ← This file
│
├── backend/
│   ├── app.py            ← Main FastAPI app
│   ├── requirements.txt   ← Dependencies
│   ├── .env.example      ← Config template
│   └── README.md         ← Backend guide
│
└── frontend/
    ├── package.json      ← Dependencies
    ├── next.config.js    ← Next.js config
    ├── tailwind.config.js ← Styling config
    ├── app/
    │   ├── page.js       ← Main page
    │   ├── layout.js     ← Root layout
    │   └── globals.css   ← Global styles
    ├── components/
    │   ├── InputBox.js   ← Input interface
    │   └── OutputBox.js  ← Output display
    ├── .env.example      ← Config template
    └── README.md         ← Frontend guide
```

---

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] Code works locally (both frontend + backend)
- [ ] All environment variables set in .env
- [ ] NVIDIA API key is active and funded
- [ ] Git repository is clean and committed

### Deploy Backend (Render)
- [ ] Push code to GitHub
- [ ] Connect GitHub to Render
- [ ] Set environment variables in Render
- [ ] Verify `/health` endpoint works
- [ ] Copy Render URL

### Deploy Frontend (Vercel)
- [ ] Connect GitHub to Vercel
- [ ] Set `NEXT_PUBLIC_API_URL` to Render URL
- [ ] Build succeeds (`npm run build`)
- [ ] App loads and connects to backend
- [ ] Copy Vercel URL

### Post-Deployment
- [ ] Update Render `FRONTEND_URLS` with Vercel URL
- [ ] Test end-to-end generation
- [ ] Test DNA mode + Prompt mode
- [ ] Check history works
- [ ] Verify copy/download buttons

---

## 🔐 Secure Configuration

### API Key Management
```bash
# NEVER commit .env files
# .gitignore should include:
backend/.env
backend/.env.local
frontend/.env.local

# Use environment variables instead:
# Render Dashboard → Environment Variables
# Vercel Dashboard → Settings → Environment Variables
```

### CORS Configuration
```python
# Render Env Variable:
FRONTEND_URLS=http://localhost:3000,https://biogpt.vercel.app
# Comma-separated, no trailing slashes
```

---

## 🐛 Common Issues & Fixes

### Backend Won't Start
```bash
# Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check port isn't in use
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows
```

### Frontend Can't Reach Backend
```bash
# Check .env.local
cat frontend/.env.local

# Should have:
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000

# Test backend is running
curl http://127.0.0.1:8000/health
```

### CORS Errors
```bash
# Error: "Access to XMLHttpRequest blocked by CORS policy"

# Solution: Update Render backend env var:
FRONTEND_URLS=http://localhost:3000,https://your-url.vercel.app

# Wait 1-2 minutes for backend to restart
```

### NVIDIA API Errors
```bash
# Error: "NVIDIA_API_KEY is missing"

# Check key is set in Render/local .env:
grep NVIDIA_API_KEY backend/.env
echo $NVIDIA_API_KEY  # Should show your key

# Verify key at: https://build.nvidia.com/
```

### Timeout Errors
```bash
# Error: "Request timed out"

# Solutions:
1. Reduce num_tokens (try 100 instead of 200)
2. Check NVIDIA service status
3. Increase REQUEST_TIMEOUT_SECONDS in Render env

# Minimum viable settings:
num_tokens: 50
temperature: 0.7
timeout: 60
```

---

## 📊 Testing Commands

### Test Backend API
```bash
# Health check
curl http://127.0.0.1:8000/health

# Generate DNA
curl -X POST http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"input":"ATGC","input_type":"dna","num_tokens":50}'

# Generate from prompt
curl -X POST http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"input":"promoter","input_type":"prompt","num_tokens":50}'

# Pretty print response
# Add | python -m json.tool (macOS/Linux)
# Add | python -m json.tool (Windows)
```

### Test Frontend
```bash
# Development
npm run dev

# Build test
npm run build
npm run start

# Lint check
npm run lint
```

---

## 🎛️ Parameter Quick Reference

| Parameter | Recommended | Min | Max | Notes |
|-----------|-------------|-----|-----|-------|
| num_tokens | 120 | 16 | 1024 | Higher = longer generation |
| temperature | 0.7 | 0.0 | 2.0 | Higher = more random |
| top_k | 4 | 1 | 6 | Higher = more diversity |
| top_p | 0.0 | 0.0 | 1.0 | 0 to disable, higher = creative |
| timeout | 60 | 30 | 120 | Seconds for NVIDIA API |

---

## 📚 Documentation Links

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Project overview |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Complete deployment guide |
| [FEATURES.md](FEATURES.md) | User features & guide |
| [backend/README.md](backend/README.md) | Backend documentation |
| [frontend/README.md](frontend/README.md) | Frontend documentation |
| QUICK_REFERENCE.md | This file |

---

## 🔍 Debug Workflow

1. **Check Logs**
   ```bash
   # Backend
   Check Render dashboard → Logs (or terminal output)
   Look for Python errors or stack traces
   
   # Frontend
   Browser F12 → Console tab
   Look for error messages or 404s
   ```

2. **Test Network**
   ```bash
   Browser F12 → Network tab
   Try the generate action
   Check request/response status and headers
   ```

3. **Test API Directly**
   ```bash
   curl -v http://127.0.0.1:8000/health
   Should return 200 OK + JSON
   ```

4. **Check Environment**
   ```bash
   # Backend
   echo $NVIDIA_API_KEY
   grep FRONTEND_URLS backend/.env
   
   # Frontend
   cat frontend/.env.local
   ```

---

## 💾 Git Workflow

```bash
# Setup once
git config user.name "Your Name"
git config user.email "your@email.com"

# Daily workflow
git status                          # See changes
git add .                          # Stage all
git commit -m "Feature: description" # Commit
git push origin main               # Push to GitHub

# Both Render + Vercel auto-deploy from main
# Wait 2-5 minutes for deployment

# Rollback if needed
git log --oneline                  # See history
git revert <commit-hash>           # Revert to previous
git push origin main               # New deploy
```

---

## 🎓 Learning Paths

### For Beginners
1. Read [README.md](README.md)
2. Run locally: `npm run dev` (frontend) + `uvicorn app:app` (backend)
3. Test with DNA mode first
4. Read [FEATURES.md](FEATURES.md)

### For Developers
1. Read [backend/README.md](backend/README.md)
2. Read [frontend/README.md](frontend/README.md)
3. Understand API flow in [backend/app.py](backend/app.py)
4. Study React hooks in [frontend/app/page.js](frontend/app/page.js)

### For Deployment
1. Read [DEPLOYMENT.md](DEPLOYMENT.md)
2. Try local production build
3. Deploy to Render (backend first)
4. Deploy to Vercel (frontend second)
5. Follow checklist

---

## 📞 Support Resources

### Error Solutions
- Check browser console (F12 → Console)
- Check backend logs (Render dashboard or terminal)
- Review error in [DEPLOYMENT.md Troubleshooting](DEPLOYMENT.md#troubleshooting)
- Test with curl commands above

### API Questions
- OpenAPI docs: `/docs` endpoint on backend
- [backend/README.md](backend/README.md)

### Feature Questions
- [FEATURES.md](FEATURES.md)
- Component README files above

### Deployment Questions
- [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 🎯 Resume Highlights

**Full-Stack Development:**
- FastAPI backend with async/await
- Next.js 14 frontend with React hooks
- Secure REST API with CORS
- LocalStorage state persistence

**DevOps & Deployment:**
- Render backend deployment
- Vercel frontend deployment
- Environment variable management
- GitHub CI/CD integration

**Features Implemented:**
- NVIDIA Evo2 AI integration
- DNA color coding visualization
- Multi-mode input (DNA/Prompt)
- Parameter tuning UI
- History management
- Error handling
- Copy/Download functionality

**Tech Stack:**
```
Backend:  FastAPI, Python 3.9+, httpx, pydantic
Frontend: Next.js 14, React 18, Tailwind CSS 3
Deployment: Render, Vercel, GitHub, NVIDIA API
Styling: Glassmorphism, responsive design
```

---

**Last Updated:** 2024  
**Version:** 1.0.0  
**Status:** Production Ready
