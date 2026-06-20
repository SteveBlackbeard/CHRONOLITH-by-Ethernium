# ROBIN HOOD

ROBIN HOOD is the externalized successor to the AgentOps incubation folder.

Planned repository:

```text
https://github.com/SteveBlackbeard/ROBIN-HOOD-by-Ethernium
```

Local extracted path:

```text
D:\Experimentos\ROBIN-HOOD
```

## Role

ROBIN HOOD owns:

- prompt-risk scanning
- least-privilege capability checks
- context packet generation
- frugality ledger
- optional MCP server
- future token budget engine
- future local/cloud/LoRA model routing
- future provider adapters for OpenAI-compatible APIs, local LLM servers, and LoRA-served variants

Continuity Legacy owns:

- repository continuity
- golden baseline verification
- governance kernel
- Lite / Pro / Omega Python packages
- release health checks

## Usage Beside Continuity

From the ROBIN HOOD repository:

```powershell
cd D:\Experimentos\ROBIN-HOOD
pip install -e .
agentops health --strict
agentops scan --path adversarial_cases --source repo --fail-on-block
```

Optional MCP server:

```powershell
cd D:\Experimentos\ROBIN-HOOD
pip install -e .[mcp]
agentops-mcp
```

## Boundary

Do not import ROBIN HOOD from Continuity Legacy runtime code.

Do not package ROBIN HOOD into Continuity Legacy PyPI artifacts.
