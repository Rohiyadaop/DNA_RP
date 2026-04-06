function PredictionResult({ prediction, isLoading }) {
  const probabilities = prediction
    ? Object.entries(prediction.probability_breakdown).sort((left, right) => right[1] - left[1])
    : [];

  return (
    <section className="glass-card rounded-[28px] border border-white/70 p-6 shadow-glow">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.32em] text-moss/80">Step 3</p>
          <h2 className="mt-2 text-2xl font-bold text-ink">Prediction Output</h2>
          <p className="mt-2 text-sm leading-6 text-ink/70">
            The backend fuses DNA, mutations, translated proteins, structure proxy,
            molecular fingerprint, docking score, and environment before the neural net
            predicts a resistance category.
          </p>
        </div>
      </div>

      <div className="mt-6 rounded-[28px] bg-gradient-to-br from-ink via-lagoon to-moss p-6 text-white">
        {prediction ? (
          <>
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-white/70">
              Predicted Category
            </p>
            <h3 className="mt-3 text-3xl font-bold">{prediction.prediction}</h3>
            <p className="mt-3 text-sm text-white/80">
              Confidence: {(prediction.confidence * 100).toFixed(2)}%
            </p>
            <p className="mt-4 text-sm leading-6 text-white/80">{prediction.message}</p>
          </>
        ) : (
          <>
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-white/65">
              Waiting For Input
            </p>
            <h3 className="mt-3 text-3xl font-bold">
              {isLoading ? "Running inference..." : "No prediction yet"}
            </h3>
            <p className="mt-4 text-sm text-white/80">
              Upload a FASTA file, enter drug/environment context, and trigger the model.
            </p>
          </>
        )}
      </div>

      {prediction ? (
        <div className="mt-6 space-y-5">
          <div className="grid gap-4 md:grid-cols-2">
            <MetricCard label="Docking Score" value={prediction.docking_score.toFixed(4)} />
            <MetricCard label="Sequence Length" value={`${prediction.sequence_length} bp`} />
          </div>

          <div className="rounded-[24px] border border-ink/8 bg-white/75 p-5">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-ink/50">
              Probability Breakdown
            </p>
            <div className="mt-4 space-y-3">
              {probabilities.map(([label, value]) => (
                <div key={label}>
                  <div className="mb-1 flex items-center justify-between text-sm text-ink">
                    <span>{label}</span>
                    <span>{(value * 100).toFixed(2)}%</span>
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

          <DetailList title="Mapped Genes" values={prediction.mapped_genes} emptyLabel="None detected" />
          <DetailList title="Mutations" values={prediction.mutations} emptyLabel="No mutation" />

          <div className="rounded-[24px] border border-ink/8 bg-white/75 p-5">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-ink/50">
              Protein Preview
            </p>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              {Object.entries(prediction.translated_protein_preview).map(([gene, preview]) => (
                <div key={gene} className="rounded-2xl border border-ink/8 bg-white p-4">
                  <p className="text-sm font-semibold text-ink">{gene}</p>
                  <p className="mt-2 break-all font-mono text-xs text-ink/75">{preview}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}

function MetricCard({ label, value }) {
  return (
    <div className="rounded-[22px] border border-ink/8 bg-white/75 p-5">
      <p className="text-xs font-semibold uppercase tracking-[0.24em] text-ink/50">{label}</p>
      <p className="mt-3 text-2xl font-bold text-ink">{value}</p>
    </div>
  );
}

function DetailList({ title, values, emptyLabel }) {
  return (
    <div className="rounded-[24px] border border-ink/8 bg-white/75 p-5">
      <p className="text-xs font-semibold uppercase tracking-[0.24em] text-ink/50">{title}</p>
      <div className="mt-4 flex flex-wrap gap-2">
        {values.length ? (
          values.map((value) => (
            <span
              key={value}
              className="rounded-full bg-ink/6 px-3 py-2 text-sm font-medium text-ink"
            >
              {value}
            </span>
          ))
        ) : (
          <span className="text-sm text-ink/60">{emptyLabel}</span>
        )}
      </div>
    </div>
  );
}

export default PredictionResult;
