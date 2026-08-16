"""Core domain types shared across the engine, CLI, and web backend."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Package:
    """A resolved node in the dependency tree.

    ``node_id`` is the install path from the lockfile (unique per install
    location), so the same name/version installed at two paths stays distinct.
    """

    node_id: str
    name: str
    version: str
    is_root: bool = False

    @property
    def coordinate(self) -> str:
        return f"{self.name}@{self.version}"


@dataclass(frozen=True, slots=True)
class Dependency:
    """A directed edge: ``requirer`` depends on ``dependency``."""

    requirer: str
    dependency: str


@dataclass(frozen=True, slots=True)
class Advisory:
    """A known vulnerability or malicious-package advisory for a package version."""

    id: str
    package: str
    summary: str
    severity: str = "UNKNOWN"
    is_malicious: bool = False
    fixed_version: str | None = None
    published: str | None = None
    modified: str | None = None


@dataclass(slots=True)
class DependencyGraph:
    """The dependency tree of a single project."""

    root: Package
    packages: dict[str, Package] = field(default_factory=dict)
    edges: list[Dependency] = field(default_factory=list)

    def add_package(self, package: Package) -> None:
        self.packages[package.node_id] = package

    def add_edge(self, requirer: str, dependency: str) -> None:
        self.edges.append(Dependency(requirer, dependency))

    def parents_of(self, node_id: str) -> list[str]:
        return [e.requirer for e in self.edges if e.dependency == node_id]


@dataclass(slots=True)
class AttackPath:
    """A concrete chain from the root project down to a compromised package."""

    nodes: list[Package]
    advisory: Advisory

    def render(self) -> str:
        return " -> ".join(p.coordinate for p in self.nodes)


@dataclass(slots=True)
class BlastRadiusReport:
    """The result of a scan: which reachable packages carry advisories.

    ``affected`` maps each reachable advisory-bearing package to its advisories.
    A package is *malware* when any of its advisories is a malicious-package
    advisory (OSV ``MAL-`` records: hijacked releases, credential stealers,
    typosquats); otherwise it is merely *vulnerable* (ordinary CVE/GHSA).
    """

    root: Package
    affected: dict[str, list[Advisory]] = field(default_factory=dict)
    paths: list[AttackPath] = field(default_factory=list)
    total_packages: int = 0

    @property
    def malware(self) -> dict[str, list[Advisory]]:
        return {n: a for n, a in self.affected.items() if any(x.is_malicious for x in a)}

    @property
    def vulnerable(self) -> dict[str, list[Advisory]]:
        return {n: a for n, a in self.affected.items() if not any(x.is_malicious for x in a)}

    @property
    def has_malware(self) -> bool:
        return bool(self.malware)

    @property
    def is_exposed(self) -> bool:
        return bool(self.paths)

    @property
    def exposure_score(self) -> int:
        """A 0-100 score driven by the worst reachable threat, its depth, and count.

        Only compromised packages that are actually reachable from the root
        (i.e. appear on an attack path) contribute. The worst advisory severity
        sets the ceiling; a shallower path and more distinct threats raise it.
        """
        if not self.paths:
            return 0

        severity = {"CRITICAL": 90, "HIGH": 70, "MODERATE": 45, "LOW": 20, "UNKNOWN": 40}
        worst = max(
            100 if path.advisory.is_malicious else severity.get(path.advisory.severity, 40)
            for path in self.paths
        )
        shortest_depth = min(len(path.nodes) for path in self.paths) - 1
        directness = max(0.80, 1.0 - (shortest_depth - 1) * 0.04)
        reachable = {path.nodes[-1].coordinate for path in self.paths}
        volume_bonus = min(8, len(reachable) - 1)
        return min(100, round(worst * directness) + volume_bonus)
