import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen bg-hero px-3 py-6 text-ink sm:px-6 md:py-8 lg:px-10">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-8 md:gap-12">
        {/* Hero Section */}
        <section className="pt-8 md:pt-12">
          <div className="overflow-hidden rounded-2xl border border-white/10 bg-white/5 p-4 shadow-glow backdrop-blur-xl sm:rounded-[28px] sm:p-6 lg:p-8">
            <div className="flex flex-col gap-4 sm:gap-6">
              <div>
                <p className="mb-2 inline-flex items-center rounded-full border border-cyan-300/20 bg-cyan-300/10 px-2 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200 sm:mb-3 sm:px-3">
                  🧬 BioGPT Evo2 Platform
                </p>
                <h1 className="text-3xl font-semibold leading-tight text-white sm:text-4xl md:text-5xl">
                  Advanced DNA & Genomics Intelligence
                </h1>
                <p className="mt-3 max-w-2xl text-xs leading-6 text-slate-200 sm:mt-4 sm:text-sm md:text-base md:leading-7">
                  A comprehensive platform for DNA sequence generation, mutation analysis, and
                  antibiotic resistance prediction powered by NVIDIA Evo2 and machine learning.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Applications Grid */}
        <section className="grid gap-6 md:grid-cols-2">
          {/* DNA Generator */}
          <Link href="/dna-generator">
            <div className="group rounded-2xl border border-white/10 bg-slate-950/40 p-4 cursor-pointer transition hover:border-cyan-400/30 hover:bg-slate-950/60 hover:shadow-lg hover:shadow-cyan-400/20 sm:rounded-3xl sm:p-6">
              <div className="mb-4">
                <div className="inline-flex rounded-xl bg-cyan-400/10 p-3 text-2xl">
                  🧬
                </div>
              </div>
              <h2 className="text-xl font-bold text-white mb-2 sm:text-2xl group-hover:text-cyan-300 transition">
                DNA Sequence Generator
              </h2>
              <p className="text-xs text-slate-300 mb-4 leading-relaxed sm:text-sm md:text-base">
                Generate realistic DNA sequences using NVIDIA Evo2 foundation model. Input raw DNA
                sequences or natural language prompts to get biologically valid outputs.
              </p>
              <div className="space-y-2 mb-4">
                <div className="flex items-start gap-2 text-xs text-slate-400">
                  <span className="text-cyan-400 mt-1">✓</span>
                  <span>Direct DNA sequence input or FASTA format</span>
                </div>
                <div className="flex items-start gap-2 text-xs text-slate-400">
                  <span className="text-cyan-400 mt-1">✓</span>
                  <span>Natural language prompts converted to DNA</span>
                </div>
                <div className="flex items-start gap-2 text-xs text-slate-400">
                  <span className="text-cyan-400 mt-1">✓</span>
                  <span>Tunable parameters (temperature, top-k, etc.)</span>
                </div>
                <div className="flex items-start gap-2 text-xs text-slate-400">
                  <span className="text-cyan-400 mt-1">✓</span>
                  <span>Local history for 8 recent generations</span>
                </div>
              </div>
              <div className="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-cyan-400/10 text-cyan-200 text-xs font-semibold group-hover:bg-cyan-400/20 transition">
                Launch Generator <span className="text-lg">→</span>
              </div>
            </div>
          </Link>

          {/* Resistance Predictor */}
          <Link href="/dna-predictor">
            <div className="group rounded-2xl border border-white/10 bg-slate-950/40 p-4 cursor-pointer transition hover:border-emerald-400/30 hover:bg-slate-950/60 hover:shadow-lg hover:shadow-emerald-400/20 sm:rounded-3xl sm:p-6">
              <div className="mb-4">
                <div className="inline-flex rounded-xl bg-emerald-400/10 p-3 text-2xl">
                  🛡️
                </div>
              </div>
              <h2 className="text-xl font-bold text-white mb-2 sm:text-2xl group-hover:text-emerald-300 transition">
                Mutation Resistance Predictor
              </h2>
              <p className="text-xs text-slate-300 mb-4 leading-relaxed sm:text-sm md:text-base">
                Predict antibiotic resistance from gene mutations using AI-powered analysis.
                Features 3D DNA visualization and scientific explanations.
              </p>
              <div className="space-y-2 mb-4">
                <div className="flex items-start gap-2 text-xs text-slate-400">
                  <span className="text-emerald-400 mt-1">✓</span>
                  <span>3D interactive DNA helix with mutation highlighting</span>
                </div>
                <div className="flex items-start gap-2 text-xs text-slate-400">
                  <span className="text-emerald-400 mt-1">✓</span>
                  <span>ML-based resistance prediction with confidence scores</span>
                </div>
                <div className="flex items-start gap-2 text-xs text-slate-400">
                  <span className="text-emerald-400 mt-1">✓</span>
                  <span>Animated data processing pipeline visualization</span>
                </div>
                <div className="flex items-start gap-2 text-xs text-slate-400">
                  <span className="text-emerald-400 mt-1">✓</span>
                  <span>AI-generated scientific explanations</span>
                </div>
              </div>
              <div className="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-emerald-400/10 text-emerald-200 text-xs font-semibold group-hover:bg-emerald-400/20 transition">
                Launch Predictor <span className="text-lg">→</span>
              </div>
            </div>
          </Link>
        </section>

        {/* Features Section */}
        <section className="rounded-2xl border border-white/10 bg-slate-950/40 p-4 shadow-glow backdrop-blur-xl sm:rounded-3xl sm:p-6">
          <h2 className="text-xl font-bold text-white mb-4 sm:text-2xl">
            Platform Capabilities
          </h2>
          <div className="grid gap-4 md:gap-6 md:grid-cols-3">
            <div className="rounded-xl border border-cyan-400/20 bg-cyan-400/5 p-4">
              <p className="text-sm font-bold text-cyan-200 mb-2">🤖 AI Intelligence</p>
              <p className="text-xs text-slate-300 leading-relaxed">
                Powered by NVIDIA Evo2 foundation model for accurate DNA generation and
                scikit-learn ML for resistance prediction.
              </p>
            </div>
            <div className="rounded-xl border border-purple-400/20 bg-purple-400/5 p-4">
              <p className="text-sm font-bold text-purple-200 mb-2">✨ Visual Rendering</p>
              <p className="text-xs text-slate-300 leading-relaxed">
                Three.js 3D visualization with animated data pipelines and real-time processing
                feedback for intuitive user experience.
              </p>
            </div>
            <div className="rounded-xl border border-emerald-400/20 bg-emerald-400/5 p-4">
              <p className="text-sm font-bold text-emerald-200 mb-2">📱 Responsive Design</p>
              <p className="text-xs text-slate-300 leading-relaxed">
                Mobile-first approach with Tailwind CSS ensures optimal experience on all
                device sizes and screen resolutions.
              </p>
            </div>
          </div>
        </section>

        {/* Tech Stack */}
        <section className="rounded-2xl border border-white/10 bg-slate-950/40 p-4 shadow-glow backdrop-blur-xl sm:rounded-3xl sm:p-6">
          <h2 className="text-xl font-bold text-white mb-4 sm:text-2xl">
            Technology Stack
          </h2>
          <div className="grid gap-3 sm:gap-4 grid-cols-2 md:grid-cols-4">
            <div className="rounded-lg border border-white/10 bg-white/5 p-3 text-center">
              <p className="text-xs font-semibold text-slate-300">Frontend</p>
              <p className="text-xs text-slate-400 mt-1">Next.js 14 • React 18</p>
            </div>
            <div className="rounded-lg border border-white/10 bg-white/5 p-3 text-center">
              <p className="text-xs font-semibold text-slate-300">3D Graphics</p>
              <p className="text-xs text-slate-400 mt-1">Three.js</p>
            </div>
            <div className="rounded-lg border border-white/10 bg-white/5 p-3 text-center">
              <p className="text-xs font-semibold text-slate-300">Backend</p>
              <p className="text-xs text-slate-400 mt-1">FastAPI • Python</p>
            </div>
            <div className="rounded-lg border border-white/10 bg-white/5 p-3 text-center">
              <p className="text-xs font-semibold text-slate-300">ML/AI</p>
              <p className="text-xs text-slate-400 mt-1">scikit-learn • Evo2</p>
            </div>
          </div>
        </section>

        {/* Footer Info */}
        <section className="text-center py-8 border-t border-white/10">
          <p className="text-xs text-slate-400">
            Built for GSOC Hackathon • Powered by NVIDIA Evo2 • Made with ❤️
          </p>
        </section>
      </div>
    </main>
  );
}

