# Change Contract: Honest Package Descriptions

## Summary

Rewrite the `description` field in the four `pyproject.toml` files, and refresh
the golden baseline, which governs `pyproject.toml`.

## Scope

- `pyproject.toml` and the three edition manifests
- `.chronolith/golden-baseline.json`

Out of scope: runtime behaviour. Only prose changes.

## Reason

The summaries carried adjectives nobody can check: "industrial-grade",
"professional", "zero-friction", "Enterprise Oracle". One called a Shannon
entropy metric "Shannon Entropy physics", and another described translation
sync as "global synchronization".

None of it is false — the entropy is computed, the impact analysis exists — but
all of it is inflated, and this project's distinguishing feature is that its own
`verify` command reports what it did **not** prove. A tool that refuses to
overclaim in its output should not overclaim in its summary.

The replacements say what each package does, and where there is a number, they
use it.

## Risk

Risk level: `low`. Prose in package metadata; no code path reads it.

## Verification

```text
python scripts/golden_baseline.py verify
python scripts/audit_all.py
```

The description reaches PyPI only on the next release, so the published
summaries stay as they are until then. That is expected, not a defect.

## Rollback

```text
git revert <commit>
```
