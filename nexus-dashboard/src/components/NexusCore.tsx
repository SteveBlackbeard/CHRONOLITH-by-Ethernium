"use client";
import React, { useRef, useMemo, useState, useCallback } from 'react';
import { Canvas, useFrame, extend, ThreeElement } from '@react-three/fiber';
import { Points, PointMaterial, Float, Octahedron, Sphere, Html, OrbitControls, Grid } from '@react-three/drei';
import { EffectComposer, Bloom, Vignette, Noise, ChromaticAberration } from '@react-three/postprocessing';
import * as THREE from 'three';
import { CoreShaderMaterial, BeamShaderMaterial } from './shaders/CoreShader';
import { buildStaticGraph, buildProjectNodes, GraphNode, GraphEdge, ScannedEntry } from '@/lib/graphData';
import { Language, translations } from '@/lib/i18n';

// Register materials for JSX use
extend({ CoreShaderMaterial, BeamShaderMaterial });

// Add types for JSX
declare module '@react-three/fiber' {
  interface ThreeElements {
    coreShaderMaterial: ThreeElement<typeof CoreShaderMaterial>;
    beamShaderMaterial: ThreeElement<typeof BeamShaderMaterial>;
  }
}

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

  const originalPoints = useMemo(() => new Float32Array(points), [points]);
  const ref = useRef<THREE.Points>(null!);
  const tempVec = new THREE.Vector3();
  const mouseVec = new THREE.Vector3();

  useFrame((s: any) => { 
    ref.current.rotation.y = s.clock.getElapsedTime() * 0.01; 
    ref.current.rotation.x = Math.sin(s.clock.getElapsedTime() * 0.05) * 0.05;

    mouseVec.set(s.mouse.x * 25, s.mouse.y * 20, 0); 
    
    const positions = ref.current.geometry.attributes.position.array as Float32Array;
    const originals = originalPoints;
    
    for (let i = 0; i < count; i++) {
        const ix = i * 3;
        const iy = i * 3 + 1;
        const iz = i * 3 + 2;

        tempVec.set(originals[ix], originals[iy], originals[iz]);
        const dist = tempVec.distanceTo(mouseVec);
        
        if (dist < 10.0) {
            const force = (1.0 - dist / 10.0) * 0.8;
            positions[ix] = THREE.MathUtils.lerp(positions[ix], mouseVec.x, force * 0.05);
            positions[iy] = THREE.MathUtils.lerp(positions[iy], mouseVec.y, force * 0.05);
        } else {
            positions[ix] = THREE.MathUtils.lerp(positions[ix], originals[ix], 0.05);
            positions[iy] = THREE.MathUtils.lerp(positions[iy], originals[iy], 0.05);
        }
    }
    ref.current.geometry.attributes.position.needsUpdate = true;
  });

  return (
    <Points ref={ref} positions={points} stride={3} frustumCulled={false}>
      <PointMaterial transparent color="#ffffff" size={0.04} sizeAttenuation depthWrite={false} blending={THREE.AdditiveBlending} opacity={0.3} />
    </Points>
  );
}

// ═══════════════════════════════════════════════════════════
// CONNECTION BEAM
// ═══════════════════════════════════════════════════════════
function ConnectionBeam({ start, end, color = '#ffffff' }: { start: [number, number, number]; end: [number, number, number]; color?: string }) {
  const count = 20;
  const matRef = useRef<any>(null!);
  
  useFrame((state) => {
    if (matRef.current) {
      matRef.current.u_time = state.clock.elapsedTime;
      matRef.current.u_color.set(color);
    }
  });

  const { points, progress } = useMemo(() => {
    const p = new Float32Array(count * 3);
    const pr = new Float32Array(count);
    for (let i = 0; i < count; i++) {
      const t = i / (count - 1);
      p[i * 3] = start[0] + (end[0] - start[0]) * t;
      p[i * 3 + 1] = start[1] + (end[1] - start[1]) * t;
      p[i * 3 + 2] = start[2] + (end[2] - start[2]) * t;
      pr[i] = t;
    }
    return { points: p, progress: pr };
  }, [start, end, count]);

  return (
    <Points positions={points} stride={3}>
      <bufferAttribute attach="geometry-attributes-aProgress" args={[progress, 1]} />
      <beamShaderMaterial ref={matRef} transparent depthWrite={false} blending={THREE.AdditiveBlending} />
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

  const matRefSolid = useRef<any>(null!);
  const matRefWire = useRef<any>(null!);

  useFrame((state) => {
    // Kinetic Sync logic: Flare exactly when the beam pulse (speed 0.8) hits the node edge.
    // The beam pulse peaks at flow=0.5. At node end (progress=1), this happens when fract(1-t*0.8)=0.5.
    const t = state.clock.elapsedTime;
    const syncFlare = Math.pow(Math.max(0, Math.cos(t * 0.8 * Math.PI * 2 - Math.PI)), 12.0);

    [matRefSolid, matRefWire].forEach((ref, idx) => {
      if (ref.current) {
        ref.current.u_time = t;
        ref.current.u_entropy = eta;
        ref.current.u_drift = drift;
        const combinedPulse = Math.max(isPulsing ? 1.0 : 0.0, syncFlare * 0.6);
        ref.current.u_pulse = THREE.MathUtils.lerp(ref.current.u_pulse, combinedPulse, 0.1);
        ref.current.u_baseColor.set(materialColor);
        ref.current.u_isWireframe = idx === 1 ? 1.0 : 0.0;
        // Omega Ocular Pass: Halved peak intensity (0.25) for surgically sharp visuals.
        ref.current.u_intensity = hovered ? 1.8 : (0.25 + syncFlare * 0.35);
      }
    });
  });

  // ─── 3D SHAPES ───
  if (node.shape === 'octahedron') {
    return (
      <Float speed={1.5} rotationIntensity={0.8} floatIntensity={0.5} position={node.position}>
        <group onPointerOver={pOver} onPointerOut={pOut} onClick={pClick}>
          <Octahedron args={[scale * 0.95, 0]}>
            <coreShaderMaterial 
              ref={matRefSolid} 
              transparent 
              depthWrite={false} 
              blending={THREE.NormalBlending} 
              side={THREE.DoubleSide} 
            />
          </Octahedron>
          <Octahedron args={[scale, 0]}>
            <coreShaderMaterial 
              ref={matRefWire} 
              transparent 
              depthWrite={false} 
              blending={THREE.AdditiveBlending} 
              wireframe={true} 
            />
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
            <coreShaderMaterial 
              ref={matRefSolid} 
              transparent 
              depthWrite={false} 
              blending={THREE.NormalBlending} 
              side={THREE.DoubleSide} 
            />
          </mesh>
          <mesh>
            <tetrahedronGeometry args={[scale, 0]} />
            <coreShaderMaterial 
              ref={matRefWire} 
              transparent 
              depthWrite={false} 
              blending={THREE.AdditiveBlending} 
              wireframe={true} 
            />
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
            <coreShaderMaterial 
              ref={matRefSolid} 
              transparent 
              depthWrite={false} 
              blending={THREE.NormalBlending} 
              side={THREE.DoubleSide} 
            />
          </Sphere>
          <Sphere args={[scale * 0.6, 12, 12]}>
            <coreShaderMaterial 
              ref={matRefWire} 
              transparent 
              depthWrite={false} 
              blending={THREE.AdditiveBlending} 
              wireframe={true} 
            />
          </Sphere>
          <Html distanceFactor={12} position={[0, -(scale * 0.6 + 0.4), 0]} center>
            <div style={{ color: materialColor, fontSize: '7px', whiteSpace: 'nowrap', textTransform: 'uppercase', letterSpacing: '2px', fontFamily: 'monospace' }}>
              ⚛️ {node.label}
            </div>
          </Html>
        </group>
      </Float>
    );
  }

  // 📄 DOCUMENT SHAPE (Restored Forensic Files)
  if (node.shape === 'document') {
    const isPy = node.label.endsWith('.py');
    const isJson = node.label.endsWith('.json');
    const isMd = node.label.endsWith('.md');
    
    // Specific cryptographic markers for forensic identification.
    let icon = '📄';
    if (isPy) icon = '🐍'; 
    if (isJson) icon = '💎'; 
    if (isMd) icon = '📜'; 

    return (
      <Float speed={isPy ? 2.2 : 1.4} rotationIntensity={isPy ? 1.2 : 0.5} floatIntensity={0.3} position={node.position}>
        <group onPointerOver={pOver} onPointerOut={pOut} onClick={pClick}>
          <mesh>
            <planeGeometry args={[scale * 0.8, scale * 1.1]} />
            <coreShaderMaterial 
              ref={matRefSolid} 
              transparent 
              depthWrite={false} 
              blending={THREE.NormalBlending} 
              side={THREE.DoubleSide} 
            />
          </mesh>
          <mesh position={[0, 0, 0.01]}>
            <planeGeometry args={[scale * 0.85, scale * 1.15]} />
            <coreShaderMaterial 
              ref={matRefWire} 
              transparent 
              depthWrite={false} 
              blending={THREE.AdditiveBlending} 
              wireframe={true} 
            />
          </mesh>
          <Html distanceFactor={12} position={[0, -(scale * 0.7), 0]} center>
            <div style={{ 
              color: materialColor, 
              fontSize: '6px', 
              whiteSpace: 'nowrap', 
              letterSpacing: '1px', 
              fontFamily: 'monospace', 
              display: 'flex', 
              alignItems: 'center', 
              gap: '4px',
              textShadow: '0 0 10px rgba(0,0,0,1.0)' 
            }}>
               <span style={{ fontSize: '10px', opacity: 0.9 }}>{icon}</span> {node.label}
            </div>
          </Html>
        </group>
      </Float>
    );
  }

  // 📂 FOLDER SHAPE
  if (node.shape === 'folder-icon') {
    return (
      <Float speed={1} rotationIntensity={0.2} floatIntensity={0.1} position={node.position}>
        <group onPointerOver={pOver} onPointerOut={pOut} onClick={pClick}>
          <mesh>
            <boxGeometry args={[scale * 0.9, scale * 0.7, scale * 0.2]} />
            <coreShaderMaterial 
              ref={matRefSolid} 
              transparent 
              depthWrite={false} 
              blending={THREE.NormalBlending} 
              side={THREE.DoubleSide} 
            />
          </mesh>
          <mesh>
            <boxGeometry args={[scale * 0.95, scale * 0.75, scale * 0.25]} />
            <coreShaderMaterial 
              ref={matRefWire} 
              transparent 
              depthWrite={false} 
              blending={THREE.AdditiveBlending} 
              wireframe={true} 
            />
          </mesh>
          <Html distanceFactor={12} position={[0, -(scale * 0.5), 0]} center>
            <div style={{ color: materialColor, fontSize: '6px', whiteSpace: 'nowrap', letterSpacing: '1px', fontFamily: 'monospace' }}>
               /{node.label}
            </div>
          </Html>
        </group>
      </Float>
    );
  }

  return null;
}

// ═══════════════════════════════════════════════════════════
// UI OVERLAYS & CONTROLS
// ═══════════════════════════════════════════════════════════
function Atmosphere() {
  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    state.camera.position.x += Math.sin(t * 0.4) * 0.001;
    state.camera.position.y += Math.cos(t * 0.3) * 0.001;
  });
  return null;
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

  const allNodes = useMemo(() => [...staticNodes, ...dynamicNodes], [staticNodes, dynamicNodes]);
  const allEdges = useMemo(() => [...staticEdges, ...dynamicEdges], [staticEdges, dynamicEdges]);

  React.useEffect(() => {
    const fetchP = () => fetch('/api/state').then(r=>r.json()).then(d => {
      if (d.physics) setPhysics({ eta: d.physics.eta, drift_kl: d.drift_kl || 0.0 });
    }).catch(()=>{});
    fetchP();
    const iv = setInterval(fetchP, 5000);
    return () => clearInterval(iv);
  }, []);

  React.useEffect(() => {
    const es = new EventSource('/api/watch');
    es.addEventListener('file-change', (e) => {
      try {
        const data = JSON.parse(e.data);
        const filename = data.path.split(/[/\\]/).pop();
        let targetId = '';
        allNodes.forEach(n => {
          if (n.label === filename || (n.filePath && n.filePath.endsWith(filename))) {
            targetId = n.id;
          }
        });
        if (targetId) {
          setPulsingNodes(prev => new Set(prev).add(targetId));
          setToastMsg({ msg: translations[language][`watch.${data.event}`] || data.event, detail: filename });
          setTimeout(() => setPulsingNodes(prev => { const n = new Set(prev); n.delete(targetId); return n; }), 2000);
          setTimeout(() => setToastMsg(null), 4000);
        }
      } catch(ex){}
    });
    return () => es.close();
  }, [allNodes, language]);

  const handleNodeClick = async (node: GraphNode) => {
    if (node.type === 'link-placeholder') { setUnlinkModal('link'); return; }
    if (node.action) {
      setToastMsg({ msg: `EXECUTING: ${node.label}...` });
      try { await fetch(node.action); setToastMsg({ msg: `SUCCESS: ${node.label} completed.` }); }
      catch(e){ setToastMsg({ msg: `FAILURE: ${node.label} failed.` }); }
      setTimeout(() => setToastMsg(null), 3000);
      return;
    }
    if (node.filePath) {
      try {
        const res = await fetch(`/api/read?path=${encodeURIComponent(node.filePath)}`);
        const data = await res.json();
        setOpenDoc({ fileName: node.label, content: data.content, truncated: data.truncated });
      } catch(e){}
    }
  };

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative', background: '#020617', overflow: 'hidden' }}>
      <Canvas camera={{ position: [0, 0, 20], fov: 45 }}>
        <color attach="background" args={['#020617']} />
        <fog attach="fog" args={['#020617', 10, 50]} />
        <ambientLight intensity={0.4} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        
        <ParticleField />
        <Atmosphere />

        {allEdges.map((edge, i) => {
          const from = allNodes.find(n => n.id === edge.from);
          const to = allNodes.find(n => n.id === edge.to);
          if (!from || !to) return null;
          return <ConnectionBeam key={`edge-${i}`} start={from.position} end={to.position} color={from.color} />;
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

        <Grid infiniteGrid fadeDistance={50} sectionSize={5} sectionColor="#1e293b" cellColor="#0f172a" />
        <OrbitControls enableDamping dampingFactor={0.02} rotateSpeed={0.5} />

        <EffectComposer>
          <Bloom luminanceThreshold={1.2} intensity={0.18} levels={8} mipmapBlur />
          <Vignette eskil={false} offset={0.1} darkness={1.1} />
          <Noise opacity={0.05} />
          <ChromaticAberration offset={new THREE.Vector2(0.0015, 0.0015)} />
        </EffectComposer>
      </Canvas>

      {/* TOP HUD */}
      <div style={{ position: 'absolute', top: 30, left: '50%', transform: 'translateX(-50%)', textAlign: 'center', pointerEvents: 'none' }}>
        <h1 style={{ color: '#fff', fontSize: '1.2rem', margin: 0, letterSpacing: '8px', fontWeight: 200, opacity: 0.8 }}>
          NEXUS OPERATING SYSTEM
        </h1>
        <div style={{ color: '#22d3ee', fontSize: '0.6rem', letterSpacing: '4px', marginTop: '5px' }}>
          PHASE 10: CONTINUITY IMMUTABLE FORENSICS
        </div>
      </div>

      {/* NODE INFO OVERLAY */}
      {hoveredNode && (
        <div style={{
          position: 'absolute', bottom: 40, left: 40, background: 'rgba(2, 6, 23, 0.85)', padding: '25px', 
          border: '1px solid #1e293b', borderRadius: '4px', color: '#fff', width: '300px',
          backdropFilter: 'blur(10px)', borderLeft: `4px solid ${hoveredNode.color || '#fff'}`
        }}>
          <div style={{ color: '#64748b', fontSize: '0.6rem', marginBottom: '8px', letterSpacing: '2px' }}>MODULE IDENTIFIER</div>
          <div style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '5px' }}>{hoveredNode.label}</div>
          <div style={{ color: '#94a3b8', fontSize: '0.8rem', lineHeight: '1.4' }}>{hoveredNode.tooltip}</div>
          <div style={{ marginTop: '15px', display: 'flex', gap: '10px' }}>
             <div style={{ background: '#0f172a', padding: '5px 10px', fontSize: '0.6rem', border: '1px solid #1e293b' }}>
               ID: {hoveredNode.id}
             </div>
             <div style={{ background: '#0f172a', padding: '5px 10px', fontSize: '0.6rem', border: '1px solid #1e293b' }}>
               TYPE: {hoveredNode.type.toUpperCase()}
             </div>
          </div>
        </div>
      )}

      {/* FILE VIEWER */}
      {openDoc && (
        <div style={{
          position: 'absolute', top: '10%', left: '15%', width: '70%', height: '80%', background: '#09090b',
          border: '1px solid #27272a', zIndex: 100, display: 'flex', flexDirection: 'column', color: '#e4e4e7'
        }}>
          <div style={{ padding: '15px', borderBottom: '1px solid #27272a', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.8rem', letterSpacing: '2px' }}>FILE_STREAM // {openDoc.fileName}</span>
            <button onClick={() => setOpenDoc(null)} style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer', fontSize: '1.2rem' }}>×</button>
          </div>
          <div style={{ flex: 1, padding: '20px', overflow: 'auto', fontFamily: 'monospace', fontSize: '0.85rem', lineHeight: '1.6', background: '#000' }}>
            {openDoc.truncated && <div style={{ color: '#f59e0b', marginBottom: '10px' }}>[!] LARGE FILE TRUNCATED FOR PERFORMANCE</div>}
            <pre style={{ margin: 0 }}>{openDoc.content}</pre>
          </div>
        </div>
      )}

      {/* TOAST NOTIFICATIONS */}
      {toastMsg && (
        <div style={{
          position: 'absolute', top: 100, right: 30, background: 'rgba(2, 6, 23, 0.9)', padding: '15px 25px', 
          borderLeft: '4px solid #22d3ee', borderTop: '1px solid #1e293b', borderRight: '1px solid #1e293b', borderBottom: '1px solid #1e293b',
          color: '#fff', zIndex: 1000, animation: 'slideIn 0.3s ease-out'
        }}>
          <div style={{ fontSize: '0.8rem', fontWeight: 600 }}>{toastMsg.msg}</div>
          {toastMsg.detail && <div style={{ fontSize: '0.6rem', color: '#94a3b8', marginTop: '4px' }}>{toastMsg.detail}</div>}
        </div>
      )}
    </div>
  );
};

interface NexusCoreProps {
  linkedProject: string | null;
  projectEntries?: ScannedEntry[];
  language: Language;
  setLinkedProject: (project: string | null) => void;
  setProjectEntries: (entries: ScannedEntry[]) => void;
}

export default NexusCore;