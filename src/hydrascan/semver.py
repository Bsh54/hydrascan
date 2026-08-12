"""A pragmatic subset of npm semver range matching.

Handles the operators that appear in real ``package.json`` files: caret,
tilde, exact, comparators, partial versions, wildcards, and ``||`` unions.
Prereleases are excluded from candidates, matching npm's default behavior.
"""

from __future__ import annotations

Version = tuple[int, int, int]


def max_satisfying(versions: list[str], requirement: str) -> str | None:
    candidates = [v for v in versions if _parse(v) is not None and "-" not in v]
    matching = [v for v in candidates if satisfies(v, requirement)]
    if not matching:
        return None
    return max(matching, key=lambda v: _parse(v))  # type: ignore[arg-type]


def satisfies(version: str, requirement: str) -> bool:
    parsed = _parse(version)
    if parsed is None:
        return False
    requirement = requirement.strip()
    if requirement in ("", "*", "x", "latest") or requirement.startswith(("http", "git", "file:", "npm:")):
        return True
    return any(_matches_all(parsed, clause) for clause in requirement.split("||"))


def _matches_all(version: Version, clause: str) -> bool:
    clause = clause.strip()
    if " - " in clause:
        low, high = clause.split(" - ", 1)
        return _cmp(version, _floor(low)) >= 0 and _cmp(version, _ceil(high)) <= 0
    return all(_matches(version, token) for token in clause.split() if token)


def _matches(version: Version, token: str) -> bool:
    for op in (">=", "<=", ">", "<", "="):
        if token.startswith(op):
            bound = _floor(token[len(op) :])
            result = _cmp(version, bound)
            return {
                ">=": result >= 0,
                "<=": result <= 0,
                ">": result > 0,
                "<": result < 0,
                "=": result == 0,
            }[op]
    if token.startswith("^"):
        return _within(version, token[1:], _caret_upper)
    if token.startswith("~"):
        return _within(version, token[1:], _tilde_upper)
    return _within(version, token, _partial_upper)


def _within(version: Version, base: str, upper_fn) -> bool:
    lower = _floor(base)
    upper = upper_fn(base)
    return _cmp(version, lower) >= 0 and _cmp(version, upper) < 0


def _caret_upper(base: str) -> Version:
    major, minor, patch = _components(base)
    if major is None or major > 0:
        return ((major or 0) + 1, 0, 0)
    if minor and minor > 0:
        return (0, minor + 1, 0)
    return (0, 0, (patch or 0) + 1)


def _tilde_upper(base: str) -> Version:
    major, minor, _ = _components(base)
    if minor is not None:
        return (major or 0, minor + 1, 0)
    return ((major or 0) + 1, 0, 0)


def _partial_upper(base: str) -> Version:
    major, minor, patch = _components(base)
    if minor is None:
        return ((major or 0) + 1, 0, 0)
    if patch is None:
        return (major or 0, minor + 1, 0)
    return (major or 0, minor, patch + 1)


def _components(base: str) -> tuple[int | None, int | None, int | None]:
    parts = base.strip().lstrip("v=").split(".")
    out: list[int | None] = []
    for i in range(3):
        if i < len(parts) and parts[i] not in ("", "x", "X", "*"):
            try:
                out.append(int(parts[i].split("-")[0]))
            except ValueError:
                out.append(None)
        else:
            out.append(None)
    return out[0], out[1], out[2]


def _floor(base: str) -> Version:
    major, minor, patch = _components(base)
    return (major or 0, minor or 0, patch or 0)


def _ceil(base: str) -> Version:
    return _partial_upper(base)


def _parse(version: str) -> Version | None:
    try:
        core = version.strip().lstrip("v").split("-")[0].split("+")[0]
        major, minor, patch = (int(p) for p in core.split(".")[:3])
        return (major, minor, patch)
    except (ValueError, TypeError):
        return None


def _cmp(a: Version, b: Version) -> int:
    return (a > b) - (a < b)
