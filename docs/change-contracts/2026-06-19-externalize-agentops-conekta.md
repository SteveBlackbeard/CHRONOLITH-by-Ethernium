# Change Contract: Externalize Robin Hood And Conekta Dev

## Scope

Remove AgentOps and Continuity Conekta source/staging folders from Continuity Legacy after confirming their successor tools exist outside the repository.

## Reason

Continuity Legacy should remain the Python runtime, governance kernel, release surface, and documentation source of truth for Lite / Pro / Omega.

Robin Hood and Conekta Dev are separate products:

- Robin Hood owns token frugality, prompt-risk scanning, capability checks, MCP, and future model routing.
- Conekta Dev owns the visual dashboard/control surface.

Keeping their source folders inside Legacy makes the root look less professional and risks confusing package/runtime boundaries.

## External Paths

- Robin Hood: `D:\Experimentos\robin-hood-by-ethernium`
- Conekta Dev: `D:\Experimentos\conekta-dev-by-ethernium`

## Planned Repositories

- `https://github.com/SteveBlackbeard/robin-hood-by-ethernium`
- `https://github.com/SteveBlackbeard/conekta-dev-by-ethernium`

## Removed From Legacy

- `AGENTOPS_TOOL/`
- `CONTINUITY_CONEKTA/`

## Kept In Legacy

- `docs/external/README.md`
- `docs/external/AGENTOPS.md`
- `docs/external/CONEKTA.md`
- `docs/CONEKTA_ADAPTER_CONTRACT.md`
- `scripts/bootstrap-local-machine.ps1` with external `-ConektaPath`

## Runtime Impact

No Python runtime API changes.

No package metadata changes.

No PyPI release change.

## Verification

Required in Continuity Legacy:

- `python scripts\health_guard.py --strict`
- `python scripts\autophagy_report.py`
- `python scripts\golden_baseline.py verify`
- `pytest -q`

Required in extracted Robin Hood:

- `cd D:\Experimentos\robin-hood-by-ethernium`
- `pytest tests -q`

Required in extracted Conekta Dev before its own publication:

- `cd D:\Experimentos\conekta-dev-by-ethernium`
- `npm run lint`
- `npm run build`

## Rollback

Restore `AGENTOPS_TOOL/` and `CONTINUITY_CONEKTA/` from Git history if a blocking dependency is found, then refresh the golden baseline with a rollback contract.
