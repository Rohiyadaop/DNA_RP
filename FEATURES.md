# ✨ BioGPT Features & User Guide

Comprehensive documentation of all BioGPT features and how to use them.

---

## 🎯 Core Features

### 1. Dual Input Modes

#### DNA Mode
**What it does:** Submit raw DNA sequences in FASTA or plain text format.

**Supported formats:**
```
Plain DNA:
ATGCGTACGTTAGCCTAGGCTAACCGTTA

FASTA format:
>sequence_name
ATGCGTACGTTAGCCTAGGCTAA
GGCTAACCGTTA

Mixed with newlines:
>my_sequence
ATGCGTACG
TTAGCCTAG
GCTAACCGTTA
```

**How it works:**
1. Switch to DNA mode (toggle at top)
2. Paste DNA sequence
3. System auto-detects and counts bases
4. Validates (only A, T, G, C allowed)
5. Sends to NVIDIA Evo2 for generation

#### Prompt Mode
**What it does:** Describe DNA in natural language, backend converts to seed.

**Example prompts:**
- "GC-rich bacterial promoter sequence"
- "Stable human kozak sequence"
- "Flexible ribosome binding site"
- "Palindromic restriction site"
- "Yeast centromere region"

**Conversion process:**
1. Extract biological keywords (promoter, gc-rich, stable, etc.)
2. Encode prompt text as DNA bases
3. Add start codon (ATG) and stop codon (TAA)
4. Hash the prompt for semantic variations
5. Combine all parts into seed (48-640 bases)
6. Evo2 generates new sequence from seed

**Recognized keywords:**
- Structural: promoter, coding, intron, exon, UTR
- Sequence properties: GC-rich, AT-rich, stable, flexible
- Organism: bacteria, yeast, human
- Features: palindrome, restriction, start codon, stop codon
- Binding: ribosome, kozak

---

### 2. Advanced Generation Parameters

#### Number of Tokens (Generated Bases)
- **Range:** 16-1024 bases
- **Default:** 120
- **Impact:** More bases = longer sequences, slower generation
- **Use case:** Start with 120, increase for longer genes

#### Temperature
- **Range:** 0.0-2.0
- **Default:** 0.7
- **Effect:**
  - 0.0 = Deterministic (always same)
  - 0.7 = Balanced (recommended)
  - 1.5+ = Very random, creative
- **Use case:** Lower for conservative sequences, higher for diversity

#### Top K
- **Range:** 1-6
- **Default:** 4
- **Effect:** Limits diversity at each position
  - 1 = Always pick best (no randomness)
  - 6 = Most flexible/diverse
- **Use case:** Lower for specific sequences, higher for exploration

#### Top P (Nucleus Sampling)
- **Range:** 0.0-1.0
- **Default:** 0.0
- **Effect:** 
  - 0.0 = Disabled
  - 0.5 = Medium diversity
  - 1.0 = Maximum diversity
- **Use case:** Enable for alternative sequence generation

#### Random Seed
- **Range:** 0-2147483647
- **Default:** Empty (random)
- **Effect:** Same seed + same parameters = identical output
- **Use case:** Reproducible research, testing

---

### 3. DNA Color Coding

**Automatic visualization with distinct colors:**

| Base | Color | Hex Code |
|------|-------|----------|
| A (Adenine) | Cyan | #38bdf8 |
| T (Thymine) | Red | #fb7185 |
| G (Guanine) | Green | #34d399 |
| C (Cytosine) | Yellow | #fbbf24 |

**Benefits:**
- Visual pattern recognition
- Easier to spot sequences by eye
- Biologically meaningful representation
- Accessible to all users

---

### 4. Copy & Download

#### Copy to Clipboard
- **Action:** Click "Copy sequence" button
- **What it does:** Copies entire generated sequence to clipboard
- **Notification:** Button shows "Copied" for 1.8 seconds
- **Use case:** Paste into other bioinformatics tools

#### Download as .txt
- **Action:** Click "Download .txt" button
- **What it does:** Downloads sequence as `biogpt-evo2-sequence.txt`
- **File format:** Plain text, one sequence per file
- **Use case:** Save multiple sequences, backup, sharing

---

### 5. Local History (Browser Storage)

#### Automatic History
- **Capacity:** Last 8 generations stored
- **Auto-save:** Every successful generation
- **Storage:** Browser localStorage (persists on page refresh)
- **Duration:** Indefinite (until cache cleared)

#### History Features
- **Click to restore:** Click any history item to reload
  - Restores input text
  - Restores all parameters
  - Restores output
- **Timestamp:** Shows when generated
- **Preview:** Shows input snippet + generated output preview

#### History Limitations
- Max 8 items (oldest automatically removed)
- Cleared if browser cache is cleared
- Per-domain (separate for localhost vs production URL)
- No cloud backup (browser-only)

#### Clear History
- **Action:** Click "Clear history" button
- **Effect:** Removes all 8 stored items
- **Irreversible:** Cannot undo

---

## 🔧 Parameter Recommendations

### Conservative Sequences
```
Temperature: 0.5
Top K: 2
Random Seed: Set for reproducibility
Length: 150-200 bases
```
**Use case:** Critical regulatory regions

### Exploratory Sequences
```
Temperature: 1.0-1.2
Top K: 5-6
Random Seed: Empty
Length: 200-300 bases
```
**Use case:** Brainstorming, generating alternatives

### Fast Generation
```
Length: 50-100 bases
Temperature: 0.7
Top K: 4
```
**Use case:** Quick tests, multiple iterations

### Production-Grade
```
Length: 300-500 bases
Temperature: 0.6-0.8
Top K: 3-4
Random Seed: Documented seed
```
**Use case:** Publishing, reproducible research

---

## 📊 Data Flow Visualization

```
User Input (DNA or Prompt)
        ↓
Frontend Validation
        ↓
API Request (Fetch)
        ↓
Backend Processing
├─ DNA: Validation + normalization
└─ Prompt: Conversion to seed
        ↓
NVIDIA Evo2 API Call
        ↓
Sequence Generation (AI)
        ↓
Response Processing
├─ Base color mapping
├─ History save
└─ Display rendering
        ↓
User sees colored output
```

---

## 💡 Use Cases

### 1. Synthetic Biology Design
```
Prompt: "Strong prokaryotic ribosome binding site with stable GC-rich region"
Use: Design expression cassette components
```

### 2. Promoter Discovery
```
DNA Mode: Paste candidate promoter region
Generate 5-10 variants with high temperature
Analyze for conservation
```

### 3. Codon Optimization
```
Prompt: "High translation human kozak sequence"
Generate multiple variants
Select based on codon usage preferences
```

### 4. Educational Demonstration
```
Use DNA mode with simple sequences
Show AI-generated variations
Discuss biological plausibility
```

### 5. Regulatory Element Library
```
Generate multiple promoter/enhancer variants
Download each as separate file
Build personal database
```

---

## 🎨 UI/UX Features

### Glassmorphism Design
- Frosted glass effect with blur
- Semi-transparent panels
- Modern, approachable aesthetic
- Works on all screen sizes

### Responsive Layout
- **Desktop:** Two-column (input + output side-by-side)
- **Tablet:** Single column, touchable buttons
- **Mobile:** Full-width, optimized spacing
- Touch-friendly button sizes

### Real-time Feedback
- Character/base counter updates as you type
- Button states change on interaction
- Loading spinner shows progress
- Error messages in red, inline

### Accessibility
- High color contrast (WCAG compliant)
- Keyboard navigation support
- Clear labels on all inputs
- Semantic HTML structure

---

## 🔐 Security & Privacy

### Data Handling
- **Input:** No logging of your sequences
- **Output:** Generated sequences not stored server-side
- **History:** Stored locally in your browser only
- **API calls:** HTTPS encrypted to NVIDIA

### CORS Protection
- Requests only from configured frontend
- Cross-site request validation
- Prevents unauthorized API usage

### No Tracking
- No analytics/cookies by default
- No user profiling
- No sequence sharing
- Privacy-focused

---

## ⚡ Performance Tips

### Fast Responses
- Keep tokens under 200 for instant results
- Use temperature 0.7-0.9 (slower at extremes)
- Test locally before production queries

### Better Results
- Use specific prompts (include organism, property)
- Longer DNA seeds generate better (150+ bases)
- Multiple runs with different temperature

### Handling Timeouts
- Reduce num_tokens if timeout occurs (60s limit)
- Check NVIDIA API status
- Try again after a few seconds
- Error message will guide you

---

## 🆘 Troubleshooting Features

### Error Messages Guide
| Message | Cause | Solution |
|---------|-------|----------|
| "DNA input must contain only A, T, G, C" | Invalid characters | Remove non-DNA characters |
| "No DNA content found" | Empty after FASTA parsing | Check sequence format |
| "Unable to generate" | API connection issue | Check backend URL in console |
| "Request timed out" | Generation too complex | Reduce num_tokens |
| "NVIDIA API error" | API key/quota issue | Check NVIDIA dashboard |

### Debug Checklist
1. Open browser DevTools (F12)
2. Go to Console tab
3. Check for error messages
4. Network tab shows API request details
5. Application tab shows localStorage history

---

## 🚀 Workflow Example

**Goal:** Generate 3-4 promoter variants and pick the best

```
1. Switch to Prompt mode
2. Enter: "GC-rich bacterial promoter sequence"
3. Set Temperature to 1.2 (more variation)
4. Set num_tokens to 150
5. Generate
   → See generated sequence + seed

6. Click "Copy sequence"
7. Paste into analysis tool A
8. Rate sequence

9. Change Temperature to 0.9
10. Generate again
   → Different variant, same seed base

11. Repeat 2-3 more times

12. Keep best variant
13. Click history to restore each try
14. Analyze side-by-side

Result: Library of 4 related variants
```

---

## 📚 Educational Resources

### Understanding Parameters

**Temperature Explained:**
- Lower = Model more confident in choices
- Higher = Model takes more risks
- 0.0 = Deterministic (no variation)
- 2.0 = Maximum randomness

**Why Color Coding Matters:**
- See GC content visually (green + yellow = high GC)
- Pattern recognition (repeats, palindromes)
- Educational tool for learning DNA structure

### Prompt Engineering Tips

**Good prompts:**
- Specific organism (bacterial, yeast, human)
- Sequence property (GC-rich, flexible, stable)
- Feature type (promoter, binding site, regulatory)

**Less effective:**
- Vague descriptions
- Made-up biological terms
- Combinations without basis

### API Documentation
See [backend/README.md](backend/README.md) for technical API details.

---

## 🔄 Future Features (Planned)

Potential additions being considered:
- Batch upload (multiple sequences)
- Compare sequences side-by-side
- Codon usage analysis
- GC content calculator
- Sequence alignment viewer
- Cloud history sync
- GeneBank file import/export

---

## 📝 Summary

BioGPT provides a complete, user-friendly interface for DNA sequence generation powered by state-of-the-art AI. Whether you're a biologist, student, or researcher, the combination of dual input modes, advanced parameters, and modern UI makes it accessible and powerful.

**Start with:** DNA mode + default settings  
**Explore with:** Prompt mode + temperature variations  
**Accomplish:** Generate novel sequences for your research

Happy generating! 🧬
