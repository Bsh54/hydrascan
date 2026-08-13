"""Client for the open-source HydraDB graph engine (OpenCypher over HTTP).

The dependency graph is written into HydraDB and the blast radius is computed by
HydraDB itself via its native shortest-path procedure. Each scan is assigned a
disjoint integer id range so concurrent scans never collide inside the shared
``default`` graph.

Set ``HYDRADB_HTTP_URL`` and ``HYDRADB_GRAPH_TOKEN`` to point at any engine
instance; both default to a local ``docker run`` of the engine.
"""

from __future__ import annotations

import itertools
import os
import random

import httpx

from .models import Advisory, AttackPath, BlastRadiusReport, DependencyGraph, Package

_DEFAULT_URL = "http://127.0.0.1:8443"
_DEFAULT_TOKEN = "local-development-token-32-bytes"
_NAMESPACE = "default"
_GRAPH = "default"
_CELL = "cell-0"
_MAX_LEN = 12
_PATHS_PER_TARGET = 5

# The engine writes into a single shared graph, so each scan takes a disjoint
# integer id range. Seeding the counter from a random offset keeps ranges from
# colliding with nodes left by a previous process after a restart.
_scan_counter = itertools.count(random.randrange(1, 1_000_000))


class HydraEngineError(RuntimeError):
    pass


class HydraEngine:
    def __init__(
        self,
        *,
        url: str | None = None,
        token: str | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self._url = (url or os.environ.get("HYDRADB_HTTP_URL") or _DEFAULT_URL).rstrip("/")
        self._token = token or os.environ.get("HYDRADB_GRAPH_TOKEN") or _DEFAULT_TOKEN
        self._client = client or httpx.Client(timeout=60.0)

    def compute_blast_radius(
        self,
        graph: DependencyGraph,
        advisories: dict[tuple[str, str], list[Advisory]],
    ) -> BlastRadiusReport:
        base = next(_scan_counter) * 10_000_000
        ids = {node_id: base + i for i, node_id in enumerate(graph.packages)}

        self._ingest(graph, ids)

        affected: dict[str, list[Advisory]] = {
            pkg.node_id: advisories[(pkg.name, pkg.version)]
            for pkg in graph.packages.values()
            if (pkg.name, pkg.version) in advisories
        }
        report = BlastRadiusReport(
            root=graph.root,
            affected=affected,
            total_packages=len(graph.packages),
        )

        root_id = ids[graph.root.node_id]
        by_hydra_id = {hid: node_id for node_id, hid in ids.items()}
        for node_id, node_advisories in affected.items():
            for hydra_path in self._shortest_paths(root_id, ids[node_id]):
                # Ignore any path that strays into another scan's id range.
                if any(h not in by_hydra_id for h in hydra_path):
                    continue
                nodes = [graph.packages[by_hydra_id[h]] for h in hydra_path]
                report.paths.append(AttackPath(nodes=nodes, advisory=_worst(node_advisories)))
        return report

    def _ingest(self, graph: DependencyGraph, ids: dict[str, int]) -> None:
        named: set[str] = set()

        def term(node_id: str) -> str:
            pkg = graph.packages[node_id]
            if node_id in named:
                return f"{{id:{ids[node_id]}}}"
            named.add(node_id)
            return f"{{id:{ids[node_id]}, name:{_quote(pkg.coordinate)}}}"

        for edge in graph.edges:
            self._query(
                f"CREATE (a {term(edge.requirer)})-[:DEPENDS_ON]->(b {term(edge.dependency)})"
            )

    def _shortest_paths(self, source: int, target: int) -> list[list[int]]:
        if source == target:
            return []
        result = self._query(
            f"CALL algo.SPpaths({{sourceNode:{source}, targetNode:{target}, "
            f"relTypes:['DEPENDS_ON'], relDirection:'outgoing', maxLen:{_MAX_LEN}, "
            f"pathCount:{_PATHS_PER_TARGET}}}) YIELD path RETURN path"
        )
        seen: set[tuple[int, ...]] = set()
        paths: list[list[int]] = []
        for row in result.get("rows", []):
            ids = tuple(n["id"] for n in row[0]["value"]["nodes"])
            if ids not in seen:
                seen.add(ids)
                paths.append(list(ids))
        return paths

    def _query(self, cypher: str) -> dict:
        try:
            response = self._client.post(
                f"{self._url}/v1/graphs/{_GRAPH}/query",
                headers={
                    "Authorization": f"Bearer {self._token}",
                    "X-Graph-Namespace": _NAMESPACE,
                    "Content-Type": "application/json",
                },
                json={"cell_id": _CELL, "query": cypher},
            )
        except httpx.HTTPError as exc:
            raise HydraEngineError(f"HydraDB is unreachable: {exc}") from exc
        if response.status_code != 200:
            raise HydraEngineError(f"HydraDB query failed ({response.status_code}): {response.text}")
        body = response.json()
        if "error" in body:
            raise HydraEngineError(f"HydraDB error: {body['error'].get('message')}")
        return body


def _worst(advisories: list[Advisory]) -> Advisory:
    order = {"CRITICAL": 0, "HIGH": 1, "MODERATE": 2, "LOW": 3, "UNKNOWN": 4}
    return min(advisories, key=lambda a: (not a.is_malicious, order.get(a.severity, 4)))


def _quote(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"
