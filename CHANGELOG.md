# CHANGELOG: CONTINUITY LEGACY 🛡️🚀

All notable changes to this project will be documented in this file.

## [2.3.0] - 2026-04-01: Glass Box Discovery 🔍
- **Added**: `tools/continuity_legacy/discover_project.py` - Automated discovery engine.
- **Improved**: `bootstrap_project.py` with `--discover` flag to auto-suggest context and rules for existing projects.
- **Improved**: Logic to detect `camelCase` vs `snake_case` in existing code bases.

## [2.2.0] - 2026-04-01: Maturity & Governance ⚖️
- **Added**: `MAINTAINERS.md` - Formal governance and succession plan.
- **Improved**: `CONTRIBUTING.md` with "Continuity Proof" PR requirements.
- **Added**: `doc_parity_check.py` now supports `info`, `warning`, and `error` severity levels.
- **Added**: `--bypass "reason"` flag in `run_continuity_cycle.py` with automatic logging in `.continuity/BYPASS_LOG.md`.

## [2.1.0] - 2026-04-01: Global Expansion 🌍
- **Added**: `OTHER_LANGUAGES/` folder with documentation in 9 languages (ES, JA, RU, ZH, FR, IT, DE, NL, EN).
- **Unified**: Root documentation (`USE_CASES.md`, `TROUBLESHOOTING.md`) updated to English for international standards.
- **Improved**: `README.md` with links to all international versions.

## [2.0.0] - 2026-04-01: The Automated Guardian 🛡️
- **Added**: Dual Git Hook system (`pre-commit` for warnings, `pre-push` for strict blocking).
- **Added**: `continuity_status.py` - Color-coded health dashboard for the project.
- **Added**: `continuity_suggest.py` - AI-assisted update suggestions based on git diffs.
- **Improved**: Modular context loading with `[include: path/to/file.md]` support.
- **Improved**: `.continuityignore` support for parity checks.

## [1.0.0] - 2026-03-31: Initial Release (Nivel 1) 💎
- First manual framework for continuity and document parity.
- Core logic for `STATE.json`, `ROADMAP.md`, and `.continuity/` surfaces.

---
*Created by Ethernium. Optimized for AI-Human pair programming.*
