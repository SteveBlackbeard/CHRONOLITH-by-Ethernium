// Graph data model for the Nexus constellation.
// Defines node families, hierarchy, and the dynamic layout used by the dashboard.
import { Language, translations } from './i18n';

export type NodeCluster = 'dashboard' | 'agents' | 'documents' | 'tools' | 'system' | 'linked-root';
export type NodeImportance = 'primary' | 'secondary' | 'tertiary';
export type NodeMotionProfile = 'static' | 'living' | 'sentinel-linked';

export interface GraphNodeAssetStageOverride {
  src: string;
  enabled?: boolean;
  scale?: number;
  offset?: [number, number, number];
  rotation?: [number, number, number];
  animatedMaterial?: boolean;
  autoplay?: boolean;
  animationClip?: string | '__auto';
  opacity?: number;
  label?: string;
}

export interface GraphNodeAssetOverride {
  appearance?: GraphNodeAssetStageOverride | null;
  effect?: GraphNodeAssetStageOverride | null;
}

export interface GraphNode {
  id: string;
  label: string;
  position: [number, number, number];
  type: 'core' | 'engine' | 'edition' | 'module' | 'file' | 'folder' | 'link-placeholder';
  shape: 'octahedron' | 'tetrahedron' | 'sphere' | 'document' | 'folder-icon';
  size: number;
  parentId: string | null;
  action?: string;
  tooltip: string;
  color?: string;
  filePath?: string;
  cluster?: NodeCluster;
  orbitLevel?: number;
  importance?: NodeImportance;
  systemId?: string | null;
  motionProfile?: NodeMotionProfile;
  assetOverride?: GraphNodeAssetOverride;
}

export interface GraphEdge {
  from: string;
  to: string;
}

export interface ScannedEntry {
  name: string;
  type: 'file' | 'dir';
  size?: number;
}

export interface LinkedSystem {
  id: string;
  name: string;
  rootPath: string;
  entries: ScannedEntry[];
  accessMode?: 'runtime' | 'handle' | 'structural';
}

const CLUSTER_ORDER: Exclude<NodeCluster, 'linked-root'>[] = ['dashboard', 'agents', 'documents', 'tools', 'system'];

export const GRAPH_CLUSTER_CONFIG: Record<NodeCluster, { label: string; color: string; tooltip: string }> = {
  'linked-root': {
    label: 'LINKED_SYSTEM',
    color: '#ffffff',
    tooltip: 'Linked sovereign system gateway.',
  },
  dashboard: {
    label: 'DASHBOARD',
    color: '#38bdf8',
    tooltip: 'Interface, UI surface, and presentation layer.',
  },
  agents: {
    label: 'AGENTS',
    color: '#a78bfa',
    tooltip: 'Agents, orchestration, and automation workers.',
  },
  documents: {
    label: 'DOCUMENTS',
    color: '#e2e8f0',
    tooltip: 'Knowledge, manifests, contexts, and narrative records.',
  },
  tools: {
    label: 'TOOLS',
    color: '#f59e0b',
    tooltip: 'Runtime tools, scripts, APIs, and operational utilities.',
  },
  system: {
    label: 'SYSTEM',
    color: '#22d3ee',
    tooltip: 'Residual runtime structure and uncategorized system assets.',
  },
};

// Helper: distribute children around a parent in 3D.
function fanPositions(
  center: [number, number, number],
  count: number,
  radius: number,
  yOffset = 0,
  startAngle = 0,
): [number, number, number][] {
  const positions: [number, number, number][] = [];
  for (let i = 0; i < count; i++) {
    const angle = startAngle + (i / Math.max(count, 1)) * Math.PI * 2;
    positions.push([
      center[0] + Math.cos(angle) * radius,
      center[1] + yOffset,
      center[2] + Math.sin(angle) * radius,
    ]);
  }
  return positions;
}

function normalizeEntryName(name: string) {
  return name.toLowerCase().trim();
}

function classifyEntry(entry: ScannedEntry): Exclude<NodeCluster, 'linked-root'> {
  const lowerName = normalizeEntryName(entry.name);
  const ext = lowerName.includes('.') ? lowerName.split('.').pop() || '' : '';

  const dashboardHints = ['dashboard', 'app', 'src', 'public', 'components', 'ui', 'pages', 'web', 'frontend'];
  const agentHints = ['agents', 'agent', '.agents', 'bots', 'workers', 'skills', 'mcp', 'automation'];
  const documentHints = ['docs', 'readme', 'context', 'manifest', 'notes', 'changelog'];
  const toolHints = ['tools', 'scripts', 'bin', 'cli', 'lib', 'utils', 'api', 'server'];

  if (dashboardHints.some((hint) => lowerName.includes(hint))) return 'dashboard';
  if (agentHints.some((hint) => lowerName.includes(hint))) return 'agents';
  if (documentHints.some((hint) => lowerName.includes(hint)) || ['md', 'txt', 'pdf'].includes(ext)) return 'documents';
  if (toolHints.some((hint) => lowerName.includes(hint)) || ['py', 'json', 'ts', 'tsx', 'js', 'sh'].includes(ext)) return 'tools';
  return 'system';
}

function buildEntryNode(
  base: {
    projectId: string;
    systemId: string | null;
    rootPath: string;
    parentId: string;
    entry: ScannedEntry;
    position: [number, number, number];
    cluster: Exclude<NodeCluster, 'linked-root'>;
    size: number;
    orbitLevel: number;
  },
): GraphNode {
  const accent = GRAPH_CLUSTER_CONFIG[base.cluster].color;
  return {
    id: `${base.projectId}-${base.parentId}-${base.entry.name}`,
    label: base.entry.name,
    position: base.position,
    type: base.entry.type === 'dir' ? 'folder' : 'file',
    shape: base.entry.type === 'dir' ? 'folder-icon' : 'document',
    size: base.size,
    parentId: base.parentId,
    tooltip: base.entry.type === 'dir'
      ? `Directory cluster member: ${base.entry.name}/`
      : `File cluster member: ${base.entry.name}`,
    color: accent,
    filePath: base.entry.type === 'file' ? `${base.rootPath.replace(/\\/g, '/')}/${base.entry.name}` : undefined,
    cluster: base.cluster,
    orbitLevel: base.orbitLevel,
    importance: 'tertiary',
    systemId: base.systemId,
    motionProfile: base.entry.type === 'dir' ? 'living' : 'static',
  };
}

const enginePositions = fanPositions([0, 0, 0], 3, 8.8, 1.75, Math.PI / 6);
const editionPositions = fanPositions([0, 0, 0], 3, 13.4, -0.82, Math.PI / 2);
const linkProjectPosition: [number, number, number] = [
  editionPositions[1][0] - 10.6,
  editionPositions[1][1],
  editionPositions[1][2],
];

function getLinkedSystemPosition(index: number, totalSystems: number): [number, number, number] {
  if (totalSystems <= 1) return linkProjectPosition;
  if (index === 0) return linkProjectPosition;

  const satelliteCount = Math.max(totalSystems - 1, 1);
  const orbitRadius = 10.2 + Math.max(0, totalSystems - 4) * 1.45;
  const satellites = fanPositions(
    [linkProjectPosition[0] - 6.6, linkProjectPosition[1], linkProjectPosition[2]],
    satelliteCount,
    orbitRadius,
    0.18,
    Math.PI / 8,
  );
  return satellites[Math.min(index - 1, satellites.length - 1)];
}

const coreScripts = [
  'crystalize.py',
  'audit_comparison.py',
  'setup_guardian.py',
  'sync_master.py',
  'fidelity_sync.py',
  'systemic_enrichment.py',
];

const rootDocs = [
  'README.md',
  'STATE.json',
  'HOW_TO_USE_DASHBOARD.md',
  'RELEASE_NOTES_MANIFEST.md',
  'HOW_TO_USE_IT.md',
  'CASE_STUDY_DRIFT.md',
  'BENCHMARKS.md',
  'PROJECT_CONTEXT.md',
];

const liteFiles = ['run_continuity_lite.py', 'STATE.json', 'PROJECT_CONTEXT.md', 'pyproject.toml'];
const proFiles = ['run_continuity_pro.py', 'STATE.json', 'PROJECT_CONTEXT.md', 'SECURITY.md', 'pyproject.toml'];
const omegaFiles = ['run_continuity_omega.py', 'PROJECT_CONTEXT.md', 'pyproject.toml'];

export function buildStaticGraph(lang: Language, linkedSystemCount = 0): { nodes: GraphNode[]; edges: GraphEdge[] } {
  const t = translations[lang];
  const nodes: GraphNode[] = [];
  const edges: GraphEdge[] = [];

  nodes.push({
    id: 'core',
    label: 'CONTINUITY LEGACY',
    position: [0, 0, 0],
    type: 'core',
    shape: 'octahedron',
    size: 1.95,
    parentId: null,
    tooltip: t['graph.core.tooltip'] || 'Central governance engine of the Ethernium ecosystem.',
    color: '#ffffff',
    orbitLevel: 0,
    importance: 'primary',
    systemId: null,
    motionProfile: 'sentinel-linked',
  });

  if (linkedSystemCount > 0) {
    nodes.push({
      id: 'imperium',
      label: 'IMPERIUM',
      position: [0, 0, 0],
      type: 'edition',
      shape: 'octahedron',
      size: 2.6,
      parentId: null,
      tooltip: t['graph.imperium.tooltip'] || 'Sovereign control node for linked systems.',
      color: '#f8fafc',
      orbitLevel: 0,
      importance: 'primary',
      systemId: null,
      motionProfile: 'sentinel-linked',
    });
  }

  const engines = [
    { id: 'crystallizer', label: 'CRYSTALLIZER', action: '/api/actions/crystallize', tooltip: t['graph.cryst.tooltip'] },
    { id: 'auditor', label: 'AUDITOR', action: '/api/actions/audit', tooltip: t['graph.audit.tooltip'] },
    { id: 'guardian', label: 'GUARDIAN', action: '/api/actions/seal', tooltip: t['graph.guard.tooltip'] },
  ];

  engines.forEach((eng, i) => {
    nodes.push({
      id: eng.id,
      label: eng.label,
      position: enginePositions[i],
      type: 'engine',
      shape: 'tetrahedron',
      size: 1.05,
      parentId: 'core',
      action: eng.action,
      tooltip: eng.tooltip,
      color: '#22d3ee',
      orbitLevel: 1,
      importance: 'secondary',
      systemId: null,
      motionProfile: 'living',
    });
    edges.push({ from: 'core', to: eng.id });
  });

  const scriptPositions = fanPositions(enginePositions[0], coreScripts.length, 5.15, 0.72, Math.PI / 7);
  coreScripts.forEach((script, i) => {
    const id = `script-${script}`;
    nodes.push({
      id,
      label: script,
      position: scriptPositions[i],
      type: 'file',
      shape: 'document',
      size: 0.4,
      parentId: 'crystallizer',
      tooltip: `Core engine script: ${script}`,
      color: '#67e8f9',
      filePath: `.github/scripts/${script}`,
      orbitLevel: 2,
      importance: 'tertiary',
      systemId: null,
      motionProfile: 'static',
    });
    edges.push({ from: 'crystallizer', to: id });
  });

  const docPositions = fanPositions([0, 0, 0], rootDocs.length, 8.5, -5.6, Math.PI / 9);
  rootDocs.forEach((doc, i) => {
    const id = `root-${doc}`;
    nodes.push({
      id,
      label: doc,
      position: docPositions[i],
      type: 'file',
      shape: 'document',
      size: doc === 'README.md' || doc === 'STATE.json' ? 0.48 : 0.34,
      parentId: 'core',
      tooltip: `Root document: ${doc}`,
      color: '#d4d4d8',
      filePath: doc,
      cluster: 'documents',
      orbitLevel: 2,
      importance: 'tertiary',
      systemId: null,
      motionProfile: 'static',
    });
    edges.push({ from: 'core', to: id });
  });

  const editionColors: Record<string, string> = { lite: '#4ade80', pro: '#fb923c', omega: '#a78bfa' };
  const editions = [
    { id: 'lite', label: 'LITE', files: liteFiles, dir: 'continuity-lite', tooltip: t['graph.lite.tooltip'] },
    { id: 'pro', label: 'PRO', files: proFiles, dir: 'continuity-pro', tooltip: t['graph.pro.tooltip'] },
    { id: 'omega', label: 'OMEGA', files: omegaFiles, dir: 'continuity-omega', tooltip: t['graph.omega.tooltip'] },
  ];

  editions.forEach((ed, i) => {
    const edColor = editionColors[ed.id];
    nodes.push({
      id: ed.id,
      label: ed.label,
      position: editionPositions[i],
      type: 'edition',
      shape: 'sphere',
      size: 1.18,
      parentId: 'core',
      tooltip: ed.tooltip,
      color: edColor,
      orbitLevel: 1,
      importance: 'secondary',
      systemId: null,
      motionProfile: 'living',
    });
    edges.push({ from: 'core', to: ed.id });

    const subPositions = fanPositions(editionPositions[i], ed.files.length, 4.35, -0.72, Math.PI / 7);
    ed.files.forEach((file, j) => {
      const fileId = `${ed.id}-${file}`;
      nodes.push({
        id: fileId,
        label: file,
        position: subPositions[j],
        type: 'file',
        shape: 'document',
        size: 0.34,
        parentId: ed.id,
        tooltip: `${ed.label} module file: ${file}`,
        color: edColor,
        filePath: `${ed.dir}/${file}`,
        orbitLevel: 2,
        importance: 'tertiary',
        systemId: null,
        motionProfile: 'static',
      });
      edges.push({ from: ed.id, to: fileId });
    });
  });

  nodes.push({
    id: 'link-placeholder',
    label: t['graph.link.label'] || 'LINK PROJECT',
    position: getLinkedSystemPosition(linkedSystemCount, linkedSystemCount + 1),
    type: 'link-placeholder',
    shape: 'sphere',
    size: 0.92,
    parentId: null,
    tooltip: t['graph.link.tooltip'] || 'Click to link an external project directory.',
    color: '#64748b',
    cluster: 'linked-root',
    orbitLevel: 1,
    importance: 'secondary',
    systemId: null,
    motionProfile: 'living',
  });

  return { nodes, edges };
}

export function buildProjectNodes(
  system: LinkedSystem,
  lang: Language,
  slotIndex = 0,
  totalSystems = 1,
): { nodes: GraphNode[]; edges: GraphEdge[] } {
  const t = translations[lang];
  const nodes: GraphNode[] = [];
  const edges: GraphEdge[] = [];

  const projectCenter = getLinkedSystemPosition(slotIndex, totalSystems);
  const projectId = `project-${system.id}`;
  const entries = system.entries;

  nodes.push({
    id: projectId,
    label: system.name.toUpperCase(),
    position: projectCenter,
    type: 'module',
    shape: 'sphere',
    size: 1.34,
    parentId: 'core',
    tooltip: `Linked project: ${system.name}`,
    color: GRAPH_CLUSTER_CONFIG['linked-root'].color,
    cluster: 'linked-root',
    orbitLevel: 1,
    importance: 'primary',
    systemId: system.id,
    motionProfile: 'sentinel-linked',
  });
  edges.push({ from: 'core', to: projectId });

  const buckets: Record<Exclude<NodeCluster, 'linked-root'>, ScannedEntry[]> = {
    dashboard: [],
    agents: [],
    documents: [],
    tools: [],
    system: [],
  };

  entries.forEach((entry) => {
    buckets[classifyEntry(entry)].push(entry);
  });

  const nonEmptyBuckets = CLUSTER_ORDER.filter((cluster) => buckets[cluster].length > 0).length;
  const adaptiveRings = entries.length >= 8 && nonEmptyBuckets >= 3;

  if (!adaptiveRings) {
    const childRadius = Math.max(7.1, 6.8 + Math.min(entries.length, 10) * 0.22);
    const childPositions = fanPositions(projectCenter, entries.length, childRadius, 0.18, Math.PI / 8);

    entries.forEach((entry, i) => {
      const cluster = classifyEntry(entry);
      const node = buildEntryNode({
        projectId,
        systemId: system.id,
        rootPath: system.rootPath,
        parentId: projectId,
        entry,
        position: childPositions[i],
        cluster,
        size: entry.type === 'dir' ? 0.54 : 0.36,
        orbitLevel: 1,
      });
      nodes.push(node);
      edges.push({ from: projectId, to: node.id });
    });

    return { nodes, edges };
  }

    const clusterPositions = fanPositions(projectCenter, CLUSTER_ORDER.length, 7.85, 0.22, Math.PI / 1.92);

  CLUSTER_ORDER.forEach((cluster, clusterIndex) => {
    const bucket = buckets[cluster];
    const config = GRAPH_CLUSTER_CONFIG[cluster];
    const translatedLabel = t[`graph.cluster.${cluster}`] || config.label;
    const translatedTooltip = t[`graph.cluster.${cluster}.tooltip`] || config.tooltip;
    const clusterId = `${projectId}-${cluster}`;
    const clusterHasPayload = bucket.length > 0;

    nodes.push({
      id: clusterId,
      label: translatedLabel,
      position: clusterPositions[clusterIndex],
      type: 'module',
      shape: 'sphere',
      size: clusterHasPayload ? 0.84 : 0.62,
      parentId: projectId,
      tooltip: clusterHasPayload ? `${translatedTooltip} [${bucket.length}]` : translatedTooltip,
      color: clusterHasPayload ? config.color : '#475569',
      cluster,
      orbitLevel: 2,
      importance: 'secondary',
      systemId: system.id,
      motionProfile: clusterHasPayload ? 'living' : 'static',
    });
    edges.push({ from: projectId, to: clusterId });

    if (!clusterHasPayload) return;

    const miniRadius = Math.max(3.55, 3.1 + Math.min(bucket.length, 8) * 0.24);
    const childPositions = fanPositions(
      clusterPositions[clusterIndex],
      bucket.length,
      miniRadius,
      -0.2,
      Math.PI / 6 + clusterIndex * 0.24,
    );

    bucket.forEach((entry, entryIndex) => {
      const node = buildEntryNode({
        projectId,
        systemId: system.id,
        rootPath: system.rootPath,
        parentId: clusterId,
        entry,
        position: childPositions[entryIndex],
        cluster,
        size: entry.type === 'dir' ? 0.48 : 0.34,
        orbitLevel: 3,
      });
      nodes.push(node);
      edges.push({ from: clusterId, to: node.id });
    });
  });

  return { nodes, edges };
}
