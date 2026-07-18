# Chronolith Governance Kernel

## Purpose

Chronolith should evolve first as a governance kernel for AI-assisted repositories, not as a larger lore archive or provider-specific agent wrapper.

The core transformation is:

> From Merkle-based continuity framework to governed chronolith kernel with contracts, checks, handoffs, and controlled memory decay.

## Product Boundary

Chronolith owns:

- repository chronolith
- cryptographic/project state integrity
- AI handoff discipline
- feature and module contracts
- rulebook validation
- drift detection
- release baseline verification
- context compaction and archival policy
- editor/agent readiness through CLI, files, and optional external integration wrappers

Chronolith does not own:

- provider-specific pricing
- model API routing
- LoRA serving
- editor-specific plugin runtime
- leaked third-party prompts
- external AI subscription strategy
- dashboard-only visual rules
- CONEKTA web application runtime
- the full Ethernium universe key map
- prompt dumps copied from other products

Those concerns belong in separate tools or documentation layers.

## Operating Model

### 1. Rulebook

A machine-readable rulebook defines what is allowed to change, what is frozen, what requires review, and what must be documented.

Recommended file:

```text
.chronolith/rulebook.json
```

Minimum fields:

- `version`
- `frozen_paths`
- `sensitive_paths`
- `required_documents`
- `required_checks`
- `change_contract_required_for`
- `rollback_required`
- `encoding_policy`

### 2. Feature Registry

A feature registry maps product capabilities to owners, modules, tests, rollback strategy, and maturity.

Recommended file:

```text
.chronolith/feature-registry.json
```

Minimum fields per feature:

- `id`
- `title`
- `status`
- `owner`
- `modules`
- `tests`
- `docs`
- `rollback`
- `risk`

### 3. Health Guard

The health guard is a local and CI-safe check that fails closed when the repository violates its governance contract.

Recommended file:

```text
scripts/health_guard.py
```

Initial checks:

- required files exist
- JSON files parse
- project version is consistent
- encoding corruption markers are absent
- frozen paths were not changed without contract
- sensitive paths require a registry update
- release checklist references current version
- `STATE.json` remains valid

### 4. Handoff Seal

The handoff seal records the state of a session without depending on chat history.

Recommended file:

```text
.chronolith/LIVE_HANDOFF.md
```

The handoff should include:

- current objective
- changed files
- pending checks
- unresolved decisions
- next safe action
- timestamp
- optional state hash

## Autophagy Layer

Autophagy is the part of Chronolith that prevents the repo from becoming cognitively overweight.

It should classify context into:

- `KEEP`: canonical and actively useful
- `FREEZE`: approved baseline, rarely edited
- `SUMMARIZE`: too long, should be compacted
- `ARCHIVE`: historical value, not active context
- `DELETE_CANDIDATE`: likely noise, never removed automatically

The autophagy layer should not delete files by itself. It should generate reports and require explicit human approval for destructive cleanup.

Recommended future file:

```text
scripts/autophagy_report.py
```

The first implementation is non-destructive. It reports attention targets but does not move, rewrite, or delete files.

## Applying Lessons From Frontier Agent Prompts

Public discussion around large system prompt leaks shows a useful engineering pattern, even when authenticity is not verified:

- strong tool permissions
- explicit browsing/search rules
- copyright and safety boundaries
- work packets instead of huge one-shot prompts
- artifact verification
- persistent checklists
- clear escalation rules
- concise final reporting

Chronolith can adopt these as design principles without copying leaked prompt text or depending on unverified proprietary material.

The safe translation is:

> Do not import leaked prompts. Extract product-agnostic control patterns and encode them as local contracts, checks, and docs.

## Clean-Room Reverse Engineering Principle

Chronolith may study external agent systems at the level of architecture, behavior, and failure modes, but it must not copy proprietary prompts, hidden instructions, or vendor-specific policy text.

The allowed method is clean-room, synergic reverse engineering:

- observe public behavior and public analysis
- identify the abstract control pattern
- name the engineering problem it solves
- design a native Chronolith equivalent
- implement it as code, schema, or verification
- document the reasoning and tradeoffs

Examples:

- A leaked prompt uses tool permissions -> Chronolith creates explicit local permission contracts.
- A frontier agent uses work packets -> Chronolith creates compact handoff/task packet schemas.
- A provider uses safety boundaries -> Chronolith creates repository-scoped fail-closed checks.
- A long prompt encodes many policies -> Chronolith converts policies into small rulebook entries and tests.

The target is not imitation. The target is a deeper mechanism:

> understand the governing pattern, then rebuild it as a deterministic, local, auditable Chronolith primitive.

## Synergic Frugality Principle

Chronolith should maximize quality and fidelity at the lowest responsible cost.

This is a golden rule for AI-assisted engineering, not a visual-design slogan:

- **Neural systems + symbolic programming**: neural models generate heuristics, candidates, summaries, textures, and analysis drafts; symbolic code validates contracts, syntax, baselines, package metadata, and release gates.
- **Biology + systems engineering**: prefer event-driven, changed-only work over continuous recomputation. Do not rerun, rerender, rescan, or resend context that has not changed.
- **Reverse engineering + cybersecurity**: study public behavior and bottlenecks, but rebuild native controls cleanly. Scan untrusted input, isolate risky material, and fail closed when structural corruption appears.
- **Low-code + advanced programming**: keep broad workflows declarative and easy to change; reserve low-level optimization for measured bottlenecks such as rendering loops, token packing, cache invalidation, and release-critical checks.

Operational translation:

```text
heuristic generation -> deterministic validation -> changed-only execution -> explicit escalation
```

Chronolith owns the deterministic validation layer. External tools such as ROBIN HOOD by Ethernium may own model routing, token frugality, prompt-risk scanning, and changed-context caching.

## Phase Plan

### Phase 1: Governance Baseline

Add:

- `.chronolith/rulebook.json`
- `.chronolith/feature-registry.json`
- `scripts/health_guard.py`
- CI step for the health guard

No runtime behavior changes.

### Phase 2: Handoff And Baseline

Add:

- `.chronolith/LIVE_HANDOFF.md`
- handoff seal command
- golden baseline manifest
- frozen-path check

The lightweight golden baseline lives at:

```text
.chronolith/golden-baseline.json
```

Verification:

```text
python scripts/golden_baseline.py verify
```

Refresh is an explicit maintainer action after reviewing the change:

```text
python scripts/golden_baseline.py refresh --contract docs/change-contracts/YYYY-MM-DD-short-name.md
```

### Phase 3: Autophagy

Add:

- cognitive weight report
- stale handoff detection
- duplicated instruction detection
- oversized docs warning
- archive recommendations

### Phase 4: Ecosystem Bridge

Add only if Chronolith becomes infrastructure for the wider Ethernium ecosystem:

- canonical key mapping
- external timestamp proof
- multi-repo registry
- cross-repo governance reports

## Decision

Start with Phase 1. It gives the highest benefit with the lowest risk and keeps Chronolith focused on its real identity: chronolith, integrity, and safe AI-assisted change.
