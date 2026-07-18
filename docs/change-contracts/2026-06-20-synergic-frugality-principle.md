# Change Contract: Synergic Frugality Principle

## Objective

Add a practical golden-rule principle to Chronolith: maximize quality and fidelity at the lowest responsible cost by combining neural heuristics, symbolic validation, biomimetic event-driven execution, reverse-engineering discipline, cybersecurity boundaries, low-code structure, and advanced programming only at measured bottlenecks.

## Scope

Allowed changes:

- `.chronolith/rulebook.json`
- `docs/CHRONOLITH_GOVERNANCE_KERNEL.md`
- external tool repository URL references

No runtime Python behavior is changed.

## Rationale

Chronolith should encode AI-assisted engineering as a governed system, not as a vague prompt style. Neural models are useful for pattern recognition and creative heuristics, but deterministic symbolic checks, baselines, health gates, and fail-closed policies should constrain the final repository state.

The principle is also frugal: do not compute, render, prompt, or regenerate what has not changed.

## Acceptance

Run:

```text
python scripts/health_guard.py --strict
python scripts/golden_baseline.py verify
pytest -q
```

If the rulebook change is accepted, refresh the golden baseline with this contract:

```text
python scripts/golden_baseline.py refresh --contract docs/change-contracts/2026-06-20-synergic-frugality-principle.md
```

## Rollback

Revert this contract, restore the previous `.chronolith/rulebook.json` and `docs/CHRONOLITH_GOVERNANCE_KERNEL.md`, then refresh the golden baseline with a rollback contract if the baseline was updated.
