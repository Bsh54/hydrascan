import { Radar } from "lucide-react";

export function Footer() {
  return (
    <footer className="mt-auto w-full border-t border-slate-edge bg-carbon">
      <div className="mx-auto mt-xl flex w-full max-w-max-width flex-col items-center justify-between gap-lg px-gutter py-lg md:flex-row md:gap-0">
        <div className="flex flex-col items-center gap-4 md:items-start">
          <div className="flex items-center gap-2 font-mono text-label-mono text-phosphor">
            <Radar className="h-[18px] w-[18px]" strokeWidth={2} /> HydraScan
          </div>
          <p className="max-w-xs text-center font-body-sm text-body-sm text-fog md:text-left">
            © 2026 HydraScan. Engineered for supply-chain integrity.
          </p>
        </div>
        <nav className="flex flex-wrap justify-center gap-6 font-mono text-label-mono text-fog">
          <a className="underline-offset-4 transition-opacity duration-200 hover:text-phosphor hover:underline" href="https://github.com/Bsh54/hydrascan" target="_blank" rel="noreferrer">GitHub</a>
          <a className="underline-offset-4 transition-opacity duration-200 hover:text-phosphor hover:underline" href="https://www.npmjs.com/package/hydrascan" target="_blank" rel="noreferrer">npm</a>
          <a className="underline-offset-4 transition-opacity duration-200 hover:text-phosphor hover:underline" href="https://pypi.org/project/hydrascan/" target="_blank" rel="noreferrer">PyPI</a>
          <a className="underline-offset-4 transition-opacity duration-200 hover:text-phosphor hover:underline" href="https://github.com/apps/hydrascan" target="_blank" rel="noreferrer">GitHub App</a>
        </nav>
      </div>
    </footer>
  );
}
