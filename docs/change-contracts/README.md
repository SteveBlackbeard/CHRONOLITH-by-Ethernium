# Change Contracts

This folder stores reviewed contracts for sensitive Chronolith changes.

Use a contract when changing:

- release metadata
- runtime behavior
- cryptographic state
- golden baseline hashes
- governance rules
- public CLI behavior
- frozen paths

Baseline refreshes should reference a contract file:

```text
python scripts/golden_baseline.py refresh --contract docs/change-contracts/YYYY-MM-DD-short-name.md
```
