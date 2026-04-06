import { Link } from "react-router-dom";

function HomePage({ hasUpload }) {
  return (
    <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
      <div className="soft-panel rounded-[30px] p-7 sm:p-9">
        <p className="text-xs font-semibold uppercase tracking-[0.32em] text-lagoon/70">
          DNA + Structure + Docking
        </p>
        <h2 className="title-font mt-4 text-4xl font-semibold leading-tight text-ink sm:text-5xl">
          Clean, local AMR prediction with real API hooks.
        </h2>
        <p className="mt-4 max-w-xl text-base leading-7 text-ink/72">
          Upload FASTA, add a drug, run docking-aware prediction, and get a simple resistance result.
        </p>

        <div className="mt-7 flex flex-wrap gap-3">
          <Link
            to={hasUpload ? "/dock" : "/upload"}
            className="rounded-full bg-ink px-5 py-3 text-sm font-semibold text-white"
          >
            {hasUpload ? "Continue" : "Start"}
          </Link>
          <Link to="/learn" className="rounded-full bg-white px-5 py-3 text-sm font-semibold text-ink">
            Learn
          </Link>
        </div>
      </div>

      <div className="grid gap-4">
        <MiniCard title="1. Upload" text="FASTA in, DNA checked, protein target selected." />
        <MiniCard title="2. Dock" text="SMILES + structure + docking + CARD context." />
        <MiniCard title="3. Result" text="Resistance level, score, confidence, gene." />
      </div>
    </section>
  );
}

function MiniCard({ title, text }) {
  return (
    <div className="soft-panel rounded-[24px] p-6">
      <p className="text-sm font-semibold text-ink">{title}</p>
      <p className="mt-2 text-sm leading-6 text-ink/68">{text}</p>
    </div>
  );
}

export default HomePage;
