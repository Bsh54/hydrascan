import { useState } from "react";
import { ShieldAlert, Wrench, Copy, Check, ExternalLink } from "lucide-react";
import type { ScanResult } from "../lib/types";

interface RemediationListProps {
  result: ScanResult;
  className?: string;
}

const OSV = "https://osv.dev/vulnerability/";

export function RemediationList({ result, className = "" }: RemediationListProps) {
  if (result.compromised.length === 0) return null;

  const fixByPackage = new Map(result.remediation.map((r) => [r.package, r]));

  return (
    <div className={`flex flex-col gap-sm rounded-[24px] border border-slate-edge p-gutter bg-glass ${className}`}>
        <h3 className="eyebrow flex items-center gap-2">
          <ShieldAlert className="h-3.5 w-3.5" strokeWidth={2} />
          Vulnerable dependencies — problem &amp; fix
        </h3>
        <p className="text-body-sm text-mercury">
          Each reachable compromised dependency, why it is flagged, and how to remediate it.
        </p>

        <div className="flex flex-col gap-md">
          {result.compromised.map((pkg) => {
            const fix = fixByPackage.get(pkg.coordinate);
            return (
              <div key={pkg.coordinate} className="flex flex-col gap-sm rounded-panel border border-slate-edge bg-surface-container-low p-md">
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-edge pb-sm">
                  <span className="font-mono text-label-mono font-bold text-error">{pkg.coordinate}</span>
                  {fix?.introducedBy && (
                    <span className="font-mono text-caption text-mercury">
                      pulled in by <span className="text-pearl">{fix.introducedBy}</span>
                    </span>
                  )}
                </div>

                {/* Problem */}
                <div className="flex flex-col gap-2">
                  {pkg.advisories.map((a) => (
                    <div key={a.id} className="flex items-start gap-2">
                      <a
                        href={`${OSV}${a.id}`}
                        target="_blank"
                        rel="noreferrer"
                        className="mt-0.5 flex items-center gap-1 font-mono text-caption font-bold text-error hover:underline"
                      >
                        {a.id} <ExternalLink className="h-3 w-3" strokeWidth={2} />
                      </a>
                      <p className="text-body-sm text-pearl">
                        {a.summary}
                        <span className="text-mercury">
                          {" "}· {a.severity}
                          {a.published ? ` · published ${a.published}` : ""}
                        </span>
                      </p>
                    </div>
                  ))}
                </div>

                {/* Fix */}
                {fix && (
                  <div className="flex items-center gap-2">
                    <Wrench className="h-3.5 w-3.5 shrink-0 text-phosphor" strokeWidth={2} />
                    <FixCommand command={fix.command} />
                  </div>
                )}
              </div>
            );
          })}
        </div>
    </div>
  );
}

function FixCommand({ command }: { command: string }) {
  const [copied, setCopied] = useState(false);
  async function copy() {
    await navigator.clipboard.writeText(command);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }
  return (
    <div className="group flex flex-1 items-center justify-between rounded-[6px] border border-slate-edge bg-carbon px-3 py-1.5">
      <code className="font-mono text-caption text-phosphor">{command}</code>
      <button onClick={copy} aria-label="Copy command" className="text-mercury hover:text-snow">
        {copied ? <Check className="h-3.5 w-3.5 text-phosphor" strokeWidth={2} /> : <Copy className="h-3.5 w-3.5" strokeWidth={2} />}
      </button>
    </div>
  );
}
