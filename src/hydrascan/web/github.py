"""Fetch a public repository's ``package-lock.json`` from GitHub."""

from __future__ import annotations

import json
import re
from typing import Any

import httpx

_REPO_RE = re.compile(r"github\.com[/:]([\w.-]+)/([\w.-]+?)(?:\.git)?/?$")
_RAW = "https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{file}"
_CONTENTS = "https://api.github.com/repos/{owner}/{repo}/contents/{file}"
_DEFAULT_REFS = ("main", "master")


class RepositoryError(ValueError):
    """Raised when a repository URL is invalid or has no usable manifest."""


def fetch_lockfile(
    repo_url: str, *, ref: str | None = None, token: str | None = None, client: httpx.Client | None = None
) -> dict[str, Any] | None:
    """Return the repository's package-lock.json, or None if it has none."""
    text = _fetch(repo_url, "package-lock.json", ref, token, client)
    return json.loads(text) if text is not None else None


def fetch_manifest(
    repo_url: str, *, ref: str | None = None, token: str | None = None, client: httpx.Client | None = None
) -> dict[str, Any]:
    """Return the repository's package.json, raising if it has none."""
    text = _fetch(repo_url, "package.json", ref, token, client)
    if text is None:
        owner, repo = _parse_repo(repo_url)
        raise RepositoryError(f"no package.json found in {owner}/{repo}")
    return json.loads(text)


def fetch_requirements(
    repo_url: str, *, ref: str | None = None, token: str | None = None, client: httpx.Client | None = None
) -> str | None:
    """Return the repository's requirements.txt, or None if it has none."""
    return _fetch(repo_url, "requirements.txt", ref, token, client)


def _fetch(
    repo_url: str, file: str, ref: str | None, token: str | None, client: httpx.Client | None
) -> str | None:
    owner, repo = _parse_repo(repo_url)
    refs = (ref, *_DEFAULT_REFS) if ref else _DEFAULT_REFS
    owned = client is None
    http = client or httpx.Client(timeout=30.0, follow_redirects=True)
    try:
        for candidate in refs:
            if token:
                response = http.get(
                    _CONTENTS.format(owner=owner, repo=repo, file=file),
                    params={"ref": candidate},
                    headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.raw"},
                )
            else:
                response = http.get(_RAW.format(owner=owner, repo=repo, ref=candidate, file=file))
            if response.status_code == 200:
                return response.text
        return None
    finally:
        if owned:
            http.close()


def _parse_repo(repo_url: str) -> tuple[str, str]:
    match = _REPO_RE.search(repo_url.strip())
    if not match:
        raise RepositoryError(f"not a valid GitHub repository URL: {repo_url!r}")
    return match.group(1), match.group(2)
