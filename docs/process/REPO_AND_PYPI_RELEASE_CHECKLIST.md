# Repo And PyPI Release Checklist

## Current judgment

The current working tree is stronger than the last GitHub snapshot in **governance and release hygiene**:

- strict governance health guard
- feature registry and machine-readable rulebook
- non-destructive autophagy report
- live handoff state
- externalized ROBIN HOOD tool
- extracted CONEKTA control surface

The previous repo snapshot kept the dashboard colocated. The current direction is cleaner:

- Continuity Legacy remains the Python package/runtime truth
- CONEKTA owns the web dashboard in its own repository
- dashboard build/lint state no longer blocks PyPI release

So the honest conclusion is:

- **current tree is better governed**
- **CONEKTA is now a separate product**
- before pushing, verify the package and governance checks independently from CONEKTA

## Before pushing to GitHub

1. Keep generated artifacts out of Git.
   - server logs
   - screenshots
   - temporary GLBs
   - local env files

2. Review these areas as separate commit groups.
   - Continuity governance kernel
   - CONEKTA extraction boundary
   - encoding/version cleanup
   - Python/runtime package changes
   - release docs / translations

3. Verify locally.
   - `python scripts/health_guard.py --strict`
   - `python scripts/autophagy_report.py`
   - `pytest -q`
   - `python -m build`
   - `twine check dist/*`

4. Confirm the repo message.
   - Continuity Legacy is the runtime/governance kernel
   - CONEKTA is external
   - ROBIN HOOD is external
   - adapter contracts are explicit

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
   - do not advertise CONEKTA actions as package commands unless the CLI actually supports them
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

1. `feat: add continuity governance kernel`
2. `chore: clean encoding and version baseline`
3. `chore: extract conekta control surface`
4. `docs: document robin hood and conekta boundaries`
5. `docs: release and deployment preparation`

## What not to do

- do not publish PyPI straight from a dirty mixed tree without a clean test install
- do not claim package parity for CONEKTA-only features
- do not push local logs, screenshots, or temp GLBs
- do not re-embed the CONEKTA web app into the Python package release

## Recommended next actions

1. Reconcile local `main` with `origin/main` without reintroducing `nexus-dashboard/`.
2. Keep CONEKTA changes in `D:\Experimentos\CONEKTA`.
3. Keep ROBIN HOOD external and outside the Python package runtime.
4. Run a clean package build/install test.
5. Tag only after the clean install passes.

## Latest release status (v3.0.2)

- GitHub release: `pypi-v3.0.2` (title: `v3.0.2 - HOTFIX`)
- PyPI package: `ethernium-continuity-legacy==3.0.2`
  https://pypi.org/project/ethernium-continuity-legacy/3.0.2/
- PyPI package: `ethernium-continuity-lite==3.0.2`
  https://pypi.org/project/ethernium-continuity-lite/3.0.2/
- PyPI package: `ethernium-continuity-pro==3.0.2`
  https://pypi.org/project/ethernium-continuity-pro/3.0.2/
- PyPI package: `ethernium-continuity-omega==3.0.2`
  https://pypi.org/project/ethernium-continuity-omega/3.0.2/

## Next release target

If the current governance and documentation cleanup is published to PyPI, use `3.0.3`.

Do not upload over `3.0.2`; PyPI releases are immutable.
