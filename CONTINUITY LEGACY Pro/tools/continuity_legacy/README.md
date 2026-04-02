# Tools Folder

This folder is the operational entry lane for `CONTINUITY LEGACY`.

## What lives here
- bootstrap scripts
- continuity validation scripts
- sync scripts

## Canonical automation
Start from:

```powershell
python tools/continuity_legacy/bootstrap_project.py --repo-root <repo> --project-name "<name>" --project-slug <slug>
```

## Agent rule
If the project is already initialized, prefer `run_continuity_cycle.py` over ad hoc script execution.
