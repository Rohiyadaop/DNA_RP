"use client";

import { useMemo, useState } from "react";

const EXAMPLES = {
  mutation: [
    {
      label: "gyrA S83L",
      value: "gyrA S83L",
      note: "Classic fluoroquinolone resistance hotspot",
    },
    {
      label: "rpoB S450L",
      value: "rpoB S450L",
      note: "High-risk rifampicin escape mutation",
    },
    {
      label: "katG S315T",
      value: "katG S315T",
      note: "Well-known isoniazid resistance driver",
    },
  ],
  sequence: [
    {
      label: "QRDR-like motif",
      value: "ATGCGATCGTCTTTAGCGTACGATCGATGCCGATCGATCGTACGATCGATC",
      note: "Contains a resistant-like codon motif",
    },
    {
      label: "Lower-risk motif",
      value: "ATGCGATCGTCTACTGCGTACGATCGATGCCGATCGATCGTACGATCGATC",
      note: "Contains a more neutral sequence signature",
    },
    {
      label: "High-GC snippet",
      value: "GCGCGACCGCGGCGTCCGCGACCGGCGCCGATCGGCGCCGCGGCGATCGCGC",
      note: "Useful for testing k-mer and GC analysis",
    },
  ],
};

const MODE_LABELS = {
  mutation: "Gene mutation",
  sequence: "Mutated DNA sequence",
};

export default function MutationInput({ onPredict, isLoading }) {
  const [inputMode, setInputMode] = useState("mutation");
  const [value, setValue] = useState("gyrA S83L");

  const sequenceStats = useMemo(() => {
    const validBases = value.toUpperCase().replace(/[^ATGC]/g, "");
    const gcCount = validBases.split("").filter((base) => base === "G" || base === "C").length;
    return {
      length: validBases.length,
      gcContent: validBases.length ? Math.round((gcCount / validBases.length) * 100) : 0,
    };
  }, [value]);

  const activeExamples = EXAMPLES[inputMode];

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!value.trim()) {
      return;
    }

    onPredict({
      input: value.trim(),
      inputType: inputMode,
    });
  };

  const loadExample = (exampleValue) => {
    setValue(exampleValue);
  };

  return (
    <section className="neon-panel scan-panel rounded-[30px] p-5 sm:p-6">
      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="status-chip w-fit border-cyan-400/30 bg-cyan-400/10 text-cyan-100">
              Intelligent Input
            </p>
            <h2 className="mt-3 text-2xl font-semibold text-white sm:text-3xl">
              Mutation Signal Console
            </h2>
            <p className="mt-2 max-w-xl text-sm leading-6 text-slate-300">
              Submit a curated mutation or a mutated DNA fragment. The predictor
              will encode the signal, score resistance, and attach a structured
              scientific explanation.
            </p>
          </div>

          <div className="grid gap-2 sm:min-w-[220px]">
            <div className="metric-tile rounded-2xl px-4 py-3">
              <p className="text-[10px] uppercase tracking-[0.28em] text-slate-400">
                Accepted Modes
              </p>
              <p className="mt-2 text-sm font-medium text-white">
                Mutation + DNA sequence
              </p>
            </div>
            <div className="metric-tile rounded-2xl px-4 py-3">
              <p className="text-[10px] uppercase tracking-[0.28em] text-slate-400">
                Output
              </p>
              <p className="mt-2 text-sm font-medium text-white">
                Resistance probability + explanation
              </p>
            </div>
          </div>
        </div>

        <div className="inline-flex w-fit rounded-full border border-white/10 bg-black/20 p-1">
          {Object.keys(MODE_LABELS).map((mode) => {
            const active = inputMode === mode;
            return (
              <button
                key={mode}
                type="button"
                onClick={() => {
                  setInputMode(mode);
                  setValue(EXAMPLES[mode][0].value);
                }}
                className={`rounded-full px-4 py-2 text-sm font-medium transition ${
                  active
                    ? "bg-gradient-to-r from-cyan-400/30 via-sky-400/20 to-fuchsia-400/25 text-white"
                    : "text-slate-300 hover:bg-white/5 hover:text-white"
                }`}
              >
                {MODE_LABELS[mode]}
              </button>
            );
          })}
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <div className="mb-2 flex items-center justify-between">
              <label className="text-xs uppercase tracking-[0.28em] text-slate-400">
                {inputMode === "mutation" ? "Mutation signature" : "DNA sequence payload"}
              </label>
              <span className="text-xs text-slate-500">
                {inputMode === "mutation"
                  ? "Format: gene + amino-acid change"
                  : `${sequenceStats.length} bases / ${sequenceStats.gcContent}% GC`}
              </span>
            </div>

            <textarea
              rows={inputMode === "sequence" ? 6 : 4}
              value={value}
              onChange={(event) => setValue(event.target.value)}
              placeholder={
                inputMode === "mutation"
                  ? "gyrA S83L or rpoB S450L"
                  : "ATGCGATCGTCTTTAGCGTACGATCGATGCCGATCGATCGTACGATCGATC"
              }
              className={`glass-input min-h-[144px] ${
                inputMode === "sequence" ? "font-mono tracking-[0.18em]" : ""
              }`}
            />
          </div>

          <div className="grid gap-3 sm:grid-cols-3">
            <div className="metric-tile rounded-2xl px-4 py-3">
              <p className="text-[10px] uppercase tracking-[0.26em] text-slate-400">
                Visualization
              </p>
              <p className="mt-2 text-sm font-medium text-white">
                Helix highlight on active locus
              </p>
            </div>
            <div className="metric-tile rounded-2xl px-4 py-3">
              <p className="text-[10px] uppercase tracking-[0.26em] text-slate-400">
                ML Core
              </p>
              <p className="mt-2 text-sm font-medium text-white">
                3-mer vectorization + logistic regression
              </p>
            </div>
            <div className="metric-tile rounded-2xl px-4 py-3">
              <p className="text-[10px] uppercase tracking-[0.26em] text-slate-400">
                Reasoning
              </p>
              <p className="mt-2 text-sm font-medium text-white">
                Evo 2-ready explanation layer
              </p>
            </div>
          </div>

          <div className="rounded-[28px] border border-white/10 bg-black/20 p-4">
            <div className="flex items-center justify-between gap-3">
              <p className="text-[10px] uppercase tracking-[0.3em] text-slate-400">
                Quick-start samples
              </p>
              <span className="text-xs text-slate-500">Tap to populate the console</span>
            </div>

            <div className="mt-4 grid gap-2">
              {activeExamples.map((example) => (
                <button
                  key={example.label}
                  type="button"
                  onClick={() => loadExample(example.value)}
                  className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-left transition hover:-translate-y-0.5 hover:border-cyan-400/40 hover:bg-cyan-400/8"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-medium text-white">{example.label}</p>
                      <p className="mt-1 text-xs leading-5 text-slate-400">{example.note}</p>
                    </div>
                    <span className="glow-pill whitespace-nowrap text-[10px] uppercase tracking-[0.24em]">
                      sample
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={!value.trim() || isLoading}
            className="w-full rounded-[26px] bg-gradient-to-r from-cyan-300 via-sky-400 to-fuchsia-400 px-5 py-4 text-sm font-semibold text-slate-950 shadow-[0_18px_45px_rgba(56,189,248,0.28)] transition hover:translate-y-[-1px] hover:brightness-110 disabled:translate-y-0 disabled:cursor-not-allowed disabled:opacity-55"
          >
            {isLoading ? "Running prediction pipeline..." : "Launch Resistance Prediction"}
          </button>
        </form>
      </div>
    </section>
  );
}
