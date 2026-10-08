/**
 * ClaimGraph AI — Interactive Knowledge Graph Component.
 *
 * Visualizes Neo4j entities and relationships with interactive node selection,
 * topology physics, relationship tags, and entity property inspection.
 */

import React, { useState, useEffect, useRef, useMemo } from 'react';
import { type GraphDataResponse, type GraphNode } from '@/services/investigation';

import { ZoomIn, ZoomOut, RotateCcw, ShieldAlert, Cpu, User, MapPin, Wrench, FileText, CheckCircle } from 'lucide-react';

interface InteractiveKnowledgeGraphProps {
  data: GraphDataResponse | null;
  loading?: boolean;
  onNodeClick?: (node: GraphNode) => void;
  selectedNodeId?: string | null;
}

const NODE_COLORS: Record<string, { bg: string; border: string; text: string }> = {
  Customer: { bg: 'rgba(56, 189, 248, 0.15)', border: '#38bdf8', text: '#38bdf8' },
  Device: { bg: 'rgba(168, 85, 247, 0.15)', border: '#a855f7', text: '#c084fc' },
  Product: { bg: 'rgba(234, 179, 8, 0.15)', border: '#eab308', text: '#fde047' },
  Claim: { bg: 'rgba(239, 68, 68, 0.15)', border: '#ef4444', text: '#f87171' },
  RepairShop: { bg: 'rgba(249, 115, 22, 0.15)', border: '#f97316', text: '#fb923c' },
  Location: { bg: 'rgba(34, 197, 94, 0.15)', border: '#22c55e', text: '#4ade80' },
  Policy: { bg: 'rgba(99, 102, 241, 0.15)', border: '#6366f1', text: '#818cf8' },
  Document: { bg: 'rgba(148, 163, 184, 0.15)', border: '#94a3b8', text: '#cbd5e1' },
};

export const InteractiveKnowledgeGraph: React.FC<InteractiveKnowledgeGraphProps> = ({
  data,
  loading = false,
  onNodeClick,
  selectedNodeId: propSelectedNodeId,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  // Compute node layout coordinates
  const nodePositions = useMemo(() => {
    if (!data || !data.nodes || data.nodes.length === 0) return new Map<string, { x: number; y: number }>();
    const positions = new Map<string, { x: number; y: number }>();
    const width = 800;
    const height = 480;
    const centerX = width / 2;
    const centerY = height / 2;

    // Place central claim node in center
    const claimNode = data.nodes.find((n) => n.type === 'Claim') || data.nodes[0];
    positions.set(claimNode.id, { x: centerX, y: centerY });

    // Place remaining nodes in radial rings
    const remaining = data.nodes.filter((n) => n.id !== claimNode.id);
    const radius = Math.min(centerX, centerY) - 80;
    const angleStep = (2 * Math.PI) / Math.max(1, remaining.length);

    remaining.forEach((node, i) => {
      const angle = i * angleStep;
      // Stagger radius slightly for organic visual distribution
      const r = radius * (0.8 + (i % 2) * 0.3);
      positions.set(node.id, {
        x: centerX + r * Math.cos(angle),
        y: centerY + r * Math.sin(angle),
      });
    });

    return positions;
  }, [data]);

  // Sync selected node from prop
  useEffect(() => {
    if (propSelectedNodeId && data?.nodes) {
      const found = data.nodes.find((n) => n.id === propSelectedNodeId);
      if (found) setSelectedNode(found);
    }
  }, [propSelectedNodeId, data]);

  const handleMouseDown = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).tagName === 'svg' || (e.target as HTMLElement).tagName === 'rect') {
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

  const handleNodeSelect = (node: GraphNode) => {
    setSelectedNode(node);
    if (onNodeClick) onNodeClick(node);
  };

  const getNodeIcon = (type: string) => {
    switch (type) {
      case 'Customer':
        return <User className="w-3.5 h-3.5 text-sky-400" />;
      case 'Device':
        return <Cpu className="w-3.5 h-3.5 text-purple-400" />;
      case 'Claim':
        return <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />;
      case 'RepairShop':
        return <Wrench className="w-3.5 h-3.5 text-amber-400" />;
      case 'Location':
        return <MapPin className="w-3.5 h-3.5 text-emerald-400" />;
      case 'Document':
        return <FileText className="w-3.5 h-3.5 text-slate-300" />;
      default:
        return <CheckCircle className="w-3.5 h-3.5 text-indigo-400" />;
    }
  };

  if (loading) {
    return (
      <div className="h-[460px] flex flex-col items-center justify-center border border-white/10 rounded-xl bg-black/40 text-slate-400 font-mono text-xs">
        <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mb-3" />
        <span>Executing Neo4j graph traversal & neighbor discovery...</span>
      </div>
    );
  }

  if (!data || data.nodes.length === 0) {
    return (
      <div className="h-[460px] flex flex-col items-center justify-center border border-white/10 rounded-xl bg-black/40 text-slate-500 font-mono text-xs p-6 text-center">
        <ShieldAlert className="w-8 h-8 text-slate-600 mb-2" />
        <span className="text-slate-400 font-medium">No Graph Topology Indexed</span>
        <span className="text-slate-500 mt-1">Run AI Investigation to synchronize claim entities into the knowledge graph.</span>
      </div>
    );
  }

  return (
    <div className="relative border border-white/10 rounded-xl overflow-hidden bg-slate-950/80 backdrop-blur-md">
      {/* Canvas Controls */}
      <div className="absolute top-3 right-3 z-10 flex items-center gap-1.5 bg-slate-900/90 border border-white/10 rounded-lg p-1 shadow-lg">
        <button
          onClick={() => setZoom((z) => Math.min(2, z + 0.15))}
          className="p-1.5 text-slate-400 hover:text-white hover:bg-white/10 rounded transition-colors"
          title="Zoom In"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={() => setZoom((z) => Math.max(0.5, z - 0.15))}
          className="p-1.5 text-slate-400 hover:text-white hover:bg-white/10 rounded transition-colors"
          title="Zoom Out"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <button
          onClick={() => {
            setZoom(1);
            setPan({ x: 0, y: 0 });
          }}
          className="p-1.5 text-slate-400 hover:text-white hover:bg-white/10 rounded transition-colors"
          title="Reset View"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>

      {/* Graph Legend */}
      <div className="absolute bottom-3 left-3 z-10 hidden sm:flex flex-wrap items-center gap-2 bg-slate-900/90 border border-white/10 rounded-lg px-3 py-1.5 text-[10px] font-mono shadow-lg">
        {Object.entries(NODE_COLORS).map(([type, color]) => (
          <div key={type} className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color.border }} />
            <span className="text-slate-300">{type}</span>
          </div>
        ))}
      </div>

      {/* SVG Canvas */}
      <div
        ref={containerRef}
        className="w-full h-[460px] cursor-grab active:cursor-grabbing overflow-hidden"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
      >
        <svg
          viewBox="0 0 800 480"
          className="w-full h-full"
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
            transformOrigin: 'center center',
            transition: isDragging ? 'none' : 'transform 0.1s ease-out',
          }}
        >
          <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 10 5 L 0 9 z" fill="rgba(148, 163, 184, 0.4)" />
            </marker>
          </defs>

          {/* Background Grid */}
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255, 255, 255, 0.03)" strokeWidth="1" />
          </pattern>
          <rect width="100%" height="100%" fill="url(#grid)" />

          {/* Links / Edges */}
          {data.links.map((link, idx) => {
            const sourcePos = nodePositions.get(link.source);
            const targetPos = nodePositions.get(link.target);
            if (!sourcePos || !targetPos) return null;

            const midX = (sourcePos.x + targetPos.x) / 2;
            const midY = (sourcePos.y + targetPos.y) / 2;

            return (
              <g key={`edge-${idx}`}>
                <line
                  x1={sourcePos.x}
                  y1={sourcePos.y}
                  x2={targetPos.x}
                  y2={targetPos.y}
                  stroke="rgba(148, 163, 184, 0.35)"
                  strokeWidth="1.5"
                  strokeDasharray={link.type.includes('COLLUSION') ? '4 4' : undefined}
                  markerEnd="url(#arrow)"
                />
                {/* Edge Label */}
                <rect
                  x={midX - 35}
                  y={midY - 7}
                  width="70"
                  height="14"
                  rx="3"
                  fill="rgba(15, 23, 42, 0.85)"
                  stroke="rgba(255, 255, 255, 0.08)"
                  strokeWidth="0.5"
                />
                <text
                  x={midX}
                  y={midY + 3}
                  textAnchor="middle"
                  fill="rgba(148, 163, 184, 0.9)"
                  fontSize="7.5"
                  fontFamily="monospace"
                >
                  {link.type.length > 14 ? link.type.slice(0, 12) + '..' : link.type}
                </text>
              </g>
            );
          })}

          {/* Nodes */}
          {data.nodes.map((node) => {
            const pos = nodePositions.get(node.id);
            if (!pos) return null;
            const isSelected = selectedNode?.id === node.id;
            const color = NODE_COLORS[node.type] || NODE_COLORS.Document;

            return (
              <g
                key={node.id}
                transform={`translate(${pos.x}, ${pos.y})`}
                className="cursor-pointer transition-transform hover:scale-110"
                onClick={() => handleNodeSelect(node)}
              >
                {/* Pulse Glow for Selected / Claim Node */}
                {(isSelected || node.type === 'Claim') && (
                  <circle
                    r="28"
                    fill="none"
                    stroke={color.border}
                    strokeWidth="1.5"
                    className="animate-ping opacity-30"
                  />
                )}

                {/* Node Body */}
                <circle
                  r="22"
                  fill={color.bg}
                  stroke={isSelected ? '#38bdf8' : color.border}
                  strokeWidth={isSelected ? '2.5' : '1.5'}
                />

                {/* Node Label Text */}
                <text
                  y="34"
                  textAnchor="middle"
                  fill="#f1f5f9"
                  fontSize="9.5"
                  fontWeight="600"
                  fontFamily="sans-serif"
                  className="select-none"
                >
                  {node.label.length > 16 ? node.label.slice(0, 15) + '…' : node.label}
                </text>

                {/* Node Subtitle Type */}
                <text
                  y="45"
                  textAnchor="middle"
                  fill={color.text}
                  fontSize="7.5"
                  fontFamily="monospace"
                  className="select-none uppercase"
                >
                  {node.type}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Selected Node Details Drawer */}
      {selectedNode && (
        <div className="border-t border-white/10 bg-slate-900/95 p-3.5 text-xs">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              {getNodeIcon(selectedNode.type)}
              <span className="font-semibold text-slate-100">{selectedNode.label}</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-white/5 border border-white/10 text-cyan-400">
                {selectedNode.type}
              </span>
            </div>
            <button
              onClick={() => setSelectedNode(null)}
              className="text-slate-400 hover:text-white text-xs px-2 py-0.5"
            >
              Close
            </button>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 font-mono text-[11px] text-slate-300">
            <div>
              <span className="text-slate-500 block text-[10px]">ID:</span>
              <span className="truncate block">{selectedNode.id}</span>
            </div>
            {Object.entries(selectedNode.properties || {}).slice(0, 3).map(([key, val]) => (
              <div key={key}>
                <span className="text-slate-500 block text-[10px] uppercase">{key}:</span>
                <span className="truncate block">{String(val)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
