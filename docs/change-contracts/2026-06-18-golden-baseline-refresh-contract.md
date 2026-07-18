# Change Contract: Golden Baseline Refresh Enforcement

## Summary

Require an explicit change contract when refreshing an existing golden baseline.

## Scope

Files expected to change:

- `scripts/golden_baseline.py`
- `.chronolith/golden-baseline.json`
- `docs/change-contracts/`

Out of scope:

- runtime package behavior
- CLI command behavior outside baseline verification
- package version metadata

## Reason

The initial golden baseline is useful, but refresh must not become a silent way to bless accidental drift. Existing baselines should only be refreshed after a reviewed contract is present.

## Risk

Risk level: `low`

Potential failure modes:

- maintainers forget to pass `--contract`
- CI fails if baseline is intentionally changed without refresh
- contract path typo prevents refresh

## Verification

Required checks:

```text
python scripts/golden_baseline.py verify
python scripts/health_guard.py --strict
pytest -q
```

## Rollback

Revert `scripts/golden_baseline.py` and `.chronolith/golden-baseline.json` to the previous commit.

## Handoff

Record that baseline refresh now requires a contract when the baseline already exists.
