import { Link } from "react-router-dom";

function GithubIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor" aria-hidden>
      <path d="M12 2C6.48 2 2 6.58 2 12.25c0 4.53 2.87 8.37 6.84 9.73.5.09.68-.22.68-.49 0-.24-.01-.87-.01-1.71-2.78.62-3.37-1.37-3.37-1.37-.46-1.18-1.11-1.49-1.11-1.49-.91-.64.07-.62.07-.62 1 .07 1.53 1.05 1.53 1.05.89 1.56 2.34 1.11 2.91.85.09-.66.35-1.11.63-1.36-2.22-.26-4.55-1.14-4.55-5.07 0-1.12.39-2.03 1.03-2.75-.1-.26-.45-1.3.1-2.71 0 0 .84-.28 2.75 1.05a9.28 9.28 0 0 1 5 0c1.91-1.33 2.75-1.05 2.75-1.05.55 1.41.2 2.45.1 2.71.64.72 1.03 1.63 1.03 2.75 0 3.94-2.34 4.81-4.57 5.06.36.32.68.94.68 1.9 0 1.37-.01 2.47-.01 2.81 0 .27.18.59.69.49A10.02 10.02 0 0 0 22 12.25C22 6.58 17.52 2 12 2Z" />
    </svg>
  );
}

function Mark() {
  return (
    <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" aria-hidden>
      <circle cx="12" cy="19" r="2.3" fill="#5fed83" />
      <circle cx="5" cy="6" r="1.8" fill="#a4aea6" />
      <circle cx="19" cy="6" r="1.8" fill="#a4aea6" />
      <circle cx="12" cy="4" r="1.8" fill="#ff5b5b" />
      <path d="M12 17V6M12 6 5 7M12 6l7 1" stroke="#484f58" strokeWidth="1.2" />
    </svg>
  );
}

export function NavBar() {
  return (
    <nav className="fixed top-0 z-50 w-full border-b border-slate-edge bg-deep-space/80 backdrop-blur-xl">
      <div className="mx-auto flex h-16 w-full max-w-max-width items-center justify-between px-gutter">
        <Link
          to="/"
          className="flex items-center gap-2 text-headline-sm font-bold tracking-tighter text-phosphor"
        >
          <Mark />
          HydraScan
        </Link>

        <div className="hidden items-center gap-8 font-mono text-label-mono text-pearl md:flex">
          <a href="#web" className="transition-colors hover:text-snow">Dashboard</a>
          <a href="#cli" className="transition-colors hover:text-snow">CLI</a>
          <a href="#bot" className="transition-colors hover:text-snow">GitHub App</a>
        </div>

        <div className="flex items-center gap-5 font-mono text-label-mono text-pearl">
          <a href="https://www.npmjs.com/package/hydrascan" target="_blank" rel="noreferrer" className="hidden transition-colors hover:text-snow sm:inline">npm</a>
          <a href="https://pypi.org/project/hydrascan/" target="_blank" rel="noreferrer" className="hidden transition-colors hover:text-snow sm:inline">PyPI</a>
          <a href="https://github.com/Bsh54/hydrascan" target="_blank" rel="noreferrer" aria-label="GitHub" className="transition-colors hover:text-snow">
            <GithubIcon className="h-[18px] w-[18px]" />
          </a>
          <a href="#top" className="rounded-[6px] bg-terminal-green px-4 py-2 font-medium text-snow transition-colors hover:bg-primary">
            Scan a repo
          </a>
        </div>
      </div>
    </nav>
  );
}
