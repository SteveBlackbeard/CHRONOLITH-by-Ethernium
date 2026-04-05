import { useEffect, useRef, useState } from 'react';
import ForceGraph3D from 'react-force-graph-3d';
import * as THREE from 'three';

// Realistic mock data symbolizing Ethernium Continuity Ecosystem
const CONTINUITY_DATA = {
  nodes: [
    { id: 'master', group: 0, label: 'Memory Core (STATE.json)', val: 20 },
    
    // Lite Subsystem
    { id: 'lite', group: 1, label: 'Lite Edition v2.1', val: 15 },
    { id: 'lite_cli', group: 1, label: 'run_continuity_lite.py', val: 10 },
    { id: 'lite_tests', group: 1, label: 'test_lite_logic.py', val: 5 },
    
    // Pro Subsystem
    { id: 'pro', group: 2, label: 'Pro Edition v2.1', val: 15 },
    { id: 'pro_crypto', group: 2, label: 'automation_common.py (RFC 6962)', val: 12 },
    { id: 'pro_secret', group: 2, label: 'secret_detector.py (15 Patterns)', val: 10 },
    { id: 'pro_hooks', group: 2, label: 'hook_utils.py (Fail-Closed)', val: 10 },
    
    // Omega Subsystem
    { id: 'omega', group: 3, label: 'Omega Edition v2.1', val: 15 },
    { id: 'omega_brain', group: 3, label: 'cognitive_map.py', val: 10 },
    { id: 'omega_rag', group: 3, label: 'ChromaDB Nexus', val: 12 },
    
    // Context Files
    { id: 'handoff', group: 4, label: 'LIVE_HANDOFF.md', val: 8 },
    { id: 'context', group: 4, label: 'PROJECT_CONTEXT.md', val: 8 },
    { id: 'dna', group: 4, label: 'PROJECT_DNA.md', val: 8 },
  ],
  links: [
    // Core connections
    { source: 'master', target: 'lite' },
    { source: 'master', target: 'pro' },
    { source: 'master', target: 'omega' },
    { source: 'master', target: 'dna' },
    
    // Lite
    { source: 'lite', target: 'lite_cli' },
    { source: 'lite', target: 'lite_tests' },
    { source: 'lite_cli', target: 'context' },
    { source: 'lite_cli', target: 'handoff' },
    
    // Pro
    { source: 'pro', target: 'pro_crypto' },
    { source: 'pro', target: 'pro_secret' },
    { source: 'pro', target: 'pro_hooks' },
    { source: 'pro_hooks', target: 'handoff' },
    { source: 'pro_crypto', target: 'dna' },
    
    // Omega
    { source: 'omega', target: 'omega_brain' },
    { source: 'omega', target: 'omega_rag' },
    { source: 'omega_brain', target: 'context' },
    { source: 'omega_rag', target: 'dna' }
  ]
};

export default function NetworkGraph() {
  const fgRef = useRef<any>();
  const [dimensions, setDimensions] = useState({ width: window.innerWidth, height: window.innerHeight });

  useEffect(() => {
    const handleResize = () => {
      setDimensions({ width: window.innerWidth, height: window.innerHeight });
    };
    window.addEventListener('resize', handleResize);
    
    // Auto-rotate camera
    let angle = 0;
    const interval = setInterval(() => {
      if (fgRef.current) {
        fgRef.current.cameraPosition({
          x: 200 * Math.cos(angle),
          z: 200 * Math.sin(angle)
        });
        angle += Math.PI / 600;
      }
    }, 20);
    
    return () => {
      window.removeEventListener('resize', handleResize);
      clearInterval(interval);
    };
  }, []);

  return (
    <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'auto' }}>
      <ForceGraph3D
        ref={fgRef}
        width={dimensions.width}
        height={dimensions.height}
        graphData={CONTINUITY_DATA}
        backgroundColor="rgba(0,0,0,0)"
        nodeColor={(node: any) => {
          if (node.group === 0) return '#ffffff'; // Core
          if (node.group === 1) return '#00f0ff'; // Lite
          if (node.group === 2) return '#ff00ff'; // Pro
          if (node.group === 3) return '#8a2be2'; // Omega
          return '#00ff88'; // Context docs
        }}
        nodeLabel="label"
        nodeRelSize={6}
        linkOpacity={0.3}
        linkWidth={1.5}
        linkColor={() => 'rgba(255, 255, 255, 0.2)'}
        enableNodeDrag={false}
        enableNavigationControls={true}
        nodeThreeObject={(node: any) => {
          // Custom glowing nodes
          const material = new THREE.MeshPhongMaterial({ 
            color: node.group === 0 ? '#ffffff' : (node.group === 1 ? '#00f0ff' : (node.group === 2 ? '#ff00ff' : (node.group === 3 ? '#8a2be2' : '#00ff88'))),
            emissive: node.group === 0 ? '#ffffff' : (node.group === 1 ? '#00f0ff' : (node.group === 2 ? '#ff00ff' : (node.group === 3 ? '#8a2be2' : '#00ff88'))),
            emissiveIntensity: 0.8,
            transparent: true,
            opacity: 0.9
          });
          const geometry = new THREE.SphereGeometry(Math.sqrt(node.val) * 2);
          return new THREE.Mesh(geometry, material);
        }}
      />
    </div>
  );
}
