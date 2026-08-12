"""Flag dependencies whose names sit one edit away from a popular package.

Typosquatting is a common supply-chain vector: an attacker publishes a package
whose name is a near-miss of a widely used one. We compare every dependency
name against a list of popular packages and report close, non-identical matches.
"""

from __future__ import annotations

from collections.abc import Iterable

# A compact list of very popular npm packages used as typosquat targets.
_POPULAR = frozenset(
    {
        "react", "react-dom", "lodash", "axios", "express", "chalk", "commander",
        "debug", "moment", "request", "async", "bluebird", "underscore", "webpack",
        "babel-core", "typescript", "eslint", "prettier", "jest", "mocha", "chai",
        "vue", "angular", "rxjs", "redux", "next", "dotenv", "uuid", "yargs",
        "glob", "minimist", "colors", "cross-env", "node-fetch", "socket.io",
        "mongoose", "sequelize", "pg", "mysql", "redis", "jsonwebtoken", "bcrypt",
        "cors", "body-parser", "nodemon", "ws", "ini", "semver", "tslib", "rimraf",
    }
)

# Popular short/common packages that must never be flagged as typosquats.
_ALLOWLIST = frozenset({"qs", "ms", "core", "pify", "ee-first", "type-is"})

_MIN_LENGTH = 4


def detect_typosquats(names: Iterable[str]) -> list[dict[str, object]]:
    """Return one entry per dependency name that looks like a typosquat."""
    findings: list[dict[str, object]] = []
    seen: set[str] = set()
    for name in names:
        if name.startswith("@"):  # scoped names can't typosquat an unscoped package
            continue
        base = _unscope(name)
        if base in _POPULAR or base in _ALLOWLIST or base in seen or len(base) < _MIN_LENGTH:
            continue
        seen.add(base)
        for target in _POPULAR:
            if abs(len(base) - len(target)) > 1:
                continue
            if _within_one_edit(base, target):
                findings.append({"package": name, "similarTo": target})
                break
    return findings


def _unscope(name: str) -> str:
    return name.rsplit("/", 1)[-1] if name.startswith("@") else name


def _within_one_edit(a: str, b: str) -> bool:
    if a == b:
        return False
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    shorter, longer = (a, b) if len(a) < len(b) else (b, a)
    i = j = 0
    edited = False
    while i < len(shorter) and j < len(longer):
        if shorter[i] != longer[j]:
            if edited:
                return False
            edited = True
            j += 1
        else:
            i += 1
            j += 1
    return True
