# Contributing to CONTINUITY LEGACY 

We value technical excellence, contextual fidelity, and clean code. Every contribution must pass the **STRICT CYCLE** check.

## 1. Getting Started
- Read the **[GOVERNANCE.md](./GOVERNANCE.md)** to understand our long-term vision.
- Choose your edition: **[Lite](./CONTINUITY%20LEGACY%20Lite)**, **[Pro](./CONTINUITY%20LEGACY%20Pro)**, or **[Omega](./CONTINUITY%20LEGACY%20Omega)**.

## 2. The Golden Rule: Parity First
Before pushing any code, you **MUST** run the continuity cycle of the corresponding edition:
`ash
python "CONTINUITY LEGACY Pro/tools/continuity_legacy/run_continuity_cycle.py" --strict
`

## 3. Pull Request Protocol
1.  **Strategic Intent**: Explain "why" the change is needed.
2.  **Update Memory**: Ensure your PR includes updates to .continuity/DECISIONS_LOG.md.
3.  **Tests**: If you add logic, you **must** add a test in the 	ests/ folder.

---
*Thank you for helping us protect the logical lineage of software.*
