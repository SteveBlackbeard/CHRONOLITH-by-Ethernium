# Continuity Live Handoff

## Current Objective

Build Phase 1 of the Continuity governance kernel while keeping ROBIN HOOD and CONEKTA as external tools.

## Current State

- Governance rulebook exists at `.continuity/rulebook.json`.
- Feature registry exists at `.continuity/feature-registry.json`.
- Health guard exists at `scripts/health_guard.py`.
- Non-destructive autophagy report exists at `scripts/autophagy_report.py`.
- Golden baseline verification exists at `scripts/golden_baseline.py`.
- Existing golden baseline refreshes require a reviewed contract under `docs/change-contracts/`.
- CI runs both governance checks in `.github/workflows/industrial_guardian.yml`.
- CI runs the health guard in strict mode.
- ROBIN HOOD is external at `D:\Experimentos\ROBIN-HOOD` and is not a Continuity dependency.
- CONEKTA is external at `D:\Experimentos\CONEKTA`.
- The former `nexus-dashboard/` source was extracted to `D:\Experimentos\CONEKTA`.
- `nexus-dashboard/` has been removed from this repository.

## Known Warnings

`python scripts/health_guard.py --strict` currently passes.
`python scripts/golden_baseline.py verify` currently passes.

Baseline cleanup completed:

- `VERSION` is UTF-8 and aligned to `pyproject.toml` as `3.0.2`.
- `docs/process/SESSION_LOG.md` is UTF-8 readable.
- Known mojibake markers were removed from governed source files.
- Generated `outputs/` directories are ignored by the health guard.

## Autophagy Findings

`python scripts/autophagy_report.py` ignores extractable external tools and currently identifies remaining Continuity attention targets.

The main remaining non-core attention targets are:

- `_tmp_reglas_oro/reglas de oro/10_CONTINUITY.md`
- translation packs under `OTHER_LANGUAGES/`
- historical/session reports

No autophagy action is destructive. Cleanup requires explicit human approval.

## Next Safe Actions

1. Treat `pyproject.toml` and `VERSION` as aligned release metadata for `3.0.2`.
2. Decide whether `_tmp_reglas_oro/` should be archived outside the repo, deleted, or converted into selected canonical governance docs.
3. Fix inherited CONEKTA lint debt in `D:\Experimentos\CONEKTA`.
4. Continue reducing autophagy attention targets when release pressure is low.

## Last Updated

2026-06-17
