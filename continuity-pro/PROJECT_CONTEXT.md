# CONTINUITY LEGACY Context



SYSTEM ROLE:

Continuity-first project operating context.



PRIMARY GOAL:

Keep the project reconstructable, governed, and usable across multiple sessions, operators, and AI agents.



EXECUTION MODE:

- Think global before acting local.

- Scan before moving.

- Analyze before improving or innovating.

- Improve only when the surrounding system is legible and the change raises coherence, quality, functionality, or code integrity.

- Prefer reversible changes over destructive shortcuts.

- Keep documentation, state, and handoff aligned with the codebase.



CONTEXT CONTINUITY RULES:

- Do not rely on chat memory as the primary source of context.

- Reconstruct context from canonical files before structural work.

- After every relevant change, update:

  - `STATE.json`

  - `ROADMAP.md`

  - `.continuity/LIVE_HANDOFF.md`

- When a lasting decision is made, also update:

  - `.continuity/DECISIONS_LOG.md`

- When a milestone is completed, also update:

  - `.continuity/TIMELINE.md`



CONSTRUCTION RULES:

- Nothing is deleted without a replacement or an archive path.

- Naming should describe purpose, not personal memory.

- Do not optimize a structure that is still incoherent.

- If a change increases entropy, it is incomplete.



OPERATOR RULES:

- Every new agent must read `.continuity/BOOT_SEQUENCE.md`.

- The first response must reconstruct the current phase, last milestone, next action, target zone, and active risks.

- If the boot sequence was not followed, the operator should not make structural changes.



AUTOMATION RULE:

- The canonical post-change command is `python tools/continuity_legacy/run_continuity_cycle.py --repo-root <repo> --strict`.



EXTERNAL DOCS POLICY:

- An external developer continuity layer is supported but optional.

- If enabled, it should be synced from canonical repo memory instead of edited manually first.

---
*Continuity Legacy: Protecting the logical lineage of your software.*
