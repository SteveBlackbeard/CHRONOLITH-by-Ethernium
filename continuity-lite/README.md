# Continuity Legacy Lite

![Version](https://img.shields.io/badge/version-3.0.3-blueviolet)

Continuity Legacy Lite is part of the Ethernium Continuity Python runtime.

## Install

```bash
pip install ethernium-continuity-lite
```

## Commands

```bash
continuity-lite --help
```

## Role

Minimal local continuity for fast handoffs, state checks, and lightweight CLI workflows.

## Governance Boundary

Continuity Legacy is the Python runtime and governance kernel. Continuity Conekta is an external visual control surface, and AgentOps is an extractable incubated tool.

## Quality Gate

Before release, run the root repository checks:

```bash
python scripts/health_guard.py --strict
python scripts/golden_baseline.py verify
pytest -q
python -m build
python -m twine check dist\*
```
