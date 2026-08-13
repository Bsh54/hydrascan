import { GitPullRequest, XCircle } from "lucide-react";

const ROWS = [
  { pkg: "keyv@6.0.0", advisory: "MAL-2026-11524", fix: "npm uninstall keyv" },
  { pkg: "flat-cache@6.1.24", advisory: "MAL-2026-11971", fix: "npm uninstall flat-cache" },
  { pkg: "file-entry-cache@11.1.6", advisory: "MAL-2026-11970", fix: "npm uninstall file-entry-cache" },
];

export function BotSection() {
  return (
    <section id="bot" className="mb-24 w-full scroll-mt-24">
      <div className="grid w-full grid-cols-1 items-center gap-16 md:grid-cols-2">
        <div>
          <span className="font-mono text-label-mono uppercase tracking-widest text-secondary">
            GitHub App
          </span>
          <h2 className="mb-6 mt-3 text-headline-lg text-snow">Reviews every pull request.</h2>
          <p className="mb-8 text-body-lg text-pearl">
            Install the HydraScan app on a repository and it checks each pull request on its own, 
            no workflow file, no config. It comments with the reachable compromised dependencies and
            their fixes, and sets a status check that can block the merge.
          </p>
          <a
            href="https://github.com/apps/hydrascan"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 rounded-[6px] bg-terminal-green px-6 py-3 font-medium text-snow transition-colors hover:bg-primary"
          >
            <GitPullRequest className="h-4 w-4" strokeWidth={2} />
            Install the GitHub App
          </a>
        </div>

        {/* Mock PR comment */}
        <div className="overflow-hidden rounded-2xl border border-slate-edge glass-card">
          <div className="flex items-center gap-2 border-b border-slate-edge/50 bg-black/20 p-sm">
            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-phosphor text-[11px] font-bold text-background">
              H
            </div>
            <span className="font-mono text-label-mono text-snow">HydraScan</span>
            <span className="font-mono text-caption text-mercury">commented on your PR</span>
          </div>
          <div className="flex flex-col gap-3 p-gutter">
            <div className="flex items-center gap-2">
              <XCircle className="h-4 w-4 text-error" strokeWidth={2} />
              <span className="font-mono text-label-mono text-error">Exposure score: 100/100</span>
            </div>
            <div className="overflow-hidden rounded-[6px] border border-slate-edge">
              <div className="grid grid-cols-[1fr_auto] gap-x-4 bg-surface-container-low px-3 py-2 font-mono text-caption text-mercury">
                <span>Dependency</span>
                <span>Fix</span>
              </div>
              {ROWS.map((r) => (
                <div
                  key={r.pkg}
                  className="grid grid-cols-[1fr_auto] gap-x-4 border-t border-slate-edge px-3 py-2 font-mono text-caption"
                >
                  <span className="text-error">{r.pkg}</span>
                  <span className="text-phosphor">{r.fix}</span>
                </div>
              ))}
            </div>
            <span className="font-mono text-caption text-mercury">Blast radius computed by HydraDB.</span>
          </div>
        </div>
      </div>
    </section>
  );
}
