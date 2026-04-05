# Outputs Folder

This folder stores generated outputs written by the toolkit.

## What lives here
- continuity reports
- bootstrap summaries

## Canonical automation
Refresh outputs with:

```powershell
python tools/continuity_legacy/run_continuity_cycle.py --repo-root <repo> --strict
```

## Agent rule
Treat outputs as derived artifacts. They should reflect canon, not replace it.
