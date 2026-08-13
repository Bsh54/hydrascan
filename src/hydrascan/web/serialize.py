"""Serialize scan results into the JSON shape consumed by the frontend.

Reachable advisory-bearing packages are split into two honest categories:
``compromised`` (malicious-package advisories — real supply-chain compromise) and
``vulnerable`` (ordinary CVE/GHSA advisories).
"""

from __future__ import annotations

from typing import Any

from ..models import Advisory
from ..service import ScanResult


def serialize_scan(result: ScanResult, ecosystem: str = "npm") -> dict[str, Any]:
    graph, report = result.graph, result.report

    malware_coords = {graph.packages[n].coordinate for n in report.malware}
    vulnerable_coords = {graph.packages[n].coordinate for n in report.vulnerable}

    nodes = [
        {
            "id": pkg.coordinate,
            "name": pkg.name,
            "version": pkg.version,
            "type": "application" if pkg.is_root else "package",
            "compromised": pkg.coordinate in malware_coords,
            "vulnerable": pkg.coordinate in vulnerable_coords,
        }
        for pkg in _unique_by_coordinate(result)
    ]

    edges = [
        {
            "source": graph.packages[edge.requirer].coordinate,
            "target": graph.packages[edge.dependency].coordinate,
        }
        for edge in graph.edges
    ]

    return {
        "project": graph.root.coordinate,
        "totalPackages": report.total_packages,
        "isExposed": report.is_exposed,
        "isCompromised": report.has_malware,
        "exposureScore": report.exposure_score,
        "compromised": _serialize_affected(result, report.malware),
        "vulnerable": _serialize_affected(result, report.vulnerable),
        "paths": [
            {
                "nodes": [p.coordinate for p in path.nodes],
                "advisory": _serialize_advisory(path.advisory),
                "malicious": path.advisory.is_malicious,
            }
            for path in report.paths
        ],
        "remediation": _serialize_remediation(result, ecosystem),
        "nodes": nodes,
        "edges": edges,
    }


def _unique_by_coordinate(result: ScanResult) -> list:
    seen: dict[str, Any] = {}
    for pkg in result.graph.packages.values():
        seen.setdefault(pkg.coordinate, pkg)
    return list(seen.values())


def _serialize_affected(
    result: ScanResult, group: dict[str, list[Advisory]]
) -> list[dict[str, Any]]:
    out = []
    for node_id, advisories in group.items():
        pkg = result.graph.packages[node_id]
        out.append(
            {
                "coordinate": pkg.coordinate,
                "advisories": [_serialize_advisory(a) for a in advisories],
            }
        )
    return out


def _serialize_remediation(result: ScanResult, ecosystem: str) -> list[dict[str, Any]]:
    introduced_by = _introduced_by(result)
    out = []
    for node_id, advisories in result.report.affected.items():
        pkg = result.graph.packages[node_id]
        malicious = any(a.is_malicious for a in advisories)
        fixed = next((a.fixed_version for a in advisories if a.fixed_version), None)
        out.append(
            {
                "package": pkg.coordinate,
                "kind": "malware" if malicious else "cve",
                "introducedBy": introduced_by.get(pkg.coordinate),
                "fixedVersion": fixed,
                "command": _fix_command(ecosystem, pkg.name, fixed, malicious),
            }
        )
    return out


def _fix_command(ecosystem: str, name: str, fixed: str | None, malicious: bool) -> str:
    # Malware has no safe version to move to — remove it outright.
    if malicious:
        return f"pip uninstall {name}" if ecosystem == "PyPI" else f"npm uninstall {name}"
    if ecosystem == "PyPI":
        return f"pip install {name}=={fixed}" if fixed else f"pip uninstall {name}"
    return f"npm install {name}@{fixed}" if fixed else f"npm uninstall {name}"


def _introduced_by(result: ScanResult) -> dict[str, str]:
    """Map each affected coordinate to the direct dependency that pulls it in."""
    mapping: dict[str, str] = {}
    for path in result.report.paths:
        if len(path.nodes) >= 2:
            mapping.setdefault(path.nodes[-1].coordinate, path.nodes[1].coordinate)
    return mapping


def _serialize_advisory(advisory) -> dict[str, Any]:
    return {
        "id": advisory.id,
        "summary": advisory.summary,
        "severity": advisory.severity,
        "isMalicious": advisory.is_malicious,
        "published": advisory.published,
        "fixedVersion": advisory.fixed_version,
    }
