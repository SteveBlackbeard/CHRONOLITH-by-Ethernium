# Editor And Agent Integration

Continuity Legacy is prepared for VS Code, Cursor, Codex, Claude, local LLMs, and other AI-assisted environments as a provider-neutral governance core.

It is not an editor extension and should not become one.

## Boundary

Continuity Legacy owns:

- repository continuity
- governed handoffs
- rulebook validation
- feature registry
- golden baseline verification
- release health checks
- token/cognitive-weight inspection through its existing token tools

Continuity Legacy does not own:

- model API routing
- LoRA serving
- provider-specific pricing
- editor-specific plugin logic
- dashboard runtime
- Robin Hood runtime

Those concerns belong to Robin Hood by Ethernium, Conekta Dev by Ethernium, or dedicated adapters.

## VS Code

Use VS Code tasks as a local convenience layer.

Recommended commands:

```powershell
python scripts\golden_baseline.py verify
python scripts\health_guard.py --strict
pytest -q
python -m build
```

Robin Hood can be used beside Continuity from its extracted repository:

```powershell
cd D:\Experimentos\robin-hood-by-ethernium
pip install -e .
agentops health --strict
agentops scan --path adversarial_cases --source repo --fail-on-block
```

Do not make VS Code tasks part of the runtime package.

## Cursor

Cursor should treat Continuity files as repository law:

- `.continuity/rulebook.json`
- `.continuity/feature-registry.json`
- `.continuity/LIVE_HANDOFF.md`
- `docs/CHANGE_CONTRACT_TEMPLATE.md`
- `docs/process/REPO_AND_PYPI_RELEASE_CHECKLIST.md`

Cursor rules may call Robin Hood for operational safety, but Cursor should not mix Robin Hood code into Continuity runtime.

## MCP

Continuity Legacy should not expose provider-specific model calls through MCP.

The better shape is:

```text
Editor / agent
  -> Robin Hood MCP tools
  -> Continuity CLI/scripts when repository governance is needed
```

This lets MCP hosts ask Robin Hood to scan, packet, and scope tasks while Continuity remains the canonical project governance layer.

## Antigravity And Other Hosts

Compatibility should be based on:

- CLI commands
- files in the workspace
- optional MCP tools
- no hidden editor assumptions

If a host can read the repository and run commands, it can use Continuity Legacy.

## Acceptance

Continuity Legacy is considered editor-ready when:

- governance checks run from terminal
- editor tasks are thin wrappers around those checks
- Cursor rules point to the rulebook and handoff files
- MCP integration stays outside the runtime
- Robin Hood remains external
