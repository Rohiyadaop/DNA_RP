"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navigation() {
  const pathname = usePathname();

  const isActivePath = (path) => {
    if (path === "/" || path === "") {
      return pathname === "/" || pathname === "";
    }
    return pathname?.startsWith(path);
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-slate-950/80 backdrop-blur-xl border-b border-white/10">
      <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-10">
        <div className="flex items-center justify-between gap-4">
          {/* Logo/Home */}
          <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-cyan-400 via-sky-400 to-fuchsia-500 text-[10px] font-bold tracking-[0.18em] text-white">
              DNA
            </div>
            <span className="hidden text-sm font-bold text-white sm:inline">BioSignal Lab</span>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center gap-2">
            <Link
              href="/dna-generator"
              className={`px-3 py-2 rounded-lg text-xs sm:text-sm font-medium transition ${
                isActivePath("/dna-generator")
                  ? "bg-cyan-400/15 text-cyan-100 border border-cyan-400/30"
                  : "text-slate-300 hover:text-white hover:bg-white/5"
              }`}
            >
              DNA Generator
            </Link>
            <Link
              href="/dna-predictor"
              className={`px-3 py-2 rounded-lg text-xs sm:text-sm font-medium transition ${
                isActivePath("/dna-predictor")
                  ? "bg-emerald-400/15 text-emerald-100 border border-emerald-400/30"
                  : "text-slate-300 hover:text-white hover:bg-white/5"
              }`}
            >
              Resistance Predictor
            </Link>
          </div>

          {/* Info */}
          <div className="hidden md:block text-xs text-slate-400">
            GSOC Hackathon
          </div>
        </div>
      </div>
    </nav>
  );
}
