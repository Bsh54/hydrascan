import { useEffect, useMemo, useRef, useState } from "react";
import type { ReactNode } from "react";
import cytoscape from "cytoscape";
import fcose from "cytoscape-fcose";
import { Plus, Minus, Maximize2 } from "lucide-react";
import { blastRadiusSubgraph } from "../lib/subgraph";
import type { ScanResult } from "../lib/types";

cytoscape.use(fcose);

// Community palette, in the spirit of emerge's cluster coloring.
const CLUSTER_COLORS = [
  "#8dd6ff", "#8c93fb", "#5fed83", "#f6c177", "#f78fb2",
  "#9ece6a", "#7dcfff", "#bb9af7", "#e0af68", "#73daca",
];

interface GraphViewProps {
  result: ScanResult;
  onSelect: (coordinate: string) => void;
}

export function GraphView({ result, onSelect }: GraphViewProps) {
  const container = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  const [empty, setEmpty] = useState(false);
  const clusters = useMemo(() => clusterOf(result), [result]);

  const zoomBy = (factor: number) => {
    const cy = cyRef.current;
    if (!cy) return;
    cy.animate({ zoom: cy.zoom() * factor, center: { eles: cy.nodes() } }, { duration: 200 });
  };
  const fit = () => cyRef.current?.animate({ fit: { eles: cyRef.current.nodes(), padding: 50 } }, { duration: 200 });

  useEffect(() => {
    if (!container.current) return;
    const { nodeIds, edges } = blastRadiusSubgraph(result);
    setEmpty(nodeIds.size === 0);
    if (nodeIds.size === 0) return;

    const index = new Map(result.nodes.map((n) => [n.id, n]));
    const rootId = result.nodes.find((n) => n.type === "application")?.id;

    const elements: cytoscape.ElementDefinition[] = [];
    for (const id of nodeIds) {
      const node = index.get(id);
      const role = node?.type === "application" ? "root" : node?.compromised ? "compromised" : "package";
      elements.push({
        data: {
          id,
          label: node?.name ?? id,
          role,
          color: CLUSTER_COLORS[(clusters.get(id) ?? 0) % CLUSTER_COLORS.length],
        },
      });
    }
    for (const edge of edges) {
      elements.push({
        data: { id: `${edge.source}->${edge.target}`, source: edge.source, target: edge.target, attack: edge.attack ? "yes" : "no" },
      });
    }

    const cy = cytoscape({
      container: container.current,
      elements,
      style: [
        {
          selector: "node",
          style: { "background-color": "data(color)", width: 14, height: 14, "border-width": 0, label: "" },
        },
        {
          selector: 'node[role = "root"]',
          style: {
            "background-color": "#5fed83", width: 34, height: 34,
            label: "data(label)", color: "#ffffff", "font-family": "'JetBrains Mono', monospace",
            "font-size": "11px", "text-valign": "bottom", "text-margin-y": 6,
          },
        },
        {
          selector: 'node[role = "compromised"]',
          style: {
            "background-color": "#ff5b5b", width: 22, height: 22,
            label: "data(label)", color: "#ffb4ab", "font-family": "'JetBrains Mono', monospace",
            "font-size": "10px", "text-valign": "bottom", "text-margin-y": 5,
          },
        },
        {
          selector: "edge",
          style: {
            width: 1, "line-color": "#39404a", "curve-style": "bezier",
            "line-style": "dashed", "line-dash-pattern": [6, 5], "target-arrow-shape": "none", opacity: 0.55,
          },
        },
        {
          selector: 'edge[attack = "yes"]',
          style: { width: 1.8, "line-color": "#ff5b5b", opacity: 0.9 },
        },
        { selector: "node:selected", style: { "border-width": 2, "border-color": "#ffffff" } },
        {
          selector: "node.hovered",
          style: {
            label: "data(label)",
            color: "#ffffff",
            "font-family": "'JetBrains Mono', monospace",
            "font-size": "11px",
            "text-valign": "top",
            "text-margin-y": -4,
            "text-background-color": "#0a0e14",
            "text-background-opacity": 0.85,
            "text-background-padding": "3px",
            "border-width": 2,
            "border-color": "#ffffff",
            "z-index": 999,
          },
        },
      ],
      layout: {
        name: "fcose",
        animate: false,
        nodeRepulsion: 9000,
        idealEdgeLength: 75,
        nodeSeparation: 120,
        ...(rootId ? { fixedNodeConstraint: [{ nodeId: rootId, position: { x: 0, y: 0 } }] } : {}),
      } as cytoscape.LayoutOptions,
      minZoom: 0.1,
      maxZoom: 3,
    });

    // Flowing dashes: the "current" runs from the compromised packages up
    // toward the project — the direction the threat actually reaches you.
    let offset = 0;
    let raf = 0;
    const flow = () => {
      offset += 0.7;
      cy.edges().style("line-dash-offset", offset);
      raf = requestAnimationFrame(flow);
    };
    raf = requestAnimationFrame(flow);

    cyRef.current = cy;
    cy.on("tap", "node", (event) => onSelect(event.target.id()));
    cy.on("mouseover", "node", (event) => {
      event.target.addClass("hovered");
      if (container.current) container.current.style.cursor = "pointer";
    });
    cy.on("mouseout", "node", (event) => {
      event.target.removeClass("hovered");
      if (container.current) container.current.style.cursor = "default";
    });
    cy.ready(() => cy.fit(undefined, 50));

    return () => {
      cancelAnimationFrame(raf);
      cy.destroy();
    };
  }, [result, clusters, onSelect]);

  if (empty) {
    return (
      <div className="flex h-full w-full items-center justify-center">
        <p className="font-mono text-label-mono text-mercury">No dependency data to display.</p>
      </div>
    );
  }

  return (
    <div className="relative h-full w-full">
      <div ref={container} className="h-full w-full" />
      <div className="pointer-events-none absolute bottom-3 left-3 z-30 flex flex-wrap items-center gap-x-3 gap-y-1 font-mono text-[10px] text-mercury/70">
        <LegendDot color="#5fed83" label="your project" />
        <LegendDot color="#ff5b5b" label="compromised" />
        <LegendDot color="#8dd6ff" label="dependency (by cluster)" />
      </div>
      <div className="absolute left-3 top-16 z-30 flex flex-col overflow-hidden rounded-[6px] border border-slate-edge bg-obsidian/90 backdrop-blur">
        <ZoomButton label="Zoom in" onClick={() => zoomBy(1.3)}>
          <Plus className="h-4 w-4" strokeWidth={2} />
        </ZoomButton>
        <ZoomButton label="Zoom out" onClick={() => zoomBy(1 / 1.3)}>
          <Minus className="h-4 w-4" strokeWidth={2} />
        </ZoomButton>
        <ZoomButton label="Fit" onClick={fit}>
          <Maximize2 className="h-3.5 w-3.5" strokeWidth={2} />
        </ZoomButton>
      </div>
    </div>
  );
}

function LegendDot({ color, label }: { color: string; label: string }) {
  return (
    <span className="flex items-center gap-1.5">
      <span className="h-2 w-2 rounded-full" style={{ backgroundColor: color }} />
      {label}
    </span>
  );
}

function ZoomButton({ label, onClick, children }: { label: string; onClick: () => void; children: ReactNode }) {
  return (
    <button
      onClick={onClick}
      aria-label={label}
      className="flex h-9 w-9 items-center justify-center border-b border-slate-edge text-mercury transition-colors last:border-b-0 hover:bg-white/5 hover:text-snow"
    >
      {children}
    </button>
  );
}

function clusterOf(result: ScanResult): Map<string, number> {
  const children = new Map<string, string[]>();
  for (const edge of result.edges) {
    children.set(edge.source, [...(children.get(edge.source) ?? []), edge.target]);
  }
  const rootId = result.nodes.find((n) => n.type === "application")?.id;
  const cluster = new Map<string, number>();
  let next = 0;
  for (const first of children.get(rootId ?? "") ?? []) {
    const group = next++;
    const stack = [first];
    while (stack.length) {
      const current = stack.pop()!;
      if (cluster.has(current)) continue;
      cluster.set(current, group);
      for (const child of children.get(current) ?? []) stack.push(child);
    }
  }
  return cluster;
}
