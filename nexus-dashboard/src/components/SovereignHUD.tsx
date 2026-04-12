"use client";
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Shield, Zap, Activity, Lock, Terminal, Globe } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Language, LANGUAGES, LANGUAGE_NAMES, translations, translateActiveCommand, translateModeLabel, translateReason, translateTrust, tt } from '@/lib/i18n';
import { LinkedSystem, ScannedEntry } from '@/lib/graphData';
import { ChainEventSnapshot, ChainStatusSnapshot, deriveDashboardSignals, StateSnapshot } from '@/lib/telemetry';
import { listTopLevelEntriesFromHandle, registerLinkedSystemHandle, removeLinkedSystemHandle } from '@/lib/filesystemHandles';

const DEFAULT_STATE: StateSnapshot = {
  merkle_root: "awaiting_crystallization",
  last_check: new Date().toISOString(),
  physics: { H: 0, H_max: 0, eta: 0, N: 0, W: 0, gini: 0 },
  drift_kl: 0,
  crystallizer_version: "3.0.1",
};

interface HUDProps {
  linkedSystems: LinkedSystem[];
  activeLinkedSystemId: string | null;
  setLinkedSystems: React.Dispatch<React.SetStateAction<LinkedSystem[]>>;
  setActiveLinkedSystemId: React.Dispatch<React.SetStateAction<string | null>>;
  language: Language;
  setLanguage: (lang: Language) => void;
  externalState?: StateSnapshot | null;
  chainEvents: ChainEventSnapshot[];
  chainStatus: ChainStatusSnapshot | null;
  setChainStatus: React.Dispatch<React.SetStateAction<ChainStatusSnapshot | null>>;
  activeCommand: string | null;
  setActiveCommand: React.Dispatch<React.SetStateAction<string | null>>;
  refreshChainEvents: () => Promise<any> | void;
  refreshSystemState: () => Promise<any> | void;
}

type DirectoryPickerWindow = Window & {
  showDirectoryPicker?: (options?: { mode?: 'read' | 'readwrite' }) => Promise<FileSystemDirectoryHandle>;
};

const SovereignHUD = ({
  linkedSystems,
  activeLinkedSystemId,
  setLinkedSystems,
  setActiveLinkedSystemId,
  language,
  setLanguage,
  externalState,
  chainEvents,
  chainStatus,
  setChainStatus,
  activeCommand,
  setActiveCommand,
  refreshChainEvents,
  refreshSystemState,
}: HUDProps) => {
  const state = externalState || DEFAULT_STATE;
  const [hoveredItem, setHoveredItem] = useState<{ id: string; text: string; x: number; y: number } | null>(null);
  const [langOpen, setLangOpen] = useState(false);
  const [viewportWidth, setViewportWidth] = useState(1440);
  const t = translations[language] || translations['EN'];
  const primaryLinkedSystem = linkedSystems.find((system) => system.id === activeLinkedSystemId) || linkedSystems[0] || null;

  useEffect(() => {
    const updateViewport = () => setViewportWidth(window.innerWidth);
    updateViewport();
    window.addEventListener('resize', updateViewport);
    return () => window.removeEventListener('resize', updateViewport);
  }, []);

  const createSystemId = (name: string) => `system-${name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')}-${Date.now().toString(36)}`;

  const upsertLinkedSystem = (
    systemName: string,
    rootPath: string,
    entries: ScannedEntry[],
    accessMode: LinkedSystem['accessMode'] = 'runtime',
  ) => {
    const normalizedRoot = (rootPath || systemName).trim();
    const existing = linkedSystems.find((system) => system.rootPath === normalizedRoot || system.name === systemName);
    const nextSystem: LinkedSystem = existing || {
      id: createSystemId(systemName),
      name: systemName,
      rootPath: normalizedRoot,
      entries: [],
      accessMode,
    };

    setLinkedSystems((prev) => {
      if (existing) {
        return prev.map((system) => system.id === existing.id ? { ...system, name: systemName, rootPath: normalizedRoot, entries, accessMode } : system);
      }
      return [...prev, { ...nextSystem, entries, accessMode }];
    });
    setActiveLinkedSystemId(nextSystem.id);
    return nextSystem.id;
  };

  const unlinkSystem = (systemId: string) => {
    removeLinkedSystemHandle(systemId);
    setLinkedSystems((prev) => {
      const remaining = prev.filter((system) => system.id !== systemId);
      setActiveLinkedSystemId((current) => current === systemId ? (remaining[0]?.id || null) : current);
      return remaining;
    });
  };

  const deriveStructuralEntries = (files: FileList) => {
    const seen = new Set<string>();
    const entries: ScannedEntry[] = [];

    for (let i = 0; i < Math.min(files.length, 64); i++) {
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

    return entries;
  };

  const handleLinkProject = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      // @ts-ignore
      const path = files[0].webkitRelativePath?.split('/')[0] || files[0].name;
      setActiveCommand(`SCANNING_${path.toUpperCase()}`);

      // Try to scan the project directory via our backend
      try {
        const res = await fetch('/api/actions/scan', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ projectPath: path }),
        });
        const data = await res.json();
        if (data.success) {
          const projectName = data.output?.match(/ROOT DIRECTORY:\s*([^\n]+)/)?.[1] || path;
          const systemId = upsertLinkedSystem(projectName, path, data.entries || [], 'runtime');
          removeLinkedSystemHandle(systemId);
          setTimeout(() => {
            refreshChainEvents();
            refreshSystemState();
          }, 500);
        } else {
          const systemId = upsertLinkedSystem(path, path, deriveStructuralEntries(files), 'structural');
          removeLinkedSystemHandle(systemId);
        }
      } catch {
        const systemId = upsertLinkedSystem(path, path, deriveStructuralEntries(files), 'structural');
        removeLinkedSystemHandle(systemId);
      }

      setTimeout(() => setActiveCommand(null), 2500);
      e.target.value = '';
    }
  };

  const openLinkFlow = useCallback(async () => {
    setActiveCommand('ACCESS_PORT');
    const pickerWindow = window as DirectoryPickerWindow;

    if (typeof pickerWindow.showDirectoryPicker === 'function') {
      try {
        const directoryHandle = await pickerWindow.showDirectoryPicker({ mode: 'read' });
        const entries = await listTopLevelEntriesFromHandle(directoryHandle);
        const systemId = upsertLinkedSystem(directoryHandle.name, directoryHandle.name, entries, 'handle');
        registerLinkedSystemHandle(systemId, directoryHandle);
        setTimeout(() => {
          refreshChainEvents();
          refreshSystemState();
        }, 300);
        setTimeout(() => setActiveCommand(null), 1500);
        return;
      } catch (error) {
        const pickerError = error as DOMException | undefined;
        if (pickerError?.name === 'AbortError') {
          setActiveCommand(null);
          return;
        }
      }
    }

    document.getElementById('project-linker')?.click();
  }, [refreshChainEvents, refreshSystemState, setActiveCommand]);

  useEffect(() => {
    const handleConfirmLink = () => {
      void openLinkFlow();
    };

    window.addEventListener('continuity:confirm-link', handleConfirmLink);
    return () => window.removeEventListener('continuity:confirm-link', handleConfirmLink);
  }, [openLinkFlow]);

  const showTooltip = (id: string, text: string, e: React.MouseEvent) => {
    setHoveredItem({ id, text, x: e.clientX, y: e.clientY });
  };

  const triggerAction = async (action: string) => {
    if (action === 'ACCESS') {
      window.dispatchEvent(new CustomEvent('continuity:open-link-modal'));
      return;
    }
    setActiveCommand(action);
    
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
          // Success: Root will fetch new state automatically via polling
          refreshChainEvents();
          refreshSystemState();
          setTimeout(() => {
            refreshChainEvents();
            refreshSystemState();
          }, 450);
        } else {
          console.error(`[SOVEREIGN] ${action} Failed:`, result.error);
        }
      } catch (err) {
        console.error(`[SOVEREIGN] Network error during ${action}:`, err);
      }
    }

    setTimeout(() => setActiveCommand(null), 2500);
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

  const signals = useMemo(() => deriveDashboardSignals({
    state,
    chainEvents,
    chainStatus,
    activeAction: activeCommand,
    linkedProject: primaryLinkedSystem?.name || null,
    linkedProjectCount: linkedSystems.length,
  }), [activeCommand, chainEvents, chainStatus, linkedSystems.length, primaryLinkedSystem?.name, state]);
  const modeLabelText = translateModeLabel(signals.modeLabel, t);
  const modeReasonText = translateReason(signals.modeReason, t);
  const chainTrustText = translateTrust(signals.chainTrustLabel, t);
  const activeCommandText = translateActiveCommand(activeCommand, t);

  const glowText = { color: '#ffffff', textShadow: '0 0 18px rgba(255,255,255,0.24)' } as const;
  const softText = { color: 'rgba(255,255,255,0.76)', textShadow: '0 0 12px rgba(255,255,255,0.16)' } as const;
  const faintText = { color: 'rgba(255,255,255,0.64)', textShadow: '0 0 10px rgba(255,255,255,0.12)' } as const;
  const isTablet = viewportWidth < 1180;
  const isPhone = viewportWidth < 780;
  const isTiny = viewportWidth < 420;
  const rootPadding = isTiny ? 10 : isPhone ? 12 : isTablet ? 18 : 24;
  const rightTabReserve = isTiny ? 28 : isPhone ? 34 : isTablet ? 46 : 56;
  const sidebarWidth = isTablet
    ? Math.max(
        isTiny ? 170 : isPhone ? 190 : 250,
        Math.min(isPhone ? 228 : 300, viewportWidth - rightTabReserve - rootPadding * 3),
      )
    : 336;
  const compactButtonStyle = isPhone
    ? { padding: '9px 14px', fontSize: '0.56rem', letterSpacing: '2px' as const }
    : isTablet
    ? { padding: '10px 18px', fontSize: '0.6rem', letterSpacing: '2.4px' as const }
    : undefined;
  const chainPreviewCount = isPhone ? 3 : 4;

  return (
    <div style={{ position: 'absolute', inset: 0, zIndex: 10, display: 'flex', padding: `${rootPadding}px`, pointerEvents: 'none', overflow: 'hidden' }}>
      {/* Sidebar */}
      <aside
        className="glass-panel hide-scrollbar"
        style={{
          width: `${sidebarWidth}px`,
          display: 'flex',
          flexDirection: 'column',
          pointerEvents: 'auto',
          padding: isPhone ? '16px 14px 14px' : isTablet ? '18px 16px 16px' : '20px 20px 18px',
          background: signals.palette.panel,
          backdropFilter: 'none',
          border: `1px solid ${signals.palette.border}`,
          boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.08), 0 18px 48px rgba(0,0,0,0.16)',
          maxHeight: `calc(100vh - ${rootPadding * 2}px)`,
          overflowY: 'auto',
        }}
      >
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: isPhone ? '10px' : '14px', marginBottom: isPhone ? '20px' : '28px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: isPhone ? '12px' : '16px', minWidth: 0 }}>
            <div
              style={{
                position: 'relative',
                width: isPhone ? '44px' : '48px',
                height: isPhone ? '44px' : '48px',
                padding: '2px',
                background: `linear-gradient(145deg, ${signals.palette.border}, rgba(255,255,255,0.06))`,
                borderRadius: '14px',
                flexShrink: 0,
                boxShadow: `0 0 0 1px ${signals.palette.border}, 0 12px 28px rgba(0,0,0,0.22)`,
              }}
            >
              <div style={{ position: 'absolute', inset: '-5px', borderRadius: '18px', border: `1px solid ${signals.palette.border}`, opacity: 0.42 }} />
              <div style={{ position: 'relative', width: '100%', height: '100%', background: '#000', borderRadius: '12px', overflow: 'hidden' }}>
                <img
                  src="/assets/branding/dawdad.png"
                  alt="Ethernium mark"
                  style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
                />
                <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(180deg, rgba(255,255,255,0.04), transparent 48%, rgba(255,255,255,0.02))', mixBlendMode: 'normal' }} />
              </div>
            </div>
            <div style={{ minWidth: 0 }}>
              <h1 className="text-gradient" style={{ fontSize: '1.25rem', fontWeight: 900, lineHeight: 1.1 }}>CONTINUITY LEGACY</h1>
              <p style={{ ...softText, fontSize: '0.55rem', letterSpacing: '3px', textTransform: 'uppercase' }}>{t['hud.brand']} // v{state.crystallizer_version}</p>
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', marginTop: '8px', padding: '4px 8px', background: signals.palette.panelSoft, border: `1px solid ${signals.palette.border}`, boxShadow: `0 0 22px ${signals.palette.accent}14` }}>
                <div className="pulse-dot" style={{ width: '6px', height: '6px', background: signals.palette.accent, boxShadow: `0 0 12px ${signals.palette.accent}` }} />
                <span style={{ ...glowText, fontSize: '0.46rem', letterSpacing: '2px', color: signals.palette.emphasis }}>{modeLabelText}</span>
              </div>
              <div style={{ ...faintText, fontSize: '0.42rem', letterSpacing: '2px', marginTop: '7px', fontFamily: 'var(--font-mono)' }}>SIGNATURE_MARK // ETHERNIUM</div>
            </div>
          </div>
          <div style={{ position: 'relative', flexShrink: 0 }}>
            <button
              onClick={() => setLangOpen(!langOpen)}
              className="btn-liquid-3d"
              style={{ padding: isPhone ? '6px 12px' : '6px 16px', fontSize: '0.6rem', borderRadius: '50px', background: '#ffffff', color: '#000' }}
              title={tt(t, 'hud.language', 'LANGUAGE')}
            >
              <Globe size={14} color="#000" style={{ marginRight: '8px' }} />
              {language}
            </button>
            <AnimatePresence>
              {langOpen && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  style={{
                    position: 'absolute',
                    top: '100%',
                     right: 0,
                     marginTop: '8px',
                     background: 'rgba(8,8,8,0.96)',
                     backdropFilter: 'none',
                     border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '10px',
                    display: 'flex',
                    flexDirection: 'column',
                    padding: '4px 0',
                    minWidth: '126px',
                    zIndex: 20,
                  }}
                >
                  {LANGUAGES.map((lang) => (
                    <div
                      key={lang}
                      onClick={() => { setLanguage(lang); setLangOpen(false); }}
                      style={{
                        padding: '8px 12px',
                        fontSize: '0.62rem',
                        fontFamily: 'var(--font-mono)',
                        cursor: 'pointer',
                        color: lang === language ? '#60a5fa' : '#fff',
                        background: lang === language ? 'rgba(255,255,255,0.05)' : 'transparent',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        gap: '10px',
                      }}
                    >
                      <span>{lang}</span>
                      <span style={{ opacity: 0.68 }}>{LANGUAGE_NAMES[lang]}</span>
                    </div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Modular Nodes */}
        <div style={{ marginBottom: '18px' }}>
          <p style={{ ...faintText, fontSize: '0.55rem', letterSpacing: '2px', textTransform: 'uppercase', marginBottom: '8px' }}>{t['hud.cluster']}</p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px' }}>
            {['LITE', 'PRO', 'OMEGA'].map((node) => (
              <div key={node} style={{ border: '1px solid rgba(255,255,255,0.05)', background: 'rgba(255,255,255,0.02)', padding: '8px', textAlign: 'center' }}>
                <p style={{ ...softText, fontSize: '0.45rem', marginBottom: '4px' }}>{node}</p>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '4px' }}>
                  <div className="pulse-dot" style={{ width: '4px', height: '4px', background: signals.palette.accent, boxShadow: `0 0 10px ${signals.palette.accent}` }} />
                  <span style={{ ...glowText, fontSize: '0.5rem', fontWeight: 700 }}>{t['hud.live']}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Command Buttons */}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: isPhone ? '10px' : '12px', marginBottom: 'auto' }}>
          <p style={{ ...faintText, fontSize: '0.6rem', letterSpacing: '3px', textTransform: 'uppercase', marginBottom: '8px' }}>{t['hud.protocols']}</p>
          <button 
            onMouseEnter={(e) => showTooltip('synth', t['hud.tooltip.synth'], e)}
            onMouseLeave={() => setHoveredItem(null)}
            onClick={() => triggerAction('CRYSTALLIZE')} 
            className="btn-liquid-3d"
            style={compactButtonStyle}
          >
            <Zap size={14} style={{ marginRight: '10px' }} /> <span>{t['hud.synth_dna']}</span>
          </button>
          <button 
            onMouseEnter={(e) => showTooltip('audit', t['hud.tooltip.audit'], e)}
            onMouseLeave={() => setHoveredItem(null)}
            onClick={() => triggerAction('AUDIT')} 
            className="btn-liquid-3d"
            style={compactButtonStyle}
          >
            <Activity size={14} style={{ marginRight: '10px' }} /> <span>{t['hud.audit_physics']}</span>
          </button>
          <button 
            onMouseEnter={(e) => showTooltip('seal', t['hud.tooltip.seal'], e)}
            onMouseLeave={() => setHoveredItem(null)}
            onClick={() => triggerAction('SEAL')} 
            className="btn-liquid-3d"
            style={compactButtonStyle}
          >
            <Lock size={14} style={{ marginRight: '10px' }} /> <span>{t['hud.seal_vault']}</span>
          </button>
          <button 
            onMouseEnter={(e) => showTooltip('access', linkedSystems.length > 0 ? t['hud.tooltip.linked'] : t['hud.tooltip.link'], e)}
            onMouseLeave={() => setHoveredItem(null)}
            onClick={() => triggerAction('ACCESS')} 
            className="btn-liquid-3d" 
            style={{ ...compactButtonStyle, marginTop: isPhone ? '8px' : '12px' }}
          >
            <Shield size={14} style={{ marginRight: '10px' }} /> <span>{linkedSystems.length > 0 ? `${tt(t, 'hud.add_system', 'ADD_SYSTEM')} // ${linkedSystems.length}` : t['hud.link_project']}</span>
          </button>
        </nav>

        {linkedSystems.length > 0 && (
          <div style={{ marginTop: '18px', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '14px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <p style={{ ...faintText, fontSize: '0.55rem', letterSpacing: '2px', textTransform: 'uppercase' }}>{tt(t, 'hud.ecosystem', 'ECOSYSTEM')}</p>
              <span style={{ ...softText, fontSize: '0.48rem', fontFamily: 'var(--font-mono)' }}>{tt(t, 'hud.systems_linked', 'SYSTEMS_LINKED')}: {linkedSystems.length}</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {linkedSystems.map((system, index) => {
                const active = system.id === activeLinkedSystemId || (!activeLinkedSystemId && index === 0);
                return (
                  <div
                    key={system.id}
                    style={{
                      display: 'grid',
                      gridTemplateColumns: '1fr auto',
                      gap: '8px',
                      padding: '8px',
                      border: `1px solid ${active ? signals.palette.accent : 'rgba(255,255,255,0.08)'}`,
                      background: active ? signals.palette.panelSoft : 'rgba(255,255,255,0.02)',
                      boxShadow: active ? `0 0 18px ${signals.palette.accent}18` : 'none',
                    }}
                  >
                    <button
                      onClick={() => setActiveLinkedSystemId(system.id)}
                      style={{ background: 'transparent', border: 'none', color: '#fff', textAlign: 'left', padding: 0, cursor: 'pointer', minWidth: 0 }}
                    >
                      <div style={{ ...glowText, fontSize: '0.55rem', letterSpacing: '1.5px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{system.name}</div>
                      <div style={{ ...softText, fontSize: '0.44rem', letterSpacing: '1.5px', fontFamily: 'var(--font-mono)' }}>
                        {system.entries.length} nodes // {tt(t, `hud.access.${system.accessMode || 'runtime'}`, (system.accessMode || 'runtime').toUpperCase())} // {system.rootPath}
                      </div>
                    </button>
                    <button
                      onClick={() => unlinkSystem(system.id)}
                      className="btn-nexus"
                      style={{ padding: '6px 10px', fontSize: '0.46rem', letterSpacing: '1.5px', alignSelf: 'center' }}
                    >
                      {tt(t, 'hud.unlink_system', 'UNLINK')}
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Event Chain */}
        <div style={{ marginTop: '18px', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '14px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <p style={{ ...faintText, fontSize: '0.55rem', letterSpacing: '2px', textTransform: 'uppercase' }}>{tt(t, 'chain.title', 'EVENT CHAIN')}</p>
            <button 
              onClick={verifyChain}
              className="btn-liquid-3d"
              style={{ padding: '4px 12px', fontSize: '0.5rem', borderRadius: '50px' }}
            >
              {tt(t, 'chain.verify', 'VERIFY')}
            </button>
          </div>
          
          {chainStatus && (
            <div style={{ marginBottom: '12px', padding: '6px', fontSize: '0.5rem', textAlign: 'center', background: chainStatus.intact ? 'rgba(34,197,94,0.1)' : 'rgba(239,68,68,0.1)', color: chainStatus.intact ? '#4ade80' : '#fca5a5', border: `1px solid ${chainStatus.intact ? 'rgba(34,197,94,0.3)' : 'rgba(239,68,68,0.3)'}` }}>
              {chainStatus.intact ? tt(t, 'chain.intact', 'CHAIN INTACT') : tt(t, 'chain.tampered', 'CHAIN TAMPERED')}
            </div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {chainEvents.slice(0, chainPreviewCount).map((ev, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.5rem', fontFamily: 'var(--font-mono)', opacity: 0.8 }}>
                <span style={{ ...glowText }}>[{ev.seq}] {ev.type}</span>
                <span style={{ ...softText }}>{ev.chain_hash?.slice(0, 8) || '00000000'}...</span>
              </div>
            ))}
            {chainEvents.length === 0 && (
               <div style={{ ...softText, fontSize: '0.5rem', fontStyle: 'italic' }}>{tt(t, 'chain.empty', 'NO EVENTS')}</div>
             )}
          </div>
        </div>

        {/* Footer */}
        <div style={{ borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '14px', marginTop: '18px' }}>
          <div style={{ ...softText, display: 'flex', justifyContent: 'space-between', fontSize: '0.5rem', fontFamily: 'var(--font-mono)' }}>
            <span>{tt(t, 'hud.root', 'ROOT')}</span>
            <span>[{state.merkle_root.slice(0, 12)}]</span>
          </div>
        </div>
      </aside>

      {/* Action VFX Overlay */}
      <AnimatePresence>
        {activeCommand && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.05 }}
            style={{ position: 'fixed', inset: 0, zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '80px', pointerEvents: 'none' }}
          >
            <div className="glass-panel" style={{ padding: isPhone ? '28px 20px' : '80px', width: isPhone ? 'min(320px, 100%)' : 'auto', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: isPhone ? '20px' : '32px', border: `1px solid ${signals.palette.border}`, background: signals.palette.panel }}>
              <motion.div animate={{ rotate: 360 }} transition={{ duration: 6, repeat: Infinity, ease: 'linear' }}>
                <Terminal size={40} color={signals.palette.emphasis} />
              </motion.div>
              <h2 style={{ fontSize: isPhone ? '1rem' : '2rem', fontWeight: 900, letterSpacing: isPhone ? '8px' : '20px', textTransform: 'uppercase', textAlign: 'center', color: signals.palette.emphasis }}>{activeCommandText}</h2>
              <div style={{ ...softText, fontSize: isPhone ? '0.52rem' : '0.62rem', letterSpacing: '3px', textTransform: 'uppercase' }}>{modeReasonText}</div>
              <div style={{ width: isPhone ? '100%' : '400px', height: '2px', background: 'rgba(255,255,255,0.1)', overflow: 'hidden' }}>
                <motion.div
                  initial={{ x: '-100%' }}
                  animate={{ x: '100%' }}
                  transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
                  style={{ width: '100%', height: '100%', background: signals.palette.accent }}
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
              background: 'rgba(8,8,8,0.96)',
              backdropFilter: 'none',
              border: '1px solid rgba(255,255,255,0.1)',
              color: '#fff',
              textShadow: '0 0 12px rgba(255,255,255,0.18)',
              fontSize: '0.65rem',
              maxWidth: isPhone ? '180px' : '240px',
              pointerEvents: 'none',
              lineHeight: 1.4,
              letterSpacing: '0.5px'
            }}
          >
            <div style={{ ...softText, fontSize: '0.5rem', marginBottom: '4px', textTransform: 'uppercase' }}>{tt(t, 'hud.protocols', 'PROTOCOLS')}</div>
            {hoveredItem.text}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SovereignHUD;

