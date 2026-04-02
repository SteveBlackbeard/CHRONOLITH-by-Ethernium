# Contributing to CONTINUITY LEGACY 🤝🧬

We value technical excellence, contextual fidelity, and clean code. Every contribution must pass the **STRICT CYCLE** check.

## 1. Getting Started
- Read the **[GOVERNANCE.md](./GOVERNANCE.md)** to understand our long-term vision.
- Choose the edition you want to improve: **[Lite](./CONTINUITY%20LEGACY%20Lite)**, **[Pro](./CONTINUITY%20LEGACY%20Pro)**, or **[Omega](./CONTINUITY%20LEGACY%20Omega)**.

## 2. The Golden Rule: Parity First
Before pushing any code, you **MUST** run the continuity cycle of the corresponding edition:
```bash
# Example for Pro
python "CONTINUITY LEGACY Pro/tools/continuity_legacy/run_continuity_cycle.py" --strict
```
If the cycle fails, the contribution will be rejected. We do not accept structural drift.

## 3. Pull Request Protocol
1.  **Strategic Intent**: Explain "why" the change is needed in terms of project continuity.
2.  **Update Memory**: Ensure your PR includes the necessary updates to `.continuity/DECISIONS_LOG.md`.
3.  **Tests**: If you add logic, you **must** add a test in the `tests/` folder of that edition.

## 4. Maintainer Succession
If you are interested in becoming a core maintainer, start by consistently improving the **Lite** version. We promote contributors based on their ability to maintain context and technical rigor.

---
*Thank you for helping us protect the logical lineage of software.*
