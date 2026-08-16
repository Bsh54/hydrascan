import { useState } from "react";
import type { ReactNode } from "react";
import { ShieldAlert, TriangleAlert, Wrench, Copy, Check, ExternalLink } from "lucide-react";
import type { ScanResult, CompromisedPackage, Remediation } from "../lib/types";

interface RemediationListProps {
  result: ScanResult;
  className?: string;
}

const OSV = "https://osv.dev/vulnerability/";

export function RemediationList({ result, className = "" }: RemediationListProps) {
  const malware = result.compromised ?? [];
  const vulnerable = result.vulnerable ?? [];
  if (malware.length === 0 && vulnerable.length === 0) return null;

  const fixByPackage = new Map(result.remediation.map((r) => [r.package, r]));

  return (
    <div className={`flex flex-col gap-lg rounded-[24px] border border-slate-edge p-gutter bg-glass ${className}`}>
      {malware.length > 0 && (
        <Section
          icon={<ShieldAlert className="h-3.5 w-3.5" strokeWidth={2} />}
          title="Compromised: malicious packages"
          subtitle="Reachable packages with malicious-package advisories. These run code at install time; remove them."
          tone="error"
          packages={malware}
          fixByPackage={fixByPackage}
        />
      )}
      {vulnerable.length > 0 && (
        <Section
          icon={<TriangleAlert className="h-3.5 w-3.5" strokeWidth={2} />}
          title="Known vulnerabilities"
          subtitle="Reachable packages with ordinary CVE/GHSA advisories, not malware, but worth patching."
          tone="tertiary"
          packages={vulnerable}
          fixByPackage={fixByPackage}
        />
      )}
    </div>
  );
}

function Section({
  icon,
  title,
  subtitle,
  tone,
  packages,
  fixByPackage,
}: {
  icon: ReactNode;
  title: string;
  subtitle: string;
  tone: "error" | "tertiary";
  packages: CompromisedPackage[];
  fixByPackage: Map<string, Remediation>;
}) {
  const text = tone === "error" ? "text-error" : "text-tertiary";
  const border = tone === "error" ? "border-error/20" : "border-tertiary/20";

  return (
    <div className="flex flex-col gap-sm">
      <h3 className={`eyebrow flex items-center gap-2 ${text}`}>
        {icon} {title} ({packages.length})
      </h3>
      <p className="text-body-sm text-mercury">{subtitle}</p>
      <div className="flex flex-col gap-md">
        {packages.map((pkg) => {
          const fix = fixByPackage.get(pkg.coordinate);
          return (
            <div key={pkg.coordinate} className={`flex flex-col gap-sm rounded-panel border ${border} bg-surface-container-low p-md`}>
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-edge pb-sm">
                <span className={`font-mono text-label-mono font-bold ${text}`}>{pkg.coordinate}</span>
                {fix?.introducedBy && (
                  <span className="font-mono text-caption text-mercury">
                    pulled in by <span className="text-pearl">{fix.introducedBy}</span>
                  </span>
                )}
              </div>

              {pkg.temporal && (
                <div className="flex flex-wrap items-center gap-2 text-caption">
                  {pkg.temporal.disclosedAt && (
                    <span className="rounded-full border border-slate-edge px-2 py-0.5 text-mercury">
                      window opened {pkg.temporal.disclosedAt}
                      {pkg.temporal.daysSinceDisclosed != null ? ` · ${pkg.temporal.daysSinceDisclosed}d live` : ""}
                    </span>
                  )}
                  <span
                    className={`rounded-full px-2 py-0.5 font-medium ${
                      pkg.temporal.patched ? "bg-tertiary/15 text-tertiary" : "bg-error/15 text-error"
                    }`}
                  >
                    {pkg.temporal.patched ? "patch available" : "no patch yet"}
                  </span>
                  {pkg.temporal.resolvedPublishedAt && (
                    <span className="text-mercury">
                      your {pkg.temporal.resolvedVersion} published {pkg.temporal.resolvedPublishedAt}
                    </span>
                  )}
                </div>
              )}

              <div className="flex flex-col gap-2">
                {pkg.advisories.map((a) => (
                  <div key={a.id} className="flex items-start gap-2">
                    <a
                      href={`${OSV}${a.id}`}
                      target="_blank"
                      rel="noreferrer"
                      className={`mt-0.5 flex items-center gap-1 font-mono text-caption font-bold ${text} hover:underline`}
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
