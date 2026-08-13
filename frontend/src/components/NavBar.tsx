import { Link } from "react-router-dom";

export function NavBar() {
  return (
    <nav className="fixed top-0 z-50 flex w-full items-center justify-between border-b border-slate-edge bg-deep-space/80 px-gutter py-base backdrop-blur-xl">
      <Link
        to="/"
        className="flex items-center gap-xs rounded p-2 text-headline-sm font-bold tracking-tighter text-phosphor transition-colors duration-150 hover:bg-white/5"
      >
        HydraScan
      </Link>
      <div className="flex items-center gap-6 font-mono text-label-mono">
        <a
          href="https://www.npmjs.com/package/hydrascan"
          target="_blank"
          rel="noreferrer"
          className="text-pearl transition-colors hover:text-snow"
        >
          npm
        </a>
        <a
          href="https://pypi.org/project/hydrascan/"
          target="_blank"
          rel="noreferrer"
          className="text-pearl transition-colors hover:text-snow"
        >
          PyPI
        </a>
      </div>
    </nav>
  );
}
