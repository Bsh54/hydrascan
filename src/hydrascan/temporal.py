"""Temporal enrichment of a scan: when was each reachable threat live?

The blast radius answers *"can this compromised package reach me?"*. The
temporal layer answers the sharper question the Track 2 brief asks: *"is the
version I actually resolved inside the window where it was known-bad, and is
that window still open?"*. It uses only data we already fetch (OSV disclosure
and patch state) plus one npm ``time`` lookup per affected package, so the cost
scales with the number of threats, not the size of the tree.
"""

from __future__ import annotations

from datetime import date
from typing import Any

import httpx

from .depsdev import version_published_at
from .service import ScanResult


def temporal_windows(result: ScanResult, ecosystem: str) -> dict[str, dict[str, Any]]:
    """Map each reachable affected coordinate to its temporal window block."""
    if ecosystem != "npm":
        return {}

    today = date.today()
    windows: dict[str, dict[str, Any]] = {}
    with httpx.Client(timeout=15.0, follow_redirects=True) as http:
        for node_id, advisories in result.report.affected.items():
            pkg = result.graph.packages[node_id]
            if pkg.coordinate in windows:
                continue
            disclosed = min(
                (a.published for a in advisories if a.published), default=None
            )
            windows[pkg.coordinate] = {
                "resolvedVersion": pkg.version,
                "resolvedPublishedAt": version_published_at(http, pkg.name, pkg.version),
                "disclosedAt": disclosed,
                "patched": any(a.fixed_version for a in advisories),
                "daysSinceDisclosed": _days_since(today, disclosed),
            }
    return windows


def _days_since(today: date, stamp: str | None) -> int | None:
    if not stamp:
        return None
    try:
        return (today - date.fromisoformat(stamp)).days
    except ValueError:
        return None
