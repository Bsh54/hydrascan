import { Activity, Download } from "lucide-react";
import type { ScanResult } from "../lib/types";

interface ExposureCardProps {
  result: ScanResult;
  className?: string;
}

const RISK = (score: number) =>
  score >= 90
    ? { label: "Critical", text: "text-error", bar: "bg-error" }
    : score >= 70
      ? { label: "High", text: "text-error", bar: "bg-error" }
      : score >= 40
        ? { label: "Moderate", text: "text-tertiary", bar: "bg-tertiary" }
        : score > 0
          ? { label: "Low", text: "text-secondary", bar: "bg-secondary" }
          : { label: "Safe", text: "text-primary", bar: "bg-primary" };

export function ExposureCard({ result, className = "" }: ExposureCardProps) {
  const risk = RISK(result.exposureScore);

  function exportReport() {
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "hydrascan-report.json";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className={`flex flex-col items-stretch gap-md rounded-[24px] border border-slate-edge p-gutter bg-glass lg:flex-row lg:items-center ${className}`}>
      {/* Score */}
      <div className="flex flex-col gap-2 lg:w-[220px] lg:shrink-0">
        <span className="eyebrow flex items-center gap-2">
          <Activity className="h-3.5 w-3.5" strokeWidth={2} /> Exposure Score
        </span>
        <div className="flex items-baseline gap-xs">
          <span className={`tnum text-display-xl font-bold tracking-tighter ${risk.text}`}>
            {result.exposureScore}
          </span>
          <span className="text-headline-sm text-fog">%</span>
          <span className={`ml-2 rounded-pill border border-current px-2 py-0.5 font-mono text-caption ${risk.text}`}>
            {risk.label}
          </span>
        </div>
        <div className="h-2 w-full overflow-hidden rounded-full bg-surface-container-high">
          <div className={`h-full rounded-full ${risk.bar}`} style={{ width: `${result.exposureScore}%` }} />
        </div>
      </div>

      {/* Metrics */}
      <div className="grid flex-1 grid-cols-3 gap-sm">
        <Stat label="Packages" value={result.totalPackages} />
        <Stat label="Compromised" value={result.compromised.length} danger />
        <Stat label="Attack paths" value={result.paths.length} danger={result.paths.length > 0} />
      </div>

      {/* Export */}
      <button
        onClick={exportReport}
        className="flex items-center justify-center gap-xs rounded-[6px] border border-slate-edge px-4 py-sm font-mono text-label-mono text-snow transition-colors hover:bg-white/5 lg:shrink-0"
      >
        <Download className="h-4 w-4" strokeWidth={2} /> Export report
      </button>
    </div>
  );
}

function Stat({ label, value, danger }: { label: string; value: string | number; danger?: boolean }) {
  return (
    <div className="flex flex-col gap-1 rounded-[6px] border border-slate-edge bg-surface-container-low p-md">
      <span className={`tnum text-3xl font-bold ${danger ? "text-error" : "text-snow"}`}>{value}</span>
      <span className="font-mono text-caption text-mercury">{label}</span>
    </div>
  );
}
