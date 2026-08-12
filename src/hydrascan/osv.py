"""Query the OSV.dev database for advisories affecting exact package versions.

OSV is free and unauthenticated. The batch endpoint keeps a full-tree scan to a
handful of requests; advisory details are fetched in parallel and cached, per
OSV's documented pattern (batch for IDs, then fetch and cache full records).
"""

from __future__ import annotations

import math
import re
import time
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor

import httpx

from .models import Advisory

_BATCH_URL = "https://api.osv.dev/v1/querybatch"
_VULN_URL = "https://api.osv.dev/v1/vulns"
_ECOSYSTEM = "npm"
_BATCH_SIZE = 1000
_DETAIL_WORKERS = 16
_CACHE_TTL = 3600.0

_cache: dict[str, tuple[float, Advisory]] = {}


def find_advisories(
    coordinates: Iterable[tuple[str, str]],
    *,
    ecosystem: str = "npm",
    client: httpx.Client | None = None,
) -> dict[tuple[str, str], list[Advisory]]:
    """Map each ``(name, version)`` to the advisories affecting that version."""
    unique = sorted({(n, v) for n, v in coordinates if n and v and v != "0.0.0"})
    if not unique:
        return {}

    owned = client is None
    http = client or httpx.Client(timeout=30.0)
    try:
        ids_by_coord = _query_batch(http, unique, ecosystem)
        wanted = {i for ids in ids_by_coord.values() for i in ids}
        details = _fetch_details(http, wanted)
    finally:
        if owned:
            http.close()

    return {
        coord: [details[i] for i in ids if i in details]
        for coord, ids in ids_by_coord.items()
    }


def _query_batch(
    http: httpx.Client, coords: list[tuple[str, str]], ecosystem: str
) -> dict[tuple[str, str], list[str]]:
    ids_by_coord: dict[tuple[str, str], list[str]] = {}
    for start in range(0, len(coords), _BATCH_SIZE):
        chunk = coords[start : start + _BATCH_SIZE]
        queries = [
            {"package": {"ecosystem": ecosystem, "name": name}, "version": version}
            for name, version in chunk
        ]
        response = http.post(_BATCH_URL, json={"queries": queries})
        response.raise_for_status()
        results = response.json().get("results", [])
        for coord, entry in zip(chunk, results):
            ids = [v["id"] for v in (entry.get("vulns") or [])]
            if ids:
                ids_by_coord[coord] = ids
    return ids_by_coord


def _fetch_details(http: httpx.Client, ids: set[str]) -> dict[str, Advisory]:
    now = time.monotonic()
    resolved = {i: _cache[i][1] for i in ids if _valid(i, now)}
    missing = [i for i in ids if i not in resolved]
    if missing:
        with ThreadPoolExecutor(max_workers=_DETAIL_WORKERS) as pool:
            for advisory in pool.map(lambda i: _fetch_vuln(http, i), missing):
                _cache[advisory.id] = (now, advisory)
                resolved[advisory.id] = advisory
    return resolved


def _valid(vuln_id: str, now: float) -> bool:
    cached = _cache.get(vuln_id)
    return cached is not None and now - cached[0] < _CACHE_TTL


def _fetch_vuln(http: httpx.Client, vuln_id: str) -> Advisory:
    response = http.get(f"{_VULN_URL}/{vuln_id}")
    response.raise_for_status()
    data = response.json()
    return Advisory(
        id=data.get("id", vuln_id),
        package=_affected_name(data),
        summary=data.get("summary") or data.get("details", "")[:200] or vuln_id,
        severity=_severity(data),
        is_malicious=vuln_id.startswith("MAL-"),
        fixed_version=_fixed_version(data),
        published=(data.get("published") or "")[:10] or None,
    )


def _affected_name(data: dict) -> str:
    affected = data.get("affected") or [{}]
    return affected[0].get("package", {}).get("name", "")


def _severity(data: dict) -> str:
    if data.get("id", "").startswith("MAL-"):
        return "CRITICAL"

    # Qualitative severity (GHSA advisories carry this at the top level).
    top = (data.get("database_specific") or {}).get("severity")
    if top:
        return _normalize_severity(str(top))
    for affected in data.get("affected") or []:
        level = (affected.get("database_specific") or {}).get("severity")
        if level:
            return _normalize_severity(str(level))

    # Otherwise derive a category from the CVSS base score.
    for entry in data.get("severity") or []:
        category = _cvss_category(entry.get("score", ""))
        if category:
            return category
    return "UNKNOWN"


def _normalize_severity(value: str) -> str:
    value = value.upper()
    return "MODERATE" if value == "MEDIUM" else value


def _cvss_category(vector: str) -> str | None:
    match = re.search(r"/(?:BS|BaseScore):?(\d+\.?\d*)", vector)
    score = float(match.group(1)) if match else _cvss_base_score(vector)
    if score is None:
        return None
    if score >= 9.0:
        return "CRITICAL"
    if score >= 7.0:
        return "HIGH"
    if score >= 4.0:
        return "MODERATE"
    return "LOW"


def _cvss_base_score(vector: str) -> float | None:
    """Best-effort CVSS v3 base score from a vector string."""
    if not vector.startswith("CVSS:3"):
        return None
    weights = {
        "AV": {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2},
        "AC": {"L": 0.77, "H": 0.44},
        "PR": {"N": 0.85, "L": 0.62, "H": 0.27},
        "UI": {"N": 0.85, "R": 0.62},
        "C": {"H": 0.56, "L": 0.22, "N": 0.0},
        "I": {"H": 0.56, "L": 0.22, "N": 0.0},
        "A": {"H": 0.56, "L": 0.22, "N": 0.0},
    }
    metrics = dict(part.split(":") for part in vector.split("/") if ":" in part and len(part.split(":")) == 2)
    try:
        iss = 1 - (1 - weights["C"][metrics["C"]]) * (1 - weights["I"][metrics["I"]]) * (1 - weights["A"][metrics["A"]])
        impact = 6.42 * iss
        exploitability = (
            8.22 * weights["AV"][metrics["AV"]] * weights["AC"][metrics["AC"]]
            * weights["PR"][metrics["PR"]] * weights["UI"][metrics["UI"]]
        )
    except KeyError:
        return None
    if impact <= 0:
        return 0.0
    scope_changed = metrics.get("S") == "C"
    raw = (min(1.08 * (impact + exploitability), 10) if scope_changed else min(impact + exploitability, 10))
    return math.ceil(raw * 10) / 10


def _fixed_version(data: dict) -> str | None:
    for affected in data.get("affected") or []:
        for rng in affected.get("ranges") or []:
            for event in rng.get("events") or []:
                if "fixed" in event:
                    return event["fixed"]
    return None
