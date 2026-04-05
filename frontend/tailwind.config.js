/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,jsx}", "./components/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#e2eefb",
        panel: "rgba(10, 17, 32, 0.72)",
        accent: "#67e8f9",
        dnaA: "#38bdf8",
        dnaT: "#fb7185",
        dnaG: "#34d399",
        dnaC: "#fbbf24"
      },
      boxShadow: {
        glow: "0 20px 60px rgba(8, 15, 32, 0.35)"
      },
      backgroundImage: {
        hero: "radial-gradient(circle at 12% 20%, rgba(103, 232, 249, 0.18), transparent 30%), radial-gradient(circle at 88% 12%, rgba(251, 146, 60, 0.18), transparent 28%), linear-gradient(135deg, #08111f 0%, #0f172a 50%, #172554 100%)"
      }
    }
  },
  plugins: []
};

