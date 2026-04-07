import { useState } from "react";
import Viewer3D from "../components/Viewer3D";

function ResultPage({ uploadData, prediction, onReset }) {
  const [activeTab, setActiveTab] = useState("overview");
  const [structurePdb, setStructurePdb] = useState(null);
  const [dockingPdb, setDockingPdb] = useState(null);
  const [loading3D, setLoading3D] = useState(false);
  const [error3D, setError3D] = useState(null);

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

  const fetchWithTimeout = async (url, timeout = 30000) => {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    try {
      const response = await fetch(url, { signal: controller.signal });
      clearTimeout(id);
      if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      return await response.json();
    } catch (error) {
      clearTimeout(id);
      if (error.name === 'AbortError') {
        throw new Error('Request timed out - backend is taking too long. Check if prediction completed successfully.');
      }
      throw error;
    }
  };

  const handleViewStructure = async () => {
    if (structurePdb) {
      setActiveTab("structure");
      return;
    }

    if (!uploadData?.upload_id) {
      setError3D("No upload ID found. Please upload and predict first.");
      return;
    }

    setLoading3D(true);
    setError3D(null);
    try {
      const apiUrl = `/api/structure?upload_id=${uploadData.upload_id}`;
      const data = await fetchWithTimeout(apiUrl, 30000);
      if (!data.pdb) throw new Error("No PDB data in response");
      setStructurePdb(data.pdb);
      setActiveTab("structure");
    } catch (err) {
      setError3D(`Error loading structure: ${err.message}`);
    } finally {
      setLoading3D(false);
    }
  };

  const handleViewDocking = async () => {
    if (dockingPdb) {
      setActiveTab("docking");
      return;
    }

    if (!uploadData?.upload_id) {
      setError3D("No upload ID found. Please upload and predict first.");
      return;
    }

    setLoading3D(true);
    setError3D(null);
    try {
      const apiUrl = `/api/docking?upload_id=${uploadData.upload_id}`;
      const data = await fetchWithTimeout(apiUrl, 30000);
      if (!data.pdb) throw new Error("No PDB data in response");
      setDockingPdb(data.pdb);
      setActiveTab("docking");
    } catch (err) {
      setError3D(`Error loading docking: ${err.message}`);
    } finally {
      setLoading3D(false);
    }
  };

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

      {/* 3D Visualization Tabs */}
      <div className="soft-panel rounded-[30px] p-7">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-ink/50 mb-4">🔬 3D Molecular Visualization</p>
        
        {/* Tab Navigation */}
        <div className="flex gap-2 mb-6 border-b border-ink/10">
          <button
            onClick={() => setActiveTab("overview")}
            className={`px-4 py-2 font-medium transition ${
              activeTab === "overview"
                ? "border-b-2 border-moss text-ink"
                : "text-ink/60 hover:text-ink"
            }`}
          >
            Overview
          </button>
          <button
            onClick={handleViewStructure}
            disabled={loading3D}
            className={`px-4 py-2 font-medium transition ${
              activeTab === "structure"
                ? "border-b-2 border-lagoon text-ink"
                : "text-ink/60 hover:text-ink"
            } disabled:opacity-50`}
          >
            {loading3D ? "Loading..." : "🧬 Protein Structure"}
          </button>
          <button
            onClick={handleViewDocking}
            disabled={loading3D}
            className={`px-4 py-2 font-medium transition ${
              activeTab === "docking"
                ? "border-b-2 border-ember text-ink"
                : "text-ink/60 hover:text-ink"
            } disabled:opacity-50`}
          >
            {loading3D ? "Loading..." : "💊 Docked Complex"}
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === "overview" && (
          <div className="grid gap-6 lg:grid-cols-[1fr_1fr]">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-ink/50 mb-4">Docking Details</p>
              <div className="grid gap-4 sm:grid-cols-2">
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

            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-ink/50 mb-4">Biology</p>
              <div className="rounded-[22px] bg-white/80 px-4 py-4">
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
        )}

        {activeTab === "structure" && (
          <>
            {loading3D && (
              <div className="flex h-80 items-center justify-center bg-gray-100 rounded-lg">
                <div className="text-center">
                  <div className="mb-4 inline-block h-10 w-10 animate-spin rounded-full border-4 border-blue-300 border-t-blue-600"></div>
                  <p className="text-gray-700 font-semibold">Loading 3D Structure...</p>
                  <p className="text-xs text-gray-500 mt-2">This may take 10-30 seconds</p>
                </div>
              </div>
            )}
            {!loading3D && structurePdb && (
              <Viewer3D
                pdbData={structurePdb}
                title="🧬 Protein Structure (ESMFold)"
                viewType="structure"
              />
            )}
          </>
        )}

        {activeTab === "docking" && (
          <>
            {loading3D && (
              <div className="flex h-80 items-center justify-center bg-gray-100 rounded-lg">
                <div className="text-center">
                  <div className="mb-4 inline-block h-10 w-10 animate-spin rounded-full border-4 border-blue-300 border-t-blue-600"></div>
                  <p className="text-gray-700 font-semibold">Loading Docking Complex...</p>
                  <p className="text-xs text-gray-500 mt-2">This may take 10-30 seconds</p>
                </div>
              </div>
            )}
            {!loading3D && dockingPdb && (
              <Viewer3D
                pdbData={dockingPdb}
                title="💊 Docked Complex (Protein + Antibiotic)"
                bindingScore={prediction.binding_score}
                viewType="docking"
              />
            )}
          </>
        )}

        {error3D && (
          <div className="mt-4 rounded-[22px] bg-red-50 border-2 border-red-300 px-6 py-4">
            <p className="text-sm font-semibold text-red-800 mb-2">⚠️ Loading Error</p>
            <p className="text-sm text-red-700">{error3D}</p>
            <p className="text-xs text-red-600 mt-3">💡 Try: Refresh page → Re-run prediction → Click tab again</p>
          </div>
        )}
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
