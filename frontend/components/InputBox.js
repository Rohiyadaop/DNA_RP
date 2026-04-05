const DNA_PLACEHOLDER = `>example_sequence
ATGCGTACGTTAGCCTAGGCTAACCGTTA`;

const PROMPT_PLACEHOLDER =
  "Design a GC-rich bacterial promoter seed for a stable synthetic biology experiment.";

const EXAMPLES = {
  dna: DNA_PLACEHOLDER,
  prompt: PROMPT_PLACEHOLDER
};

export default function InputBox({
  error,
  inputMode,
  inputValue,
  loading,
  onGenerate,
  onInputChange,
  onModeChange,
  onSettingChange,
  settings
}) {
  const metricLabel =
    inputMode === "dna"
      ? `${inputValue.replace(/[^ATGCatgc]/g, "").length} DNA bases detected`
      : `${inputValue.trim().length} prompt characters`;

  return (
    <section className="glass-card">
      <div className="mb-4 flex flex-col gap-3 sm:mb-6 sm:gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-white sm:text-2xl">Input Workspace</h2>
          <p className="mt-1 text-xs text-slate-300 sm:text-sm">
            Submit a DNA seed directly or write a natural language prompt that the backend converts into a DNA seed.
          </p>
        </div>
        <div className="inline-flex rounded-full border border-white/10 bg-slate-950/40 p-1">
          {["dna", "prompt"].map((mode) => (
            <button
              key={mode}
              className={`rounded-full px-2 py-1 text-xs font-medium capitalize transition sm:px-4 sm:py-2 sm:text-sm ${
                inputMode === mode
                  ? "bg-cyan-300/15 text-cyan-100"
                  : "text-slate-300 hover:bg-white/5 hover:text-white"
              }`}
              onClick={() => onModeChange(mode)}
              type="button"
            >
              {mode}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-3 sm:space-y-5">
        <div>
          <div className="mb-2 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <label className="text-xs font-medium text-slate-200 sm:text-sm">
              {inputMode === "dna" ? "DNA Sequence or FASTA" : "Natural Language Prompt"}
            </label>
            <button
              className="rounded-full border border-white/10 bg-white/5 px-2 py-1 text-xs font-medium text-slate-200 transition hover:bg-white/10 w-fit"
              onClick={() => onInputChange(EXAMPLES[inputMode])}
              type="button"
            >
              Load example
            </button>
          </div>
          <textarea
            className="glass-input min-h-[160px] sm:min-h-[240px]"
            onChange={(event) => onInputChange(event.target.value)}
            placeholder={inputMode === "dna" ? DNA_PLACEHOLDER : PROMPT_PLACEHOLDER}
            value={inputValue}
          />
          <div className="mt-2 flex flex-col gap-2 text-xs text-slate-400 sm:flex-row sm:items-center sm:justify-between">
            <span>{metricLabel}</span>
            <span className="text-right sm:text-left">
              {inputMode === "dna" ? "Allowed bases: A T G C" : "Prompt is translated to a DNA seed automatically"}
            </span>
          </div>
        </div>

        <div className="grid gap-3 grid-cols-1 sm:gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-200 sm:mb-2 sm:text-sm">Number of generated bases</label>
            <input
              className="glass-input"
              min="16"
              max="1024"
              onChange={(event) => onSettingChange("numTokens", event.target.value)}
              type="number"
              value={settings.numTokens}
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-200 sm:mb-2 sm:text-sm">Temperature</label>
            <input
              className="glass-input"
              max="2"
              min="0"
              onChange={(event) => onSettingChange("temperature", event.target.value)}
              step="0.1"
              type="number"
              value={settings.temperature}
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-200 sm:mb-2 sm:text-sm">Top K</label>
            <input
              className="glass-input"
              max="6"
              min="1"
              onChange={(event) => onSettingChange("topK", event.target.value)}
              type="number"
              value={settings.topK}
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-200 sm:mb-2 sm:text-sm">Top P</label>
            <input
              className="glass-input"
              max="1"
              min="0"
              onChange={(event) => onSettingChange("topP", event.target.value)}
              step="0.1"
              type="number"
              value={settings.topP}
            />
          </div>
        </div>

        <div>
          <label className="mb-1 block text-xs font-medium text-slate-200 sm:mb-2 sm:text-sm">Random Seed (optional)</label>
          <input
            className="glass-input"
            onChange={(event) => onSettingChange("randomSeed", event.target.value)}
            placeholder="Leave blank for non-deterministic generation"
            type="number"
            value={settings.randomSeed}
          />
        </div>

        {error ? (
          <div className="rounded-2xl border border-rose-300/20 bg-rose-400/10 px-3 py-2 text-xs text-rose-100 sm:rounded-3xl sm:px-4 sm:py-3 sm:text-sm">{error}</div>
        ) : null}

        <button
          className="inline-flex w-full items-center justify-center rounded-2xl bg-gradient-to-r from-cyan-400 via-sky-400 to-orange-300 px-4 py-3 text-xs font-semibold text-slate-950 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-70 sm:rounded-3xl sm:px-5 sm:py-4 sm:text-sm"
          disabled={loading || !inputValue.trim()}
          onClick={onGenerate}
          type="button"
        >
          {loading ? "Generating DNA..." : "Generate DNA Sequence"}
        </button>
      </div>
    </section>
  );
}

