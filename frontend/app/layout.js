import "./globals.css";
import Navigation from "@/components/Navigation";

export const metadata = {
  title: "DNA Mutation Resistance Predictor",
  description:
    "Predict antibiotic resistance from mutated DNA sequences or gene mutations with a cinematic dashboard, 3D DNA visualization, and scientific reasoning.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <Navigation />
        <div className="pt-16 sm:pt-20">
          {children}
        </div>
      </body>
    </html>
  );
}
