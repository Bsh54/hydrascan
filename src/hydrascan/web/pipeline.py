"""Shared scan pipeline used by the API and the GitHub bot."""

from __future__ import annotations

from ..depsdev import resolve_from_package_json
from ..lockfile import parse_lockfile_data
from ..maintainers import analyze_ownership
from ..models import DependencyGraph
from ..pypi import resolve_from_requirements
from ..service import scan_graph
from ..temporal import temporal_windows
from ..typosquat import detect_typosquats
from .github import fetch_lockfile, fetch_manifest, fetch_requirements
from .serialize import serialize_scan


class ScanInputError(ValueError):
    """No usable input was provided."""


def build_graph(
    *,
    repo_url: str | None = None,
    lockfile: dict | None = None,
    requirements: str | None = None,
    ref: str | None = None,
    token: str | None = None,
) -> tuple[DependencyGraph, str, str]:
    if lockfile is not None:
        return parse_lockfile_data(lockfile), "lockfile", "npm"
    if requirements is not None:
        return resolve_from_requirements(requirements), "deps.dev", "PyPI"
    if not repo_url:
        raise ScanInputError("provide repoUrl, lockfile, or requirements")

    lock = fetch_lockfile(repo_url, ref=ref, token=token)
    if lock is not None:
        return parse_lockfile_data(lock), "lockfile", "npm"

    reqs = fetch_requirements(repo_url, ref=ref, token=token)
    if reqs is not None:
        return resolve_from_requirements(reqs), "deps.dev", "PyPI"

    return resolve_from_package_json(fetch_manifest(repo_url, ref=ref, token=token)), "deps.dev", "npm"


def run_scan(
    *,
    repo_url: str | None = None,
    lockfile: dict | None = None,
    requirements: str | None = None,
    ref: str | None = None,
    token: str | None = None,
) -> dict:
    graph, source, ecosystem = build_graph(
        repo_url=repo_url, lockfile=lockfile, requirements=requirements, ref=ref, token=token
    )
    result = scan_graph(graph, ecosystem=ecosystem)

    payload = serialize_scan(result, ecosystem)
    payload["source"] = source
    payload["ecosystem"] = ecosystem
    payload["engine"] = result.engine

    # Temporal layer: attach each reachable threat's window (when it was
    # disclosed, whether a patch exists, and how long it has been live).
    windows = temporal_windows(result, ecosystem)
    for entry in payload["compromised"] + payload["vulnerable"]:
        entry["temporal"] = windows.get(entry["coordinate"])
    payload["unpatchedThreats"] = sum(
        1 for w in windows.values() if not w["patched"]
    )

    # Shared-maintainer / infrastructure analysis is the worm signal: it only
    # makes sense for genuinely malicious packages, not ordinary CVEs.
    malware = [
        result.graph.packages[node_id].coordinate for node_id in result.report.malware
    ]
    if ecosystem == "npm":
        payload["typosquats"] = detect_typosquats(
            [pkg.name for pkg in result.graph.packages.values()]
        )
        ownership = analyze_ownership(malware)
        payload["sharedMaintainers"] = ownership["maintainers"]
        payload["sharedInfrastructure"] = ownership["infrastructure"]
    else:
        payload["typosquats"] = []
        payload["sharedMaintainers"] = []
        payload["sharedInfrastructure"] = []
    return payload
