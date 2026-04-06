import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Home" },
  { to: "/upload", label: "Upload" },
  { to: "/dock", label: "Dock" },
  { to: "/result", label: "Result" },
  { to: "/learn", label: "Learn" }
];

function TopNav({ routeLabel, hasUpload, hasPrediction }) {
  return (
    <header className="soft-panel sticky top-4 z-20 rounded-[26px] px-4 py-4 sm:px-5">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-lagoon/75">
            AMR Structure Dock
          </p>
          <h1 className="title-font mt-2 text-2xl font-semibold text-ink">AI Antibiotic Resistance Predictor</h1>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `nav-chip rounded-full px-4 py-2 text-sm font-medium ${
                  isActive ? "bg-ink text-white" : "bg-white/85 text-ink hover:bg-lagoon/10"
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </div>

        <div className="flex items-center gap-2 text-xs text-ink/65">
          <span className="rounded-full bg-white/85 px-3 py-2">{routeLabel}</span>
          <span className={`rounded-full px-3 py-2 ${hasUpload ? "bg-moss/15 text-moss" : "bg-white/85"}`}>
            {hasUpload ? "FASTA ready" : "No FASTA"}
          </span>
          <span
            className={`rounded-full px-3 py-2 ${hasPrediction ? "bg-lagoon/15 text-lagoon" : "bg-white/85"}`}
          >
            {hasPrediction ? "Result ready" : "No result"}
          </span>
        </div>
      </div>
    </header>
  );
}

export default TopNav;
