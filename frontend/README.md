# 💻 BioGPT Frontend

Modern React/Next.js frontend with Tailwind CSS styling for DNA sequence generation.

## Quick Start

```bash
# Setup
npm install
# or: yarn install

# Configure
cp .env.example .env.local
# Edit .env.local with your backend API URL

# Run Development
npm run dev
# or: yarn dev
```

App available at: `http://localhost:3000`

## Architecture

### Core Files
- **app/page.js** - Main application page with state management
- **app/layout.js** - Root layout with metadata
- **app/globals.css** - Global styles with Tailwind
- **components/InputBox.js** - DNA/Prompt input interface
- **components/OutputBox.js** - Results display with color coding
- **tailwind.config.js** - Theme configuration with DNA colors
- **package.json** - Dependencies and build scripts

### Key Features

**State Management:**
- Input mode (DNA/Prompt)
- Input value
- Generation parameters
- Results
- History (localStorage)
- Loading state
- Error handling

**LocalStorage Features:**
- Persists last 8 generations
- Auto-loads on page refresh
- Clear history button
- Click to restore previous run

**UI Components:**
- Glassmorphism design
- DNA color coding (A, T, G, C)
- Loading spinner
- Error messages
- Copy & download buttons
- History grid

## Environment Variables

```bash
# In .env.local

# Required
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000

# Optional for future expansions
# NEXT_PUBLIC_ANALYTICS_ID=your_analytics_id
```

**Note:** `NEXT_PUBLIC_` prefix makes variable available in browser (not secret data)

## Components

### InputBox.js
**Props:**
- `inputMode` - "dna" or "prompt"
- `inputValue` - Current input text
- `settings` - Generation parameters
- `loading` - Loading state
- `error` - Error message
- `onModeChange` - Mode switch handler
- `onInputChange` - Input text handler
- `onSettingChange` - Parameter change handler
- `onGenerate` - Generation handler

**Features:**
- Mode toggle (DNA/Prompt)
- FASTA format support
- Live character counter
- Parameter controls
- Error display
- Generate button

### OutputBox.js
**Props:**
- `result` - Generation result object
- `loading` - Loading state

**Features:**
- Color-coded DNA display
- Timing information
- Copy to clipboard
- Download as .txt
- Submitted sequence display (for prompt mode)
- Loading spinner

## Styling

### Tailwind Colors (Custom)
```css
--color-dnaA: #38bdf8 (Cyan)
--color-dnaT: #fb7185 (Red)
--color-dnaG: #34d399 (Green)
--color-dnaC: #fbbf24 (Yellow)
--color-panel: rgba(10, 17, 32, 0.72)
--color-accent: #67e8f9
```

### CSS Classes
- `.glass-input` - Input field with blur effect
- `.glass-card` - Card container
- `.dna-scrollbar` - Custom scrollbar for sequences
- `.hero` - Background gradient

## API Integration

**Endpoint:** `POST /generate`

**Request:**
```javascript
{
  input: string,              // DNA or prompt
  input_type: "dna"|"prompt", // Input type
  num_tokens: number,         // Generated bases
  temperature: number,        // 0.0-2.0
  top_k: number,             // 1-6
  top_p: number,             // 0.0-1.0
  random_seed: number|null   // Optional
}
```

**Response:**
```javascript
{
  generated_sequence: string,  // New DNA bases
  submitted_sequence: string,  // Input sequence/seed
  input_type: string,         // Type echo
  upstream_elapsed_ms: number, // NVIDIA response time
  model_endpoint: string      // API endpoint used
}
```

## Key Functions

| Function | Purpose |
|----------|---------|
| `handleGenerate()` | Calls API and updates results |
| `handleHistorySelect()` | Restores previous generation |
| `handleClearHistory()` | Clears localStorage |
| `buildHistoryItem()` | Creates history record |
| `formatTimestamp()` | Localizes date display |

## Development

### Build for Production
```bash
npm run build
# Creates optimized .next folder
```

### Start Production Server
```bash
npm run start
# Runs optimized build
```

### Linting
```bash
npm run lint
# Checks for code issues
```

## Deployment

See [DEPLOYMENT.md](../DEPLOYMENT.md) for full production guide.

Quick deploy to Vercel:
```bash
# Automatic via GitHub
# 1. Push to GitHub
# 2. Vercel auto-deploys
# 3. Add NEXT_PUBLIC_API_URL in Vercel dashboard
```

## Performance Optimization

- **Static Generation:** Pages pre-built at build time
- **Image Optimization:** Next.js image component (if added)
- **Code Splitting:** Automatic per-route bundling
- **Compression:** Automatic gzip compression
- **Caching:** Browser cache headers configured

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Works on:
- Desktop browsers
- Tablets (iPad, Android tablets)
- Mobile devices (responsive design)

## Data Privacy

- No data sent to external services except NVIDIA API
- All sequences processed locally on your instance
- LocalStorage history stays in user's browser
- No tracking or analytics by default

## Accessibility

- Semantic HTML structure
- Color contrast compliant
- Keyboard navigation support
- ARIA labels on interactive elements
- Focus indicators on buttons

## Common Issues

**API connection fails:**
1. Check `NEXT_PUBLIC_API_URL` in .env.local
2. Verify backend is running at that URL
3. Look for CORS errors in browser console
4. On Vercel, ensure environment variable is set

**Styling looks broken:**
1. Check tailwind.config.js exists
2. Run `npm run build` to test
3. Clear browser cache (Ctrl+Shift+Delete)
4. Check for CSS import errors in globals.css

**History not persisting:**
1. Check localStorage isn't disabled
2. Verify browser settings allow storage
3. Check browser console for errors
4. Try a different browser

## Testing

### Manual Testing Checklist
- [ ] Load example DNA sequence
- [ ] Generate DNA sequence
- [ ] Verify color coding (A=cyan, T=red, G=green, C=yellow)
- [ ] Test copy button
- [ ] Test download button
- [ ] Switch to prompt mode
- [ ] Generate from natural language
- [ ] Check history saves
- [ ] Click history item to restore
- [ ] Clear history button works
- [ ] Error handling (invalid input, timeout)

## Future Enhancements

Potential additions:
- FASTA batch upload
- Multiple simultaneous generations
- Save to cloud instead of localStorage
- Compare sequences side-by-side
- Alignment visualization
- Codon usage analysis
- GC content calculator

## Support

For issues:
1. Check browser console for errors (F12)
2. Verify API URL in .env.local
3. Test backend connection with curl
4. Review DEPLOYMENT.md troubleshooting section
