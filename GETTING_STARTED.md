# 🚀 Getting Started with BioGPT

**Fast track to running BioGPT locally in under 10 minutes.**

---

## 📋 Requirements

Before starting, you need:
- [ ] Python 3.9+ ([Download](https://www.python.org/))
- [ ] Node.js 18+ ([Download](https://nodejs.org/))
- [ ] NVIDIA API Key ([Get Here](https://build.nvidia.com/))
- [ ] Text editor (VS Code recommended)

---

## ⚡ 5-Minute Quick Start

Open **two terminals** side-by-side.

### Terminal 1: Backend

```bash
# Navigate to backend
cd backend

# Create Python virtual environment (one-time)
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install packages (one-time)
pip install -r requirements.txt

# Setup environment file
cp .env.example .env

# IMPORTANT: Edit .env and paste your NVIDIA API key
# Open .env file in editor, find NVIDIA_API_KEY line, paste your key

# Start server
uvicorn app:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Terminal 2: Frontend

```bash
# Navigate to frontend
cd frontend

# Install packages (one-time)
npm install

# Setup environment file
cp .env.example .env.local

# Start development server
npm run dev
```

You should see:
```
Local:        http://localhost:3000
```

---

## 🌐 Open in Browser

1. Visit: **http://localhost:3000**
2. You should see the BioGPT interface
3. The page is interactive - try these steps:

### Test 1: DNA Mode (Easiest)
1. Click "Load example" button
2. Click "Generate DNA Sequence"
3. Wait 10-30 seconds
4. See colored DNA output

### Test 2: Prompt Mode
1. Switch to "Prompt" mode (top toggle)
2. Type: `promoter sequence`
3. Click "Generate DNA Sequence"
4. See generated output

### Test 3: History
1. Do a few generations
2. Scroll down to "Local History"
3. Click any saved item
4. It restores all settings

---

## 🔑 Where's My NVIDIA API Key?

### Get Your Key (2 minutes)

1. Go to: https://build.nvidia.com/
2. Sign up or log in
3. Go to API Console
4. Copy your API key (looks like `nvapi-...`)
5. Paste into `backend/.env`:

```
NVIDIA_API_KEY=nvapi-your-actual-key-here
```

6. Save file
7. Backend should work (try refreshing browser)

### If No Key Yet

Get free credits from NVIDIA:
1. Create account at build.nvidia.com
2. You get $5/month free tier
3. Copy the API key
4. That's it!

---

## ✅ Common First-Time Issues

### Issue: "Cannot find python"
```bash
# Try:
python3 --version

# If that works, use python3 instead of python in commands
python3 -m venv .venv
```

### Issue: "Port 3000/8000 already in use"
```bash
# Windows - kill process on port 3000:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:3000 | xargs kill -9
```

### Issue: "Cannot find npm"
- Reinstall Node.js from https://nodejs.org/
- Make sure to check "npm" during installation

### Issue: "Blank page" or "Cannot connect to backend"
1. Make sure both terminals are running
2. Backend should show "Uvicorn running on http://127.0.0.1:8000"
3. Frontend should show "Local: http://localhost:3000"
4. Check browser console (F12 → Console tab)

### Issue: "NVIDIA_API_KEY is missing"
1. Edit `backend/.env`
2. Find the line with `NVIDIA_API_KEY=`
3. Replace `nvapi-your-key-here` with your actual key
4. Save file
5. Backend automatically restarts

---

## 🎨 What You're Looking At

### Left Panel (Input)
- **Toggle:** Switch between DNA and Prompt modes
- **Text area:** Paste DNA or describe sequence
- **Sliders:** Adjust generation settings
- **Button:** Generate new sequence

### Right Panel (Output)
- **Colored bases:** A=Cyan, T=Red, G=Green, C=Yellow
- **Buttons:** Copy or download sequence
- **Stats:** Generation time and stats

### Bottom (History)
- **Cards:** Your recent generations
- **Click any:** Restores that run
- **Clear:** Removes all history

---

## 📝 Next Steps

Once you have it running:

### 1. Experiment (5 minutes)
- Try different temperature values
- Generate with different num_tokens
- Try both DNA and Prompt modes
- Download a sequence

### 2. Understand (10 minutes)
- Read [FEATURES.md](FEATURES.md) for all features
- Read [README.md](README.md) for full documentation

### 3. Deploy (30 minutes)
- When ready for production, follow [DEPLOYMENT.md](DEPLOYMENT.md)
- Takes ~30 minutes to deploy to Render + Vercel

### 4. Customize (varies)
- Add your own prompt keywords in backend
- Change colors in frontend/tailwind.config.js
- Add new parameters as needed

---

## 🐛 Quick Debugging

**If something breaks:**

1. **Check terminal output** - Look for red error messages
2. **Check browser console** - Press F12 → Console tab
3. **Restart both servers:**
   ```bash
   # Both terminals: Ctrl+C to stop
   # Then restart with commands above
   ```

4. **Check environment:**
   ```bash
   # Backend - does .env have API key?
   cat backend/.env
   
   # Frontend - does .env.local have API URL?
   cat frontend/.env.local
   ```

5. **Test backend directly:**
   ```bash
   # In new terminal:
   curl http://127.0.0.1:8000/health
   
   # Should return: {"status":"ok",...}
   ```

---

## 📚 Documentation

Once running, explore these:
- **[README.md](README.md)** - Full project docs
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Commands & tips
- **[FEATURES.md](FEATURES.md)** - All features explained
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Ready to deploy?
- **[backend/README.md](backend/README.md)** - API details
- **[frontend/README.md](frontend/README.md)** - Code details

---

## 🎓 Learning Points

As you use the app, notice:

**Frontend (React):**
- State management with useState/useEffect
- API calls with fetch
- LocalStorage for persistence
- Component composition

**Backend (FastAPI):**
- Async request handling
- Input validation with Pydantic
- Error handling
- External API integration

**Integration:**
- How frontend calls backend
- How to handle loading/error states
- CORS configuration

---

## ✨ Tips for Best Results

1. **Start with DNA mode** - Simpler to understand
2. **Use default parameters** - Temperature 0.7 is good
3. **Keep tokens under 500** - Faster generation
4. **Read error messages** - They tell you what's wrong
5. **Try prompt mode** - See intelligent seed generation

---

## 🎯 Success Checklist

You've successfully set up BioGPT when:
- [ ] Backend terminal shows "Uvicorn running"
- [ ] Frontend terminal shows "Local: http://localhost:3000"
- [ ] Browser loads page (not blank/error)
- [ ] "Load example" button works
- [ ] Can generate DNA sequence
- [ ] Output shows colored bases
- [ ] History saves generations
- [ ] No errors in browser console (F12)

---

## 🆘 Stuck?

**Check in this order:**

1. **Is backend running?**
   ```bash
   curl http://127.0.0.1:8000/health
   ```
   Should return JSON (not error)

2. **Is frontend running?**
   - Browser should not show blank/error
   - Check console (F12) for errors

3. **Is API key set?**
   ```bash
   # Check:
   cat backend/.env
   # Should have: NVIDIA_API_KEY=nvapi-...
   ```

4. **Is npm/python installed?**
   ```bash
   npm --version  # Should show version
   python --version  # Should show 3.9+
   ```

5. **Are both files correct?**
   - `backend/.env` - Has NVIDIA_API_KEY
   - `frontend/.env.local` - Empty is OK (has default)

---

## 📞 Useful Resources

| Resource | Link |
|----------|------|
| Python | https://python.org/ |
| Node.js | https://nodejs.org/ |
| NVIDIA API | https://build.nvidia.com/ |
| FastAPI Docs | https://fastapi.tiangolo.com/ |
| Next.js Docs | https://nextjs.org/ |
| React Docs | https://react.dev/ |

---

## 🎉 You're Ready!

That's it! You now have a working BioGPT instance.

**Next:** Try generating some sequences, then read [FEATURES.md](FEATURES.md) to understand what you can do.

**When ready to deploy:** Follow [DEPLOYMENT.md](DEPLOYMENT.md)

**Questions?** Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) or read the full [README.md](README.md)

---

**Happy generating! 🧬**

Go to http://localhost:3000 and start creating DNA sequences! 🚀
