"use client";
import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Points, PointMaterial, Float, Octahedron, Sphere, Html } from '@react-three/drei';
import * as THREE from 'three';

interface NexusCoreProps {
  linkedProject: string | null;
}

function ConnectionBeams({ count = 50, start = [0, 0, 0], end = [5, 5, 0] }) {
  const points = useMemo(() => {
    const p = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const t = i / count;
      p[i * 3] = start[0] + (end[0] - start[0]) * t;
      p[i * 3 + 1] = start[1] + (end[1] - start[1]) * t;
      p[i * 3 + 2] = start[2] + (end[2] - start[2]) * t;
    }
    return p;
  }, [count, start, end]);

  const ref = useRef<THREE.Points>(null!);
  useFrame((state: any) => {
    const t = state.clock.getElapsedTime();
    ref.current.position.y = Math.sin(t) * 0.05;
  });

  return (
    <Points ref={ref} positions={points} stride={3}>
      <PointMaterial transparent color="#ffffff" size={0.05} sizeAttenuation depthWrite={false} blending={THREE.AdditiveBlending} />
    </Points>
  );
}

function ParticleField({ count = 5000 }) {
  const points = useMemo(() => {
    const p = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      p[i * 3] = (Math.random() - 0.5) * 20;
      p[i * 3 + 1] = (Math.random() - 0.5) * 20;
      p[i * 3 + 2] = (Math.random() - 0.5) * 20;
    }
    return p;
  }, [count]);

  const ref = useRef<THREE.Points>(null!);

  useFrame((state: any) => {
    const t = state.clock.getElapsedTime();
    ref.current.rotation.y = t * 0.05;
  });

  return (
    <Points ref={ref} positions={points} stride={3} frustumCulled={false}>
      <PointMaterial transparent color="#ffffff" size={0.01} sizeAttenuation={true} depthWrite={false} blending={THREE.AdditiveBlending} />
    </Points>
  );
}

function Rig() {
  const { camera, mouse } = useThree();
  const vec = new THREE.Vector3();
  return useFrame((state: any) => {
    camera.position.lerp(vec.set(mouse.x * 2, mouse.y * 1, 10), 0.05);
    camera.lookAt(0, 0, 0);
  });
}

const NexusCore = ({ linkedProject }: NexusCoreProps) => {
  return (
    <div className="w-full h-full absolute inset-0 pointer-events-none">
      <Canvas camera={{ position: [0, 0, 10], fov: 60 }} dpr={[1, 2]}>
        <color attach="background" args={['#000000']} />
        <fog attach="fog" args={['#000000', 5, 20]} />
        <ambientLight intensity={0.5} />
        
        <ParticleField />
        
        {/* Central Core: Continuity Legacy */}
        <Float speed={2} rotationIntensity={1} floatIntensity={1}>
           <Octahedron args={[1.5, 0]}>
             <meshBasicMaterial color="#ffffff" wireframe />
             <Html distanceFactor={10} position={[0, -2, 0]} center>
               <div style={{ color: '#fff', fontSize: '10px', whiteSpace: 'nowrap', textTransform: 'uppercase', letterSpacing: '4px', opacity: 0.5 }}>CONTINUITY_LEGACY</div>
             </Html>
           </Octahedron>
        </Float>

        {/* Linked Project Node */}
        <Float speed={3} position={[6, 3, 0]} rotationIntensity={2}>
          <Sphere args={[0.8, 16, 16]}>
            <meshBasicMaterial color={linkedProject ? "#ffffff" : "#333"} wireframe />
            <Html distanceFactor={10} position={[0, 1.5, 0]} center>
              <div style={{ color: linkedProject ? '#fff' : '#52525b', fontSize: '8px', whiteSpace: 'nowrap', textTransform: 'uppercase', letterSpacing: '2px', background: 'rgba(0,0,0,0.5)', padding: '4px 8px', border: '1px solid rgba(255,255,255,0.1)' }}>
                {linkedProject ? `LINKED: ${linkedProject}` : 'ENLAZA_TU_PROYECTO'}
              </div>
            </Html>
          </Sphere>
        </Float>

        {linkedProject && <ConnectionBeams start={[0, 0, 0]} end={[6, 3, 0]} />}

        <Rig />
      </Canvas>
    </div>
  );
};

export default NexusCore;