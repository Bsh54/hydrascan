import type { ScanResult } from "./types";

export interface SubEdge {
  source: string;
  target: string;
  attack: boolean;
}

export interface SubgraphElement {
  nodeIds: Set<string>;
  edges: SubEdge[];
}

const MAX_NODES = 200;

/**
 * The graph to render. When attack paths exist, show the focused blast-radius
 * subgraph (root -> compromised). Otherwise fall back to a bounded view of the
 * dependency tree so the canvas is never empty.
 */
export function blastRadiusSubgraph(result: ScanResult): SubgraphElement {
  const paths = attackPathSubgraph(result);
  if (paths.nodeIds.size > 0) return paths;
  return dependencyPreview(result);
}

function attackPathSubgraph(result: ScanResult): SubgraphElement {
  const nodeIds = new Set<string>();
  const edges = new Map<string, SubEdge>();

  for (const path of result.paths) {
    for (let i = 0; i < path.nodes.length; i += 1) {
      nodeIds.add(path.nodes[i]);
      if (i > 0) {
        const source = path.nodes[i - 1];
        const target = path.nodes[i];
        edges.set(`${source}->${target}`, { source, target, attack: true });
      }
    }
  }
  return { nodeIds, edges: [...edges.values()] };
}

function dependencyPreview(result: ScanResult): SubgraphElement {
  const root = result.nodes.find((n) => n.type === "application")?.id;
  const nodeIds = new Set<string>(root ? [root] : []);
  const edges: SubEdge[] = [];

  const adjacency = new Map<string, string[]>();
  for (const edge of result.edges) {
    adjacency.set(edge.source, [...(adjacency.get(edge.source) ?? []), edge.target]);
  }

  const queue = root ? [root] : [];
  while (queue.length && nodeIds.size < MAX_NODES) {
    const current = queue.shift()!;
    for (const child of adjacency.get(current) ?? []) {
      edges.push({ source: current, target: child, attack: false });
      if (!nodeIds.has(child) && nodeIds.size < MAX_NODES) {
        nodeIds.add(child);
        queue.push(child);
      }
    }
  }

  return { nodeIds, edges: edges.filter((e) => nodeIds.has(e.source) && nodeIds.has(e.target)) };
}
