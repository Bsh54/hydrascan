import { useState } from "react";
import { Copy, Check } from "lucide-react";

const COMMANDS = [
  { label: "npm", note: "JavaScript / npm projects", command: "npx hydrascan" },
  { label: "PyPI", note: "Python projects", command: "pip install hydrascan" },
];

export function InstallCommands() {
  return (
    <section className="mb-24 flex w-full flex-col items-center">
      <p className="mb-8 max-w-2xl text-center text-body-md text-mercury">
        Or install it and run it straight from your project.
      </p>
      <div className="grid w-full max-w-3xl grid-cols-1 gap-6 md:grid-cols-2">
        {COMMANDS.map((c) => (
          <CommandCard key={c.label} {...c} />
        ))}
      </div>
    </section>
  );
}

function CommandCard({ label, note, command }: { label: string; note: string; command: string }) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    await navigator.clipboard.writeText(command);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <div className="flex flex-col gap-3 rounded-2xl border border-slate-edge p-6 glass-card">
      <div className="flex items-center justify-between">
        <span className="font-mono text-label-mono uppercase tracking-widest text-secondary">{label}</span>
        <span className="font-mono text-caption text-mercury">{note}</span>
      </div>
      <div className="group flex items-center justify-between rounded-[6px] border border-slate-edge bg-black/40 px-4 py-3">
        <code className="font-mono text-body-sm text-phosphor">
          <span className="text-fog">$ </span>
          {command}
        </code>
        <button
          onClick={copy}
          aria-label="Copy command"
          className="text-mercury transition-colors hover:text-snow"
        >
          {copied ? <Check className="h-4 w-4 text-phosphor" strokeWidth={2} /> : <Copy className="h-4 w-4" strokeWidth={2} />}
        </button>
      </div>
    </div>
  );
}
