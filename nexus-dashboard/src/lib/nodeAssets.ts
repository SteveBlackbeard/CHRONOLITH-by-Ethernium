import { GraphNode } from './graphData';

export type NodeAssetFamily =
  | 'core'
  | 'engine'
  | 'edition'
  | 'module'
  | 'document'
  | 'folder'
  | 'link-placeholder'
  | 'sentinel';
export type CanonicalAssetTarget =
  | 'core'
  | 'lite'
  | 'pro'
  | 'omega'
  | 'crystallizer'
  | 'auditor'
  | 'guardian'
  | 'linked-root'
  | 'sentinel';

export interface NodeAssetStage {
  enabled: boolean;
  src: string;
  scale?: number;
  offset?: [number, number, number];
  rotation?: [number, number, number];
  normalizationMode?: 'spatial' | 'planar';
  anchorMode?: 'origin' | 'mass';
  animatedMaterial?: boolean;
  autoplay?: boolean;
  animationClip?: string | '__auto';
  opacity?: number;
  label?: string;
}

export interface NodeAssetProfile {
  family: NodeAssetFamily;
  appearance: NodeAssetStage;
  effect?: NodeAssetStage;
  preserveFallback?: boolean;
  tintStrength?: number;
}

export type NodeAssetSource = 'fallback' | 'family' | 'override';
type NodeAssetStageOverrideLike = Partial<NodeAssetStage> & { src: string; enabled?: boolean };
type CanonicalNodeAssetOverride = {
  appearance?: NodeAssetStageOverrideLike;
  effect?: NodeAssetStageOverrideLike;
  preserveFallback?: boolean;
  tintStrength?: number;
} | null;
export type NodeAssetFamilyProfileOverride = Partial<Omit<NodeAssetProfile, 'family'>> & {
  appearance?: Partial<NodeAssetStage>;
  effect?: Partial<NodeAssetStage>;
};
export type NodeAssetFamilyOverrides = Partial<Record<NodeAssetFamily, NodeAssetFamilyProfileOverride>>;

export const CANONICAL_ASSET_FILES: Record<CanonicalAssetTarget, string> = {
  core: '/assets/nodes/core/Core0.glb',
  lite: '/assets/nodes/edition/lite/Core1.glb',
  pro: '/assets/nodes/edition/pro/Core2.glb',
  omega: '/assets/nodes/edition/omega/Core3.glb',
  crystallizer: '/assets/nodes/engine/crystallizer/Coreconnection.glb',
  auditor: '/assets/nodes/engine/auditor/Coreconnection.glb',
  guardian: '/assets/nodes/engine/guardian/Coreconnection.glb',
  'linked-root': '/assets/nodes/linked-root/Corerealconnection.glb',
  sentinel: '/assets/nodes/sentinel/sentinels.glb',
};

const CANONICAL_ASSET_STAGE_OVERRIDES: Record<CanonicalAssetTarget, Partial<NodeAssetStage>> = {
  core: {
    scale: 1.1,
    offset: [0, 0, 0],
    rotation: [0.44, 0.2, 0],
    normalizationMode: 'spatial',
    anchorMode: 'origin',
  },
  lite: {
    scale: 1.04,
    offset: [0, 0, 0],
    rotation: [0, 0, 0],
    normalizationMode: 'planar',
    anchorMode: 'origin',
  },
  pro: {
    scale: 1.04,
    offset: [0, 0, 0],
    rotation: [0, 0, 0],
    normalizationMode: 'planar',
    anchorMode: 'origin',
  },
  omega: {
    scale: 1.04,
    offset: [0, 0, 0],
    rotation: [0, 0, 0],
    normalizationMode: 'planar',
    anchorMode: 'origin',
  },
  crystallizer: {
    scale: 1.12,
    offset: [0, 0, 0],
    rotation: [0, 0, 0],
    normalizationMode: 'planar',
    anchorMode: 'origin',
  },
  auditor: {
    scale: 1.12,
    offset: [0, 0, 0],
    rotation: [0, 0, 0],
    normalizationMode: 'planar',
    anchorMode: 'origin',
  },
  guardian: {
    scale: 1.12,
    offset: [0, 0, 0],
    rotation: [0, 0, 0],
    normalizationMode: 'planar',
    anchorMode: 'origin',
  },
  'linked-root': {
    scale: 1.08,
    offset: [0, 0, 0],
    rotation: [0, 0, 0],
    normalizationMode: 'planar',
    anchorMode: 'origin',
  },
  sentinel: {
    scale: 1.18,
    offset: [0, 0, 0],
    rotation: [0, 0, 0],
    normalizationMode: 'planar',
    anchorMode: 'origin',
  },
};

const DEFAULT_ASSET_OPTIONS = {
  enabled: false,
  scale: 1,
  offset: [0, 0, 0] as [number, number, number],
  rotation: [0, 0, 0] as [number, number, number],
  animatedMaterial: false,
  autoplay: true,
  opacity: 1,
};

export const NODE_ASSET_PROFILES: Record<NodeAssetFamily, NodeAssetProfile> = {
  core: {
    family: 'core',
    appearance: { ...DEFAULT_ASSET_OPTIONS, src: '/assets/nodes/core/core_appearance.glb' },
    effect: { ...DEFAULT_ASSET_OPTIONS, src: '/assets/nodes/core/core_effect.glb', opacity: 0.82 },
    preserveFallback: false,
    tintStrength: 0,
  },
  engine: {
    family: 'engine',
    appearance: { ...DEFAULT_ASSET_OPTIONS, src: '/assets/nodes/engine/engine_appearance.glb' },
    effect: { ...DEFAULT_ASSET_OPTIONS, src: '/assets/nodes/engine/engine_effect.glb', opacity: 0.76 },
    preserveFallback: false,
    tintStrength: 0,
  },
  edition: {
    family: 'edition',
    appearance: { ...DEFAULT_ASSET_OPTIONS, src: '/assets/nodes/edition/edition_appearance.glb' },
    effect: { ...DEFAULT_ASSET_OPTIONS, src: '/assets/nodes/edition/edition_effect.glb', opacity: 0.72 },
    preserveFallback: false,
    tintStrength: 0,
  },
  module: {
    family: 'module',
    appearance: { ...DEFAULT_ASSET_OPTIONS, src: '/assets/nodes/module/module_appearance.glb' },
    effect: { ...DEFAULT_ASSET_OPTIONS, src: '/assets/nodes/module/module_effect.glb', opacity: 0.7 },
    preserveFallback: false,
    tintStrength: 0,
  },
  document: {
    family: 'document',
    appearance: { ...DEFAULT_ASSET_OPTIONS, src: '/assets/nodes/document/document_appearance.glb' },
    effect: { ...DEFAULT_ASSET_OPTIONS, src: '/assets/nodes/document/document_effect.glb', opacity: 0.64 },
    preserveFallback: false,
    tintStrength: 0,
  },
  folder: {
    family: 'folder',
    appearance: { ...DEFAULT_ASSET_OPTIONS, src: '/assets/nodes/folder/folder_appearance.glb' },
    effect: { ...DEFAULT_ASSET_OPTIONS, src: '/assets/nodes/folder/folder_effect.glb', opacity: 0.62 },
    preserveFallback: false,
    tintStrength: 0,
  },
  'link-placeholder': {
    family: 'link-placeholder',
    appearance: { ...DEFAULT_ASSET_OPTIONS, src: '/assets/nodes/link-placeholder/link_placeholder_appearance.glb' },
    effect: { ...DEFAULT_ASSET_OPTIONS, src: '/assets/nodes/link-placeholder/link_placeholder_effect.glb', opacity: 0.46 },
    preserveFallback: false,
    tintStrength: 0,
  },
  sentinel: {
    family: 'sentinel',
    appearance: {
      ...DEFAULT_ASSET_OPTIONS,
      src: '/assets/nodes/sentinel/sentinels.glb',
      enabled: true,
      scale: 0.9,
      rotation: [0, 0, 0],
      normalizationMode: 'planar',
      anchorMode: 'origin',
      label: 'sentinels.glb',
    },
    preserveFallback: false,
    tintStrength: 0,
  },
};

function createCanonicalStage(target: CanonicalAssetTarget, src: string, label: string): NodeAssetStageOverrideLike {
  return {
    ...DEFAULT_ASSET_OPTIONS,
    ...CANONICAL_ASSET_STAGE_OVERRIDES[target],
    src,
    enabled: true,
    label,
  };
}

export function resolveCanonicalAssetTarget(node: GraphNode): CanonicalAssetTarget | null {
  if (node.id === 'core') return 'core';
  if (node.id === 'lite') return 'lite';
  if (node.id === 'pro') return 'pro';
  if (node.id === 'omega') return 'omega';
  if (node.id === 'crystallizer') return 'crystallizer';
  if (node.id === 'auditor') return 'auditor';
  if (node.id === 'guardian') return 'guardian';
  if (node.cluster === 'linked-root' && node.type === 'module') return 'linked-root';
  return null;
}

function getCanonicalNodeAssetOverride(node: GraphNode): CanonicalNodeAssetOverride {
  const canonicalTarget = resolveCanonicalAssetTarget(node);
  if (canonicalTarget) {
    return {
      appearance: createCanonicalStage(
        canonicalTarget,
        CANONICAL_ASSET_FILES[canonicalTarget],
        CANONICAL_ASSET_FILES[canonicalTarget].split('/').pop() || `${canonicalTarget}.glb`,
      ),
      preserveFallback: false,
      tintStrength: 0,
    };
  }

  return null;
}

export function getNodeAssetFamily(node: GraphNode): NodeAssetFamily {
  if (node.type === 'link-placeholder') return 'link-placeholder';
  if (node.type === 'core') return 'core';
  if (node.type === 'engine') return 'engine';
  if (node.type === 'edition') return 'edition';
  if (node.type === 'module') return 'module';
  if (node.type === 'folder') return 'folder';
  return 'document';
}

export function getSentinelAssetProfile(familyOverrides?: NodeAssetFamilyOverrides) {
  return getFamilyAssetProfile('sentinel', familyOverrides);
}

export function getCanonicalNodeAssetProfile(node: GraphNode): CanonicalNodeAssetOverride {
  return getCanonicalNodeAssetOverride(node);
}

export function nodeHasCanonicalAsset(node: GraphNode) {
  const canonicalOverride = getCanonicalNodeAssetOverride(node);
  return Boolean(canonicalOverride?.appearance?.src || canonicalOverride?.effect?.src);
}

function mergeStage(
  stage: NodeAssetStage,
  overrideStage?: (Partial<NodeAssetStage> & { src?: string; enabled?: boolean }) | null,
) {
  if (!overrideStage) return stage;
  return {
    ...stage,
    ...overrideStage,
    src: overrideStage.src || stage.src,
    enabled: overrideStage.enabled ?? stage.enabled,
  } satisfies NodeAssetStage;
}

export function getFamilyAssetProfile(
  family: NodeAssetFamily,
  familyOverrides?: NodeAssetFamilyOverrides,
) {
  const baseProfile = NODE_ASSET_PROFILES[family];
  const familyOverride = familyOverrides?.[family];
  return {
    ...baseProfile,
    ...familyOverride,
    appearance: mergeStage(baseProfile.appearance, familyOverride?.appearance),
    effect: baseProfile.effect
      ? mergeStage(baseProfile.effect, familyOverride?.effect)
      : familyOverride?.effect && familyOverride.effect.src
      ? mergeStage({ ...DEFAULT_ASSET_OPTIONS, src: familyOverride.effect.src }, familyOverride.effect)
      : baseProfile.effect,
  } satisfies NodeAssetProfile;
}

export function getNodeAssetProfile(node: GraphNode, familyOverrides?: NodeAssetFamilyOverrides) {
  const baseProfile = getFamilyAssetProfile(getNodeAssetFamily(node), familyOverrides);
  const canonicalOverride = getCanonicalNodeAssetOverride(node);
  const override = node.assetOverride;
  const canonicalAppearance = canonicalOverride?.appearance?.src
    ? mergeStage(baseProfile.appearance, canonicalOverride.appearance)
    : baseProfile.appearance;
  const canonicalEffect = canonicalOverride?.effect
    ? mergeStage(
        baseProfile.effect || { ...DEFAULT_ASSET_OPTIONS, src: canonicalOverride.effect.src },
        canonicalOverride.effect,
      )
    : baseProfile.effect;
  const effectiveAppearanceBase = canonicalAppearance;
  const effectiveEffectBase = canonicalEffect;

  const nextAppearance = override?.appearance?.src
    ? mergeStage(effectiveAppearanceBase, { ...override.appearance, enabled: override.appearance.enabled ?? true })
    : mergeStage(effectiveAppearanceBase, override?.appearance);
  const nextEffect = override?.effect?.src
    ? mergeStage(
        effectiveEffectBase || { ...DEFAULT_ASSET_OPTIONS, src: override.effect.src },
        { ...override.effect, enabled: override.effect.enabled ?? true },
      )
    : effectiveEffectBase;

  return {
    ...baseProfile,
    appearance: nextAppearance,
    effect: nextEffect,
    preserveFallback: canonicalOverride?.preserveFallback ?? baseProfile.preserveFallback,
    tintStrength: canonicalOverride?.tintStrength ?? baseProfile.tintStrength,
  };
}

export function getNodeAssetSource(node: GraphNode, familyOverrides?: NodeAssetFamilyOverrides): NodeAssetSource {
  if (node.assetOverride?.appearance?.src || node.assetOverride?.effect?.src) {
    return 'override';
  }
  const canonicalOverride = getCanonicalNodeAssetOverride(node);
  if (canonicalOverride?.appearance?.enabled || canonicalOverride?.effect?.enabled) {
    return 'family';
  }
  const familyProfile = getFamilyAssetProfile(getNodeAssetFamily(node), familyOverrides);
  if (familyProfile.appearance.enabled || familyProfile.effect?.enabled) {
    return 'family';
  }
  return 'fallback';
}

export function nodeUsesExternalAsset(node: GraphNode, familyOverrides?: NodeAssetFamilyOverrides) {
  const profile = getNodeAssetProfile(node, familyOverrides);
  return Boolean(profile.appearance.enabled || profile.effect?.enabled);
}
