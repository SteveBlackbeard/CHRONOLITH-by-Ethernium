"use client";
import React, { useState, useEffect } from 'react';
import { Shield, Zap, Hexagon, Activity, Lock, Terminal } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface PhysicsData {
  H: number;
  H_max: number;
  eta: number;
  N: number;
  W: number;
  gini: number;
}

interface StateData {
  merkle_root: string;
  last_check: string;
  physics: PhysicsData;
  drift_kl: number;
  crystallizer_version: string;
}

const DEFAULT_STATE: StateData = {
  merkle_root: "awaiting_crystallization",
  last_check: new Date().toISOString(),
  physics: { H: 0, H_max: 0, eta: 0, N: 0, W: 0, gini: 0 },
  drift_kl: 0,
  crystallizer_version: "3.0.0",
};

const SovereignHUD = () => {
  const [activeAction, setActiveAction] = useState<string | null>(null);
  const [state, setState] = useState<StateData>(DEFAULT_STATE);

  useEffect(() => {
    fetch('/api/state').then(r => r.json()).then(setState).catch(() => {});
  }, []);

  const triggerAction = (action: string) => {
    setActiveAction(action);
    setTimeout(() => setActiveAction(null), 2500);
  };

  const healthLabel = state.physics.eta >= 0.75
    ? "HEALTHY" : state.physics.eta >= 0.50
    ? "MODERATE_DRIFT" : "SEVERE_DRIFT";

  const healthColor = state.physics.eta >= 0.75
    ? "#ffffff" : state.physics.eta >= 0.50
    ? "#a1a1aa" : "#ef4444";

  return (
    <div style={{ position: 'absolute', inset: 0, zIndex: 10, display: 'flex', padding: '24px', pointerEvents: 'none', overflow: 'hidden' }}>
      {/* Sidebar */}
      <aside className="glass-panel" style={{ width: '340px', display: 'flex', flexDirection: 'column', pointerEvents: 'auto', padding: '24px', background: 'rgba(0,0,0,0.4)', backdropFilter: 'blur(40px)' }}>
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '40px' }}>
          <div style={{ width: '40px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#fff' }}>
            <Hexagon size={18} color="#000" />
          </div>
          <div>
            <h1 className="text-gradient" style={{ fontSize: '1.25rem', fontWeight: 900, lineHeight: 1.1 }}>CONTINUITY LEGACY</h1>
            <p style={{ fontSize: '0.55rem', color: '#71717a', letterSpacing: '3px', textTransform: 'uppercase' }}>by Ethernium // v{state.crystallizer_version}</p>
          </div>
        </div>

        {/* Physics Telemetry */}
        <div style={{ padding: '16px', border: '1px solid rgba(255,255,255,0.05)', background: 'rgba(255,255,255,0.02)', marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <div className="pulse-dot" />
            <span style={{ fontSize: '0.65rem', fontWeight: 700, letterSpacing: '2px', color: healthColor }}>{healthLabel}</span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div>
              <p style={{ fontSize: '0.55rem', color: '#71717a', textTransform: 'uppercase', letterSpacing: '1px' }}>Entropy H(Ω)</p>
              <p style={{ fontSize: '1.8rem', fontWeight: 900, fontVariantNumeric: 'tabular-nums' }}>{state.physics.H.toFixed(4)}</p>
            </div>
            <div>
              <p style={{ fontSize: '0.55rem', color: '#71717a', textTransform: 'uppercase', letterSpacing: '1px' }}>Balance η</p>
              <p style={{ fontSize: '1.8rem', fontWeight: 900, fontVariantNumeric: 'tabular-nums' }}>{state.physics.eta.toFixed(3)}</p>
            </div>
          </div>

          <div style={{ marginTop: '12px', display: 'flex', gap: '16px' }}>
            <div>
              <p style={{ fontSize: '0.5rem', color: '#52525b' }}>H_max</p>
              <p style={{ fontSize: '0.75rem', fontWeight: 600 }}>{state.physics.H_max.toFixed(2)} bits</p>
            </div>
            <div>
              <p style={{ fontSize: '0.5rem', color: '#52525b' }}>Gini</p>
              <p style={{ fontSize: '0.75rem', fontWeight: 600 }}>{Math.abs(state.physics.gini).toFixed(3)}</p>
            </div>
            <div>
              <p style={{ fontSize: '0.5rem', color: '#52525b' }}>Blocks</p>
              <p style={{ fontSize: '0.75rem', fontWeight: 600 }}>{state.physics.N}</p>
            </div>
            <div>
              <p style={{ fontSize: '0.5rem', color: '#52525b' }}>D_KL</p>
              <p style={{ fontSize: '0.75rem', fontWeight: 600 }}>{state.drift_kl.toFixed(4)}</p>
            </div>
          </div>
        </div>

        {/* Command Buttons */}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: 'auto' }}>
          <p style={{ fontSize: '0.55rem', color: '#52525b', letterSpacing: '2px', textTransform: 'uppercase', marginBottom: '4px' }}>Protocols</p>
          <button onClick={() => triggerAction('CRYSTALLIZE')} className="btn-nexus">
            <Zap size={14} /> <span>SYNTH_DNA</span>
          </button>
          <button onClick={() => triggerAction('AUDIT')} className="btn-nexus">
            <Activity size={14} /> <span>AUDIT_PHYSICS</span>
          </button>
          <button onClick={() => triggerAction('SEAL')} className="btn-nexus">
            <Lock size={14} /> <span>SEAL_VAULT</span>
          </button>
          <button onClick={() => triggerAction('ACCESS')} className="btn-nexus primary" style={{ marginTop: '8px' }}>
            <Shield size={14} /> <span>OPEN_SOVEREIGN</span>
          </button>
        </nav>

        {/* Footer */}
        <div style={{ borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '16px', marginTop: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', opacity: 0.3, fontSize: '0.5rem', fontFamily: 'monospace' }}>
            <span>ROOT</span>
            <span>[{state.merkle_root.slice(0, 12)}]</span>
          </div>
        </div>
      </aside>

      {/* Action VFX Overlay */}
      <AnimatePresence>
        {activeAction && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.05 }}
            style={{ position: 'fixed', inset: 0, zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '80px', pointerEvents: 'none' }}
          >
            <div className="glass-panel" style={{ padding: '80px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '32px', border: '1px solid rgba(255,255,255,0.4)' }}>
              <motion.div animate={{ rotate: 360 }} transition={{ duration: 6, repeat: Infinity, ease: 'linear' }}>
                <Terminal size={40} color="#fff" />
              </motion.div>
              <h2 style={{ fontSize: '2rem', fontWeight: 900, letterSpacing: '20px', textTransform: 'uppercase' }}>{activeAction}</h2>
              <div style={{ width: '400px', height: '2px', background: 'rgba(255,255,255,0.1)', overflow: 'hidden' }}>
                <motion.div
                  initial={{ x: '-100%' }}
                  animate={{ x: '100%' }}
                  transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
                  style={{ width: '100%', height: '100%', background: '#fff' }}
                />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Telemetry Overlay */}
      <div style={{ position: 'absolute', top: '32px', right: '48px', textAlign: 'right', opacity: 0.15, pointerEvents: 'none' }}>
        <p style={{ fontSize: '0.55rem', fontFamily: 'monospace', lineHeight: 1.8 }}>
          CONTINUITY_LEGACY_MIRROR<br />
          CRYSTALLIZER_ENGINE: v{state.crystallizer_version}<br />
          MERKLE: {state.merkle_root.slice(0, 24)}...<br />
          MASS: {state.physics.W.toLocaleString()} bytes
        </p>
      </div>
    </div>
  );
};

export default SovereignHUD;