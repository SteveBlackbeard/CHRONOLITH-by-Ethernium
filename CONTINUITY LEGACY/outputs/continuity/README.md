# Continuity Outputs

This folder stores continuity-specific derived artifacts.

## What lives here
- `context_bootstrap_summary.json`
- `continuity_cycle_report.json`

## Canonical automation
Regenerate them with:

```powershell
python tools/continuity_legacy/run_continuity_cycle.py --repo-root <repo> --strict
```

## Agent rule
Use these as evidence and diagnostics, not as the primary memory surface.
