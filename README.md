# CONTINUITY LEGACY by Ethernium

`CONTINUITY LEGACY` is a standalone starter toolkit for building projects with persistent continuity, canonical memory, and repeatable handoff between humans and AI operators.

This toolkit is continuity-first: it provides a reusable discipline for context persistence, document parity, and governed handoff without depending on any external framework.

## What this includes
- a minimal canonical memory surface
- a continuity bootstrap snapshot
- document parity checks
- system membership checks
- an optional external developer layer like `PROJECTDEV/`
- a strict continuity closeout command
- a bootstrapper to personalize the template for a new project

## Quick Start

### 1. The "Pro" Way (CLI) - RECOMMENDED
Install the global CLI to initialize projects in one step:

```powershell
pip install continuity-legacy
continuity-legacy init "My Project"
```

### 2. Fast Step
Fast step five to the new agent `AGENT_START.md` (One step)
or 

### 3. Manual Control (Copy/Paste)
1. Copy this folder to the root of your new project.
2. Run the bootstrapper:

```powershell
python tools/continuity_legacy/bootstrap_project.py --repo-root . --project-name "My Project" --project-slug my_project
```

3. If you want an external continuity layer:

```powershell
python tools/continuity_legacy/bootstrap_project.py --repo-root . --project-name "My Project" --project-slug my_project --enable-external-docs
```

4. Run the strict closeout:

```powershell
python tools/continuity_legacy/run_continuity_cycle.py --repo-root . --strict
```

## Core Files
- `PROJECT_CONTEXT.md`
- `STATE.json`
- `ROADMAP.md`
- `.continuity/BOOT_SEQUENCE.md`
- `.continuity/CONTEXT_CONTINUITY.md`
- `.continuity/LIVE_HANDOFF.md`
- `.continuity/DECISIONS_LOG.md`
- `.continuity/TIMELINE.md`
- `continuity_legacy.json`

## Configuration & Metadata
The `continuity_legacy.json` file controls paths and project identity.

By default, generated reports and snapshots include **provenance metadata** to indicate they were generated with Continuity Legacy. You can disable this by setting `"include_in_reports": false` under the `"metadata"` key in the config file.

```json
  "metadata": {
    "generated_by": "Continuity Legacy by Ethernium",
    "tool_version": "1.0.0",
    "creator": "@Steveblackbeard",
    "include_in_reports": true
  }
```

## Automation & Safety (Continuity Guard)
To ensure the project remains coherent without manual effort, `CONTINUITY LEGACY` includes two safety layers:

1. **Local Guard (Git Hooks)**: Every project bootstrapped with this tool automatically installs a Git `pre-commit` hook. If your `STATE.json` or handoff documents are inconsistent with the rules, Git will block the commit and ask you to fix it.
2. **Cloud Guard (GitHub Actions)**: A built-in workflow validates the continuity cycle on every push to GitHub, ensuring that the repository's "source of truth" is always valid.

## Folder Map
- `/.continuity`
  Canonical continuity memory, handoff, timeline, decisions, and boot rules.
- `/.continuity/registry`
  Registries used by strict validation for document parity and membership.
- `/.continuity/templates`
  Template support surfaces for optional generated layers.
- `/tools`
  Operational entry lane for the toolkit.
- `/tools/continuity_legacy`
  User-facing automation commands such as bootstrap, sync, checks, and strict closeout.
- `/tools/continuity_legacy/core`
  Shared helpers used by the user-facing automation commands.
- `/outputs`
  Generated outputs lane.
- `/outputs/continuity`
  Continuity reports and bootstrap snapshots written by automation.
- `/examples`
  Safe place for test copies or demo instantiations.

## What To Hand An Agent
Passing only `PROJECT_CONTEXT.md` is not enough for a full reconstruction.

If you want a single first file, hand the agent:
- `AGENT_START.md`

For a real agent handoff, use this boot packet:
1. `PROJECT_CONTEXT.md`
2. `.continuity/BOOT_SEQUENCE.md`
3. `STATE.json`
4. `ROADMAP.md`
5. `.continuity/LIVE_HANDOFF.md`

If you must give only one file first, give `PROJECT_CONTEXT.md`, but the next file should immediately be `.continuity/BOOT_SEQUENCE.md`.

## Commands
```powershell
python tools/continuity_legacy/bootstrap_project.py --repo-root <repo>
python tools/continuity_legacy/bootstrap_context.py --repo-root <repo>
python tools/continuity_legacy/doc_parity_check.py --repo-root <repo> --strict
python tools/continuity_legacy/system_membership_check.py --repo-root <repo> --strict
python tools/continuity_legacy/sync_external_dev_context.py --repo-root <repo>
python tools/continuity_legacy/run_continuity_cycle.py --repo-root <repo> --strict
```

## Usage Rule
After any relevant structural, canonical, or continuity change, finish with:

```powershell
python tools/continuity_legacy/run_continuity_cycle.py --repo-root <repo> --strict
```
