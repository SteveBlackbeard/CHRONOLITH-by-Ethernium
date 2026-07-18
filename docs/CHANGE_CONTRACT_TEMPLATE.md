# Change Contract Template

Use this template when a change touches sensitive paths, runtime behavior, release metadata, cryptographic state, CI workflows, or frozen assets.

## Summary

Short description of the intended change.

## Scope

Files or modules expected to change:

- `path/to/file`

Out of scope:

- `path/to/other-area`

## Reason

Why this change is needed now.

## Risk

Risk level:

- `low`
- `medium`
- `high`

Potential failure modes:

- behavior regression
- package metadata drift
- encoding drift
- state/hash mismatch
- documentation mismatch

## Verification

Required checks:

```text
python scripts/health_guard.py
python scripts/golden_baseline.py verify
pytest
```

Additional checks:

```text
python -m build
twine check dist/*
```

## Rollback

Exact rollback path:

```text
Describe how to disable, revert, or isolate the change.
```

## Handoff

Update `.chronolith/LIVE_HANDOFF.md` or the relevant session log with:

- final state
- warnings
- skipped checks
- next action

## Baseline Refresh

If this contract approves a golden baseline refresh, run:

```text
python scripts/golden_baseline.py refresh --contract docs/change-contracts/<this-file>.md
```
