"use client";
import React, { useRef, useMemo, useState, useCallback } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial, Float, Octahedron, Sphere, Html, OrbitControls, Grid } from '@react-three/drei';
import { EffectComposer, Bloom, Vignette, Noise, ChromaticAberration } from '@react-three/postprocessing';
import * as THREE from 'three';
import { buildStaticGraph, buildProjectNodes, GraphNode, GraphEdge, ScannedEntry } from '@/lib/graphData';
import { Language, translations } from '@/lib/i18n';
import { CoreShaderMaterial, BeamShaderMaterial } from './shaders/CoreShader';

// ═══════════════════════════════════════════════════════════
// PARTICLE FIELD
// ═══════════════════════════════════════════════════════════
function ParticleField({ count = 2000 }) {
  const points = useMemo(() => {
    const p = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      p[i * 3]     = (Math.random() - 0.5) * 60;
      p[i * 3 + 1] = (Math.random() - 0.5) * 60;
      p[i * 3 + 2] = (Math.random() - 0.5) * 60;
    }
    return p;
  }, [count]);
  const ref = useRef<THREE.Points>(null!);
  useFrame((s: any) => { 
    ref.current.rotation.y = s.clock.getElapsedTime() * 0.015; 
    ref.current.rotation.x = Math.sin(s.clock.getElapsedTime() * 0.05) * 0.1;
  });
  return (
    <Points ref={ref} positions={points} stride={3} frustumCulled={false}>
      <PointMaterial transparent color="#ffffff" size={0.03} sizeAttenuation depthWrite={false} blending={THREE.AdditiveBlending} opacity={0.6} />
    </Points>
  );
}

// ═══════════════════════════════════════════════════════════
// CONNECTION BEAM
// ═══════════════════════════════════════════════════════════
function ConnectionBeam({ start, end, color = '#ffffff' }: { start: [number, number, number]; end: [number, number, number]; color?: string }) {
  const count = 20;
  const matRef = useRef<THREE.ShaderMaterial>(null!);
  useFrame((state) => {
    if (matRef.current) {
      matRef.current.uniforms.u_time.value = state.clock.elapsedTime;
      matRef.current.uniforms.u_color.value.set(color);
    }
  });

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
      <shaderMaterial ref={matRef} args={[BeamShaderMaterial]} transparent depthWrite={false} blending={THREE.AdditiveBlending} />
      <PointMaterial transparent color={color} size={0.06} sizeAttenuation depthWrite={false} blending={THREE.AdditiveBlending} opacity={0.4} />
    </Points>
  );
}

// ═══════════════════════════════════════════════════════════
// SYSTEM NODE
// ═══════════════════════════════════════════════════════════
function SystemNode({
  node, isPulsing, eta = 1.0, drift = 0.0, onHover, onUnhover, onClick,
}: {
  node: GraphNode;
  isPulsing?: boolean;
  eta?: number;
  drift?: number;
  onHover: (n: GraphNode) => void;
  onUnhover: () => void;
  onClick: (n: GraphNode) => void;
}) {
  const [hovered, setHovered] = useState(false);
  const baseColor = node.color || '#888';
  const activeColor = hovered ? '#60a5fa' : baseColor;
  const materialColor = isPulsing ? '#ffffff' : activeColor;
  const scale = (hovered ? node.size * 1.15 : node.size) * (isPulsing ? 1.4 : 1);

  const pOver = useCallback(() => { setHovered(true); onHover(node); }, [node, onHover]);
  const pOut = useCallback(() => { setHovered(false); onUnhover(); }, [onUnhover]);
  const pClick = useCallback(() => onClick(node), [node, onClick]);

  // AAA Chromatic Fix: Unique memory for every node instance
  const uniformsSolid = useMemo(() => CoreShaderMaterial.clone(), []);
  const uniformsWire = useMemo(() => CoreShaderMaterial.clone(), []);
  
  const matRefSolid = useRef<THREE.ShaderMaterial>(null!);
  const matRefWire = useRef<THREE.ShaderMaterial>(null!);

  useFrame((state) => {
    [matRefSolid, matRefWire].forEach((ref, idx) => {
      if (ref.current) {
        const u = ref.current.uniforms;
        u.u_time.value = state.clock.elapsedTime;
        u.u_entropy.value = eta;
        u.u_drift.value = drift;
        u.u_pulse.value = THREE.MathUtils.lerp(u.u_pulse.value, isPulsing ? 1.0 : 0.0, 0.1);
        u.u_baseColor.value.set(materialColor);
        u.u_isWireframe.value = idx === 1 ? 1.0 : 0.0;
        u.u_intensity.value = hovered ? 2.5 : 1.2;
      }
    });
  });

  // ─── 3D SHAPES ───
  if (node.shape === 'octahedron') {
    return (
      <Float speed={1.5} rotationIntensity={0.8} floatIntensity={0.5} position={node.position}>
        <group onPointerOver={pOver} onPointerOut={pOut} onClick={pClick}>
          {/* Inner Glass Body */}
          <Octahedron args={[scale * 0.95, 0]}>
            <shaderMaterial ref={matRefSolid} uniforms={uniformsSolid} transparent depthWrite={false} blending={THREE.NormalBlending} side={THREE.DoubleSide} />
          </Octahedron>
          {/* Outer Energy Lattice */}
          <Octahedron args={[scale, 0]}>
            <shaderMaterial ref={matRefWire} uniforms={uniformsWire} transparent depthWrite={false} blending={THREE.AdditiveBlending} wireframe={true} />
          </Octahedron>
          <Html distanceFactor={12} position={[0, -(scale + 0.8), 0]} center>
            <div style={{ color: materialColor, fontSize: '9px', whiteSpace: 'nowrap', textTransform: 'uppercase', letterSpacing: '3px', opacity: 0.7, fontFamily: 'monospace' }}>
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
            <tetrahedronGeometry args={[scale * 0.95, 0]} />
            <shaderMaterial ref={matRefSolid} uniforms={uniformsSolid} transparent depthWrite={false} blending={THREE.NormalBlending} side={THREE.DoubleSide} />
          </mesh>
          <mesh>
            <tetrahedronGeometry args={[scale, 0]} />
            <shaderMaterial ref={matRefWire} uniforms={uniformsWire} transparent depthWrite={false} blending={THREE.AdditiveBlending} wireframe={true} />
          </mesh>
          <Html distanceFactor={12} position={[0, -(scale + 0.5), 0]} center>
            <div style={{ color: materialColor, fontSize: '7px', whiteSpace: 'nowrap', textTransform: 'uppercase', letterSpacing: '2px', fontFamily: 'monospace' }}>
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
          <Sphere args={[scale * 0.55, 12, 12]}>
            <shaderMaterial ref={matRefSolid} uniforms={uniformsSolid} transparent depthWrite={false} blending={THREE.NormalBlending} side={THREE.DoubleSide} />
          </Sphere>
          <Sphere args={[scale * 0.6, 12, 12]}>
            <shaderMaterial ref={matRefWire} uniforms={uniformsWire} transparent depthWrite={false} blending={THREE.AdditiveBlending} wireframe={true} />
          </Sphere>
          <Html distanceFactor={12} position={[0, -(scale * 0.6 + 0.4), 0]} center>
            <div style={{ color: materialColor, fontSize: '7px', whiteSpace: 'nowrap', textTransform: 'uppercase', letterSpacing: '2px', fontFamily: 'monospace' }}>
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
            cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            transform: hovered ? 'scale(1.4) translateY(-5px)' : 'scale(1)',
            opacity: isPulsing ? 1 : (hovered ? 1 : 0.7),
            padding: '12px',
            background: hovered ? 'rgba(255,255,255,0.03)' : 'none',
            borderRadius: '12px',
            border: hovered ? `1px solid ${labelColor}33` : '1px solid transparent',
            backdropFilter: hovered ? 'blur(8px)' : 'none',
            boxShadow: (hovered || isPulsing) ? `0 0 20px ${isPulsing ? '#fff' : labelColor}33` : 'none'
          }}
        >
          <div style={{ 
            fontSize: '1.8rem', 
            filter: isPulsing ? 'drop-shadow(0 0 12px #fff)' : hovered ? `drop-shadow(0 0 8px ${labelColor})` : 'grayscale(0.5)',
            transition: 'filter 0.3s'
          }}>
            {icon}
          </div>
          <div style={{
            color: isPulsing ? '#fff' : hovered ? '#fff' : labelColor,
            fontSize: '7px', fontFamily: 'monospace', fontWeight: 700,
            whiteSpace: 'nowrap', letterSpacing: '2px', textTransform: 'uppercase',
            textShadow: hovered ? `0 0 10px ${labelColor}` : 'none',
            transition: 'all 0.3s'
          }}>
            {node.label}
          </div>
        </div>
      </Html>
    </group>
  );
}

// ═══════════════════════════════════════════════════════════
// DOCUMENT READER PANEL
// ═══════════════════════════════════════════════════════════
function DocumentPanel({ fileName, content, truncated, onClose, language }: {
  fileName: string; content: string; truncated: boolean; onClose: () => void; language: Language;
}) {
  const t = translations[language];
  const clickToClose = language === 'ES' ? 'CLIC PARA CERRAR' : 'CLICK TO CLOSE';
  const truncatedMsg = language === 'ES' ? '⚠ Contenido truncado a 10,000 caracteres.' : '⚠ Content truncated at 10,000 characters.';

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
          {clickToClose}
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
            {truncatedMsg}
          </div>
        )}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// TOOLTIP BAR
// ═══════════════════════════════════════════════════════════
function TooltipBar({ node, language }: { node: GraphNode | null; language: Language }) {
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
  const execText = language === 'ES' ? 'CLIC PARA EJECUTAR' : 'CLICK TO EXECUTE';
  const readText = language === 'ES' ? 'CLIC PARA LEER' : 'CLICK TO READ';

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
      {node.action && <div style={{ color: '#22d3ee', fontSize: '0.45rem', marginTop: '4px' }}>{execText}</div>}
      {node.filePath && <div style={{ color: '#d4d4d8', fontSize: '0.45rem', marginTop: '4px' }}>{readText}</div>}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// ATMospheric Camera Motion
// ═══════════════════════════════════════════════════════════
function AtmosphericCamera() {
  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    state.camera.position.x += Math.sin(t * 0.4) * 0.001;
    state.camera.position.y += Math.cos(t * 0.3) * 0.001;
    state.camera.rotation.z += Math.sin(t * 0.2) * 0.0002;
  });
  return null;
}

// ═══════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════════════
interface NexusCoreProps {
  linkedProject: string | null;
  projectEntries?: ScannedEntry[];
  language: Language;
  setLinkedProject: (project: string | null) => void;
  setProjectEntries: (entries: ScannedEntry[]) => void;
}

const NexusCore = ({ linkedProject, projectEntries, language, setLinkedProject, setProjectEntries }: NexusCoreProps) => {
  const [hoveredNode, setHoveredNode] = useState<GraphNode | null>(null);
  const [openDoc, setOpenDoc] = useState<{ fileName: string; content: string; truncated: boolean } | null>(null);
  const [unlinkModal, setUnlinkModal] = useState<string | null>(null);
  const [pulsingNodes, setPulsingNodes] = useState<Set<string>>(new Set());
  const [toastMsg, setToastMsg] = useState<{ msg: string; detail?: string } | null>(null);
  const [physics, setPhysics] = useState({ eta: 1.0, drift_kl: 0.0 });

  const { staticNodes, staticEdges, dynamicNodes, dynamicEdges } = useMemo(() => {
    const { nodes: sn, edges: se } = buildStaticGraph(language);
    let dn: GraphNode[] = [];
    let de: GraphEdge[] = [];
    if (linkedProject && projectEntries && projectEntries.length > 0) {
      const result = buildProjectNodes(linkedProject, projectEntries, language);
      dn = result.nodes;
      de = result.edges;
    }
    return { staticNodes: sn, staticEdges: se, dynamicNodes: dn, dynamicEdges: de };
  }, [linkedProject, projectEntries, language]);

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

  React.useEffect(() => {
    const fetchP = () => fetch('/api/state').then(r=>r.json()).then(d => {
      if (d.physics) setPhysics({ eta: d.physics.eta, drift_kl: d.drift_kl || 0.0 });
    }).catch(()=>{});
    fetchP();
    const iv = setInterval(fetchP, 5000);
    return () => clearInterval(iv);
  }, []);

  // Synaptic Live Wire (SSE File Watcher)
  React.useEffect(() => {
    const es = new EventSource('/api/watch');
    
    es.addEventListener('file-change', (e) => {
      try {
        const data = JSON.parse(e.data);
        const filename = data.path.split(/[/\\]/).pop();
        
        let targetId = '';
        // Find corresponding node
        allNodes.forEach(n => {
          if (n.label === filename || (n.filePath && n.filePath.endsWith(filename))) {
            targetId = n.id;
          }
        });

        if (targetId) {
          setPulsingNodes(prev => new Set(prev).add(targetId));
          setToastMsg({ msg: translations[language][`watch.${data.event}`] || data.event, detail: filename });
          
          setTimeout(() => {
            setPulsingNodes(prev => {
              const next = new Set(prev);
              next.delete(targetId);
              return next;
            });
          }, 1500);

          setTimeout(() => setToastMsg(null), 3000);
        }
      } catch {}
    });
    
    es.addEventListener('connected', (e) => {
      try {
        const data = JSON.parse(e.data);
        setToastMsg({ msg: translations[language]['watch.connection'] || 'SYNAPTIC LINK ACTIVE', detail: '' });
        setTimeout(() => setToastMsg(null), 3000);
      } catch {}
    });

    return () => es.close();
  }, [allNodes, language]);

  const handleNodeClick = useCallback(async (node: GraphNode) => {
    // If it's the click-to-link node
    if (node.id === 'link-placeholder') {
      document.getElementById('project-linker')?.click();
      return;
    }

    // If it's a linked project module, offer to unlink
    if (node.type === 'module' && node.id.startsWith('project-')) {
      setUnlinkModal(node.label);
      return;
    }

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
              isPulsing={pulsingNodes.has(node.id)}
              eta={physics.eta}
              drift={physics.drift_kl}
              onHover={setHoveredNode}
              onUnhover={() => setHoveredNode(null)}
              onClick={handleNodeClick}
            />
          ))}

          {/* Cyber Corporate Post-Processing and Subgrid */}
          <Grid 
            position={[0, -5, 0]} 
            args={[100, 100]} 
            cellSize={2} 
            cellThickness={0.5} 
            cellColor="#1e293b" 
            sectionSize={10} 
            sectionThickness={1} 
            sectionColor="#334155" 
            fadeDistance={60} 
            fadeStrength={1.5} 
          />
          <ambientLight intensity={0.2} />
          <EffectComposer>
            <Bloom luminanceThreshold={1.2} luminanceSmoothing={0.5} intensity={1.8} mipmapBlur />
            <ChromaticAberration offset={new THREE.Vector2(0.0015, 0.0015)} />
            <Vignette eskil={false} offset={0.1} darkness={1.1} />
            <Noise opacity={0.04} />
          </EffectComposer>
        </Canvas>
      </div>

      {/* Document Reader Panel */}
      {openDoc && (
        <DocumentPanel
          fileName={openDoc.fileName}
          content={openDoc.content}
          truncated={openDoc.truncated}
          onClose={() => setOpenDoc(null)}
          language={language}
        />
      )}

      {/* Unlink Confirmation Modal */}
      {unlinkModal && (
        <div style={{
          position: 'fixed', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', zIndex: 6000,
          background: 'rgba(0,0,0,0.92)', backdropFilter: 'blur(10px)', border: '1px solid rgba(255,100,100,0.3)',
          padding: '24px 32px', textAlign: 'center', fontFamily: 'monospace', color: '#fff',
          display: 'flex', flexDirection: 'column', gap: '12px', borderRadius: '4px',
          boxShadow: '0px 10px 40px rgba(0,0,0,0.8)'
        }}>
          <div style={{ fontSize: '1rem', letterSpacing: '2px', fontWeight: 700, color: '#fca5a5' }}>
            {translations[language]['graph.unlink.title'] || 'Unlink this project?'}
          </div>
          <div style={{ color: '#aaa', fontSize: '0.75rem', marginBottom: '8px' }}>
            {unlinkModal}
          </div>
          <div style={{ display: 'flex', gap: '16px', justifyContent: 'center' }}>
            <button 
              onClick={() => { setLinkedProject(null); setProjectEntries([]); setUnlinkModal(null); }}
              style={{ background: 'rgba(255,100,100,0.2)', border: '1px solid rgba(255,100,100,0.5)', padding: '6px 20px', color: '#fca5a5', cursor: 'pointer', borderRadius: '2px', transition: 'background 0.2s' }}
              onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,100,100,0.3)'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(255,100,100,0.2)'}
            >
              {translations[language]['graph.unlink.yes'] || 'YES'}
            </button>
            <button 
              onClick={() => setUnlinkModal(null)}
              style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', padding: '6px 20px', color: '#fff', cursor: 'pointer', borderRadius: '2px', transition: 'background 0.2s' }}
              onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.2)'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.1)'}
            >
              {translations[language]['graph.unlink.no'] || 'NO'}
            </button>
          </div>
        </div>
      )}

      {/* Synaptic Watcher Toast */}
      {toastMsg && (
        <div style={{
          position: 'fixed', top: '32px', left: '50%', transform: 'translateX(-50%)', zIndex: 7000,
          background: 'rgba(96, 165, 250, 0.1)', border: '1px solid rgba(96, 165, 250, 0.4)',
          backdropFilter: 'blur(10px)', padding: '8px 16px', borderRadius: '4px',
          display: 'flex', alignItems: 'center', gap: '8px', pointerEvents: 'none',
          boxShadow: '0 0 20px rgba(96, 165, 250, 0.2)'
        }}>
          <div className="pulse-dot" style={{ background: '#60a5fa', width: '6px', height: '6px' }} />
          <span style={{ color: '#60a5fa', fontSize: '0.65rem', fontFamily: 'monospace', fontWeight: 700, textTransform: 'uppercase' }}>
            {toastMsg.msg}
          </span>
          {toastMsg.detail && (
            <span style={{ color: '#fff', fontSize: '0.65rem', fontFamily: 'monospace' }}>
              {toastMsg.detail}
            </span>
          )}
        </div>
      )}

      {/* Tooltip Bar */}
      <TooltipBar node={hoveredNode} language={language} />
    </>
  );
};

export default NexusCore;