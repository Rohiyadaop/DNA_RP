/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      boxShadow: {
        glow: "0 18px 45px rgba(19, 74, 70, 0.18)"
      },
      colors: {
        ink: "#10231d",
        lagoon: "#155e63",
        moss: "#5f7c2f",
        paper: "#f8f6ef",
        ember: "#e08b2c"
      }
    }
  },
  plugins: []
};
