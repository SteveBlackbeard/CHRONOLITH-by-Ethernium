## [3.2.0] - 2026-07-16: Sovereign DNA Security 🔐

### Fixed (production-critical)
- **Real DNA drift detection.** `check` previously computed the Merkle root but never compared it to a baseline, so document drift was never actually caught — the guardian only halted on secrets and doc-parity. It now compares against a signed baseline and fails closed on divergence.
- **Path-bound Merkle leaves.** Content-only leaves were blind to renames and cross-file content swaps; leaves are now keyed by file path.
- **State signature is verified on read.** `sign_state` was write-only (stamped but never checked); `check`/`status` now verify it and fail closed on tampering.
- **Config filename mismatch** (`continuity-legacy.json` vs `continuity_legacy.json`) resolved with a tolerant resolver; `resolve_repo_root` no longer risks an `IndexError` on shallow trees.
- **`decision_engine.py` import fixed** (a stray character made the module unimportable, silently skipping its tests).

### Added — sovereign cryptography (`sovereign_vault.py`, new commands)
- **`sovereign-init`** (`--encrypt`): Ed25519 signing + X25519 encryption keys; optional scrypt + ChaCha20-Poly1305 vault unlocked via `CONTINUITY_PASSPHRASE`.
- **Ed25519-signed baselines and chain entries** — a recomputed checksum no longer passes; the local public key is the trust anchor (keypair-swap rejected).
- **DNA transparency chain** (`chain`): append-only, hash-linked, signed log of every crystallization; history rewrites are detectable.
- **Merkle inclusion proofs** (`prove` / `verify-proof`): O(log n) per-file verification without rehashing the repo.
- **Attestations** (`attest` / `verify-attest`): signed provenance over THE_CHOSEN_ONES.
- **Bitcoin anchoring** (`anchor` / `verify-anchor`): an external witness. Timestamps the transparency-chain head into Bitcoin via OpenTimestamps, so a third party can verify the DNA state existed at a confirmed time without trusting the operator (and a past timestamp survives key compromise). Optional `ots` client; local sovereign record written either way.
- **Key rotation** (`sovereign-rotate`): the old key signs the hand-off; retired keys still verify old records; forged hand-offs stop the trust walk.
- **Real sealed context**: `seal_context` replaced its base64 obfuscation with authenticated X25519 + ChaCha20-Poly1305 encryption.
- **Crypto-agility**: `sig_alg` tags on all signed records for a future post-quantum signer.
- **Incremental hashing** (mtime+size cache) so `check` stops rehashing every file each run.

### Docs
- Added `SOVEREIGN_SECURITY.md`; corrected the main README's integrity claims to match the implementation.

## [3.1.0] - 2026-04-01: The Professional Pillar 🏛️🛡️🚀

- **Added**: `tools/continuity_legacy/heal_parity.py` - Self-healing engine for document markers.

- **Improved**: `run_continuity_cycle.py` with actionable healing suggestions and detailed notifications.

- **Added**: Automated PyPI release workflow in `.github/workflows/continuity.yml`.

- **Added**: `tests/test_logic.py` - Core reliability suite with unit tests for parity checks.



## [3.0.0] - 2026-04-01: Modular Heritage 🏗️🧠🛡️



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



## [1.0.0] - 2026-03-31: Initial Release () 💎

- First manual framework for continuity and document parity.

- Core logic for `STATE.json`, `ROADMAP.md`, and `.continuity/` surfaces.



---

*Created by Ethernium. Optimized for AI-Human pair programming.*

---
*Continuity Legacy: Protecting the logical lineage of your software.*
