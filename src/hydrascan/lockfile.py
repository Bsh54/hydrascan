"""Parse an npm ``package-lock.json`` into a resolved dependency graph.

Supports lockfile versions 2 and 3, which both expose the flat ``packages``
map keyed by install path. Dependency edges are resolved with npm's nearest
``node_modules`` lookup so that nested versions are attributed correctly.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import DependencyGraph, Package


class LockfileError(ValueError):
    """Raised when a lockfile is missing, malformed, or unsupported."""


def parse_lockfile(path: str | Path) -> DependencyGraph:
    return parse_lockfile_data(_load(path))


def parse_lockfile_data(data: dict[str, Any]) -> DependencyGraph:
    version = data.get("lockfileVersion")
    if version not in (2, 3):
        raise LockfileError(
            f"unsupported lockfileVersion {version!r}; regenerate with npm >= 7"
        )

    packages: dict[str, Any] = data.get("packages") or {}
    if "" not in packages:
        raise LockfileError("lockfile has no root package entry")

    root_entry = packages[""]
    root = Package(
        node_id="",
        name=root_entry.get("name") or data.get("name") or "root",
        version=root_entry.get("version") or data.get("version") or "0.0.0",
        is_root=True,
    )
    graph = DependencyGraph(root=root)
    graph.add_package(root)

    links = {
        node_id: entry["resolved"]
        for node_id, entry in packages.items()
        if entry.get("link") and entry.get("resolved")
    }

    for node_id, entry in packages.items():
        if node_id == "" or node_id in links:
            continue
        graph.add_package(
            Package(
                node_id=node_id,
                name=_name_from_path(node_id, entry),
                version=entry.get("version") or "0.0.0",
            )
        )

    seen_edges: set[tuple[str, str]] = set()

    def connect(source: str, target: str | None) -> None:
        target = links.get(target, target)
        if not target or target == source:
            return
        if source not in graph.packages or target not in graph.packages:
            return
        if (source, target) not in seen_edges:
            seen_edges.add((source, target))
            graph.add_edge(source, target)

    for node_id, entry in packages.items():
        source = links.get(node_id, node_id)
        for dep_name in _declared_dependencies(entry, node_id):
            connect(source, _resolve(node_id, dep_name, packages))

    # Workspace links have no declared edge from the root; connect the owner of
    # each linked node_modules entry to the workspace package it points to.
    for link_id, target in links.items():
        connect(_owner(link_id), target)

    return graph


def _load(path: str | Path) -> dict[str, Any]:
    file = Path(path)
    if not file.is_file():
        raise LockfileError(f"lockfile not found: {file}")
    try:
        return json.loads(file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise LockfileError(f"invalid JSON in {file}: {exc}") from exc


def _declared_dependencies(entry: dict[str, Any], node_id: str) -> set[str]:
    names: set[str] = set()
    for key in ("dependencies", "optionalDependencies", "peerDependencies"):
        names.update((entry.get(key) or {}).keys())
    # devDependencies are installed for the root project and its workspaces, but
    # not for transitive packages under node_modules.
    if "node_modules" not in node_id:
        names.update((entry.get("devDependencies") or {}).keys())
    return names


def _name_from_path(node_id: str, entry: dict[str, Any]) -> str:
    if entry.get("name"):
        return entry["name"]
    marker = "node_modules/"
    index = node_id.rfind(marker)
    if index != -1:
        return node_id[index + len(marker) :]
    return node_id.rsplit("/", 1)[-1]


def _owner(node_id: str) -> str:
    marker = "/node_modules/"
    cut = node_id.rfind(marker)
    if cut != -1:
        return node_id[:cut]
    return "" if node_id.startswith("node_modules/") else node_id


def _resolve(requirer: str, dep_name: str, packages: dict[str, Any]) -> str | None:
    """Find the install path that satisfies ``dep_name`` for ``requirer``.

    Mirrors Node resolution: look under the requirer's own ``node_modules``,
    then walk up each parent scope until a matching entry is found.
    """
    prefix = requirer
    while True:
        candidate = f"{prefix}/node_modules/{dep_name}" if prefix else f"node_modules/{dep_name}"
        if candidate in packages:
            return candidate
        if not prefix:
            return None
        cut = prefix.rfind("/node_modules/")
        prefix = prefix[:cut] if cut != -1 else ""
