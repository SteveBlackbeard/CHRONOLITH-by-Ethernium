// Graph Data Model for the Nexus Constellation
// Defines all nodes and their relationships in the Ethernium ecosystem
import { Language, translations } from './i18n';

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
  filePath?: string; // relative path for reading file content
}

export interface GraphEdge {
  from: string;
  to: string;
}

// Helper: distribute children around a parent in 3D
function fanPositions(
  center: [number, number, number],
  count: number,
  radius: number,
  yOffset: number = 0,
  startAngle: number = 0
): [number, number, number][] {
  const positions: [number, number, number][] = [];
  for (let i = 0; i < count; i++) {
    const angle = startAngle + (i / count) * Math.PI * 2;
    positions.push([
      center[0] + Math.cos(angle) * radius,
      center[1] + yOffset,
      center[2] + Math.sin(angle) * radius,
    ]);
  }
  return positions;
}

// ═══════════════════════════════════════════════════════════
// STATIC CONSTELLATION: Always visible
// ═══════════════════════════════════════════════════════════

const enginePositions = fanPositions([0, 0, 0], 3, 4.5, 1.5, Math.PI / 6);
const editionPositions = fanPositions([0, 0, 0], 3, 7, -0.5, Math.PI / 2);

// Core scripts sub-files
const coreScripts = [
  'crystalize.py', 'audit_comparison.py', 'setup_guardian.py',
  'sync_master.py', 'fidelity_sync.py', 'systemic_enrichment.py'
];

// Root documents
const rootDocs = [
  'README.md', 'STATE.json', 'HOW_TO_USE_DASHBOARD.md',
  'RELEASE_NOTES_MANIFEST.md', 'HOW_TO_USE_IT.md',
  'CASE_STUDY_DRIFT.md', 'BENCHMARKS.md', 'PROJECT_CONTEXT.md'
];

// Edition sub-files
const liteFiles = ['run_continuity_lite.py', 'STATE.json', 'PROJECT_CONTEXT.md', 'pyproject.toml'];
const proFiles = ['run_continuity_pro.py', 'STATE.json', 'PROJECT_CONTEXT.md', 'SECURITY.md', 'pyproject.toml'];
const omegaFiles = ['run_continuity_omega.py', 'PROJECT_CONTEXT.md', 'pyproject.toml'];

export function buildStaticGraph(lang: Language): { nodes: GraphNode[]; edges: GraphEdge[] } {
  const t = translations[lang];
  const nodes: GraphNode[] = [];
  const edges: GraphEdge[] = [];

  // ─── CORE ───
  nodes.push({
    id: 'core',
    label: 'CONTINUITY LEGACY',
    position: [0, 0, 0],
    type: 'core',
    shape: 'octahedron',
    size: 1.8,
    parentId: null,
    tooltip: t['graph.core.tooltip'] || 'Central governance engine of the Ethernium ecosystem.',
    color: '#ffffff',
  });

  // ─── ENGINES ───
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
      size: 1.0,
      parentId: 'core',
      action: eng.action,
      tooltip: eng.tooltip,
      color: '#22d3ee', // cyan for engines
    });
    edges.push({ from: 'core', to: eng.id });
  });

  // ─── CORE SCRIPTS (fan around crystallizer) ───
  const scriptPositions = fanPositions(enginePositions[0], coreScripts.length, 2.5, 0.5);
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
      color: '#67e8f9', // light cyan
      filePath: `.github/scripts/${script}`,
    });
    edges.push({ from: 'crystallizer', to: id });
  });

  // ─── ROOT DOCUMENTS (fan around core, lower ring) ───
  const docPositions = fanPositions([0, 0, 0], rootDocs.length, 3, -2.5);
  rootDocs.forEach((doc, i) => {
    const id = `root-${doc}`;
    nodes.push({
      id,
      label: doc,
      position: docPositions[i],
      type: 'file',
      shape: 'document',
      size: doc === 'README.md' || doc === 'STATE.json' ? 0.5 : 0.35,
      parentId: 'core',
      tooltip: `Root document: ${doc}`,
      color: '#d4d4d8', // warm grey for docs
      filePath: doc,
    });
    edges.push({ from: 'core', to: id });
  });

  // ─── EDITIONS ───
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
      size: 1.2,
      parentId: 'core',
      tooltip: ed.tooltip,
      color: edColor,
    });
    edges.push({ from: 'core', to: ed.id });

    // Sub-files for each edition
    const subPositions = fanPositions(editionPositions[i], ed.files.length, 2, -0.5);
    ed.files.forEach((file, j) => {
      const fileId = `${ed.id}-${file}`;
      nodes.push({
        id: fileId,
        label: file,
        position: subPositions[j],
        type: 'file',
        shape: 'document',
        size: 0.35,
        parentId: ed.id,
        tooltip: `${ed.label} module file: ${file}`,
        color: edColor,
        filePath: `${ed.dir}/${file}`,
      });
      edges.push({ from: ed.id, to: fileId });
    });
  });

  // ─── LINK PLACEHOLDER ───
  nodes.push({
    id: 'link-placeholder',
    label: t['graph.link.label'] || 'LINK PROJECT',
    position: [0, 5, -4],
    type: 'link-placeholder',
    shape: 'sphere',
    size: 0.8,
    parentId: null,
    tooltip: t['graph.link.tooltip'] || 'Click to link an external project directory.',
    color: '#333333',
  });

  return { nodes, edges };
}

// ═══════════════════════════════════════════════════════════
// DYNAMIC NODES: Generated when a project is linked
// ═══════════════════════════════════════════════════════════

export interface ScannedEntry {
  name: string;
  type: 'file' | 'dir';
  size?: number;
}

export function buildProjectNodes(
  projectName: string,
  entries: ScannedEntry[],
  lang: Language
): { nodes: GraphNode[]; edges: GraphEdge[] } {
  const t = translations[lang];
  const nodes: GraphNode[] = [];
  const edges: GraphEdge[] = [];

  const projectCenter: [number, number, number] = [0, 5, -4];
  const projectId = `project-${projectName}`;

  // Replace the placeholder with the real project node
  nodes.push({
    id: projectId,
    label: projectName.toUpperCase(),
    position: projectCenter,
    type: 'module',
    shape: 'sphere',
    size: 1.2,
    parentId: 'core',
    tooltip: `Linked project: ${projectName}`,
    color: '#ffffff',
  });
  edges.push({ from: 'core', to: projectId });

  // Fan children around the project node
  const childPositions = fanPositions(projectCenter, entries.length, 3, 0);
  entries.forEach((entry, i) => {
    const entryId = `${projectId}-${entry.name}`;
    nodes.push({
      id: entryId,
      label: entry.name,
      position: childPositions[i],
      type: entry.type === 'dir' ? 'folder' : 'file',
      shape: entry.type === 'dir' ? 'folder-icon' : 'document',
      size: entry.type === 'dir' ? 0.5 : 0.35,
      parentId: projectId,
      tooltip: entry.type === 'dir' ? `Directory: ${entry.name}/` : `File: ${entry.name}`,
    });
    edges.push({ from: projectId, to: entryId });
  });

  return { nodes, edges };
}
