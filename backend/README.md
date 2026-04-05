# 🧬 BioGPT Backend API

FastAPI backend for BioGPT DNA generation service using NVIDIA Evo2 AI model.

## Quick Start

```bash
# Setup
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your NVIDIA_API_KEY

# Run
uvicorn app:app --reload
```

API available at: `http://127.0.0.1:8000`  
Interactive docs: `http://127.0.0.1:8000/docs`

## Architecture

### Core Files
- **app.py** - FastAPI application with all endpoints and business logic
- **requirements.txt** - Python package dependencies
- **.env.example** - Environment variable template

### Key Components

**Pydantic Models:**
- `GenerateRequest` - Incoming request schema with validation
- `GenerateResponse` - Response schema with generated sequence

**Functions:**

| Function | Purpose |
|----------|---------|
| `parse_fasta_or_plain_dna()` | Validates and normalizes DNA sequences |
| `prompt_to_dna_seed()` | Converts natural language to DNA seed |
| `bytes_to_dna()` | Encodes text as DNA bases |
| `keyword_motifs()` | Extracts biological keywords from prompts |
| `invoke_evo2()` | Makes async request to NVIDIA API |
| `sanitize_generated_sequence()` | Cleans API response |

### Endpoints

```
GET  /               → Service info
GET  /health         → API health check
POST /generate       → Generate DNA sequence
```

## Environment Variables

```bash
# Required
NVIDIA_API_KEY=nvapi-your-key-here

# Optional with defaults
NVIDIA_EVO2_URL=https://health.api.nvidia.com/v1/biology/arc/evo2-40b/generate
FRONTEND_URLS=http://localhost:3000
REQUEST_TIMEOUT_SECONDS=60
```

## API Examples

### Health Check
```bash
curl http://127.0.0.1:8000/health
```

### Generate from DNA
```bash
curl -X POST http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "input": "ATGCGTACGTTAGCCTAGGCTAACCGTTA",
    "input_type": "dna",
    "num_tokens": 120,
    "temperature": 0.7,
    "top_k": 4,
    "top_p": 0.0
  }'
```

### Generate from Prompt
```bash
curl -X POST http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Design a GC-rich stable promoter sequence",
    "input_type": "prompt",
    "num_tokens": 150,
    "temperature": 0.8,
    "top_k": 5,
    "top_p": 0.1
  }'
```

## Request Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| input | string | 2-5000 | - | DNA sequence or natural language |
| input_type | enum | dna, prompt | dna | Input format |
| num_tokens | integer | 16-1024 | 120 | Generated bases count |
| temperature | float | 0.0-2.0 | 0.7 | Sampling randomness |
| top_k | integer | 1-6 | 4 | Top-k diversity |
| top_p | float | 0.0-1.0 | 0.0 | Nucleus sampling |
| random_seed | integer | 0-2147483647 | null | Optional reproducibility |

## Error Handling

**422 Unprocessable Entity** - Invalid input
```json
{"detail": "DNA input must contain only A, T, G, and C characters."}
```

**500 Server Error** - Missing API key
```json
{"detail": "NVIDIA_API_KEY is missing. Add it to backend/.env before starting the API."}
```

**502 Bad Gateway** - NVIDIA API error
```json
{"detail": "Unable to reach NVIDIA Evo2: ..."}
```

**504 Gateway Timeout** - Request too slow
```json
{"detail": "The request to NVIDIA Evo2 timed out. Try again with fewer tokens."}
```

## Development

### Type Checking
```bash
mypy app.py
```

### Code Formatting
```bash
black app.py
```

### Linting
```bash
flake8 app.py
```

## Deployment

See [DEPLOYMENT.md](../DEPLOYMENT.md) for detailed production deployment guide.

Quick deploy to Render:
```bash
git push origin main
# Render auto-deploys from GitHub
```

## Technical Details

### CORS Security
- Configured to accept requests from specified frontend URLs only
- Prevents unauthorized cross-origin requests
- Update `FRONTEND_URLS` for each deployment

### Async/Await
- All endpoints and NVIDIA calls use async patterns
- Handles concurrent requests efficiently
- FastAPI runs with Uvicorn async server

### API Integration
- Uses `httpx` for async HTTP requests
- Proper timeout handling (default 60s, configurable)
- Comprehensive error messages from NVIDIA API

### DNA Processing
- **DNA Input**: FASTA format or plain sequence, case-insensitive
- **Prompt Input**: Multi-step conversion
  1. Extract biological keywords (promoter, GC-rich, etc.)
  2. Encode prompt text to DNA using base mapping
  3. Create SHA256 hash seed
  4. Combine components with start (ATG) and stop (TAA) codons
  5. Ensure length between 48-640 bases

## Support

For issues:
1. Check `.env` file has correct API key
2. Verify NVIDIA API key is active at build.nvidia.com
3. Review error logs in console
4. Test endpoint with `curl` command from examples above
