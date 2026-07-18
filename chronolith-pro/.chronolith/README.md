# Chronolith Folder

This folder is the canonical chronolith nucleus of the project.

## What lives here
- boot rules
- chronolith rules
- live handoff
- decisions log
- timeline
- activation protocol

## Canonical automation
Run this after any relevant structural, canonical, or chronolith change:

```powershell
python tools/chronolith/run_chronolith_cycle.py --repo-root <repo> --strict
```

## Agent rule
The next agent should read `BOOT_SEQUENCE.md` first inside this folder.
