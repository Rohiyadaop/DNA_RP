"use client";

import { useMemo, useState } from "react";
import dynamic from "next/dynamic";

import DataFlowPipeline from "@/components/dna-predictor/DataFlowPipeline";
import ExplanationPanel from "@/components/dna-predictor/ExplanationPanel";
import MutationInput from "@/components/dna-predictor/MutationInput";
import PredictionCard from "@/components/dna-predictor/PredictionCard";

const DNAHelix3D = dynamic(() => import("@/components/dna-predictor/DNAHelix3D"), {
  ssr: false,
  loading: () => (
    <div className="neon-panel rounded-[34px] p-4 sm:p-5">
      <div className="h-[520px] animate-pulse rounded-[28px] border border-white/10 bg-white/[0.04]" />
    </div>
  ),
});

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000").replace(
  /\/$/,
  ""
);

const PIPELINE_TEMPLATE = [
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
    detail: "3-mer and residue signatures will be generated.",
    metric: "Sparse vectors",
    status: "idle",
  },
  {
    key: "ml",
    code: "ML",
    label: "ML Model",
    detail: "Logistic regression will assign phenotype probability.",
    metric: "Ready",
    status: "idle",
  },
  {
    key: "reasoning",
    code: "AI",
    label: "LLM Reasoning",
    detail: "Biological rationale will be synthesized next.",
    metric: "Evo 2-ready",
    status: "idle",
  },
  {
    key: "output",
    code: "OUT",
    label: "Final Output",
    detail: "Confidence, explanation, and helix highlights will be rendered.",
    metric: "Pending",
    status: "idle",
  },
];

const DEFAULT_LOGS = [
  "01 DNA Input :: Waiting for a mutation or sequence sample.",
  "02 Encoding :: 3-mer and residue vectorization idle.",
  "03 ML Model :: Logistic regression warmed and ready.",
];

const HERO_METRICS = [
  {
    label: "Classifier",
    value: "Logistic Regression",
    caption: "Lightweight and fast for demo-ready feedback",
  },
  {
    label: "Encoding",
    value: "3-mer + Residue Signals",
    caption: "Mutation tokens and DNA fragments become vector features",
  },
  {
    label: "Visualization",
    value: "Interactive 3D DNA",
    caption: "Neon helix with live mutation highlighting",
  },
  {
    label: "Reasoning",
    value: "Evo 2-ready Layer",
    caption: "Grounded scientific explanation with graceful fallback",
  },
];

function delay(duration) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, duration);
  });
}

function createPipelineState(input, inputType) {
  const cleanedLength = inputType === "sequence" ? input.replace(/[^ATGC]/gi, "").length : null;

  return PIPELINE_TEMPLATE.map((step) => {
    if (step.key === "input") {
      return {
        ...step,
        detail:
          inputType === "sequence"
            ? "Sequence payload received and preparing base normalization."
            : "Mutation payload received and preparing gene/residue parsing.",
        metric:
          inputType === "sequence"
            ? `${cleanedLength || 0} bases`
            : input.trim().toUpperCase(),
      };
    }

    return { ...step };
  });
}

async function safeReadJson(response) {
  try {
    return await response.json();
  } catch (error) {
    return null;
  }
}

export default function DNAPredictorPage() {
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [pipelineSteps, setPipelineSteps] = useState(PIPELINE_TEMPLATE);
  const [consoleLines, setConsoleLines] = useState(DEFAULT_LOGS);
  const [lastRequest, setLastRequest] = useState({
    input: "gyrA S83L",
    inputType: "mutation",
  });

  const updateStep = (key, updates) => {
    setPipelineSteps((current) =>
      current.map((step) => (step.key === key ? { ...step, ...updates } : step))
    );
  };

  const visualState = useMemo(() => {
    if (!result) {
      return {
        highlightPositions: [7, 21, 35],
        predictionTone: "neutral",
        focusLabel:
          lastRequest.inputType === "sequence"
            ? "Sequence anomaly scan"
            : "Awaiting mutation lock",
        confidence: 0.54,
      };
    }

    return {
      highlightPositions: result.visualization.highlight_positions,
      predictionTone: result.visualization.prediction_tone,
      focusLabel: result.visualization.focus_label,
      confidence: result.confidence,
    };
  }, [lastRequest.inputType, result]);

  const handlePredict = async ({ input, inputType }) => {
    setIsLoading(true);
    setResult(null);
    setError("");
    setLastRequest({ input, inputType });
    setPipelineSteps(createPipelineState(input, inputType));
    setConsoleLines([
      `01 DNA Input :: Accepted ${inputType} payload.`,
      "02 Encoding :: Preparing 3-mer / residue-signature vectorization.",
      "03 ML Model :: Launching resistance scoring.",
      "04 LLM Reasoning :: Waiting for structured biological context.",
    ]);

    try {
      updateStep("input", {
        status: "processing",
        detail:
          inputType === "sequence"
            ? "Cleaning bases and checking for usable sequence content."
            : "Parsing gene and amino-acid change notation.",
      });
      await delay(260);

      updateStep("input", {
        status: "completed",
      });

      updateStep("encoding", {
        status: "processing",
        detail: "Tokenizing the signal into 3-mers and residue-aware sparse features.",
        metric: inputType === "sequence" ? "3-mer scan" : "Residue tokens",
      });
      await delay(340);

      const response = await fetch(`${API_BASE_URL}/api/dna-predictor/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          input,
          input_type: inputType,
        }),
      });

      const payload = await safeReadJson(response);
      if (!response.ok) {
        throw new Error(payload?.detail || "Prediction failed. Please try another input.");
      }

      updateStep("encoding", {
        status: "completed",
        detail: payload.pipeline?.[1]?.detail || "Encoding completed.",
        metric: payload.encoding?.top_kmers?.slice(0, 2).join(" / ") || "Encoded",
      });

      updateStep("ml", {
        status: "processing",
        detail: "Scoring resistant phenotype using the encoded molecular features.",
        metric: "Inferencing",
      });
      await delay(240);
      updateStep("ml", {
        status: "completed",
        detail: payload.pipeline?.[2]?.detail || "Model scoring complete.",
        metric: `${Math.round(payload.probability_resistant * 100)}% resistant`,
      });

      updateStep("reasoning", {
        status: "processing",
        detail: "Fusing model confidence with curated biological mechanism hints.",
        metric: "Synthesizing",
      });
      await delay(420);
      updateStep("reasoning", {
        status: "completed",
        detail: payload.pipeline?.[3]?.detail || "Reasoning prepared.",
        metric: payload.reasoning_source,
      });

      updateStep("output", {
        status: "processing",
        detail: "Rendering response cards, explanation, and 3D helix highlights.",
        metric: "Streaming",
      });
      setResult(payload);
      setConsoleLines(
        (payload.pipeline || []).map(
          (step, index) =>
            `${String(index + 1).padStart(2, "0")} ${step.name} :: ${step.detail}`
        )
      );
      await delay(180);

      updateStep("output", {
        status: "completed",
        detail: payload.pipeline?.[4]?.detail || "Final output rendered.",
        metric: `${Math.round(payload.confidence * 100)}% confidence`,
      });
    } catch (requestError) {
      const message = requestError.message || "Prediction pipeline failed.";
      setError(message);
      setConsoleLines((current) => [
        ...current.slice(-3),
        `!! Pipeline Halted :: ${message}`,
      ]);
      setPipelineSteps((current) =>
        current.map((step) =>
          step.status === "processing"
            ? { ...step, status: "error", detail: message, metric: "Stopped" }
            : step
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="dna-lab-bg min-h-screen px-4 py-8 text-ink sm:px-6 lg:px-10">
      <div className="relative z-10 mx-auto flex w-full max-w-[1480px] flex-col gap-6 lg:gap-8">
        <section className="neon-panel scan-panel overflow-hidden rounded-[36px] p-6 sm:p-8">
          <div className="grid gap-8 xl:grid-cols-[1.18fr_0.82fr]">
            <div>
              <p className="status-chip w-fit border-cyan-400/30 bg-cyan-400/10 text-cyan-100">
                DNA Mutation Resistance Predictor
              </p>
              <h1 className="mt-5 max-w-4xl text-4xl font-semibold leading-tight text-white sm:text-5xl xl:text-6xl">
                Futuristic antibiotic resistance intelligence for mutated DNA
                signals
              </h1>
              <p className="mt-5 max-w-3xl text-sm leading-7 text-slate-300 sm:text-base">
                A cinematic hackathon-ready prototype that accepts a mutation or a
                mutated DNA fragment, vectorizes the signal, predicts bacterial
                resistance, and explains the result with grounded biological
                reasoning.
              </p>

              <div className="mt-6 flex flex-wrap gap-2">
                <span className="glow-pill border-cyan-400/20 bg-cyan-400/10 text-cyan-100">
                  Input / Processing / Prediction / Explanation
                </span>
                <span className="glow-pill border-fuchsia-400/20 bg-fuchsia-400/10 text-fuchsia-100">
                  ML + LLM reasoning
                </span>
                <span className="glow-pill border-emerald-400/20 bg-emerald-400/10 text-emerald-100">
                  Live 3D DNA highlight
                </span>
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              {HERO_METRICS.map((item) => (
                <div key={item.label} className="metric-tile rounded-[26px] px-5 py-4">
                  <p className="text-[10px] uppercase tracking-[0.3em] text-slate-400">
                    {item.label}
                  </p>
                  <p className="mt-3 text-lg font-medium text-white">{item.value}</p>
                  <p className="mt-2 text-sm leading-6 text-slate-400">{item.caption}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="grid gap-6 xl:grid-cols-[0.95fr_1.24fr_0.91fr]">
          <MutationInput onPredict={handlePredict} isLoading={isLoading} />

          <DNAHelix3D
            highlightPositions={visualState.highlightPositions}
            predictionTone={visualState.predictionTone}
            focusLabel={visualState.focusLabel}
            confidence={visualState.confidence}
          />

          <PredictionCard result={result} isLoading={isLoading} error={error} />
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.08fr_0.92fr]">
          <DataFlowPipeline
            steps={pipelineSteps}
            isProcessing={isLoading}
            consoleLines={consoleLines}
          />
          <ExplanationPanel result={result} error={error} lastRequest={lastRequest} />
        </section>

        <section className="grid gap-4 lg:grid-cols-3">
          <div className="metric-tile rounded-[28px] px-5 py-5">
            <p className="text-[10px] uppercase tracking-[0.3em] text-slate-400">
              Scientific Storytelling
            </p>
            <p className="mt-3 text-lg font-medium text-white">
              Confidence is paired with mechanism-level reasoning
            </p>
            <p className="mt-2 text-sm leading-6 text-slate-400">
              Each response surfaces k-mer evidence, resistance probability, and
              a clear narrative about why binding, activation, or protein
              function may change.
            </p>
          </div>

          <div className="metric-tile rounded-[28px] px-5 py-5">
            <p className="text-[10px] uppercase tracking-[0.3em] text-slate-400">
              Lightweight Prototype
            </p>
            <p className="mt-3 text-lg font-medium text-white">
              FastAPI backend + React front-end + Three.js helix
            </p>
            <p className="mt-2 text-sm leading-6 text-slate-400">
              The stack stays compact and hackathon-friendly while still showing
              a complete product loop from molecular input to interpretable
              output.
            </p>
          </div>

          <div className="metric-tile rounded-[28px] px-5 py-5">
            <p className="text-[10px] uppercase tracking-[0.3em] text-slate-400">
              Visual Focus
            </p>
            <p className="mt-3 text-lg font-medium text-white">
              Dynamic locus highlighting inside the 3D DNA structure
            </p>
            <p className="mt-2 text-sm leading-6 text-slate-400">
              The helix keeps rotating in the center of the interface and locks
              onto predicted mutation points or sequence anomalies as soon as a
              result is available.
            </p>
          </div>
        </section>
      </div>
    </main>
  );
}
