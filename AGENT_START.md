# AGENT START

If you can give a new agent only one file first, give this one.

## What this toolkit is
`CONTINUITY LEGACY by Ethernium` is a continuity-first starter for projects that need persistent memory, canonical handoff, and strict closeout between human and AI operators.

## Immediate Read Order
1. `PROJECT_CONTEXT.md`
2. `.continuity/BOOT_SEQUENCE.md`
3. `STATE.json`
4. `ROADMAP.md`
5. `.continuity/LIVE_HANDOFF.md`

## First Reconstruction Output
Before editing, the agent should be able to answer:
- current phase
- last completed milestone
- next exact action
- current target zone
- active risks

## Resuming an Active Project (Continuity Mode)
If this is an existing project, do not try to "start over" or "re-innovate" from scratch. Your priority is strictly to rebuild the context from the files above. If there is a `LIVE_HANDOFF.md` or a `STATE.json`, those are your true source of truth, not your initial chat imagination.

## Main Commands
Bootstrap a copied starter:

```powershell
python tools/continuity_legacy/bootstrap_project.py --repo-root <repo> --project-name "<name>" --project-slug <slug>
```

Strict closeout:

```powershell
python tools/continuity_legacy/run_continuity_cycle.py --repo-root <repo> --strict
```

## Rule
Do not start implementation from chat memory alone. Reconstruct from the files above first.
