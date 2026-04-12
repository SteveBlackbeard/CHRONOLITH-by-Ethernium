"use client";
import React, { Suspense, useRef, useMemo, useState, useCallback, useEffect, useDeferredValue } from 'react';
import { Canvas, useFrame, extend, ThreeElement, useThree } from '@react-three/fiber';
import { Points, PointMaterial, Octahedron, Sphere, OrbitControls, Text, Html } from '@react-three/drei';
import * as THREE from 'three';
const { MOUSE } = THREE;
import { CoreShaderMaterial, BeamShaderMaterial } from './shaders/CoreShader';
import { buildStaticGraph, buildProjectNodes, GraphNode, GraphEdge, LinkedSystem, NodeCluster, GRAPH_CLUSTER_CONFIG, GraphNodeAssetOverride, GraphNodeAssetStageOverride } from '@/lib/graphData';
import { getNodeAssetProfile, getNodeAssetSource, getSentinelAssetProfile, nodeHasCanonicalAsset, nodeUsesExternalAsset, NodeAssetFamilyOverrides, NodeAssetProfile, NodeAssetStage } from '@/lib/nodeAssets';
import { createNodeGlyphTexture, DocumentGlyphKind } from '@/lib/nodeGlyphTextures';
import { Language, translations, translateActiveCommand, translateModeLabel, translateReason, translateSeverity, translateTrust, tt } from '@/lib/i18n';
import { ChainEventSnapshot, ChainStatusSnapshot, DashboardSignals, deriveDashboardSignals, PhysicsSnapshot } from '@/lib/telemetry';
import { readHandleBackedFile, removeLinkedSystemHandle } from '@/lib/filesystemHandles';
const LazyNodeAssetRig = React.lazy(() => import('./NodeAssetRig'));

type QualityTier = 'ultra' | 'balanced' | 'safe';
type OpenDocState = { fileName: string; filePath: string; content: string; truncated: boolean };
type ChatMessage = { id: string; role: 'user' | 'assistant' | 'system'; content: string };
type CameraMode = 'overview' | 'focus' | 'manual';
type ZoomTier = 'detail' | 'cluster' | 'overview';
type MerkleReplayEntry = { id: number; hash: string; eventType: string; chainTrust: number; drift: number; timestamp: number };
type AggregateBadge = {
  id: string;
  parentId: string;
  label: string;
  count: number;
  color: string;
  cluster: Exclude<NodeCluster, 'linked-root'>;
  position: [number, number, number];
  active: boolean;
};

type AssetStageSlot = 'appearance' | 'effect';
type NodeAccessMode = LinkedSystem['accessMode'] | 'none';
type NodeCapabilityKind = 'engine' | 'document' | 'folder' | 'system' | 'access' | 'passive';
type NodeCapabilities = {
  kind: NodeCapabilityKind;
  accessMode: NodeAccessMode;
  system: LinkedSystem | null;
  canExecute: boolean;
  canOpenDocument: boolean;
  canAssignAsset: boolean;
  canClearAsset: boolean;
  canFocus: boolean;
  blockReason: string | null;
};

type DockCommandItem = {
  id: string;
  label: string;
  onClick: () => void;
  visible?: boolean;
  active?: boolean;
  tone?: 'default' | 'accent' | 'warning';
};

type NodeAssetEditState = {
  enabled: boolean;
};

type EditModeSessionBaseline = {
  overrides: Record<string, GraphNodeAssetOverride>;
  familyProfiles: NodeAssetFamilyOverrides;
};

const EDIT_MODE_SECRET_CODES = [
  83, 73, 67, 77, 86, 78, 68, 86, 83, 67, 82, 69, 65, 84, 86, 83, 69, 83, 84,
] as const;

type PendingAssetTarget =
  | { nodeId: string; slot: AssetStageSlot; family?: undefined }
  | { family: 'sentinel'; slot: AssetStageSlot; nodeId?: undefined };

function mergeGraphNodeAssetOverride(
  base?: GraphNodeAssetOverride,
  draft?: GraphNodeAssetOverride,
): GraphNodeAssetOverride | undefined {
  if (!base && !draft) return undefined;
  const mergedAppearance = (base?.appearance || draft?.appearance)
    ? {
        ...(base?.appearance || {}),
        ...(draft?.appearance || {}),
      }
    : undefined;
  const mergedEffect = (base?.effect || draft?.effect)
    ? {
        ...(base?.effect || {}),
        ...(draft?.effect || {}),
      }
    : undefined;
  return {
    ...base,
    ...draft,
    appearance: mergedAppearance?.src ? (mergedAppearance as GraphNodeAssetStageOverride) : base?.appearance,
    effect: mergedEffect?.src ? (mergedEffect as GraphNodeAssetStageOverride) : base?.effect,
  };
}

function deriveZoomTier(zoom: number): ZoomTier {
  if (zoom >= 34) return 'detail';
  if (zoom >= 24) return 'cluster';
  return 'overview';
}

function inferAggregateCluster(node: GraphNode): Exclude<NodeCluster, 'linked-root'> {
  if (node.cluster && node.cluster !== 'linked-root') return node.cluster;

  if (node.type === 'folder') return 'system';

  const lower = node.label.toLowerCase();
  if (lower.endsWith('.md') || lower.endsWith('.txt') || lower.endsWith('.pdf')) return 'documents';
  if (lower.endsWith('.py') || lower.endsWith('.json') || lower.endsWith('.ts') || lower.endsWith('.tsx') || lower.endsWith('.js') || lower.endsWith('.sh')) {
    return 'tools';
  }
  return 'system';
}

function shouldRenderNodeForZoomTier(
  node: GraphNode,
  zoomTier: ZoomTier,
  highlightedIds: Set<string>,
) {
  if (highlightedIds.has(node.id)) return true;
  return true;
}

function shouldRenderNodeLabel(
  node: GraphNode,
  zoomTier: ZoomTier,
  hovered: boolean,
  isSelected: boolean,
) {
  if (hovered || isSelected) return true;

  if (zoomTier === 'detail') {
    return node.type === 'core' || node.type === 'engine' || node.type === 'edition' || node.type === 'module';
  }

  if (zoomTier === 'cluster') {
    return node.type === 'core' || node.type === 'engine' || node.type === 'edition' || node.type === 'module';
  }

  return node.type === 'core' || node.type === 'edition' || node.cluster === 'linked-root';
}

// SOVEREIGN SIDE RAIL
function WaveMonitor({
  drift,
  eta,
  merkle,
  logs,
  chainEvents,
  signals,
  sessionStart,
  dictionary,
  physics,
  linkedSystems,
  primaryLinkedSystem,
  activeVectorText,
  topReplay,
  qualityTier,
  audioArmed,
  reducedMotion,
  open,
  onToggle,
}: {
  drift: number;
  eta: number;
  merkle: string;
  logs: { id: number; msg: string }[];
  chainEvents: ChainEventSnapshot[];
  signals: DashboardSignals;
  sessionStart: number;
  dictionary: Record<string, string>;
  physics: PhysicsSnapshot;
  linkedSystems: LinkedSystem[];
  primaryLinkedSystem: LinkedSystem | null;
  activeVectorText: string;
  topReplay: MerkleReplayEntry[];
  qualityTier: QualityTier;
  audioArmed: boolean;
  reducedMotion: boolean;
  open: boolean;
  onToggle: () => void;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null!);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [viewportWidth, setViewportWidth] = useState(1440);
  const normalizedDrift = Math.max(0, Math.min(1, drift));
  const normalizedEta = Math.max(0, Math.min(1, eta));
  const quadrantSync = Math.max(0, Math.min(100, ((normalizedEta * 0.72) + ((1 - normalizedDrift) * 0.28)) * 100));
  const latencyMs = (
    0.72
    + normalizedDrift * 7.5
    + (1 - normalizedEta) * 2.4
    + Math.abs(Math.sin(elapsedSeconds * 0.7)) * 0.38
  ).toFixed(3);
  const palette = signals.palette;
  const latestChainEvent = chainEvents[0];
  const syncColor = quadrantSync < 80 ? palette.warning : quadrantSync < 92 ? palette.secondary : palette.emphasis;
  const glowText = { color: palette.emphasis, textShadow: `0 0 18px ${palette.secondary}22` } as const;
  const softText = { color: 'rgba(255,255,255,0.76)', textShadow: `0 0 12px ${palette.secondary}18` } as const;
  const faintText = { color: 'rgba(255,255,255,0.52)' } as const;
  const isTablet = viewportWidth < 1180;
  const isPhone = viewportWidth < 780;
  const railTop = isPhone ? 104 : isTablet ? 132 : 148;
  const railBottom = isPhone ? 14 : 18;
  const tabWidth = isPhone ? 34 : 38;
  const railWidth = isPhone ? 220 : isTablet ? 252 : 286;
  const canvasHeight = isPhone ? 84 : isTablet ? 96 : 112;
  const canvasWidth = isPhone ? 188 : isTablet ? 214 : 248;
  const modeLabelText = translateModeLabel(signals.modeLabel, dictionary);
  const modeReasonText = translateReason(signals.modeReason, dictionary);
  const chainTrustText = translateTrust(signals.chainTrustLabel, dictionary);
  const severityText = translateSeverity(signals.severityLabel, dictionary);
  const entropyBars = useMemo(
    () => Array.from({ length: 14 }, (_, index) => Math.abs(Math.sin(elapsedSeconds * 0.22 + index * 0.78 + physics.eta * 2.8))),
    [elapsedSeconds, physics.eta],
  );

  useEffect(() => {
    const interval = setInterval(() => {
      setElapsedSeconds((Date.now() - sessionStart) / 1000);
    }, 1000);
    return () => clearInterval(interval);
  }, [sessionStart]);

  useEffect(() => {
    const updateViewport = () => setViewportWidth(window.innerWidth);
    updateViewport();
    window.addEventListener('resize', updateViewport);
    return () => window.removeEventListener('resize', updateViewport);
  }, []);

  useEffect(() => {
    let frame = 0;
    let disposed = false;
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (!canvas || !ctx) return;

    const render = () => {
      if (disposed) return;
      const liveCanvas = canvasRef.current;
      if (!liveCanvas) return;
      const { width, height } = liveCanvas;
      ctx.clearRect(0, 0, width, height);
      const t = Date.now() / 1000;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';

      ctx.beginPath();
      ctx.strokeStyle = signals.mode === 'INCIDENT' ? palette.warning : palette.secondary;
      ctx.lineWidth = 3.5;
      ctx.shadowBlur = 18;
      ctx.shadowColor = palette.secondary;
      ctx.globalAlpha = 0.18;
      for (let x = 0; x < width; x++) {
        const field = Math.sin(x * 0.045 + t * 1.3) * (height * 0.18) + Math.cos(x * 0.012 - t * 0.86) * (6 + drift * 12);
        const y = height * 0.5 + field;
        if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.stroke();

      ctx.beginPath();
      ctx.strokeStyle = palette.emphasis;
      ctx.lineWidth = 2.2;
      ctx.shadowBlur = 12;
      ctx.shadowColor = palette.emphasis;
      ctx.globalAlpha = 0.88;
      for (let x = 0; x < width; x++) {
        const wobble = Math.sin(x * 0.08 + t * 4.2) * (8 + eta * 10);
        const noise = Math.cos(x * 0.03 - t * 1.4) * drift * 8;
        const y = height * 0.5 + wobble + noise;
        if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.stroke();

      ctx.beginPath();
      ctx.shadowBlur = 0;
      ctx.strokeStyle = palette.line;
      ctx.lineWidth = 1;
      ctx.globalAlpha = 0.22;
      for (let x = 0; x < width; x++) {
        const y = height * 0.5 + Math.cos(x * (0.06 + eta * 0.03) + t * 3.2) * (5 + eta * 6);
        if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.stroke();

      if (!disposed) frame = requestAnimationFrame(render);
    };

    render();
    return () => {
      disposed = true;
      cancelAnimationFrame(frame);
    };
  }, [drift, eta, palette.emphasis, palette.line, palette.secondary, palette.warning, signals.mode]);

  return (
    <div style={{ position: 'absolute', top: railTop, right: 0, bottom: railBottom, width: railWidth + tabWidth, zIndex: 500, pointerEvents: 'none' }}>
      <button
        onClick={onToggle}
        className="btn-nexus"
        style={{
          position: 'absolute',
          right: railWidth - 1,
          top: '50%',
          transform: 'translateY(-50%)',
          transformOrigin: 'center',
          pointerEvents: 'auto',
          writingMode: 'vertical-lr',
          padding: isPhone ? '10px 7px' : '12px 8px',
          fontSize: '0.46rem',
          letterSpacing: '3px',
          minWidth: `${tabWidth - 6}px`,
          borderTopLeftRadius: 0,
          borderBottomLeftRadius: 0,
          borderTopRightRadius: '10px',
          borderBottomRightRadius: '10px',
          boxShadow: '0 12px 26px rgba(0,0,0,0.2)',
        }}
      >
        {open ? tt(dictionary, 'common.hide', 'HIDE') : tt(dictionary, 'common.open', 'OPEN')}
      </button>

      <div
        style={{
          position: 'absolute',
          top: 0,
          right: 0,
          bottom: 0,
          width: railWidth,
          transform: open ? 'translateX(0)' : `translateX(${railWidth + 24}px)`,
          transition: 'transform 0.34s cubic-bezier(0.16, 1, 0.3, 1)',
          pointerEvents: open ? 'auto' : 'none',
          display: 'flex',
          flexDirection: 'column',
          gap: isPhone ? '8px' : '10px',
          padding: isPhone ? '10px' : '12px',
          border: `1px solid ${palette.border}`,
          background: palette.panel,
          boxShadow: '0 18px 54px rgba(0,0,0,0.22)',
          overflowY: 'auto',
        }}
        className="hide-scrollbar"
      >
        <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '8px', alignItems: 'start', paddingBottom: '8px', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
          <div>
            <div style={{ ...glowText, fontSize: isPhone ? '0.54rem' : '0.62rem', letterSpacing: '3px', fontWeight: 800 }}>{modeLabelText}</div>
            <div style={{ ...softText, fontSize: '0.46rem', letterSpacing: '2px', lineHeight: 1.4, marginTop: '4px' }}>{modeReasonText}</div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, auto)', gap: '10px', textAlign: 'right' }}>
            <div>
              <div style={{ ...faintText, fontSize: '0.4rem', letterSpacing: '2px' }}>{tt(dictionary, 'common.sync', 'SYNC')}</div>
              <div style={{ color: syncColor, fontSize: '0.62rem', fontWeight: 800 }}>{quadrantSync.toFixed(0)}%</div>
            </div>
            <div>
              <div style={{ ...faintText, fontSize: '0.4rem', letterSpacing: '2px' }}>{tt(dictionary, 'common.trust', 'TRUST')}</div>
              <div style={{ ...glowText, fontSize: '0.62rem', fontWeight: 800 }}>{chainTrustText}</div>
            </div>
            <div>
              <div style={{ ...faintText, fontSize: '0.4rem', letterSpacing: '2px' }}>{tt(dictionary, 'common.load', 'LOAD')}</div>
              <div style={{ ...glowText, fontSize: '0.62rem', fontWeight: 800 }}>{Math.round(signals.activity * 100)}%</div>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <canvas ref={canvasRef} width={canvasWidth} height={canvasHeight} style={{ width: '100%', height: `${canvasHeight}px`, border: `1px solid ${palette.border}`, background: 'rgba(255,255,255,0.015)' }} />
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
            <div>
              <div style={{ ...faintText, fontSize: '0.42rem', letterSpacing: '2px' }}>{tt(dictionary, 'core.wave.system_uptime', 'SYSTEM_UP_TIME')}</div>
              <div style={{ ...glowText, fontSize: '0.92rem', fontWeight: 900, fontVariantNumeric: 'tabular-nums' }}>{(elapsedSeconds + 1775500).toFixed(0)}</div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ ...faintText, fontSize: '0.42rem', letterSpacing: '2px' }}>{tt(dictionary, 'core.wave.latency', 'LATENCY')}</div>
              <div style={{ ...glowText, fontSize: '0.8rem', fontWeight: 800 }}>{latencyMs}ms</div>
            </div>
          </div>
        </div>

        <div style={{ paddingTop: '4px', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
          <div style={{ ...softText, fontSize: '0.46rem', letterSpacing: '3px', marginBottom: '8px' }}>{tt(dictionary, 'core.context_entropy_bars', 'CONTEXT_ENTROPY_BARS')}</div>
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: '4px', height: '26px' }}>
            {entropyBars.map((value, index) => (
              <div
                key={`rail-entropy-${index}`}
                style={{
                  width: index % 3 === 0 ? '6px' : '5px',
                  height: `${Math.max(6, value * 26)}px`,
                  background: index % 4 === 0 ? palette.accent : palette.emphasis,
                  opacity: 0.2 + value * 0.56,
                  borderRadius: '999px',
                  boxShadow: `0 0 12px ${index % 4 === 0 ? palette.accent : palette.emphasis}22`,
                }}
              />
            ))}
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: '8px', marginTop: '10px' }}>
            <div><div style={{ ...faintText, fontSize: '0.4rem', letterSpacing: '2px' }}>H</div><div style={{ ...glowText, fontSize: '0.68rem', fontWeight: 700 }}>{physics.H.toFixed(4)}</div></div>
            <div><div style={{ ...faintText, fontSize: '0.4rem', letterSpacing: '2px' }}>ETA</div><div style={{ ...glowText, fontSize: '0.68rem', fontWeight: 700 }}>{physics.eta.toFixed(3)}</div></div>
            <div><div style={{ ...faintText, fontSize: '0.4rem', letterSpacing: '2px' }}>N</div><div style={{ ...glowText, fontSize: '0.68rem', fontWeight: 700 }}>{physics.N}</div></div>
            <div><div style={{ ...faintText, fontSize: '0.4rem', letterSpacing: '2px' }}>D_KL</div><div style={{ ...glowText, fontSize: '0.68rem', fontWeight: 700 }}>{drift.toFixed(4)}</div></div>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', paddingTop: '6px', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
          <div style={{ ...softText, fontSize: '0.46rem', letterSpacing: '2px' }}>{tt(dictionary, 'core.active_system', 'ACTIVE_SYSTEM')}: {primaryLinkedSystem?.name || tt(dictionary, 'common.idle', 'IDLE')}</div>
          <div style={{ ...softText, fontSize: '0.46rem', letterSpacing: '2px' }}>{tt(dictionary, 'core.link_mode', 'LINK_MODE')}: {primaryLinkedSystem ? tt(dictionary, `hud.access.${primaryLinkedSystem.accessMode || 'runtime'}`, (primaryLinkedSystem.accessMode || 'runtime').toUpperCase()) : tt(dictionary, 'common.idle', 'IDLE')}</div>
          <div style={{ ...softText, fontSize: '0.46rem', letterSpacing: '2px' }}>{tt(dictionary, 'core.system_count', 'SYSTEM_COUNT')}: {linkedSystems.length}</div>
          <div style={{ ...softText, fontSize: '0.46rem', letterSpacing: '2px' }}>{tt(dictionary, 'core.active_vector', 'ACTIVE_VECTOR')}: {activeVectorText}</div>
          <div style={{ ...softText, fontSize: '0.46rem', letterSpacing: '2px' }}>{tt(dictionary, 'common.severity', 'SEVERITY')}: {severityText}</div>
          <div style={{ ...softText, fontSize: '0.46rem', letterSpacing: '2px' }}>{tt(dictionary, 'core.wave.merkle_log', 'MERKLE_LOG')}: {merkle.slice(0, 10).toUpperCase()}</div>
          <div style={{ ...softText, fontSize: '0.46rem', letterSpacing: '2px' }}>{tt(dictionary, 'core.audio_bus', 'AUDIO_BUS')}: {audioArmed ? tt(dictionary, 'core.audio.armed', 'ARMED') : tt(dictionary, 'core.audio.standby', 'STANDBY')} // {tt(dictionary, 'core.motion', 'MOTION')}: {reducedMotion ? tt(dictionary, 'core.motion.reduced', 'REDUCED') : tt(dictionary, 'core.motion.full', 'FULL')}</div>
          <div style={{ ...softText, fontSize: '0.46rem', letterSpacing: '2px' }}>{tt(dictionary, 'core.quality_profile', 'QUALITY_PROFILE')}: {qualityTier.toUpperCase()}</div>
          {latestChainEvent && <div style={{ color: palette.accent, fontSize: '0.44rem', letterSpacing: '2px' }}>{tt(dictionary, 'core.recent_chain_event', 'RECENT_CHAIN_EVENT')}: {latestChainEvent.type}</div>}
        </div>

        <div style={{ paddingTop: '6px', borderTop: '1px solid rgba(255,255,255,0.08)', display: 'flex', flexDirection: 'column', gap: '7px' }}>
          <div style={{ ...softText, fontSize: '0.46rem', letterSpacing: '3px' }}>{tt(dictionary, 'replay.title', 'MERKLE_REPLAY')}</div>
          {topReplay.length > 0 ? (
            <>
              <div style={{ display: 'flex', alignItems: 'flex-end', gap: '5px', height: '26px' }}>
                {topReplay.map((entry, index) => (
                  <div
                    key={entry.id}
                    style={{
                      flex: 1,
                      height: `${Math.max(8, (1 - Math.min(1, entry.drift)) * 26)}px`,
                      borderRadius: '999px',
                      background: index === 0 ? palette.warning : entry.chainTrust < 0.7 ? palette.accent : palette.emphasis,
                      opacity: 0.28 + (topReplay.length - index) * 0.12,
                    }}
                  />
                ))}
              </div>
              {topReplay.slice(0, 3).map((entry) => (
                <div key={`rail-replay-${entry.id}`} style={{ display: 'flex', justifyContent: 'space-between', gap: '10px', fontSize: '0.42rem', letterSpacing: '1.5px', color: 'rgba(255,255,255,0.74)' }}>
                  <span style={{ color: palette.emphasis }}>{entry.hash.slice(0, 8).toUpperCase()}</span>
                  <span>{entry.eventType}</span>
                  <span style={{ color: palette.secondary }}>{formatReplayAge(entry.timestamp)}</span>
                </div>
              ))}
            </>
          ) : (
            <div style={{ ...faintText, fontSize: '0.44rem', fontStyle: 'italic' }}>{tt(dictionary, 'replay.empty', 'NO_REPLAY_EVENTS')}</div>
          )}
        </div>

        <div style={{ paddingTop: '6px', borderTop: '1px solid rgba(255,255,255,0.08)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <div style={{ ...softText, fontSize: '0.44rem', letterSpacing: '3px' }}>{tt(dictionary, 'core.wave.event_chain_stream', 'EVENT_CHAIN_STREAM')}</div>
          {logs.slice(0, 2).map((log) => (
            <div key={log.id} style={{ color: palette.secondary, fontSize: '0.46rem', letterSpacing: '1.4px', fontFamily: 'var(--font-mono)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {log.msg}
            </div>
          ))}
          {logs.length === 0 && <div style={{ ...faintText, fontSize: '0.44rem', fontStyle: 'italic' }}>{tt(dictionary, 'core.wave.stream_idle', 'STREAM_IDLE')}</div>}
        </div>
      </div>
    </div>
  );
}

// Register materials for JSX use
extend({ CoreShaderMaterial, BeamShaderMaterial });

// Add types for JSX
declare module '@react-three/fiber' {
  interface ThreeElements {
    coreShaderMaterial: ThreeElement<typeof CoreShaderMaterial>;
    beamShaderMaterial: ThreeElement<typeof BeamShaderMaterial>;
  }
}

// DATA SENTINEL (Autonomous Drone)
function SentinelDrone({
  index = 0,
  drift = 0,
  anchor = [0, 0, 0],
  color = '#cbd5e1',
  familyAssetOverrides,
  assetStage,
  editMode = false,
  isSelected = false,
  onSelectForEdit,
  onOpenAssetPicker,
  onDraftAssetOffset,
  onCommitAssetOffset,
  onDraftAssetRotation,
  onCommitAssetRotation,
  onDraftAssetScale,
  onCommitAssetScale,
}: {
  index?: number;
  drift?: number;
  anchor?: [number, number, number];
  color?: string;
  familyAssetOverrides?: NodeAssetFamilyOverrides;
  assetStage?: NodeAssetStage;
  editMode?: boolean;
  isSelected?: boolean;
  onSelectForEdit?: (index: number) => void;
  onOpenAssetPicker?: () => void;
  onDraftAssetOffset?: (offset: [number, number, number]) => void;
  onCommitAssetOffset?: () => void;
  onDraftAssetRotation?: (rotation: [number, number, number]) => void;
  onCommitAssetRotation?: () => void;
  onDraftAssetScale?: (scale: number) => void;
  onCommitAssetScale?: () => void;
}) {
  const groupRef = useRef<THREE.Group>(null!);
  const visualRef = useRef<THREE.Group>(null!);
  const previousPositionRef = useRef(new THREE.Vector3(anchor[0], 0, anchor[2]));
  const previousHeadingRef = useRef(0);
  const rotatingRef = useRef(false);
  const scalingRef = useRef(false);
  const isAlert = drift > 0.1;
  const sentinelNode = useMemo<GraphNode>(() => ({
    id: `sentinel-${index}`,
    label: `SENTINEL-${index + 1}`,
    position: [0, 0, 0],
    type: 'module',
    shape: 'tetrahedron',
    size: 0.32,
    parentId: null,
    tooltip: 'Autonomous sentinel patrol.',
    color,
    cluster: 'system',
    orbitLevel: 0,
    importance: 'secondary',
    systemId: null,
    motionProfile: 'sentinel-linked',
  }), [color, index]);
  const sentinelAssetProfile = useMemo<NodeAssetProfile>(() => {
    const baseProfile = getSentinelAssetProfile(familyAssetOverrides);
    return {
      ...baseProfile,
      preserveFallback: false,
      appearance: {
        ...baseProfile.appearance,
        ...(assetStage || {}),
        enabled: true,
        offset: [0, 0, 0],
        scale: (assetStage?.scale ?? baseProfile.appearance.scale ?? 1) * (isAlert ? 1.08 : 0.88),
      }
    };
  }, [assetStage, familyAssetOverrides, isAlert]);
  const assetResetKey = `${sentinelNode.id}:${sentinelAssetProfile.appearance.src}`;
  const assetRotation = assetStage?.rotation || sentinelAssetProfile.appearance.rotation || [0, 0, 0];
  const editRingRadius = 0.9;
  const editHandlePosition: [number, number, number] = [
    Math.sin(assetRotation[1] || 0) * editRingRadius,
    0.08,
    Math.cos(assetRotation[1] || 0) * editRingRadius,
  ];
  const scaleHandlePosition: [number, number, number] = [
    Math.sin((assetRotation[1] || 0) + Math.PI / 2) * (editRingRadius + 0.28),
    0.08,
    Math.cos((assetRotation[1] || 0) + Math.PI / 2) * (editRingRadius + 0.28),
  ];
  const proceduralFallback = (
    <mesh>
      <tetrahedronGeometry args={[0.3, 0]} />
      <meshStandardMaterial
        color={isAlert ? '#ef4444' : color}
        emissive={isAlert ? '#ef4444' : color}
        emissiveIntensity={isAlert ? 0.28 : 0.1}
        metalness={0.94}
        roughness={0.18}
        transparent
        opacity={isAlert ? 0.88 : 0.72}
      />
    </mesh>
  );
  const startRotate = useCallback((event: any) => {
    if (!editMode) return;
    rotatingRef.current = true;
    event.stopPropagation();
    event.target?.setPointerCapture?.(event.pointerId);
    onSelectForEdit?.(index);
  }, [editMode, index, onSelectForEdit]);
  const moveRotate = useCallback((event: any) => {
    if (!rotatingRef.current || !editMode) return;
    event.stopPropagation();
    const dx = event.point.x - groupRef.current.position.x;
    const dz = event.point.z - groupRef.current.position.z;
    const nextHeading = Math.atan2(dx, dz);
    onDraftAssetRotation?.([assetRotation[0] || 0, nextHeading, assetRotation[2] || 0]);
  }, [assetRotation, editMode, onDraftAssetRotation]);
  const endRotate = useCallback((event: any) => {
    if (!rotatingRef.current) return;
    rotatingRef.current = false;
    event.stopPropagation();
    event.target?.releasePointerCapture?.(event.pointerId);
    onCommitAssetRotation?.();
  }, [onCommitAssetRotation]);
  const startScale = useCallback((event: any) => {
    if (!editMode) return;
    scalingRef.current = true;
    event.stopPropagation();
    event.target?.setPointerCapture?.(event.pointerId);
    onSelectForEdit?.(index);
  }, [editMode, index, onSelectForEdit]);
  const moveScale = useCallback((event: any) => {
    if (!scalingRef.current || !editMode) return;
    event.stopPropagation();
    const dx = event.point.x - groupRef.current.position.x;
    const dz = event.point.z - groupRef.current.position.z;
    const distance = Math.max(0.15, Math.sqrt(dx * dx + dz * dz));
    onDraftAssetScale?.(THREE.MathUtils.clamp(distance / editRingRadius, 0.18, 6));
  }, [editMode, onDraftAssetScale]);
  const endScale = useCallback((event: any) => {
    if (!scalingRef.current) return;
    scalingRef.current = false;
    event.stopPropagation();
    event.target?.releasePointerCapture?.(event.pointerId);
    onCommitAssetScale?.();
  }, [onCommitAssetScale]);
  useFrame((state) => {
    if (!groupRef.current) return;
    const t = state.clock.elapsedTime * (isAlert ? 0.54 : 0.34) + index * 0.8;
    const orbitRadius = 5.8 + (index % 3) * 1.6 + Math.min(1.8, drift * 12);
    const radialWave = Math.sin(t * 1.8 + index) * 0.42;
    const nextPosition = new THREE.Vector3(
      anchor[0] + Math.cos(t) * (orbitRadius + radialWave),
      0.14 + Math.sin(t * 2.2 + index * 0.3) * 0.08,
      anchor[2] + Math.sin(t * 0.96) * (orbitRadius * 0.78),
    );
    const travelVector = nextPosition.clone().sub(previousPositionRef.current);
    const heading = travelVector.lengthSq() > 0.000001
      ? Math.atan2(travelVector.x, travelVector.z)
      : previousHeadingRef.current;
    const normalizedTurn = Math.atan2(
      Math.sin(heading - previousHeadingRef.current),
      Math.cos(heading - previousHeadingRef.current),
    );
    const speed = travelVector.length();
    const bank = THREE.MathUtils.clamp(-normalizedTurn * 2.8, -0.32, 0.32);
    const pitch = THREE.MathUtils.clamp(speed * 3.2, 0, 0.18);

    groupRef.current.position.copy(nextPosition);
    previousPositionRef.current.copy(nextPosition);
    previousHeadingRef.current = heading;

    if (visualRef.current) {
      visualRef.current.rotation.set(
        pitch,
        heading,
        bank + (isAlert ? Math.sin(t * 2.1) * 0.04 : Math.sin(t * 1.6) * 0.018),
      );
    }
  });

  return (
    <group ref={groupRef}>
      <mesh
        visible={false}
        onClick={(event) => {
          event.stopPropagation();
          onSelectForEdit?.(index);
        }}
      >
        <sphereGeometry args={[0.82, 18, 18]} />
      </mesh>
      <group ref={visualRef}>
        <NodeAssetErrorBoundary resetKey={assetResetKey} fallback={proceduralFallback}>
          <Suspense fallback={proceduralFallback}>
            <LazyNodeAssetRig
              node={sentinelNode}
              accent={isAlert ? '#ef4444' : color}
              scale={0.575}
              pulsing
              selected={isAlert}
              profile={sentinelAssetProfile}
            />
          </Suspense>
        </NodeAssetErrorBoundary>
      </group>
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.34, 0.39, 24]} />
        <meshBasicMaterial
          color={isAlert ? '#fb7185' : color}
          transparent
          opacity={isAlert ? 0.24 : 0.14}
          blending={THREE.AdditiveBlending}
          side={THREE.DoubleSide}
        />
      </mesh>
      {editMode && (
        <Html center position={[0, 0.42, -1.05]} style={{ pointerEvents: 'auto' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', padding: '4px', borderRadius: '999px', background: 'rgba(2,6,23,0.9)', border: '1px solid rgba(255,255,255,0.14)', boxShadow: '0 10px 28px rgba(0,0,0,0.28)' }}>
            <button
              onClick={(event) => {
                event.stopPropagation();
                onSelectForEdit?.(index);
              }}
              className="btn-nexus"
              style={{ padding: '5px 8px', fontSize: '0.42rem', letterSpacing: '1.4px' }}
            >
              EDIT
            </button>
            <button
              onClick={(event) => {
                event.stopPropagation();
                onSelectForEdit?.(index);
                onOpenAssetPicker?.();
              }}
              className="btn-nexus"
              style={{ padding: '5px 8px', fontSize: '0.42rem', letterSpacing: '1.4px' }}
            >
              GLB
            </button>
          </div>
        </Html>
      )}
      {editMode && isSelected && (
        <group>
          <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.06, 0]}>
            <ringGeometry args={[editRingRadius - 0.03, editRingRadius + 0.03, 48]} />
            <meshBasicMaterial color={color} transparent opacity={0.44} />
          </mesh>
          <mesh position={editHandlePosition} onPointerDown={startRotate} onPointerMove={moveRotate} onPointerUp={endRotate} onPointerLeave={endRotate}>
            <sphereGeometry args={[0.12, 18, 18]} />
            <meshBasicMaterial color="#f8fafc" transparent opacity={0.92} />
          </mesh>
          <mesh position={scaleHandlePosition} onPointerDown={startScale} onPointerMove={moveScale} onPointerUp={endScale} onPointerLeave={endScale}>
            <boxGeometry args={[0.18, 0.18, 0.18]} />
            <meshBasicMaterial color="#fbbf24" transparent opacity={0.9} />
          </mesh>
          <mesh position={[0, 0.07, 0]}>
            <sphereGeometry args={[0.06, 14, 14]} />
            <meshBasicMaterial color={color} transparent opacity={0.82} />
          </mesh>
        </group>
      )}
    </group>
  );
}

function LinkParticleStream({
  start,
  end,
  color = '#ffffff',
  count = 10,
  chromatic = true,
  emphasis = 0.8,
}: {
  start: [number, number, number];
  end: [number, number, number];
  color?: string;
  count?: number;
  chromatic?: boolean;
  emphasis?: number;
}) {
  const baseRef = useRef<THREE.Points>(null!);
  const cyanRef = useRef<THREE.Points>(null!);
  const redRef = useRef<THREE.Points>(null!);

  const [basePositions, cyanPositions, redPositions] = useMemo(
    () => [new Float32Array(count * 3), new Float32Array(count * 3), new Float32Array(count * 3)],
    [count],
  );

  const vectors = useMemo(() => {
    const startVec = new THREE.Vector3(...start);
    const endVec = new THREE.Vector3(...end);
    const direction = endVec.clone().sub(startVec);
    const tangent = direction.clone().normalize();
    const normal = new THREE.Vector3(-tangent.z, 0, tangent.x);
    if (normal.lengthSq() < 0.0001) {
      normal.set(0, 1, 0).cross(tangent);
    }
    normal.normalize();
    const binormal = new THREE.Vector3().crossVectors(tangent, normal).normalize();
    return {
      start: startVec.toArray() as [number, number, number],
      direction: direction.toArray() as [number, number, number],
      normal: normal.toArray() as [number, number, number],
      binormal: binormal.toArray() as [number, number, number],
    };
  }, [end, start]);

  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    const flowSpeed = 0.38 + emphasis * 0.34;
    const split = 0.08 + emphasis * 0.06;
    const sway = 0.04 + emphasis * 0.03;
    const [sx, sy, sz] = vectors.start;
    const [dx, dy, dz] = vectors.direction;
    const [nx, ny, nz] = vectors.normal;
    const [bx, by, bz] = vectors.binormal;

    const updateStream = (ref: React.MutableRefObject<THREE.Points>, phase: number, lateralBias: number, wobbleSign: number) => {
      if (!ref.current) return;
      const positions = ref.current.geometry.attributes.position.array as Float32Array;
      for (let i = 0; i < count; i++) {
        const index = i * 3;
        const progress = (t * flowSpeed + phase + i / Math.max(count, 1)) % 1;
        const envelope = Math.sin(progress * Math.PI);
        const lateral = lateralBias + Math.sin(t * 4.8 + i * 0.72) * split * 0.18 * envelope;
        const wobble = Math.cos(t * 3.4 + i * 0.54) * sway * wobbleSign * envelope;

        positions[index] = sx + dx * progress + nx * lateral + bx * wobble;
        positions[index + 1] = sy + dy * progress + ny * lateral + by * wobble;
        positions[index + 2] = sz + dz * progress + nz * lateral + bz * wobble;
      }
      ref.current.geometry.attributes.position.needsUpdate = true;
    };

    updateStream(baseRef, 0, 0, 1);
    if (chromatic) {
      updateStream(cyanRef, 0.16, split, 1);
      updateStream(redRef, 0.3, -split, -1);
    }
  });

  return (
    <group>
      <Points ref={baseRef} positions={basePositions} stride={3} frustumCulled={false}>
        <PointMaterial
          transparent
          color={color}
          size={0.085 + emphasis * 0.035}
          sizeAttenuation
          depthWrite={false}
          blending={THREE.AdditiveBlending}
          opacity={0.72}
        />
      </Points>
      {chromatic && (
        <>
          <Points ref={cyanRef} positions={cyanPositions} stride={3} frustumCulled={false}>
            <PointMaterial
              transparent
              color="#67e8f9"
              size={0.07 + emphasis * 0.028}
              sizeAttenuation
              depthWrite={false}
              blending={THREE.AdditiveBlending}
              opacity={0.44}
            />
          </Points>
          <Points ref={redRef} positions={redPositions} stride={3} frustumCulled={false}>
            <PointMaterial
              transparent
              color="#fb7185"
              size={0.07 + emphasis * 0.028}
              sizeAttenuation
              depthWrite={false}
              blending={THREE.AdditiveBlending}
              opacity={0.34}
            />
          </Points>
        </>
      )}
    </group>
  );
}

// CONNECTION BEAM
function ConnectionBeam({
  start,
  end,
  color = '#ffffff',
  streamParticles = 0,
  chromaticParticles = false,
  emphasis = 0.8,
}: {
  start: [number, number, number];
  end: [number, number, number];
  color?: string;
  streamParticles?: number;
  chromaticParticles?: boolean;
  emphasis?: number;
}) {
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
    <group>
      <Points positions={points} stride={3}>
        <bufferAttribute attach="geometry-attributes-aProgress" args={[progress, 1]} />
        <beamShaderMaterial ref={matRef} transparent depthWrite={false} blending={THREE.AdditiveBlending} />
      </Points>
      {streamParticles > 0 && (
        <LinkParticleStream
          start={start}
          end={end}
          color={color}
          count={streamParticles}
          chromatic={chromaticParticles}
          emphasis={emphasis}
        />
      )}
    </group>
  );
}

function NodeGlyphSprite({
  kind,
  accent,
  scale,
  opacity = 1,
}: {
  kind: DocumentGlyphKind;
  accent: string;
  scale: number;
  opacity?: number;
}) {
  const texture = useMemo(() => createNodeGlyphTexture(kind, accent), [accent, kind]);
  const aspect = kind === 'folder' ? 0.86 : 1;
  return (
    <sprite scale={[scale * aspect, scale, 1]}>
      <spriteMaterial
        map={texture}
        transparent
        depthWrite={false}
        opacity={opacity}
        color="#ffffff"
      />
    </sprite>
  );
}

function getNodeBadge(node: GraphNode) {
  const lowerLabel = node.label.toLowerCase();
  if (node.id === 'imperium') return 'IMPERIUM_NODE';
  if (node.cluster === 'linked-root') return 'LINKED_SYSTEM';
  if (node.cluster === 'dashboard' && node.orbitLevel === 2) return 'DASHBOARD_CORE';
  if (node.cluster === 'agents' && node.orbitLevel === 2) return 'AGENT_CORE';
  if (node.cluster === 'documents' && node.orbitLevel === 2) return 'DOCUMENT_CORE';
  if (node.cluster === 'tools' && node.orbitLevel === 2) return 'TOOL_CORE';
  if (node.cluster === 'system' && node.orbitLevel === 2) return 'SYSTEM_CORE';
  if (node.type === 'core') return 'SOVEREIGN_CORE';
  if (node.type === 'engine') return 'ACTIVE_ENGINE';
  if (node.type === 'edition') return 'EDITION_NODE';
  if (node.type === 'module') return 'LINKED_MODULE';
  if (node.type === 'folder') return 'DIRECTORY_OBJECT';
  if (node.type === 'link-placeholder') return 'ACCESS_PORT';
  if (lowerLabel.endsWith('.py')) return 'PY_EXEC';
  if (lowerLabel.endsWith('.json')) return 'JSON_STATE';
  if (lowerLabel.endsWith('.md')) return 'MARKDOWN';
  return 'FILE_OBJECT';
}

function getNodeAccent(node: GraphNode, signals: DashboardSignals, materialColor: string) {
  if (node.type === 'core') return signals.palette.emphasis;
  if (node.type === 'engine') return signals.palette.secondary;
  if (node.type === 'edition') return node.color || signals.palette.warning;
  if (node.type === 'module') return node.color || signals.palette.emphasis;
  if (node.type === 'folder') return node.color || signals.palette.accent;
  if (node.type === 'link-placeholder') return node.color || signals.palette.warning;
  return materialColor;
}

type NodeActivityState = 'neutral' | 'active' | 'muted';

function resolveLinkedSystemId(nodeId: string, linkedSystems: LinkedSystem[]) {
  for (const system of linkedSystems) {
    const rootId = `project-${system.id}`;
    if (nodeId === rootId || nodeId.startsWith(`${rootId}-`)) {
      return system.id;
    }
  }
  return null;
}

function inferMotionProfile(node: GraphNode) {
  if (node.motionProfile) return node.motionProfile;
  if (node.type === 'core') return 'sentinel-linked';
  if (node.type === 'engine' || node.type === 'edition' || node.type === 'module' || node.type === 'link-placeholder') {
    return 'living';
  }
  return node.type === 'folder' ? 'living' : 'static';
}

function getNodeSystem(node: GraphNode, linkedSystems: LinkedSystem[]) {
  const systemId = node.systemId || resolveLinkedSystemId(node.id, linkedSystems);
  return systemId ? linkedSystems.find((system) => system.id === systemId) || null : null;
}

function getNodeCapabilities(node: GraphNode | null, linkedSystems: LinkedSystem[], hasAssetOverride: boolean): NodeCapabilities {
  if (!node) {
    return {
      kind: 'passive',
      accessMode: 'none',
      system: null,
      canExecute: false,
      canOpenDocument: false,
      canAssignAsset: false,
      canClearAsset: false,
      canFocus: false,
      blockReason: null,
    };
  }

  const system = getNodeSystem(node, linkedSystems);
  const accessMode: NodeAccessMode = system?.accessMode || 'none';

  if (node.type === 'link-placeholder') {
    return {
      kind: 'access',
      accessMode,
      system,
      canExecute: false,
      canOpenDocument: false,
      canAssignAsset: true,
      canClearAsset: hasAssetOverride,
      canFocus: true,
      blockReason: null,
    };
  }

  if (node.action) {
    return {
      kind: 'engine',
      accessMode,
      system,
      canExecute: true,
      canOpenDocument: false,
      canAssignAsset: true,
      canClearAsset: hasAssetOverride,
      canFocus: true,
      blockReason: null,
    };
  }

  if (node.filePath) {
    const blocked = system?.accessMode === 'structural';
    return {
      kind: 'document',
      accessMode,
      system,
      canExecute: false,
      canOpenDocument: !blocked,
      canAssignAsset: true,
      canClearAsset: hasAssetOverride,
      canFocus: true,
      blockReason: blocked ? 'STRUCTURAL_ONLY_LINK' : null,
    };
  }

  if (node.type === 'folder') {
    return {
      kind: 'folder',
      accessMode,
      system,
      canExecute: false,
      canOpenDocument: false,
      canAssignAsset: true,
      canClearAsset: hasAssetOverride,
      canFocus: true,
      blockReason: null,
    };
  }

  return {
    kind: 'system',
    accessMode,
    system,
    canExecute: false,
    canOpenDocument: false,
    canAssignAsset: true,
    canClearAsset: hasAssetOverride,
    canFocus: true,
    blockReason: null,
  };
}

function formatAssetLabel(stage?: { label?: string; src?: string } | null) {
  if (!stage?.src) return 'UNASSIGNED';
  return stage.label || stage.src.split('/').pop() || 'ASSET';
}

function NodeAnchor({
  position,
  children,
}: {
  position: [number, number, number];
  children: React.ReactNode;
}) {
  return <group position={position}>{children}</group>;
}

function NodeLabel({
  badge,
  label,
  color,
  compact = false,
  opacity = 0.94,
}: {
  badge: string;
  label: string;
  color: string;
  compact?: boolean;
  opacity?: number;
}) {
  return (
    <group position={[0, 0.06, 0]}>
      <Text
        position={[0, 0, compact ? -0.34 : -0.42]}
        rotation={[-Math.PI / 2, 0, 0]}
        color="#cbd5e1"
        fontSize={compact ? 0.12 : 0.13}
        anchorX="center"
        anchorY="middle"
        maxWidth={compact ? 4.4 : 5.6}
        outlineWidth={0.012}
        outlineColor="#020617"
        fillOpacity={Math.max(0.34, opacity * 0.74)}
      >
        {badge}
      </Text>
      <Text
        position={[0, 0, compact ? -0.08 : -0.18]}
        rotation={[-Math.PI / 2, 0, 0]}
        color={color}
        fontSize={compact ? 0.17 : 0.2}
        anchorX="center"
        anchorY="middle"
        maxWidth={compact ? 4.6 : 5.8}
        outlineWidth={0.016}
        outlineColor="#020617"
        fillOpacity={opacity}
      >
        {label}
      </Text>
    </group>
  );
}

function AggregateClusterBadge({
  badge,
  dictionary,
}: {
  badge: AggregateBadge;
  dictionary: Record<string, string>;
}) {
  const translatedLabel = tt(dictionary, `graph.cluster.${badge.cluster}`, GRAPH_CLUSTER_CONFIG[badge.cluster].label);
  const badgeColor = badge.active ? badge.color : new THREE.Color(badge.color).lerp(new THREE.Color('#94a3b8'), 0.38).getStyle();

  return (
    <group position={badge.position}>
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.46, 0.56, 48]} />
        <meshBasicMaterial
          color={badgeColor}
          transparent
          opacity={badge.active ? 0.34 : 0.2}
          blending={THREE.AdditiveBlending}
          side={THREE.DoubleSide}
        />
      </mesh>
      <Sphere args={[0.18, 16, 16]}>
        <meshBasicMaterial color={badgeColor} transparent opacity={badge.active ? 0.3 : 0.18} />
      </Sphere>
      <Text
        position={[0, 0.05, -0.26]}
        rotation={[-Math.PI / 2, 0, 0]}
        color="#e2e8f0"
        fontSize={0.13}
        anchorX="center"
        anchorY="middle"
        maxWidth={4.8}
        outlineWidth={0.012}
        outlineColor="#020617"
        fillOpacity={badge.active ? 0.92 : 0.72}
      >
        {translatedLabel}
      </Text>
      <Text
        position={[0, 0.05, 0.02]}
        rotation={[-Math.PI / 2, 0, 0]}
        color={badgeColor}
        fontSize={0.19}
        anchorX="center"
        anchorY="middle"
        outlineWidth={0.016}
        outlineColor="#020617"
        fillOpacity={badge.active ? 1 : 0.78}
      >
        {`${badge.count}`}
      </Text>
    </group>
  );
}

class SceneErrorBoundary extends React.Component<
  { children: React.ReactNode; dictionary: Record<string, string> },
  { hasError: boolean }
> {
  constructor(props: { children: React.ReactNode; dictionary: Record<string, string> }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: unknown) {
    console.error('[NEXUS_CORE] Scene runtime failure:', error);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'rgba(0,0,0,0.82)',
            color: '#fff',
            zIndex: 40,
            pointerEvents: 'none',
            textAlign: 'center',
            padding: '24px',
            letterSpacing: '2px',
            fontFamily: 'var(--font-mono)',
          }}
        >
          <div>
            <div style={{ fontSize: '0.72rem', opacity: 0.72, marginBottom: '10px' }}>
              {tt(this.props.dictionary, 'core.scene.guard', 'SCENE_GUARD_ACTIVE')}
            </div>
            <div style={{ fontSize: '0.92rem', fontWeight: 700 }}>
              {tt(this.props.dictionary, 'core.scene.guard.detail', 'RUNTIME_VISUAL_LAYER_FAILED_BUT_CONTROL_SURFACE_REMAINS_AVAILABLE')}
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

class NodeAssetErrorBoundary extends React.Component<
  { children: React.ReactNode; fallback: React.ReactNode; resetKey: string },
  { hasError: boolean }
> {
  constructor(props: { children: React.ReactNode; fallback: React.ReactNode; resetKey: string }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: unknown) {
    console.warn('[NEXUS_CORE] Node asset fallback engaged:', error);
  }

  componentDidUpdate(prevProps: Readonly<{ resetKey: string }>) {
    if (prevProps.resetKey !== this.props.resetKey && this.state.hasError) {
      this.setState({ hasError: false });
    }
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }

    return this.props.children;
  }
}

// SYSTEM NODE
function SystemNode({
  node, isPulsing, isSelected = false, eta = 1.0, drift = 0.0, signals, zoomTier, reducedMotion = false, familyAssetOverrides, activityState = 'neutral', editMode, onHover, onUnhover, onClick, onOpenAssetPicker, onSelectForEdit, onDraftAssetOffset, onCommitAssetOffset, onDraftAssetRotation, onCommitAssetRotation, onDraftAssetScale, onCommitAssetScale, imperiumOrbit,
}: {
  node: GraphNode;
  isPulsing?: boolean;
  isSelected?: boolean;
  eta?: number;
  drift?: number;
  signals: DashboardSignals;
  zoomTier: ZoomTier;
  reducedMotion?: boolean;
  familyAssetOverrides?: NodeAssetFamilyOverrides;
  activityState?: NodeActivityState;
  editMode?: boolean;
  onHover: (n: GraphNode) => void;
  onUnhover: () => void;
  onClick: (n: GraphNode) => void;
  onOpenAssetPicker?: (node: GraphNode, slot: AssetStageSlot) => void;
  onSelectForEdit?: (node: GraphNode) => void;
  onDraftAssetOffset?: (nodeId: string, offset: [number, number, number]) => void;
  onCommitAssetOffset?: (nodeId: string) => void;
  onDraftAssetRotation?: (nodeId: string, rotation: [number, number, number]) => void;
  onCommitAssetRotation?: (nodeId: string) => void;
  onDraftAssetScale?: (nodeId: string, scale: number) => void;
  onCommitAssetScale?: (nodeId: string) => void;
  imperiumOrbit?: { center: [number, number, number]; radius: number };
}) {
  const [hovered, setHovered] = useState(false);
  const groupRef = useRef<THREE.Group>(null!);
  const anchorRef = useRef<THREE.Group>(null!);
  const draggingRef = useRef(false);
  const rotatingRef = useRef(false);
  const scalingRef = useRef(false);
  const isImperium = node.id === 'imperium';
  const isLinkPlaceholder = node.type === 'link-placeholder';
  const isSphereNode = node.shape === 'sphere';
  const baseColor = node.color || '#888';
  const activeColor = isLinkPlaceholder
    ? (hovered ? '#94a3b8' : baseColor)
    : hovered
    ? '#93c5fd'
    : isSelected
    ? signals.palette.warning
    : baseColor;
  const materialColor = activeColor;
  const familyAccent = getNodeAccent(node, signals, materialColor);
  const badge = getNodeBadge(node);
  const isMuted = activityState === 'muted';
  const severityBoost = signals.mode === 'INCIDENT' ? 1 + signals.severity * 0.08 : 1;
  const importanceBoost = node.importance === 'primary' ? 1.08 : node.importance === 'secondary' ? 1 : 0.94;
  const activityBoost = activityState === 'active' ? 1.05 : isMuted ? 0.94 : 1;
  const interactionScale = isLinkPlaceholder ? (hovered ? 1.03 : 1) : hovered ? 1.11 : isSelected ? 1.06 : activityState === 'active' ? 1.02 : 1;
  const scale = (node.size * interactionScale * activityBoost) * (isPulsing ? 1.08 : 1) * severityBoost * importanceBoost;
  const labelOpacity = isLinkPlaceholder ? (hovered ? 0.9 : 0.8) : isMuted ? 0.46 : activityState === 'active' ? 1 : 0.94;
  const haloOpacityFactor = isLinkPlaceholder ? 0.18 : isMuted ? 0.35 : activityState === 'active' ? 1.04 : 0.92;
  const showLabel = shouldRenderNodeLabel(node, zoomTier, hovered, isSelected);
  const motionProfile = inferMotionProfile(node);

  const resolvedAssetProfile = getNodeAssetProfile(node, familyAssetOverrides);
  const usesExternalAsset = nodeUsesExternalAsset(node, familyAssetOverrides);
  const showEditOverlay = Boolean(editMode && usesExternalAsset && node.type !== 'file' && node.type !== 'folder');
  const assetResetKey = `${node.id}:${resolvedAssetProfile.appearance.src}:${resolvedAssetProfile.effect?.src || ''}`;
  const pOver = useCallback(() => { setHovered(true); onHover(node); }, [node, onHover]);
  const pOut = useCallback(() => { setHovered(false); onUnhover(); }, [onUnhover]);
  const pClick = useCallback(() => onClick(node), [node, onClick]);
  const assetOffsetY = resolvedAssetProfile.appearance.offset?.[1] ?? 0;
  const assetRotation = resolvedAssetProfile.appearance.rotation || [0, 0, 0];
  const editRingRadius = Math.max(scale * 1.08, 0.8);
  const editHandlePosition: [number, number, number] = [
    Math.sin(assetRotation[1] || 0) * editRingRadius,
    0.04,
    Math.cos(assetRotation[1] || 0) * editRingRadius,
  ];
  const scaleHandlePosition: [number, number, number] = [
    Math.sin((assetRotation[1] || 0) + Math.PI / 2) * (editRingRadius + 0.34),
    0.04,
    Math.cos((assetRotation[1] || 0) + Math.PI / 2) * (editRingRadius + 0.34),
  ];
  const startDrag = useCallback((event: any) => {
    if (!editMode || !usesExternalAsset) return;
    draggingRef.current = true;
    event.stopPropagation();
    event.target?.setPointerCapture?.(event.pointerId);
    onSelectForEdit?.(node);
  }, [editMode, node, onSelectForEdit, usesExternalAsset]);
  const moveDrag = useCallback((event: any) => {
    if (!draggingRef.current || !editMode || !usesExternalAsset) return;
    event.stopPropagation();
    const nextOffset: [number, number, number] = [
      event.point.x - node.position[0],
      assetOffsetY,
      event.point.z - node.position[2],
    ];
    onDraftAssetOffset?.(node.id, nextOffset);
  }, [assetOffsetY, editMode, node.id, node.position, onDraftAssetOffset, usesExternalAsset]);
  const endDrag = useCallback((event: any) => {
    if (!draggingRef.current) return;
    draggingRef.current = false;
    event.stopPropagation();
    event.target?.releasePointerCapture?.(event.pointerId);
    onCommitAssetOffset?.(node.id);
  }, [node.id, onCommitAssetOffset]);
  const startRotate = useCallback((event: any) => {
    if (!editMode || !usesExternalAsset) return;
    rotatingRef.current = true;
    event.stopPropagation();
    event.target?.setPointerCapture?.(event.pointerId);
    onSelectForEdit?.(node);
  }, [editMode, node, onSelectForEdit, usesExternalAsset]);
  const moveRotate = useCallback((event: any) => {
    if (!rotatingRef.current || !editMode || !usesExternalAsset) return;
    event.stopPropagation();
    const dx = event.point.x - node.position[0];
    const dz = event.point.z - node.position[2];
    const nextHeading = Math.atan2(dx, dz);
    const nextRotation: [number, number, number] = [assetRotation[0] || 0, nextHeading, assetRotation[2] || 0];
    onDraftAssetRotation?.(node.id, nextRotation);
  }, [assetRotation, editMode, node.id, node.position, onDraftAssetRotation, usesExternalAsset]);
  const endRotate = useCallback((event: any) => {
    if (!rotatingRef.current) return;
    rotatingRef.current = false;
    event.stopPropagation();
    event.target?.releasePointerCapture?.(event.pointerId);
    onCommitAssetRotation?.(node.id);
  }, [node.id, onCommitAssetRotation]);
  const startScale = useCallback((event: any) => {
    if (!editMode || !usesExternalAsset) return;
    scalingRef.current = true;
    event.stopPropagation();
    event.target?.setPointerCapture?.(event.pointerId);
    onSelectForEdit?.(node);
  }, [editMode, node, onSelectForEdit, usesExternalAsset]);
  const moveScale = useCallback((event: any) => {
    if (!scalingRef.current || !editMode || !usesExternalAsset) return;
    event.stopPropagation();
    const dx = event.point.x - node.position[0];
    const dz = event.point.z - node.position[2];
    const distance = Math.max(0.15, Math.sqrt(dx * dx + dz * dz));
    const nextScale = THREE.MathUtils.clamp(distance / Math.max(editRingRadius, 0.0001), 0.18, 6);
    onDraftAssetScale?.(node.id, nextScale);
  }, [editMode, editRingRadius, node.id, node.position, onDraftAssetScale, usesExternalAsset]);
  const endScale = useCallback((event: any) => {
    if (!scalingRef.current) return;
    scalingRef.current = false;
    event.stopPropagation();
    event.target?.releasePointerCapture?.(event.pointerId);
    onCommitAssetScale?.(node.id);
  }, [node.id, onCommitAssetScale]);
  const solidOpacity = isLinkPlaceholder
    ? (hovered ? 0.42 : 0.26)
    : isSelected
    ? 0.92
    : hovered
    ? 0.88
    : isMuted
    ? 0.42
    : 0.74;
  const wireOpacity = isLinkPlaceholder
    ? 0.08
    : isSelected
    ? 0.24
    : hovered
    ? 0.18
    : 0.12;

  const assetFallback = (
    <group>
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[Math.max(scale * 0.34, 0.18), Math.max(scale * 0.5, 0.26), 42]} />
        <meshBasicMaterial color={familyAccent} transparent opacity={Math.max(0.32, solidOpacity * 0.72)} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]}>
        <circleGeometry args={[Math.max(scale * 0.28, 0.14), 42]} />
        <meshBasicMaterial color={familyAccent} transparent opacity={Math.max(0.2, solidOpacity * 0.44)} />
      </mesh>
    </group>
  );
  const assetSupportVisual = (
    <group>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.02, 0]}>
        <ringGeometry args={[Math.max(scale * 0.42, 0.22), Math.max(scale * 0.62, 0.32), 48]} />
        <meshBasicMaterial color={familyAccent} transparent opacity={Math.max(0.18, solidOpacity * 0.42)} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.03, 0]}>
        <circleGeometry args={[Math.max(scale * 0.18, 0.1), 32]} />
        <meshBasicMaterial color={familyAccent} transparent opacity={Math.max(0.14, solidOpacity * 0.2)} />
      </mesh>
    </group>
  );
  const assetHybridBody = node.shape === 'octahedron'
    ? (
      <group>
        <Octahedron args={[scale * 0.72, 0]}>
          <meshBasicMaterial color={familyAccent} transparent opacity={Math.max(0.26, solidOpacity * 0.52)} />
        </Octahedron>
        <Octahedron args={[scale * 0.76, 0]}>
          <meshBasicMaterial color={familyAccent} transparent opacity={Math.max(0.14, wireOpacity * 1.2)} wireframe />
        </Octahedron>
      </group>
    )
    : node.shape === 'tetrahedron'
    ? (
      <group>
        <mesh>
          <tetrahedronGeometry args={[scale * 0.72, 0]} />
          <meshStandardMaterial
            color={familyAccent}
            emissive={familyAccent}
            emissiveIntensity={0.12 + (hovered || isSelected ? 0.08 : 0)}
            metalness={0.88}
            roughness={0.22}
            transparent
            opacity={Math.max(0.24, solidOpacity * 0.46)}
          />
        </mesh>
        <mesh>
          <tetrahedronGeometry args={[scale * 0.76, 0]} />
          <meshBasicMaterial color={familyAccent} transparent opacity={Math.max(0.1, wireOpacity * 1.2)} wireframe />
        </mesh>
      </group>
    )
    : node.shape === 'sphere'
    ? (
      <group>
        <Sphere args={[scale * 0.38, 24, 24]}>
          <meshStandardMaterial
            color={familyAccent}
            emissive={familyAccent}
            emissiveIntensity={0.08 + (hovered || isSelected ? 0.08 : 0)}
            metalness={0.62}
            roughness={0.34}
            transparent
            opacity={Math.max(0.22, solidOpacity * 0.34)}
          />
        </Sphere>
        <Sphere args={[scale * 0.42, 20, 20]}>
          <meshBasicMaterial color={familyAccent} transparent opacity={Math.max(0.1, wireOpacity)} wireframe />
        </Sphere>
      </group>
    )
    : node.shape === 'document'
    ? (
      <NodeGlyphSprite
        kind={
          node.label.toLowerCase().endsWith('.py')
            ? 'python'
            : node.label.toLowerCase().endsWith('.json')
            ? 'json'
            : node.label.toLowerCase().endsWith('.md')
            ? 'markdown'
            : 'generic'
        }
        accent={familyAccent}
        scale={scale * 1.36}
        opacity={Math.max(0.34, labelOpacity * 0.8)}
      />
    )
    : node.shape === 'folder-icon'
    ? <NodeGlyphSprite kind="folder" accent={familyAccent} scale={scale * 1.28} opacity={Math.max(0.34, labelOpacity * 0.8)} />
    : null;

  const wrapWithAnchor = (children: React.ReactNode) =>
    isImperium ? <group ref={anchorRef}>{children}</group> : <NodeAnchor position={node.position}>{children}</NodeAnchor>;

  useFrame((state) => {
    if (!isImperium || !imperiumOrbit || !anchorRef.current) return;
    const t = state.clock.elapsedTime;
    const angle = t * 0.08;
    anchorRef.current.position.set(
      imperiumOrbit.center[0] + Math.cos(angle) * imperiumOrbit.radius,
      node.position[1],
      imperiumOrbit.center[2] + Math.sin(angle) * imperiumOrbit.radius,
    );
  });

  useFrame((state, delta) => {
    if (!groupRef.current) return;
    const t = state.clock.elapsedTime + node.id.length * 0.09;
    const motionEnergy = reducedMotion ? 0 : motionProfile === 'sentinel-linked' ? 0.72 : motionProfile === 'living' ? 0.42 : 0.14;
    const pulse = isPulsing ? 0.032 : hovered || isSelected ? 0.022 : 0.012;
    const driftWave = Math.min(0.012, drift * 0.06);
    const zoomDamp = zoomTier === 'overview' ? 0.4 : zoomTier === 'cluster' ? 0.7 : 1;
    const baseLateralDrift = node.type === 'file'
      ? 0.008
      : node.type === 'folder'
      ? 0.012
      : node.shape === 'sphere'
      ? 0.024
      : node.shape === 'tetrahedron'
      ? 0.02
      : 0.016;
    const baseVerticalDrift = node.shape === 'sphere'
      ? 0.009
      : node.type === 'file' || node.type === 'folder'
      ? 0.004
      : 0.006;
    const anchorLerp = 1 - Math.exp(-delta * 7.5);
    const organicScale = 1 + (Math.sin(t * (node.shape === 'sphere' ? 1.8 : 2.4)) * pulse + driftWave) * motionEnergy * zoomDamp;
    const targetX = 0;
    const targetZ = 0;
    const targetY = node.shape === 'sphere'
      ? Math.sin(t * 1.16 + node.size) * baseVerticalDrift * motionEnergy
      : Math.sin(t * 1.5 + node.position[2] * 0.2) * baseVerticalDrift * motionEnergy;
    groupRef.current.scale.setScalar(organicScale);
    groupRef.current.position.x = THREE.MathUtils.lerp(groupRef.current.position.x, targetX, anchorLerp);
    groupRef.current.position.z = THREE.MathUtils.lerp(groupRef.current.position.z, targetZ, anchorLerp);
    groupRef.current.position.y = THREE.MathUtils.lerp(groupRef.current.position.y, targetY, anchorLerp);
    groupRef.current.rotation.y = (node.shape === 'octahedron' || node.shape === 'tetrahedron')
      ? Math.sin(t * 0.9) * 0.1 * motionEnergy
      : Math.sin(t * 0.42) * 0.04 * motionEnergy;
    groupRef.current.rotation.x = node.shape === 'tetrahedron'
      ? 0.05 + Math.cos(t * 1.1) * 0.04 * motionEnergy
      : 0;
  });

  if (usesExternalAsset) {
    return wrapWithAnchor(
      <group ref={groupRef} onPointerOver={pOver} onPointerOut={pOut} onClick={pClick}>
          <mesh visible={false} onClick={pClick} onPointerDown={startDrag} onPointerMove={moveDrag} onPointerUp={endDrag} onPointerLeave={endDrag}>
            <sphereGeometry args={[scale * 0.84, 18, 18]} />
          </mesh>
          {resolvedAssetProfile.preserveFallback !== false && assetHybridBody}
          {resolvedAssetProfile.preserveFallback !== false && assetSupportVisual}
          <NodeAssetErrorBoundary resetKey={assetResetKey} fallback={assetFallback}>
            <Suspense fallback={assetFallback}>
              <LazyNodeAssetRig
                node={node}
                accent={familyAccent}
                scale={scale * 1.02}
                pulsing={Boolean(isPulsing)}
                selected={isSelected}
                profile={resolvedAssetProfile}
              />
            </Suspense>
          </NodeAssetErrorBoundary>
          {showLabel && (
            <group position={[0, 0, -(scale * 0.7 + 1.0)]}>
              <NodeLabel badge={badge} label={node.label} color={familyAccent} opacity={labelOpacity} />
            </group>
          )}
          {showEditOverlay && isSelected && (
            <group>
              <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.02, 0]}>
                <ringGeometry args={[editRingRadius - 0.03, editRingRadius + 0.03, 48]} />
                <meshBasicMaterial color={familyAccent} transparent opacity={0.44} />
              </mesh>
              <mesh position={editHandlePosition} onPointerDown={startRotate} onPointerMove={moveRotate} onPointerUp={endRotate} onPointerLeave={endRotate}>
                <sphereGeometry args={[0.12, 18, 18]} />
                <meshBasicMaterial color="#f8fafc" transparent opacity={0.9} />
              </mesh>
              <mesh position={scaleHandlePosition} onPointerDown={startScale} onPointerMove={moveScale} onPointerUp={endScale} onPointerLeave={endScale}>
                <boxGeometry args={[0.18, 0.18, 0.18]} />
                <meshBasicMaterial color={signals.palette.warning} transparent opacity={0.9} />
              </mesh>
              <mesh position={[0, 0.03, 0]}>
                <sphereGeometry args={[0.06, 14, 14]} />
                <meshBasicMaterial color={familyAccent} transparent opacity={0.82} />
              </mesh>
            </group>
          )}
          {showEditOverlay && (
            <Html center position={[0, 0.2, -(scale * 0.92 + 0.58)]} style={{ pointerEvents: 'auto' }}>
              <div style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                padding: '4px',
                borderRadius: '999px',
                background: 'rgba(2,6,23,0.9)',
                border: `1px solid ${signals.palette.border}`,
                boxShadow: '0 10px 28px rgba(0,0,0,0.28)',
              }}>
                <button
                  onClick={(event) => {
                    event.stopPropagation();
                    onSelectForEdit?.(node);
                  }}
                  className="btn-nexus"
                  style={{ padding: '5px 8px', fontSize: '0.42rem', letterSpacing: '1.4px' }}
                >
                  EDIT
                </button>
                <button
                  onClick={(event) => {
                    event.stopPropagation();
                    onSelectForEdit?.(node);
                    onOpenAssetPicker?.(node, 'appearance');
                  }}
                  className="btn-nexus"
                  style={{ padding: '5px 8px', fontSize: '0.42rem', letterSpacing: '1.4px' }}
                >
                  GLB
                </button>
              </div>
            </Html>
          )}
      </group>,
    );
  }

  // 3D SHAPES
  if (node.shape === 'octahedron') {
    return wrapWithAnchor(
      <group ref={groupRef} onPointerOver={pOver} onPointerOut={pOut} onClick={pClick}>
          {/* 3D Invisible Hitbox for Guaranteed Selection */}
          <mesh visible={false} onClick={pClick}>
            <sphereGeometry args={[scale * 0.8, 16, 16]} />
          </mesh>
          <Octahedron args={[scale * 0.95, 0]}>
            <meshBasicMaterial color={familyAccent} transparent opacity={solidOpacity} />
          </Octahedron>
          <Octahedron args={[scale, 0]}>
            <meshBasicMaterial color={familyAccent} transparent opacity={wireOpacity} wireframe />
          </Octahedron>
          {showLabel && (
            <group position={[0, 0, -(scale + 1.0)]}>
              <NodeLabel badge={badge} label={node.label} color={familyAccent} opacity={labelOpacity} />
            </group>
          )}
      </group>,
    );
  }

  if (node.shape === 'tetrahedron') {
    return wrapWithAnchor(
      <group ref={groupRef} onPointerOver={pOver} onPointerOut={pOut} onClick={pClick}>
          <mesh visible={false} onClick={pClick}>
            <sphereGeometry args={[scale * 0.8, 16, 16]} />
          </mesh>
          <mesh>
            <tetrahedronGeometry args={[scale * 0.95, 0]} />
            <meshStandardMaterial color={familyAccent} emissive={familyAccent} emissiveIntensity={0.08 + (hovered || isSelected ? 0.12 : 0)} metalness={0.92} roughness={0.18} transparent opacity={solidOpacity} />
          </mesh>
          <mesh>
            <tetrahedronGeometry args={[scale, 0]} />
            <meshBasicMaterial color={familyAccent} transparent opacity={wireOpacity} wireframe />
          </mesh>
          {showLabel && (
            <group position={[0, 0, -(scale + 0.6)]}>
              <NodeLabel badge={badge} label={node.label} color={familyAccent} opacity={labelOpacity} />
            </group>
          )}
      </group>,
    );
  }

  if (node.shape === 'sphere') {
    return wrapWithAnchor(
      <group ref={groupRef} onPointerOver={pOver} onPointerOut={pOut} onClick={pClick}>
          <mesh visible={false} onClick={pClick}>
            <sphereGeometry args={[scale * 0.6, 16, 16]} />
          </mesh>
          {/* Hyper-Fidelity Sphere segments: 32x32 */}
          <Sphere args={[scale * 0.55, 32, 32]}>
            <meshStandardMaterial color={familyAccent} emissive={familyAccent} emissiveIntensity={0.06 + (hovered || isSelected ? 0.08 : 0)} metalness={0.68} roughness={0.32} transparent opacity={solidOpacity} />
          </Sphere>
          <Sphere args={[scale * 0.48, 24, 24]}>
            <meshBasicMaterial color={familyAccent} transparent opacity={Math.min(0.38, solidOpacity * 0.46)} />
          </Sphere>
          <Sphere args={[scale * 0.6, 32, 32]}>
            <meshBasicMaterial color={familyAccent} transparent opacity={wireOpacity} wireframe />
          </Sphere>
          {showLabel && (
            <group position={[0, 0, -(scale * 0.6 + 1.2)]}>
              <NodeLabel badge={badge} label={node.label} color={familyAccent} opacity={labelOpacity} />
            </group>
          )}
      </group>,
    );
  }

  // DOCUMENT SHAPE (Restored Forensic Files)
  if (node.shape === 'document') {
    const lowerLabel = node.label.toLowerCase();
    const isPy = lowerLabel.endsWith('.py');
    const isJson = lowerLabel.endsWith('.json');
    const isMd = lowerLabel.endsWith('.md');
    const glyphKind: DocumentGlyphKind = isPy
      ? 'python'
      : isJson
      ? 'json'
      : isMd
      ? 'markdown'
      : 'generic';

    return wrapWithAnchor(
      <group ref={groupRef} onPointerOver={pOver} onPointerOut={pOut} onClick={pClick}>
          <mesh visible={false} onClick={pClick}>
            <sphereGeometry args={[scale * 0.8, 16, 16]} />
          </mesh>
          <NodeGlyphSprite kind={glyphKind} accent={familyAccent} scale={scale * 1.95} opacity={labelOpacity} />
          
          <mesh rotation={[Math.PI / 2, 0, 0]}>
            <ringGeometry args={[scale * 0.45, scale * 0.52, 32]} />
            <meshBasicMaterial color={familyAccent} transparent opacity={wireOpacity} />
          </mesh>
          {showLabel && (
            <group position={[0, 0, -(scale * 1.34)]}>
              <NodeLabel badge={badge} label={node.label} color={familyAccent} compact opacity={labelOpacity} />
            </group>
          )}
      </group>,
    );
  }

  // FOLDER SHAPE
  if (node.shape === 'folder-icon') {
    return wrapWithAnchor(
      <group ref={groupRef} onPointerOver={pOver} onPointerOut={pOut} onClick={pClick}>
          <mesh visible={false} onClick={pClick}>
            <sphereGeometry args={[scale * 0.8, 16, 16]} />
          </mesh>
          <NodeGlyphSprite kind="folder" accent={familyAccent} scale={scale * 1.74} opacity={labelOpacity} />
          {showLabel && (
            <group position={[0, 0, -(scale * 1.08)]}>
              <NodeLabel badge={badge} label={`/${node.label}`} color={familyAccent} compact opacity={labelOpacity} />
            </group>
          )}
      </group>,
    );
  }

  return null;
}

function DecryptionHandshake({ onComplete, dictionary }: { onComplete: () => void; dictionary: Record<string, string> }) {
  const [stream, setStream] = useState<string[]>([]);
  useEffect(() => {
    const chars = "0123456789ABCDEF";
    const iv = setInterval(() => {
      let line = "";
      for (let i = 0; i < 40; i++) line += chars[Math.floor(Math.random() * 16)];
      setStream(prev => [line, ...prev].slice(0, 5));
    }, 40);
    setTimeout(() => { clearInterval(iv); setStream([]); onComplete(); }, 600);
    return () => clearInterval(iv);
  }, [onComplete]);

  if (stream.length === 0) return null;
  return (
    <div style={{ color: '#ffffff22', fontFamily: 'var(--font-mono)', fontSize: '0.7rem', paddingBottom: '20px', borderBottom: '1px solid #ffffff11', marginBottom: '20px' }}>
       <div style={{ color: '#ffffff', marginBottom: '10px', fontSize: '0.6rem', letterSpacing: '2px' }}>
         [ {tt(dictionary, 'viewer.handshake', 'INTEGRITY_HANDSHAKE_IN_PROGRESS')} ]
       </div>
       {stream.map((s, i) => <div key={i}>{s}</div>)}
    </div>
  );
}

function escapeRegex(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function countQueryMatches(content: string, query: string) {
  if (!query.trim()) return 0;
  const matches = content.match(new RegExp(escapeRegex(query.trim()), 'gi'));
  return matches ? matches.length : 0;
}

function highlightText(text: string, query: string, keyPrefix: string) {
  if (!query.trim()) return text;
  const normalizedQuery = query.trim().toLowerCase();
  const pattern = new RegExp(`(${escapeRegex(query.trim())})`, 'ig');
  return text.split(pattern).map((part, index) => (
    part.toLowerCase() === normalizedQuery ? (
      <mark key={`${keyPrefix}-${index}`} style={{ background: 'rgba(34, 211, 238, 0.22)', color: '#f8fafc', padding: '0 2px', borderRadius: '3px', boxShadow: '0 0 10px rgba(34, 211, 238, 0.18)' }}>{part}</mark>
    ) : (
      <React.Fragment key={`${keyPrefix}-${index}`}>{part}</React.Fragment>
    )
  ));
}

function inferDocumentFormat(fileName: string) {
  const lower = fileName.toLowerCase();
  if (lower.endsWith('.md')) return 'markdown';
  if (lower.endsWith('.json')) return 'json';
  if (lower.endsWith('.py') || lower.endsWith('.ts') || lower.endsWith('.tsx') || lower.endsWith('.js') || lower.endsWith('.jsx') || lower.endsWith('.sh')) return 'source';
  return 'text';
}

function syntaxSegments(line: string, format: 'json' | 'source' | 'text') {
  if (format === 'text') return [{ text: line, color: '#e2e8f0' }];
  const patterns = [
    { regex: /(#.*$)/g, color: '#94a3b8' },
    { regex: /(\/\/.*$)/g, color: '#94a3b8' },
    { regex: /("([^"\\]|\\.)*")/g, color: '#67e8f9' },
    { regex: /('([^'\\]|\\.)*')/g, color: '#67e8f9' },
    { regex: /\b(true|false|null|None)\b/g, color: '#fb7185' },
    { regex: /\b(def|class|return|if|elif|else|for|while|try|except|import|from|as|await|async|with|const|let|function|export|default|interface|type)\b/g, color: '#f59e0b' },
    { regex: /\b\d+(\.\d+)?\b/g, color: '#a78bfa' },
    { regex: /([{}\[\]():.,])/g, color: '#e2e8f0' },
  ];

  const matches: Array<{ start: number; end: number; color: string }> = [];
  patterns.forEach(({ regex, color }) => {
    const localRegex = new RegExp(regex.source, regex.flags);
    let match;
    while ((match = localRegex.exec(line)) !== null) {
      matches.push({ start: match.index, end: match.index + match[0].length, color });
      if (match[0].length === 0) break;
    }
  });

  matches.sort((a, b) => a.start - b.start || b.end - a.end);
  const filtered: typeof matches = [];
  let cursor = -1;
  matches.forEach((match) => {
    if (match.start >= cursor) {
      filtered.push(match);
      cursor = match.end;
    }
  });

  const segments: Array<{ text: string; color: string }> = [];
  let position = 0;
  filtered.forEach((match) => {
    if (match.start > position) {
      segments.push({ text: line.slice(position, match.start), color: '#e2e8f0' });
    }
    segments.push({ text: line.slice(match.start, match.end), color: match.color });
    position = match.end;
  });
  if (position < line.length) {
    segments.push({ text: line.slice(position), color: '#e2e8f0' });
  }
  return segments.length ? segments : [{ text: line, color: '#e2e8f0' }];
}

function renderCodeFrame(content: string, query: string, format: 'json' | 'source' | 'text') {
  return (
    <div style={{ display: 'grid', gap: '1px', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', overflow: 'hidden' }}>
      {content.split('\n').map((line, index) => {
        const queryHit = query.trim() && line.toLowerCase().includes(query.trim().toLowerCase());
        const segments = syntaxSegments(line, format);
        return (
          <div key={`code-line-${index}`} style={{ display: 'grid', gridTemplateColumns: '56px 1fr', background: queryHit ? 'rgba(34, 211, 238, 0.08)' : 'rgba(2, 6, 23, 0.72)' }}>
            <div style={{ padding: '5px 10px', textAlign: 'right', color: queryHit ? '#67e8f9' : 'rgba(255,255,255,0.38)', borderRight: '1px solid rgba(255,255,255,0.06)', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>
              {index + 1}
            </div>
            <div style={{ padding: '5px 14px', whiteSpace: 'pre-wrap', wordBreak: 'break-word', fontSize: '0.8rem', lineHeight: 1.7, fontFamily: 'var(--font-mono)' }}>
              {segments.map((segment, segmentIndex) => (
                <span key={`seg-${index}-${segmentIndex}`} style={{ color: segment.color }}>
                  {highlightText(segment.text, query, `code-${index}-${segmentIndex}`)}
                </span>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function renderInlineMarkdown(text: string, query: string, keyPrefix: string): React.ReactNode[] {
  const tokens = text.split(/(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*|\[[^\]]+\]\([^)]+\))/g).filter(Boolean);
  return tokens.map((token, index) => {
    if (/^`[^`]+`$/.test(token)) {
      return <code key={`${keyPrefix}-${index}`} style={{ fontFamily: 'var(--font-mono)', padding: '2px 6px', borderRadius: '6px', background: 'rgba(15, 23, 42, 0.9)', color: '#67e8f9' }}>{highlightText(token.slice(1, -1), query, `${keyPrefix}-code-${index}`)}</code>;
    }
    if (/^\*\*[^*]+\*\*$/.test(token)) {
      return <strong key={`${keyPrefix}-${index}`} style={{ color: '#f8fafc' }}>{highlightText(token.slice(2, -2), query, `${keyPrefix}-strong-${index}`)}</strong>;
    }
    if (/^\*[^*]+\*$/.test(token)) {
      return <em key={`${keyPrefix}-${index}`} style={{ color: '#cbd5e1' }}>{highlightText(token.slice(1, -1), query, `${keyPrefix}-em-${index}`)}</em>;
    }
    const linkMatch = token.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
    if (linkMatch) {
      return <a key={`${keyPrefix}-${index}`} href={linkMatch[2]} target="_blank" rel="noreferrer" style={{ color: '#67e8f9', textDecoration: 'underline' }}>{highlightText(linkMatch[1], query, `${keyPrefix}-link-${index}`)}</a>;
    }
    return <React.Fragment key={`${keyPrefix}-${index}`}>{highlightText(token, query, `${keyPrefix}-text-${index}`)}</React.Fragment>;
  });
}

function renderMarkdownSurface(content: string, query: string) {
  const lines = content.split('\n');
  const blocks: React.ReactNode[] = [];
  let codeFenceLanguage = '';
  let codeFenceBuffer: string[] = [];

  const flushCodeFence = (key: string) => {
    if (!codeFenceBuffer.length) return;
    blocks.push(
      <div key={key} style={{ margin: '14px 0' }}>
        {renderCodeFrame(codeFenceBuffer.join('\n'), query, codeFenceLanguage === 'json' ? 'json' : 'source')}
      </div>
    );
    codeFenceBuffer = [];
    codeFenceLanguage = '';
  };

  lines.forEach((line, index) => {
    const trimmed = line.trim();
    if (trimmed.startsWith('```')) {
      if (codeFenceLanguage) {
        flushCodeFence(`code-fence-${index}`);
      } else {
        codeFenceLanguage = trimmed.slice(3).trim() || 'source';
      }
      return;
    }

    if (codeFenceLanguage) {
      codeFenceBuffer.push(line);
      return;
    }

    if (!trimmed) {
      blocks.push(<div key={`gap-${index}`} style={{ height: '10px' }} />);
      return;
    }

    const heading = line.match(/^(#{1,6})\s+(.*)$/);
    if (heading) {
      const level = heading[1].length;
      const sizes = ['1.5rem', '1.32rem', '1.16rem', '1rem', '0.92rem', '0.86rem'];
      blocks.push(
        <div key={`heading-${index}`} style={{ marginTop: index === 0 ? 0 : '18px', marginBottom: '8px', color: '#f8fafc', fontWeight: 800, letterSpacing: '0.04em', fontSize: sizes[level - 1], textShadow: '0 0 18px rgba(255,255,255,0.1)' }}>
          {renderInlineMarkdown(heading[2], query, `heading-${index}`)}
        </div>
      );
      return;
    }

    if (/^---+$/.test(trimmed) || /^\*\*\*+$/.test(trimmed)) {
      blocks.push(<div key={`hr-${index}`} style={{ height: '1px', margin: '14px 0', background: 'linear-gradient(90deg, transparent, rgba(103,232,249,0.4), transparent)' }} />);
      return;
    }

    const quote = line.match(/^\s*>\s+(.*)$/);
    if (quote) {
      blocks.push(
        <div key={`quote-${index}`} style={{ margin: '10px 0', padding: '10px 14px', borderLeft: '2px solid rgba(103,232,249,0.6)', background: 'rgba(15, 23, 42, 0.54)', color: '#cbd5e1', fontStyle: 'italic' }}>
          {renderInlineMarkdown(quote[1], query, `quote-${index}`)}
        </div>
      );
      return;
    }

    const unordered = line.match(/^\s*[-*]\s+(.*)$/);
    if (unordered) {
      blocks.push(
        <div key={`li-${index}`} style={{ display: 'grid', gridTemplateColumns: '18px 1fr', gap: '10px', color: '#e2e8f0', margin: '6px 0' }}>
          <span style={{ color: '#67e8f9' }}>+</span>
          <div>{renderInlineMarkdown(unordered[1], query, `li-${index}`)}</div>
        </div>
      );
      return;
    }

    const ordered = line.match(/^\s*(\d+)\.\s+(.*)$/);
    if (ordered) {
      blocks.push(
        <div key={`ol-${index}`} style={{ display: 'grid', gridTemplateColumns: '28px 1fr', gap: '10px', color: '#e2e8f0', margin: '6px 0' }}>
          <span style={{ color: '#67e8f9', textAlign: 'right' }}>{ordered[1]}.</span>
          <div>{renderInlineMarkdown(ordered[2], query, `ol-${index}`)}</div>
        </div>
      );
      return;
    }

    blocks.push(
      <div key={`p-${index}`} style={{ color: '#e2e8f0', lineHeight: 1.85, margin: '7px 0' }}>
        {renderInlineMarkdown(line, query, `p-${index}`)}
      </div>
    );
  });

  flushCodeFence('code-fence-final');
  return <div>{blocks}</div>;
}

function renderDocumentSurface(doc: OpenDocState, query: string, dictionary: Record<string, string>) {
  const format = inferDocumentFormat(doc.fileName);
  const lowerFormat = format as 'markdown' | 'json' | 'source' | 'text';

  if (lowerFormat === 'markdown') {
    return renderMarkdownSurface(doc.content, query);
  }

  if (lowerFormat === 'json') {
    try {
      const normalized = JSON.stringify(JSON.parse(doc.content), null, 2);
      return renderCodeFrame(normalized, query, 'json');
    } catch {
      return renderCodeFrame(doc.content, query, 'json');
    }
  }

  if (lowerFormat === 'source') {
    return renderCodeFrame(doc.content, query, 'source');
  }

  if (!doc.content.trim()) {
    return (
      <div style={{ color: 'rgba(255,255,255,0.56)', fontStyle: 'italic', letterSpacing: '0.06em' }}>
        {tt(dictionary, 'core.wave.stream_idle', 'STREAM_IDLE')}
      </div>
    );
  }

  return renderCodeFrame(doc.content, query, 'text');
}

function formatReplayAge(timestamp: number) {
  const seconds = Math.max(0, Math.floor((Date.now() - timestamp) / 1000));
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
  return `${Math.floor(seconds / 3600)}h`;
}

function ModeField({
  signals,
  reducedMotion,
}: {
  signals: DashboardSignals;
  reducedMotion: boolean;
}) {
  const ringOpacity = reducedMotion ? 0.12 : 0.18 + signals.activity * 0.06;

  return (
    <group>
      {signals.mode === 'STABLE' && (
        <>
          <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, -0.15, 0]}>
            <ringGeometry args={[4.5, 4.7, 64]} />
            <meshBasicMaterial color={signals.palette.secondary} transparent opacity={ringOpacity} blending={THREE.AdditiveBlending} side={THREE.DoubleSide} />
          </mesh>
          <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, -0.2, 0]}>
            <ringGeometry args={[8.2, 8.28, 96]} />
            <meshBasicMaterial color={signals.palette.emphasis} transparent opacity={0.08} blending={THREE.AdditiveBlending} side={THREE.DoubleSide} />
          </mesh>
        </>
      )}

      {signals.mode === 'AUDIT' && (
        <>
          <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, 0, 0]}>
            <ringGeometry args={[4.2, 4.28, 96]} />
            <meshBasicMaterial color={signals.palette.accent} transparent opacity={0.2} blending={THREE.AdditiveBlending} side={THREE.DoubleSide} />
          </mesh>
          <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, 1.6, 0]}>
            <ringGeometry args={[6.6, 6.7, 96]} />
            <meshBasicMaterial color={signals.palette.secondary} transparent opacity={0.12} blending={THREE.AdditiveBlending} side={THREE.DoubleSide} />
          </mesh>
          <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, -1.6, 0]}>
            <ringGeometry args={[6.6, 6.7, 96]} />
            <meshBasicMaterial color={signals.palette.secondary} transparent opacity={0.12} blending={THREE.AdditiveBlending} side={THREE.DoubleSide} />
          </mesh>
        </>
      )}

      {signals.mode === 'INCIDENT' && (
        <>
          <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, -0.2, 0]}>
            <ringGeometry args={[4.8, 5.05, 96]} />
            <meshBasicMaterial color={signals.palette.accent} transparent opacity={0.24 + signals.severity * 0.08} blending={THREE.AdditiveBlending} side={THREE.DoubleSide} />
          </mesh>
          <mesh rotation={[0, 0, Math.PI / 2]} position={[0, 0, 0]}>
            <torusGeometry args={[5.3, 0.06, 16, 80]} />
            <meshBasicMaterial color={signals.palette.warning} transparent opacity={0.16} blending={THREE.AdditiveBlending} />
          </mesh>
        </>
      )}

      {signals.mode === 'SEAL' && (
        <>
          <Sphere args={[5.1, 26, 26]} position={[0, 0, 0]}>
            <meshBasicMaterial color={signals.palette.accent} wireframe transparent opacity={0.11} blending={THREE.AdditiveBlending} />
          </Sphere>
          <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, 0, 0]}>
            <ringGeometry args={[5.25, 5.34, 96]} />
            <meshBasicMaterial color={signals.palette.warning} transparent opacity={0.18} blending={THREE.AdditiveBlending} side={THREE.DoubleSide} />
          </mesh>
        </>
      )}
    </group>
  );
}

function SceneRig({
  signals,
  reducedMotion,
  cameraMode,
  focusedNode,
  controlsRef,
  sceneBounds,
}: {
  signals: DashboardSignals;
  reducedMotion: boolean;
  cameraMode: CameraMode;
  focusedNode: GraphNode | null;
  controlsRef: React.MutableRefObject<any>;
  sceneBounds: { minX: number; maxX: number; minZ: number; maxZ: number };
}) {
  const { camera } = useThree();
  const positionRef = useRef(new THREE.Vector3(0, 34, 0.001));
  const lookAtRef = useRef(new THREE.Vector3(0, 0, 0));
  const zoomRef = useRef(30);

  useFrame((_state, delta) => {
    if (cameraMode === 'manual') {
      if (controlsRef.current?.target) {
        const marginX = 10;
        const marginZ = 10;
        const target = controlsRef.current.target as THREE.Vector3;
        const clampedX = THREE.MathUtils.clamp(target.x, sceneBounds.minX - marginX, sceneBounds.maxX + marginX);
        const clampedZ = THREE.MathUtils.clamp(target.z, sceneBounds.minZ - marginZ, sceneBounds.maxZ + marginZ);
        const deltaX = clampedX - target.x;
        const deltaZ = clampedZ - target.z;
        if (deltaX !== 0 || deltaZ !== 0) {
          target.set(clampedX, 0, clampedZ);
          camera.position.x += deltaX;
          camera.position.z += deltaZ;
          controlsRef.current.update();
        }
      }
      return;
    }
    const topHeight = signals.mode === 'INCIDENT'
      ? 36
      : signals.mode === 'AUDIT'
      ? 34
      : signals.mode === 'SEAL'
      ? 33
      : 35;

    if (cameraMode === 'focus' && focusedNode) {
      lookAtRef.current.set(focusedNode.position[0], 0, focusedNode.position[2]);
      positionRef.current.set(focusedNode.position[0], topHeight, focusedNode.position[2] + 0.001);
      zoomRef.current = focusedNode.type === 'core'
        ? 44
        : focusedNode.type === 'edition' || focusedNode.type === 'module'
        ? 36
        : 32;
    } else {
      lookAtRef.current.set(0, 0, 0);
      positionRef.current.set(0, topHeight, 0.001);
      zoomRef.current = signals.mode === 'INCIDENT' ? 26 : signals.mode === 'AUDIT' ? 28 : 30;
    }

    const lerpFactor = 1 - Math.exp(-delta * (reducedMotion ? 1.4 : 2.2));
    camera.position.lerp(positionRef.current, lerpFactor);
    camera.up.set(0, 0, -1);

    if (controlsRef.current?.target) {
      controlsRef.current.target.lerp(lookAtRef.current, 1 - Math.exp(-delta * 3.2));
      controlsRef.current.update();
    }

    if ('zoom' in camera) {
      const orthoCamera = camera as THREE.OrthographicCamera;
      orthoCamera.zoom = THREE.MathUtils.lerp(orthoCamera.zoom, zoomRef.current, 1 - Math.exp(-delta * 2.2));
      orthoCamera.updateProjectionMatrix();
    }
    if (!controlsRef.current?.target) {
      camera.lookAt(lookAtRef.current);
    }
  });

  return null;
}

function ZoomTierTracker({
  onZoomTierChange,
}: {
  onZoomTierChange: (tier: ZoomTier) => void;
}) {
  const { camera } = useThree();
  const tierRef = useRef<ZoomTier>(deriveZoomTier(('zoom' in camera ? (camera as THREE.OrthographicCamera).zoom : 30)));

  useFrame(() => {
    if (!('zoom' in camera)) return;
    const nextTier = deriveZoomTier((camera as THREE.OrthographicCamera).zoom);
    if (nextTier !== tierRef.current) {
      tierRef.current = nextTier;
      onZoomTierChange(nextTier);
    }
  });

  return null;
}

function CanvasBackgroundSync({
}: {
  background: string;
  fog: string;
}) {
  const { gl, scene } = useThree();

  useEffect(() => {
    gl.setClearColor('#000000', 0);
    scene.background = null;
    scene.fog = null;
  }, [gl, scene]);

  return null;
}

function IntegrityHalo({
  signals,
  chainStatus,
  activeCommand,
  reducedMotion,
}: {
  signals: DashboardSignals;
  chainStatus?: ChainStatusSnapshot | null;
  activeCommand?: string | null;
  reducedMotion: boolean;
}) {
  const breached = chainStatus ? !chainStatus.intact : false;
  const activityBoost = activeCommand ? 0.04 : 0;
  const shellColor = breached ? signals.palette.accent : signals.palette.secondary;
  const ringColor = signals.mode === 'SEAL' ? signals.palette.warning : signals.palette.emphasis;

  return (
    <group>
      <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, 0, 0]}>
        <ringGeometry args={[3.85, 4.04, 128]} />
        <meshBasicMaterial
          color={ringColor}
          transparent
          opacity={0.14 + signals.chainTrust * 0.09 + activityBoost}
          blending={THREE.AdditiveBlending}
          side={THREE.DoubleSide}
        />
      </mesh>
      <mesh rotation={[0, Math.PI / 2, 0]} position={[0, 0, 0]}>
        <torusGeometry args={[4.35, 0.05, 20, 144]} />
        <meshBasicMaterial
          color={shellColor}
          transparent
          opacity={breached ? 0.18 + signals.severity * 0.08 : 0.08 + signals.chainTrust * 0.06}
          blending={THREE.AdditiveBlending}
        />
      </mesh>
      <Sphere args={[4.7, 28, 28]} position={[0, 0, 0]}>
        <meshBasicMaterial
          color={shellColor}
          wireframe
          transparent
          opacity={signals.mode === 'SEAL' ? 0.14 : breached ? 0.1 : 0.05 + signals.activity * 0.03}
          blending={THREE.AdditiveBlending}
        />
      </Sphere>
    </group>
  );
}

function ModeDirectiveField({
  signals,
  reducedMotion,
}: {
  signals: DashboardSignals;
  reducedMotion: boolean;
}) {
  if (signals.mode !== 'INCIDENT' && signals.mode !== 'SEAL') return null;

  return (
    <group>
      {signals.mode === 'INCIDENT' && (
        <>
          {[0, 1, 2].map((index) => (
            <mesh key={`incident-ring-${index}`} rotation={[Math.PI / 2, index * 0.36, index * 0.18]} position={[0, (index - 1) * 1.4, 0]}>
              <torusGeometry args={[6.4 + index * 0.95, 0.05 + index * 0.01, 18, 120]} />
              <meshBasicMaterial color={index === 1 ? signals.palette.warning : signals.palette.accent} transparent opacity={0.12 + signals.severity * 0.05 - index * 0.02} blending={THREE.AdditiveBlending} />
            </mesh>
          ))}
          {[0, 1, 2, 3].map((index) => (
            <mesh key={`incident-column-${index}`} position={[Math.cos(index * (Math.PI / 2)) * 6.8, 0, Math.sin(index * (Math.PI / 2)) * 6.8]}>
              <cylinderGeometry args={[0.05, 0.18, 11, 10, 1, true]} />
              <meshBasicMaterial color={signals.palette.accent} transparent opacity={0.12 + signals.severity * 0.04} blending={THREE.AdditiveBlending} side={THREE.DoubleSide} />
            </mesh>
          ))}
        </>
      )}

      {signals.mode === 'SEAL' && (
        <>
          <Sphere args={[7.1, 32, 32]}>
            <meshBasicMaterial color={signals.palette.warning} wireframe transparent opacity={0.08} blending={THREE.AdditiveBlending} />
          </Sphere>
          {[0, 1, 2, 3, 4, 5].map((index) => {
            const angle = (Math.PI * 2 * index) / 6;
            return (
              <group key={`seal-lock-${index}`} position={[Math.cos(angle) * 6.1, Math.sin(angle * 1.5) * 1.7, Math.sin(angle) * 6.1]}>
                <Sphere args={[0.18, 18, 18]}>
                  <meshBasicMaterial color={signals.palette.warning} transparent opacity={0.24} blending={THREE.AdditiveBlending} />
                </Sphere>
                <mesh rotation={[Math.PI / 2, angle, 0]}>
                  <ringGeometry args={[0.32, 0.38, 28]} />
                  <meshBasicMaterial color={signals.palette.emphasis} transparent opacity={0.16} blending={THREE.AdditiveBlending} side={THREE.DoubleSide} />
                </mesh>
              </group>
            );
          })}
        </>
      )}
    </group>
  );
}

const NexusCore = ({ 
  linkedSystems,
  activeLinkedSystemId,
  language, 
  setLinkedSystems,
  setActiveLinkedSystemId,
  physics: externalPhysics,
  drift: externalDrift,
  merkle: externalMerkle,
  chainEvents,
  chainStatus,
  activeCommand,
}: NexusCoreProps) => {
  const [hoveredNode, setHoveredNode] = useState<GraphNode | null>(null);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [openDoc, setOpenDoc] = useState<OpenDocState | null>(null);
  const [unlinkModal, setUnlinkModal] = useState<string | null>(null);
  const [pulsingNodes, setPulsingNodes] = useState<Set<string>>(new Set());
  const [toastMsg, setToastMsg] = useState<{ msg: string; detail?: string } | null>(null);
  const [qualityTier, setQualityTier] = useState<QualityTier>('ultra');
  const [reducedMotion, setReducedMotion] = useState(false);
  const [audioArmed, setAudioArmed] = useState(false);
  const [cameraMode, setCameraMode] = useState<CameraMode>('overview');
  const [zoomTier, setZoomTier] = useState<ZoomTier>('cluster');
  const [merkleReplay, setMerkleReplay] = useState<MerkleReplayEntry[]>([]);
  const [docQuery, setDocQuery] = useState('');
  const [isRightRailOpen, setIsRightRailOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    { id: 'chat-system', role: 'system', content: 'CLAWDBOT LINK READY // LOCAL BRIDGE STANDBY' },
  ]);
  const [chatPrompt, setChatPrompt] = useState('');
  const [chatBusy, setChatBusy] = useState(false);
  const [nodeAssetOverrides, setNodeAssetOverrides] = useState<Record<string, GraphNodeAssetOverride>>({});
  const [nodeAssetDrafts, setNodeAssetDrafts] = useState<Record<string, GraphNodeAssetOverride>>({});
  const [familyAssetOverrides, setFamilyAssetOverrides] = useState<NodeAssetFamilyOverrides>({});
  const [editModeSessionBaseline, setEditModeSessionBaseline] = useState<EditModeSessionBaseline | null>(null);
  const [isProcessingCanonicalAssets, setIsProcessingCanonicalAssets] = useState(false);
  const [pendingAssetTarget, setPendingAssetTarget] = useState<PendingAssetTarget | null>(null);
  const [assetEditState, setAssetEditState] = useState<NodeAssetEditState>({ enabled: false });
  const [editModeAuthorized, setEditModeAuthorized] = useState(false);
  const [editModePromptOpen, setEditModePromptOpen] = useState(false);
  const [editModePassword, setEditModePassword] = useState('');
  const [selectedSentinelIndex, setSelectedSentinelIndex] = useState<number | null>(null);
  const [sentinelAssetDraft, setSentinelAssetDraft] = useState<Partial<NodeAssetStage> | null>(null);
  const [linkedSystemScanTimes, setLinkedSystemScanTimes] = useState<Record<string, number>>({});
  const audioContextRef = useRef<AudioContext | null>(null);
  const controlsRef = useRef<any>(null);
  const assetFileInputRef = useRef<HTMLInputElement>(null);
  const previousModeRef = useRef<string>('');
  const previousCommandRef = useRef<string | null>(null);
  const previousChainIntactRef = useRef<boolean | null>(null);
  
  // Authority: Use props from page.tsx
  const physics = externalPhysics || { H: 0, H_max: 0, eta: 1.0, N: 0, W: 0, gini: 0 };
  const drift = typeof externalDrift === 'number' ? externalDrift : 0;
  const merkle = externalMerkle || '00000000000000000000000000000000';
  const t = translations[language] || translations['EN'];
  const primaryLinkedSystem = linkedSystems.find((system) => system.id === activeLinkedSystemId) || linkedSystems[0] || null;
  const activeSystemIndex = primaryLinkedSystem ? linkedSystems.findIndex((system) => system.id === primaryLinkedSystem.id) : -1;
  const [logs, setLogs] = useState<{ id: number; msg: string }[]>([]);
  const [displayNode, setDisplayNode] = useState<GraphNode | null>(null);
  const deferredDocQuery = useDeferredValue(docQuery);
  const sessionStart = useMemo(() => Date.now(), []);
  const signals = useMemo(() => deriveDashboardSignals({
    state: {
      merkle_root: merkle,
      drift_kl: drift,
      physics,
    },
    chainEvents,
    chainStatus,
    activeAction: activeCommand,
    linkedProject: primaryLinkedSystem?.name || null,
    linkedProjectCount: linkedSystems.length,
    liveLogs: logs,
  }), [activeCommand, chainEvents, chainStatus, drift, linkedSystems.length, logs, merkle, physics, primaryLinkedSystem?.name]);
  const normalizedEta = Math.max(0, Math.min(1, physics.eta || 0));
  const normalizedDrift = Math.max(0, Math.min(1, drift));
  const modeLabelText = translateModeLabel(signals.modeLabel, t);
  const modeReasonText = translateReason(signals.modeReason, t);
  const activeVectorText = translateActiveCommand(activeCommand, t);
  const cameraModeLabel = cameraMode === 'focus'
    ? tt(t, 'nav.mode.focus', 'FOCUS')
    : cameraMode === 'manual'
    ? tt(t, 'nav.mode.manual', 'MANUAL')
    : tt(t, 'nav.mode.overview', 'OVERVIEW');
  const healthLabel = normalizedEta >= 0.75
    ? t['hud.health.healthy']
    : normalizedEta >= 0.50
    ? t['hud.health.moderate']
    : t['hud.health.severe'];
  const healthColor = normalizedEta >= 0.75
    ? signals.palette.emphasis
    : normalizedEta >= 0.50
    ? signals.palette.secondary
    : signals.palette.warning;
  const syncLevel = Math.max(0, Math.min(100, (1 - normalizedDrift) * 100));
  const fluxColor = drift > 0.1
    ? signals.palette.accent
    : drift > 0.03
    ? signals.palette.secondary
    : signals.palette.warning;
  const fluxBorder = signals.palette.border;
  const fluxBackground = signals.palette.panelSoft;

  const [viewportWidth, setViewportWidth] = useState(1440);
  const isTablet = viewportWidth < 1180;
  const isPhone = viewportWidth < 780;
  const isTiny = viewportWidth < 420;
  const dockWidth = isTiny
    ? 'calc(100vw - 20px)'
    : isPhone
    ? 'calc(100vw - 24px)'
    : isTablet
    ? 'min(700px, calc(100vw - 56px))'
    : 'min(780px, calc(100vw - 500px))';
  const dockPadding = isPhone
    ? '12px 12px 14px'
    : isTablet
    ? '14px 16px 16px'
    : '15px 18px 18px';
  const railRight = isTiny ? 10 : isPhone ? 12 : isTablet ? 24 : 72;
  const titleTelemetryWidth = isTiny ? 'min(188px, calc(100vw - 24px))' : isPhone ? 'min(216px, calc(100vw - 26px))' : isTablet ? '238px' : '282px';
  const overlayGlowText = { color: signals.palette.emphasis, textShadow: `0 0 18px ${signals.palette.secondary}3a` } as const;
  const overlaySoftText = { color: 'rgba(255,255,255,0.76)', textShadow: `0 0 12px ${signals.palette.secondary}22` } as const;
  const overlayFaintText = { color: 'rgba(255,255,255,0.64)', textShadow: `0 0 10px ${signals.palette.secondary}1c` } as const;
  const qualityProfile = useMemo(() => {
    if (qualityTier === 'safe') {
      return { particleCount: 280, particleSize: 0.045, rainCount: 0, fxScale: 0.42, dpr: [1, 1.05] as [number, number], autoRotateSpeed: 0.18, droneCount: 2, structuralStreamCount: 3, hoverStreamCount: 5 };
    }
    if (qualityTier === 'balanced') {
      return { particleCount: 520, particleSize: 0.042, rainCount: 36, fxScale: 0.66, dpr: [1, 1.2] as [number, number], autoRotateSpeed: 0.24, droneCount: 3, structuralStreamCount: 5, hoverStreamCount: 8 };
    }
    return { particleCount: 860, particleSize: 0.038, rainCount: 72, fxScale: 0.82, dpr: [1, 1.35] as [number, number], autoRotateSpeed: 0.28, droneCount: 5, structuralStreamCount: 7, hoverStreamCount: 11 };
  }, [qualityTier]);
  useEffect(() => {
    setDocQuery('');
  }, [openDoc?.filePath]);

  useEffect(() => {
    setMerkleReplay((previous) => {
      const latestEventType = chainEvents[0]?.type || 'STATE_SYNC';
      if (previous[0]?.hash === merkle && previous[0]?.eventType === latestEventType) {
        return previous;
      }
      const nextEntry: MerkleReplayEntry = {
        id: Date.now(),
        hash: merkle,
        eventType: latestEventType,
        chainTrust: signals.chainTrust,
        drift,
        timestamp: Date.now(),
      };
      return [nextEntry, ...previous].slice(0, 7);
    });
  }, [chainEvents, drift, merkle, signals.chainTrust]);

  useEffect(() => {
    const updateViewport = () => setViewportWidth(window.innerWidth);
    updateViewport();
    window.addEventListener('resize', updateViewport);
    return () => window.removeEventListener('resize', updateViewport);
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const media = window.matchMedia('(prefers-reduced-motion: reduce)');
    const assessQuality = () => {
      const nav = window.navigator as Navigator & { deviceMemory?: number };
      const memory = Number(nav.deviceMemory || 8);
      const cores = Number(nav.hardwareConcurrency || 8);
      const prefersReduced = media.matches;
      setReducedMotion(prefersReduced);

      if (prefersReduced || viewportWidth < 720 || memory <= 4 || cores <= 4) {
        setQualityTier('safe');
      } else if (viewportWidth < 1280 || memory <= 8 || cores <= 8) {
        setQualityTier('balanced');
      } else {
        setQualityTier('ultra');
      }
    };

    assessQuality();

    if (typeof media.addEventListener === 'function') {
      media.addEventListener('change', assessQuality);
      return () => media.removeEventListener('change', assessQuality);
    }

    media.addListener(assessQuality);
    return () => media.removeListener(assessQuality);
  }, [viewportWidth]);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const armAudio = async () => {
      if (audioContextRef.current) {
        if (audioContextRef.current.state === 'suspended') {
          await audioContextRef.current.resume().catch(() => {});
        }
        setAudioArmed(audioContextRef.current.state === 'running');
        return;
      }

      const AudioCtor = window.AudioContext || (window as Window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
      if (!AudioCtor) return;

      try {
        const ctx = new AudioCtor();
        audioContextRef.current = ctx;
        await ctx.resume().catch(() => {});
        setAudioArmed(ctx.state === 'running');
      } catch {
        setAudioArmed(false);
      }
    };

    window.addEventListener('pointerdown', armAudio);
    window.addEventListener('keydown', armAudio);

    return () => {
      window.removeEventListener('pointerdown', armAudio);
      window.removeEventListener('keydown', armAudio);
    };
  }, []);

  useEffect(() => {
    return () => {
      audioContextRef.current?.close().catch(() => {});
    };
  }, []);

  useEffect(() => {
    const ctx = audioContextRef.current;
    if (!audioArmed || !ctx || ctx.state !== 'running') return;

    const playCue = (frequencies: number[], duration = 0.12, type: OscillatorType = 'sine', gainLevel = 0.018) => {
      const now = ctx.currentTime;
      frequencies.forEach((freq, index) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(freq, now + index * 0.045);
        gain.gain.setValueAtTime(0.0001, now + index * 0.045);
        gain.gain.exponentialRampToValueAtTime(gainLevel, now + index * 0.045 + 0.012);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + index * 0.045 + duration);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now + index * 0.045);
        osc.stop(now + index * 0.045 + duration + 0.03);
      });
    };

    if (previousModeRef.current && previousModeRef.current !== signals.mode) {
      if (signals.mode === 'AUDIT') playCue([520, 660, 780], 0.11, 'triangle', 0.014);
      if (signals.mode === 'SEAL') playCue([392, 523, 784], 0.14, 'sine', 0.016);
      if (signals.mode === 'INCIDENT') playCue([196, 156, 116], 0.16, 'sawtooth', 0.02);
      if (signals.mode === 'STABLE') playCue([440, 660], 0.1, 'triangle', 0.012);
    }

    if (activeCommand && previousCommandRef.current !== activeCommand) {
      if (activeCommand.includes('AUDIT')) playCue([600, 820], 0.1, 'triangle', 0.014);
      else if (activeCommand.includes('SEAL')) playCue([340, 510, 680], 0.13, 'sine', 0.016);
      else if (activeCommand.includes('CRYSTALLIZE')) playCue([480, 620, 760], 0.1, 'triangle', 0.015);
      else playCue([420, 540], 0.08, 'triangle', 0.012);
    }

    if (chainStatus && previousChainIntactRef.current !== chainStatus.intact) {
      if (chainStatus.intact) playCue([660, 880], 0.09, 'sine', 0.013);
      else playCue([170, 138, 110], 0.18, 'square', 0.02);
    }

    previousModeRef.current = signals.mode;
    previousCommandRef.current = activeCommand;
    previousChainIntactRef.current = chainStatus?.intact ?? null;
  }, [activeCommand, audioArmed, chainStatus, signals.mode]);

  useEffect(() => {
    let cancelled = false;
    fetch('/api/node-assets')
      .then((response) => response.json())
      .then((payload) => {
        if (cancelled) return;
        if (payload?.success && payload.overrides) {
          setNodeAssetOverrides(payload.overrides);
          setFamilyAssetOverrides(payload.familyProfiles || {});
        }
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);


  const { staticNodes, staticEdges, dynamicNodes, dynamicEdges } = useMemo(() => {
    const { nodes: sn, edges: se } = buildStaticGraph(language, linkedSystems.length);
    const dn: GraphNode[] = [];
    const de: GraphEdge[] = [];
    linkedSystems.forEach((system, index) => {
      const result = buildProjectNodes(system, language, index, linkedSystems.length);
      dn.push(...result.nodes);
      de.push(...result.edges);
    });
    return { staticNodes: sn, staticEdges: se, dynamicNodes: dn, dynamicEdges: de };
  }, [language, linkedSystems]);

  const allNodes = useMemo(
    () =>
      [...staticNodes, ...dynamicNodes].map((node) => {
        const systemId = node.systemId ?? resolveLinkedSystemId(node.id, linkedSystems);
        return {
          ...node,
          systemId,
          motionProfile: inferMotionProfile(node),
          assetOverride: mergeGraphNodeAssetOverride(nodeAssetOverrides[node.id], nodeAssetDrafts[node.id]),
        };
      }),
    [dynamicNodes, linkedSystems, nodeAssetDrafts, nodeAssetOverrides, staticNodes],
  );
  const allEdges = useMemo(() => [...staticEdges, ...dynamicEdges], [staticEdges, dynamicEdges]);
  const nodesById = useMemo(() => new Map(allNodes.map((node) => [node.id, node])), [allNodes]);
  const selectedNode = useMemo(() => allNodes.find((node) => node.id === selectedNodeId) || null, [allNodes, selectedNodeId]);
  const sentinelInspectorNode = useMemo<GraphNode | null>(() => {
    if (selectedSentinelIndex === null) return null;
    return {
      id: `sentinel-${selectedSentinelIndex}`,
      label: `SENTINEL-${selectedSentinelIndex + 1}`,
      position: [0, 0, 0],
      type: 'module',
      shape: 'tetrahedron',
      size: 0.32,
      parentId: null,
      tooltip: 'Autonomous sentinel patrol.',
      color: signals.palette.secondary,
      cluster: 'system',
      orbitLevel: 0,
      importance: 'secondary',
      systemId: null,
      motionProfile: 'sentinel-linked',
    };
  }, [selectedSentinelIndex, signals.palette.secondary]);
  const coreNode = useMemo(() => nodesById.get('core') || null, [nodesById]);
  const cameraControlActive = cameraMode === 'manual';
  const activeNode = hoveredNode || selectedNode || displayNode;
  const getNodeActivityState = useCallback((node: GraphNode): NodeActivityState => {
    if (!primaryLinkedSystem || linkedSystems.length <= 1) return 'neutral';
    const nodeSystemId = resolveLinkedSystemId(node.id, linkedSystems);
    if (!nodeSystemId) return 'neutral';
    return nodeSystemId === primaryLinkedSystem.id ? 'active' : 'muted';
  }, [linkedSystems, primaryLinkedSystem]);
  const highlightedNodeIds = useMemo(() => {
    const next = new Set<string>();
    if (hoveredNode?.id) next.add(hoveredNode.id);
    if (selectedNode?.id) next.add(selectedNode.id);
    return next;
  }, [hoveredNode?.id, selectedNode?.id]);
  const visibleNodes = useMemo(
    () => allNodes.filter((node) => shouldRenderNodeForZoomTier(node, zoomTier, highlightedNodeIds)),
    [allNodes, highlightedNodeIds, zoomTier],
  );
  const sceneBounds = useMemo(() => {
    if (!allNodes.length) {
      return { minX: -12, maxX: 12, minZ: -12, maxZ: 12 };
    }
    return allNodes.reduce((acc, node) => ({
      minX: Math.min(acc.minX, node.position[0]),
      maxX: Math.max(acc.maxX, node.position[0]),
      minZ: Math.min(acc.minZ, node.position[2]),
      maxZ: Math.max(acc.maxZ, node.position[2]),
    }), {
      minX: Number.POSITIVE_INFINITY,
      maxX: Number.NEGATIVE_INFINITY,
      minZ: Number.POSITIVE_INFINITY,
      maxZ: Number.NEGATIVE_INFINITY,
    });
  }, [allNodes]);

  const imperiumOrbit = useMemo(() => {
    const centerX = (sceneBounds.minX + sceneBounds.maxX) / 2;
    const centerZ = (sceneBounds.minZ + sceneBounds.maxZ) / 2;
    const extentX = Math.max(4, (sceneBounds.maxX - sceneBounds.minX) / 2);
    const extentZ = Math.max(4, (sceneBounds.maxZ - sceneBounds.minZ) / 2);
    const radius = Math.max(extentX, extentZ) + 6.5;
    return { center: [centerX, 0, centerZ] as [number, number, number], radius };
  }, [sceneBounds]);
  const visibleNodeIds = useMemo(() => new Set(visibleNodes.map((node) => node.id)), [visibleNodes]);
  const visibleEdges = useMemo(
    () => allEdges.filter((edge) => visibleNodeIds.has(edge.from) && visibleNodeIds.has(edge.to)),
    [allEdges, visibleNodeIds],
  );
  const selectedNodeCapabilities = useMemo(
    () => getNodeCapabilities(selectedNode, linkedSystems, Boolean(selectedNode?.assetOverride)),
    [linkedSystems, selectedNode],
  );
  const selectedNodeAssetProfile = useMemo(
    () => (selectedNode ? getNodeAssetProfile(selectedNode, familyAssetOverrides) : null),
    [familyAssetOverrides, selectedNode],
  );
  const selectedNodeAssetSource = useMemo(
    () => (selectedNode ? getNodeAssetSource(selectedNode, familyAssetOverrides) : 'fallback'),
    [familyAssetOverrides, selectedNode],
  );
  const selectedAssetStage = useMemo(() => selectedNodeAssetProfile?.appearance || null, [selectedNodeAssetProfile]);
  const selectedAssetStageTransform = useMemo(() => ({
    offset: selectedAssetStage?.offset || [0, 0, 0] as [number, number, number],
    rotation: selectedAssetStage?.rotation || [0, 0, 0] as [number, number, number],
    scale: selectedAssetStage?.scale ?? 1,
  }), [selectedAssetStage]);
  const sentinelEditProfile = useMemo(() => getSentinelAssetProfile(familyAssetOverrides), [familyAssetOverrides]);
  const sentinelAppearanceStage = useMemo<NodeAssetStage>(
    () => ({
      ...sentinelEditProfile.appearance,
      ...(sentinelAssetDraft || {}),
      rotation: (sentinelAssetDraft?.rotation || sentinelEditProfile.appearance.rotation || [0, 0, 0]) as [number, number, number],
      offset: (sentinelAssetDraft?.offset || sentinelEditProfile.appearance.offset || [0, 0, 0]) as [number, number, number],
      scale: sentinelAssetDraft?.scale ?? sentinelEditProfile.appearance.scale ?? 1,
    }),
    [sentinelAssetDraft, sentinelEditProfile.appearance],
  );
  const selectedAppearanceLabel = useMemo(() => {
    if (selectedSentinelIndex !== null) return formatAssetLabel(sentinelAppearanceStage);
    if (!selectedNode || !selectedNodeAssetProfile) return 'UNASSIGNED';
    if (selectedNode.assetOverride?.appearance?.src) return formatAssetLabel(selectedNodeAssetProfile.appearance);
    if (selectedNodeAssetSource === 'family' && selectedNodeAssetProfile.appearance.enabled) return formatAssetLabel(selectedNodeAssetProfile.appearance);
    return 'UNASSIGNED';
  }, [selectedNode, selectedNodeAssetProfile, selectedNodeAssetSource, selectedSentinelIndex, sentinelAppearanceStage]);
  const effectiveNodeAssetOverrides = useMemo(
    () =>
      Object.fromEntries(
        Object.keys({ ...nodeAssetOverrides, ...nodeAssetDrafts }).map((nodeId) => [
          nodeId,
          mergeGraphNodeAssetOverride(nodeAssetOverrides[nodeId], nodeAssetDrafts[nodeId]),
        ]).filter((entry): entry is [string, GraphNodeAssetOverride] => Boolean(entry[1])),
      ),
    [nodeAssetDrafts, nodeAssetOverrides],
  );
  const effectiveFamilyAssetOverrides = useMemo<NodeAssetFamilyOverrides>(() => {
    if (!sentinelAssetDraft) return familyAssetOverrides;
    const baseAppearance = familyAssetOverrides.sentinel?.appearance;
    if (!baseAppearance?.src) return familyAssetOverrides;
    return {
      ...familyAssetOverrides,
      sentinel: {
        ...familyAssetOverrides.sentinel,
        appearance: {
          ...(baseAppearance || {}),
          ...sentinelAssetDraft,
          enabled: baseAppearance?.enabled ?? true,
          src: baseAppearance.src,
        },
      },
    };
  }, [familyAssetOverrides, sentinelAssetDraft]);
  const editSessionDirty = useMemo(() => {
    if (!assetEditState.enabled || !editModeSessionBaseline) return false;
    return JSON.stringify(effectiveNodeAssetOverrides) !== JSON.stringify(editModeSessionBaseline.overrides)
      || JSON.stringify(effectiveFamilyAssetOverrides) !== JSON.stringify(editModeSessionBaseline.familyProfiles);
  }, [assetEditState.enabled, editModeSessionBaseline, effectiveFamilyAssetOverrides, effectiveNodeAssetOverrides]);
  const aggregateBadges = useMemo<AggregateBadge[]>(() => {
    if (zoomTier === 'detail') return [];

    const groups = new Map<string, { parent: GraphNode; cluster: Exclude<NodeCluster, 'linked-root'>; count: number }>();

    const findVisibleAncestor = (node: GraphNode) => {
      let cursor = node.parentId;
      while (cursor) {
        if (visibleNodeIds.has(cursor)) {
          return nodesById.get(cursor) || null;
        }
        cursor = nodesById.get(cursor)?.parentId || null;
      }
      return null;
    };

    allNodes.forEach((node) => {
      if (visibleNodeIds.has(node.id)) return;
      if (node.type !== 'file' && node.type !== 'folder') return;

      const parent = findVisibleAncestor(node);
      if (!parent) return;

      const cluster = inferAggregateCluster(node);
      const key = `${parent.id}:${cluster}`;
      const existing = groups.get(key);
      if (existing) {
        existing.count += 1;
        return;
      }
      groups.set(key, { parent, cluster, count: 1 });
    });

    const parentBuckets = new Map<string, AggregateBadge[]>();
    groups.forEach(({ parent, cluster, count }, key) => {
      const siblings = parentBuckets.get(parent.id) || [];
      const parentSystemId = resolveLinkedSystemId(parent.id, linkedSystems);
      const active = !parentSystemId || !primaryLinkedSystem || parentSystemId === primaryLinkedSystem.id;
      siblings.push({
        id: `aggregate-${key}`,
        parentId: parent.id,
        label: GRAPH_CLUSTER_CONFIG[cluster].label,
        count,
        color: GRAPH_CLUSTER_CONFIG[cluster].color,
        cluster,
        position: [...parent.position] as [number, number, number],
        active,
      });
      parentBuckets.set(parent.id, siblings);
    });

    const badges: AggregateBadge[] = [];
    parentBuckets.forEach((siblings, parentId) => {
      const parent = nodesById.get(parentId);
      if (!parent) return;
      const radius = zoomTier === 'overview' ? 2.4 : 1.92;
      siblings.forEach((badge, index) => {
        const angle = (-Math.PI / 2) + (index / Math.max(siblings.length, 1)) * Math.PI * 2;
        badges.push({
          ...badge,
          position: [
            parent.position[0] + Math.cos(angle) * radius,
            parent.position[1] + 0.02,
            parent.position[2] + Math.sin(angle) * radius,
          ],
        });
      });
    });

    return badges;
  }, [allNodes, linkedSystems, nodesById, primaryLinkedSystem, visibleNodeIds, zoomTier]);

  useEffect(() => {
    if (hoveredNode) {
      setDisplayNode(hoveredNode);
      return;
    }
    if (selectedNode) {
      setDisplayNode(selectedNode);
    }
  }, [hoveredNode, selectedNode]);

  useEffect(() => {
    if (selectedNodeId && !allNodes.some((node) => node.id === selectedNodeId)) {
      setSelectedNodeId(null);
      setDisplayNode(null);
    }
  }, [allNodes, selectedNodeId]);

  useEffect(() => {
    const openLinkModal = () => setUnlinkModal('link');
    window.addEventListener('continuity:open-link-modal', openLinkModal);
    return () => window.removeEventListener('continuity:open-link-modal', openLinkModal);
  }, []);

  const getEdgeStreamProfile = useCallback((from: GraphNode, to: GraphNode) => {
    if (zoomTier === 'overview') {
      return { streamParticles: 0, chromaticParticles: false, emphasis: 0.3 };
    }
    const hovered = hoveredNode ? hoveredNode.id === from.id || hoveredNode.id === to.id : false;
    const nodeFamilies = [from.type, to.type];
    const structural = nodeFamilies.some((family) => family === 'core' || family === 'engine' || family === 'edition' || family === 'module');
    const linkedActivity = from.cluster === 'linked-root'
      || to.cluster === 'linked-root'
      || (((from.orbitLevel ?? 0) >= 2) && Boolean(from.cluster))
      || (((to.orbitLevel ?? 0) >= 2) && Boolean(to.cluster));

    if (hovered) {
      return { streamParticles: qualityProfile.hoverStreamCount, chromaticParticles: true, emphasis: 1.06 };
    }
    if (structural) {
      return { streamParticles: qualityProfile.structuralStreamCount, chromaticParticles: true, emphasis: from.type === 'core' || to.type === 'core' ? 0.92 : 0.78 };
    }
    if (linkedSystems.length > 0 && linkedActivity) {
      return { streamParticles: Math.max(3, qualityProfile.structuralStreamCount - 2), chromaticParticles: true, emphasis: 0.68 };
    }
    return { streamParticles: 0, chromaticParticles: false, emphasis: 0.58 };
  }, [hoveredNode, linkedSystems.length, qualityProfile.hoverStreamCount, qualityProfile.structuralStreamCount, zoomTier]);

  // Watch events still handled locally for now


  // Pulse Vivo: Live Forensic Watcher
  React.useEffect(() => {
    const systemsToWatch = linkedSystems
      .filter((system) => system.accessMode === 'runtime')
      .map((system) => ({ id: system.id, rootPath: system.rootPath, name: system.name }));

    if (!systemsToWatch.length) return;

    const sources = systemsToWatch.map((system) => {
      console.log(`[PULSE_VIVO] Establishing link: ${system.name}`);
      const es = new EventSource(`/api/projects/watch?path=${encodeURIComponent(system.rootPath)}`);

      es.addEventListener('add', (e) => {
        try {
          const data = JSON.parse(e.data);
          console.log(`[PULSE_VIVO] ENTRY_ADDED:`, data.name);
          setLinkedSystems((prev) => prev.map((entry) => {
            if (entry.id !== system.id) return entry;
            if (entry.entries.find((item) => item.name === data.name)) return entry;
            return { ...entry, entries: [...entry.entries, { name: data.name, type: data.type }] };
          }));
          setLogs(prev => [{ id: Date.now(), msg: `[${tt(t, 'watch.add', 'CREATED')}] ${system.name}/${data.name}` }, ...prev].slice(0, 5));
        } catch(ex){}
      });

      es.addEventListener('unlink', (e) => {
        try {
          const data = JSON.parse(e.data);
          console.log(`[PULSE_VIVO] ENTRY_PURGED:`, data.name);
          setLinkedSystems((prev) => prev.map((entry) => entry.id === system.id ? { ...entry, entries: entry.entries.filter((item) => item.name !== data.name) } : entry));
          setLogs(prev => [{ id: Date.now(), msg: `[${tt(t, 'watch.unlink', 'DELETED')}] ${system.name}/${data.name}` }, ...prev].slice(0, 5));
        } catch(ex){}
      });

      return es;
    });

    return () => {
      sources.forEach((source) => source.close());
    };
  }, [linkedSystems.map((system) => `${system.id}:${system.rootPath}:${system.accessMode || 'runtime'}`).join('|'), setLinkedSystems, t]);


  const focusNode = useCallback((node: GraphNode | null) => {
    if (!node) return;
    setSelectedNodeId(node.id);
    setDisplayNode(node);
    const systemId = resolveLinkedSystemId(node.id, linkedSystems);
    if (systemId) {
      setActiveLinkedSystemId(systemId);
    }
    setCameraMode('focus');
  }, [linkedSystems, setActiveLinkedSystemId]);

  const resetView = useCallback(() => {
    setSelectedNodeId(null);
    setCameraMode('overview');
    const controls = controlsRef.current;
    const camera = controls?.object as THREE.OrthographicCamera | undefined;
    if (camera && 'zoom' in camera) {
      camera.zoom = signals.mode === 'INCIDENT' ? 26 : signals.mode === 'AUDIT' ? 28 : 30;
      camera.updateProjectionMatrix();
    }
    if (controls?.target) {
      controls.target.set(0, 0, 0);
      controls.update();
    }
  }, [signals.mode]);

  const focusLinkedRoot = useCallback(() => {
    const linkedRoot = primaryLinkedSystem
      ? allNodes.find((node) => node.id === `project-${primaryLinkedSystem.id}`) || null
      : allNodes.find((node) => node.cluster === 'linked-root' && node.type !== 'link-placeholder') || null;
    if (linkedRoot) {
      focusNode(linkedRoot);
      return;
    }
    setSelectedNodeId(null);
    setCameraMode('overview');
  }, [allNodes, focusNode, primaryLinkedSystem]);

  const refreshLinkedSystem = useCallback(async (system: LinkedSystem) => {
    if (!system.rootPath) return;
    try {
      const res = await fetch('/api/actions/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ projectPath: system.rootPath }),
      });
      const payload = await res.json().catch(() => ({}));
      if (!payload?.success) {
        throw new Error(payload?.error || 'SCAN_FAILED');
      }
      setLinkedSystems((prev) =>
        prev.map((entry) => (entry.id === system.id ? { ...entry, entries: payload.entries || [] } : entry)),
      );
      setLinkedSystemScanTimes((prev) => ({ ...prev, [system.id]: Date.now() }));
    } catch (error: any) {
      setToastMsg({ msg: 'SCAN_FAILED', detail: error?.message || system.name });
      setTimeout(() => setToastMsg(null), 2400);
    }
  }, [setLinkedSystems]);

  const refreshAllLinkedSystems = useCallback(async () => {
    if (!linkedSystems.length) return;
    setToastMsg({ msg: 'SCANNING_ALL_LINKED_SYSTEMS', detail: `${linkedSystems.length}` });
    try {
      await Promise.all(linkedSystems.map((system) => refreshLinkedSystem(system)));
      setToastMsg({ msg: 'SCAN_COMPLETE', detail: 'LINKED_SYSTEMS_REFRESHED' });
    } catch {
      setToastMsg({ msg: 'SCAN_FAILED', detail: 'ONE_OR_MORE_SYSTEMS' });
    }
    setTimeout(() => setToastMsg(null), 2400);
  }, [linkedSystems, refreshLinkedSystem]);

  const cycleActiveSystem = useCallback(() => {
    if (linkedSystems.length <= 1) return;
    const nextIndex = activeSystemIndex >= 0 ? (activeSystemIndex + 1) % linkedSystems.length : 0;
    const nextSystem = linkedSystems[nextIndex];
    setActiveLinkedSystemId(nextSystem.id);
    const nextRoot = allNodes.find((node) => node.id === `project-${nextSystem.id}`) || null;
    if (nextRoot) {
      focusNode(nextRoot);
    }
  }, [activeSystemIndex, allNodes, focusNode, linkedSystems, setActiveLinkedSystemId]);

  const focusNextDocument = useCallback(() => {
    const ecosystemDocNodes = primaryLinkedSystem
      ? allNodes.filter((node) => node.type === 'file' && resolveLinkedSystemId(node.id, linkedSystems) === primaryLinkedSystem.id)
      : [];
    const docNodes = ecosystemDocNodes.length > 0 ? ecosystemDocNodes : allNodes.filter((node) => node.type === 'file');
    if (!docNodes.length) return;
    const currentIndex = selectedNode ? docNodes.findIndex((node) => node.id === selectedNode.id) : -1;
    const nextNode = docNodes[(currentIndex + 1 + docNodes.length) % docNodes.length];
    focusNode(nextNode);
  }, [allNodes, focusNode, linkedSystems, primaryLinkedSystem, selectedNode]);

  const executeNodeAction = useCallback(async (node: GraphNode) => {
    if (!node.action) return;
    setToastMsg({ msg: tt(t, 'toast.executing', 'EXECUTING: {label}...', { label: node.label }) });
    try {
      await fetch(node.action);
      setToastMsg({ msg: tt(t, 'toast.success', 'SUCCESS: {label} COMPLETED.', { label: node.label }) });
    } catch {
      setToastMsg({ msg: tt(t, 'toast.failure', 'FAILURE: {label} FAILED.', { label: node.label }) });
    }
    setTimeout(() => setToastMsg(null), 3000);
  }, [t]);

  const openNodeDocument = useCallback(async (node: GraphNode) => {
    if (!node.filePath) return;
    if (openDoc?.filePath === node.filePath) {
      setOpenDoc(null);
      return;
    }

    const linkedSystem = getNodeSystem(node, linkedSystems);
    if (linkedSystem?.accessMode === 'structural') {
      setToastMsg({
        msg: tt(t, 'toast.structural_only', 'STRUCTURAL_ONLY_LINK'),
        detail: tt(t, 'toast.structural_only.detail', 'DIRECT_FILESYSTEM_READ_REQUIRES_RUNTIME_OR_HANDLE_ACCESS'),
      });
      setTimeout(() => setToastMsg(null), 3200);
      return;
    }

    try {
      if (linkedSystem?.accessMode === 'handle') {
        const relativeName = node.filePath.split('/').pop() || node.label;
        const data = await readHandleBackedFile(linkedSystem.id, relativeName);
        setOpenDoc({ fileName: data.fileName || node.label, filePath: node.filePath, content: data.content, truncated: data.truncated });
        return;
      }

      const res = await fetch('/api/actions/read', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filePath: node.filePath }),
      });
      const data = await res.json();
      if (data.success) {
        setOpenDoc({ fileName: data.fileName || node.label, filePath: node.filePath, content: data.content, truncated: data.truncated });
      } else {
        setToastMsg({ msg: tt(t, 'toast.failure', 'FAILURE: {label} FAILED.', { label: node.label }), detail: data.error || 'READ_ERROR' });
        setTimeout(() => setToastMsg(null), 3200);
      }
    } catch (error: any) {
      setToastMsg({
        msg: tt(t, 'toast.failure', 'FAILURE: {label} FAILED.', { label: node.label }),
        detail: error?.message || 'READ_ERROR',
      });
      setTimeout(() => setToastMsg(null), 3200);
    }
  }, [linkedSystems, openDoc?.filePath, t]);

  const openAssetPicker = useCallback((node: GraphNode, slot: AssetStageSlot) => {
    setSelectedNodeId(node.id);
    if (slot !== 'appearance') return;
    setPendingAssetTarget({ nodeId: node.id, slot });
    assetFileInputRef.current?.click();
  }, []);

  const openSentinelAssetPicker = useCallback(() => {
    setPendingAssetTarget({ family: 'sentinel', slot: 'appearance' });
    assetFileInputRef.current?.click();
  }, []);

  const patchNodeAssetSettings = useCallback((nodeId: string, slot: AssetStageSlot, settings: Partial<GraphNodeAssetOverride['appearance']>) => {
    setNodeAssetDrafts((prev) => {
      const next = { ...prev };
      delete next[nodeId];
      return next;
    });
    setNodeAssetOverrides((prev) => {
      const previous = prev[nodeId] || {};
      const previousStage = (previous[slot] || {}) as NonNullable<GraphNodeAssetOverride['appearance']>;
      return {
        ...prev,
        [nodeId]: {
          ...previous,
          [slot]: {
            ...previousStage,
            ...settings,
            enabled: previousStage?.enabled ?? true,
            src: previousStage?.src || '',
          },
        },
      };
    });

    void fetch('/api/node-assets', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nodeId, slot, settings }),
    })
      .then((response) => response.json())
      .then((payload) => {
        if (payload?.success && payload.overrides) {
          setNodeAssetOverrides(payload.overrides);
          setFamilyAssetOverrides(payload.familyProfiles || {});
          return;
        }
        throw new Error(payload?.error || 'ASSET_NODE_PATCH_ERROR');
      })
      .catch((error: any) => {
        setToastMsg({ msg: 'ASSET_EDIT_FAILURE', detail: error?.message || 'ASSET_NODE_PATCH_ERROR' });
        setTimeout(() => setToastMsg(null), 2600);
      });
  }, []);

  const draftNodeAssetOffset = useCallback((nodeId: string, offset: [number, number, number]) => {
    setNodeAssetDrafts((prev) => ({
      ...prev,
      [nodeId]: {
        ...(prev[nodeId] || {}),
        appearance: {
          ...((prev[nodeId]?.appearance || nodeAssetOverrides[nodeId]?.appearance || {}) as NonNullable<GraphNodeAssetOverride['appearance']>),
          offset,
        },
      },
    }));
  }, [nodeAssetOverrides]);

  const draftNodeAssetRotation = useCallback((nodeId: string, rotation: [number, number, number]) => {
    setNodeAssetDrafts((prev) => ({
      ...prev,
      [nodeId]: {
        ...(prev[nodeId] || {}),
        appearance: {
          ...((prev[nodeId]?.appearance || nodeAssetOverrides[nodeId]?.appearance || {}) as NonNullable<GraphNodeAssetOverride['appearance']>),
          rotation,
        },
      },
    }));
  }, [nodeAssetOverrides]);

  const draftNodeAssetScale = useCallback((nodeId: string, scale: number) => {
    setNodeAssetDrafts((prev) => ({
      ...prev,
      [nodeId]: {
        ...(prev[nodeId] || {}),
        appearance: {
          ...((prev[nodeId]?.appearance || nodeAssetOverrides[nodeId]?.appearance || {}) as NonNullable<GraphNodeAssetOverride['appearance']>),
          scale,
        },
      },
    }));
  }, [nodeAssetOverrides]);

  const commitNodeAssetOffset = useCallback((nodeId: string) => {
    const draft = nodeAssetDrafts[nodeId]?.appearance;
    if (!draft?.offset) return;
    patchNodeAssetSettings(nodeId, 'appearance', { offset: draft.offset });
  }, [nodeAssetDrafts, patchNodeAssetSettings]);

  const commitNodeAssetRotation = useCallback((nodeId: string) => {
    const draft = nodeAssetDrafts[nodeId]?.appearance;
    if (!draft?.rotation) return;
    patchNodeAssetSettings(nodeId, 'appearance', { rotation: draft.rotation });
  }, [nodeAssetDrafts, patchNodeAssetSettings]);

  const commitNodeAssetScale = useCallback((nodeId: string) => {
    const draft = nodeAssetDrafts[nodeId]?.appearance;
    if (typeof draft?.scale !== 'number') return;
    patchNodeAssetSettings(nodeId, 'appearance', { scale: draft.scale });
  }, [nodeAssetDrafts, patchNodeAssetSettings]);

  const revertSelectedAssetEdits = useCallback(() => {
    if (!selectedNode) return;
    setNodeAssetDrafts((prev) => {
      const next = { ...prev };
      delete next[selectedNode.id];
      return next;
    });
  }, [selectedNode]);

  const nudgeSelectedAssetOffset = useCallback((axis: 'x' | 'z', delta: number) => {
    if (!selectedNode || !selectedNodeAssetProfile) return;
    const slot: AssetStageSlot = 'appearance';
    const currentStage = selectedNodeAssetProfile.appearance;
    if (!currentStage?.src) return;
    const currentOffset = currentStage.offset || [0, 0, 0];
    const nextOffset: [number, number, number] = [...currentOffset] as [number, number, number];
    const index = axis === 'x' ? 0 : 2;
    nextOffset[index] += delta;
    patchNodeAssetSettings(selectedNode.id, slot, { offset: nextOffset });
  }, [patchNodeAssetSettings, selectedNode, selectedNodeAssetProfile]);

  const rotateSelectedAssetY = useCallback((deltaDegrees: number) => {
    if (!selectedNode || !selectedNodeAssetProfile) return;
    const slot: AssetStageSlot = 'appearance';
    const currentStage = selectedNodeAssetProfile.appearance;
    if (!currentStage?.src) return;
    const currentRotation = currentStage.rotation || [0, 0, 0];
    const nextRotation: [number, number, number] = [...currentRotation] as [number, number, number];
    nextRotation[1] += THREE.MathUtils.degToRad(deltaDegrees);
    patchNodeAssetSettings(selectedNode.id, slot, { rotation: nextRotation });
  }, [patchNodeAssetSettings, selectedNode, selectedNodeAssetProfile]);

  const scaleSelectedAsset = useCallback((delta: number) => {
    if (!selectedNode || !selectedNodeAssetProfile) return;
    const slot: AssetStageSlot = 'appearance';
    const currentStage = selectedNodeAssetProfile.appearance;
    if (!currentStage?.src) return;
    const nextScale = THREE.MathUtils.clamp((currentStage.scale ?? 1) + delta, 0.1, 8);
    patchNodeAssetSettings(selectedNode.id, slot, { scale: nextScale });
  }, [patchNodeAssetSettings, selectedNode, selectedNodeAssetProfile]);

  const patchSentinelAssetSettings = useCallback((settings: Partial<GraphNodeAssetOverride['appearance']>) => {
    setSentinelAssetDraft(null);
    void fetch('/api/node-assets', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ family: 'sentinel', slot: 'appearance', settings }),
    })
      .then((response) => response.json())
      .then((payload) => {
        if (payload?.success) {
          setNodeAssetOverrides(payload.overrides || {});
          setFamilyAssetOverrides(payload.familyProfiles || {});
          return;
        }
        throw new Error(payload?.error || 'SENTINEL_ASSET_PATCH_ERROR');
      })
      .catch((error: any) => {
        setToastMsg({ msg: 'SENTINEL_EDIT_FAILURE', detail: error?.message || 'SENTINEL_ASSET_PATCH_ERROR' });
        setTimeout(() => setToastMsg(null), 2600);
      });
  }, []);

  const rotateSentinelAssetY = useCallback((deltaDegrees: number) => {
    const currentRotation = sentinelAppearanceStage.rotation || [0, 0, 0];
    const nextRotation: [number, number, number] = [...currentRotation] as [number, number, number];
    nextRotation[1] += THREE.MathUtils.degToRad(deltaDegrees);
    patchSentinelAssetSettings({ rotation: nextRotation });
  }, [patchSentinelAssetSettings, sentinelAppearanceStage.rotation]);
  const rotateSentinelAssetX = useCallback((deltaDegrees: number) => {
    const currentRotation = sentinelAppearanceStage.rotation || [0, 0, 0];
    const nextRotation: [number, number, number] = [...currentRotation] as [number, number, number];
    nextRotation[0] += THREE.MathUtils.degToRad(deltaDegrees);
    patchSentinelAssetSettings({ rotation: nextRotation });
  }, [patchSentinelAssetSettings, sentinelAppearanceStage.rotation]);

  const scaleSentinelAsset = useCallback((delta: number) => {
    const nextScale = THREE.MathUtils.clamp((sentinelAppearanceStage.scale ?? 1) + delta, 0.1, 8);
    patchSentinelAssetSettings({ scale: nextScale });
  }, [patchSentinelAssetSettings, sentinelAppearanceStage.scale]);
  const draftSentinelAssetOffset = useCallback((offset: [number, number, number]) => {
    setSentinelAssetDraft((prev) => ({ ...(prev || {}), offset }));
  }, []);
  const commitSentinelAssetOffset = useCallback(() => {
    const offset = sentinelAssetDraft?.offset;
    if (!offset) return;
    patchSentinelAssetSettings({ offset });
  }, [patchSentinelAssetSettings, sentinelAssetDraft?.offset]);
  const draftSentinelAssetRotation = useCallback((rotation: [number, number, number]) => {
    setSentinelAssetDraft((prev) => ({ ...(prev || {}), rotation }));
  }, []);
  const commitSentinelAssetRotation = useCallback(() => {
    const rotation = sentinelAssetDraft?.rotation;
    if (!rotation) return;
    patchSentinelAssetSettings({ rotation });
  }, [patchSentinelAssetSettings, sentinelAssetDraft?.rotation]);
  const draftSentinelAssetScale = useCallback((scale: number) => {
    setSentinelAssetDraft((prev) => ({ ...(prev || {}), scale }));
  }, []);
  const commitSentinelAssetScale = useCallback(() => {
    const scale = sentinelAssetDraft?.scale;
    if (typeof scale !== 'number') return;
    patchSentinelAssetSettings({ scale });
  }, [patchSentinelAssetSettings, sentinelAssetDraft?.scale]);

  const clearSelectedNodeAssetOverride = useCallback(() => {
    if (!selectedNode) return;
    void fetch('/api/node-assets', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nodeId: selectedNode.id }),
    })
      .then((response) => response.json())
      .then((payload) => {
        if (payload?.success && payload.overrides) {
          setNodeAssetOverrides(payload.overrides);
          setFamilyAssetOverrides(payload.familyProfiles || {});
          setToastMsg({ msg: `${selectedNode.label} // GLB RESET` });
          setTimeout(() => setToastMsg(null), 2400);
        } else {
          setToastMsg({ msg: tt(t, 'toast.failure', 'FAILURE: {label} FAILED.', { label: selectedNode.label }), detail: payload?.error || 'ASSET_CLEAR_ERROR' });
          setTimeout(() => setToastMsg(null), 3200);
        }
      })
      .catch((error: any) => {
        setToastMsg({ msg: tt(t, 'toast.failure', 'FAILURE: {label} FAILED.', { label: selectedNode.label }), detail: error?.message || 'ASSET_CLEAR_ERROR' });
        setTimeout(() => setToastMsg(null), 3200);
      });
  }, [selectedNode, t]);

  const handleAssetInputChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    const target = pendingAssetTarget;
    if (!file || !target) {
      event.target.value = '';
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    if ('nodeId' in target && target.nodeId) {
      formData.append('nodeId', target.nodeId);
    }
    if ('family' in target && target.family) {
      formData.append('family', target.family);
    }
    formData.append('slot', target.slot);
    formData.append('label', file.name);

    void fetch('/api/node-assets', {
      method: 'POST',
      body: formData,
    })
      .then((response) => response.json())
      .then((payload) => {
        if (payload?.success && payload.overrides) {
          setNodeAssetOverrides(payload.overrides);
          setFamilyAssetOverrides(payload.familyProfiles || {});
          const nodeLabel = 'nodeId' in target && target.nodeId
            ? (nodesById.get(target.nodeId)?.label || target.nodeId)
            : (target.family || 'SENTINEL').toUpperCase();
          setToastMsg({ msg: `${nodeLabel} // GLB ${target.slot.toUpperCase()} LINKED` });
          setTimeout(() => setToastMsg(null), 2600);
        } else {
          setToastMsg({ msg: 'GLB_LINK_FAILURE', detail: payload?.error || 'ASSET_UPLOAD_ERROR' });
          setTimeout(() => setToastMsg(null), 3200);
        }
      })
      .catch((error: any) => {
        setToastMsg({ msg: 'GLB_LINK_FAILURE', detail: error?.message || 'ASSET_UPLOAD_ERROR' });
        setTimeout(() => setToastMsg(null), 3200);
      })
      .finally(() => {
        setPendingAssetTarget(null);
        event.target.value = '';
      });
  }, [nodesById, pendingAssetTarget]);

  const processCanonicalAssets = useCallback(() => {
    if (isProcessingCanonicalAssets) return;
    setIsProcessingCanonicalAssets(true);

    void fetch('/api/node-assets', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'process-canonical-assets' }),
    })
      .then((response) => response.json())
      .then((payload) => {
        if (payload?.success) {
          const processedTargets: string[] = Array.isArray(payload.processedTargets) ? payload.processedTargets : [];
          const missingTargets: string[] = Array.isArray(payload.missingTargets) ? payload.missingTargets : [];
          setNodeAssetOverrides(payload.overrides || {});
          setFamilyAssetOverrides(payload.familyProfiles || {});

          const processedSummary = processedTargets.length
            ? processedTargets.map((target) => target.replace(/-/g, '_').toUpperCase()).join(' // ')
            : 'NO_CANONICAL_TARGETS_FOUND';
          const missingSummary = missingTargets.length
            ? `MISSING // ${missingTargets.map((target) => target.replace(/-/g, '_').toUpperCase()).join(' // ')}`
            : processedSummary;

          setToastMsg({
            msg: `3D_ASSETS // ${processedTargets.length} PROCESSED`,
            detail: missingSummary,
          });
          setTimeout(() => setToastMsg(null), 3600);
        } else {
          setToastMsg({ msg: '3D_ASSET_PROCESS_FAILURE', detail: payload?.error || 'CANONICAL_ASSET_PROCESS_ERROR' });
          setTimeout(() => setToastMsg(null), 3200);
        }
      })
      .catch((error: any) => {
        setToastMsg({ msg: '3D_ASSET_PROCESS_FAILURE', detail: error?.message || 'CANONICAL_ASSET_PROCESS_ERROR' });
        setTimeout(() => setToastMsg(null), 3200);
      })
      .finally(() => {
        setIsProcessingCanonicalAssets(false);
      });
  }, [isProcessingCanonicalAssets]);

  const submitChatPrompt = useCallback(async () => {
    const prompt = chatPrompt.trim();
    if (!prompt || chatBusy) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: prompt,
    };
    setChatMessages((prev) => [...prev, userMessage]);
    setChatPrompt('');
    setChatBusy(true);

    try {
      const response = await fetch('/api/chat/bridge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      });
      const payload = await response.json().catch(() => ({}));
      if (!payload?.success) {
        throw new Error(payload?.error || 'CHAT_BRIDGE_FAILURE');
      }
      setChatMessages((prev) => [
        ...prev,
        {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: String(payload.reply || 'NO_RESPONSE'),
        },
      ]);
    } catch (error: any) {
      setChatMessages((prev) => [
        ...prev,
        {
          id: `assistant-error-${Date.now()}`,
          role: 'assistant',
          content: `LINK FAILURE // ${error?.message || 'CHAT_BRIDGE_FAILURE'}`,
        },
      ]);
    } finally {
      setChatBusy(false);
    }
  }, [chatBusy, chatPrompt]);

  const handleNodeClick = async (node: GraphNode) => {
    setSelectedSentinelIndex(null);
    const capabilities = getNodeCapabilities(node, linkedSystems, Boolean(node.assetOverride));
    if (capabilities.kind === 'access') {
      setUnlinkModal('link');
      return;
    }
    focusNode(node);
    if (capabilities.canExecute && node.action) {
      await executeNodeAction(node);
      return;
    }
    if (capabilities.canOpenDocument || capabilities.blockReason) {
      await openNodeDocument(node);
    }
  };

  const beginCameraControl = () => {
    setCameraMode('manual');
  };

  const endCameraControl = () => {};

  const docFormat = openDoc ? inferDocumentFormat(openDoc.fileName) : 'text';
  const docFormatLabel = docFormat === 'markdown'
    ? tt(t, 'viewer.format.markdown', 'MARKDOWN_SURFACE')
    : docFormat === 'json'
    ? tt(t, 'viewer.format.json', 'JSON_STATE')
    : docFormat === 'source'
    ? tt(t, 'viewer.format.source', 'SOURCE_STREAM')
    : tt(t, 'viewer.format.text', 'TEXT_STREAM');
  const docMatchCount = openDoc ? countQueryMatches(openDoc.content, deferredDocQuery) : 0;
  const topReplay = merkleReplay.slice(0, 5);
  const resolvedEditModeSecret = useMemo(
    () => String.fromCharCode(...EDIT_MODE_SECRET_CODES),
    [],
  );
  const inspectorNode = selectedNode || sentinelInspectorNode || null;
  const inspectorCapabilities = selectedNode
    ? selectedNodeCapabilities
    : ({
        kind: 'passive',
        accessMode: 'none',
        system: null,
        canExecute: false,
        canOpenDocument: false,
        canAssignAsset: true,
        canClearAsset: false,
        canFocus: false,
        blockReason: null,
      } satisfies NodeCapabilities);
  const assetEditorVisible = Boolean(inspectorNode);
  const dockBottom = isPhone ? 12 : isTablet ? 16 : 22;
  const dockExpanded = assetEditState.enabled && Boolean(inspectorNode);
  const dockReferenceNode = inspectorNode || displayNode;
  const dockAccent = dockReferenceNode?.color || signals.palette.accent;
  const dockAccessMode: NodeAccessMode = inspectorNode ? (inspectorCapabilities.accessMode || 'none') : (primaryLinkedSystem?.accessMode || 'none');
  const dockAccessLabel = dockAccessMode === 'none'
    ? 'ROOT'
    : tt(t, `hud.access.${dockAccessMode}`, dockAccessMode.toUpperCase());
  const dockTrustText = translateTrust(signals.chainTrustLabel, t);
  const dockTitle = dockReferenceNode?.label || primaryLinkedSystem?.name || tt(t, 'common.idle', 'IDLE');
  const dockTitleColor = dockReferenceNode?.color || signals.palette.emphasis;
  const dockDescriptor = inspectorNode
    ? inspectorNode.tooltip
    : dockReferenceNode?.tooltip || (
        primaryLinkedSystem
          ? `${tt(t, 'core.active_system', 'SYSTEM')}: ${primaryLinkedSystem.name}`
          : modeReasonText
      );
  const formatScanAge = useCallback((timestamp?: number) => {
    if (!timestamp) return 'NEVER';
    const deltaMs = Date.now() - timestamp;
    const seconds = Math.max(0, Math.floor(deltaMs / 1000));
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h`;
    const days = Math.floor(hours / 24);
    return `${days}d`;
  }, []);
  const dockSystemLabel = selectedSentinelIndex !== null
    ? 'SENTINEL_FAMILY'
    : inspectorCapabilities.system?.name || primaryLinkedSystem?.name || 'ROOT';
  const dockMetaLabel = inspectorNode
    ? `${tt(t, 'dock.mod_identifier', 'NODE_INSPECTOR')} // ${tt(t, `graph.type.${inspectorNode.type}`, inspectorNode.type.toUpperCase())}`
    : `TACTICAL_DOCK // ${cameraModeLabel}`;
  const dockStatusItems = inspectorNode
    ? [
        { id: 'type', label: tt(t, 'dock.mod_identifier', 'NODE'), value: tt(t, `graph.type.${inspectorNode.type}`, inspectorNode.type.toUpperCase()) },
        { id: 'status', label: tt(t, 'common.status', 'STATUS'), value: modeLabelText },
        { id: 'system', label: tt(t, 'core.active_system', 'SYSTEM'), value: dockSystemLabel },
        { id: 'access', label: tt(t, 'common.mode', 'MODE'), value: dockAccessLabel },
      ]
    : [
        { id: 'mode', label: tt(t, 'common.mode', 'MODE'), value: cameraModeLabel },
        { id: 'status', label: tt(t, 'common.status', 'STATUS'), value: modeLabelText },
        { id: 'system', label: tt(t, 'core.active_system', 'SYSTEM'), value: dockSystemLabel },
        { id: 'trust', label: tt(t, 'common.trust', 'TRUST'), value: dockTrustText },
      ];
  const dockCommandItems: DockCommandItem[] = [
    {
      id: 'edit-mode',
      label: assetEditState.enabled ? 'EXIT_EDIT_MODE' : 'EDIT_MODE',
      onClick: () => setAssetEditState((prev) => ({ ...prev, enabled: !prev.enabled })),
      active: assetEditState.enabled,
      tone: 'warning' as const,
    },
    {
      id: 'process-3d-assets',
      label: isProcessingCanonicalAssets
        ? tt(t, 'dock.process_3d_assets.processing', 'PROCESSING_3D_ASSETS')
        : tt(t, 'dock.process_3d_assets', 'PROCESS_3D_ASSETS'),
      onClick: processCanonicalAssets,
      active: isProcessingCanonicalAssets,
      tone: 'accent' as const,
    },
    { id: 'reset', label: tt(t, 'nav.reset_view', 'RESET_VIEW'), onClick: resetView },
    { id: 'focus-core', label: tt(t, 'nav.focus_core', 'FOCUS_CORE'), onClick: () => focusNode(coreNode) },
    { id: 'focus-linked', label: tt(t, 'nav.focus_linked', 'FOCUS_ACTIVE_SYSTEM'), onClick: focusLinkedRoot },
    { id: 'next-doc', label: tt(t, 'nav.next_doc', 'NEXT_DOC'), onClick: focusNextDocument },
    { id: 'cycle', label: tt(t, 'nav.cycle_systems', 'CYCLE_SYSTEMS'), onClick: cycleActiveSystem, visible: linkedSystems.length > 1 },
  ].filter((item) => item.visible !== false);
  const handleEditModeToggle = useCallback(() => {
    if (assetEditState.enabled) {
      setNodeAssetDrafts({});
      setSentinelAssetDraft(null);
      setAssetEditState({ enabled: false });
      return;
    }
    if (editModeAuthorized) {
      setEditModeSessionBaseline({
        overrides: JSON.parse(JSON.stringify(nodeAssetOverrides)),
        familyProfiles: JSON.parse(JSON.stringify(familyAssetOverrides)),
      });
      setAssetEditState({ enabled: true });
      return;
    }
    setEditModePassword('');
    setEditModePromptOpen(true);
  }, [assetEditState.enabled, editModeAuthorized, familyAssetOverrides, nodeAssetOverrides]);
  const submitEditModePassword = useCallback(() => {
    if (editModePassword.trim() !== resolvedEditModeSecret) {
      setToastMsg({ msg: 'EDIT_MODE_LOCKED', detail: 'INVALID_ACCESS_KEY' });
      setTimeout(() => setToastMsg(null), 2200);
      return;
    }
    setEditModeAuthorized(true);
    setEditModeSessionBaseline({
      overrides: JSON.parse(JSON.stringify(nodeAssetOverrides)),
      familyProfiles: JSON.parse(JSON.stringify(familyAssetOverrides)),
    });
    setAssetEditState({ enabled: true });
    setEditModePromptOpen(false);
    setEditModePassword('');
  }, [editModePassword, familyAssetOverrides, nodeAssetOverrides, resolvedEditModeSecret]);
  const dockContextMaxHeight = assetEditorVisible
    ? (isPhone ? '42vh' : '38vh')
    : undefined;
  const dockCommandButtonStyle = (item: DockCommandItem): React.CSSProperties => {
    const borderColor = item.active
      ? dockAccent
      : item.tone === 'warning'
      ? signals.palette.warning
      : signals.palette.border;
    const background = item.active
      ? 'rgba(255,255,255,0.1)'
      : item.tone === 'accent'
      ? 'rgba(255,255,255,0.05)'
      : 'rgba(255,255,255,0.025)';
    return {
      padding: isPhone ? '8px 10px' : '9px 14px',
      minHeight: isPhone ? '36px' : '38px',
      fontSize: isPhone ? '0.42rem' : '0.46rem',
      letterSpacing: isPhone ? '1.5px' : '1.9px',
      borderColor,
      background,
      boxShadow: item.active ? `0 0 0 1px ${dockAccent}26 inset, 0 0 18px ${dockAccent}18` : 'none',
      color: item.active ? signals.palette.emphasis : 'rgba(255,255,255,0.86)',
      gap: '0',
      justifyContent: 'center',
      borderRadius: '0',
      flex: isPhone ? '1 1 132px' : '1 1 auto',
      fontFamily: 'var(--font-mono)',
    };
  };
  const persistEditModeSession = useCallback(async (nextOverrides: Record<string, GraphNodeAssetOverride>, nextFamilyProfiles: NodeAssetFamilyOverrides) => {
    const response = await fetch('/api/node-assets', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        overrides: nextOverrides,
        familyProfiles: nextFamilyProfiles,
      }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!payload?.success) {
      throw new Error(payload?.error || 'EDIT_MODE_SESSION_SYNC_ERROR');
    }
    setNodeAssetOverrides(payload.overrides || {});
    setFamilyAssetOverrides(payload.familyProfiles || {});
    setNodeAssetDrafts({});
    setSentinelAssetDraft(null);
    return payload;
  }, []);
  const saveEditModeSession = useCallback(async () => {
    try {
      const payload = await persistEditModeSession(effectiveNodeAssetOverrides, effectiveFamilyAssetOverrides);
      setEditModeSessionBaseline({
        overrides: JSON.parse(JSON.stringify(payload.overrides || {})),
        familyProfiles: JSON.parse(JSON.stringify(payload.familyProfiles || {})),
      });
      setToastMsg({ msg: 'EDIT_MODE_SESSION_SAVED', detail: 'LAYOUT_AND_ASSET_TRANSFORMS_COMMITTED' });
      setTimeout(() => setToastMsg(null), 2400);
    } catch (error: any) {
      setToastMsg({ msg: 'EDIT_MODE_SAVE_FAILURE', detail: error?.message || 'EDIT_MODE_SESSION_SYNC_ERROR' });
      setTimeout(() => setToastMsg(null), 2800);
    }
  }, [effectiveFamilyAssetOverrides, effectiveNodeAssetOverrides, persistEditModeSession]);
  const revertEditModeSession = useCallback(async () => {
    if (!editModeSessionBaseline) return;
    try {
      const payload = await persistEditModeSession(editModeSessionBaseline.overrides, editModeSessionBaseline.familyProfiles);
      setEditModeSessionBaseline({
        overrides: JSON.parse(JSON.stringify(payload.overrides || {})),
        familyProfiles: JSON.parse(JSON.stringify(payload.familyProfiles || {})),
      });
      setToastMsg({ msg: 'EDIT_MODE_SESSION_REVERTED', detail: 'SESSION_ROLLED_BACK_TO_ENTRY_STATE' });
      setTimeout(() => setToastMsg(null), 2400);
    } catch (error: any) {
      setToastMsg({ msg: 'EDIT_MODE_REVERT_FAILURE', detail: error?.message || 'EDIT_MODE_SESSION_SYNC_ERROR' });
      setTimeout(() => setToastMsg(null), 2800);
    }
  }, [editModeSessionBaseline, persistEditModeSession]);
  const renderDockCommandStrip = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0', alignItems: 'stretch', border: `1px solid ${signals.palette.border}`, background: 'rgba(255,255,255,0.015)' }}>
        {dockCommandItems.map((item, index) => (
          <button
            key={item.id}
            onClick={item.onClick}
            className="btn-nexus"
            style={{
              ...dockCommandButtonStyle(item),
              borderWidth: '0',
              borderRight: index < dockCommandItems.length - 1 ? `1px solid ${signals.palette.border}` : '0',
            }}
          >
            {item.label}
          </button>
        ))}
      </div>
    </div>
  );
  const renderDockContextActions = () => {
    if (!inspectorNode) return null;

    const isImperium = inspectorNode.id === 'imperium';
    const imperiumSystems = isImperium ? linkedSystems : [];

    const actionItems: DockCommandItem[] = [
      ...(inspectorCapabilities.kind !== 'access' && inspectorCapabilities.canFocus
        ? [{ id: 'focus', label: tt(t, 'nav.focus_core', 'FOCUS'), onClick: () => focusNode(inspectorNode) }]
        : []),
      ...(inspectorCapabilities.kind === 'access'
        ? [{ id: 'link', label: tt(t, 'graph.link.label', 'LINK PROJECT'), onClick: () => setUnlinkModal('link'), tone: 'accent' as const }]
        : []),
      ...(inspectorCapabilities.canExecute
        ? [{ id: 'execute', label: tt(t, 'common.execute', 'EXECUTE'), onClick: () => { void executeNodeAction(inspectorNode); }, tone: 'accent' as const }]
        : []),
      ...(inspectorCapabilities.canOpenDocument || inspectorCapabilities.blockReason
        ? [{
            id: 'open',
            label: openDoc?.filePath === inspectorNode.filePath ? tt(t, 'common.close', 'CLOSE') : tt(t, 'common.open', 'OPEN'),
            onClick: () => { void openNodeDocument(inspectorNode); },
          }]
        : []),
      ...(inspectorCapabilities.system
        ? [{ id: 'unlink', label: tt(t, 'hud.unlink_system', 'UNLINK'), onClick: () => setUnlinkModal('unlink'), tone: 'warning' as const }]
        : []),
  ];

    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {isImperium && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', padding: '10px', border: `1px solid ${signals.palette.border}`, background: 'rgba(8,12,22,0.6)' }}>
            <div style={{ fontSize: '0.46rem', letterSpacing: '2px', color: 'rgba(255,255,255,0.52)' }}>IMPERIUM_CONSOLE</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              <button
                onClick={() => void refreshAllLinkedSystems()}
                className="btn-nexus"
                style={dockCommandButtonStyle({ id: 'scan-all', label: 'SCAN_ALL', onClick: () => {} })}
              >
                SCAN_ALL
              </button>
              <button
                onClick={() => { void fetch('/api/actions/crystallize'); }}
                className="btn-nexus"
                style={dockCommandButtonStyle({ id: 'crystallize', label: 'CRYSTALLIZE_CORE', onClick: () => {} })}
              >
                CRYSTALLIZE_CORE
              </button>
              <button
                onClick={() => { void fetch('/api/actions/audit'); }}
                className="btn-nexus"
                style={dockCommandButtonStyle({ id: 'audit', label: 'AUDIT_CORE', onClick: () => {} })}
              >
                AUDIT_CORE
              </button>
              <button
                onClick={() => { void fetch('/api/actions/seal'); }}
                className="btn-nexus"
                style={dockCommandButtonStyle({ id: 'seal', label: 'SEAL_CORE', onClick: () => {} })}
              >
                SEAL_CORE
              </button>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {imperiumSystems.length === 0 && (
                <div style={{ fontSize: '0.5rem', color: 'rgba(255,255,255,0.55)' }}>NO_LINKED_SYSTEMS</div>
              )}
              {imperiumSystems.map((system) => (
                <div key={system.id} style={{ display: 'flex', flexDirection: 'column', gap: '6px', padding: '6px 8px', border: `1px solid ${signals.palette.border}`, background: 'rgba(10,16,26,0.72)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', gap: '12px', fontSize: '0.48rem', letterSpacing: '1.6px', color: 'rgba(255,255,255,0.72)' }}>
                    <span>{system.name}</span>
                    <span>{system.accessMode ? system.accessMode.toUpperCase() : 'RUNTIME'}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', gap: '12px', fontSize: '0.44rem', letterSpacing: '1.4px', color: 'rgba(255,255,255,0.5)' }}>
                    <span>{`ENTRIES ${system.entries.length}`}</span>
                    <span>{`LAST_SCAN ${formatScanAge(linkedSystemScanTimes[system.id])}`}</span>
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    <button
                      onClick={() => {
                        setActiveLinkedSystemId(system.id);
                        const node = allNodes.find((n) => n.id === `project-${system.id}`) || null;
                        if (node) focusNode(node);
                      }}
                      className="btn-nexus"
                      style={dockCommandButtonStyle({ id: `focus-${system.id}`, label: 'FOCUS', onClick: () => {} })}
                    >
                      {`FOCUS`}
                    </button>
                    <button
                      onClick={() => setActiveLinkedSystemId(system.id)}
                      className="btn-nexus"
                      style={dockCommandButtonStyle({ id: `active-${system.id}`, label: 'SET_ACTIVE', onClick: () => {} })}
                    >
                      {`SET_ACTIVE`}
                    </button>
                    <button
                      onClick={() => void refreshLinkedSystem(system)}
                      className="btn-nexus"
                      style={dockCommandButtonStyle({ id: `scan-${system.id}`, label: 'SCAN', onClick: () => {} })}
                    >
                      {`SCAN`}
                    </button>
                    <button
                      onClick={() => {
                        setActiveLinkedSystemId(system.id);
                        setUnlinkModal('unlink');
                      }}
                      className="btn-nexus"
                      style={dockCommandButtonStyle({ id: `unlink-${system.id}`, label: 'UNLINK', onClick: () => {} })}
                    >
                      {`UNLINK`}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '8px' }}>
          {actionItems.map((item) => (
            <button
              key={item.id}
              onClick={item.onClick}
              className="btn-nexus"
              style={dockCommandButtonStyle(item)}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>
    );
  };
  const sentinelAnchor = (primaryLinkedSystem && nodesById.get(`project-${primaryLinkedSystem.id}`)?.position) || nodesById.get('core')?.position || [0, 0, 0];

  return (
    <div style={{ width: '100%', height: '100%', position: 'absolute', inset: 0, zIndex: 1, background: 'transparent', overflow: 'hidden' }}>
      <SceneErrorBoundary dictionary={t}>
      <Canvas
        style={{ position: 'absolute', inset: 0, zIndex: 0, background: 'transparent' }}
        orthographic
        dpr={qualityProfile.dpr}
        gl={{ antialias: true, alpha: true, powerPreference: 'high-performance', stencil: false }}
        camera={{ position: [0, 35, 0.001], zoom: 30, near: 0.1, far: 200 }}
      >
        <CanvasBackgroundSync background={signals.palette.sceneBg} fog={signals.palette.fog} />
        <SceneRig signals={signals} reducedMotion={reducedMotion} cameraMode={cameraMode} focusedNode={selectedNode} controlsRef={controlsRef} sceneBounds={sceneBounds} />
        <ZoomTierTracker onZoomTierChange={setZoomTier} />
        <ambientLight intensity={0.7} color="#f8fafc" />
        <directionalLight intensity={0.38} color={signals.palette.emphasis} position={[12, 28, 6]} />
        <directionalLight intensity={0.24} color={signals.palette.secondary} position={[-10, 22, -8]} />

        {/* TARGET ACQUISITION RETICLE & DATA BRIDGE */}
        {hoveredNode && (
          <group position={hoveredNode.position as any}>
             <mesh rotation={[0, 0, Math.PI / 4]}>
                <ringGeometry args={[1.2, 1.25, 4]} />
                <meshBasicMaterial color={hoveredNode.color} transparent opacity={0.4} />
             </mesh>
             <mesh rotation={[0, 0, 0]}>
                <ringGeometry args={[1.4, 1.42, 32]} />
                <meshBasicMaterial color="#ffffff" transparent opacity={0.1} />
             </mesh>
             
             {/* Data Bridge Beam to HUD */}
              <ConnectionBeam 
                start={[0, 0, 0]} 
                end={[15, 10, -5]} // Fixed camera-relative pos for the telemetry wing
                color={hoveredNode.color || signals.palette.secondary}
                streamParticles={qualityProfile.hoverStreamCount}
                chromaticParticles
                emphasis={1.12}
              />
           </group>
        )}

        {[...Array(qualityProfile.droneCount)].map((_, i) => (
          <SentinelDrone
            key={i}
            index={i}
            drift={drift}
            anchor={sentinelAnchor as [number, number, number]}
            color={signals.palette.secondary}
            familyAssetOverrides={familyAssetOverrides}
            assetStage={sentinelAppearanceStage}
            editMode={assetEditState.enabled}
            isSelected={selectedSentinelIndex === i}
            onSelectForEdit={(index) => {
              setSelectedNodeId(null);
              setSelectedSentinelIndex(index);
            }}
            onOpenAssetPicker={openSentinelAssetPicker}
            onDraftAssetOffset={draftSentinelAssetOffset}
            onCommitAssetOffset={commitSentinelAssetOffset}
            onDraftAssetRotation={draftSentinelAssetRotation}
            onCommitAssetRotation={commitSentinelAssetRotation}
            onDraftAssetScale={draftSentinelAssetScale}
            onCommitAssetScale={commitSentinelAssetScale}
          />
        ))}

        {visibleEdges.map((edge, i) => {
          const from = nodesById.get(edge.from);
          const to = nodesById.get(edge.to);
          if (!from || !to) return null;
          const streamProfile = getEdgeStreamProfile(from, to);
          return (
            <ConnectionBeam
              key={`edge-${i}`}
              start={from.position}
              end={to.position}
              color={from.color || to.color || signals.palette.secondary}
              streamParticles={streamProfile.streamParticles}
              chromaticParticles={streamProfile.chromaticParticles}
              emphasis={streamProfile.emphasis}
            />
          );
        })}

        {visibleNodes.map((node) => (
            <SystemNode
              key={node.id}
              node={node}
              isPulsing={pulsingNodes.has(node.id)}
              isSelected={selectedNodeId === node.id}
            eta={physics.eta}
            drift={drift}
            signals={signals}
            zoomTier={zoomTier}
              reducedMotion={reducedMotion}
              familyAssetOverrides={familyAssetOverrides}
              activityState={getNodeActivityState(node)}
              editMode={assetEditState.enabled}
              onHover={setHoveredNode}
              onUnhover={() => setHoveredNode(null)}
              onClick={handleNodeClick}
              onOpenAssetPicker={openAssetPicker}
              onSelectForEdit={(target) => {
                setSelectedSentinelIndex(null);
                setSelectedNodeId(target.id);
              }}
              onDraftAssetOffset={draftNodeAssetOffset}
              onCommitAssetOffset={commitNodeAssetOffset}
              onDraftAssetRotation={draftNodeAssetRotation}
              onCommitAssetRotation={commitNodeAssetRotation}
              onDraftAssetScale={draftNodeAssetScale}
              onCommitAssetScale={commitNodeAssetScale}
              imperiumOrbit={imperiumOrbit}
            />
        ))}

        {zoomTier !== 'overview' && aggregateBadges.map((badge) => (
          <AggregateClusterBadge key={badge.id} badge={badge} dictionary={t} />
        ))}

        <OrbitControls 
          ref={controlsRef}
          makeDefault
          enableDamping 
          dampingFactor={0.12} 
          enableRotate={false}
          panSpeed={0.72}
          zoomSpeed={0.82}
          enablePan
          enableZoom
          screenSpacePanning
          autoRotate={false}
          minZoom={0.001}
          mouseButtons={{
            LEFT: MOUSE.PAN,
            MIDDLE: MOUSE.PAN,
            RIGHT: MOUSE.PAN,
          }}
          onStart={beginCameraControl}
          onEnd={endCameraControl}
        />

      </Canvas>
      </SceneErrorBoundary>

      <input
        ref={assetFileInputRef}
        type="file"
        accept=".glb,.gltf,model/gltf-binary,model/gltf+json"
        onChange={handleAssetInputChange}
        style={{ display: 'none' }}
      />

      <WaveMonitor
        drift={drift}
        eta={physics.eta}
        merkle={merkle}
        logs={logs}
        chainEvents={chainEvents}
        signals={signals}
        sessionStart={sessionStart}
        dictionary={t}
        physics={physics}
        linkedSystems={linkedSystems}
        primaryLinkedSystem={primaryLinkedSystem}
        activeVectorText={activeVectorText}
        topReplay={topReplay}
        qualityTier={qualityTier}
        audioArmed={audioArmed}
        reducedMotion={reducedMotion}
        open={isRightRailOpen}
        onToggle={() => setIsRightRailOpen((current) => !current)}
      />

      <div
        style={{
          position: 'absolute',
          top: isPhone ? 104 : isTablet ? 132 : 148,
          right: 0,
          bottom: isPhone ? 14 : 18,
          width: (isPhone ? 280 : isTablet ? 320 : 360) + (isPhone ? 34 : 38),
          zIndex: 510,
          pointerEvents: 'none',
        }}
      >
        <button
          onClick={() => setIsChatOpen((current) => !current)}
          className="btn-nexus"
          style={{
            position: 'absolute',
            right: (isPhone ? 280 : isTablet ? 320 : 360) - 1,
            top: 'calc(50% - 88px)',
            transform: 'translateY(-50%)',
            pointerEvents: 'auto',
            writingMode: 'vertical-lr',
            padding: isPhone ? '10px 7px' : '12px 8px',
            fontSize: '0.46rem',
            letterSpacing: '3px',
            minWidth: `${(isPhone ? 34 : 38) - 6}px`,
            borderTopLeftRadius: 0,
            borderBottomLeftRadius: 0,
            borderTopRightRadius: '10px',
            borderBottomRightRadius: '10px',
            borderColor: signals.palette.secondary,
            boxShadow: `0 12px 26px rgba(0,0,0,0.2), 0 0 16px ${signals.palette.secondary}12`,
          }}
        >
          {isChatOpen ? 'HIDE_CHAT' : 'CHAT'}
        </button>

        <div
          className="hide-scrollbar"
          style={{
            position: 'absolute',
            top: 0,
            right: 0,
            bottom: 0,
            width: isPhone ? 280 : isTablet ? 320 : 360,
            transform: isChatOpen ? 'translateX(0)' : `translateX(${(isPhone ? 280 : isTablet ? 320 : 360) + 24}px)`,
            transition: 'transform 0.34s cubic-bezier(0.16, 1, 0.3, 1)',
            pointerEvents: isChatOpen ? 'auto' : 'none',
            display: 'grid',
            gridTemplateRows: 'auto 1fr auto',
            gap: '0',
            padding: isPhone ? '10px' : '12px',
            border: `1px solid ${signals.palette.border}`,
            background: signals.palette.panel,
            boxShadow: '0 18px 54px rgba(0,0,0,0.22)',
            overflow: 'hidden',
          }}
        >
          <div style={{ display: 'grid', gap: '5px', paddingBottom: '10px', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
            <div style={{ ...overlayGlowText, fontSize: isPhone ? '0.56rem' : '0.62rem', fontWeight: 800, letterSpacing: '3px' }}>
              CLAWDBOT_LINK
            </div>
            <div style={{ ...overlaySoftText, fontSize: '0.46rem', letterSpacing: '1.8px', lineHeight: 1.5 }}>
              LOCAL CHAT SURFACE // TOOL-CALL EMULATION READY
            </div>
          </div>

          <div style={{ overflowY: 'auto', padding: '12px 0', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {chatMessages.map((message) => (
              <div
                key={message.id}
                style={{
                  alignSelf: message.role === 'user' ? 'flex-end' : 'stretch',
                  maxWidth: message.role === 'user' ? '88%' : '100%',
                  padding: '10px 12px',
                  border: `1px solid ${message.role === 'user' ? signals.palette.secondary : signals.palette.border}`,
                  background: message.role === 'user' ? 'rgba(8, 47, 73, 0.44)' : 'rgba(255,255,255,0.03)',
                  color: message.role === 'system' ? 'rgba(255,255,255,0.66)' : '#e8f7ff',
                  fontSize: '0.58rem',
                  letterSpacing: '1px',
                  lineHeight: 1.55,
                  whiteSpace: 'pre-wrap',
                }}
              >
                <div style={{ fontSize: '0.36rem', letterSpacing: '1.8px', opacity: 0.58, marginBottom: '5px' }}>
                  {message.role === 'user' ? 'OPERATOR' : message.role === 'assistant' ? 'CLAWDBOT' : 'SYSTEM'}
                </div>
                {message.content}
              </div>
            ))}
            {chatBusy && (
              <div style={{ color: signals.palette.secondary, fontSize: '0.48rem', letterSpacing: '2px' }}>
                CLAWDBOT // THINKING...
              </div>
            )}
          </div>

          <div style={{ paddingTop: '10px', borderTop: '1px solid rgba(255,255,255,0.08)', display: 'grid', gap: '8px' }}>
            <textarea
              value={chatPrompt}
              onChange={(event) => setChatPrompt(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' && !event.shiftKey) {
                  event.preventDefault();
                  void submitChatPrompt();
                }
              }}
              placeholder="SEND ORDER TO CLAWDBOT..."
              style={{
                width: '100%',
                minHeight: isPhone ? '72px' : '84px',
                resize: 'none',
                background: 'rgba(15,23,42,0.82)',
                border: `1px solid ${signals.palette.border}`,
                color: '#f8fafc',
                padding: '12px 14px',
                fontSize: '0.64rem',
                letterSpacing: '1px',
                outline: 'none',
              }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '10px' }}>
              <div style={{ color: 'rgba(255,255,255,0.46)', fontSize: '0.38rem', letterSpacing: '1.7px' }}>
                ENTER // SEND
              </div>
              <button
                onClick={() => { void submitChatPrompt(); }}
                disabled={chatBusy || !chatPrompt.trim()}
                className="btn-nexus"
                style={{
                  padding: '8px 12px',
                  fontSize: '0.44rem',
                  letterSpacing: '1.8px',
                  opacity: chatBusy || !chatPrompt.trim() ? 0.52 : 1,
                  borderColor: signals.palette.secondary,
                }}
              >
                SEND
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* SOVEREIGN COMMAND HUD (Left Side) */}
      {/* Telemetry overlays now live in-scene for better spatial separation */}

      <div style={{ position: 'absolute', top: 30, left: '50%', transform: 'translateX(-50%)', textAlign: 'center', pointerEvents: 'none', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', zIndex: 180 }}>
        <h1 className="text-gradient" style={{ fontSize: isPhone ? '1rem' : isTablet ? '1.15rem' : '1.4rem', margin: 0, letterSpacing: isPhone ? '6px' : isTablet ? '9px' : '12px', fontWeight: 800, fontFamily: 'var(--font-sans)' }}>
          INVICTVS PROTOCOL
        </h1>

        <div style={{ color: '#ffffff', fontSize: isPhone ? '0.42rem' : '0.6rem', letterSpacing: isPhone ? '2px' : '6px', marginTop: '4px', fontWeight: 600, opacity: 0.74, textShadow: '0 0 14px rgba(255,255,255,0.18)', maxWidth: isPhone ? '180px' : 'none' }}>
          {tt(t, 'core.phase.subtitle', 'PHASE 25: SOVEREIGN BEVEL & LIQUID MASTERY')}
        </div>

        <div style={{ width: titleTelemetryWidth, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: isPhone ? '6px' : '8px', marginTop: isPhone ? '2px' : '5px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', padding: '4px 10px', background: signals.palette.panelSoft, border: `1px solid ${signals.palette.border}`, backdropFilter: 'none' }}>
            <div className="pulse-dot" style={{ width: '7px', height: '7px', background: fluxColor, boxShadow: `0 0 14px ${fluxColor}` }} />
            <span style={{ ...overlayGlowText, fontSize: isPhone ? '0.56rem' : '0.62rem', fontWeight: 800, letterSpacing: isPhone ? '2px' : '3px', color: healthColor }}>{healthLabel}</span>
            <span style={{ ...overlaySoftText, fontSize: '0.46rem', letterSpacing: '2px' }}>{modeLabelText}</span>
          </div>

          <div style={{ width: '100%', padding: isPhone ? '8px 10px' : '10px 12px', border: `1px solid ${fluxBorder}`, background: fluxBackground, backdropFilter: 'none', boxShadow: '0 14px 44px rgba(0,0,0,0.18)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2px' }}>
            <div style={{ ...overlaySoftText, fontSize: isPhone ? '0.5rem' : '0.56rem', letterSpacing: isPhone ? '2px' : '4px' }}>{tt(t, 'core.stability_flux', 'STABILITY_FLUX')}</div>
            <div style={{ color: fluxColor, fontSize: isPhone ? '0.6rem' : '0.68rem', letterSpacing: isPhone ? '2px' : '3px', fontWeight: 800 }}>{tt(t, 'core.sync_level', 'SYNC_LEVEL')}</div>
            <div style={{ ...overlayGlowText, fontSize: isPhone ? '1rem' : '1.18rem', fontWeight: 900, fontVariantNumeric: 'tabular-nums' }}>{syncLevel.toFixed(1)}%</div>
            <div style={{ color: fluxColor, fontSize: isPhone ? '0.48rem' : '0.54rem', letterSpacing: '2px', fontWeight: 700 }}>{tt(t, 'core.live_drift', 'LIVE_DRIFT')} {drift.toFixed(4)}</div>
            <div style={{ ...overlaySoftText, fontSize: '0.42rem', letterSpacing: '2px' }}>{modeReasonText}</div>
          </div>
        </div>
      </div>

      <div style={{ position: 'absolute', top: isPhone ? 16 : 22, right: isPhone ? 16 : 24, zIndex: 620, pointerEvents: 'auto' }}>
        <button
          onClick={handleEditModeToggle}
          className="btn-nexus"
          style={{
            padding: isPhone ? '8px 10px' : '9px 12px',
            fontSize: isPhone ? '0.44rem' : '0.5rem',
            letterSpacing: '2px',
            background: assetEditState.enabled ? 'rgba(5, 46, 73, 0.96)' : 'rgba(2, 6, 23, 0.92)',
            borderColor: assetEditState.enabled ? signals.palette.secondary : signals.palette.border,
            boxShadow: assetEditState.enabled ? `0 0 18px ${signals.palette.secondary}26` : '0 10px 24px rgba(0,0,0,0.25)',
          }}
        >
          {assetEditState.enabled ? 'EDIT_MODE_ON' : 'EDIT_MODE'}
        </button>
        {assetEditState.enabled && (
          <div
            style={{
              marginTop: '8px',
              padding: isPhone ? '7px 9px' : '8px 10px',
              background: 'rgba(2, 6, 23, 0.92)',
              border: `1px solid ${signals.palette.secondary}`,
              boxShadow: `0 0 18px ${signals.palette.secondary}16`,
              color: '#e5f7ff',
              fontSize: isPhone ? '0.4rem' : '0.44rem',
              letterSpacing: '1.8px',
              lineHeight: 1.45,
              textAlign: 'right',
              maxWidth: isPhone ? '160px' : '190px',
            }}
          >
            EDIT ACTIVE
            <br />
            SELECT NODE // DRAG MOVE
          </div>
        )}
      </div>

      {editModePromptOpen && (
        <div
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) {
              setEditModePromptOpen(false);
              setEditModePassword('');
            }
          }}
          style={{
            position: 'absolute',
            inset: 0,
            zIndex: 860,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'rgba(0,0,0,0.72)',
            backdropFilter: 'none',
            pointerEvents: 'auto',
          }}
        >
          <div
            style={{
              width: isPhone ? 'min(320px, calc(100vw - 24px))' : '360px',
              background: 'linear-gradient(180deg, rgba(2,6,23,0.985), rgba(4,10,24,0.96))',
              border: `1px solid ${signals.palette.border}`,
              borderTop: `2px solid ${signals.palette.secondary}`,
              borderRadius: '14px',
              boxShadow: `0 18px 48px rgba(0,0,0,0.36), 0 0 0 1px ${signals.palette.border}22 inset`,
              padding: isPhone ? '16px' : '18px',
              display: 'grid',
              gap: '12px',
            }}
          >
            <div style={{ display: 'grid', gap: '4px' }}>
              <div style={{ color: 'rgba(255,255,255,0.42)', fontSize: '0.36rem', letterSpacing: '2px' }}>
                SECURE ACCESS
              </div>
              <div style={{ color: '#e5f7ff', fontSize: isPhone ? '0.72rem' : '0.82rem', fontWeight: 800, letterSpacing: '1.5px' }}>
                UNLOCK_EDIT_MODE
              </div>
              <div style={{ color: 'rgba(255,255,255,0.62)', fontSize: '0.46rem', letterSpacing: '1.6px', lineHeight: 1.5 }}>
                AUTHORIZATION REQUIRED FOR ASSET POSITION, ROTATION AND SCALE EDITS.
              </div>
            </div>

            <input
              type="password"
              value={editModePassword}
              onChange={(event) => setEditModePassword(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter') {
                  submitEditModePassword();
                }
                if (event.key === 'Escape') {
                  setEditModePromptOpen(false);
                  setEditModePassword('');
                }
              }}
              autoFocus
              placeholder="ACCESS KEY"
              style={{
                width: '100%',
                background: 'rgba(15,23,42,0.82)',
                border: `1px solid ${signals.palette.border}`,
                color: '#f8fafc',
                borderRadius: '10px',
                padding: '12px 14px',
                fontSize: '0.72rem',
                letterSpacing: '2px',
                outline: 'none',
                boxShadow: `0 0 18px ${signals.palette.secondary}12 inset`,
              }}
            />

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', flexWrap: 'wrap' }}>
              <button
                onClick={() => {
                  setEditModePromptOpen(false);
                  setEditModePassword('');
                }}
                className="btn-nexus"
                style={{ padding: '8px 12px', fontSize: '0.44rem', letterSpacing: '1.8px' }}
              >
                CANCEL
              </button>
              <button
                onClick={submitEditModePassword}
                className="btn-nexus"
                style={{
                  padding: '8px 12px',
                  fontSize: '0.44rem',
                  letterSpacing: '1.8px',
                  borderColor: signals.palette.secondary,
                  boxShadow: `0 0 16px ${signals.palette.secondary}18`,
                }}
              >
                UNLOCK
              </button>
            </div>
          </div>
        </div>
      )}

      {assetEditState.enabled && (
        <div style={{ position: 'absolute', left: '50%', transform: 'translateX(-50%)', bottom: dockBottom, zIndex: 240, width: isPhone ? 'calc(100vw - 24px)' : 'min(620px, calc(100vw - 180px))', maxWidth: 'calc(100vw - 20px)', pointerEvents: 'auto' }}>
          <div style={{
            background: `linear-gradient(180deg, rgba(2, 6, 23, 0.985), rgba(4, 10, 24, 0.96))`,
            border: `1px solid ${signals.palette.border}`,
            borderTop: `2px solid ${dockAccent}`,
            borderRadius: isPhone ? '12px' : '14px',
            boxShadow: `0 14px 30px rgba(0,0,0,0.24), 0 0 0 1px ${signals.palette.border}16 inset`,
            overflow: 'hidden',
          }}>
            <div style={{ padding: isPhone ? '10px' : '11px 12px', display: 'grid', gap: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                <div style={{ minWidth: 0 }}>
                  <div style={{ color: 'rgba(255,255,255,0.42)', fontSize: '0.34rem', letterSpacing: '2px' }}>EDIT_MODE</div>
                  <div style={{ color: dockTitleColor, fontSize: isPhone ? '0.62rem' : '0.72rem', fontWeight: 800, letterSpacing: '1px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {dockTitle}
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  <button
                    onClick={() => { void saveEditModeSession(); }}
                    className="btn-nexus"
                    style={{
                      padding: '7px 10px',
                      fontSize: '0.44rem',
                      letterSpacing: '1.8px',
                      borderColor: editSessionDirty ? signals.palette.secondary : signals.palette.border,
                      color: editSessionDirty ? signals.palette.emphasis : 'rgba(255,255,255,0.62)',
                    }}
                  >
                    SAVE
                  </button>
                  <button
                    onClick={() => { void revertEditModeSession(); }}
                    className="btn-nexus"
                    style={{
                      padding: '7px 10px',
                      fontSize: '0.44rem',
                      letterSpacing: '1.8px',
                      borderColor: editSessionDirty ? signals.palette.warning : signals.palette.border,
                      color: editSessionDirty ? signals.palette.warning : 'rgba(255,255,255,0.62)',
                    }}
                  >
                    REVERT
                  </button>
                  <button onClick={handleEditModeToggle} className="btn-nexus" style={{ padding: '7px 10px', fontSize: '0.44rem', letterSpacing: '1.8px' }}>CLOSE_EDIT</button>
                  {inspectorNode && (
                    <button onClick={() => selectedSentinelIndex !== null ? openSentinelAssetPicker() : openAssetPicker(inspectorNode, 'appearance')} className="btn-nexus" style={{ padding: '7px 10px', fontSize: '0.44rem', letterSpacing: '1.8px' }}>
                      ASSIGN GLB
                    </button>
                  )}
                </div>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                <div style={{ color: editSessionDirty ? signals.palette.warning : 'rgba(255,255,255,0.48)', fontSize: '0.36rem', letterSpacing: '1.8px' }}>
                  {editSessionDirty ? 'SESSION DIRTY // SAVE OR REVERT' : 'SESSION SYNCED'}
                </div>
                <div style={{ color: 'rgba(255,255,255,0.42)', fontSize: '0.34rem', letterSpacing: '1.6px' }}>
                  ACCESS LOCKED // EDIT SURFACE
                </div>
              </div>
              {inspectorNode ? (
                <>
                  <div style={{ display: 'grid', gridTemplateColumns: isPhone ? 'repeat(2, minmax(0, 1fr))' : 'repeat(4, minmax(0, 1fr))', gap: '8px' }}>
                    <button onClick={() => selectedSentinelIndex !== null ? patchSentinelAssetSettings({ offset: [((sentinelAppearanceStage.offset?.[0] || 0) - 0.1), sentinelAppearanceStage.offset?.[1] || 0, sentinelAppearanceStage.offset?.[2] || 0] }) : nudgeSelectedAssetOffset('x', -0.1)} className="btn-nexus" style={{ padding: '7px 8px', fontSize: '0.44rem', letterSpacing: '1.6px' }}>MOVE_X-</button>
                    <button onClick={() => selectedSentinelIndex !== null ? patchSentinelAssetSettings({ offset: [((sentinelAppearanceStage.offset?.[0] || 0) + 0.1), sentinelAppearanceStage.offset?.[1] || 0, sentinelAppearanceStage.offset?.[2] || 0] }) : nudgeSelectedAssetOffset('x', 0.1)} className="btn-nexus" style={{ padding: '7px 8px', fontSize: '0.44rem', letterSpacing: '1.6px' }}>MOVE_X+</button>
                    <button onClick={() => selectedSentinelIndex !== null ? patchSentinelAssetSettings({ offset: [sentinelAppearanceStage.offset?.[0] || 0, sentinelAppearanceStage.offset?.[1] || 0, ((sentinelAppearanceStage.offset?.[2] || 0) - 0.1)] }) : nudgeSelectedAssetOffset('z', -0.1)} className="btn-nexus" style={{ padding: '7px 8px', fontSize: '0.44rem', letterSpacing: '1.6px' }}>MOVE_Z-</button>
                    <button onClick={() => selectedSentinelIndex !== null ? patchSentinelAssetSettings({ offset: [sentinelAppearanceStage.offset?.[0] || 0, sentinelAppearanceStage.offset?.[1] || 0, ((sentinelAppearanceStage.offset?.[2] || 0) + 0.1)] }) : nudgeSelectedAssetOffset('z', 0.1)} className="btn-nexus" style={{ padding: '7px 8px', fontSize: '0.44rem', letterSpacing: '1.6px' }}>MOVE_Z+</button>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: isPhone ? 'repeat(2, minmax(0, 1fr))' : 'repeat(4, minmax(0, 1fr))', gap: '8px' }}>
                    <button onClick={() => selectedSentinelIndex !== null ? rotateSentinelAssetX(-15) : rotateSelectedAssetY(-15)} className="btn-nexus" style={{ padding: '7px 8px', fontSize: '0.44rem', letterSpacing: '1.6px' }}>{selectedSentinelIndex !== null ? 'ROT_X-15' : 'ROT_Y-15'}</button>
                    <button onClick={() => selectedSentinelIndex !== null ? rotateSentinelAssetX(15) : rotateSelectedAssetY(15)} className="btn-nexus" style={{ padding: '7px 8px', fontSize: '0.44rem', letterSpacing: '1.6px' }}>{selectedSentinelIndex !== null ? 'ROT_X+15' : 'ROT_Y+15'}</button>
                    <button onClick={() => selectedSentinelIndex !== null ? scaleSentinelAsset(-0.08) : scaleSelectedAsset(-0.08)} className="btn-nexus" style={{ padding: '7px 8px', fontSize: '0.44rem', letterSpacing: '1.6px' }}>SCALE-</button>
                    <button onClick={() => selectedSentinelIndex !== null ? scaleSentinelAsset(0.08) : scaleSelectedAsset(0.08)} className="btn-nexus" style={{ padding: '7px 8px', fontSize: '0.44rem', letterSpacing: '1.6px' }}>SCALE+</button>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: isPhone ? 'repeat(2, minmax(0, 1fr))' : selectedSentinelIndex !== null ? 'repeat(4, minmax(0, 1fr))' : 'repeat(3, minmax(0, 1fr))', gap: '8px' }}>
                    <div style={{ background: signals.palette.panelSoft, padding: '7px 9px', border: `1px solid ${signals.palette.border}` }}>
                      <div style={{ ...overlayFaintText, fontSize: '0.36rem', letterSpacing: '1.8px' }}>OFFSET</div>
                      <div style={{ ...overlayGlowText, fontSize: '0.46rem', fontWeight: 700 }}>{selectedSentinelIndex !== null ? `${(sentinelAppearanceStage.offset?.[0] || 0).toFixed(2)} / ${(sentinelAppearanceStage.offset?.[2] || 0).toFixed(2)}` : `${selectedAssetStageTransform.offset[0].toFixed(2)} / ${selectedAssetStageTransform.offset[2].toFixed(2)}`}</div>
                    </div>
                    {selectedSentinelIndex !== null && (
                      <div style={{ background: signals.palette.panelSoft, padding: '7px 9px', border: `1px solid ${signals.palette.border}` }}>
                        <div style={{ ...overlayFaintText, fontSize: '0.36rem', letterSpacing: '1.8px' }}>ROT_X</div>
                        <div style={{ ...overlayGlowText, fontSize: '0.46rem', fontWeight: 700 }}>{THREE.MathUtils.radToDeg((sentinelAppearanceStage.rotation || [0, 0, 0])[0]).toFixed(1)}°</div>
                      </div>
                    )}
                    <div style={{ background: signals.palette.panelSoft, padding: '7px 9px', border: `1px solid ${signals.palette.border}` }}>
                      <div style={{ ...overlayFaintText, fontSize: '0.36rem', letterSpacing: '1.8px' }}>ROT_Y</div>
                      <div style={{ ...overlayGlowText, fontSize: '0.46rem', fontWeight: 700 }}>{selectedSentinelIndex !== null ? `${THREE.MathUtils.radToDeg((sentinelAppearanceStage.rotation || [0, 0, 0])[1]).toFixed(1)}°` : `${THREE.MathUtils.radToDeg(selectedAssetStageTransform.rotation[1]).toFixed(1)}°`}</div>
                    </div>
                    <div style={{ background: signals.palette.panelSoft, padding: '7px 9px', border: `1px solid ${signals.palette.border}` }}>
                      <div style={{ ...overlayFaintText, fontSize: '0.36rem', letterSpacing: '1.8px' }}>SCALE</div>
                      <div style={{ ...overlayGlowText, fontSize: '0.46rem', fontWeight: 700 }}>{selectedSentinelIndex !== null ? `${(sentinelAppearanceStage.scale ?? 1).toFixed(2)}` : `${selectedAssetStageTransform.scale.toFixed(2)}`}</div>
                    </div>
                  </div>
                </>
              ) : (
                <div style={{ ...overlaySoftText, fontSize: '0.44rem', letterSpacing: '1.8px', textAlign: 'center' }}>
                  SELECT NODE OR SENTINEL TO EDIT
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* FILE VIEWER (With Forensic Handshake) */}
      {openDoc && (
        <div
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) setOpenDoc(null);
          }}
          style={{
          position: 'absolute', inset: 0, zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center',
          background: 'rgba(0,0,0,0.56)', backdropFilter: 'none'
        }}>
          <div style={{
            width: isPhone ? '90%' : '70%', height: isPhone ? '88%' : '80%', background: `linear-gradient(180deg, ${signals.palette.panel}, rgba(0,0,0,0.96))`,
            border: `1px solid ${signals.palette.border}`, display: 'flex', flexDirection: 'column', color: '#e4e4e7',
            backdropFilter: 'none', borderRadius: '12px', overflow: 'hidden', textShadow: '0 0 14px rgba(255,255,255,0.18)', boxShadow: '0 24px 80px rgba(0,0,0,0.36)'
          }}>
          <div style={{ padding: '15px 25px', borderBottom: '1px solid rgba(255,255,255,0.1)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: signals.palette.panelSoft, gap: '16px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '7px', minWidth: 0 }}>
              <span style={{ fontSize: '0.7rem', letterSpacing: '4px', fontWeight: 800, fontFamily: 'var(--font-mono)', opacity: 0.72 }}>{tt(t, 'viewer.decrypting_stream', 'DECRYPTING_STREAM')} // {openDoc.fileName}</span>
              <span style={{ ...overlaySoftText, fontSize: '0.46rem', letterSpacing: '2px' }}>{modeReasonText}</span>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', fontSize: '0.44rem', letterSpacing: '1.8px', color: 'rgba(255,255,255,0.66)' }}>
                <span>{tt(t, 'viewer.path', 'PATH')}: {openDoc.filePath}</span>
                <span>{tt(t, 'viewer.format', 'FORMAT')}: {docFormatLabel}</span>
                <span>{tt(t, 'viewer.readonly', 'READ_ONLY')}</span>
                {openDoc.truncated && <span style={{ color: signals.palette.warning }}>{tt(t, 'viewer.truncated', 'TRUNCATED')}</span>}
              </div>
            </div>
            <button onClick={() => setOpenDoc(null)} className="btn-nexus" style={{ padding: '8px 20px', fontSize: '0.6rem' }}>X {tt(t, 'viewer.terminate', 'TERMINATE')}</button>
          </div>
          <div style={{ padding: '12px 24px', borderBottom: '1px solid rgba(255,255,255,0.08)', background: 'rgba(2,6,23,0.7)', display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
            <input
              value={docQuery}
              onChange={(event) => setDocQuery(event.target.value)}
              placeholder={tt(t, 'viewer.search', 'SEARCH_STREAM')}
              style={{
                flex: '1 1 240px',
                minWidth: isPhone ? '100%' : '240px',
                background: 'rgba(15,23,42,0.82)',
                border: `1px solid ${signals.palette.border}`,
                color: '#f8fafc',
                borderRadius: '999px',
                padding: '10px 14px',
                fontSize: '0.72rem',
                letterSpacing: '2px',
                outline: 'none',
                boxShadow: `0 0 18px ${signals.palette.secondary}12 inset`,
              }}
            />
            <div style={{ color: 'rgba(255,255,255,0.68)', fontSize: '0.48rem', letterSpacing: '2px' }}>
              {tt(t, 'viewer.matches', 'MATCHES')}: {docMatchCount}
            </div>
          </div>
          <div style={{ flex: 1, padding: '30px', overflow: 'auto', background: 'linear-gradient(180deg, rgba(0,0,0,0.94), rgba(3,7,18,0.98))' }}>
            <DecryptionHandshake onComplete={() => {}} dictionary={t} />
            {renderDocumentSurface(openDoc, deferredDocQuery, t)}
          </div>
          </div>
        </div>
      )}

      {/* UNLINK / LINK MODAL */}
      {unlinkModal && (
        <div style={{
          position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.8)', zIndex: 2000,
          display: 'flex', alignItems: 'center', justifyContent: 'center', backdropFilter: 'none'
        }}>
          <div className="glass-panel" style={{ padding: isPhone ? '24px 20px' : '40px', width: isPhone ? 'min(340px, calc(100vw - 24px))' : '400px', textAlign: 'center', borderRadius: '14px' }}>
            <h2 style={{ letterSpacing: '4px', fontSize: '1.2rem', marginBottom: '20px' }}>
              {unlinkModal === 'link' ? tt(t, 'modal.initiate_link', 'INITIATE_LINK') : tt(t, 'modal.terminate_link', 'TERMINATE_LINK')}
            </h2>
            <p style={{ fontSize: '0.8rem', opacity: 0.7, marginBottom: '30px', lineHeight: '1.6' }}>
              {unlinkModal === 'link' 
                ? tt(t, 'modal.link.confirm', 'ESTABLISHING CORE CONNECTION WITH EXTERNAL PROJECT STREAM. PROCEED?')
                : tt(t, 'modal.unlink.confirm', 'DISCONNECTING FROM THE CURRENT PROJECT ARCHITECTURE. ALL DYNAMIC NODES WILL BE PURGED.')}
            </p>
            <div style={{ display: 'flex', gap: '15px', justifyContent: 'center' }}>
               <button 
                  onPointerDown={() => {
                     if (unlinkModal === 'link') {
                      window.dispatchEvent(new CustomEvent('continuity:confirm-link'));
                       setUnlinkModal(null);
                       return;
                     }
                     if (primaryLinkedSystem) {
                      removeLinkedSystemHandle(primaryLinkedSystem.id);
                       setLinkedSystems((prev) => {
                         const remaining = prev.filter((system) => system.id !== primaryLinkedSystem.id);
                         setActiveLinkedSystemId(remaining[0]?.id || null);
                         return remaining;
                      });
                    }
                    setUnlinkModal(null);
                  }}
                  className="btn-liquid-3d"
                  style={{ borderRadius: '50px' }}
                >
                  {tt(t, 'common.confirm', 'CONFIRM_ACTION')}
                </button>
                <button 
                  onClick={() => setUnlinkModal(null)}
                  className="btn-liquid-3d"
                  style={{ background: 'linear-gradient(135deg, #333, #000)', color: '#fff', borderRadius: '50px' }}
                >
                  {tt(t, 'common.abort', 'ABORT')}
                </button>
             </div>
          </div>
        </div>
      )}

      {/* TOAST NOTIFICATIONS */}
      {toastMsg && (
        <div className="btn-liquid-3d" style={{
          position: 'absolute', top: isPhone ? 'auto' : 180, bottom: isPhone ? 20 : 'auto', right: railRight, padding: isPhone ? '12px 18px' : '15px 30px', 
          borderLeft: '4px solid #000', zIndex: 1000, animation: 'slideIn 0.3s ease-out',
          flexDirection: 'column', alignItems: 'flex-start', minWidth: isPhone ? '160px' : '200px', maxWidth: isPhone ? '200px' : '280px', pointerEvents: 'none'
        }}>
          <div style={{ fontSize: '0.8rem', fontWeight: 800 }}>{toastMsg.msg}</div>
          {toastMsg.detail && <div style={{ fontSize: '0.6rem', color: '#000', opacity: 0.6, marginTop: '4px' }}>{toastMsg.detail}</div>}
        </div>
      )}
    </div>
  );
};

interface NexusCoreProps {
  linkedSystems: LinkedSystem[];
  activeLinkedSystemId: string | null;
  language: Language;
  setLinkedSystems: React.Dispatch<React.SetStateAction<LinkedSystem[]>>;
  setActiveLinkedSystemId: React.Dispatch<React.SetStateAction<string | null>>;
  physics?: PhysicsSnapshot;
  drift?: number;
  merkle?: string;
  chainEvents: ChainEventSnapshot[];
  chainStatus: ChainStatusSnapshot | null;
  activeCommand: string | null;
}

export default NexusCore;
