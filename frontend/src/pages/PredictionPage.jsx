import { useState } from "react";

import FastaUploadCard from "../components/FastaUploadCard";
import PredictionForm from "../components/PredictionForm";
import PredictionResult from "../components/PredictionResult";
import WorkflowPanel from "../components/WorkflowPanel";
import { predictResistance, uploadFastaFile } from "../services/api";

const initialFormState = {
  smiles: "C1CC1N2C=C(C(=O)C3=CC(=C(C=C32)N4CCNCC4)F)C(=O)O",
  temperature: "37.0",
  ph: "7.0",
  medium: "MHB"
};

function PredictionPage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadData, setUploadData] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [formState, setFormState] = useState(initialFormState);
  const [uploadError, setUploadError] = useState("");
  const [predictError, setPredictError] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [isPredicting, setIsPredicting] = useState(false);

  const handleFileChange = (event) => {
    const file = event.target.files?.[0] || null;
    setSelectedFile(file);
    setUploadData(null);
    setPrediction(null);
    setUploadError("");
    setPredictError("");
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadError("Please select a FASTA file before uploading.");
      return;
    }

    setIsUploading(true);
    setUploadError("");
    setPrediction(null);
    try {
      const response = await uploadFastaFile(selectedFile);
      setUploadData(response);
    } catch (error) {
      setUploadError(
        error?.response?.data?.detail || "FASTA upload failed. Please check the file format."
      );
    } finally {
      setIsUploading(false);
    }
  };

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormState((current) => ({ ...current, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!uploadData?.upload_id) {
      setPredictError("Upload a FASTA file first so the backend can build the sequence context.");
      return;
    }

    setIsPredicting(true);
    setPredictError("");
    try {
      const response = await predictResistance({
        upload_id: uploadData.upload_id,
        smiles: formState.smiles,
        temperature: Number(formState.temperature),
        ph: Number(formState.ph),
        medium: formState.medium
      });
      setPrediction(response);
    } catch (error) {
      setPredictError(
        error?.response?.data?.detail || "Prediction failed. Please review the submitted inputs."
      );
    } finally {
      setIsPredicting(false);
    }
  };

  return (
    <main className="grid-pattern min-h-screen px-4 py-8 text-ink sm:px-6 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <section className="mb-8 rounded-[32px] border border-white/80 bg-white/65 px-6 py-8 shadow-glow backdrop-blur md:px-8">
          <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
            <div className="max-w-3xl">
              <p className="text-xs font-semibold uppercase tracking-[0.36em] text-lagoon/80">
                Context-Aware AMR Web App
              </p>
              <h1 className="mt-3 text-4xl font-bold leading-tight text-ink md:text-5xl">
                Predict antibiotic resistance from DNA, chemistry, and lab context.
              </h1>
              <p className="mt-4 max-w-2xl text-base leading-7 text-ink/72">
                This app connects a React frontend to a FastAPI backend that runs a
                multi-modal machine learning pipeline for FASTA parsing, mutation
                detection, protein translation, structure approximation, docking-style
                scoring, and resistance classification.
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
              <HeroMetric label="Inputs" value="Genome + Drug + Env" />
              <HeroMetric label="Model" value="CPU Neural Net" />
              <HeroMetric label="Outputs" value="Class + Confidence" />
            </div>
          </div>
        </section>

        <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
          <div className="space-y-6">
            <FastaUploadCard
              selectedFile={selectedFile}
              uploadData={uploadData}
              uploadError={uploadError}
              isUploading={isUploading}
              onFileChange={handleFileChange}
              onUpload={handleUpload}
            />

            <PredictionForm
              formState={formState}
              onChange={handleChange}
              onSubmit={handleSubmit}
              isSubmitting={isPredicting}
              hasUpload={Boolean(uploadData?.upload_id)}
            />

            {predictError ? (
              <div className="rounded-[24px] border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
                {predictError}
              </div>
            ) : null}
          </div>

          <div className="space-y-6">
            <PredictionResult prediction={prediction} isLoading={isPredicting} />
            <WorkflowPanel />
          </div>
        </div>
      </div>
    </main>
  );
}

function HeroMetric({ label, value }) {
  return (
    <div className="rounded-[22px] border border-ink/8 bg-white/80 px-4 py-4">
      <p className="text-xs font-semibold uppercase tracking-[0.24em] text-ink/50">{label}</p>
      <p className="mt-2 text-sm font-semibold text-ink">{value}</p>
    </div>
  );
}

export default PredictionPage;
