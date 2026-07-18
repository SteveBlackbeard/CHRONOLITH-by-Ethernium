# Chronolith Lite

![Version](https://img.shields.io/badge/version-3.0.3-blueviolet)

Chronolith Lite is part of the Ethernium Chronolith Python runtime.

## Install

```bash
pip install chronolith-lite
```

## Commands

```bash
chronolith-lite --help
```

## Role

Minimal local chronolith for fast handoffs, state checks, and lightweight CLI workflows.

## Governance Boundary

Chronolith is the Python runtime and governance kernel. Chronolith Conekta is an external visual control surface, and AgentOps is an extractable incubated tool.

## Quality Gate

Before release, run the root repository checks:

```bash
python scripts/health_guard.py --strict
python scripts/golden_baseline.py verify
pytest -q
python -m build
python -m twine check dist\*
```
