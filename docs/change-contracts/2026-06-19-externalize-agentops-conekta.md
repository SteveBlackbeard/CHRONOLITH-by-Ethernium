# Change Contract: Externalize ROBIN HOOD And CONEKTA

## Scope

Remove AgentOps and Chronolith Conekta source/staging folders from Chronolith after confirming their successor tools exist outside the repository.

## Reason

Chronolith should remain the Python runtime, governance kernel, release surface, and documentation source of truth for Lite / Pro / Omega.

ROBIN HOOD and CONEKTA are separate products:

- ROBIN HOOD owns token frugality, prompt-risk scanning, capability checks, MCP, and future model routing.
- CONEKTA owns the visual dashboard/control surface.

Keeping their source folders inside Legacy makes the root look less professional and risks confusing package/runtime boundaries.

## External Paths

- ROBIN HOOD: `D:\Experimentos\ROBIN-HOOD`
- CONEKTA: `D:\Experimentos\CONEKTA`

## Planned Repositories

- `https://github.com/SteveBlackbeard/ROBIN-HOOD-by-Ethernium`
- `https://github.com/SteveBlackbeard/CONEKTA-by-Ethernium`

## Removed From Legacy

- `AGENTOPS_TOOL/`
- `CHRONOLITH_CONEKTA/`

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

Required in Chronolith:

- `python scripts\health_guard.py --strict`
- `python scripts\autophagy_report.py`
- `python scripts\golden_baseline.py verify`
- `pytest -q`

Required in extracted ROBIN HOOD:

- `cd D:\Experimentos\ROBIN-HOOD`
- `pytest tests -q`

Required in extracted CONEKTA before its own publication:

- `cd D:\Experimentos\CONEKTA`
- `npm run lint`
- `npm run build`

## Rollback

Restore `AGENTOPS_TOOL/` and `CHRONOLITH_CONEKTA/` from Git history if a blocking dependency is found, then refresh the golden baseline with a rollback contract.
