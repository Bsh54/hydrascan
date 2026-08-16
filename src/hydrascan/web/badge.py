"""A small shields-style SVG status badge for a scanned repository.

Rendered server-side so a project can embed its live exposure state in a README
with a plain Markdown image, no external badge service involved.
"""

from __future__ import annotations

_FONT = (
    "font-family='Verdana,Geneva,DejaVu Sans,sans-serif' font-size='11'"
)


def render_badge(message: str, color: str, label: str = "hydrascan") -> str:
    """Return a flat two-part SVG badge (label on gray, message on color)."""
    lw = 7 * len(label) + 20
    mw = 7 * len(message) + 20
    total = lw + mw
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total}" height="20" role="img" aria-label="{label}: {message}">
<linearGradient id="s" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient>
<clipPath id="r"><rect width="{total}" height="20" rx="3" fill="#fff"/></clipPath>
<g clip-path="url(#r)">
<rect width="{lw}" height="20" fill="#333"/>
<rect x="{lw}" width="{mw}" height="20" fill="{color}"/>
<rect width="{total}" height="20" fill="url(#s)"/>
</g>
<g fill="#fff" text-anchor="middle" {_FONT}>
<text x="{lw / 2}" y="14">{label}</text>
<text x="{lw + mw / 2}" y="14">{message}</text>
</g>
</svg>"""


def badge_for_scan(scan: dict) -> tuple[str, str]:
    """Map a scan payload to a badge (message, color)."""
    malware = len(scan.get("compromised") or [])
    vulnerable = len(scan.get("vulnerable") or [])
    if malware:
        return f"{malware} compromised", "#e5484d"
    if vulnerable:
        return f"{vulnerable} vulnerable", "#f5a623"
    return "clean", "#3fb950"
