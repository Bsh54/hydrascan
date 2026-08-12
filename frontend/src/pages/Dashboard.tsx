import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Radar } from "lucide-react";
import { NavBar } from "../components/NavBar";
import { Footer } from "../components/Footer";
import { GraphView } from "../components/GraphView";
import { ExposureCard } from "../components/ExposureCard";
import { RemediationList } from "../components/RemediationList";
import { IntelligencePanel } from "../components/IntelligencePanel";
import type { ScanResult } from "../lib/types";

export function Dashboard() {
  const location = useLocation();
  const result = location.state as ScanResult | null;
  const [, setSelected] = useState<string | null>(null);

  if (!result) {
    return (
      <div className="flex min-h-screen flex-col bg-background text-on-background">
        <NavBar />
        <main className="mx-auto flex flex-1 flex-col items-center justify-center gap-4 px-6 text-center">
          <p className="text-mercury">No scan loaded.</p>
          <Link to="/" className="rounded-[6px] bg-terminal-green px-6 py-3 text-snow hover:bg-opacity-90">
            Scan a repository
          </Link>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col overflow-x-hidden bg-background text-on-background">
      <NavBar />

      <main className="relative mx-auto mt-[64px] w-full max-w-max-width px-sm py-md">
        <div className="pointer-events-none absolute inset-0 z-0 flex items-center justify-center overflow-hidden">
          <div className="absolute h-[600px] w-[600px] rounded-full bg-tertiary/10 opacity-50 blur-[80px] mix-blend-screen" />
        </div>

        {/* Cinema graph: full width */}
        <div className="relative z-10 flex h-[72vh] w-full flex-col overflow-hidden rounded-[24px] border border-slate-edge bg-surface-container-low">
          <div className="pointer-events-none absolute left-0 top-0 z-20 flex w-full items-start justify-between p-sm">
            <div className="flex items-center gap-xs rounded-[6px] border border-slate-edge bg-obsidian px-sm py-xs shadow-lg">
              <Radar className="h-4 w-4 text-mercury" strokeWidth={2} />
              <span className="font-mono text-label-mono text-snow">
                Scanning: <span className="text-phosphor">{result.project}</span>
              </span>
              {result.ecosystem && (
                <span className="rounded-pill border border-slate-edge px-2 py-0.5 font-mono text-caption text-mercury">
                  {result.ecosystem}
                </span>
              )}
            </div>
            {result.isExposed && (
              <div className="flex items-center gap-xs rounded-[6px] border border-slate-edge bg-obsidian px-sm py-xs shadow-lg">
                <div className="h-2 w-2 rounded-full bg-error" />
                <span className="font-mono text-label-mono text-mercury">Compromised Path Detected</span>
              </div>
            )}
          </div>
          <div className="h-full w-full bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-surface/50 to-abyss">
            <GraphView result={result} onSelect={setSelected} />
          </div>
        </div>
      </main>

      {/* Analyses below the cinema graph */}
      <section className="relative z-10 mx-auto flex w-full max-w-max-width flex-col gap-sm px-sm pb-md">
        <ExposureCard result={result} />
        <div className="grid grid-cols-1 gap-sm md:grid-cols-3">
          <IntelligencePanel result={result} />
        </div>
        <RemediationList result={result} />
      </section>
      <Footer />
    </div>
  );
}
