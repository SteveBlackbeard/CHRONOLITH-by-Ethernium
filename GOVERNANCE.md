# Chronolith: Project Governance & Resilience

This document defines the technical management and long-term sustainability of the **Chronolith** framework.

## 1. Decision Protocol

All architectural changes are evaluated through the project governance contract, feature registry, and verification checks before they become part of the release baseline.

## 2. Succession & Chronolith

To reduce maintainer abandonment risk, the project's chronolith files (`.chronolith/DECISIONS_LOG.md`, `.chronolith/LIVE_HANDOFF.md`, `STATE.json`) serve as canonical context for future maintainers and agents.

## 3. Contributions

Technical contributions are welcome when they pass the required validation checks:

```text
python scripts/health_guard.py --strict
pytest -q
```

Changes that touch runtime behavior, release metadata, cryptographic state, public CLI behavior, or frozen paths should include a change contract based on `docs/CHANGE_CONTRACT_TEMPLATE.md`.

## 4. Sintergic Evolution Mandate: ABSORB & ADAPT

Existing code, lore, and logic should not be overwritten during a system upgrade without an explicit contract and rollback path.

- **Absorb:** Integrate new functionality into the existing ownership model where possible.
- **Adapt:** Preserve legacy intent while translating it into maintainable, testable implementation.
- **Inherit:** When duplication exists, prefer canonical modules, proxies, adapters, or migration notes over silent replacement.

This mandate protects chronolith lineage while keeping the repository practical, auditable, and releasable.

---
*Chronolith: Protecting the logical lineage of your software.*
