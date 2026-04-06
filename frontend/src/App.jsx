import { useEffect, useMemo, useState } from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";

import TopNav from "./components/TopNav";
import DockPage from "./pages/DockPage";
import HomePage from "./pages/HomePage";
import LearnPage from "./pages/LearnPage";
import ResultPage from "./pages/ResultPage";
import UploadPage from "./pages/UploadPage";
import { predictResistance, uploadFastaFile } from "./services/api";

const STORAGE_KEY = "amr-structure-docking-state";

const initialFormState = {
  smiles: "C1CC1N2C=C(C(=O)C3=CC(=C(C=C32)N4CCNCC4)F)C(=O)O",
  temperature: "37.0",
  ph: "7.0",
  medium: "MHB"
};

function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}

function AppRoutes() {
  const navigate = useNavigate();
  const location = useLocation();
  const [uploadData, setUploadData] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [formState, setFormState] = useState(initialFormState);
  const [selectedFileName, setSelectedFileName] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [isPredicting, setIsPredicting] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [predictError, setPredictError] = useState("");

  useEffect(() => {
    const saved = window.localStorage.getItem(STORAGE_KEY);
    if (!saved) {
      return;
    }
    try {
      const parsed = JSON.parse(saved);
      setUploadData(parsed.uploadData || null);
      setPrediction(parsed.prediction || null);
      setFormState(parsed.formState || initialFormState);
      setSelectedFileName(parsed.selectedFileName || "");
    } catch {
      window.localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  useEffect(() => {
    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ uploadData, prediction, formState, selectedFileName })
    );
  }, [uploadData, prediction, formState, selectedFileName]);

  const routeLabel = useMemo(() => {
    if (location.pathname.startsWith("/upload")) return "Upload";
    if (location.pathname.startsWith("/dock")) return "Docking";
    if (location.pathname.startsWith("/result")) return "Result";
    if (location.pathname.startsWith("/learn")) return "Learn";
    return "Home";
  }, [location.pathname]);

  const handleUpload = async (file) => {
    setIsUploading(true);
    setUploadError("");
    setPredictError("");
    setPrediction(null);
    setSelectedFileName(file?.name || "");
    try {
      const response = await uploadFastaFile(file);
      setUploadData(response);
      navigate("/dock");
    } catch (error) {
      setUploadError(error?.response?.data?.detail || "Upload failed.");
    } finally {
      setIsUploading(false);
    }
  };

  const handlePredict = async () => {
    if (!uploadData?.upload_id) {
      setPredictError("Upload FASTA first.");
      navigate("/upload");
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
      navigate("/result");
    } catch (error) {
      setPredictError(error?.response?.data?.detail || "Prediction failed.");
    } finally {
      setIsPredicting(false);
    }
  };

  const resetSession = () => {
    setUploadData(null);
    setPrediction(null);
    setFormState(initialFormState);
    setSelectedFileName("");
    setUploadError("");
    setPredictError("");
    window.localStorage.removeItem(STORAGE_KEY);
    navigate("/upload");
  };

  return (
    <div className="page-shell grid-pattern">
      <div className="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-4 py-5 sm:px-6 lg:px-8">
        <TopNav routeLabel={routeLabel} hasUpload={Boolean(uploadData)} hasPrediction={Boolean(prediction)} />
        <div className="mt-6 flex-1">
          <Routes>
            <Route path="/" element={<HomePage hasUpload={Boolean(uploadData)} />} />
            <Route
              path="/upload"
              element={
                <UploadPage
                  selectedFileName={selectedFileName}
                  uploadData={uploadData}
                  uploadError={uploadError}
                  isUploading={isUploading}
                  onUpload={handleUpload}
                />
              }
            />
            <Route
              path="/dock"
              element={
                <DockPage
                  formState={formState}
                  setFormState={setFormState}
                  uploadData={uploadData}
                  prediction={prediction}
                  predictError={predictError}
                  isPredicting={isPredicting}
                  onPredict={handlePredict}
                />
              }
            />
            <Route
              path="/result"
              element={
                <ResultPage
                  uploadData={uploadData}
                  prediction={prediction}
                  onReset={resetSession}
                />
              }
            />
            <Route path="/learn" element={<LearnPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </div>
    </div>
  );
}

export default App;
