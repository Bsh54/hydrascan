import { NavBar } from "../components/NavBar";
import { Footer } from "../components/Footer";
import { ScanForm } from "../components/ScanForm";
import { HeroGraph } from "../components/HeroGraph";
import { WebSection } from "../components/WebSection";
import { CliSection } from "../components/CliSection";
import { BotSection } from "../components/BotSection";

export function Landing() {
  const scrollTop = () => window.scrollTo({ top: 0, behavior: "smooth" });

  return (
    <div className="relative flex min-h-screen flex-col overflow-x-hidden text-on-surface">
      <div className="fixed inset-0 -z-20 bg-deep-space" />
      <div className="halo-glow pointer-events-none absolute left-1/2 top-[-200px] -z-10 h-[800px] w-full -translate-x-1/2" />
      <HeroGraph />

      <NavBar />

      <main className="relative z-10 mx-auto flex w-full max-w-max-width flex-grow flex-col items-center px-gutter pb-xl pt-[88px]">
        {/* Hero — the one primary action */}
        <section id="top" className="mb-40 mt-lg flex w-full scroll-mt-24 flex-col items-center text-center">
          <span className="mb-4 font-mono text-label-mono uppercase tracking-widest text-mercury">
            Supply-chain security · powered by HydraDB
          </span>
          <h1 className="mb-md max-w-4xl text-display-xl leading-tight tracking-tighter text-snow drop-shadow-md">
            Map your impact. <br />Trace the threat.
          </h1>
          <p className="mb-lg max-w-2xl text-body-lg text-pearl">
            Map your npm or PyPI dependency graph, and see exactly which of your projects a
            compromised package can reach — and through which path.
          </p>
          <ScanForm />
        </section>

        {/* Product showcase — one surface per section, consistent rhythm */}
        <WebSection onScan={scrollTop} />
        <CliSection />
        <BotSection />
      </main>
      <Footer />
    </div>
  );
}
