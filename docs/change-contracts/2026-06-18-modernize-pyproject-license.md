# Change Contract: Modernize PyPI License Metadata

## Summary

Modernize `pyproject.toml` license metadata to use an SPDX expression and remove the deprecated license classifier.

## Scope

Files expected to change:

- `pyproject.toml`
- `.continuity/golden-baseline.json`

Out of scope:

- runtime package behavior
- public CLI behavior
- package version number
- dependency surface beyond the build backend requirement

## Reason

`python -m build` reports Setuptools deprecation warnings for `project.license` as a TOML table and license classifiers. Setuptools indicates these formats will stop being supported in the future. Updating now keeps the release path clean.

## Risk

Risk level: `low`

Potential failure modes:

- older build environments may need a newer Setuptools
- package metadata changes should be checked before upload

## Verification

Required checks:

```text
python scripts/golden_baseline.py verify
python scripts/health_guard.py --strict
pytest -q
python -m build
python -m twine check dist/*
```

## Rollback

Revert `pyproject.toml` and refresh `.continuity/golden-baseline.json` using this contract or a follow-up rollback contract.

## Handoff

Record that package metadata now uses SPDX license syntax.
