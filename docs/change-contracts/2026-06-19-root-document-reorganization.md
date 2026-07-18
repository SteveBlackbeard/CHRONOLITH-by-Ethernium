# Change Contract: Root Document Reorganization

## Scope

Reduce root-level documentation and demo noise without changing Chronolith runtime behavior.

## Reason

Chronolith is now released and governed. The repository root should present the product surface first: README, package metadata, governance, security, core editions, tests, scripts, and canonical docs.

Process logs, release staging notes, session token reports, archived portal artifacts, and demo folders remain useful, but they should not dominate the first repository view.

## Moves

- `REPO_AND_PYPI_RELEASE_CHECKLIST.md` -> `docs/process/REPO_AND_PYPI_RELEASE_CHECKLIST.md`
- `RELEASE_STAGING_PLAN.md` -> `docs/process/RELEASE_STAGING_PLAN.md`
- `SESSION_LOG.md` -> `docs/process/SESSION_LOG.md`
- `SESSION_TOKEN_REPORT.md` -> `docs/process/SESSION_TOKEN_REPORT.md`
- `Ethernium_Portal_Outside.json` -> `docs/archive/Ethernium_Portal_Outside.json`
- `demo_portal.zip` -> `docs/archive/demo_portal.zip`
- `demo_folder/` -> `examples/demo-folder/`
- `example-project/` -> `examples/example-project/`

## Files Updated

- `README.md`
- `.chronolith/rulebook.json`
- `.chronolith/LIVE_HANDOFF.md`
- `scripts/autophagy_report.py`
- `docs/EDITOR_AGENT_INTEGRATION.md`
- `docs/process/README.md`
- `docs/archive/README.md`

## Runtime Impact

No Python runtime API changes.

No package metadata changes.

No PyPI release change.

## Verification

Required:

- `python scripts\health_guard.py --strict`
- `python scripts\autophagy_report.py`
- `python scripts\golden_baseline.py verify`
- `pytest -q`
- `cd D:\Experimentos\ROBIN-HOOD; pytest tests -q`

## Rollback

Move the files back to their previous root paths, restore references, refresh the golden baseline with a rollback contract, and rerun the verification commands.
