# Changelog: Chronolith (Industrial Evolution)

All notable changes to the Chronolith ecosystem will be documented in this file.

## [Unreleased]
### The tool did not enforce its own doctrine
- **`check` now fails closed by default.** With stock defaults — not permissive,
  no `--strict` — the old exit logic printed the drift and then fell through to
  exit 0. A CI job running plain `chronolith-pro check` passed on a drifting
  repository, the exact failure the tool exists to catch and the opposite of its
  own Law 3. Safety is now opt-out: `CHRONOLITH_MODE=permissive` is the only way
  past an inconsistency. `--strict` is a deprecated no-op. Found by an agent
  running the tool for real, not by reading it.
- **Severity is respected.** A finding of any kind was collapsed into a security
  failure, so `check` halted on the very sovereign keys `sovereign-init` creates
  — it told you to make a key, then condemned you for having it. Only a
  danger-level finding (a tracked key in the index) now fails the run; an
  untracked local key is a warning.
- **The pre-push hook is portable.** It wrote a bare `python` and a hardcoded
  absolute site-packages path; under git-bash on Windows `python` is often not
  on PATH, so the hook died with "command not found" and blocked every push
  regardless of DNA state. It now invokes `sys.executable -m` the module.
- **The status panel cannot lie.** It printed a hardcoded `Status: Status: OK`
  above the fail-closed check, announcing OK on a run about to halt. The verdict
  is computed first; the panel says OK or INCONSISTENT to match the exit code.
- Regression tests cover all of the above, including the reproduction that
  exposed the exit-0 bug.


## [3.2.1] - 2026-07-18
### Commands that never ran, and checks that never passed
- **`chain` worked for the first time.** It rendered the transparency chain
  using rich's `Table` without importing it, so it raised `NameError` on every
  invocation since the rename — a documented, shipped command that had never
  once succeeded. Nothing executed it, so nothing noticed.
- Added a CLI surface test that discovers commands from the Typer app and runs
  the read-only ones against a real project. A command may refuse; it may not
  crash. Verified by reintroducing the bug and confirming the suite fails.
- **The Sentinel had never succeeded either.** `git add` aborts across all its
  arguments when one path is missing, and `SESSION_TOKEN_REPORT.md` is not in
  this repository, so nothing was ever staged. The drift check then read the
  working tree rather than the index and committed with an empty stage.
- **The Guardian and the Sentinel were fighting each other.** The Sentinel
  rewrites `README.md` and `STATE.json` on every push and commits them, and the
  golden baseline governed both, so the Sentinel's own commit was reported as
  drift. Machine-regenerated files are now out of the governed set.
- Refreshed the golden baseline, stale since the rename, through a change
  contract — verified against `git cat-file` rather than the local working tree.
- `health_guard` required `docs/CHRONOLITH_GOVERNANCE_KERNEL.md` while the file
  still carried its pre-rename name.
- The secret scanner could not see private keys: the extension filter skipped
  `.priv` before reading it, and every pattern was a text regex. It now reports
  key material ahead of that filter and separates tracked from untracked.
- Root-level `pytest` no longer reports 34 false failures caused by the three
  editions shadowing each other's `chronolith` package.
- Releases publish through Trusted Publishing. No API token exists in the
  workflow, and each edition's tests now run against the built wheel instead of
  the working tree.
- README no longer advertises a 3D dashboard this repository does not ship.

## [3.0.3] - 2026-06-18
### Governed Release Candidate
- Raised all package metadata from `3.0.2` to `3.0.3` for the next immutable PyPI release line.
- Added governance-first release material with the canonical Ethernium banner.
- Balanced local governance work with remote KO/AR translation intent without reintroducing the separated dashboard.
- Kept Chronolith Conekta and AgentOps as explicitly separate tools so the Python framework remains focused.
- Refreshed the golden baseline through a documented change contract.

## [2.1.0] - 2026-04-05
### Industrial Hardening (Major Evolution)
- **Unified Typ-Rich CLI**: Complete refactor of Lite, Pro, and Omega editions to Typer + Rich UI.
- **Symmetry Architectures**: Distinct themes (Industrial, Solemne, Celestial) across all command-line interfaces.
- **deterministic Governance**: Established `SECURITY.md` and `CONTRIBUTING.md` standards.
- **Memory Core**: Decoupled engine from state, enabling zero-loss context sharing between editions.
- **DNA Security**: Implemented SHA-256 state signatures and audited Merkle Tree logic.
- **Sentinel Guardian**: Automated Git-Hook installation via `setup_guardian.py`.
- **Global Awareness**: Robust synchronization engine (v1.6.3) for 9 languages with UTF-16/BOM sanitization.
- **Observability**: Structured JSON logging for enterprise auditability.

## [1.5.0] - 2026-04-02
### Ethernium Synchronization
- Initial transition to 9 languages.
- Basic DNA Synthesis with Merkle Trees.
- Placeholder badges and tactical Quickstart.

## [1.3.1] - 2026-03-20
### Genesis Lite
- Alpha version of the Lite engine.
- Experimental command-line interface.

---
*Chronolith: Protecting the logical lineage of your software.*
