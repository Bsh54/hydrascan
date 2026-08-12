"""Resolve a PyPI dependency graph from a requirements.txt via deps.dev.

Direct requirements are read from requirements.txt, resolved to concrete
versions (pinned or the registry default), then expanded with deps.dev's
precomputed transitive graph — mirroring the npm deps.dev path.
"""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import httpx

from .depsdev import ResolutionError, _ensure_package, _merge_subtree
from .models import DependencyGraph, Package

_WORKERS = 12
_VERSIONS = "https://api.deps.dev/v3/systems/pypi/packages/{name}"
_DEPSDEV = "https://api.deps.dev/v3/systems/pypi/packages/{name}/versions/{version}:dependencies"
_REQUIREMENT = re.compile(r"^\s*([A-Za-z0-9._-]+)\s*(?:==\s*([A-Za-z0-9.+!-]+))?")


def resolve_from_requirements(
    text: str,
    *,
    project_name: str = "project",
    client: httpx.Client | None = None,
) -> DependencyGraph:
    direct = _parse_requirements(text)
    if not direct:
        raise ResolutionError("requirements.txt declares no dependencies")

    owned = client is None
    http = client or httpx.Client(timeout=30.0, follow_redirects=True)
    try:
        root = Package(node_id="", name=project_name, version="0.0.0", is_root=True)
        graph = DependencyGraph(root=root)
        graph.add_package(root)

        with ThreadPoolExecutor(max_workers=_WORKERS) as pool:
            subtrees = pool.map(lambda item: _resolve_subtree(http, *item), direct.items())

        for resolved in subtrees:
            if resolved is None:
                continue
            name, version, data = resolved
            coordinate = f"{name}@{version}"
            _ensure_package(graph, coordinate, name, version)
            graph.add_edge("", coordinate)
            _merge_subtree(graph, data)
        return graph
    finally:
        if owned:
            http.close()


def _parse_requirements(text: str) -> dict[str, str | None]:
    direct: dict[str, str | None] = {}
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or line.startswith(("-", "git+", "http")):
            continue
        match = _REQUIREMENT.match(line)
        if match:
            direct[_normalize(match.group(1))] = match.group(2)
    return direct


def _normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _resolve_subtree(
    http: httpx.Client, name: str, pinned: str | None
) -> tuple[str, str, dict[str, Any]] | None:
    version = pinned or _default_version(http, name)
    if version is None:
        return None
    response = http.get(_DEPSDEV.format(name=name, version=version))
    data = response.json() if response.status_code == 200 else {}
    return name, version, data


def _default_version(http: httpx.Client, name: str) -> str | None:
    response = http.get(_VERSIONS.format(name=name))
    if response.status_code != 200:
        return None
    versions = response.json().get("versions", [])
    for entry in versions:
        if entry.get("isDefault"):
            return entry.get("versionKey", {}).get("version")
    return versions[-1].get("versionKey", {}).get("version") if versions else None
