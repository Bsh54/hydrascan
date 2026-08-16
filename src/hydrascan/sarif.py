"""Convert a scan payload into SARIF 2.1.0.

SARIF is the format GitHub code scanning ingests, so a CI job can run
``hydrascan <repo> --sarif > hydrascan.sarif`` and upload it to surface reachable
compromised dependencies directly in the repository's Security tab.
"""

from __future__ import annotations

from typing import Any

_SCHEMA = "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json"
_HELP = "https://hydrascan.shadrakbessanh.me"


def to_sarif(scan: dict[str, Any]) -> dict[str, Any]:
    manifest = _manifest_uri(scan)
    rules: dict[str, dict] = {}
    results: list[dict] = []

    for group, malicious in (("compromised", True), ("vulnerable", False)):
        for entry in scan.get(group) or []:
            pkg = entry["coordinate"]
            for adv in entry.get("advisories") or []:
                rid = adv["id"]
                rules.setdefault(rid, _rule(rid, adv))
                results.append(_result(rid, pkg, adv, malicious, manifest))

    return {
        "$schema": _SCHEMA,
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "HydraScan",
                        "informationUri": _HELP,
                        "rules": list(rules.values()),
                    }
                },
                "results": results,
            }
        ],
    }


def _rule(rid: str, adv: dict) -> dict:
    return {
        "id": rid,
        "name": "MaliciousPackage" if adv.get("isMalicious") else "VulnerableDependency",
        "shortDescription": {"text": adv.get("summary") or rid},
        "helpUri": f"https://osv.dev/vulnerability/{rid}",
        "defaultConfiguration": {"level": "error" if adv.get("isMalicious") else "warning"},
    }


def _result(rid: str, pkg: str, adv: dict, malicious: bool, manifest: str) -> dict:
    kind = "Compromised package" if malicious else "Vulnerable dependency"
    text = f"{kind} reachable from your project: {pkg}. {adv.get('summary') or rid}"
    return {
        "ruleId": rid,
        "level": "error" if malicious else "warning",
        "message": {"text": text},
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": manifest},
                    "region": {"startLine": 1},
                }
            }
        ],
    }


def _manifest_uri(scan: dict) -> str:
    if scan.get("source") == "lockfile":
        return "package-lock.json"
    return "requirements.txt" if scan.get("ecosystem") == "PyPI" else "package.json"
