import { Radar, ArrowRight } from "lucide-react";

const AFFECTED = [
  { pkg: "keyv@6.0.0", advisory: "MAL-2026-11524" },
  { pkg: "flat-cache@6.1.24", advisory: "MAL-2026-11971" },
  { pkg: "cacheable-request@13.0.20", advisory: "MAL-2026-11964" },
];

export function WebSection({ onScan }: { onScan: () => void }) {
  return (
    <section className="mb-24 w-full">
      <div className="grid w-full grid-cols-1 items-center gap-16 md:grid-cols-2">
        {/* Text */}
        <div>
          <span className="font-mono text-label-mono uppercase tracking-widest text-secondary">Web dashboard</span>
          <h2 className="mb-6 mt-3 text-headline-lg text-snow">See the whole blast radius.</h2>
          <p className="mb-8 text-body-lg text-pearl">
            Paste a repository URL and get the full picture: an interactive dependency graph, the
            exposure score, every reachable compromised package, and the exact fix for each one.
          </p>
          <button
            onClick={onScan}
            className="inline-flex items-center gap-2 rounded-[6px] bg-terminal-green px-6 py-3 font-medium text-snow transition-colors hover:bg-primary"
          >
            Scan a repository <ArrowRight className="h-4 w-4" strokeWidth={2} />
          </button>
        </div>

        {/* Mock dashboard card */}
        <div className="overflow-hidden rounded-2xl border border-slate-edge glass-card">
          <div className="flex items-center gap-2 border-b border-slate-edge/50 bg-black/20 p-sm">
            <Radar className="h-4 w-4 text-mercury" strokeWidth={2} />
            <span className="font-mono text-label-mono text-snow">
              Scanning: <span className="text-phosphor">got@15.1.0</span>
            </span>
            <span className="ml-auto rounded-pill border border-slate-edge px-2 py-0.5 font-mono text-caption text-mercury">
              npm
            </span>
          </div>
          <div className="flex flex-col gap-sm p-gutter">
            <div className="flex items-end justify-between">
              <div>
                <span className="font-mono text-caption uppercase tracking-widest text-mercury">Exposure score</span>
                <div className="mt-1 flex items-baseline gap-1">
                  <span className="tnum text-5xl font-bold text-error">97</span>
                  <span className="text-headline-sm text-fog">%</span>
                </div>
              </div>
              <span className="rounded-pill border border-error px-3 py-1 font-mono text-caption text-error">High</span>
            </div>
            <div className="h-1.5 w-full overflow-hidden rounded-full bg-surface-container-high">
              <div className="h-full rounded-full bg-error" style={{ width: "97%" }} />
            </div>
            <div className="mt-1 flex flex-col gap-2">
              {AFFECTED.map((a) => (
                <div key={a.pkg} className="flex items-center justify-between rounded-[6px] border border-error/20 bg-error/5 px-3 py-2 font-mono text-caption">
                  <span className="font-bold text-error">{a.pkg}</span>
                  <span className="text-mercury">{a.advisory}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
