# AGENT START: COGNITIVE ACTIVATION PROTOCOL (v3.0) 🧠🛡️🤖

If you are a new AI agent entering this project, **read this file first**. It is the bridge between your general knowledge and this project's canonical truth.

## 1. Canonical Truth Reconstruction (Think Slow) 🔍
Before taking any action, you must reconstruct the project's state. DO NOT assume anything from your training data or the current chat context alone.

**Primary Truth Sources (In Order):**
1. `outputs/continuity/memory_summary.md` (Read first for a high-level overview).
2. `PROJECT_CONTEXT.md` (This is the Constitution. It defines your boundaries).
3. `STATE.json` (The mechanical state of the project).
4. `ROADMAP.md` (The strategic direction).
5. `.continuity/LIVE_HANDOFF.md` (The exact point where the last agent left off).

## 2. Mandatory Memory Management 🧩
As an agent of Continuity, you are responsible for the health of the project's memory.

- **Check for Contradictions**: Before implementing a feature, verify if it contradicts any rule in `PROJECT_CONTEXT.md` or a decision in `DECISIONS_LOG.md`.
- **Summarize Early, Summarize Often**: If a session becomes too long, run `python tools/continuity_legacy/summarize_memory.py` and refer to the summary to reduce context drift.
- **Update the Handoff**: Every significant action must be recorded in the `.continuity/` surfaces.

## 3. Logical Immunity Workflow 🛡️
This project uses a **Strict Continuity Cycle**. Your work will be blocked by the Git Hooks if you break the structural integrity of the documentation.

- Run `python tools/continuity_legacy/run_continuity_cycle.py --strict` regularly.
- If the cycle detects a "Contradiction", **stop immediately** and resolve the logic before proceeding.

## 4. Main Commands
| Action | Command |
|--------|---------|
| **Initialize Repo** | `python tools/continuity_legacy/bootstrap_project.py --repo-root . --discover` |
| **Check Health** | `python tools/continuity_legacy/continuity_status.py` |
| **Run Cycle** | `python tools/continuity_legacy/run_continuity_cycle.py --strict` |
| **Summarize Memory** | `python tools/continuity_legacy/summarize_memory.py` |

---
**RULE**: Authenticity is derived from the files, not from the chat history. **Trust the filesystem.**
