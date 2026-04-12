export interface PhysicsSnapshot {
  H: number;
  H_max: number;
  eta: number;
  N: number;
  W: number;
  gini: number;
}

export interface StateSnapshot {
  merkle_root: string;
  last_check?: string;
  physics: PhysicsSnapshot;
  drift_kl: number;
  crystallizer_version?: string;
}

export interface ChainEventSnapshot {
  seq?: number;
  type: string;
  timestamp?: string;
  chain_hash?: string;
}

export interface ChainStatusSnapshot {
  intact: boolean;
  error?: string;
}

export type DashboardMode = 'STABLE' | 'AUDIT' | 'INCIDENT' | 'SEAL';

interface ModePalette {
  accent: string;
  secondary: string;
  emphasis: string;
  panel: string;
  panelSoft: string;
  border: string;
  haze: string;
  sceneBg: string;
  fog: string;
  ambient: string;
  line: string;
  warning: string;
  label: string;
}

export interface DashboardSignals {
  mode: DashboardMode;
  palette: ModePalette;
  modeReason: string;
  modeLabel: string;
  syncLevel: number;
  chainTrust: number;
  chainTrustLabel: string;
  severity: number;
  severityLabel: string;
  entropyRatio: number;
  activity: number;
  merkleShort: string;
  merkleFingerprint: string;
  recentEventType: string;
  recentEventFreshnessSec: number | null;
}

interface DashboardSignalInput {
  state?: Partial<StateSnapshot> | null;
  chainEvents?: ChainEventSnapshot[];
  chainStatus?: ChainStatusSnapshot | null;
  activeAction?: string | null;
  linkedProject?: string | null;
  linkedProjectCount?: number;
  liveLogs?: Array<{ msg?: string }>;
}

const MODE_PALETTES: Record<DashboardMode, ModePalette> = {
  STABLE: {
    accent: '#22d3ee',
    secondary: '#67e8f9',
    emphasis: '#ffffff',
    panel: 'rgba(16, 19, 24, 0.58)',
    panelSoft: 'rgba(255, 255, 255, 0.06)',
    border: 'rgba(34, 211, 238, 0.2)',
    haze: 'radial-gradient(circle at 50% 22%, rgba(34,211,238,0.12), transparent 42%), radial-gradient(circle at 70% 82%, rgba(255,255,255,0.05), transparent 30%)',
    sceneBg: '#020617',
    fog: '#020617',
    ambient: '#a5f3fc',
    line: '#e0f2fe',
    warning: '#22c55e',
    label: 'SYSTEM_STABLE',
  },
  AUDIT: {
    accent: '#e2e8f0',
    secondary: '#38bdf8',
    emphasis: '#ffffff',
    panel: 'rgba(18, 20, 26, 0.6)',
    panelSoft: 'rgba(255, 255, 255, 0.065)',
    border: 'rgba(226, 232, 240, 0.18)',
    haze: 'radial-gradient(circle at 50% 18%, rgba(148,163,184,0.14), transparent 40%), radial-gradient(circle at 78% 74%, rgba(56,189,248,0.08), transparent 28%)',
    sceneBg: '#020617',
    fog: '#0f172a',
    ambient: '#cbd5e1',
    line: '#f8fafc',
    warning: '#38bdf8',
    label: 'AUDIT_VECTOR',
  },
  INCIDENT: {
    accent: '#ef4444',
    secondary: '#f59e0b',
    emphasis: '#fff1f2',
    panel: 'rgba(25, 16, 16, 0.62)',
    panelSoft: 'rgba(255, 255, 255, 0.055)',
    border: 'rgba(239, 68, 68, 0.22)',
    haze: 'radial-gradient(circle at 50% 18%, rgba(239,68,68,0.16), transparent 40%), radial-gradient(circle at 74% 80%, rgba(245,158,11,0.10), transparent 24%)',
    sceneBg: '#08050b',
    fog: '#12060a',
    ambient: '#fda4af',
    line: '#fecaca',
    warning: '#f59e0b',
    label: 'INCIDENT_RESPONSE',
  },
  SEAL: {
    accent: '#22c55e',
    secondary: '#bef264',
    emphasis: '#f7fee7',
    panel: 'rgba(16, 23, 20, 0.6)',
    panelSoft: 'rgba(255, 255, 255, 0.055)',
    border: 'rgba(34, 197, 94, 0.2)',
    haze: 'radial-gradient(circle at 50% 18%, rgba(34,197,94,0.14), transparent 40%), radial-gradient(circle at 76% 78%, rgba(190,242,100,0.08), transparent 24%)',
    sceneBg: '#020b08',
    fog: '#04110d',
    ambient: '#86efac',
    line: '#dcfce7',
    warning: '#bef264',
    label: 'VAULT_SEALING',
  },
};

function clamp(value: number, min = 0, max = 1) {
  return Math.min(max, Math.max(min, value));
}

function normalizeType(raw?: string | null) {
  return (raw || 'IDLE').toUpperCase().replace(/[^A-Z0-9]+/g, '_');
}

function getEventFreshnessSeconds(timestamp?: string) {
  if (!timestamp) return null;
  const eventTime = Date.parse(timestamp);
  if (Number.isNaN(eventTime)) return null;
  return Math.max(0, Math.floor((Date.now() - eventTime) / 1000));
}

function inferMode({
  drift,
  chainStatus,
  activeAction,
  recentEventType,
  recentEventFreshnessSec,
}: {
  drift: number;
  chainStatus?: ChainStatusSnapshot | null;
  activeAction?: string | null;
  recentEventType: string;
  recentEventFreshnessSec: number | null;
}): DashboardMode {
  const action = normalizeType(activeAction);
  const recentType = normalizeType(recentEventType);
  const recentEventHot = recentEventFreshnessSec !== null && recentEventFreshnessSec < 120;
  const tampered = chainStatus ? !chainStatus.intact : false;

  if (action.includes('SEAL') || (recentEventHot && recentType.includes('SEAL'))) return 'SEAL';
  if (tampered || drift >= 0.11) return 'INCIDENT';
  if (action.includes('AUDIT') || (recentEventHot && recentType.includes('AUDIT'))) return 'AUDIT';
  if (action.includes('CRYSTALLIZE') || (recentEventHot && recentType.includes('CRYSTALLIZE'))) return 'AUDIT';
  return 'STABLE';
}

export function deriveDashboardSignals(input: DashboardSignalInput): DashboardSignals {
  const state = input.state;
  const physics = state?.physics;
  const drift = clamp(Number(state?.drift_kl || 0), 0, 1);
  const eta = clamp(Number(physics?.eta || 0), 0, 1);
  const entropyRatio = physics?.H_max ? clamp((physics.H || 0) / physics.H_max) : 0;
  const chainEvents = input.chainEvents || [];
  const liveLogs = input.liveLogs || [];
  const linkedProjectCount = Math.max(0, Number(input.linkedProjectCount || (input.linkedProject ? 1 : 0)));
  const latestEvent = chainEvents[0];
  const recentEventType = normalizeType(latestEvent?.type);
  const recentEventFreshnessSec = getEventFreshnessSeconds(latestEvent?.timestamp);
  const mode = inferMode({
    drift,
    chainStatus: input.chainStatus,
    activeAction: input.activeAction,
    recentEventType,
    recentEventFreshnessSec,
  });
  const palette = MODE_PALETTES[mode];
  const chainTrustBase = input.chainStatus
    ? (input.chainStatus.intact ? 1 : 0.12)
    : chainEvents.length > 0
    ? 0.84
    : 0.72;
  const chainTrust = clamp(chainTrustBase - drift * 0.08);
  const syncLevel = clamp((eta * 0.68) + ((1 - drift) * 0.24) + (chainTrust * 0.08)) * 100;
  const activity = clamp(
    chainEvents.length / 8
    + liveLogs.length / 8
    + (input.activeAction ? 0.28 : 0)
    + Math.min(0.18, linkedProjectCount * 0.05),
  );
  const severity = clamp(
    drift * 4.6
    + (input.chainStatus && !input.chainStatus.intact ? 0.46 : 0)
    + (mode === 'AUDIT' ? 0.12 : 0)
    + (mode === 'SEAL' ? 0.18 : 0)
    + activity * 0.1,
  );
  const severityLabel = severity >= 0.72 ? 'CRITICAL' : severity >= 0.4 ? 'ELEVATED' : 'LOW';
  const chainTrustLabel = chainTrust >= 0.92 ? 'LOCKED' : chainTrust >= 0.72 ? 'VERIFIED' : chainTrust >= 0.42 ? 'WATCH' : 'BREACHED';
  const merkle = String(state?.merkle_root || '0'.repeat(64));
  const merkleShort = merkle.slice(0, 12).toUpperCase();
  const merkleFingerprint = `${merkle.slice(0, 6).toUpperCase()}-${merkle.slice(-6).toUpperCase()}`;

  let modeReason = 'SOVEREIGN_IDLE';
  if (input.chainStatus && !input.chainStatus.intact) {
    modeReason = 'CHAIN_TAMPER_DETECTED';
  } else if (mode === 'SEAL') {
    modeReason = 'VAULT_LOCK_SEQUENCE_ACTIVE';
  } else if (mode === 'AUDIT') {
    modeReason = 'AUDIT_PHYSICS_VECTOR_ENGAGED';
  } else if (drift >= 0.05) {
    modeReason = 'DRIFT_CONTAINMENT_ACTIVE';
  } else if (linkedProjectCount > 0 || input.linkedProject) {
    modeReason = 'LIVE_PROJECT_LINK_ESTABLISHED';
  }

  return {
    mode,
    palette,
    modeReason,
    modeLabel: palette.label,
    syncLevel,
    chainTrust,
    chainTrustLabel,
    severity,
    severityLabel,
    entropyRatio,
    activity,
    merkleShort,
    merkleFingerprint,
    recentEventType,
    recentEventFreshnessSec,
  };
}
