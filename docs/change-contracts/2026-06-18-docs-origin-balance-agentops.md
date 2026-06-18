# Change Contract: Docs Origin Balance And AgentOps Governance

## Purpose

Balance the local governed Continuity Legacy tree with useful documentation changes that existed on `origin/main`, without reintroducing the extracted `nexus-dashboard` runtime into the Python repository.

## Scope

- Add active Korean and Arabic README files aligned to the current package names.
- Prepare the governed `3.0.3` release candidate because `3.0.2` is already immutable on PyPI.
- Add release notes that use the canonical Ethernium banner at `banners/ethernium_header.png`.
- Update active README version badges and install command references.
- Keep Continuity Conekta external.
- Add a governance seed for the extractable AgentOps incubation folder.
- Harden `health_guard.py` and `autophagy_report.py` so release smoke-test virtual environments are ignored consistently.
- Refresh the golden baseline after validation.

## Explicit Non-Goals

- Do not re-embed `nexus-dashboard/`.
- Do not publish to PyPI.
- Do not change Python runtime behavior or public CLI contracts.
- Do not copy leaked prompts or vendor hidden instructions.

## Rollback

Revert this documentation change set and rerun:

```bash
python scripts/golden_baseline.py verify
python scripts/health_guard.py --strict
pytest -q
```

## Verification

Required before commit:

```bash
python scripts/health_guard.py --strict
pytest -q
python -m build
python -m twine check dist\*
```
