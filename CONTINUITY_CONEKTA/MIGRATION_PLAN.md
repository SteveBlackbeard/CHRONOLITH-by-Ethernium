# Continuity Conekta Migration Plan

## Phase 1: Boundary

- `nexus-dashboard/` has been copied to the local standalone repository path.
- Treat it as the source for the future `continuity-conekta` repository.
- Remove it from Continuity governance as an internal feature.
- Keep Continuity release checks independent from dashboard build state.

## Phase 2: Clean Source

Before extraction:

- remove local logs
- remove `.next/`
- remove `.edge-headless/`
- remove `node_modules/`
- remove `.env.local`
- remove screenshots and DOM dumps
- keep `.env.example`

## Phase 3: New Repository

Create a new repo named:

```text
continuity-conekta
```

Copy only the files listed in `EXTRACTION_MANIFEST.json`.

Local extraction target:

```text
D:\Experimentos\continuity-conekta
```

## Phase 4: Adapter Contract

Define a stable adapter between Conekta and Continuity Legacy:

```text
GET /state
GET /events
POST /actions/audit
POST /actions/scan
POST /actions/seal
POST /actions/crystallize
```

The adapter must fail closed if the local Continuity runtime is missing or reports invalid state.

## Phase 5: Continuity Cleanup

After the new repo exists:

- remove `nexus-dashboard/` from this repository: done
- replace README dashboard sections with a link to Continuity Conekta: done
- keep only adapter docs in Continuity Legacy: done
- rerun `python scripts/health_guard.py --strict`
- rerun `pytest -q`

## Current Verification

Completed in `D:\Experimentos\continuity-conekta`:

```text
npm install
npm run build
```

`npm run lint` currently fails on inherited lint debt. Track that work in the Conekta repo, not in Continuity Legacy.
