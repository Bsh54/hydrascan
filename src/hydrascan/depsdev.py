"""Resolve a full transitive dependency graph without a lockfile.

When a repository ships no ``package-lock.json`` we reconstruct the tree from
its ``package.json``: direct requirements are resolved to concrete versions via
the npm registry, then each is expanded using deps.dev's precomputed transitive
dependency graph. The result is lockfile-equivalent for analysis purposes.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any

import httpx

from .models import DependencyGraph, Package
from .semver import max_satisfying

_WORKERS = 12

_REGISTRY = "https://registry.npmjs.org/{name}"
_DEPSDEV = "https://api.deps.dev/v3/systems/npm/packages/{name}/versions/{version}:dependencies"
_DIRECT_FIELDS = ("dependencies", "devDependencies", "optionalDependencies")


class ResolutionError(ValueError):
    """Raised when a package.json cannot be resolved into a graph."""


def resolve_from_package_json(
    manifest: dict[str, Any],
    *,
    client: httpx.Client | None = None,
) -> DependencyGraph:
    direct = _direct_requirements(manifest)
    if not direct:
        raise ResolutionError("package.json declares no dependencies")

    owned = client is None
    http = client or httpx.Client(timeout=30.0, follow_redirects=True)
    try:
        root = Package(
            node_id="",
            name=manifest.get("name") or "root",
            version=manifest.get("version") or "0.0.0",
            is_root=True,
        )
        graph = DependencyGraph(root=root)
        graph.add_package(root)

        with ThreadPoolExecutor(max_workers=_WORKERS) as pool:
            subtrees = pool.map(
                lambda item: _resolve_subtree(http, *item), direct.items()
            )

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


def _resolve_subtree(
    http: httpx.Client, name: str, requirement: str
) -> tuple[str, str, dict[str, Any]] | None:
    version = _resolve_version(http, name, requirement)
    if version is None:
        return None
    response = http.get(_DEPSDEV.format(name=name, version=version))
    data = response.json() if response.status_code == 200 else {}
    return name, version, data


def _direct_requirements(manifest: dict[str, Any]) -> dict[str, str]:
    requirements: dict[str, str] = {}
    for field in _DIRECT_FIELDS:
        requirements.update(manifest.get(field) or {})
    return requirements


def version_published_at(http: httpx.Client, name: str, version: str) -> str | None:
    """Return the npm publish date (YYYY-MM-DD) of a specific package version."""
    response = http.get(_REGISTRY.format(name=name))
    if response.status_code != 200:
        return None
    stamp = (response.json().get("time") or {}).get(version)
    return stamp[:10] if stamp else None


def _resolve_version(http: httpx.Client, name: str, requirement: str) -> str | None:
    response = http.get(_REGISTRY.format(name=name))
    if response.status_code != 200:
        return None
    document = response.json()
    versions = list((document.get("versions") or {}).keys())
    latest = document.get("dist-tags", {}).get("latest")
    return max_satisfying(versions, requirement) or latest


def _merge_subtree(graph: DependencyGraph, data: dict[str, Any]) -> None:
    coordinates: list[str] = []
    for node in data.get("nodes", []):
        key = node.get("versionKey", {})
        coordinate = f"{key.get('name')}@{key.get('version')}"
        coordinates.append(coordinate)
        _ensure_package(graph, coordinate, key.get("name", ""), key.get("version", ""))
    for edge in data.get("edges", []):
        source = coordinates[edge["fromNode"]]
        target = coordinates[edge["toNode"]]
        if source != target:
            graph.add_edge(source, target)


def _ensure_package(graph: DependencyGraph, coordinate: str, name: str, version: str) -> None:
    if coordinate not in graph.packages:
        graph.add_package(Package(node_id=coordinate, name=name, version=version))
