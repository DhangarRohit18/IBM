import React, { useState, useMemo } from 'react';
import { ZoomIn, ZoomOut, RotateCcw, Filter, ExternalLink, ShieldCheck } from 'lucide-react';
import type { CodeGraphData, CodeGraphNode, CodeGraphEdge } from '../../services/api';
import { SourceEvidenceViewer } from './SourceEvidenceViewer';

interface ArchitectureGraphProps {
  graphData: CodeGraphData;
  onSelectEntity: (entityId: string) => void;
}

const CATEGORY_COLORS: Record<string, { bg: string; border: string; text: string; fill: string }> = {
  CONTROLLER: { bg: 'bg-emerald-950', border: 'border-emerald-500', text: 'text-emerald-300', fill: '#10b981' },
  SERVICE: { bg: 'bg-blue-950', border: 'border-blue-500', text: 'text-blue-300', fill: '#3b82f6' },
  REPOSITORY: { bg: 'bg-amber-950', border: 'border-amber-500', text: 'text-amber-300', fill: '#f59e0b' },
  ENTITY: { bg: 'bg-purple-950', border: 'border-purple-500', text: 'text-purple-300', fill: '#a855f7' },
  CONFIGURATION: { bg: 'bg-cyan-950', border: 'border-cyan-500', text: 'text-cyan-300', fill: '#06b6d4' },
  COMPONENT: { bg: 'bg-indigo-950', border: 'border-indigo-500', text: 'text-indigo-300', fill: '#6366f1' },
  UTILITY: { bg: 'bg-slate-800', border: 'border-slate-500', text: 'text-slate-300', fill: '#64748b' },
  FRAMEWORK_OTHER: { bg: 'bg-slate-900', border: 'border-slate-700', text: 'text-slate-400', fill: '#475569' },
};

const EDGE_COLORS: Record<string, string> = {
  DEPENDS_ON: '#3b82f6', // blue
  CALLS: '#06b6d4',      // cyan
  INHERITS: '#a855f7',   // purple
  IMPLEMENTS: '#f59e0b', // amber
  ANNOTATED_WITH: '#64748b', // slate
};

export const ArchitectureGraph: React.FC<ArchitectureGraphProps> = ({
  graphData,
  onSelectEntity,
}) => {
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<CodeGraphEdge | null>(null);
  const [activeCategoryFilter, setActiveCategoryFilter] = useState<Record<string, boolean>>({
    CONTROLLER: true,
    SERVICE: true,
    REPOSITORY: true,
    ENTITY: true,
    CONFIGURATION: true,
    COMPONENT: true,
    UTILITY: true,
    FRAMEWORK_OTHER: true,
  });

  // Calculate layout coordinates deterministically
  const positionedNodes = useMemo(() => {
    const nodes = graphData.nodes.filter(n => activeCategoryFilter[n.component_type] ?? true);
    const nodeMap = new Map<string, { node: CodeGraphNode; x: number; y: number }>();
    
    // Group by layer/component type for intuitive layered layout
    const layers: Record<string, CodeGraphNode[]> = {
      CONTROLLER: [],
      SERVICE: [],
      REPOSITORY: [],
      ENTITY: [],
      CONFIGURATION: [],
      COMPONENT: [],
      UTILITY: [],
      FRAMEWORK_OTHER: [],
    };

    nodes.forEach(n => {
      const cat = n.component_type in layers ? n.component_type : 'FRAMEWORK_OTHER';
      layers[cat].push(n);
    });

    const activeLayers = Object.keys(layers).filter(cat => layers[cat].length > 0);
    const layerSpacingX = 220;
    const itemSpacingY = 90;

    activeLayers.forEach((cat, colIdx) => {
      const list = layers[cat];
      const startY = 100 + (Math.max(0, 5 - list.length) * itemSpacingY) / 2;
      list.forEach((node, rowIdx) => {
        nodeMap.set(node.id, {
          node,
          x: 120 + colIdx * layerSpacingX,
          y: startY + rowIdx * itemSpacingY,
        });
      });
    });

    return nodeMap;
  }, [graphData.nodes, activeCategoryFilter]);

  const visibleEdges = useMemo(() => {
    return graphData.edges.filter(
      e => positionedNodes.has(e.source_id) && positionedNodes.has(e.target_id)
    );
  }, [graphData.edges, positionedNodes]);

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget || (e.target as HTMLElement).tagName === 'svg') {
      setIsDragging(true);
      setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPan({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
    }
  };

  const handleMouseUp = () => setIsDragging(false);

  const toggleCategory = (cat: string) => {
    setActiveCategoryFilter(prev => ({ ...prev, [cat]: !prev[cat] }));
  };

  const selectedNode = selectedNodeId ? graphData.nodes.find(n => n.id === selectedNodeId) : null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden flex flex-col h-[650px] font-mono text-sm">
      {/* Controls Bar */}
      <div className="p-3 bg-slate-950 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <span className="text-slate-400 font-semibold uppercase text-[11px]">Filter Layers:</span>
          {Object.keys(CATEGORY_COLORS).map(cat => {
            const style = CATEGORY_COLORS[cat];
            const active = activeCategoryFilter[cat];
            return (
              <button
                key={cat}
                onClick={() => toggleCategory(cat)}
                className={`px-2 py-0.5 rounded text-[10px] border transition-all ${
                  active
                    ? `${style.bg} ${style.text} ${style.border}`
                    : 'bg-slate-900 text-slate-600 border-slate-800 line-through'
                }`}
              >
                {cat}
              </button>
            );
          })}
        </div>

        <div className="flex items-center space-x-1 bg-slate-900 border border-slate-800 rounded-md p-1">
          <button
            onClick={() => setZoom(z => Math.min(2.0, z + 0.15))}
            className="p-1 hover:bg-slate-800 text-slate-300 rounded"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={() => setZoom(z => Math.max(0.4, z - 0.15))}
            className="p-1 hover:bg-slate-800 text-slate-300 rounded"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <button
            onClick={() => {
              setZoom(1);
              setPan({ x: 0, y: 0 });
            }}
            className="p-1 hover:bg-slate-800 text-slate-300 rounded"
            title="Reset View"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Canvas + Detail Drawer Container */}
      <div className="flex-1 relative flex overflow-hidden bg-slate-950/80">
        {/* SVG Canvas */}
        <div
          className="flex-1 cursor-grab active:cursor-grabbing overflow-hidden"
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
        >
          <svg className="w-full h-full">
            <defs>
              <marker
                id="arrowhead"
                markerWidth="8"
                markerHeight="6"
                refX="22"
                refY="3"
                orient="auto"
              >
                <polygon points="0 0, 8 3, 0 6" fill="#64748b" />
              </marker>
            </defs>

            <g transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}>
              {/* Edges */}
              {visibleEdges.map((edge) => {
                const source = positionedNodes.get(edge.source_id);
                const target = positionedNodes.get(edge.target_id);
                if (!source || !target) return null;

                const isSelected = selectedEdge === edge;
                const edgeColor = EDGE_COLORS[edge.type] || '#64748b';

                return (
                  <g key={edge.id} className="cursor-pointer" onClick={() => { setSelectedEdge(edge); setSelectedNodeId(null); }}>
                    <line
                      x1={source.x}
                      y1={source.y}
                      x2={target.x}
                      y2={target.y}
                      stroke={edgeColor}
                      strokeWidth={isSelected ? 3 : 1.5}
                      strokeDasharray={edge.type === 'CALLS' ? '4 3' : edge.type === 'IMPLEMENTS' ? '2 2' : undefined}
                      markerEnd="url(#arrowhead)"
                      opacity={isSelected ? 1 : 0.75}
                    />
                    <text
                      x={(source.x + target.x) / 2}
                      y={(source.y + target.y) / 2 - 5}
                      fill={edgeColor}
                      fontSize="9"
                      textAnchor="middle"
                      className="font-mono select-none"
                    >
                      {edge.type}
                    </text>
                  </g>
                );
              })}

              {/* Nodes */}
              {Array.from(positionedNodes.values()).map(({ node, x, y }) => {
                const colors = CATEGORY_COLORS[node.component_type] || CATEGORY_COLORS.FRAMEWORK_OTHER;
                const isSelected = selectedNodeId === node.id;

                return (
                  <g
                    key={node.id}
                    transform={`translate(${x}, ${y})`}
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedNodeId(node.id);
                      setSelectedEdge(null);
                    }}
                    className="cursor-pointer select-none"
                  >
                    <rect
                      x="-80"
                      y="-25"
                      width="160"
                      height="50"
                      rx="6"
                      fill="#0f172a"
                      stroke={isSelected ? '#3b82f6' : colors.fill}
                      strokeWidth={isSelected ? 3 : 1.5}
                      className="transition-all hover:brightness-125"
                    />
                    <circle x="-65" y="0" r="4" fill={colors.fill} />
                    <text
                      x="-55"
                      y="-4"
                      fill="#f8fafc"
                      fontSize="11"
                      fontWeight="600"
                      className="font-mono"
                    >
                      {node.name.length > 15 ? `${node.name.substring(0, 14)}…` : node.name}
                    </text>
                    <text
                      x="-55"
                      y="12"
                      fill={colors.fill}
                      fontSize="9"
                      className="font-mono uppercase tracking-wider"
                    >
                      {node.component_type}
                    </text>
                  </g>
                );
              })}
            </g>
          </svg>
        </div>

        {/* Selected Entity / Edge Inspector Drawer */}
        {(selectedNode || selectedEdge) && (
          <div className="w-80 border-l border-slate-800 bg-slate-900 p-4 overflow-y-auto z-10 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-3">
                <h4 className="font-semibold text-slate-200 text-xs uppercase tracking-wider">
                  {selectedNode ? 'Entity Inspector' : 'Relationship Evidence'}
                </h4>
                <button
                  onClick={() => { setSelectedNodeId(null); setSelectedEdge(null); }}
                  className="text-slate-500 hover:text-slate-300 text-xs"
                >
                  Close
                </button>
              </div>

              {selectedNode && (
                <div className="space-y-4 text-xs">
                  <div>
                    <span className="text-slate-500 text-[10px] uppercase">Qualified Name</span>
                    <p className="font-semibold text-slate-200 break-all">{selectedNode.qualified_name}</p>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[10px] uppercase">Classification</span>
                    <p className="mt-1">
                      <span className="px-2 py-0.5 rounded bg-blue-950 border border-blue-800 text-blue-300 font-semibold text-[11px]">
                        {selectedNode.component_type}
                      </span>
                    </p>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[10px] uppercase">Package</span>
                    <p className="text-slate-300">{selectedNode.package_name}</p>
                  </div>

                  <button
                    onClick={() => onSelectEntity(selectedNode.id)}
                    className="w-full mt-2 py-1.5 rounded bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs flex items-center justify-center space-x-1"
                  >
                    <span>Full Entity Details</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}

              {selectedEdge && (
                <div className="space-y-4 text-xs">
                  <div>
                    <span className="text-slate-500 text-[10px] uppercase">Relationship Type</span>
                    <p className="font-bold text-cyan-400 text-sm mt-0.5">{selectedEdge.type}</p>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[10px] uppercase">Resolution Status</span>
                    <p className="mt-1">
                      {selectedEdge.is_resolved ? (
                        <span className="px-2 py-0.5 rounded bg-emerald-950 border border-emerald-800 text-emerald-300 text-[10px]">
                          VERIFIED / RESOLVED
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded bg-amber-950 border border-amber-800 text-amber-300 text-[10px]">
                          AMBIGUOUS / UNRESOLVED
                        </span>
                      )}
                    </p>
                  </div>

                  <SourceEvidenceViewer
                    line_number={selectedEdge.line_number}
                    source_construct={selectedEdge.source_construct}
                    evidence_reason={selectedEdge.evidence_reason}
                  />
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-slate-800 text-[10px] text-slate-500 flex items-center space-x-1">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
              <span>Deterministic static evidence trace preserved.</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
