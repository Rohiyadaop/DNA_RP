const MEDIUM_OPTIONS = ["LB", "MHB", "Minimal", "Blood"];

function PredictionForm({ formState, onChange, onSubmit, isSubmitting, hasUpload }) {
  return (
    <section className="glass-card rounded-[28px] border border-white/70 p-6 shadow-glow">
      <p className="text-xs font-semibold uppercase tracking-[0.32em] text-ember/80">Step 2</p>
      <h2 className="mt-2 text-2xl font-bold text-ink">Drug + Environment Context</h2>
      <p className="mt-2 text-sm leading-6 text-ink/70">
        Provide the antibiotic SMILES string and lab environment. These inputs are
        converted into molecular fingerprints, docking-style interaction scores, and
        encoded growth-condition features.
      </p>

      <form className="mt-6 space-y-5" onSubmit={onSubmit}>
        <Field label="SMILES String" htmlFor="smiles">
          <textarea
            id="smiles"
            name="smiles"
            rows="4"
            value={formState.smiles}
            onChange={onChange}
            placeholder="e.g. C1CC1N2C=C(C(=O)..."
            className="w-full rounded-2xl border border-ink/10 bg-white px-4 py-3 text-sm text-ink outline-none transition focus:border-lagoon focus:ring-2 focus:ring-lagoon/20"
          />
        </Field>

        <div className="grid gap-5 md:grid-cols-3">
          <Field label="Temperature (°C)" htmlFor="temperature">
            <input
              id="temperature"
              name="temperature"
              type="number"
              min="20"
              max="50"
              step="0.1"
              value={formState.temperature}
              onChange={onChange}
              className="w-full rounded-2xl border border-ink/10 bg-white px-4 py-3 text-sm text-ink outline-none transition focus:border-lagoon focus:ring-2 focus:ring-lagoon/20"
            />
          </Field>

          <Field label="pH" htmlFor="ph">
            <input
              id="ph"
              name="ph"
              type="number"
              min="3"
              max="10"
              step="0.1"
              value={formState.ph}
              onChange={onChange}
              className="w-full rounded-2xl border border-ink/10 bg-white px-4 py-3 text-sm text-ink outline-none transition focus:border-lagoon focus:ring-2 focus:ring-lagoon/20"
            />
          </Field>

          <Field label="Medium" htmlFor="medium">
            <select
              id="medium"
              name="medium"
              value={formState.medium}
              onChange={onChange}
              className="w-full rounded-2xl border border-ink/10 bg-white px-4 py-3 text-sm text-ink outline-none transition focus:border-lagoon focus:ring-2 focus:ring-lagoon/20"
            >
              {MEDIUM_OPTIONS.map((medium) => (
                <option key={medium} value={medium}>
                  {medium}
                </option>
              ))}
            </select>
          </Field>
        </div>

        <button
          type="submit"
          disabled={!hasUpload || isSubmitting}
          className="w-full rounded-full bg-gradient-to-r from-lagoon via-ink to-moss px-5 py-3 text-sm font-semibold text-white transition hover:opacity-95 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {isSubmitting ? "Predicting..." : "Run Resistance Prediction"}
        </button>
      </form>
    </section>
  );
}

function Field({ label, htmlFor, children }) {
  return (
    <label className="block" htmlFor={htmlFor}>
      <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.24em] text-ink/55">
        {label}
      </span>
      {children}
    </label>
  );
}

export default PredictionForm;
