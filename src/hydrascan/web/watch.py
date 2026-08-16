"""Scheduled watch: re-scan every installed repository and open an issue the
moment a dependency it already trusts becomes a reachable compromise.

Dependabot tells you when a fix becomes available. This answers the sharper
supply-chain question: a package you installed while it was clean can be hijacked
days later (the keyv / Shai-Hulud pattern). The watch re-computes the blast radius
on a timer and, if a compromised package is now reachable in the graph, opens a
single GitHub issue with the exact path and fix. It closes the issue once the
threat is gone. Run on a timer:

    python -m hydrascan.web.watch
"""

from __future__ import annotations

import httpx

from .bot import _ACCEPT, _API, _app_jwt, _installation_token, _render_comment
from .pipeline import run_scan

_MARKER = "<!-- hydrascan-watch -->"
_TITLE = "HydraScan: a reachable dependency has become compromised"
_INTRO = (
    "A package already in this repository's dependency graph is now flagged as "
    "compromised and is **reachable** from your project. It was likely fine when "
    "you installed it and was hijacked later.\n\n"
)


def run_watch() -> None:
    for installation_id in _installations():
        token = _installation_token(installation_id)
        for repo in _repos(token):
            try:
                _check_repo(repo, token)
            except Exception as exc:  # noqa: BLE001 - one bad repo must not stop the run
                print(f"[watch] {repo}: {exc}")


def _check_repo(repo: str, token: str) -> None:
    result = run_scan(repo_url=f"https://github.com/{repo}", token=token)
    malware = result.get("compromised", [])
    existing = _open_issue(repo, token)

    if malware and existing is None:
        body = _MARKER + "\n\n" + _INTRO + _render_comment(result)
        _create_issue(repo, token, body)
        print(f"[watch] {repo}: opened issue ({len(malware)} compromised)")
    elif not malware and existing is not None:
        _close_issue(repo, token, existing)
        print(f"[watch] {repo}: threat cleared, closed issue #{existing}")


def _installations() -> list[int]:
    response = httpx.get(
        f"{_API}/app/installations",
        headers={"Authorization": f"Bearer {_app_jwt()}", "Accept": _ACCEPT},
        timeout=20.0,
    )
    response.raise_for_status()
    return [item["id"] for item in response.json()]


def _repos(token: str) -> list[str]:
    response = httpx.get(
        f"{_API}/installation/repositories",
        headers={"Authorization": f"Bearer {token}", "Accept": _ACCEPT},
        params={"per_page": 100},
        timeout=20.0,
    )
    response.raise_for_status()
    return [r["full_name"] for r in response.json().get("repositories", [])]


def _open_issue(repo: str, token: str) -> int | None:
    response = httpx.get(
        f"{_API}/repos/{repo}/issues",
        headers={"Authorization": f"Bearer {token}", "Accept": _ACCEPT},
        params={"state": "open", "per_page": 100},
        timeout=20.0,
    )
    response.raise_for_status()
    for issue in response.json():
        if _MARKER in (issue.get("body") or ""):
            return issue["number"]
    return None


def _create_issue(repo: str, token: str, body: str) -> None:
    response = httpx.post(
        f"{_API}/repos/{repo}/issues",
        headers={"Authorization": f"Bearer {token}", "Accept": _ACCEPT},
        json={"title": _TITLE, "body": body},
        timeout=20.0,
    )
    response.raise_for_status()


def _close_issue(repo: str, token: str, number: int) -> None:
    headers = {"Authorization": f"Bearer {token}", "Accept": _ACCEPT}
    httpx.post(
        f"{_API}/repos/{repo}/issues/{number}/comments",
        headers=headers,
        json={"body": _MARKER + "\n\nThe reachable compromised dependency is gone. Closing. ✅"},
        timeout=20.0,
    )
    httpx.patch(
        f"{_API}/repos/{repo}/issues/{number}",
        headers=headers,
        json={"state": "closed"},
        timeout=20.0,
    )


if __name__ == "__main__":
    run_watch()
