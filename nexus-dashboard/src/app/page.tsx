"use client";
import React, { startTransition, useCallback, useState } from 'react';
import dynamic from 'next/dynamic';
import SovereignHUD from '@/components/SovereignHUD';
import { LinkedSystem } from '@/lib/graphData';
import { Language } from '@/lib/i18n';
import { ChainEventSnapshot, ChainStatusSnapshot, StateSnapshot } from '@/lib/telemetry';

// Loading 3D Canvas via dynamic import to avoid SSR errors
const NexusCore = dynamic(() => import('@/components/NexusCore'), { 
  ssr: false,
  loading: () => <div className="absolute inset-0 bg-black" />
});

function samePhysics(left?: StateSnapshot['physics'], right?: StateSnapshot['physics']) {
  if (!left && !right) return true;
  if (!left || !right) return false;
  return left.H === right.H
    && left.H_max === right.H_max
    && left.eta === right.eta
    && left.N === right.N
    && left.W === right.W
    && left.gini === right.gini;
}

function sameStateSnapshot(left: StateSnapshot | null, right: StateSnapshot | null) {
  if (!left && !right) return true;
  if (!left || !right) return false;
  return left.merkle_root === right.merkle_root
    && left.drift_kl === right.drift_kl
    && left.crystallizer_version === right.crystallizer_version
    && samePhysics(left.physics, right.physics);
}

function sameChainStatus(left: ChainStatusSnapshot | null, right: ChainStatusSnapshot | null) {
  if (!left && !right) return true;
  if (!left || !right) return false;
  return left.intact === right.intact && left.error === right.error;
}

function sameChainEvents(left: ChainEventSnapshot[], right: ChainEventSnapshot[]) {
  if (left.length !== right.length) return false;
  return left.every((entry, index) => {
    const candidate = right[index];
    return entry.seq === candidate?.seq
      && entry.type === candidate?.type
      && entry.timestamp === candidate?.timestamp
      && entry.chain_hash === candidate?.chain_hash;
  });
}

export default function Home() {
  const [linkedSystems, setLinkedSystems] = useState<LinkedSystem[]>([]);
  const [activeLinkedSystemId, setActiveLinkedSystemId] = useState<string | null>(null);
  const [language, setLanguage] = useState<Language>('EN');
  const [systemState, setSystemState] = useState<StateSnapshot | null>(null);
  const [chainEvents, setChainEvents] = useState<ChainEventSnapshot[]>([]);
  const [chainStatus, setChainStatus] = useState<ChainStatusSnapshot | null>(null);
  const [activeCommand, setActiveCommand] = useState<string | null>(null);

  const refreshSystemState = useCallback(() => {
    return fetch('/api/state')
      .then(r => r.json())
      .then((nextState: StateSnapshot) => {
        startTransition(() => {
          setSystemState((previous) => sameStateSnapshot(previous, nextState) ? previous : nextState);
        });
      })
      .catch(() => {});
  }, []);

  const refreshChainEvents = useCallback(() => {
    return fetch('/api/events')
      .then(r => r.json())
      .then((payload) => {
        const nextEvents = payload.events || [];
        startTransition(() => {
          setChainEvents((previous) => sameChainEvents(previous, nextEvents) ? previous : nextEvents);
        });
      })
      .catch(() => {});
  }, []);

  const refreshChainStatus = useCallback(() => {
    return fetch('/api/events/verify', { method: 'POST' })
      .then(r => r.json())
      .then((nextStatus: ChainStatusSnapshot) => {
        startTransition(() => {
          setChainStatus((previous) => sameChainStatus(previous, nextStatus) ? previous : nextStatus);
        });
      })
      .catch(() => {});
  }, []);

  React.useEffect(() => {
    refreshSystemState();
    refreshChainEvents();
    refreshChainStatus();

    const stateInterval = setInterval(refreshSystemState, 3500);
    const chainInterval = setInterval(refreshChainEvents, 7000);
    const verifyInterval = setInterval(refreshChainStatus, 18000);

    return () => {
      clearInterval(stateInterval);
      clearInterval(chainInterval);
      clearInterval(verifyInterval);
    };
  }, [refreshChainEvents, refreshChainStatus, refreshSystemState]);

  return (
    <main className="relative w-screen h-screen overflow-hidden bg-black">
      <div className="ethernium-dashboard-bg" aria-hidden="true">
        <div className="ethernium-dashboard-bg__shade" />
        <div className="ethernium-dashboard-bg__dots" />
        <div className="ethernium-dashboard-bg__vignette" />
      </div>
      {/* Dynamic 3D Layer */}
      <NexusCore 
        linkedSystems={linkedSystems}
        activeLinkedSystemId={activeLinkedSystemId}
        language={language}
        setLinkedSystems={setLinkedSystems}
        setActiveLinkedSystemId={setActiveLinkedSystemId}
        physics={systemState?.physics}
        drift={systemState?.drift_kl}
        merkle={systemState?.merkle_root}
        chainEvents={chainEvents}
        chainStatus={chainStatus}
        activeCommand={activeCommand}
      />

      {/* Primary UI Layer */}
      <SovereignHUD 
        linkedSystems={linkedSystems}
        activeLinkedSystemId={activeLinkedSystemId}
        setLinkedSystems={setLinkedSystems}
        setActiveLinkedSystemId={setActiveLinkedSystemId}
        language={language}
        setLanguage={setLanguage}
        externalState={systemState}
        chainEvents={chainEvents}
        chainStatus={chainStatus}
        setChainStatus={setChainStatus}
        activeCommand={activeCommand}
        setActiveCommand={setActiveCommand}
        refreshChainEvents={refreshChainEvents}
        refreshSystemState={refreshSystemState}
      />

    </main>
  );
}
