"use client";
import React, { useState, useEffect } from 'react';
import { Shield, Zap, Hexagon, Activity, Lock, Terminal, Globe } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Language, LANGUAGES, translations } from '@/lib/i18n';

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
  crystallizer_version: "3.0.1",
};

interface HUDProps {
  linkedProject: string | null;
  setLinkedProject: (project: string | null) => void;
  setProjectEntries: (entries: any[]) => void;
  language: Language;
  setLanguage: (lang: Language) => void;
}

const SovereignHUD = ({ linkedProject, setLinkedProject, setProjectEntries, language, setLanguage }: HUDProps) => {
  const [activeAction, setActiveAction] = useState<string | null>(null);
  const [state, setState] = useState<StateData>(DEFAULT_STATE);
  const [hoveredItem, setHoveredItem] = useState<{ id: string; text: string; x: number; y: number } | null>(null);
  const [langOpen, setLangOpen] = useState(false);
  const [chainEvents, setChainEvents] = useState<any[]>([]);
  const [chainStatus, setChainStatus] = useState<{ intact: boolean; error?: string } | null>(null);
  const t = translations[language] || translations['EN'];

  const fetchEvents = () => fetch('/api/events').then(r => r.json()).then(d => setChainEvents(d.events || [])).catch(() => {});

  useEffect(() => {
    fetch('/api/state').then(r => r.json()).then(setState).catch(() => {});
    fetchEvents();
    const interval = setInterval(() => {
      fetch('/api/state').then(r => r.json()).then(setState).catch(() => {});
      fetchEvents();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleLinkProject = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      // @ts-ignore
      const path = files[0].webkitRelativePath?.split('/')[0] || files[0].name;
      setLinkedProject(path);
      setActiveAction(`SCANNING_${path.toUpperCase()}`);

      // Try to scan the project directory via our backend
      try {
        const res = await fetch('/api/actions/scan', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ projectPath: path }),
        });
        const data = await res.json();
        if (data.success) {
          if ('ACCESS' === 'ACCESS') {
            const projectName = data.output?.match(/ROOT DIRECTORY:\s*([^\n]+)/)?.[1] || path;
            setLinkedProject(projectName);
            setProjectEntries(data.entries || []);
          }
          setTimeout(() => {
            fetch('/api/state').then(r => r.json()).then(setState).catch(() => {});
            fetchEvents();
          }, 500);
        } else {
          // If scan fails (expected for browser-uploaded dirs), generate nodes from file list
          const seen = new Set<string>();
          const entries: any[] = [];
          for (let i = 0; i < Math.min(files.length, 50); i++) {
            // @ts-ignore
            const rel = files[i].webkitRelativePath || files[i].name;
            const parts = rel.split('/');
            if (parts.length > 1 && !seen.has(parts[1])) {
              seen.add(parts[1]);
              entries.push({
                name: parts[1],
                type: parts.length > 2 ? 'dir' : 'file',
              });
            }
          }
          setProjectEntries(entries);
        }
      } catch {
        // Fallback: derive structure from uploaded file paths
        const seen = new Set<string>();
        const entries: any[] = [];
        for (let i = 0; i < Math.min(files.length, 50); i++) {
          // @ts-ignore
          const rel = files[i].webkitRelativePath || files[i].name;
          const parts = rel.split('/');
          if (parts.length > 1 && !seen.has(parts[1])) {
            seen.add(parts[1]);
            entries.push({
              name: parts[1],
              type: parts.length > 2 ? 'dir' : 'file',
            });
          }
        }
        setProjectEntries(entries);
      }

      setTimeout(() => setActiveAction(null), 2500);
    }
  };

  const showTooltip = (id: string, text: string, e: React.MouseEvent) => {
    setHoveredItem({ id, text, x: e.clientX, y: e.clientY });
  };

  const triggerAction = async (action: string) => {
    if (action === 'ACCESS') {
      document.getElementById('project-linker')?.click();
      return;
    }
    setActiveAction(action);
    
    // Map button actions to API endpoints or internal logic
    const endpointMap: Record<string, string> = {
      'CRYSTALLIZE': '/api/actions/crystallize',
      'AUDIT': '/api/actions/audit',
      'SEAL': '/api/actions/seal',
    };

    const endpoint = endpointMap[action];
    
    if (endpoint) {
      try {
        console.log(`[SOVEREIGN] Triggering ${action} via ${endpoint}`);
        const response = await fetch(endpoint, { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
          // Success: Refresh telemetry to show new state
          const newState = await fetch('/api/state').then(r => r.json());
          setState(newState);
        } else {
          console.error(`[SOVEREIGN] ${action} Failed:`, result.error);
        }
      } catch (err) {
        console.error(`[SOVEREIGN] Network error during ${action}:`, err);
      }
    }

    setTimeout(() => setActiveAction(null), 2500);
  };

  const verifyChain = async () => {
    setChainStatus(null);
    try {
      const res = await fetch('/api/events/verify', { method: 'POST' });
      const data = await res.json();
      setChainStatus(data);
    } catch (e: any) {
      setChainStatus({ intact: false, error: e.message });
    }
  };

  const healthLabel = state.physics.eta >= 0.75
    ? t['hud.health.healthy'] : state.physics.eta >= 0.50
    ? t['hud.health.moderate'] : t['hud.health.severe'];

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
            <p style={{ fontSize: '0.55rem', color: '#71717a', letterSpacing: '3px', textTransform: 'uppercase' }}>{t['hud.brand']} // v{state.crystallizer_version}</p>
          </div>
        </div>

        {/* Physics Telemetry */}
        <div style={{ padding: '16px', border: '1px solid rgba(255,255,255,0.05)', background: 'rgba(255,255,255,0.02)', marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <div className="pulse-dot" />
            <span style={{ fontSize: '0.65rem', fontWeight: 700, letterSpacing: '2px', color: healthColor }}>{healthLabel}</span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div 
              onMouseEnter={(e) => showTooltip('entropy', t['hud.tooltip.entropy'], e)}
              onMouseLeave={() => setHoveredItem(null)}
            >
              <p style={{ fontSize: '0.55rem', color: '#71717a', textTransform: 'uppercase', letterSpacing: '1px' }}>{t['hud.entropy']}</p>
              <p style={{ fontSize: '1.8rem', fontWeight: 900, fontVariantNumeric: 'tabular-nums' }}>{state.physics.H.toFixed(4)}</p>
            </div>
            <div
              onMouseEnter={(e) => showTooltip('balance', t['hud.tooltip.balance'], e)}
              onMouseLeave={() => setHoveredItem(null)}
            >
              <p style={{ fontSize: '0.55rem', color: '#71717a', textTransform: 'uppercase', letterSpacing: '1px' }}>{t['hud.balance']}</p>
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
              <p style={{ fontSize: '0.5rem', color: '#52525b' }}>{t['hud.blocks']}</p>
              <p style={{ fontSize: '0.75rem', fontWeight: 600 }}>{state.physics.N}</p>
            </div>
            <div
              onMouseEnter={(e) => showTooltip('drift', t['hud.tooltip.drift'], e)}
              onMouseLeave={() => setHoveredItem(null)}
            >
              <p style={{ fontSize: '0.5rem', color: '#52525b' }}>{t['hud.drift']}</p>
              <p style={{ fontSize: '0.75rem', fontWeight: 600 }}>{state.drift_kl.toFixed(4)}</p>
            </div>
          </div>
        </div>

        {/* Modular Nodes */}
        <div style={{ marginBottom: '24px' }}>
          <p style={{ fontSize: '0.55rem', color: '#52525b', letterSpacing: '2px', textTransform: 'uppercase', marginBottom: '8px' }}>{t['hud.cluster']}</p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px' }}>
            {['LITE', 'PRO', 'OMEGA'].map((node) => (
              <div key={node} style={{ border: '1px solid rgba(255,255,255,0.05)', background: 'rgba(255,255,255,0.02)', padding: '8px', textAlign: 'center' }}>
                <p style={{ fontSize: '0.45rem', color: '#71717a', marginBottom: '4px' }}>{node}</p>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '4px' }}>
                  <div className="pulse-dot" style={{ width: '4px', height: '4px', background: '#fff' }} />
                  <span style={{ fontSize: '0.5rem', fontWeight: 700 }}>{t['hud.live']}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Command Buttons */}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: 'auto' }}>
          <p style={{ fontSize: '0.55rem', color: '#52525b', letterSpacing: '2px', textTransform: 'uppercase', marginBottom: '4px' }}>{t['hud.protocols']}</p>
          <button 
            onMouseEnter={(e) => showTooltip('synth', t['hud.tooltip.synth'], e)}
            onMouseLeave={() => setHoveredItem(null)}
            onClick={() => triggerAction('CRYSTALLIZE')} 
            className="btn-nexus"
          >
            <Zap size={14} /> <span>{t['hud.synth_dna']}</span>
          </button>
          <button 
            onMouseEnter={(e) => showTooltip('audit', t['hud.tooltip.audit'], e)}
            onMouseLeave={() => setHoveredItem(null)}
            onClick={() => triggerAction('AUDIT')} 
            className="btn-nexus"
          >
            <Activity size={14} /> <span>{t['hud.audit_physics']}</span>
          </button>
          <button 
            onMouseEnter={(e) => showTooltip('seal', t['hud.tooltip.seal'], e)}
            onMouseLeave={() => setHoveredItem(null)}
            onClick={() => triggerAction('SEAL')} 
            className="btn-nexus"
          >
            <Lock size={14} /> <span>{t['hud.seal_vault']}</span>
          </button>
          <button 
            onMouseEnter={(e) => showTooltip('access', linkedProject ? t['hud.tooltip.linked'] : t['hud.tooltip.link'], e)}
            onMouseLeave={() => setHoveredItem(null)}
            onClick={() => triggerAction('ACCESS')} 
            className="btn-nexus primary" 
            style={{ marginTop: '8px' }}
          >
            <Shield size={14} /> <span>{linkedProject ? `${t['hud.linked']} ${linkedProject}` : t['hud.link_project']}</span>
          </button>
        </nav>

        {/* Event Chain */}
        <div style={{ marginTop: '24px', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <p style={{ fontSize: '0.55rem', color: '#52525b', letterSpacing: '2px', textTransform: 'uppercase' }}>{t['chain.title'] || 'EVENT CHAIN'}</p>
            <button 
              onClick={verifyChain}
              style={{ padding: '4px 8px', fontSize: '0.45rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', cursor: 'pointer', borderRadius: '2px', textTransform: 'uppercase' }}
            >
              {t['chain.verify'] || 'VERIFY'}
            </button>
          </div>
          
          {chainStatus && (
            <div style={{ marginBottom: '12px', padding: '6px', fontSize: '0.5rem', textAlign: 'center', background: chainStatus.intact ? 'rgba(34,197,94,0.1)' : 'rgba(239,68,68,0.1)', color: chainStatus.intact ? '#4ade80' : '#fca5a5', border: `1px solid ${chainStatus.intact ? 'rgba(34,197,94,0.3)' : 'rgba(239,68,68,0.3)'}` }}>
              {chainStatus.intact ? (t['chain.intact'] || '✓ CHAIN INTACT') : (t['chain.tampered'] || '✗ CHAIN TAMPERED')}
            </div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {chainEvents.slice(0, 5).map((ev, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.5rem', fontFamily: 'monospace', opacity: 0.8 }}>
                <span style={{ color: '#fff' }}>[{ev.seq}] {ev.type}</span>
                <span style={{ color: '#71717a' }}>{ev.chain_hash.slice(0, 8)}...</span>
              </div>
            ))}
            {chainEvents.length === 0 && (
               <div style={{ fontSize: '0.5rem', color: '#71717a', fontStyle: 'italic' }}>{t['chain.empty'] || 'No events'}</div>
            )}
          </div>
        </div>

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

      {/* Project Linker Hidden Input */}
      <input 
        id="project-linker"
        type="file" 
        // @ts-ignore
        webkitdirectory="" 
        directory="" 
        onChange={handleLinkProject} 
        style={{ display: 'none' }} 
      />

      {/* Tooltip Overlay */}
      <AnimatePresence>
        {hoveredItem && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            style={{
              position: 'fixed',
              left: hoveredItem.x + 20,
              top: hoveredItem.y - 20,
              zIndex: 2000,
              padding: '12px 16px',
              background: 'rgba(0,0,0,0.8)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255,255,255,0.1)',
              color: '#fff',
              fontSize: '0.65rem',
              maxWidth: '240px',
              pointerEvents: 'none',
              lineHeight: 1.4,
              letterSpacing: '0.5px'
            }}
          >
            <div style={{ color: '#71717a', fontSize: '0.5rem', marginBottom: '4px', textTransform: 'uppercase' }}>Protocol_Info</div>
            {hoveredItem.text}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Telemetry Overlay */}
      <div style={{ position: 'absolute', top: '32px', right: '48px', textAlign: 'right', opacity: 0.15, pointerEvents: 'none', display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '16px' }}>
        <p style={{ fontSize: '0.55rem', fontFamily: 'monospace', lineHeight: 1.8 }}>
          CONTINUITY_LEGACY_MIRROR<br />
          CRYSTALLIZER_ENGINE: v{state.crystallizer_version}<br />
          MERKLE: {state.merkle_root.slice(0, 24)}...<br />
          MASS: {state.physics.W.toLocaleString()} bytes
        </p>
      </div>

      {/* Language Selector Overlay */}
      <div style={{ position: 'absolute', top: '24px', right: '350px', zIndex: 50, pointerEvents: 'auto' }}>
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setLangOpen(!langOpen)}
            style={{
              background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255,255,255,0.1)', color: '#fff',
              padding: '6px 12px', fontSize: '0.65rem', fontFamily: 'monospace',
              display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer',
              borderRadius: '4px'
            }}
          >
            <Globe size={14} color="#60a5fa" />
            {language}
          </button>
          <AnimatePresence>
            {langOpen && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                style={{
                  position: 'absolute', top: '100%', right: 0, marginTop: '8px',
                  background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(255,255,255,0.1)', borderRadius: '4px',
                  display: 'flex', flexDirection: 'column', padding: '4px 0',
                  minWidth: '80px'
                }}
              >
                {LANGUAGES.map((lang) => (
                  <div
                    key={lang}
                    onClick={() => { setLanguage(lang); setLangOpen(false); }}
                    style={{
                      padding: '8px 16px', fontSize: '0.65rem', fontFamily: 'monospace',
                      cursor: 'pointer', color: lang === language ? '#60a5fa' : '#fff',
                      background: lang === language ? 'rgba(255,255,255,0.05)' : 'transparent',
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(255,255,255,0.1)')}
                    onMouseLeave={(e) => (e.currentTarget.style.background = lang === language ? 'rgba(255,255,255,0.05)' : 'transparent')}
                  >
                    {lang}
                  </div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};

export default SovereignHUD;