function ResultPage({ uploadData, prediction, onReset }) {
  if (!uploadData?.upload_id) {
    return (
      <section className="soft-panel rounded-[30px] p-8">
        <h2 className="title-font text-3xl font-semibold text-ink">No run yet</h2>
        <p className="mt-3 text-sm text-ink/68">Upload a FASTA file and run docking first.</p>
      </section>
    );
  }

  if (!prediction) {
    return (
      <section className="soft-panel rounded-[30px] p-8">
        <h2 className="title-font text-3xl font-semibold text-ink">Prediction pending</h2>
        <p className="mt-3 text-sm text-ink/68">Go to Dock and run the prediction.</p>
      </section>
    );
  }

  const probabilities = Object.entries(prediction.probability_breakdown).sort((a, b) => b[1] - a[1]);

  return (
    <section className="space-y-6">
      <div className="rounded-[32px] bg-gradient-to-br from-ink via-lagoon to-moss p-7 text-white shadow-glow sm:p-9">
        <p className="text-xs font-semibold uppercase tracking-[0.28em] text-white/70">Result</p>
        <h2 className="title-font mt-3 text-4xl font-semibold">{prediction.prediction}</h2>
        <div className="mt-5 flex flex-wrap gap-3 text-sm">
          <Badge value={`Gene: ${prediction.gene}`} />
          <Badge value={`Binding: ${prediction.binding_score}`} />
          <Badge value={`Confidence: ${(prediction.confidence * 100).toFixed(1)}%`} />
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_1fr]">
        <div className="soft-panel rounded-[30px] p-7">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-ink/50">Docking</p>
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <Stat label="Structure" value={prediction.structure_source} />
            <Stat label="Ligand" value={prediction.ligand_source} />
            <Stat label="Docking" value={prediction.docking_source} />
            <Stat label="Dock conf" value={(prediction.docking_confidence * 100).toFixed(1) + "%"} />
          </div>
          <div className="mt-4 rounded-[22px] bg-white/80 px-4 py-4">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-ink/45">Pose</p>
            <p className="mt-2 break-all font-mono text-sm text-ink">{prediction.binding_pose_preview}</p>
          </div>
        </div>

        <div className="soft-panel rounded-[30px] p-7">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-ink/50">Biology</p>
          <div className="mt-4 rounded-[22px] bg-white/80 px-4 py-4">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-ink/45">Mutations</p>
            <p className="mt-2 text-sm leading-6 text-ink">
              {prediction.mutations.length ? prediction.mutations.join(", ") : "No mutation"}
            </p>
          </div>
          <div className="mt-4 rounded-[22px] bg-white/80 px-4 py-4">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-ink/45">Protein preview</p>
            <div className="mt-2 space-y-2">
              {Object.entries(prediction.translated_protein_preview).map(([gene, preview]) => (
                <p key={gene} className="text-sm text-ink">
                  <span className="font-semibold">{gene}:</span>{" "}
                  <span className="font-mono text-xs">{preview}</span>
                </p>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="soft-panel rounded-[30px] p-7">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-ink/50">Class probabilities</p>
            <div className="mt-4 space-y-3">
              {probabilities.map(([label, value]) => (
                <div key={label}>
                  <div className="mb-1 flex items-center justify-between text-sm text-ink">
                    <span>{label}</span>
                    <span>{(value * 100).toFixed(1)}%</span>
                  </div>
                  <div className="h-2 rounded-full bg-ink/8">
                    <div
                      className="h-2 rounded-full bg-gradient-to-r from-ember via-lagoon to-moss"
                      style={{ width: `${Math.max(4, value * 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <button
            type="button"
            onClick={onReset}
            className="rounded-full bg-ink px-5 py-3 text-sm font-semibold text-white"
          >
            New run
          </button>
        </div>
      </div>
    </section>
  );
}

function Stat({ label, value }) {
  return (
    <div className="rounded-[22px] bg-white/80 px-4 py-4">
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-ink/45">{label}</p>
      <p className="mt-2 text-sm font-semibold text-ink">{value}</p>
    </div>
  );
}

function Badge({ value }) {
  return <span className="rounded-full bg-white/15 px-4 py-2">{value}</span>;
}

export default ResultPage;
