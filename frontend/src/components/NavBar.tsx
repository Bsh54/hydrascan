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
      <button className="flex items-center gap-2 rounded-[6px] bg-primary-container px-4 py-2 font-mono text-label-mono text-snow transition-colors hover:bg-primary-container/90">
        Sign in with GitHub
      </button>
    </nav>
  );
}
