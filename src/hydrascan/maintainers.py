"""Group compromised packages by shared maintainer or shared infrastructure.

Worm-style supply-chain attacks (keyv, Shai-Hulud) hijack a single maintainer
account and republish every package that account controls. Surfacing the shared
maintainer — or the shared source repository they all publish from — makes that
blast radius obvious: many compromised packages, one owner.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor

import httpx

_REGISTRY = "https://registry.npmjs.org/{name}"
_WORKERS = 8


def analyze_ownership(
    packages: Iterable[str],
    *,
    client: httpx.Client | None = None,
) -> dict[str, list[dict[str, object]]]:
    """Return maintainers and source repositories shared by multiple packages."""
    names = sorted({_name(p) for p in packages if p})
    if not names:
        return {"maintainers": [], "infrastructure": []}

    owned = client is None
    http = client or httpx.Client(timeout=20.0)
    try:
        with ThreadPoolExecutor(max_workers=_WORKERS) as pool:
            metadata = list(pool.map(lambda n: (n, _metadata(http, n)), names))
    finally:
        if owned:
            http.close()

    by_maintainer: dict[str, set[str]] = defaultdict(set)
    by_repo: dict[str, set[str]] = defaultdict(set)
    for name, (maintainers, repo) in metadata:
        for maintainer in maintainers:
            by_maintainer[maintainer].add(name)
        if repo:
            by_repo[repo].add(name)

    return {
        "maintainers": _shared(by_maintainer, "maintainer"),
        "infrastructure": _shared(by_repo, "repository"),
    }


def _shared(groups: dict[str, set[str]], key: str) -> list[dict[str, object]]:
    result = [
        {key: value, "packages": sorted(pkgs)}
        for value, pkgs in groups.items()
        if len(pkgs) > 1
    ]
    result.sort(key=lambda entry: len(entry["packages"]), reverse=True)  # type: ignore[arg-type]
    return result


def _name(coordinate: str) -> str:
    return coordinate.rpartition("@")[0] or coordinate


def _metadata(http: httpx.Client, name: str) -> tuple[list[str], str]:
    try:
        response = http.get(_REGISTRY.format(name=name))
        if response.status_code != 200:
            return [], ""
        data = response.json()
        maintainers = [m.get("name", "") for m in data.get("maintainers", []) if m.get("name")]
        repo = _repository(data)
        return maintainers, repo
    except (httpx.HTTPError, ValueError):
        return [], ""


def _repository(data: dict) -> str:
    repo = data.get("repository")
    url = repo.get("url", "") if isinstance(repo, dict) else (repo or "")
    return url.replace("git+", "").replace(".git", "").replace("ssh://git@", "https://").strip()
