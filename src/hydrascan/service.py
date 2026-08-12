"""High-level scan orchestration shared by the CLI and the web backend."""

from __future__ import annotations

from dataclasses import dataclass

from .analysis import compute_blast_radius
from .hydra_engine import HydraEngine, HydraEngineError
from .models import Advisory, BlastRadiusReport, DependencyGraph
from .osv import find_advisories


@dataclass(slots=True)
class ScanResult:
    graph: DependencyGraph
    advisories: dict[tuple[str, str], list[Advisory]]
    report: BlastRadiusReport
    engine: str


def scan_graph(graph: DependencyGraph, *, ecosystem: str = "npm") -> ScanResult:
    """Enrich a dependency graph with advisories and compute its blast radius.

    Reachability is computed by the HydraDB graph engine when reachable, which
    stores the graph and returns attack paths from its native path procedure.
    A local traversal is used as a fallback so the tool always produces a result.
    """
    coordinates = {(p.name, p.version) for p in graph.packages.values()}
    advisories = find_advisories(coordinates, ecosystem=ecosystem)

    try:
        report = HydraEngine().compute_blast_radius(graph, advisories)
        engine = "hydradb"
    except HydraEngineError:
        report = compute_blast_radius(graph, advisories)
        engine = "local"

    return ScanResult(graph=graph, advisories=advisories, report=report, engine=engine)
