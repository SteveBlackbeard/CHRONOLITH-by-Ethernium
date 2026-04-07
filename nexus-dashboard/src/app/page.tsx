"use client";
import React from 'react';
import dynamic from 'next/dynamic';
import SovereignHUD from '@/components/SovereignHUD';

// Loading 3D Canvas via dynamic import to avoid SSR errors
const NexusCore = dynamic(() => import('@/components/NexusCore'), { 
  ssr: false,
  loading: () => <div className="absolute inset-0 bg-black" />
});

export default function Home() {
  const [linkedProject, setLinkedProject] = React.useState<string | null>(null);

  return (
    <main className="relative w-screen h-screen overflow-hidden bg-black">
      {/* Dynamic 3D Layer */}
      <NexusCore linkedProject={linkedProject} />

      {/* Cinematic Overlays */}
      <div className="vignette" />
      <div className="scanlines" />

      {/* Primary UI Layer */}
      <SovereignHUD linkedProject={linkedProject} setLinkedProject={setLinkedProject} />

      {/* Global Grain VFX (Pseudo-Grain with CSS) */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-[200]">
        <div style={{ width: '100%', height: '100%', backgroundImage: 'url("https://grainy-gradients.vercel.app/noise.svg")' }} />
      </div>
    </main>
  );
}