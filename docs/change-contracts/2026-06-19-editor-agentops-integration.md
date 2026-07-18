# Change Contract: Editor And AgentOps Integration

## Scope

Document editor and agent-host integration boundaries for Chronolith and AgentOps.

## Reason

Chronolith is already provider-neutral and editor-friendly through CLI, repository files, handoffs, and governance checks. The repository needed explicit documentation separating:

- Chronolith as the governed Python core
- AgentOps as the optional operations and MCP layer
- VS Code/Cursor integration as thin wrappers
- future model routing and LoRA/local LLM support as AgentOps responsibilities

## Files

- `README.md`
- `docs/CHRONOLITH_GOVERNANCE_KERNEL.md`
- `docs/EDITOR_AGENT_INTEGRATION.md`
- `AGENTOPS_TOOL/README.md`
- `AGENTOPS_TOOL/ROADMAP.md`
- `AGENTOPS_TOOL/PENDING.md`
- `AGENTOPS_TOOL/INTEGRATIONS.md`
- `AGENTOPS_TOOL/TOOL_MANIFEST.json`
- `AGENTOPS_TOOL/agentops/health_guard.py`
- `AGENTOPS_TOOL/agentops/mcp_server.py`
- `AGENTOPS_TOOL/tests/test_agentops.py`
- `AGENTOPS_TOOL/integrations/`
- `.cursor/rules/chronolith-agentops.mdc`

## Runtime Impact

No Chronolith runtime API changes.

AgentOps gains an optional MCP server entrypoint behind the `mcp` extra. The base AgentOps package remains dependency-free.

## Verification

Required:

- `python scripts\health_guard.py --strict`
- `pytest -q`
- `$env:PYTHONPATH="AGENTOPS_TOOL"; pytest AGENTOPS_TOOL\tests -q`
- `$env:PYTHONPATH="AGENTOPS_TOOL"; python -m agentops.cli health --strict`
- `python scripts\golden_baseline.py verify`

## Rollback

Revert this contract, the editor integration docs/templates, the optional MCP module, and refresh the golden baseline again after review.
