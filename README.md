# CONTINUITY LEGACY by Ethernium

`CONTINUITY LEGACY` is a standalone starter toolkit for building projects with persistent continuity, canonical memory, and repeatable handoff between humans and AI operators.

This toolkit is continuity-first: it provides a reusable discipline for context persistence, document parity, and governed handoff without depending on any external framework.

## What this includes
- a minimal canonical memory surface
- a minimal canonical memory surface
- a continuity [bootstrap snapshot](file:///d:/Experimentos/CONTINUITY_LEGACY/outputs/continuity/context_bootstrap_summary.json)
- document [parity checks](file:///d:/Experimentos/CONTINUITY_LEGACY/tools/continuity_legacy/doc_parity_check.py)
- system [membership checks](file:///d:/Experimentos/CONTINUITY_LEGACY/tools/continuity_legacy/system_membership_check.py)
- an optional external developer layer like `PROJECTDEV/`
- a strict continuity [closeout command](file:///d:/Experimentos/CONTINUITY_LEGACY/tools/continuity_legacy/run_continuity_cycle.py)
- a [bootstrapper](file:///d:/Experimentos/CONTINUITY_LEGACY/tools/continuity_legacy/bootstrap_project.py) to personalize the template

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
To ensure the project remains coherent without manual effort, `CONTINUITY LEGACY` includes a double-layered safety system:

1. **Local Guard (`pre-commit`)**: Installed by default. Uses **Soft Mode** to warn you about drift or missing markers while you work, without blocking your creative flow.
2. **Border Guard (`pre-push`)**: Installed by default. Uses **Strict Mode** to **block the push** to GitHub if the continuity cycle is not 100% valid. This ensures the master/main branch is always canonical.
3. **Cloud Guard (GitHub Actions)**: Validates the continuity cycle on every PR or push to the server.

## Resources
- [🚀 Real-world Use Cases](file:///d:/Experimentos/CONTINUITY_LEGACY/USE_CASES.md)
- [🛠️ Troubleshooting Guide](file:///d:/Experimentos/CONTINUITY_LEGACY/TROUBLESHOOTING.md)
- [🛡️ Security Policy](file:///d:/Experimentos/CONTINUITY_LEGACY/SECURITY.md)
- [🤝 Contributing Guide](file:///d:/Experimentos/CONTINUITY_LEGACY/CONTRIBUTING.md)
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

### Resuming an Existing Project
If the project already has code and active implementation:
1.  Hand the new agent `AGENT_START.md`.
2.  The agent will detect the existing `STATE.json` and `.continuity/` folder.
3.  The agent will calculate the exact stopping point from `LIVE_HANDOFF.md`.
4.  The agent is required to re-state the **Next Exact Action** to confirm alignment before writing any new code.

## Survival Guide: How to keep Continuity alive
Continuity is a living system. If ignored, its value degrades.

1. **Be Honest in `STATE.json`**: If you just broke something, update the state to reflect it. Don't hide debt.
2. **Next Exact Action is Sacred**: The next agent needs to know exactly where to click or what to write first.
3. **Commit often, Cycle often**: Running the cycle is fast. Use it to catch drift early.

## Anti-Patterns: What NOT to do
- ✘ **The "Just this once" skip**: Skipping the cycle when you're in a hurry is the first step toward project amnesia.
- ✘ **Markdown Overload**: Don't treat `PROJECT_CONTEXT.md` as a wiki. Keep it as governing rules. Use the `[include: path/to/file.md]` feature for modularity.
- ✘ **Ignoring the Hook**: If the Git Hook warns you, don't ignore it. It's your safety net.

## Commands (v2.0)
```powershell
# High-level health dashboard
python tools/continuity_legacy/continuity_status.py

# Assisted updates based on git changes
python tools/continuity_legacy/continuity_suggest.py

# Standard cycles & checks
python tools/continuity_legacy/run_continuity_cycle.py --repo-root . --strict
python tools/continuity_legacy/bootstrap_project.py --repo-root .
```
-   `--strict`: Block on any inconsistency.
-   `--soft` (default): Warn but continue.

## Usage Rule
After any relevant structural, canonical, or continuity change, finish with:

```powershell
python tools/continuity_legacy/run_continuity_cycle.py --repo-root .
```
Check your dashboard:
```powershell
python tools/continuity_legacy/continuity_status.py
```

## International Versions 🌍
Access the documentation in your preferred language:

- [English (EN)](file:///d:/Experimentos/CONTINUITY_LEGACY/OTHER_LANGUAGES/en/README.md)
- [Español (ES)](file:///d:/Experimentos/CONTINUITY_LEGACY/OTHER_LANGUAGES/es/README.md)
- [日本語 (JA)](file:///d:/Experimentos/CONTINUITY_LEGACY/OTHER_LANGUAGES/ja/README.md)
- [Русский (RU)](file:///d:/Experimentos/CONTINUITY_LEGACY/OTHER_LANGUAGES/ru/README.md)
- [中文 (ZH)](file:///d:/Experimentos/CONTINUITY_LEGACY/OTHER_LANGUAGES/zh/README.md)
- [Français (FR)](file:///d:/Experimentos/CONTINUITY_LEGACY/OTHER_LANGUAGES/fr/README.md)
- [Italiano (IT)](file:///d:/Experimentos/CONTINUITY_LEGACY/OTHER_LANGUAGES/it/README.md)
- [Deutsch (DE)](file:///d:/Experimentos/CONTINUITY_LEGACY/OTHER_LANGUAGES/de/README.md)
- [Nederlands (NL)](file:///d:/Experimentos/CONTINUITY_LEGACY/OTHER_LANGUAGES/nl/README.md)

---
*Created by Ethernium. Optimized for AI-Human pair programming.*
