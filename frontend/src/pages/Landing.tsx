import { ScanLine, Network, ShieldCheck, Telescope, Gauge, Wand2, SearchCheck, ArrowRight, Rocket } from "lucide-react";
import { NavBar } from "../components/NavBar";
import { Footer } from "../components/Footer";
import { ScanForm } from "../components/ScanForm";

export function Landing() {
  const scrollTop = () => window.scrollTo({ top: 0, behavior: "smooth" });

  return (
    <div className="relative flex min-h-screen flex-col overflow-x-hidden bg-deep-space text-on-surface">
      <div className="fixed inset-0 -z-20 bg-deep-space" />
      <div className="halo-glow pointer-events-none absolute left-1/2 top-[-200px] -z-10 h-[800px] w-full -translate-x-1/2" />

      <NavBar />

      <main className="relative z-10 mx-auto flex w-full max-w-max-width flex-grow flex-col items-center px-gutter pb-xl pt-[100px]">
        {/* Hero */}
        <section className="mb-xl mt-xl flex w-full flex-col items-center text-center">
          <h1 className="mb-md max-w-4xl text-display-xl leading-tight tracking-tighter text-snow drop-shadow-md">
            Map your impact. <br />Trace the threat.
          </h1>
          <p className="mb-lg max-w-2xl text-body-lg text-pearl">
            Map your npm or PyPI dependency graph, and see exactly which of your projects a
            compromised package can reach — and through which path.
          </p>
          <ScanForm />
        </section>

        {/* How it works */}
        <section className="mb-24 flex w-full flex-col items-center">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-headline-lg text-snow">How it works</h2>
            <p className="mx-auto max-w-2xl text-body-lg text-pearl">
              From a repository URL to a full blast-radius graph, computed by HydraDB.
            </p>
          </div>
          <div className="grid w-full grid-cols-1 gap-8 md:grid-cols-3">
            {[
              { step: "Step 01", icon: ScanLine, title: "Resolve", body: "Point at any npm or PyPI repository. We resolve the full transitive dependency tree from its lockfile or manifest." },
              { step: "Step 02", icon: Network, title: "Map", body: "The tree is written into the HydraDB graph engine and cross-referenced with live OSV advisories." },
              { step: "Step 03", icon: ShieldCheck, title: "Trace", body: "HydraDB computes every attack path from your project to a compromised package — with the exact fix." },
            ].map(({ step, icon: Icon, title, body }) => (
              <div key={step} className="group relative flex flex-col overflow-hidden rounded-2xl p-8 glass-card">
                <div className="absolute -right-4 -top-4 h-24 w-24 rounded-full bg-tertiary-container/10 blur-2xl transition-all group-hover:bg-tertiary-container/20" />
                <span className="mb-4 font-mono text-label-mono text-secondary">{step}</span>
                <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-lg border border-slate-edge bg-obsidian">
                  <Icon className="h-6 w-6 text-phosphor" strokeWidth={1.75} />
                </div>
                <h3 className="mb-3 text-headline-sm text-snow">{title}</h3>
                <p className="text-body-md text-mercury">{body}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Uncover the unseen depth */}
        <section className="mb-24 flex w-full flex-col items-center">
          <div className="grid w-full grid-cols-1 items-center gap-16 md:grid-cols-2">
            <div>
              <h2 className="mb-6 text-headline-lg text-snow">Uncover the unseen depth.</h2>
              <p className="mb-8 text-body-lg text-pearl">
                Modern applications are built on thousands of dependencies. When one falls, the
                blast radius is massive. We give you the radar.
              </p>
              <ul className="space-y-6">
                {[
                  { icon: Telescope, tint: "bg-primary-container/20 text-phosphor", title: "Transitive dependency detection", body: "See vulnerabilities hiding 4, 5, or 6 levels deep in your supply chain." },
                  { icon: Gauge, tint: "bg-tertiary-container/20 text-tertiary", title: "Reachability-based scoring", body: "Severity driven by what is actually reachable from your project, not raw CVE counts." },
                  { icon: Wand2, tint: "bg-error-container/20 text-error", title: "Guided remediation", body: "For each compromised package, the exact command to remove or upgrade it." },
                ].map(({ icon: Icon, tint, title, body }) => (
                  <li key={title} className="flex items-start gap-4">
                    <div className={`mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded ${tint}`}>
                      <Icon className="h-[18px] w-[18px]" strokeWidth={2} />
                    </div>
                    <div>
                      <h4 className="mb-1 text-lg text-snow">{title}</h4>
                      <p className="text-body-md text-mercury">{body}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
            <div className="relative flex h-[500px] w-full items-center justify-center overflow-hidden rounded-2xl border border-[rgba(167,162,255,0.2)] glass-card">
              <div className="absolute inset-0 bg-gradient-to-br from-tertiary-container/10 to-transparent" />
              <svg className="h-full w-full opacity-60 mix-blend-screen" viewBox="0 0 400 400">
                <circle cx="200" cy="200" fill="none" r="150" stroke="#21262d" strokeWidth="1" />
                <circle cx="200" cy="200" fill="none" r="100" stroke="#31353c" strokeDasharray="4 4" strokeWidth="1" />
                <circle cx="200" cy="200" fill="none" r="50" stroke="#31353c" strokeWidth="1" />
                <circle className="animate-pulse" cx="200" cy="200" fill="#08872b" r="6" />
                <circle cx="280" cy="120" fill="#a4aea6" r="4" />
                <circle cx="100" cy="250" fill="#a4aea6" r="5" />
                <circle cx="300" cy="280" fill="#ffb4ab" r="8" />
                <circle cx="150" cy="80" fill="#bfc2ff" r="6" />
                <line stroke="#31353c" strokeWidth="1" x1="200" x2="280" y1="200" y2="120" />
                <line stroke="#31353c" strokeWidth="1" x1="200" x2="100" y1="200" y2="250" />
                <line stroke="#93000a" strokeWidth="1.5" x1="200" x2="300" y1="200" y2="280" />
                <line stroke="#31353c" strokeWidth="1" x1="280" x2="150" y1="120" y2="80" />
              </svg>
            </div>
          </div>
        </section>

        {/* Keyv case study */}
        <section className="relative mb-24 flex w-full flex-col items-start">
          <div className="mb-lg">
            <div className="mb-md inline-block rounded-full border border-slate-edge bg-obsidian px-3 py-1">
              <span className="font-mono text-label-mono uppercase tracking-widest text-secondary">The Data: Case Study</span>
            </div>
            <h2 className="text-headline-md text-snow">The Keyv Attack (August 2026)</h2>
            <p className="mt-2 max-w-2xl text-body-md text-mercury">
              A demonstration of a cascading dependency failure originating from a minor utility update.
            </p>
          </div>
          <div className="relative z-10 grid w-full grid-cols-1 gap-md md:grid-cols-12">
            <div className="relative col-span-1 flex min-h-[450px] flex-col overflow-hidden rounded-[24px] border border-[rgba(167,162,255,0.2)] glass-card md:col-span-8">
              <div className="flex items-center justify-between border-b border-slate-edge/50 bg-black/20 p-gutter">
                <span className="font-mono text-label-mono text-snow">Dependency Graph Visualization</span>
                <div className="flex gap-2">
                  <div className="h-3 w-3 rounded-full bg-error-container" />
                  <div className="h-3 w-3 rounded-full bg-tertiary-container" />
                  <div className="h-3 w-3 rounded-full bg-primary-container" />
                </div>
              </div>
              <div className="group relative flex w-full flex-grow items-center justify-center overflow-hidden bg-obsidian/30">
                <svg className="pointer-events-none absolute inset-0 h-full w-full opacity-40 mix-blend-screen" viewBox="0 0 800 400">
                  <path d="M400,200 L300,100 L200,150 L100,50" fill="none" stroke="#21262d" strokeWidth="1.5" />
                  <path d="M400,200 L500,120 L600,180 L700,90" fill="none" stroke="#21262d" strokeWidth="1.5" />
                  <path d="M400,200 L450,300 L350,350" fill="none" stroke="#21262d" strokeWidth="1.5" />
                  <circle className="animate-pulse" cx="400" cy="200" fill="#93000a" r="8" />
                  <circle cx="300" cy="100" fill="#a4aea6" r="4" />
                  <circle cx="500" cy="120" fill="#a4aea6" r="5" />
                  <circle cx="450" cy="300" fill="#a4aea6" r="6" />
                </svg>
                <div className="relative z-10 rounded-xl border border-white/5 bg-black/40 p-6 text-center opacity-0 backdrop-blur-sm transition-opacity duration-300 group-hover:opacity-100">
                  <p className="font-mono text-label-mono text-snow">Node <span className="text-error">keyv@6.0.0</span> compromised</p>
                </div>
              </div>
            </div>
            <div className="col-span-1 flex flex-col gap-md md:col-span-4">
              <div className="relative flex flex-grow flex-col justify-center overflow-hidden rounded-[24px] border border-slate-edge bg-obsidian p-gutter">
                <div className="absolute -right-4 -top-4 h-32 w-32 rounded-full bg-error-container/10 blur-3xl" />
                <span className="relative z-10 mb-xs block font-mono text-label-mono uppercase text-mercury">Blast Radius</span>
                <div className="relative z-10 mb-2 text-display-xl text-error">400+</div>
                <p className="relative z-10 text-body-sm text-pearl">Packages downstream impacted within 4 hours of the malicious commit.</p>
              </div>
              <div className="flex flex-col justify-between rounded-[24px] border border-[rgba(167,162,255,0.2)] p-gutter glass-card">
                <div>
                  <SearchCheck className="mb-2 h-6 w-6 text-secondary" strokeWidth={2} />
                  <h3 className="mb-2 text-headline-sm text-snow">Trace Route</h3>
                  <p className="text-body-sm text-mercury">Analyze the exact path the vulnerability took through transitive dependencies.</p>
                </div>
                <button onClick={scrollTop} className="mt-4 flex w-full items-center justify-center gap-2 rounded-[6px] border border-slate-edge bg-transparent px-4 py-2 font-mono text-label-mono text-snow transition-colors hover:bg-white/5">
                  Scan a Repository <ArrowRight className="h-4 w-4" strokeWidth={2} />
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* FAQ */}
        <section className="mx-auto mb-24 flex w-full max-w-3xl flex-col items-center">
          <h2 className="mb-12 text-center text-headline-lg text-snow">Frequently Asked Questions</h2>
          <div className="w-full space-y-4">
            {[
              { q: "Is my code safe?", a: "We only read your package.json, requirements.txt, and lockfiles to build the dependency graph. Your source code is never read or stored." },
              { q: "npm only?", a: "Both npm and PyPI. When a lockfile is present it is used directly; otherwise the transitive tree is resolved via deps.dev." },
              { q: "Do you support private repositories?", a: "Public repositories work today. Private repository support via GitHub sign-in is on the roadmap." },
              { q: "Is there a CLI?", a: "Yes — the same engine runs from the terminal with `hydrascan scan`, so you can wire it into your own scripts." },
            ].map(({ q, a }) => (
              <div key={q} className="rounded-xl border border-slate-edge bg-obsidian p-6">
                <h3 className="mb-2 text-lg text-snow">{q}</h3>
                <p className="text-body-md text-mercury">{a}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Final CTA */}
        <section className="relative flex w-full flex-col items-center overflow-hidden rounded-[24px] border border-slate-edge bg-obsidian/50 py-24 text-center">
          <div className="halo-glow absolute inset-0 z-0 opacity-50" />
          <div className="relative z-10 flex flex-col items-center">
            <h2 className="mb-6 text-4xl tracking-tighter text-snow md:text-5xl">Secure your project now.</h2>
            <p className="mb-10 max-w-xl text-body-lg text-pearl">
              Don't wait for the next major supply chain attack. Map your blast radius today.
            </p>
            <button onClick={scrollTop} className="flex items-center justify-center gap-xs rounded-[6px] bg-terminal-green px-8 py-4 text-lg font-bold text-snow transition-all hover:bg-opacity-90">
              Start Scanning for Free <Rocket className="h-5 w-5" strokeWidth={2} />
            </button>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
