import { Terminal } from "lucide-react";

export function CliSection() {
  return (
    <section id="cli" className="mb-24 w-full scroll-mt-24">
      <div className="grid w-full grid-cols-1 items-center gap-16 md:grid-cols-2">
        {/* Text */}
        <div>
          <span className="font-mono text-label-mono uppercase tracking-widest text-secondary">Command line</span>
          <h2 className="mb-6 mt-3 text-headline-lg text-snow">Fix it from your terminal.</h2>
          <p className="mb-8 text-body-lg text-pearl">
            The same engine runs from your shell — no setup. It prints the fix for every compromised
            dependency and exits non-zero when one is reachable, so it drops straight into CI.
          </p>
          <div className="flex flex-wrap gap-3">
            <div className="inline-flex items-center gap-2 rounded-[6px] border border-slate-edge bg-obsidian px-4 py-3 font-mono text-label-mono">
              <span className="text-fog">$</span>
              <span className="text-phosphor">npx hydrascan</span>
            </div>
            <div className="inline-flex items-center gap-2 rounded-[6px] border border-slate-edge bg-obsidian px-4 py-3 font-mono text-label-mono">
              <span className="text-fog">$</span>
              <span className="text-phosphor">pip install hydrascan</span>
            </div>
          </div>
        </div>

        {/* Terminal mock */}
        <div className="overflow-hidden rounded-2xl border border-slate-edge bg-carbon">
          <div className="flex items-center gap-2 border-b border-slate-edge/50 bg-black/30 px-4 py-3">
            <span className="h-3 w-3 rounded-full bg-error" />
            <span className="h-3 w-3 rounded-full bg-tertiary" />
            <span className="h-3 w-3 rounded-full bg-phosphor" />
            <Terminal className="ml-2 h-3.5 w-3.5 text-mercury" strokeWidth={2} />
          </div>
          <div className="flex flex-col gap-1 p-gutter font-mono text-caption leading-relaxed">
            <div><span className="text-fog">$</span> <span className="text-snow">npx hydrascan my-org/my-app</span></div>
            <div className="h-2" />
            <div className="text-snow">my-app@1.0.0</div>
            <div className="text-mercury">642 packages&nbsp; | &nbsp;npm&nbsp; | &nbsp;engine: hydradb</div>
            <div className="h-2" />
            <div className="text-error">Exposure score: 100/100 (Critical)</div>
            <div className="h-2" />
            <div className="text-error">Compromised - malicious packages reachable (3):</div>
            <div className="h-1" />
            <div><span className="text-error">keyv@6.0.0</span>&nbsp;&nbsp;&nbsp;-&gt;&nbsp;&nbsp;&nbsp;<span className="text-phosphor">npm uninstall keyv</span></div>
            <div><span className="text-error">flat-cache@6.1.24</span>&nbsp;&nbsp;-&gt;&nbsp;&nbsp;&nbsp;<span className="text-phosphor">npm uninstall flat-cache</span></div>
            <div><span className="text-error">file-entry-cache@11.1.6</span>&nbsp;&nbsp;-&gt;&nbsp;&nbsp;&nbsp;<span className="text-phosphor">npm uninstall file-entry-cache</span></div>
            <div className="h-2" />
            <div style={{ color: "#f6c177" }}>Known vulnerabilities reachable (2):</div>
            <div className="h-1" />
            <div><span style={{ color: "#f6c177" }}>express@4.19.2</span>&nbsp;&nbsp;-&gt;&nbsp;&nbsp;&nbsp;<span className="text-phosphor">npm install express@4.20.0</span></div>
          </div>
        </div>
      </div>
    </section>
  );
}
