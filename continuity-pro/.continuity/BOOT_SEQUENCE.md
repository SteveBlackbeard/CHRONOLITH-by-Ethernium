# BOOT SEQUENCE

Date: 2026-03-31
Status: canonical

## Objective
Define the exact order any new operator or AI must follow when entering the project.

## Read Order
1. `PROJECT_CONTEXT.md`
2. `STATE.json`
3. `ROADMAP.md`
4. `.continuity/CONTEXT_CONTINUITY.md`
5. `.continuity/LIVE_HANDOFF.md`
6. `.continuity/DECISIONS_LOG.md`
7. `.continuity/TIMELINE.md`
8. optional external continuity docs if enabled
9. relevant zone-specific files for the active task

## Required Reconstruction Output
Before editing, the operator should be able to answer:
- what the project is
- what phase it is in
- what was completed last
- what the exact next step is
- what areas are risky
- which files are canonical for the current task

## Required First Response Pattern
Any new operator should begin with:
1. current phase
2. last completed milestone
3. current target zone
4. next exact action
5. active risks
6. assumptions if any

## Rule
If the boot sequence was not followed, the operator should not make structural changes.
