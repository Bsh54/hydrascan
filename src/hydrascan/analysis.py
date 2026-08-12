"""Compute the blast radius: reachable attack paths from the root to compromised nodes."""

from __future__ import annotations

from .models import Advisory, AttackPath, BlastRadiusReport, DependencyGraph, Package

_MAX_PATHS_PER_TARGET = 8


def compute_blast_radius(
    graph: DependencyGraph,
    advisories: dict[tuple[str, str], list[Advisory]],
) -> BlastRadiusReport:
    """Given a graph and per-coordinate advisories, find every path root -> compromised."""
    compromised: dict[str, list[Advisory]] = {
        pkg.node_id: advisories[(pkg.name, pkg.version)]
        for pkg in graph.packages.values()
        if (pkg.name, pkg.version) in advisories
    }

    parents: dict[str, list[str]] = {}
    for edge in graph.edges:
        parents.setdefault(edge.dependency, []).append(edge.requirer)

    report = BlastRadiusReport(
        root=graph.root,
        compromised=compromised,
        total_packages=len(graph.packages),
    )
    for node_id, node_advisories in compromised.items():
        if not node_advisories:
            continue
        primary = _worst(node_advisories)
        for path in _paths_to_root(graph, parents, node_id):
            report.paths.append(AttackPath(nodes=path, advisory=primary))
    return report


def _worst(advisories: list[Advisory]) -> Advisory:
    order = {"CRITICAL": 0, "HIGH": 1, "MODERATE": 2, "LOW": 3, "UNKNOWN": 4}
    return min(advisories, key=lambda a: (not a.is_malicious, order.get(a.severity, 4)))


def _paths_to_root(
    graph: DependencyGraph,
    parents: dict[str, list[str]],
    target: str,
) -> list[list[Package]]:
    """Enumerate upward paths from ``target`` to the root, returned root-first."""
    paths: list[list[Package]] = []

    def climb(node_id: str, trail: list[str], seen: frozenset[str]) -> None:
        if len(paths) >= _MAX_PATHS_PER_TARGET:
            return
        if node_id == graph.root.node_id:
            paths.append([graph.packages[n] for n in reversed(trail + [node_id])])
            return
        for parent in parents.get(node_id, []):
            if parent not in seen:
                climb(parent, trail + [node_id], seen | {parent})

    climb(target, [], frozenset({target}))
    return paths
