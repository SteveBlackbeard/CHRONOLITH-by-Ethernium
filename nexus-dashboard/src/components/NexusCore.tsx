"use client";
import React, { useRef, useMemo, useState, useCallback } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Points, PointMaterial, Float, Octahedron, Sphere, Html } from '@react-three/drei';
import * as THREE from 'three';
import { buildStaticGraph, buildProjectNodes, GraphNode, GraphEdge, ScannedEntry } from '@/lib/graphData';

// ═══════════════════════════════════════════════════════════
// PARTICLE FIELD (ambient background)
// ═══════════════════════════════════════════════════════════
function ParticleField({ count = 3000 }) {
  const points = useMemo(() => {
    const p = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      p[i * 3] = (Math.random() - 0.5) * 30;
      p[i * 3 + 1] = (Math.random() - 0.5) * 30;
      p[i * 3 + 2] = (Math.random() - 0.5) * 30;
    }
    return p;
  }, [count]);

  const ref = useRef<THREE.Points>(null!);
  useFrame((state: any) => {
    ref.current.rotation.y = state.clock.getElapsedTime() * 0.03;
  });

  return (
    <Points ref={ref} positions={points} stride={3} frustumCulled={false}>
      <PointMaterial transparent color="#ffffff" size={0.008} sizeAttenuation depthWrite={false} blending={THREE.AdditiveBlending} />
    </Points>
  );
}

// ═══════════════════════════════════════════════════════════
// CONNECTION BEAM (particle stream between two positions)
// ═══════════════════════════════════════════════════════════
function ConnectionBeam({ start, end }: { start: [number, number, number]; end: [number, number, number] }) {
  const count = 30;
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

  const ref = useRef<THREE.Points>(null!);
  useFrame((state: any) => {
    ref.current.position.y = Math.sin(state.clock.getElapsedTime() * 2) * 0.02;
  });

  return (
    <Points ref={ref} positions={points} stride={3}>
      <PointMaterial transparent color="#ffffff" size={0.03} sizeAttenuation depthWrite={false} blending={THREE.AdditiveBlending} opacity={0.4} />
    </Points>
  );
}

// ═══════════════════════════════════════════════════════════
// SYSTEM NODE (renders the correct shape per node type)
// ═══════════════════════════════════════════════════════════
function SystemNode({
  node,
  onHover,
  onUnhover,
  onClick,
}: {
  node: GraphNode;
  onHover: (node: GraphNode) => void;
  onUnhover: () => void;
  onClick: (node: GraphNode) => void;
}) {
  const [hovered, setHovered] = useState(false);

  const handlePointerOver = useCallback(() => {
    setHovered(true);
    onHover(node);
  }, [node, onHover]);

  const handlePointerOut = useCallback(() => {
    setHovered(false);
    onUnhover();
  }, [onUnhover]);

  const handleClick = useCallback(() => {
    onClick(node);
  }, [node, onClick]);

  const scale = hovered ? node.size * 1.2 : node.size;
  const color = hovered ? '#60a5fa' : (node.color || '#888888');

  // ─── 3D Shape nodes ───
  if (node.shape === 'octahedron') {
    return (
      <Float speed={1.5} rotationIntensity={0.8} floatIntensity={0.5} position={node.position}>
        <group
          onPointerOver={handlePointerOver}
          onPointerOut={handlePointerOut}
          onClick={handleClick}
        >
          <Octahedron args={[scale, 0]}>
            <meshBasicMaterial color={color} wireframe />
          </Octahedron>
          <Html distanceFactor={12} position={[0, -(scale + 0.8), 0]} center>
            <div style={{
              color: '#fff', fontSize: '9px', whiteSpace: 'nowrap',
              textTransform: 'uppercase', letterSpacing: '3px', opacity: 0.6,
              textAlign: 'center', fontFamily: 'monospace',
            }}>
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
        <group
          onPointerOver={handlePointerOver}
          onPointerOut={handlePointerOut}
          onClick={handleClick}
        >
          <mesh>
            <tetrahedronGeometry args={[scale, 0]} />
            <meshBasicMaterial color={color} wireframe />
          </mesh>
          <Html distanceFactor={12} position={[0, -(scale + 0.6), 0]} center>
            <div style={{
              color: hovered ? '#60a5fa' : '#aaa', fontSize: '7px', whiteSpace: 'nowrap',
              textTransform: 'uppercase', letterSpacing: '2px',
              textAlign: 'center', fontFamily: 'monospace',
            }}>
              {node.label}
            </div>
          </Html>
        </group>
      </Float>
    );
  }

  if (node.shape === 'sphere') {
    return (
      <Float speed={2.5} rotationIntensity={0.5} floatIntensity={0.4} position={node.position}>
        <group
          onPointerOver={handlePointerOver}
          onPointerOut={handlePointerOut}
          onClick={handleClick}
        >
          <Sphere args={[scale * 0.6, 12, 12]}>
            <meshBasicMaterial color={color} wireframe />
          </Sphere>
          <Html distanceFactor={12} position={[0, -(scale * 0.6 + 0.5), 0]} center>
            <div style={{
              color: hovered ? '#60a5fa' : '#aaa', fontSize: '7px', whiteSpace: 'nowrap',
              textTransform: 'uppercase', letterSpacing: '2px',
              textAlign: 'center', fontFamily: 'monospace',
            }}>
              {node.label}
            </div>
          </Html>
        </group>
      </Float>
    );
  }

  // ─── DOCUMENT / FOLDER ICONS (Html in 3D) ───
  const isFolder = node.shape === 'folder-icon';
  const icon = isFolder ? '📁' : '📄';

  return (
    <group position={node.position}>
      <Html distanceFactor={10} center>
        <div
          onMouseEnter={() => { setHovered(true); onHover(node); }}
          onMouseLeave={() => { setHovered(false); onUnhover(); }}
          onClick={() => onClick(node)}
          style={{
            cursor: node.action ? 'pointer' : 'default',
            display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2px',
            transition: 'transform 0.2s, opacity 0.2s',
            transform: hovered ? 'scale(1.3)' : 'scale(1)',
            opacity: hovered ? 1 : 0.6,
          }}
        >
          <span style={{ fontSize: `${Math.max(12, node.size * 28)}px`, filter: 'grayscale(0.8)' }}>
            {icon}
          </span>
          <span style={{
            color: hovered ? '#60a5fa' : '#666',
            fontSize: '6px',
            fontFamily: 'monospace',
            whiteSpace: 'nowrap',
            letterSpacing: '0.5px',
            maxWidth: '80px',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}>
            {node.label}
          </span>
        </div>
      </Html>
    </group>
  );
}

// ═══════════════════════════════════════════════════════════
// CAMERA RIG
// ═══════════════════════════════════════════════════════════
function Rig() {
  const { camera, mouse } = useThree();
  const vec = new THREE.Vector3();
  useFrame(() => {
    camera.position.lerp(vec.set(mouse.x * 3, mouse.y * 2, 16), 0.03);
    camera.lookAt(0, 0, 0);
  });
  return null;
}

// ═══════════════════════════════════════════════════════════
// TOOLTIP OVERLAY (2D, positioned at pointer)
// ═══════════════════════════════════════════════════════════
function Tooltip3D({ node }: { node: GraphNode | null }) {
  if (!node) return null;
  return (
    <div style={{
      position: 'fixed', bottom: '32px', left: '50%', transform: 'translateX(-50%)',
      zIndex: 3000, padding: '12px 20px',
      background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(12px)',
      border: '1px solid rgba(255,255,255,0.1)',
      color: '#fff', fontSize: '0.7rem', maxWidth: '360px',
      textAlign: 'center', letterSpacing: '0.5px', lineHeight: 1.5,
      fontFamily: 'monospace',
      pointerEvents: 'none',
      transition: 'opacity 0.2s',
    }}>
      <div style={{ color: '#60a5fa', fontSize: '0.55rem', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '2px' }}>
        {node.type === 'engine' ? '⚡ ENGINE' : node.type === 'edition' ? '📦 EDITION' : node.type === 'core' ? '◆ CORE' : node.type === 'file' ? '📄 FILE' : '📁 MODULE'}
      </div>
      <div style={{ fontWeight: 700, marginBottom: '4px' }}>{node.label}</div>
      <div style={{ color: '#999', fontSize: '0.6rem' }}>{node.tooltip}</div>
      {node.action && <div style={{ color: '#60a5fa', fontSize: '0.5rem', marginTop: '6px' }}>CLICK TO EXECUTE</div>}
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

  // Build the graph
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

  // Merge all nodes for position lookups
  const allNodes = useMemo(() => {
    const merged = [...staticNodes, ...dynamicNodes];
    // If project is linked, hide the placeholder
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
    if (node.action) {
      try {
        await fetch(node.action, { method: 'POST' });
      } catch (err) {
        console.error('[NEXUS] Action failed:', err);
      }
    }
  }, []);

  return (
    <>
      <div className="w-full h-full absolute inset-0" style={{ pointerEvents: 'auto' }}>
        <Canvas camera={{ position: [0, 0, 16], fov: 60 }} dpr={[1, 2]}>
          <color attach="background" args={['#000000']} />
          <fog attach="fog" args={['#000000', 10, 35]} />
          <ambientLight intensity={0.4} />

          <ParticleField />

          {/* Render all connection beams */}
          {allEdges.map((edge, i) => {
            const fromNode = nodeMap[edge.from];
            const toNode = nodeMap[edge.to];
            if (!fromNode || !toNode) return null;
            return <ConnectionBeam key={`edge-${i}`} start={fromNode.position} end={toNode.position} />;
          })}

          {/* Render all nodes */}
          {allNodes.map((node) => (
            <SystemNode
              key={node.id}
              node={node}
              onHover={setHoveredNode}
              onUnhover={() => setHoveredNode(null)}
              onClick={handleNodeClick}
            />
          ))}

          <Rig />
        </Canvas>
      </div>

      {/* Tooltip at bottom of screen */}
      <Tooltip3D node={hoveredNode} />
    </>
  );
};

export default NexusCore;