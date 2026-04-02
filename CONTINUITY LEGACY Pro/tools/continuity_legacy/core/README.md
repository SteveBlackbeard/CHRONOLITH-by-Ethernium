# Continuity Legacy Core

This folder contains shared helpers used by the user-facing commands.

## What lives here
- config loading
- path resolution
- snapshot building
- common JSON and text helpers

## Canonical automation
There is no direct CLI entrypoint here.

Use:

```powershell
python tools/continuity_legacy/run_continuity_cycle.py --repo-root <repo> --strict
```

## Agent rule
Only edit this folder when changing cross-command behavior.
