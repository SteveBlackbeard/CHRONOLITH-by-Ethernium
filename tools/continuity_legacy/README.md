# Continuity Legacy Commands

This folder contains the user-facing automation commands.

## Commands
- `bootstrap_project.py`
- `bootstrap_context.py`
- `doc_parity_check.py`
- `system_membership_check.py`
- `sync_external_dev_context.py`
- `run_continuity_cycle.py`

## Canonical automation
The main closeout command is:

```powershell
python tools/continuity_legacy/run_continuity_cycle.py --repo-root <repo> --strict
```

## Agent rule
Use this folder as the runtime interface of the toolkit. Do not start from `core/` unless you are changing the toolkit itself.
