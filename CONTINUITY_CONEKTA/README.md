# Continuity Conekta

Continuity Conekta is the standalone visual control surface for Continuity Legacy.

This folder records the extraction boundary from the Continuity Legacy repository. The former `nexus-dashboard/` source has been copied to the local standalone repository:

```text
D:\Experimentos\continuity-conekta
```

## Product Boundary

Continuity Legacy owns:

- Python package runtime
- Lite / Pro / Omega editions
- Merkle and state integrity
- governance kernel
- health guard
- autophagy reporting
- release safety

Continuity Conekta owns:

- web dashboard
- local control surface
- 3D ecosystem graph
- linked project visualization
- local AI chat bridge UI
- node asset pipeline
- browser/runtime adapters

## Extraction Source

Former source folder:

```text
nexus-dashboard/ (removed from Continuity Legacy)
```

Local target repository:

```text
D:\Experimentos\continuity-conekta
```

Suggested package/app name:

```text
continuity-conekta
```

## Extraction Rule

The standalone repo was created from source files only. Do not carry local runtime debris.

Include:

- `src/`
- `public/`
- `config/` templates only
- `docs/`
- `.env.example`
- `.gitignore`
- `README.md`
- `package.json`
- `package-lock.json`
- `next.config.ts`
- `eslint.config.mjs`
- `postcss.config.mjs`
- `tsconfig.json`

Exclude:

- `node_modules/`
- `.next/`
- `.edge-headless/`
- logs
- screenshots
- temporary GLBs
- `.env.local`
- `*.tsbuildinfo`
- generated DOM dumps

## Runtime Relationship

Continuity Conekta should talk to Continuity Legacy through explicit adapters, not by assuming dashboard buttons map directly to package commands.

Recommended bridge:

```text
Conekta UI -> local adapter/API -> Continuity Legacy CLI/runtime -> STATE.json / reports
```

## Migration Status

```text
status: extracted-locally
source: nexus-dashboard/ (removed)
target: D:\Experimentos\continuity-conekta
blocks_continuity_release: false
```
