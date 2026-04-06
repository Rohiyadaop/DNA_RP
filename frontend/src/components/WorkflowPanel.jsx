const pipelineSteps = [
  "1. BioPython reads the uploaded FASTA file and validates the DNA sequence.",
  "2. The backend performs CARD-style gene mapping and mutation detection against a reference genome.",
  "3. Mapped gene regions are translated into protein sequences and summarized into structure-approximation features.",
  "4. RDKit converts the antibiotic SMILES into a molecular fingerprint.",
  "5. A docking-style interaction score is simulated from protein, mutation, drug, and environment context.",
  "6. All feature blocks are fused and the neural network predicts the resistance level."
];

function WorkflowPanel() {
  return (
    <section className="glass-card rounded-[28px] border border-white/70 p-6 shadow-glow">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.32em] text-ink/55">
            System Workflow
          </p>
          <h2 className="mt-2 text-2xl font-bold text-ink">How The Full Stack Fits Together</h2>
        </div>
        <div className="rounded-full bg-ember/10 px-4 py-2 text-xs font-semibold text-ember">
          React + FastAPI + scikit-learn
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {pipelineSteps.map((step) => (
          <div key={step} className="rounded-[22px] border border-ink/8 bg-white/75 p-5">
            <p className="text-sm leading-6 text-ink/80">{step}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default WorkflowPanel;
