"use client";

import { useEffect, useMemo, useState } from "react";
import InputBox from "../../components/InputBox";
import OutputBox from "../../components/OutputBox";

const HISTORY_STORAGE_KEY = "biogpt-evo2-history-v1";
const DEFAULT_SETTINGS = {
  numTokens: 120,
  temperature: 0.7,
  topK: 4,
  topP: 0,
  randomSeed: ""
};

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

function buildHistoryItem(sourceInput, settings, result) {
  return {
    id: globalThis.crypto?.randomUUID?.() || `${Date.now()}`,
    sourceInput,
    settings,
    createdAt: new Date().toISOString(),
    ...result
  };
}

function formatTimestamp(value) {
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

export default function DNAGeneratorPage() {
  const [inputMode, setInputMode] = useState("dna");
  const [inputValue, setInputValue] = useState("");
  const [settings, setSettings] = useState(DEFAULT_SETTINGS);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    try {
      const rawHistory = localStorage.getItem(HISTORY_STORAGE_KEY);
      if (rawHistory) {
        const parsed = JSON.parse(rawHistory);
        if (Array.isArray(parsed)) {
          setHistory(parsed);
        }
      }
    } catch (storageError) {
      console.error("Unable to read history from localStorage.", storageError);
    }
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(history));
    } catch (storageError) {
      console.error("Unable to persist history to localStorage.", storageError);
    }
  }, [history]);

  const historyCountLabel = useMemo(
    () => `${history.length} saved run${history.length === 1 ? "" : "s"}`,
    [history.length]
  );

  const handleSettingChange = (key, value) => {
    setSettings((current) => ({
      ...current,
      [key]: value
    }));
  };

  const handleGenerate = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          input: inputValue,
          input_type: inputMode,
          num_tokens: Number(settings.numTokens),
          temperature: Number(settings.temperature),
          top_k: Number(settings.topK),
          top_p: Number(settings.topP),
          random_seed: settings.randomSeed === "" ? null : Number(settings.randomSeed)
        })
      });

      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.detail || "Unable to generate a DNA sequence right now.");
      }

      setResult(payload);
      setHistory((current) => {
        const nextHistory = [buildHistoryItem(inputValue, settings, payload), ...current];
        return nextHistory.slice(0, 8);
      });
    } catch (requestError) {
      setError(requestError.message || "Something went wrong while contacting the backend.");
    } finally {
      setLoading(false);
    }
  };

  const handleHistorySelect = (item) => {
    setInputMode(item.input_type);
    setInputValue(item.sourceInput);
    setSettings(item.settings || DEFAULT_SETTINGS);
    setResult(item);
    setError("");
  };

  const handleClearHistory = () => {
    setHistory([]);
  };

  return (
    <main className="min-h-screen bg-hero px-3 py-6 text-ink sm:px-6 md:py-8 lg:px-10">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 md:gap-8">
        <section className="overflow-hidden rounded-2xl border border-white/10 bg-white/5 p-4 shadow-glow backdrop-blur-xl sm:rounded-[28px] sm:p-6 lg:p-8">
          <div className="flex flex-col gap-4 sm:gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-3xl">
              <p className="mb-2 inline-flex items-center rounded-full border border-cyan-300/20 bg-cyan-300/10 px-2 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200 sm:mb-3 sm:px-3">
                BioGPT • DNA AI Web Application
              </p>
              <h1 className="text-3xl font-semibold leading-tight text-white sm:text-4xl md:text-5xl">
                Generate DNA sequences with NVIDIA Evo2 from raw DNA or natural language ideas.
              </h1>
              <p className="mt-3 max-w-2xl text-xs leading-6 text-slate-200 sm:mt-4 sm:text-sm md:text-base md:leading-7">
                Paste DNA, describe your intent, tune generation parameters, and keep a local history of every run. The
                backend adapts text prompts into Evo2-compatible DNA seeds before calling NVIDIA&apos;s generation API.
              </p>
            </div>
            <div className="grid gap-2 rounded-2xl border border-white/10 bg-slate-950/30 p-3 text-xs text-slate-200 sm:gap-3 sm:rounded-3xl sm:p-4 sm:text-sm grid-cols-3">
              <div>
                <p className="uppercase tracking-[0.2em] text-slate-400 text-xs sm:text-xs">Model</p>
                <p className="mt-1 font-medium text-white text-sm sm:text-base">Evo2 40B</p>
              </div>
              <div>
                <p className="uppercase tracking-[0.2em] text-slate-400 text-xs sm:text-xs">Modes</p>
                <p className="mt-1 font-medium text-white text-sm sm:text-base">DNA + Prompt</p>
              </div>
              <div>
                <p className="uppercase tracking-[0.2em] text-slate-400 text-xs sm:text-xs">History</p>
                <p className="mt-1 font-medium text-white text-sm sm:text-base">{historyCountLabel}</p>
              </div>
            </div>
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-2 xl:grid-cols-[1.05fr_0.95fr]">
          <InputBox
            error={error}
            inputMode={inputMode}
            inputValue={inputValue}
            loading={loading}
            onGenerate={handleGenerate}
            onInputChange={setInputValue}
            onModeChange={setInputMode}
            onSettingChange={handleSettingChange}
            settings={settings}
          />

          <OutputBox loading={loading} result={result} />
        </section>

        <section className="rounded-2xl border border-white/10 bg-panel p-4 shadow-glow backdrop-blur-xl sm:rounded-[28px] sm:p-6">
          <div className="mb-4 flex flex-col gap-3 sm:mb-5 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-xl font-semibold text-white sm:text-2xl">Local History</h2>
              <p className="mt-1 text-xs text-slate-300 sm:text-sm">
                Your latest eight generations stay in the browser for quick recall.
              </p>
            </div>
            <button
              className="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-xs font-medium text-slate-200 transition hover:bg-white/10 sm:px-4 sm:py-2 sm:text-sm"
              onClick={handleClearHistory}
              type="button"
            >
              Clear history
            </button>
          </div>

          {history.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-white/10 bg-slate-950/20 p-4 text-xs text-slate-400 sm:rounded-3xl sm:p-6 sm:text-sm">
              No generations saved yet. Your next successful run will show up here automatically.
            </div>
          ) : (
            <div className="grid gap-3 sm:gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {history.map((item) => (
                <button
                  key={item.id}
                  className="group rounded-2xl border border-white/10 bg-slate-950/30 p-3 text-left transition hover:-translate-y-1 hover:border-cyan-300/40 hover:bg-slate-950/50 sm:rounded-3xl sm:p-4"
                  onClick={() => handleHistorySelect(item)}
                  type="button"
                >
                  <div className="mb-3 flex items-center justify-between gap-2 sm:gap-3">
                    <span className="rounded-full bg-cyan-300/10 px-2 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-cyan-200 sm:px-3">
                      {item.input_type}
                    </span>
                    <span className="text-right text-xs text-slate-400 line-clamp-1">{formatTimestamp(item.createdAt)}</span>
                  </div>
                  <p className="line-clamp-3 text-xs text-slate-200 leading-5 sm:text-sm sm:leading-6">{item.sourceInput}</p>
                  <div className="mt-3 rounded-2xl bg-black/20 p-2 sm:mt-4 sm:p-3">
                    <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Generated DNA</p>
                    <p className="mt-1 line-clamp-2 break-all font-mono text-xs text-white sm:mt-2 sm:line-clamp-3">{item.generated_sequence}</p>
                  </div>
                  <p className="mt-2 text-xs text-cyan-200 opacity-80 transition group-hover:opacity-100 sm:mt-3">Click to load</p>
                </button>
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
