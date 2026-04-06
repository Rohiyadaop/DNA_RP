const samples = [
  {
    label: "Ciprofloxacin",
    smiles: "C1CC1N2C=C(C(=O)C3=CC(=C(C=C32)N4CCNCC4)F)C(=O)O"
  },
  {
    label: "Ampicillin",
    smiles: "CC1([C@@H](N2[C@H](S1)[C@@H](C2=O)NC(=O)[C@@H](C3=CC=CC=C3)N)C(=O)O)C"
  },
  {
    label: "Tetracycline",
    smiles: "CC1(C2CC3C(C(=O)C(=C(C3(C(=O)C2=C(C4=C1C=CC=C4O)O)O)O)C(=O)N)N(C)C)O"
  }
];

function DockPage({ formState, setFormState, uploadData, prediction, predictError, isPredicting, onPredict }) {
  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormState((current) => ({ ...current, [name]: value }));
  };

  if (!uploadData?.upload_id) {
    return (
      <section className="soft-panel rounded-[30px] p-8">
        <h2 className="title-font text-3xl font-semibold text-ink">Upload FASTA first</h2>
        <p className="mt-3 text-sm text-ink/68">This step needs a sequence before docking can run.</p>
      </section>
    );
  }

  return (
    <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
      <div className="soft-panel rounded-[30px] p-7 sm:p-8">
        <p className="text-xs font-semibold uppercase tracking-[0.28em] text-ember/80">Step 2</p>
        <h2 className="title-font mt-3 text-3xl font-semibold text-ink">Drug + docking</h2>

        <div className="mt-5 flex flex-wrap gap-2">
          {samples.map((sample) => (
            <button
              key={sample.label}
              type="button"
              onClick={() => setFormState((current) => ({ ...current, smiles: sample.smiles }))}
              className="rounded-full bg-white px-4 py-2 text-sm font-medium text-ink"
            >
              {sample.label}
            </button>
          ))}
        </div>

        <div className="mt-6 space-y-5">
          <label className="block">
            <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.24em] text-ink/50">
              SMILES
            </span>
            <textarea
              name="smiles"
              rows="4"
              value={formState.smiles}
              onChange={handleChange}
              className="w-full rounded-[22px] border border-ink/10 bg-white px-4 py-3 text-sm text-ink outline-none focus:border-lagoon"
            />
          </label>

          <div className="grid gap-4 md:grid-cols-3">
            <Input label="Temp" name="temperature" value={formState.temperature} onChange={handleChange} />
            <Input label="pH" name="ph" value={formState.ph} onChange={handleChange} />
            <label className="block">
              <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.24em] text-ink/50">
                Medium
              </span>
              <select
                name="medium"
                value={formState.medium}
                onChange={handleChange}
                className="w-full rounded-[22px] border border-ink/10 bg-white px-4 py-3 text-sm text-ink outline-none focus:border-lagoon"
              >
                {["LB", "MHB", "Minimal", "Blood"].map((medium) => (
                  <option key={medium} value={medium}>
                    {medium}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <button
            type="button"
            onClick={onPredict}
            disabled={isPredicting}
            className="rounded-full bg-ink px-6 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-ink/30"
          >
            {isPredicting ? "Running..." : "Run prediction"}
          </button>
        </div>

        {predictError ? (
          <div className="mt-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {predictError}
          </div>
        ) : null}
      </div>

      <div className="soft-panel rounded-[30px] p-7 sm:p-8">
        <p className="text-xs font-semibold uppercase tracking-[0.28em] text-ink/55">Ready</p>
        <div className="mt-4 space-y-4">
          <Stat label="Gene" value={uploadData.primary_gene} />
          <Stat label="Protein" value={`${uploadData.protein_length} aa`} />
          <Stat label="Preview" value={uploadData.protein_sequence_preview} mono />
          {prediction ? <Stat label="Last result" value={prediction.prediction} /> : null}
        </div>
      </div>
    </section>
  );
}

function Input({ label, name, value, onChange }) {
  return (
    <label className="block">
      <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.24em] text-ink/50">{label}</span>
      <input
        name={name}
        value={value}
        onChange={onChange}
        className="w-full rounded-[22px] border border-ink/10 bg-white px-4 py-3 text-sm text-ink outline-none focus:border-lagoon"
      />
    </label>
  );
}

function Stat({ label, value, mono = false }) {
  return (
    <div className="rounded-[22px] bg-white/80 px-4 py-4">
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-ink/45">{label}</p>
      <p className={`mt-2 text-sm font-semibold text-ink ${mono ? "break-all font-mono" : ""}`}>{value}</p>
    </div>
  );
}

export default DockPage;
