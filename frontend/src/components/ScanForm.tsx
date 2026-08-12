import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Link2, Radar, Loader2 } from "lucide-react";
import { scanRepository } from "../lib/api";
import { ScanLoading } from "./ScanLoading";

export function ScanForm() {
  const navigate = useNavigate();
  const [repoUrl, setRepoUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    if (!repoUrl.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const result = await scanRepository(repoUrl.trim());
      navigate("/dashboard", { state: result });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Scan failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      {loading && <ScanLoading />}
    <div className="relative z-20 flex w-full max-w-3xl flex-col items-center gap-xs md:flex-row">
      <div className="relative w-full flex-grow">
        <Link2 className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-mercury" strokeWidth={2} />
        <input
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          placeholder="https://github.com/your-org/your-repo"
          className="w-full rounded-[6px] border border-slate-edge bg-obsidian py-4 pl-12 pr-4 font-mono text-label-mono text-snow placeholder-mercury shadow-inner transition-all focus:border-phosphor focus:outline-none focus:ring-1 focus:ring-phosphor"
        />
      </div>
      <button
        onClick={submit}
        disabled={loading}
        className="flex w-full items-center justify-center gap-xs whitespace-nowrap rounded-[6px] bg-terminal-green px-8 py-4 font-mono text-label-mono font-bold text-snow transition-all hover:bg-opacity-90 disabled:cursor-not-allowed disabled:opacity-60 md:w-auto"
      >
        {loading ? "Scanning..." : "Scan Repository"}
        {loading ? (
          <Loader2 className="h-[18px] w-[18px] animate-spin" strokeWidth={2} />
        ) : (
          <Radar className="h-[18px] w-[18px]" strokeWidth={2} />
        )}
      </button>
      {error && (
        <p className="absolute -bottom-7 left-0 font-mono text-label-mono text-danger">{error}</p>
      )}
    </div>
    </>
  );
}
