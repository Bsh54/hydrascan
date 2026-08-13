#!/usr/bin/env node
import { readFileSync, existsSync } from "node:fs";

const API = (process.env.HYDRASCAN_API_URL || "https://hydrascan.shadrakbessanh.me").replace(/\/$/, "");
const RISK = [[90, "Critical"], [70, "High"], [40, "Moderate"], [1, "Low"]];

const c = {
  red: (s) => `\x1b[31m${s}\x1b[0m`,
  green: (s) => `\x1b[32m${s}\x1b[0m`,
  yellow: (s) => `\x1b[33m${s}\x1b[0m`,
  dim: (s) => `\x1b[90m${s}\x1b[0m`,
  bold: (s) => `\x1b[1m${s}\x1b[0m`,
};

function usage() {
  console.error("usage: hydrascan [target] [--json]   (run --help for details)");
  process.exitCode = 2;
}

function help() {
  console.log(`
${c.bold("hydrascan")} — graph-native supply-chain blast-radius analysis, powered by HydraDB.

Scan an npm or PyPI project and see which dependencies are compromised and
reachable, with the exact command to fix each one.

${c.bold("Usage")}
  hydrascan [target] [options]

${c.bold("Target")} (optional — omit to scan the current directory)
  owner/repo                 a GitHub repository shorthand
  https://github.com/x/y     a full GitHub repository URL
  ./package-lock.json        a local npm lockfile
  (none)                     scan package-lock.json and requirements.txt here

${c.bold("Options")}
  --json                     emit the raw JSON result for CI and automation
  -h, --help                 show this help

${c.bold("Examples")}
  npx hydrascan sindresorhus/got
  npx hydrascan https://github.com/expressjs/express
  npx hydrascan --json
  hydrascan chalk/chalk

${c.bold("Environment")}
  HYDRASCAN_API_URL          point at your own HydraScan instance

${c.bold("Exit codes")}
  0  clean          1  compromised dependency reachable          2  error
`);
}

function payload(target) {
  if (existsSync(target)) {
    return { lockfile: JSON.parse(readFileSync(target, "utf8")) };
  }
  if (/^[\w.-]+\/[\w.-]+$/.test(target) && !target.includes("github.com")) {
    return { repoUrl: `https://github.com/${target}` };
  }
  return { repoUrl: target };
}

function localTargets() {
  const targets = [];
  if (existsSync("package-lock.json")) {
    targets.push({ label: "npm (package-lock.json)", body: { lockfile: JSON.parse(readFileSync("package-lock.json", "utf8")) } });
  }
  if (existsSync("requirements.txt")) {
    targets.push({ label: "PyPI (requirements.txt)", body: { requirements: readFileSync("requirements.txt", "utf8") } });
  }
  return targets;
}

function risk(score) {
  for (const [threshold, label] of RISK) if (score >= threshold) return label;
  return "Safe";
}

function render(data) {
  const score = data.exposureScore ?? 0;
  const paint = score >= 70 ? c.red : score ? c.yellow : c.green;

  console.log();
  console.log("  " + c.bold(data.project ?? "project"));
  console.log("  " + c.dim(`${data.totalPackages ?? 0} packages  |  ${data.ecosystem ?? "npm"}  |  engine: ${data.engine ?? "local"}`));
  console.log();
  console.log("  " + paint(c.bold(`Exposure score: ${score}/100  (${risk(score)})`)));

  const fixes = data.remediation ?? [];
  if (fixes.length === 0) {
    console.log();
    console.log("  " + c.green("No reachable compromised dependencies."));
    console.log();
    return;
  }

  const width = Math.max(...fixes.map((f) => f.package.length));
  console.log();
  console.log("  " + c.red(c.bold(`Fixes (${fixes.length} compromised ${fixes.length === 1 ? "dependency" : "dependencies"}):`)));
  console.log();
  for (const fix of fixes) {
    console.log("    " + c.red(fix.package.padEnd(width)) + "   ->   " + c.green(fix.command));
  }
  console.log();
}

async function run(body) {
  const response = await fetch(`${API}/api/scan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail ?? response.statusText);
  }
  return data;
}

async function main() {
  const args = process.argv.slice(2);
  if (args.includes("--help") || args.includes("-h")) {
    help();
    return;
  }
  const asJson = args.includes("--json");
  const target = args.find((a) => !a.startsWith("-"));

  const jobs = target
    ? [{ label: null, body: payload(target) }]
    : localTargets();

  if (jobs.length === 0) {
    console.error(c.red("error: no package-lock.json or requirements.txt in the current directory."));
    usage();
    return;
  }

  const results = [];
  for (const job of jobs) {
    try {
      const data = await run(job.body);
      results.push(data);
      if (asJson) {
        console.log(JSON.stringify(data, null, 2));
      } else {
        if (job.label) console.log("\n" + c.dim(`── ${job.label} ──`));
        render(data);
      }
    } catch (err) {
      console.error(c.red(`error: ${err.message}`));
      process.exitCode = 2;
      return;
    }
  }

  process.exitCode = results.some((r) => r.isExposed) ? 1 : 0;
}

main();
