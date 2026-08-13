import { Users, TextSearch, Server } from "lucide-react";
import type { ScanResult } from "../lib/types";

interface IntelligencePanelProps {
  result: ScanResult;
}

export function IntelligencePanel({ result }: IntelligencePanelProps) {
  const maintainers = result.sharedMaintainers ?? [];
  const infrastructure = result.sharedInfrastructure ?? [];
  const typosquats = result.typosquats ?? [];
  if (maintainers.length === 0 && infrastructure.length === 0 && typosquats.length === 0) return null;

  return (
    <>
      {maintainers.length > 0 && (
        <div className="flex flex-col gap-sm rounded-[24px] border border-slate-edge p-gutter bg-glass">
          <h3 className="eyebrow flex items-center gap-2">
            <Users className="h-3.5 w-3.5" strokeWidth={2} />
            Shared Maintainers
          </h3>
          <p className="text-body-sm text-mercury">
            One hijacked account can compromise every package it controls, the worm pattern.
          </p>
          <ul className="flex flex-col gap-xs">
            {maintainers.map((m) => (
              <li key={m.maintainer} className="rounded-[6px] border border-error/20 bg-error/5 p-sm">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-label-mono font-bold text-error">{m.maintainer}</span>
                  <span className="font-mono text-caption text-mercury">{m.packages.length} packages</span>
                </div>
                <p className="mt-1 font-mono text-caption text-pearl">{m.packages.join(", ")}</p>
              </li>
            ))}
          </ul>
        </div>
      )}

      {infrastructure.length > 0 && (
        <div className="flex flex-col gap-sm rounded-[24px] border border-slate-edge p-gutter bg-glass">
          <h3 className="eyebrow flex items-center gap-2">
            <Server className="h-3.5 w-3.5" strokeWidth={2} />
            Shared Infrastructure
          </h3>
          <p className="text-body-sm text-mercury">
            Compromised packages published from the same source repository.
          </p>
          <ul className="flex flex-col gap-xs">
            {infrastructure.map((i) => (
              <li key={i.repository} className="rounded-[6px] border border-error/20 bg-error/5 p-sm">
                <p className="truncate font-mono text-label-mono font-bold text-error" title={i.repository}>
                  {i.repository}
                </p>
                <p className="mt-1 font-mono text-caption text-pearl">{i.packages.join(", ")}</p>
              </li>
            ))}
          </ul>
        </div>
      )}

      {typosquats.length > 0 && (
        <div className="flex flex-col gap-sm rounded-[24px] border border-slate-edge p-gutter bg-glass">
          <h3 className="eyebrow flex items-center gap-2">
            <TextSearch className="h-3.5 w-3.5" strokeWidth={2} />
            Possible Typosquats
          </h3>
          <p className="text-body-sm text-mercury">
            Dependency names one edit away from a popular package, a common attack vector.
          </p>
          <ul className="flex flex-col gap-xs">
            {typosquats.map((t) => (
              <li key={t.package} className="flex items-center justify-between rounded-[6px] border border-slate-edge bg-surface-container-low p-sm font-mono text-label-mono">
                <span className="text-snow">{t.package}</span>
                <span className="text-mercury">looks like <span className="text-phosphor">{t.similarTo}</span></span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </>
  );
}
