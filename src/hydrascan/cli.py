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

app = typer.Typer(add_completion=False, help="Graph-native supply-chain analysis.")

_DEFAULT_API = "https://hydrascan.shadrakbessanh.me"
_SHORTHAND = re.compile(r"^[\w.-]+/[\w.-]+$")

_RISK = [(90, "Critical"), (70, "High"), (40, "Moderate"), (1, "Low")]


@app.command()
def scan(
    target: str = typer.Argument(..., help="Repo URL, owner/repo, or a lockfile path."),
    api: str = typer.Option("", help="HydraScan API base URL."),
    as_json: bool = typer.Option(False, "--json", help="Emit raw JSON for CI/automation."),
) -> None:
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

    raise typer.Exit(1 if data.get("isExposed") else 0)


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
    if not fixes:
        typer.echo()
        typer.secho("  No reachable compromised dependencies.", fg=typer.colors.GREEN)
        typer.echo()
        return

    width = max(len(f["package"]) for f in fixes)
    typer.echo()
    plural = "y" if len(fixes) == 1 else "ies"
    typer.secho(f"  Fixes ({len(fixes)} compromised dependenc{plural}):", fg=typer.colors.RED, bold=True)
    typer.echo()
    for fix in fixes:
        typer.echo("    ", nl=False)
        typer.secho(f"{fix['package']:<{width}}", fg=typer.colors.RED, nl=False)
        typer.echo("   ->   ", nl=False)
        typer.secho(fix["command"], fg=typer.colors.GREEN)
    typer.echo()


def _risk(score: int) -> str:
    for threshold, label in _RISK:
        if score >= threshold:
            return label
    return "Safe"


if __name__ == "__main__":
    app()
