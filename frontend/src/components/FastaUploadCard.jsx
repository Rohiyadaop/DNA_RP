function FastaUploadCard({
  selectedFile,
  uploadData,
  uploadError,
  isUploading,
  onFileChange,
  onUpload
}) {
  return (
    <section className="glass-card rounded-[28px] border border-white/70 p-6 shadow-glow">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.32em] text-lagoon/70">
            Step 1
          </p>
          <h2 className="mt-2 text-2xl font-bold text-ink">Upload FASTA Sequence</h2>
          <p className="mt-2 max-w-xl text-sm leading-6 text-ink/70">
            Load a bacterial genome FASTA file. The backend validates DNA symbols, maps
            resistance genes, translates protein regions, and derives structure-aware
            sequence features.
          </p>
        </div>
        <div className="rounded-full bg-lagoon/10 px-4 py-2 text-xs font-semibold text-lagoon">
          BioPython + CARD-style mapping
        </div>
      </div>

      <label className="mt-6 flex cursor-pointer flex-col items-center justify-center rounded-[24px] border border-dashed border-lagoon/35 bg-gradient-to-br from-white to-white/40 px-6 py-10 text-center transition hover:border-lagoon/60 hover:bg-white">
        <span className="rounded-full bg-lagoon/10 px-4 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-lagoon">
          FASTA Input
        </span>
        <span className="mt-4 text-lg font-semibold text-ink">
          {selectedFile ? selectedFile.name : "Choose a .fasta / .fa / .fna file"}
        </span>
        <span className="mt-2 text-sm text-ink/60">
          Single-record DNA FASTA recommended for the demo workflow
        </span>
        <input
          className="hidden"
          type="file"
          accept=".fasta,.fa,.fna,text/plain"
          onChange={onFileChange}
        />
      </label>

      <div className="mt-5 flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={onUpload}
          disabled={!selectedFile || isUploading}
          className="rounded-full bg-ink px-5 py-3 text-sm font-semibold text-white transition hover:bg-lagoon disabled:cursor-not-allowed disabled:bg-ink/30"
        >
          {isUploading ? "Uploading..." : "Upload FASTA"}
        </button>
        <span className="text-sm text-ink/60">
          {uploadData ? "Sequence ready for prediction." : "Upload is required before prediction."}
        </span>
      </div>

      {uploadError ? (
        <div className="mt-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {uploadError}
        </div>
      ) : null}

      {uploadData ? (
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <InfoBlock label="Sequence Length" value={`${uploadData.sequence_length} bp`} />
          <InfoBlock label="GC Content" value={`${(uploadData.gc_content * 100).toFixed(2)}%`} />
          <InfoBlock
            label="Mapped Genes"
            value={uploadData.mapped_genes.length ? uploadData.mapped_genes.join(", ") : "None"}
          />
          <InfoBlock
            label="Mutations"
            value={uploadData.mutations.length ? uploadData.mutations.join(", ") : "No mutation"}
          />
        </div>
      ) : null}
    </section>
  );
}

function InfoBlock({ label, value }) {
  return (
    <div className="rounded-[22px] border border-ink/8 bg-white/75 p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.24em] text-ink/45">{label}</p>
      <p className="mt-2 text-sm font-medium leading-6 text-ink">{value}</p>
    </div>
  );
}

export default FastaUploadCard;
