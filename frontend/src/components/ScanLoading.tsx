import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";

const STEPS = [
  "Resolving dependencies",
  "Querying advisories",
  "Building graph in HydraDB",
  "Computing blast radius",
];

export function ScanLoading() {
  const [step, setStep] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setStep((s) => Math.min(s + 1, STEPS.length - 1)), 3500);
    return () => clearInterval(id);
  }, []);

  const progress = ((step + 1) / STEPS.length) * 100;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center">
      {/* Blurred dashboard skeleton behind */}
      <div className="pointer-events-none absolute inset-0 mx-auto flex max-w-max-width flex-col gap-sm px-sm pt-[80px] blur-md">
        <div className="h-[72vh] w-full rounded-[24px] border border-slate-edge bg-surface-container-low" />
        <div className="h-24 w-full rounded-[24px] border border-slate-edge bg-glass" />
      </div>
      <div className="absolute inset-0 bg-deep-space/70 backdrop-blur-sm" />

      {/* Loader */}
      <div className="relative flex w-full max-w-sm flex-col items-center gap-6 px-6">
        <Loader2 className="h-8 w-8 animate-spin text-phosphor" strokeWidth={2} />
        <div className="w-full">
          <div className="mb-2 flex items-center justify-between font-mono text-label-mono">
            <span className="text-snow">{STEPS[step]}</span>
            <span className="tnum text-mercury">
              {step + 1}/{STEPS.length}
            </span>
          </div>
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-edge">
            <div
              className="h-full rounded-full bg-phosphor transition-[width] duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
