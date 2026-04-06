# Continuity Registry

This folder stores the machine-checked continuity registries.

## What lives here
- `document_dependency_map.json`
- `system_membership_registry.json`

## Canonical automation
These files are validated through:

```powershell
python tools/continuity_legacy/run_continuity_cycle.py --repo-root <repo> --strict
```

## Agent rule
Edit these only when new canonical files or parity-tracked documents are added or retired.
