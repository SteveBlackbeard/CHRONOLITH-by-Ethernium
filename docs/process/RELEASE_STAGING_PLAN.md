# Release Staging Plan

This plan separates what should go to GitHub from what should stay local.

## 1. Definitely keep local only

Do **not** publish these:

- `nexus-dashboard/config/node-asset-overrides.json`
- `nexus-dashboard/config/node-asset-family-overrides.json`
- `nexus-dashboard/public/assets/nodes/overrides/*.glb`
- local logs, screenshots, temp DOM dumps, `.env.local`

These are now ignored in `.gitignore`.

## 2. Dashboard release set

Stage these together for the dashboard release:

```bash
git add .gitignore
git add nexus-dashboard/README.md
git add nexus-dashboard/.env.example
git add nexus-dashboard/docs/NODE_ASSET_PIPELINE.md
git add nexus-dashboard/public/assets/nodes
git add nexus-dashboard/src/app/page.tsx
git add nexus-dashboard/src/app/globals.css
git add nexus-dashboard/src/app/layout.tsx
git add nexus-dashboard/src/app/api/chat
git add nexus-dashboard/src/app/api/node-assets
git add nexus-dashboard/src/app/api/projects
git add nexus-dashboard/src/components/NexusCore.tsx
git add nexus-dashboard/src/components/NodeAssetRig.tsx
git add nexus-dashboard/src/components/SovereignHUD.tsx
git add nexus-dashboard/src/components/shaders/CoreShader.ts
git add nexus-dashboard/src/lib/eventChain.ts
git add nexus-dashboard/src/lib/filesystemHandles.ts
git add nexus-dashboard/src/lib/graphData.ts
git add nexus-dashboard/src/lib/i18n.ts
git add nexus-dashboard/src/lib/localAdapters.ts
git add nexus-dashboard/src/lib/nodeAssets.ts
git add nexus-dashboard/src/lib/nodeGlyphTextures.ts
git add nexus-dashboard/src/lib/telemetry.ts
git add docs/process/REPO_AND_PYPI_RELEASE_CHECKLIST.md
git add docs/process/RELEASE_STAGING_PLAN.md
```

Suggested commit:

```bash
git commit -m "feat: sovereign dashboard asset runtime and local ai bridge"
```

## 3. Python/runtime package release set

Review these separately before staging:

- `.github/scripts/audit_comparison.py`
- `continuity-pro/...`
- `continuity-omega/...`
- `continuity-pro/tests/test_logic.py`
- `pytest.ini`

Suggested commit after review:

```bash
git commit -m "feat: continuity runtime and package hardening"
```

## 4. Docs / release notes set

Review and stage separately:

- `README.md`
- `RELEASE_NOTES_MANIFEST.md`
- `OTHER_LANGUAGES/...`
- `examples/demo-folder/README.md`

Suggested commit:

```bash
git commit -m "docs: update release notes and translated manifests"
```

## 5. PyPI readiness gate

Before publishing any package:

1. build in a clean env
2. install from built artifacts
3. run the real CLI entrypoints
4. confirm versioning is intentional
5. only then upload

## 6. Honest recommendation

Best release order:

1. dashboard commit
2. runtime/package commit
3. docs/release notes commit
4. tag
5. PyPI upload

That keeps the history understandable and reduces rollback pain.
