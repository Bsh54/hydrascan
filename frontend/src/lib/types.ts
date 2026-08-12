export interface Advisory {
  id: string;
  summary: string;
  severity: string;
  isMalicious: boolean;
  published?: string | null;
  fixedVersion?: string | null;
}

export interface SharedMaintainer {
  maintainer: string;
  packages: string[];
}

export interface SharedInfrastructure {
  repository: string;
  packages: string[];
}

export interface Typosquat {
  package: string;
  similarTo: string;
}

export interface GraphNode {
  id: string;
  name: string;
  version: string;
  type: "application" | "package";
  compromised: boolean;
}

export interface GraphEdge {
  source: string;
  target: string;
}

export interface AttackPath {
  nodes: string[];
  advisory: Advisory;
}

export interface CompromisedPackage {
  coordinate: string;
  advisories: Advisory[];
}

export interface Remediation {
  package: string;
  introducedBy: string | null;
  fixedVersion: string | null;
  command: string;
}

export interface ScanResult {
  project: string;
  totalPackages: number;
  isExposed: boolean;
  exposureScore: number;
  compromised: CompromisedPackage[];
  paths: AttackPath[];
  remediation: Remediation[];
  nodes: GraphNode[];
  edges: GraphEdge[];
  source?: "lockfile" | "deps.dev";
  engine?: "hydradb" | "local";
  ecosystem?: "npm" | "PyPI";
  sharedMaintainers?: SharedMaintainer[];
  sharedInfrastructure?: SharedInfrastructure[];
  typosquats?: Typosquat[];
}
