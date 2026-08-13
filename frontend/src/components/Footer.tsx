function GithubIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor" aria-hidden>
      <path d="M12 2C6.48 2 2 6.58 2 12.25c0 4.53 2.87 8.37 6.84 9.73.5.09.68-.22.68-.49 0-.24-.01-.87-.01-1.71-2.78.62-3.37-1.37-3.37-1.37-.46-1.18-1.11-1.49-1.11-1.49-.91-.64.07-.62.07-.62 1 .07 1.53 1.05 1.53 1.05.89 1.56 2.34 1.11 2.91.85.09-.66.35-1.11.63-1.36-2.22-.26-4.55-1.14-4.55-5.07 0-1.12.39-2.03 1.03-2.75-.1-.26-.45-1.3.1-2.71 0 0 .84-.28 2.75 1.05a9.28 9.28 0 0 1 5 0c1.91-1.33 2.75-1.05 2.75-1.05.55 1.41.2 2.45.1 2.71.64.72 1.03 1.63 1.03 2.75 0 3.94-2.34 4.81-4.57 5.06.36.32.68.94.68 1.9 0 1.37-.01 2.47-.01 2.81 0 .27.18.59.69.49A10.02 10.02 0 0 0 22 12.25C22 6.58 17.52 2 12 2Z" />
    </svg>
  );
}

const COLUMNS = [
  {
    title: "Product",
    links: [
      { label: "Web dashboard", href: "#web" },
      { label: "CLI", href: "#cli" },
      { label: "GitHub App", href: "#bot" },
    ],
  },
  {
    title: "Install",
    links: [
      { label: "npm", href: "https://www.npmjs.com/package/hydrascan" },
      { label: "PyPI", href: "https://pypi.org/project/hydrascan/" },
      { label: "GitHub App", href: "https://github.com/apps/hydrascan" },
    ],
  },
  {
    title: "Project",
    links: [
      { label: "GitHub", href: "https://github.com/Bsh54/hydrascan" },
      { label: "HydraDB", href: "https://github.com/hydra-db/hydradb" },
      { label: "OSV.dev", href: "https://osv.dev" },
    ],
  },
];

export function Footer() {
  return (
    <footer className="mt-auto w-full border-t border-slate-edge bg-carbon">
      <div className="mx-auto grid w-full max-w-max-width grid-cols-2 gap-lg px-gutter py-xl md:grid-cols-[1.4fr_1fr_1fr_1fr]">
        <div className="col-span-2 flex flex-col gap-4 md:col-span-1">
          <img src="/logo.png" alt="HydraScan" className="h-9 w-auto self-start" />
          <p className="max-w-xs text-body-sm text-mercury">
            Graph-native supply-chain blast-radius analysis, powered by HydraDB.
          </p>
          <a
            href="https://github.com/Bsh54/hydrascan"
            target="_blank"
            rel="noreferrer"
            aria-label="GitHub"
            className="text-mercury transition-colors hover:text-phosphor"
          >
            <GithubIcon className="h-6 w-6" />
          </a>
        </div>

        {COLUMNS.map((col) => (
          <div key={col.title} className="flex flex-col gap-3">
            <span className="font-mono text-label-mono uppercase tracking-widest text-snow">{col.title}</span>
            {col.links.map((l) => (
              <a
                key={l.label}
                href={l.href}
                target={l.href.startsWith("http") ? "_blank" : undefined}
                rel={l.href.startsWith("http") ? "noreferrer" : undefined}
                className="text-body-md text-pearl transition-colors hover:text-phosphor"
              >
                {l.label}
              </a>
            ))}
          </div>
        ))}
      </div>

      <div className="border-t border-slate-edge/60">
        <div className="mx-auto flex w-full max-w-max-width flex-col items-center justify-between gap-2 px-gutter py-5 font-mono text-body-sm text-mercury md:flex-row">
          <span>© 2026 HydraScan. Engineered for supply-chain integrity.</span>
          <span>Powered by HydraDB.</span>
        </div>
      </div>
    </footer>
  );
}
