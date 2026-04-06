function LearnPage() {
  return (
    <section className="grid gap-6 lg:grid-cols-3">
      <Card
        title="Structure prediction"
        text="Protein sequence is sent to an ESMFold-compatible endpoint when configured. If not, the app creates a local mock PDB so the workflow still runs."
      />
      <Card
        title="Docking"
        text="The app tries a DiffDock-compatible API for protein-ligand docking. If that fails, a local docking heuristic returns binding score and confidence."
      />
      <Card
        title="Prediction"
        text="DNA, mutations, protein features, drug fingerprint, docking score, and environment are fused into a lightweight neural network."
      />
    </section>
  );
}

function Card({ title, text }) {
  return (
    <div className="soft-panel rounded-[30px] p-7">
      <h2 className="title-font text-2xl font-semibold text-ink">{title}</h2>
      <p className="mt-3 text-sm leading-7 text-ink/68">{text}</p>
    </div>
  );
}

export default LearnPage;
