import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import { join, extname } from 'path';
import { GraphNodeAssetOverride } from '@/lib/graphData';
import { CANONICAL_ASSET_FILES, CanonicalAssetTarget, NodeAssetFamily, NodeAssetFamilyOverrides } from '@/lib/nodeAssets';

export const runtime = 'nodejs';

type OverrideManifest = Record<string, GraphNodeAssetOverride>;
type FamilyManifest = NodeAssetFamilyOverrides;

const configDir = join(process.cwd(), 'config');
const manifestPath = join(configDir, 'node-asset-overrides.json');
const familyManifestPath = join(configDir, 'node-asset-family-overrides.json');
const overrideAssetDir = join(process.cwd(), 'public', 'assets', 'nodes', 'overrides');
const publicDir = join(process.cwd(), 'public');
const CANONICAL_TARGET_NODE_IDS: Partial<Record<CanonicalAssetTarget, string>> = {
  core: 'core',
  lite: 'lite',
  pro: 'pro',
  omega: 'omega',
  crystallizer: 'crystallizer',
  auditor: 'auditor',
  guardian: 'guardian',
};

async function ensureStorage() {
  await fs.mkdir(configDir, { recursive: true });
  await fs.mkdir(overrideAssetDir, { recursive: true });
}

async function loadOverrides(): Promise<OverrideManifest> {
  await ensureStorage();
  try {
    const raw = await fs.readFile(manifestPath, 'utf-8');
    return JSON.parse(raw) as OverrideManifest;
  } catch {
    return {};
  }
}

async function saveOverrides(overrides: OverrideManifest) {
  await ensureStorage();
  await fs.writeFile(manifestPath, JSON.stringify(overrides, null, 2), 'utf-8');
}

async function loadFamilyProfiles(): Promise<FamilyManifest> {
  await ensureStorage();
  try {
    const raw = await fs.readFile(familyManifestPath, 'utf-8');
    return JSON.parse(raw) as FamilyManifest;
  } catch {
    return {};
  }
}

async function saveFamilyProfiles(familyProfiles: FamilyManifest) {
  await ensureStorage();
  await fs.writeFile(familyManifestPath, JSON.stringify(familyProfiles, null, 2), 'utf-8');
}

function normalizeNodeId(nodeId: string) {
  return nodeId.toLowerCase().replace(/[^a-z0-9-_]+/g, '-').replace(/(^-|-$)/g, '') || 'node';
}

function toRuntimePath(fileName: string) {
  return `/api/node-assets/file/${encodeURIComponent(fileName)}`;
}

function extractManagedFileName(pathValue?: string | null) {
  if (!pathValue) return null;
  if (pathValue.startsWith('/assets/nodes/overrides/')) {
    return pathValue.slice('/assets/nodes/overrides/'.length);
  }
  if (pathValue.startsWith('/api/node-assets/file/')) {
    return decodeURIComponent(pathValue.slice('/api/node-assets/file/'.length));
  }
  return null;
}

function toAbsolutePath(fileName: string) {
  return join(overrideAssetDir, fileName);
}

function toPublicAbsolutePath(publicPath: string) {
  return join(publicDir, ...publicPath.replace(/^\/+/, '').split('/'));
}

function normalizeOverrides(overrides: OverrideManifest): OverrideManifest {
  return Object.fromEntries(
    Object.entries(overrides).map(([nodeId, override]) => [
      nodeId,
      {
        ...override,
        appearance: override.appearance
          ? {
              ...override.appearance,
              src: extractManagedFileName(override.appearance.src)
                ? toRuntimePath(extractManagedFileName(override.appearance.src)!)
                : override.appearance.src,
            }
          : override.appearance,
        effect: override.effect
          ? {
              ...override.effect,
              src: extractManagedFileName(override.effect.src)
                ? toRuntimePath(extractManagedFileName(override.effect.src)!)
                : override.effect.src,
            }
          : override.effect,
      } satisfies GraphNodeAssetOverride,
    ]),
  );
}

function normalizeFamilyProfiles(familyProfiles: FamilyManifest): FamilyManifest {
  return Object.fromEntries(
    Object.entries(familyProfiles).map(([family, profile]) => [
      family,
      {
        ...profile,
        appearance: profile?.appearance
          ? {
              ...profile.appearance,
              src: extractManagedFileName(profile.appearance.src)
                ? toRuntimePath(extractManagedFileName(profile.appearance.src)!)
                : profile.appearance.src,
            }
          : profile?.appearance,
        effect: profile?.effect
          ? {
              ...profile.effect,
              src: extractManagedFileName(profile.effect.src)
                ? toRuntimePath(extractManagedFileName(profile.effect.src)!)
                : profile.effect.src,
            }
          : profile?.effect,
      },
    ]),
  ) as FamilyManifest;
}

async function safeRemoveIfManaged(publicPath?: string | null) {
  const fileName = extractManagedFileName(publicPath);
  if (!fileName) return;
  try {
    await fs.unlink(toAbsolutePath(fileName));
  } catch {}
}

async function processCanonicalAssets() {
  const overrides = await loadOverrides();
  const familyProfiles = await loadFamilyProfiles();
  const processedTargets: CanonicalAssetTarget[] = [];
  const missingTargets: CanonicalAssetTarget[] = [];
  const clearedNodeIds: string[] = [];

  for (const [target, publicPath] of Object.entries(CANONICAL_ASSET_FILES) as [CanonicalAssetTarget, string][]) {
    try {
      await fs.access(toPublicAbsolutePath(publicPath));
      processedTargets.push(target);

      const nodeId = CANONICAL_TARGET_NODE_IDS[target];
      if (nodeId && overrides[nodeId]) {
        await safeRemoveIfManaged(overrides[nodeId]?.appearance?.src);
        await safeRemoveIfManaged(overrides[nodeId]?.effect?.src);
        delete overrides[nodeId];
        clearedNodeIds.push(nodeId);
      }
    } catch {
      missingTargets.push(target);
    }
  }

  await saveOverrides(overrides);

  return {
    success: true,
    overrides: normalizeOverrides(overrides),
    familyProfiles: normalizeFamilyProfiles(familyProfiles),
    processedTargets,
    missingTargets,
    clearedNodeIds,
  };
}

export async function GET() {
  const overrides = await loadOverrides();
  const familyProfiles = await loadFamilyProfiles();
  return NextResponse.json({
    success: true,
    overrides: normalizeOverrides(overrides),
    familyProfiles: normalizeFamilyProfiles(familyProfiles),
  });
}

export async function POST(request: Request) {
  try {
    await ensureStorage();
    const contentType = request.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      const payload = await request.json().catch(() => ({}));
      if (payload?.action === 'process-canonical-assets') {
        return NextResponse.json(await processCanonicalAssets());
      }
      return NextResponse.json({ success: false, error: 'Unsupported node asset operation' }, { status: 400 });
    }

    const formData = await request.formData();
    const file = formData.get('file');
    const nodeId = String(formData.get('nodeId') || '').trim();
    const family = String(formData.get('family') || '').trim() as NodeAssetFamily;
    const slot = String(formData.get('slot') || '').trim();
    const label = String(formData.get('label') || '').trim();

    if (!(file instanceof File)) {
      return NextResponse.json({ success: false, error: 'No asset file provided' }, { status: 400 });
    }
    if ((slot !== 'appearance' && slot !== 'effect') || (!nodeId && !family)) {
      return NextResponse.json({ success: false, error: 'Invalid asset target' }, { status: 400 });
    }

    const ext = extname(file.name || '').toLowerCase();
    if (!['.glb', '.gltf'].includes(ext)) {
      return NextResponse.json({ success: false, error: 'Unsupported asset type' }, { status: 400 });
    }

    const overrides = await loadOverrides();
    const familyProfiles = await loadFamilyProfiles();
    const targetKey = family || nodeId;
    const safeId = normalizeNodeId(targetKey);
    const fileName = `${safeId}-${slot}-${Date.now().toString(36)}${ext}`;
    const buffer = Buffer.from(await file.arrayBuffer());
    const absPath = join(overrideAssetDir, fileName);
    await fs.writeFile(absPath, buffer);

    const previous = family
      ? familyProfiles[family]?.[slot]
      : overrides[nodeId]?.[slot as 'appearance' | 'effect'];
    await safeRemoveIfManaged(previous?.src);

    if (family) {
      familyProfiles[family] = {
        ...familyProfiles[family],
        [slot]: {
          ...(familyProfiles[family]?.[slot] || {}),
          src: toRuntimePath(fileName),
          enabled: true,
          autoplay: true,
          animatedMaterial: slot === 'effect',
          opacity: slot === 'effect' ? 0.78 : 1,
          label: label || file.name,
        },
      };
      await saveFamilyProfiles(familyProfiles);
    } else {
      overrides[nodeId] = {
        ...overrides[nodeId],
        [slot]: {
          src: toRuntimePath(fileName),
          enabled: true,
          autoplay: true,
          animatedMaterial: slot === 'effect',
          opacity: slot === 'effect' ? 0.78 : 1,
          label: label || file.name,
        },
      };
      await saveOverrides(overrides);
    }

    return NextResponse.json({
      success: true,
      overrides: normalizeOverrides(overrides),
      familyProfiles: normalizeFamilyProfiles(familyProfiles),
      nodeId,
      family: family || null,
      slot,
      src: toRuntimePath(fileName),
    });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error?.message || 'ASSET_PERSIST_ERROR' }, { status: 500 });
  }
}

export async function PATCH(request: Request) {
  try {
    const payload = await request.json().catch(() => ({}));
    const nodeId = String(payload?.nodeId || '').trim();
    const family = String(payload?.family || '').trim() as NodeAssetFamily;
    const slot = String(payload?.slot || '').trim() as 'appearance' | 'effect';
    const settings = payload?.settings;

    if (nodeId) {
      if (slot !== 'appearance' && slot !== 'effect') {
        return NextResponse.json({ success: false, error: 'Invalid slot' }, { status: 400 });
      }
      if (!settings || typeof settings !== 'object') {
        return NextResponse.json({ success: false, error: 'Missing settings' }, { status: 400 });
      }

      const overrides = await loadOverrides();
      const previousStage = overrides[nodeId]?.[slot];
      if (!previousStage?.src) {
        return NextResponse.json({ success: false, error: 'Node asset override not found' }, { status: 404 });
      }

      overrides[nodeId] = {
        ...overrides[nodeId],
        [slot]: {
          ...previousStage,
          ...settings,
          src: previousStage.src,
        },
      };

      await saveOverrides(overrides);
      const familyProfiles = await loadFamilyProfiles();
      return NextResponse.json({
        success: true,
        overrides: normalizeOverrides(overrides),
        familyProfiles: normalizeFamilyProfiles(familyProfiles),
        nodeId,
        slot,
      });
    }

    if (!family || !['core', 'engine', 'edition', 'module', 'document', 'folder', 'link-placeholder', 'sentinel'].includes(family)) {
      return NextResponse.json({ success: false, error: 'Invalid family' }, { status: 400 });
    }
    if (slot !== 'appearance' && slot !== 'effect') {
      return NextResponse.json({ success: false, error: 'Invalid slot' }, { status: 400 });
    }
    if (!settings || typeof settings !== 'object') {
      return NextResponse.json({ success: false, error: 'Missing settings' }, { status: 400 });
    }

    const familyProfiles = await loadFamilyProfiles();
    familyProfiles[family] = {
      ...familyProfiles[family],
      [slot]: {
        ...(familyProfiles[family]?.[slot] || {}),
        ...settings,
      },
    };
    await saveFamilyProfiles(familyProfiles);
    const overrides = await loadOverrides();
    return NextResponse.json({
      success: true,
      overrides: normalizeOverrides(overrides),
      familyProfiles: normalizeFamilyProfiles(familyProfiles),
      family,
      slot,
    });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error?.message || 'ASSET_FAMILY_PATCH_ERROR' }, { status: 500 });
  }
}

export async function PUT(request: Request) {
  try {
    const payload = await request.json().catch(() => ({}));
    const overrides = (payload?.overrides && typeof payload.overrides === 'object') ? payload.overrides as OverrideManifest : null;
    const familyProfiles = (payload?.familyProfiles && typeof payload.familyProfiles === 'object') ? payload.familyProfiles as FamilyManifest : null;

    if (!overrides || !familyProfiles) {
      return NextResponse.json({ success: false, error: 'Missing overrides or familyProfiles' }, { status: 400 });
    }

    await saveOverrides(overrides);
    await saveFamilyProfiles(familyProfiles);

    return NextResponse.json({
      success: true,
      overrides: normalizeOverrides(overrides),
      familyProfiles: normalizeFamilyProfiles(familyProfiles),
    });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error?.message || 'ASSET_SESSION_SYNC_ERROR' }, { status: 500 });
  }
}

export async function DELETE(request: Request) {
  try {
    const payload = await request.json().catch(() => ({}));
    const nodeId = String(payload?.nodeId || '').trim();
    const family = String(payload?.family || '').trim() as NodeAssetFamily;
    const slot = String(payload?.slot || '').trim() as 'appearance' | 'effect' | '';

    if (family) {
      const familyProfiles = await loadFamilyProfiles();
      if (!familyProfiles[family]) {
        const overrides = await loadOverrides();
        return NextResponse.json({
          success: true,
          overrides: normalizeOverrides(overrides),
          familyProfiles: normalizeFamilyProfiles(familyProfiles),
          family,
        });
      }

      if (slot === 'appearance' || slot === 'effect') {
        delete familyProfiles[family]?.[slot];
        if (familyProfiles[family] && Object.keys(familyProfiles[family]!).length === 0) {
          delete familyProfiles[family];
        }
      } else {
        delete familyProfiles[family];
      }

      await saveFamilyProfiles(familyProfiles);
      const overrides = await loadOverrides();
      return NextResponse.json({
        success: true,
        overrides: normalizeOverrides(overrides),
        familyProfiles: normalizeFamilyProfiles(familyProfiles),
        family,
        slot: slot || null,
      });
    }

    if (!nodeId) {
      return NextResponse.json({ success: false, error: 'Missing nodeId or family' }, { status: 400 });
    }

    const overrides = await loadOverrides();
    const existing = overrides[nodeId];
    if (existing?.appearance?.src) {
      await safeRemoveIfManaged(existing.appearance.src);
    }
    if (existing?.effect?.src) {
      await safeRemoveIfManaged(existing.effect.src);
    }
    delete overrides[nodeId];
    await saveOverrides(overrides);
    const familyProfiles = await loadFamilyProfiles();
    return NextResponse.json({
      success: true,
      overrides: normalizeOverrides(overrides),
      familyProfiles: normalizeFamilyProfiles(familyProfiles),
      nodeId,
    });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error?.message || 'ASSET_DELETE_ERROR' }, { status: 500 });
  }
}
