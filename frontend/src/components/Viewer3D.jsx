import { useEffect, useRef, useState } from "react";
import $3Dmol from "3dmol";

const Viewer3D = ({ pdbData, title = "3D Structure Viewer", bindingScore = null, viewType = "structure" }) => {
  const containerRef = useRef(null);
  const viewerRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true);
  const [viewStyle, setViewStyle] = useState("cartoon");
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!pdbData || !containerRef.current) {
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      // Initialize 3Dmol viewer
      const config = { backgroundColor: "white" };
      const viewer = $3Dmol.createViewer(containerRef.current, config);

      // Add PDB data
      viewer.addModel(pdbData, "pdb");

      // Apply style based on viewType
      if (viewType === "docking") {
        // Protein as cartoon (blue)
        viewer.setStyle({ ss: "s" }, { cartoon: { color: "spectrum" } });
        viewer.setStyle({ ss: "h" }, { cartoon: { color: "spectrum" } });
        viewer.setStyle({ ss: "c" }, { cartoon: { color: "spectrum" } });

        // Ligand as stick (orange)
        viewer.setStyle({ atom: "C" }, { stick: { colorscheme: "orangecarbon" } });
        viewer.setStyle({ atom: "O" }, { stick: { colorscheme: "orangecarbon" } });
        viewer.setStyle({ atom: "N" }, { stick: { colorscheme: "orangecarbon" } });
      } else {
        // Default protein visualization
        applyStyle(viewer, viewStyle);
      }

      // Center and zoom
      viewer.zoomTo();
      viewerRef.current = viewer;
      setIsLoading(false);
    } catch (err) {
      setError(`Error rendering structure: ${err.message}`);
      setIsLoading(false);
    }
  }, [pdbData, viewType]);

  // Update style when viewStyle changes
  useEffect(() => {
    if (viewerRef.current && viewType === "structure") {
      try {
        viewerRef.current.setStyle({}, { cartoon: {} });
        applyStyle(viewerRef.current, viewStyle);
        viewerRef.current.render();
      } catch (err) {
        console.error("Error updating style:", err);
      }
    }
  }, [viewStyle, viewType]);

  const applyStyle = (viewer, style) => {
    if (style === "cartoon") {
      viewer.setStyle({}, { cartoon: { color: "spectrum" } });
    } else if (style === "stick") {
      viewer.setStyle({}, { stick: { colorscheme: "whiteCarbon" } });
    } else if (style === "sphere") {
      viewer.setStyle({}, { sphere: { colorscheme: "chainHetatm" } });
    } else if (style === "surface") {
      viewer.addSurface($3Dmol.SurfaceType.VDW, {
        opacity: 0.8,
        color: "spectrum",
      });
    }
  };

  const handleStyleChange = (newStyle) => {
    setViewStyle(newStyle);
    if (viewerRef.current) {
      viewerRef.current.setStyle({}, {});
    }
  };

  return (
    <div className="w-full rounded-lg border border-gray-300 bg-white p-4 shadow-md">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-gray-900">{title}</h3>
          {bindingScore !== null && (
            <p className="text-sm text-gray-600">Binding Score: {bindingScore}</p>
          )}
        </div>
        {viewType === "structure" && (
          <div className="flex gap-2">
            <button
              onClick={() => handleStyleChange("cartoon")}
              className={`rounded px-3 py-1 text-sm font-medium transition ${
                viewStyle === "cartoon"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-800 hover:bg-gray-300"
              }`}
            >
              Cartoon
            </button>
            <button
              onClick={() => handleStyleChange("stick")}
              className={`rounded px-3 py-1 text-sm font-medium transition ${
                viewStyle === "stick"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-800 hover:bg-gray-300"
              }`}
            >
              Stick
            </button>
            <button
              onClick={() => handleStyleChange("sphere")}
              className={`rounded px-3 py-1 text-sm font-medium transition ${
                viewStyle === "sphere"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-800 hover:bg-gray-300"
              }`}
            >
              Sphere
            </button>
          </div>
        )}
      </div>

      {isLoading && (
        <div className="flex h-80 items-center justify-center bg-gray-100">
          <div className="text-center">
            <div className="mb-2 inline-block h-8 w-8 animate-spin rounded-full border-4 border-blue-300 border-t-blue-600"></div>
            <p className="text-gray-600">Loading 3D structure...</p>
          </div>
        </div>
      )}

      {error && (
        <div className="flex h-80 items-center justify-center bg-red-50">
          <div className="text-center text-red-600">
            <p className="font-semibold">Error Loading Structure</p>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      )}

      {!isLoading && !error && (
        <div
          ref={containerRef}
          className="h-80 rounded bg-gradient-to-br from-gray-50 to-gray-100"
          style={{ position: "relative" }}
        />
      )}

      <div className="mt-4 text-xs text-gray-500">
        💡 Tip: Use mouse to rotate • Scroll to zoom • Right-click to pan
      </div>
    </div>
  );
};

export default Viewer3D;
