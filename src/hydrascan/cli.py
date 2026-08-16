"""Command-line interface: scan a repository and print the fixes.

By default the CLI talks to a hosted HydraScan API, so no local setup is needed:

    hydrascan sindresorhus/got
    hydrascan https://github.com/expressjs/express
    hydrascan ./package-lock.json

Point it at your own instance with ``--api`` or ``HYDRASCAN_API_URL``.

Exit codes: 0 = no reachable compromise, 1 = compromised dependencies found,
2 = error. This lets you gate CI with ``hydrascan <repo> || exit 1``.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import httpx
import typer

_HELP = """Graph-native supply-chain blast-radius analysis, powered by HydraDB.

Scan an npm or PyPI project and see which of your dependencies are compromised
and reachable, with the exact command to fix each one.

Examples:
  hydrascan sindresorhus/got          scan a GitHub repo (owner/repo)
  hydrascan https://github.com/x/y    scan a GitHub repo (full URL)
  hydrascan ./package-lock.json       scan a local npm lockfile
  hydrascan --json                    machine-readable output for CI

Exit codes: 0 = clean, 1 = compromised dependency reachable, 2 = error.
"""

app = typer.Typer(add_completion=False, help=_HELP)

_DEFAULT_API = "https://hydrascan.shadrakbessanh.me"
_SHORTHAND = re.compile(r"^[\w.-]+/[\w.-]+$")

_RISK = [(90, "Critical"), (70, "High"), (40, "Moderate"), (1, "Low")]


@app.command()
def scan(
    target: str = typer.Argument(
        ...,
        help="A GitHub repo URL, an owner/repo shorthand, or a path to a lockfile.",
    ),
    api: str = typer.Option(
        "", "--api", help="Base URL of the HydraScan API (or set HYDRASCAN_API_URL)."
    ),
    as_json: bool = typer.Option(
        False, "--json", help="Emit the raw JSON result for CI and automation."
    ),
) -> None:
    """Scan an npm or PyPI project for reachable compromised dependencies.

    Examples:

      hydrascan sindresorhus/got          scan a GitHub repo (owner/repo)

      hydrascan https://github.com/x/y    scan a GitHub repo (full URL)

      hydrascan ./package-lock.json       scan a local npm lockfile

      hydrascan chalk/chalk --json        machine-readable output for CI

    Exit codes: 0 = clean, 1 = compromised dependency reachable, 2 = error.
    """
    base = (api or os.environ.get("HYDRASCAN_API_URL") or _DEFAULT_API).rstrip("/")

    try:
        response = httpx.post(f"{base}/api/scan", json=_payload(target), timeout=180.0)
    except httpx.HTTPError as exc:
        typer.secho(f"error: cannot reach {base} ({exc})", fg=typer.colors.RED, err=True)
        raise typer.Exit(2) from exc

    if response.status_code != 200:
        detail = response.json().get("detail", response.text)
        typer.secho(f"error: {detail}", fg=typer.colors.RED, err=True)
        raise typer.Exit(2)

    data = response.json()
    if as_json:
        typer.echo(json.dumps(data, indent=2))
    else:
        _render(data)

    # Non-zero only on real compromise (reachable malware), so CI blocks on the
    # thing that actually runs code, not on every transitive CVE.
    raise typer.Exit(1 if data.get("isCompromised") else 0)


def _payload(target: str) -> dict:
    path = Path(target)
    if path.is_file():
        return {"lockfile": json.loads(path.read_text(encoding="utf-8"))}
    if _SHORTHAND.match(target) and "github.com" not in target:
        return {"repoUrl": f"https://github.com/{target}"}
    return {"repoUrl": target}


def _render(data: dict) -> None:
    score = data.get("exposureScore", 0)
    color = typer.colors.RED if score >= 70 else typer.colors.YELLOW if score else typer.colors.GREEN

    typer.echo()
    typer.secho(f"  {data.get('project', 'project')}", bold=True)
    typer.secho(
        f"  {data.get('totalPackages', 0)} packages  |  {data.get('ecosystem', 'npm')}  |  "
        f"engine: {data.get('engine', 'local')}",
        fg=typer.colors.BRIGHT_BLACK,
    )
    typer.echo()
    typer.secho(f"  Exposure score: {score}/100  ({_risk(score)})", fg=color, bold=True)

    fixes = data.get("remediation", [])
    malware = [f for f in fixes if f.get("kind") == "malware"]
    cves = [f for f in fixes if f.get("kind") != "malware"]

    temporal = {
        e["coordinate"]: e["temporal"]
        for e in data.get("compromised", []) + data.get("vulnerable", [])
        if e.get("temporal")
    }

    if not fixes:
        typer.echo()
        typer.secho("  No reachable compromised or vulnerable dependencies.", fg=typer.colors.GREEN)
        typer.echo()
        return

    if malware:
        _section("Compromised - malicious packages reachable", malware, typer.colors.RED, temporal)
    if cves:
        _section("Known vulnerabilities reachable", cves, typer.colors.YELLOW, temporal)
    typer.echo()


def _section(title: str, fixes: list[dict], color: str, temporal: dict) -> None:
    width = max(len(f["package"]) for f in fixes)
    typer.echo()
    typer.secho(f"  {title} ({len(fixes)}):", fg=color, bold=True)
    typer.echo()
    for fix in fixes:
        typer.echo("    ", nl=False)
        typer.secho(f"{fix['package']:<{width}}", fg=color, nl=False)
        typer.echo("   ->   ", nl=False)
        typer.secho(fix["command"], fg=typer.colors.GREEN)
        window = _window_line(temporal.get(fix["package"]))
        if window:
            typer.secho(f"    {' ' * width}        {window}", fg=typer.colors.BRIGHT_BLACK)


def _window_line(window: dict | None) -> str:
    if not window:
        return ""
    bits = []
    if window.get("disclosedAt"):
        days = window.get("daysSinceDisclosed")
        age = f" ({days}d ago)" if days is not None else ""
        bits.append(f"disclosed {window['disclosedAt']}{age}")
    bits.append("patch available" if window.get("patched") else "no patch yet")
    return "  |  ".join(bits)


def _risk(score: int) -> str:
    for threshold, label in _RISK:
        if score >= threshold:
            return label
    return "Safe"


if __name__ == "__main__":
    app()
