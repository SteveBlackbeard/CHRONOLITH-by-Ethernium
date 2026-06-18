# Continuity Legacy Pro

![Version](https://img.shields.io/badge/version-3.0.3-blueviolet)

Continuity Legacy Pro is part of the Ethernium Continuity Python runtime.

## Install

```bash
pip install ethernium-continuity-pro
```

## Commands

```bash
continuity-pro --help
```

## Role

Industrial continuity with stronger checks, hooks, parity diagnostics, and token/context tooling.

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
