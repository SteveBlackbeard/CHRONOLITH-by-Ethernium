# Continuity Legacy: Persistent Governance Layer 



`CONTINUITY LEGACY` is a standalone starter toolkit for building projects with persistent continuity, canonical memory, and repeatable handoff between humans and AI operators.



This toolkit is continuity-first: it provides a reusable discipline for context persistence, document parity, and governed handoff without depending on any external framework.



## What this includes

- a minimal canonical memory surface

- a continuity bootstrap snapshot

- document parity checks

- system membership checks

- an optional external developer layer like `PROJECTDEV/`

- a strict continuity closeout command

- a bootstrapper to personalize the template



## Quick Start



### 1. The "Pro" Way (CLI) - RECOMMENDED

Install the global CLI to initialize projects in one step:



```powershell

pip install continuity-legacy

continuity-legacy init "My Project"

```



### 2. Manual Control (Copy/Paste)

1. Copy this folder to the root of your new project.

2. Run the bootstrapper:



```powershell

python tools/continuity_legacy/bootstrap_project.py --repo-root . --project-name "My Project" --project-slug my_project

```



3. If you want an external continuity layer:



```powershell

python tools/continuity_legacy/bootstrap_project.py --repo-root . --project-name "My Project" --project-slug my_project --enable-external-docs

```



## Automation & Safety (Continuity Guard)

To ensure the project remains coherent without manual effort, it includes a double-layered safety system:



1. **Local Guard (`pre-commit`)**: Installed by default. Uses **Soft Mode** to warn you about drift or missing markers while you work, without blocking your creative flow.

2. **Border Guard (`pre-push`)**: Installed by default. Uses **Strict Mode** to **block the push** to GitHub if the continuity cycle is not 100% valid.



## Core Files

- `PROJECT_CONTEXT.md`

- `STATE.json`

- `ROADMAP.md`

- `.continuity/LIVE_HANDOFF.md`

- `AGENT_START.md` (File to hand over to a new AI agent)



---

**For more details, see the use cases and troubleshooting guide in the root directory.**

---

| Guide | Link |
| :--- | :--- |
| [**Industrial Guide**](../../../docs/HOW_TO_USE_IT.md) | [HOW_TO_USE_IT.md](../../../docs/HOW_TO_USE_IT.md) |
| [**Release Manifest**](../../../RELEASE_NOTES_MANIFEST.md) | [RELEASE_NOTES_MANIFEST.md](../../../RELEASE_NOTES_MANIFEST.md) |

---

---
*Continuity Legacy: Protecting the logical lineage of your software.*
