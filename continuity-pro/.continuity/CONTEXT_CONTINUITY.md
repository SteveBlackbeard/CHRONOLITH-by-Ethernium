# CONTEXT CONTINUITY

Date: 2026-03-31
Status: canonical

## Purpose
Make the project reconstructable by any new human or AI operator, not only by the current chat or session.

## Principle
Context must be rebuilt from files, not guessed from conversation history.

## Canonical Continuity Artifacts
- `PROJECT_CONTEXT.md`
- `STATE.json`
- `ROADMAP.md`
- `.continuity/BOOT_SEQUENCE.md`
- `.continuity/LIVE_HANDOFF.md`
- `.continuity/DECISIONS_LOG.md`
- `.continuity/TIMELINE.md`
- optional external developer docs layer

## Context Layers
### Stable Context
- system rules
- construction laws
- naming rules
- operator behavior

Primary source:
- `PROJECT_CONTEXT.md`

### Current State
- current phase
- current truth
- priority zones
- next actions

Primary sources:
- `STATE.json`
- `ROADMAP.md`

### Handoff
- exact stop point
- completed work
- active risks
- next exact action

Primary source:
- `.continuity/LIVE_HANDOFF.md`

### History
- decisions
- milestones
- sequence of changes

Primary sources:
- `.continuity/DECISIONS_LOG.md`
- `.continuity/TIMELINE.md`

## Mandatory Update Rule
Every relevant structural, canonical, or continuity change must update:
1. `STATE.json`
2. `ROADMAP.md`
3. `.continuity/LIVE_HANDOFF.md`

If the change sets a lasting rule or decision, also update:
4. `.continuity/DECISIONS_LOG.md`

If the change completes a milestone, also update:
5. `.continuity/TIMELINE.md`

## Mandatory Automation Closeout
After every relevant structural, canonical, or continuity change, run:
- `python tools/continuity_legacy/run_continuity_cycle.py --repo-root <repo> --strict`
