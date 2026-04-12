# Repo And PyPI Release Checklist

## Current judgment

The current working tree is stronger than the last GitHub snapshot in **dashboard capability**:

- multi-system graph
- node asset pipeline
- edit mode with protected access
- local chat bridge for `openclaw` / `ollama` / `moltbot`
- direct canonical asset folders
- persistent node asset overrides

The previous repo snapshot is stronger in **stability / cleanliness**:

- smaller change surface
- fewer generated files
- fewer moving parts in the dashboard runtime

So the honest conclusion is:

- **current tree is better functionally**
- **older repo state is cleaner operationally**
- before pushing, we should publish the current tree only after a hygiene pass

## Before pushing to GitHub

1. Keep generated artifacts out of Git.
   - server logs
   - screenshots
   - temporary GLBs
   - local env files

2. Review these areas as separate commit groups.
   - dashboard runtime and UI
   - asset pipeline
   - local AI bridge
   - Python/runtime package changes
   - release docs / translations

3. Verify locally.
   - `npm run build` in `nexus-dashboard`
   - Python tests that matter for `continuity-pro` / `continuity-omega`
   - smoke test on `localhost:3000`

4. Confirm the repo message.
   - dashboard is now a sovereign control surface
   - package remains the runtime truth
   - local AI bridge is adapter-based, not hardwired to one provider

## Before publishing PyPI

1. Decide whether this release is:
   - `ethernium-continuity-legacy`
   - `ethernium-continuity-lite`
   - `ethernium-continuity-pro`
   - `ethernium-continuity-omega`
   - or all of them together

2. Bump versions consistently.
   - root `pyproject.toml`
   - modular package `pyproject.toml` files
   - release notes / changelog

3. Verify CLI parity.
   - do not advertise dashboard actions as package commands unless the CLI actually supports them
   - keep package/runtime truth strict

4. Build distributions.
   - source dist
   - wheel

5. Test installation in a clean venv.
   - install from built artifacts
   - run CLI entrypoints
   - verify imports

6. Only then upload to PyPI.

## Recommended commit sequence

1. `chore: ignore local dashboard artifacts`
2. `feat: sovereign dashboard multi-system asset runtime`
3. `feat: local chat bridge for openclaw/ollama/moltbot`
4. `docs: release and deployment preparation`
5. `feat/fix: continuity package updates` (Python side, separately if possible)

## What not to do

- do not publish PyPI straight from a dirty mixed tree without a clean test install
- do not claim package parity for dashboard-only features
- do not push local logs, screenshots, or temp GLBs
- do not auto-install packages from the dashboard UI without explicit operator intent

## Recommended next actions

1. Create a clean branch for release preparation.
2. Split dashboard changes from Python/package changes if possible.
3. Run a clean package build/install test.
4. Tag only after the clean install passes.
