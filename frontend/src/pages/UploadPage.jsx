import { useState } from "react";

function UploadPage({ selectedFileName, uploadData, uploadError, isUploading, onUpload }) {
  const [file, setFile] = useState(null);

  return (
    <section className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
      <div className="soft-panel rounded-[30px] p-7 sm:p-8">
        <p className="text-xs font-semibold uppercase tracking-[0.28em] text-lagoon/70">Step 1</p>
        <h2 className="title-font mt-3 text-3xl font-semibold text-ink">Upload FASTA</h2>

        <label className="mt-6 flex min-h-[240px] cursor-pointer flex-col items-center justify-center rounded-[28px] border border-dashed border-lagoon/35 bg-white/70 px-6 text-center">
          <span className="rounded-full bg-lagoon/10 px-4 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-lagoon">
            DNA File
          </span>
          <span className="mt-5 text-lg font-semibold text-ink">
            {file?.name || selectedFileName || "Choose .fasta / .fa / .fna"}
          </span>
          <span className="mt-2 text-sm text-ink/60">Single FASTA record recommended</span>
          <input
            type="file"
            accept=".fasta,.fa,.fna,text/plain"
            className="hidden"
            onChange={(event) => setFile(event.target.files?.[0] || null)}
          />
        </label>

        <button
          type="button"
          onClick={() => file && onUpload(file)}
          disabled={!file || isUploading}
          className="mt-5 rounded-full bg-ink px-5 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-ink/30"
        >
          {isUploading ? "Uploading..." : "Upload Sequence"}
        </button>

        {uploadError ? (
          <div className="mt-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {uploadError}
          </div>
        ) : null}
      </div>

      <div className="soft-panel rounded-[30px] p-7 sm:p-8">
        <p className="text-xs font-semibold uppercase tracking-[0.28em] text-ink/55">Detected</p>
        {uploadData ? (
          <div className="mt-4 space-y-4">
            <Stat label="Gene" value={uploadData.primary_gene} />
            <Stat label="Protein" value={`${uploadData.protein_length} aa`} />
            <Stat label="GC" value={`${(uploadData.gc_content * 100).toFixed(1)}%`} />
            <Stat
              label="Mutations"
              value={uploadData.mutations.length ? uploadData.mutations.join(", ") : "No mutation"}
            />
          </div>
        ) : (
          <p className="mt-4 text-sm leading-6 text-ink/68">
            After upload, this page will show the main gene, protein length, GC content, and detected mutations.
          </p>
        )}
      </div>
    </section>
  );
}

function Stat({ label, value }) {
  return (
    <div className="rounded-[22px] bg-white/80 px-4 py-4">
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-ink/45">{label}</p>
      <p className="mt-2 text-sm font-semibold leading-6 text-ink">{value}</p>
    </div>
  );
}

export default UploadPage;
