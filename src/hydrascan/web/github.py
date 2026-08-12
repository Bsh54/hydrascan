"""Fetch a public repository's ``package-lock.json`` from GitHub."""

from __future__ import annotations

import re
from typing import Any

import httpx

_REPO_RE = re.compile(r"github\.com[/:]([\w.-]+)/([\w.-]+?)(?:\.git)?/?$")
_RAW = "https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{file}"
_DEFAULT_REFS = ("main", "master")


class RepositoryError(ValueError):
    """Raised when a repository URL is invalid or has no usable manifest."""


def fetch_lockfile(repo_url: str, *, client: httpx.Client | None = None) -> dict[str, Any] | None:
    """Return the repository's package-lock.json, or None if it has none."""
    return _fetch_json(repo_url, "package-lock.json", client=client)


def fetch_manifest(repo_url: str, *, client: httpx.Client | None = None) -> dict[str, Any]:
    """Return the repository's package.json, raising if it has none."""
    manifest = _fetch_json(repo_url, "package.json", client=client)
    if manifest is None:
        owner, repo = _parse_repo(repo_url)
        raise RepositoryError(f"no package.json found in {owner}/{repo}")
    return manifest


def fetch_requirements(repo_url: str, *, client: httpx.Client | None = None) -> str | None:
    """Return the repository's requirements.txt, or None if it has none."""
    return _fetch_text(repo_url, "requirements.txt", client=client)


def _fetch_text(repo_url: str, file: str, *, client: httpx.Client | None) -> str | None:
    owner, repo = _parse_repo(repo_url)
    owned = client is None
    http = client or httpx.Client(timeout=30.0, follow_redirects=True)
    try:
        for ref in _DEFAULT_REFS:
            response = http.get(_RAW.format(owner=owner, repo=repo, ref=ref, file=file))
            if response.status_code == 200:
                return response.text
        return None
    finally:
        if owned:
            http.close()


def _fetch_json(
    repo_url: str, file: str, *, client: httpx.Client | None
) -> dict[str, Any] | None:
    owner, repo = _parse_repo(repo_url)
    owned = client is None
    http = client or httpx.Client(timeout=30.0, follow_redirects=True)
    try:
        for ref in _DEFAULT_REFS:
            response = http.get(_RAW.format(owner=owner, repo=repo, ref=ref, file=file))
            if response.status_code == 200:
                return response.json()
        return None
    finally:
        if owned:
            http.close()


def _parse_repo(repo_url: str) -> tuple[str, str]:
    match = _REPO_RE.search(repo_url.strip())
    if not match:
        raise RepositoryError(f"not a valid GitHub repository URL: {repo_url!r}")
    return match.group(1), match.group(2)
