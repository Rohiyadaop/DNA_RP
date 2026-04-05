"use client";

const DEFAULT_STEPS = [
  {
    key: "input",
    code: "IN",
    label: "DNA Input",
    detail: "Waiting for mutation or sequence payload.",
    metric: "Standby",
    status: "idle",
  },
  {
    key: "encoding",
    code: "KM",
    label: "Encoding",
    detail: "3-mer and residue signatures are generated here.",
    metric: "Sparse vectors",
    status: "idle",
  },
  {
    key: "ml",
    code: "ML",
    label: "ML Model",
    detail: "Classifier score will appear after vectorization.",
    metric: "LogReg",
    status: "idle",
  },
  {
    key: "reasoning",
    code: "AI",
    label: "LLM Reasoning",
    detail: "Biological reasoning layer enriches the prediction.",
    metric: "Evo 2-ready",
    status: "idle",
  },
  {
    key: "output",
    code: "OUT",
    label: "Final Output",
    detail: "Resistance class, confidence, and explanation are rendered here.",
    metric: "Pending",
    status: "idle",
  },
];

function statusClasses(status) {
  switch (status) {
    case "completed":
      return {
        card: "border-cyan-400/30 bg-cyan-400/8 shadow-[0_18px_45px_rgba(34,211,238,0.12)]",
        badge: "border-cyan-300/30 bg-cyan-300/12 text-cyan-100",
        dot: "bg-cyan-300",
      };
    case "processing":
      return {
        card: "border-fuchsia-400/30 bg-fuchsia-400/10 shadow-[0_18px_45px_rgba(168,85,247,0.16)]",
        badge: "border-fuchsia-300/30 bg-fuchsia-300/12 text-fuchsia-100",
        dot: "bg-fuchsia-300 animate-pulse",
      };
    case "error":
      return {
        card: "border-rose-400/30 bg-rose-400/8",
        badge: "border-rose-300/30 bg-rose-300/12 text-rose-100",
        dot: "bg-rose-300",
      };
    default:
      return {
        card: "border-white/10 bg-white/[0.03]",
        badge: "border-white/10 bg-white/[0.05] text-slate-300",
        dot: "bg-slate-600",
      };
  }
}

export default function DataFlowPipeline({
  steps = DEFAULT_STEPS,
  isProcessing = false,
  consoleLines = [],
}) {
  const logs =
    consoleLines.length > 0
      ? consoleLines
      : [
          "01 DNA Input :: Waiting for sample submission.",
          "02 Encoding :: 3-mer / residue vectorization idle.",
          "03 ML Model :: Logistic regression ready.",
        ];

  return (
    <section className="neon-panel rounded-[30px] p-5 sm:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="status-chip w-fit border-cyan-400/30 bg-cyan-400/10 text-cyan-100">
            Live Processing Pipeline
          </p>
          <h3 className="mt-4 text-2xl font-semibold text-white">
            Input / Encoding / Prediction / Explanation
          </h3>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
            The interface streams each stage of the decision path so the user can
            see how molecular input turns into a resistance call.
          </p>
        </div>

        <div className="metric-tile rounded-2xl px-4 py-3">
          <p className="text-[10px] uppercase tracking-[0.28em] text-slate-400">Stream State</p>
          <p className="mt-2 text-sm font-medium text-white">
            {isProcessing ? "Processing live" : "Standing by"}
          </p>
        </div>
      </div>

      <div className="relative mt-8">
        <div className="absolute left-[8%] right-[8%] top-7 hidden h-px bg-white/10 xl:block">
          <div className={`data-stream h-full ${isProcessing ? "is-active" : ""}`} />
        </div>

        <div className="grid gap-3 xl:grid-cols-5">
          {steps.map((step, index) => {
            const styles = statusClasses(step.status);
            return (
              <div
                key={step.key || `${step.label}-${index}`}
                className={`rounded-[26px] border p-4 transition duration-300 ${styles.card}`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div
                    className={`inline-flex h-11 w-11 items-center justify-center rounded-2xl border text-xs font-semibold tracking-[0.2em] ${styles.badge}`}
                  >
                    {step.code}
                  </div>
                  <span className={`mt-2 h-2.5 w-2.5 rounded-full ${styles.dot}`} />
                </div>

                <p className="mt-4 text-lg font-medium text-white">{step.label}</p>
                <p className="mt-2 text-sm leading-6 text-slate-300">{step.detail}</p>

                <div className="mt-4 rounded-2xl border border-white/10 bg-black/20 px-3 py-2">
                  <p className="text-[10px] uppercase tracking-[0.24em] text-slate-500">Signal</p>
                  <p className="mt-1 text-sm font-medium text-white">{step.metric}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="mt-6 rounded-[28px] border border-white/10 bg-black/20 p-4">
        <div className="flex items-center justify-between gap-3">
          <p className="text-[10px] uppercase tracking-[0.3em] text-slate-400">Telemetry Stream</p>
          <span className="text-xs text-slate-500">Live pipeline narration</span>
        </div>

        <div className="dna-scrollbar mt-4 max-h-56 space-y-2 overflow-y-auto font-mono text-xs text-slate-300">
          {logs.map((line) => (
            <div
              key={line}
              className="rounded-2xl border border-white/10 bg-white/[0.03] px-3 py-2 leading-6"
            >
              {line}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
