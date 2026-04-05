"use client";

export default function ExplanationPanel({ result, error, lastRequest }) {
  if (error) {
    return (
      <section className="neon-panel rounded-[30px] p-5 sm:p-6">
        <p className="status-chip w-fit border-rose-400/30 bg-rose-400/10 text-rose-100">
          Explanation Unavailable
        </p>
        <h3 className="mt-4 text-2xl font-semibold text-white">Reasoning layer stopped</h3>
        <p className="mt-3 text-sm leading-6 text-slate-300">
          The scientific explanation could not be produced because the prediction
          pipeline did not complete successfully.
        </p>
      </section>
    );
  }

  if (!result) {
    return (
      <section className="neon-panel rounded-[30px] p-5 sm:p-6">
        <p className="status-chip w-fit border-white/10 bg-white/5 text-slate-200">
          Explanation Panel
        </p>
        <h3 className="mt-4 text-2xl font-semibold text-white">Scientific reasoning will appear here</h3>
        <p className="mt-3 text-sm leading-6 text-slate-300">
          Submit a mutation such as <span className="text-cyan-200">gyrA S83L</span> or a
          mutated DNA fragment to generate a model-backed explanation with
          biological context.
        </p>

        <div className="mt-6 grid gap-3 sm:grid-cols-2">
          <div className="metric-tile rounded-[24px] px-4 py-4">
            <p className="text-[10px] uppercase tracking-[0.28em] text-slate-400">Expected Input</p>
            <p className="mt-2 text-sm font-medium text-white">
              {lastRequest.inputType === "sequence" ? "Mutated DNA sequence" : "Gene mutation"}
            </p>
          </div>
          <div className="metric-tile rounded-[24px] px-4 py-4">
            <p className="text-[10px] uppercase tracking-[0.28em] text-slate-400">Reasoning Mode</p>
            <p className="mt-2 text-sm font-medium text-white">Evo 2-ready fallback synthesis</p>
          </div>
        </div>
      </section>
    );
  }

  const markers = result.encoding.detected_markers || [];
  const topKmers = result.encoding.top_kmers || [];

  return (
    <section className="neon-panel rounded-[30px] p-5 sm:p-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="status-chip w-fit border-violet-400/30 bg-violet-400/10 text-violet-100">
            Explanation Layer
          </p>
          <h3 className="mt-4 text-2xl font-semibold text-white">AI-generated biological interpretation</h3>
        </div>
        <div className="metric-tile rounded-2xl px-4 py-3 lg:min-w-[220px]">
          <p className="text-[10px] uppercase tracking-[0.28em] text-slate-400">Reasoning Source</p>
          <p className="mt-2 text-sm font-medium text-white">{result.reasoning_source}</p>
        </div>
      </div>

      <div className="mt-6 rounded-[28px] border border-white/10 bg-black/20 p-5">
        <p className="text-[10px] uppercase tracking-[0.3em] text-slate-400">Narrative Summary</p>
        <p className="mt-4 text-sm leading-7 text-slate-100">{result.explanation}</p>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <div className="rounded-[28px] border border-white/10 bg-white/[0.03] p-5">
          <p className="text-[10px] uppercase tracking-[0.3em] text-slate-400">Scientific Rationale</p>
          <div className="mt-4 space-y-3">
            {result.scientific_rationale.map((item) => (
              <div
                key={item}
                className="rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm leading-6 text-slate-200"
              >
                {item}
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-4">
          <div className="rounded-[28px] border border-white/10 bg-white/[0.03] p-5">
            <p className="text-[10px] uppercase tracking-[0.3em] text-slate-400">Encoding Summary</p>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <div className="metric-tile rounded-2xl px-4 py-4">
                <p className="text-[10px] uppercase tracking-[0.24em] text-slate-400">Strategy</p>
                <p className="mt-2 text-sm font-medium text-white">{result.encoding.strategy}</p>
              </div>
              <div className="metric-tile rounded-2xl px-4 py-4">
                <p className="text-[10px] uppercase tracking-[0.24em] text-slate-400">Input Length</p>
                <p className="mt-2 text-sm font-medium text-white">{result.encoding.input_length}</p>
              </div>
              <div className="metric-tile rounded-2xl px-4 py-4">
                <p className="text-[10px] uppercase tracking-[0.24em] text-slate-400">GC Content</p>
                <p className="mt-2 text-sm font-medium text-white">
                  {Math.round(result.encoding.gc_content * 100)}%
                </p>
              </div>
              <div className="metric-tile rounded-2xl px-4 py-4">
                <p className="text-[10px] uppercase tracking-[0.24em] text-slate-400">Vector Size</p>
                <p className="mt-2 text-sm font-medium text-white">{result.encoding.vector_dimensions}</p>
              </div>
            </div>
          </div>

          <div className="rounded-[28px] border border-white/10 bg-white/[0.03] p-5">
            <p className="text-[10px] uppercase tracking-[0.3em] text-slate-400">Dominant Signatures</p>
            <div className="mt-4 flex flex-wrap gap-2">
              {topKmers.length ? (
                topKmers.map((token) => (
                  <span
                    key={token}
                    className="glow-pill border-cyan-400/20 bg-cyan-400/10 text-cyan-100"
                  >
                    {token}
                  </span>
                ))
              ) : (
                <span className="text-sm text-slate-400">No dominant k-mers captured.</span>
              )}
            </div>
          </div>

          <div className="rounded-[28px] border border-white/10 bg-white/[0.03] p-5">
            <p className="text-[10px] uppercase tracking-[0.3em] text-slate-400">Detected Evidence Markers</p>
            <div className="mt-4 flex flex-wrap gap-2">
              {markers.length ? (
                markers.map((marker) => (
                  <span
                    key={marker}
                    className="glow-pill border-fuchsia-400/20 bg-fuchsia-400/10 text-fuchsia-100"
                  >
                    {marker}
                  </span>
                ))
              ) : (
                <span className="text-sm text-slate-400">
                  No curated markers were matched directly.
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
