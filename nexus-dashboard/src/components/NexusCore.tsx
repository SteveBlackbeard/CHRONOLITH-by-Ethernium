"use client";
import React, { useRef, useMemo, useState, useCallback } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial, Float, Octahedron, Sphere, Html, OrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import { buildStaticGraph, buildProjectNodes, GraphNode, GraphEdge, ScannedEntry } from '@/lib/graphData';

// ═══════════════════════════════════════════════════════════
// PARTICLE FIELD
// ═══════════════════════════════════════════════════════════
function ParticleField({ count = 2000 }) {
  const points = useMemo(() => {
    const p = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      p[i * 3] = (Math.random() - 0.5) * 40;
      p[i * 3 + 1] = (Math.random() - 0.5) * 40;
      p[i * 3 + 2] = (Math.random() - 0.5) * 40;
    }
    return p;
  }, [count]);
  const ref = useRef<THREE.Points>(null!);
  useFrame((s: any) => { ref.current.rotation.y = s.clock.getElapsedTime() * 0.02; });
  return (
    <Points ref={ref} positions={points} stride={3} frustumCulled={false}>
      <PointMaterial transparent color="#ffffff" size={0.008} sizeAttenuation depthWrite={false} blending={THREE.AdditiveBlending} />
    </Points>
  );
}

// ═══════════════════════════════════════════════════════════
// CONNECTION BEAM
// ═══════════════════════════════════════════════════════════
function ConnectionBeam({ start, end, color = '#ffffff' }: { start: [number, number, number]; end: [number, number, number]; color?: string }) {
  const count = 20;
  const points = useMemo(() => {
    const p = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const t = i / count;
      p[i * 3] = start[0] + (end[0] - start[0]) * t;
      p[i * 3 + 1] = start[1] + (end[1] - start[1]) * t;
      p[i * 3 + 2] = start[2] + (end[2] - start[2]) * t;
    }
    return p;
  }, [start, end]);
  return (
    <Points positions={points} stride={3}>
      <PointMaterial transparent color={color} size={0.03} sizeAttenuation depthWrite={false} blending={THREE.AdditiveBlending} opacity={0.3} />
    </Points>
  );
}

// ═══════════════════════════════════════════════════════════
// SYSTEM NODE
// ═══════════════════════════════════════════════════════════
function SystemNode({
  node, onHover, onUnhover, onClick,
}: {
  node: GraphNode;
  onHover: (n: GraphNode) => void;
  onUnhover: () => void;
  onClick: (n: GraphNode) => void;
}) {
  const [hovered, setHovered] = useState(false);
  const baseColor = node.color || '#888';
  const activeColor = hovered ? '#60a5fa' : baseColor;
  const scale = hovered ? node.size * 1.15 : node.size;

  const pOver = useCallback(() => { setHovered(true); onHover(node); }, [node, onHover]);
  const pOut = useCallback(() => { setHovered(false); onUnhover(); }, [onUnhover]);
  const pClick = useCallback(() => onClick(node), [node, onClick]);

  // ─── 3D SHAPES ───
  if (node.shape === 'octahedron') {
    return (
      <Float speed={1.5} rotationIntensity={0.8} floatIntensity={0.5} position={node.position}>
        <group onPointerOver={pOver} onPointerOut={pOut} onClick={pClick}>
          <Octahedron args={[scale, 0]}>
            <meshBasicMaterial color={activeColor} wireframe />
          </Octahedron>
          <Html distanceFactor={12} position={[0, -(scale + 0.8), 0]} center>
            <div style={{ color: activeColor, fontSize: '9px', whiteSpace: 'nowrap', textTransform: 'uppercase', letterSpacing: '3px', opacity: 0.7, fontFamily: 'monospace' }}>
              {node.label}
            </div>
          </Html>
        </group>
      </Float>
    );
  }

  if (node.shape === 'tetrahedron') {
    return (
      <Float speed={2} rotationIntensity={1.5} floatIntensity={0.3} position={node.position}>
        <group onPointerOver={pOver} onPointerOut={pOut} onClick={pClick}>
          <mesh>
            <tetrahedronGeometry args={[scale, 0]} />
            <meshBasicMaterial color={activeColor} wireframe />
          </mesh>
          <Html distanceFactor={12} position={[0, -(scale + 0.5), 0]} center>
            <div style={{ color: activeColor, fontSize: '7px', whiteSpace: 'nowrap', textTransform: 'uppercase', letterSpacing: '2px', fontFamily: 'monospace' }}>
              ⚡ {node.label}
            </div>
          </Html>
        </group>
      </Float>
    );
  }

  if (node.shape === 'sphere') {
    return (
      <Float speed={2.5} rotationIntensity={0.5} floatIntensity={0.4} position={node.position}>
        <group onPointerOver={pOver} onPointerOut={pOut} onClick={pClick}>
          <Sphere args={[scale * 0.6, 12, 12]}>
            <meshBasicMaterial color={activeColor} wireframe />
          </Sphere>
          <Html distanceFactor={12} position={[0, -(scale * 0.6 + 0.4), 0]} center>
            <div style={{ color: activeColor, fontSize: '7px', whiteSpace: 'nowrap', textTransform: 'uppercase', letterSpacing: '2px', fontFamily: 'monospace' }}>
              {node.label}
            </div>
          </Html>
        </group>
      </Float>
    );
  }

  // ─── DOCUMENT / FOLDER ICONS ───
  const isFolder = node.shape === 'folder-icon';
  const icon = isFolder ? '📁' : '📄';
  const labelColor = node.color || (isFolder ? '#fbbf24' : '#999');

  return (
    <group position={node.position}>
      <Html distanceFactor={10} center>
        <div
          onMouseEnter={() => { setHovered(true); onHover(node); }}
          onMouseLeave={() => { setHovered(false); onUnhover(); }}
          onClick={() => pClick()}
          style={{
            cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2px',
            transition: 'transform 0.2s, opacity 0.2s',
            transform: hovered ? 'scale(1.3)' : 'scale(1)',
            opacity: hovered ? 1 : 0.65,
          }}
        >
          <span style={{ fontSize: `${Math.max(14, node.size * 32)}px`, filter: hovered ? 'none' : 'grayscale(0.6)' }}>
            {icon}
          </span>
          <span style={{
            color: hovered ? '#60a5fa' : labelColor,
            fontSize: '5.5px', fontFamily: 'monospace',
            whiteSpace: 'nowrap', letterSpacing: '0.5px',
            maxWidth: '90px', overflow: 'hidden', textOverflow: 'ellipsis',
          }}>
            {node.label}
          </span>
        </div>
      </Html>
    </group>
  );
}

// ═══════════════════════════════════════════════════════════
// DOCUMENT READER PANEL
// ═══════════════════════════════════════════════════════════
function DocumentPanel({ fileName, content, truncated, onClose }: {
  fileName: string; content: string; truncated: boolean; onClose: () => void;
}) {
  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed', top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
        zIndex: 5000, width: '700px', maxWidth: '90vw', maxHeight: '80vh',
        background: 'rgba(0,0,0,0.92)', backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255,255,255,0.1)',
        display: 'flex', flexDirection: 'column', overflow: 'hidden',
        cursor: 'pointer',
      }}
    >
      {/* Header */}
      <div style={{
        padding: '16px 20px', borderBottom: '1px solid rgba(255,255,255,0.08)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      }}>
        <span style={{ color: '#60a5fa', fontSize: '0.7rem', fontFamily: 'monospace', letterSpacing: '2px', textTransform: 'uppercase' }}>
          📄 {fileName}
        </span>
        <span style={{ color: '#555', fontSize: '0.6rem', fontFamily: 'monospace' }}>
          CLICK TO CLOSE
        </span>
      </div>
      {/* Content */}
      <div style={{
        padding: '20px', overflowY: 'auto', flex: 1,
        color: '#d4d4d8', fontSize: '0.65rem', fontFamily: 'monospace',
        lineHeight: 1.7, whiteSpace: 'pre-wrap', wordBreak: 'break-word',
      }}>
        {content}
        {truncated && (
          <div style={{ color: '#f59e0b', marginTop: '16px', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '8px' }}>
            ⚠ Content truncated at 10,000 characters.
          </div>
        )}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// TOOLTIP BAR
// ═══════════════════════════════════════════════════════════
function TooltipBar({ node }: { node: GraphNode | null }) {
  if (!node) return null;
  const typeColors: Record<string, string> = {
    core: '#fff', engine: '#22d3ee', edition: node.color || '#fff',
    file: node.color || '#d4d4d8', folder: '#fbbf24', module: '#fff',
    'link-placeholder': '#555',
  };
  const typeLabel: Record<string, string> = {
    core: '◆ CORE', engine: '⚡ ENGINE', edition: '📦 EDITION',
    file: '📄 FILE', folder: '📁 FOLDER', module: '🔗 MODULE',
    'link-placeholder': '🔗 LINK',
  };
  return (
    <div style={{
      position: 'fixed', bottom: '24px', left: '50%', transform: 'translateX(-50%)',
      zIndex: 3000, padding: '10px 24px',
      background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(12px)',
      border: `1px solid ${typeColors[node.type] || '#333'}33`,
      color: '#fff', fontSize: '0.65rem', maxWidth: '420px',
      textAlign: 'center', fontFamily: 'monospace', pointerEvents: 'none',
    }}>
      <div style={{ color: typeColors[node.type], fontSize: '0.5rem', marginBottom: '4px', letterSpacing: '2px' }}>
        {typeLabel[node.type] || 'NODE'}
      </div>
      <div style={{ fontWeight: 700, marginBottom: '2px' }}>{node.label}</div>
      <div style={{ color: '#888', fontSize: '0.55rem' }}>{node.tooltip}</div>
      {node.action && <div style={{ color: '#22d3ee', fontSize: '0.45rem', marginTop: '4px' }}>CLICK TO EXECUTE</div>}
      {node.filePath && <div style={{ color: '#d4d4d8', fontSize: '0.45rem', marginTop: '4px' }}>CLICK TO READ</div>}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════════════
interface NexusCoreProps {
  linkedProject: string | null;
  projectEntries?: ScannedEntry[];
}

const NexusCore = ({ linkedProject, projectEntries }: NexusCoreProps) => {
  const [hoveredNode, setHoveredNode] = useState<GraphNode | null>(null);
  const [openDoc, setOpenDoc] = useState<{ fileName: string; content: string; truncated: boolean } | null>(null);

  const { staticNodes, staticEdges, dynamicNodes, dynamicEdges } = useMemo(() => {
    const { nodes: sn, edges: se } = buildStaticGraph();
    let dn: GraphNode[] = [];
    let de: GraphEdge[] = [];
    if (linkedProject && projectEntries && projectEntries.length > 0) {
      const result = buildProjectNodes(linkedProject, projectEntries);
      dn = result.nodes;
      de = result.edges;
    }
    return { staticNodes: sn, staticEdges: se, dynamicNodes: dn, dynamicEdges: de };
  }, [linkedProject, projectEntries]);

  const allNodes = useMemo(() => {
    const merged = [...staticNodes, ...dynamicNodes];
    if (linkedProject && projectEntries && projectEntries.length > 0) {
      return merged.filter(n => n.id !== 'link-placeholder');
    }
    return merged;
  }, [staticNodes, dynamicNodes, linkedProject, projectEntries]);

  const allEdges = useMemo(() => [...staticEdges, ...dynamicEdges], [staticEdges, dynamicEdges]);

  const nodeMap = useMemo(() => {
    const map: Record<string, GraphNode> = {};
    allNodes.forEach(n => { map[n.id] = n; });
    return map;
  }, [allNodes]);

  const handleNodeClick = useCallback(async (node: GraphNode) => {
    // If engine with an action → execute it
    if (node.action) {
      try { await fetch(node.action, { method: 'POST' }); } catch {}
      return;
    }

    // If file with a path → read and show content
    if (node.filePath) {
      // Toggle: if same doc is open, close it
      if (openDoc && openDoc.fileName === node.label) {
        setOpenDoc(null);
        return;
      }
      try {
        const res = await fetch('/api/actions/read', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ filePath: node.filePath }),
        });
        const data = await res.json();
        if (data.success) {
          setOpenDoc({ fileName: data.fileName, content: data.content, truncated: data.truncated });
        }
      } catch {}
    }
  }, [openDoc]);

  return (
    <>
      <div className="w-full h-full absolute inset-0" style={{ pointerEvents: 'auto' }}>
        <Canvas camera={{ position: [0, 2, 18], fov: 55 }} dpr={[1, 2]}>
          <color attach="background" args={['#050505']} />
          <fog attach="fog" args={['#050505', 12, 40]} />
          <ambientLight intensity={0.3} />

          {/* Orbit Controls: click+drag to rotate, scroll to zoom */}
          <OrbitControls
            enablePan={true}
            enableZoom={true}
            enableRotate={true}
            autoRotate={true}
            autoRotateSpeed={0.3}
            minDistance={5}
            maxDistance={35}
          />

          <ParticleField />

          {allEdges.map((edge, i) => {
            const from = nodeMap[edge.from];
            const to = nodeMap[edge.to];
            if (!from || !to) return null;
            return <ConnectionBeam key={`e-${i}`} start={from.position} end={to.position} color={to.color || '#444'} />;
          })}

          {allNodes.map((node) => (
            <SystemNode
              key={node.id}
              node={node}
              onHover={setHoveredNode}
              onUnhover={() => setHoveredNode(null)}
              onClick={handleNodeClick}
            />
          ))}
        </Canvas>
      </div>

      {/* Document Reader Panel */}
      {openDoc && (
        <DocumentPanel
          fileName={openDoc.fileName}
          content={openDoc.content}
          truncated={openDoc.truncated}
          onClose={() => setOpenDoc(null)}
        />
      )}

      {/* Tooltip Bar */}
      <TooltipBar node={hoveredNode} />
    </>
  );
};

export default NexusCore;