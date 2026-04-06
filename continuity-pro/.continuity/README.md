# Continuity Folder

This folder is the canonical continuity nucleus of the project.

## What lives here
- boot rules
- continuity rules
- live handoff
- decisions log
- timeline
- activation protocol

## Canonical automation
Run this after any relevant structural, canonical, or continuity change:

```powershell
python tools/continuity_legacy/run_continuity_cycle.py --repo-root <repo> --strict
```

## Agent rule
The next agent should read `BOOT_SEQUENCE.md` first inside this folder.
