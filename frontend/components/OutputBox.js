"use client";

import { useState } from "react";

const DNA_COLORS = {
  A: "text-dnaA",
  T: "text-dnaT",
  G: "text-dnaG",
  C: "text-dnaC"
};

function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-12 sm:gap-4 sm:py-16">
      <div className="h-10 w-10 animate-spin rounded-full border-4 border-cyan-300/20 border-t-cyan-300 sm:h-14 sm:w-14" />
      <p className="text-xs text-slate-300 sm:text-sm">Contacting NVIDIA Evo2 and decoding a fresh DNA sequence...</p>
    </div>
  );
}

function ColorCodedSequence({ label, sequence }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-black/20 p-3 sm:rounded-3xl sm:p-4">
      <div className="mb-2 flex flex-col gap-1 items-start justify-between sm:mb-3 sm:flex-row sm:items-center sm:gap-2">
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">{label}</p>
        <p className="text-xs text-slate-500">{sequence.length} bases</p>
      </div>
      <div className="dna-scrollbar max-h-40 overflow-y-auto rounded-xl bg-slate-950/40 p-2 font-mono text-xs leading-6 break-all sm:max-h-56 sm:rounded-2xl sm:p-4 sm:text-sm sm:leading-8">
        {sequence.split("").map((base, index) => (
          <span className={DNA_COLORS[base] || "text-slate-200"} key={`${base}-${index}`}>
            {base}
          </span>
        ))}
      </div>
    </div>
  );
}

export default function OutputBox({ loading, result }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!result?.generated_sequence) {
      return;
    }

    await navigator.clipboard.writeText(result.generated_sequence);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1800);
  };

  const handleDownload = () => {
    if (!result?.generated_sequence) {
      return;
    }

    const blob = new Blob([result.generated_sequence], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "biogpt-evo2-sequence.txt";
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <section className="glass-card">
      <div className="mb-4 flex flex-col gap-1 sm:mb-6 sm:gap-2">
        <h2 className="text-xl font-semibold text-white sm:text-2xl">Generated Output</h2>
        <p className="text-xs text-slate-300 sm:text-sm">
          Your returned DNA sequence appears here with nucleotide-aware coloring, plus one-click copy and download actions.
        </p>
      </div>

      {loading ? (
        <LoadingSpinner />
      ) : result ? (
        <div className="space-y-3 sm:space-y-5">
          <div className="grid gap-3 grid-cols-1 sm:gap-4 sm:grid-cols-3">
            <div className="rounded-2xl border border-white/10 bg-slate-950/30 p-3 sm:rounded-3xl sm:p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Input Type</p>
              <p className="mt-1 text-base font-semibold text-white capitalize sm:mt-2 sm:text-lg">{result.input_type}</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-slate-950/30 p-3 sm:rounded-3xl sm:p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Upstream Time</p>
              <p className="mt-1 text-base font-semibold text-white sm:mt-2 sm:text-lg">
                {result.upstream_elapsed_ms ? `${result.upstream_elapsed_ms} ms` : "Unavailable"}
              </p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-slate-950/30 p-3 sm:rounded-3xl sm:p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Model Endpoint</p>
              <p className="mt-1 truncate text-xs font-medium text-white break-words sm:mt-2 sm:text-sm">{result.model_endpoint}</p>
            </div>
          </div>

          <div className="flex flex-col gap-2 sm:flex-row sm:gap-3">
            <button
              className="rounded-full bg-cyan-300/15 px-3 py-2 text-xs font-medium text-cyan-100 transition hover:bg-cyan-300/20 sm:px-4 sm:py-2 sm:text-sm"
              onClick={handleCopy}
              type="button"
            >
              {copied ? "Copied" : "Copy sequence"}
            </button>
            <button
              className="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-xs font-medium text-slate-200 transition hover:bg-white/10 sm:px-4 sm:py-2 sm:text-sm"
              onClick={handleDownload}
              type="button"
            >
              Download .txt
            </button>
          </div>

          {result.input_type === "prompt" ? (
            <ColorCodedSequence label="Evo2 Seed Derived From Prompt" sequence={result.submitted_sequence} />
          ) : null}

          <ColorCodedSequence label="Generated DNA Sequence" sequence={result.generated_sequence} />
        </div>
      ) : (
        <div className="rounded-2xl border border-dashed border-white/10 bg-slate-950/20 px-4 py-8 text-center sm:rounded-3xl sm:px-6 sm:py-12">
          <p className="text-base font-medium text-white sm:text-lg">No sequence yet</p>
          <p className="mt-2 text-xs text-slate-400 sm:text-sm">
            Submit a DNA sequence or prompt from the left panel to see Evo2 output here.
          </p>
        </div>
      )}
    </section>
  );
}

