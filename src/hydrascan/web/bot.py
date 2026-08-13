"""GitHub App webhook: scan pull requests and report the blast radius.

On each pull request the bot resolves the repository's dependency graph, computes
the reachable compromised set with HydraDB, posts a summary comment, and sets a
commit status so a compromised dependency blocks the merge.

Configuration (environment):
  GITHUB_APP_ID              the app id
  GITHUB_APP_PRIVATE_KEY     the PEM contents, or set GITHUB_APP_PRIVATE_KEY_FILE
  GITHUB_WEBHOOK_SECRET      the webhook signing secret
"""

from __future__ import annotations

import hashlib
import hmac
import os
import time

import httpx
import jwt
from fastapi import APIRouter, HTTPException, Request

from .pipeline import run_scan

router = APIRouter()

_API = "https://api.github.com"
_ACCEPT = "application/vnd.github+json"


@router.post("/api/github/webhook")
async def webhook(request: Request) -> dict[str, str]:
    body = await request.body()
    if not _verify_signature(request.headers.get("X-Hub-Signature-256"), body):
        raise HTTPException(status_code=401, detail="invalid signature")

    if request.headers.get("X-GitHub-Event") != "pull_request":
        return {"status": "ignored"}

    event = await request.json()
    if event.get("action") not in ("opened", "reopened", "synchronize"):
        return {"status": "ignored"}

    _handle_pull_request(event)
    return {"status": "processed"}


def _handle_pull_request(event: dict) -> None:
    installation_id = event["installation"]["id"]
    repo = event["repository"]["full_name"]
    pr = event["pull_request"]
    number = pr["number"]
    head_sha = pr["head"]["sha"]
    head_repo = pr["head"]["repo"]["full_name"]
    head_ref = pr["head"]["ref"]

    token = _installation_token(installation_id)
    _set_status(repo, head_sha, token, "pending", "Scanning dependencies...")

    try:
        result = run_scan(repo_url=f"{_API_HTML}/{head_repo}", ref=head_ref, token=token)
    except Exception as exc:  # noqa: BLE001 - report any failure back to the PR
        _set_status(repo, head_sha, token, "error", "Scan failed")
        _comment(repo, number, token, f"HydraScan could not scan this repository: `{exc}`")
        return

    compromised = result.get("compromised", [])
    _comment(repo, number, token, _render_comment(result))
    if compromised:
        _set_status(repo, head_sha, token, "failure", f"{len(compromised)} compromised dependencies reachable")
    else:
        _set_status(repo, head_sha, token, "success", "No reachable compromised dependencies")


def _render_comment(result: dict) -> str:
    compromised = result.get("compromised", [])
    score = result.get("exposureScore", 0)
    project = result.get("project", "project")
    header = f"### HydraScan — `{project}`\n\n**Exposure score: {score}/100**\n\n"

    if not compromised:
        return header + "No reachable compromised dependencies. ✅"

    fixes = {r["package"]: r for r in result.get("remediation", [])}
    lines = [
        header,
        f"{len(compromised)} compromised dependenc{'y' if len(compromised) == 1 else 'ies'} "
        "reachable from your project:\n",
        "| Dependency | Advisory | Fix |",
        "| --- | --- | --- |",
    ]
    for pkg in compromised:
        advisory = (pkg.get("advisories") or [{}])[0]
        fix = fixes.get(pkg["coordinate"], {}).get("command", "")
        lines.append(f"| `{pkg['coordinate']}` | {advisory.get('id', '')} | `{fix}` |")
    lines.append("\n_Blast radius computed by HydraDB._")
    return "\n".join(lines)


def _verify_signature(signature: str | None, body: bytes) -> bool:
    secret = os.environ.get("GITHUB_WEBHOOK_SECRET", "")
    if not secret:
        return True
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={digest}", signature or "")


def _app_jwt() -> str:
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + 540, "iss": os.environ["GITHUB_APP_ID"]}
    return jwt.encode(payload, _private_key(), algorithm="RS256")


def _private_key() -> str:
    key = os.environ.get("GITHUB_APP_PRIVATE_KEY")
    if key and "BEGIN" in key:
        return key.replace("\\n", "\n")
    path = os.environ.get("GITHUB_APP_PRIVATE_KEY_FILE")
    if path and os.path.isfile(path):
        return open(path, encoding="utf-8").read()
    raise RuntimeError("GitHub App private key is not configured")


def _installation_token(installation_id: int) -> str:
    response = httpx.post(
        f"{_API}/app/installations/{installation_id}/access_tokens",
        headers={"Authorization": f"Bearer {_app_jwt()}", "Accept": _ACCEPT},
        timeout=20.0,
    )
    response.raise_for_status()
    return response.json()["token"]


def _comment(repo: str, number: int, token: str, body: str) -> None:
    httpx.post(
        f"{_API}/repos/{repo}/issues/{number}/comments",
        headers={"Authorization": f"Bearer {token}", "Accept": _ACCEPT},
        json={"body": body},
        timeout=20.0,
    )


def _set_status(repo: str, sha: str, token: str, state: str, description: str) -> None:
    httpx.post(
        f"{_API}/repos/{repo}/statuses/{sha}",
        headers={"Authorization": f"Bearer {token}", "Accept": _ACCEPT},
        json={"state": state, "description": description[:140], "context": "HydraScan"},
        timeout=20.0,
    )


_API_HTML = "https://github.com"
