"use client";

function tonePalette(result) {
  if (!result) {
    return {
      accent: "#67e8f9",
      secondary: "#8b5cf6",
      soft: "rgba(103, 232, 249, 0.12)",
      border: "border-cyan-400/20",
      label: "Standby",
      summary: "Awaiting a mutation or sequence signal.",
    };
  }

  if (result.resistant) {
    return {
      accent: "#fb7185",
      secondary: "#f97316",
      soft: "rgba(251, 113, 133, 0.14)",
      border: "border-rose-400/30",
      label: "Resistance Detected",
      summary: "The model sees a resistance-like phenotype.",
    };
  }

  return {
    accent: "#22d3ee",
    secondary: "#7c3aed",
    soft: "rgba(34, 211, 238, 0.14)",
    border: "border-cyan-400/30",
    label: "Low Resistance Signal",
    summary: "The signal stays closer to lower-risk patterns.",
  };
}

function ProbabilityBar({ label, value, accentClass, trackClass }) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between gap-3 text-sm">
        <span className="text-slate-300">{label}</span>
        <span className="font-medium text-white">{Math.round(value * 100)}%</span>
      </div>
      <div className={`signal-track ${trackClass}`}>
        <div
          className={`signal-fill ${accentClass}`}
          style={{ width: `${Math.max(6, Math.round(value * 100))}%` }}
        />
      </div>
    </div>
  );
}

export default function PredictionCard({ result, isLoading, error }) {
  const palette = tonePalette(result);

  if (error) {
    return (
      <section className="neon-panel rounded-[30px] border-rose-400/30 p-5 sm:p-6">
        <p className="status-chip w-fit border-rose-400/30 bg-rose-400/10 text-rose-100">
          Prediction Halted
        </p>
        <h2 className="mt-4 text-2xl font-semibold text-white">Unable to complete analysis</h2>
        <p className="mt-3 text-sm leading-6 text-slate-300">{error}</p>
      </section>
    );
  }

  if (isLoading && !result) {
    return (
      <section className="neon-panel rounded-[30px] p-5 sm:p-6">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="status-chip w-fit border-cyan-400/30 bg-cyan-400/10 text-cyan-100">
              Scoring Mutation
            </p>
            <h2 className="mt-4 text-2xl font-semibold text-white">Prediction engine online</h2>
            <p className="mt-2 text-sm text-slate-300">
              Encoding molecular signatures, running the classifier, and preparing
              the explanation layer.
            </p>
          </div>
          <div className="h-14 w-14 animate-spin rounded-full border-2 border-cyan-300/20 border-t-cyan-300" />
        </div>

        <div className="mt-6 grid gap-3 sm:grid-cols-3">
          {[0, 1, 2].map((index) => (
            <div
              key={index}
              className="h-24 rounded-[24px] border border-white/10 bg-white/[0.03] animate-pulse"
            />
          ))}
        </div>
      </section>
    );
  }

  if (!result) {
    return (
      <section className="neon-panel rounded-[30px] p-5 sm:p-6">
        <p className="status-chip w-fit border-white/10 bg-white/5 text-slate-200">
          Result Feed
        </p>
        <h2 className="mt-4 text-2xl font-semibold text-white">Prediction snapshot</h2>
        <p className="mt-2 text-sm leading-6 text-slate-300">{palette.summary}</p>

        <div className="mt-6 grid gap-3 sm:grid-cols-3">
          <div className="metric-tile rounded-[24px] px-4 py-4">
            <p className="text-[10px] uppercase tracking-[0.28em] text-slate-400">Classifier</p>
            <p className="mt-2 text-sm font-medium text-white">Logistic Regression</p>
          </div>
          <div className="metric-tile rounded-[24px] px-4 py-4">
            <p className="text-[10px] uppercase tracking-[0.28em] text-slate-400">Confidence</p>
            <p className="mt-2 text-sm font-medium text-white">Pending</p>
          </div>
          <div className="metric-tile rounded-[24px] px-4 py-4">
            <p className="text-[10px] uppercase tracking-[0.28em] text-slate-400">Reasoning</p>
            <p className="mt-2 text-sm font-medium text-white">Evo 2-ready</p>
          </div>
        </div>
      </section>
    );
  }

  const confidencePercent = Math.round(result.confidence * 100);
  const resistantPercent = Math.round(result.probability_resistant * 100);
  const notResistantPercent = Math.round(result.probability_not_resistant * 100);
  const confidenceGradient = `conic-gradient(${palette.accent} 0deg ${
    confidencePercent * 3.6
  }deg, rgba(255,255,255,0.08) ${confidencePercent * 3.6}deg 360deg)`;

  return (
    <section className={`neon-panel rounded-[30px] p-5 sm:p-6 ${palette.border}`}>
      <div className="flex flex-col gap-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p
              className="status-chip w-fit"
              style={{
                borderColor: palette.soft,
                backgroundColor: palette.soft,
                color: "white",
              }}
            >
              {palette.label}
            </p>
            <h2 className="mt-4 text-3xl font-semibold text-white">{result.prediction}</h2>
            <p className="mt-2 max-w-xl text-sm leading-6 text-slate-300">
              {palette.summary} This output combines vectorized mutation features
              with a biological reasoning layer.
            </p>
          </div>

          <div className="confidence-orb mx-auto lg:mx-0" style={{ background: confidenceGradient }}>
            <div className="confidence-orb__inner">
              <span className="text-[11px] uppercase tracking-[0.28em] text-slate-400">
                Confidence
              </span>
              <span className="mt-2 text-4xl font-semibold text-white">
                {confidencePercent}%
              </span>
            </div>
          </div>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <div className="metric-tile rounded-[24px] px-4 py-4">
            <p className="text-[10px] uppercase tracking-[0.28em] text-slate-400">Model</p>
            <p className="mt-2 text-sm font-medium text-white">{result.model_name}</p>
          </div>
          <div className="metric-tile rounded-[24px] px-4 py-4">
            <p className="text-[10px] uppercase tracking-[0.28em] text-slate-400">Input Type</p>
            <p className="mt-2 text-sm font-medium capitalize text-white">{result.input_type}</p>
          </div>
          <div className="metric-tile rounded-[24px] px-4 py-4">
            <p className="text-[10px] uppercase tracking-[0.28em] text-slate-400">Reasoning</p>
            <p className="mt-2 text-sm font-medium text-white">{result.reasoning_source}</p>
          </div>
          <div className="metric-tile rounded-[24px] px-4 py-4">
            <p className="text-[10px] uppercase tracking-[0.28em] text-slate-400">Focus Locus</p>
            <p className="mt-2 text-sm font-medium text-white">
              {result.mutation_label || "Sequence anomaly scan"}
            </p>
          </div>
        </div>

        <div className="rounded-[28px] border border-white/10 bg-black/20 p-4">
          <div className="flex items-center justify-between gap-4">
            <p className="text-[10px] uppercase tracking-[0.3em] text-slate-400">
              Probability Breakdown
            </p>
            <span className="text-xs text-slate-500">
              Based on classifier output and biological calibration
            </span>
          </div>

          <div className="mt-4 space-y-4">
            <ProbabilityBar
              label="Resistant"
              value={result.probability_resistant}
              accentClass="from-rose-400 via-fuchsia-400 to-orange-300"
              trackClass="bg-rose-950/40"
            />
            <ProbabilityBar
              label="Not Resistant"
              value={result.probability_not_resistant}
              accentClass="from-cyan-300 via-sky-400 to-violet-400"
              trackClass="bg-cyan-950/30"
            />
          </div>
        </div>

        {result.gene_info ? (
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="metric-tile rounded-[24px] px-4 py-4">
              <p className="text-[10px] uppercase tracking-[0.28em] text-slate-400">Gene</p>
              <p className="mt-2 text-sm font-medium text-white">{result.gene_info.gene}</p>
            </div>
            <div className="metric-tile rounded-[24px] px-4 py-4">
              <p className="text-[10px] uppercase tracking-[0.28em] text-slate-400">Protein</p>
              <p className="mt-2 text-sm font-medium text-white">{result.gene_info.protein}</p>
            </div>
            <div className="metric-tile rounded-[24px] px-4 py-4">
              <p className="text-[10px] uppercase tracking-[0.28em] text-slate-400">
                Antibiotic Class
              </p>
              <p className="mt-2 text-sm font-medium text-white">
                {result.gene_info.antibiotic_class}
              </p>
            </div>
          </div>
        ) : (
          <div className="metric-tile rounded-[24px] px-4 py-4">
            <p className="text-[10px] uppercase tracking-[0.28em] text-slate-400">
              Sequence Input
            </p>
            <p className="mt-2 text-sm font-medium text-white">
              {resistantPercent}% resistant vs {notResistantPercent}% not resistant
            </p>
          </div>
        )}
      </div>
    </section>
  );
}
