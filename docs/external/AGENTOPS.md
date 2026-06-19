# Robin Hood by Ethernium

Robin Hood by Ethernium is the externalized successor to the AgentOps incubation folder.

Planned repository:

```text
https://github.com/SteveBlackbeard/robin-hood-by-ethernium
```

Local extracted path:

```text
D:\Experimentos\robin-hood-by-ethernium
```

## Role

Robin Hood owns:

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

From the Robin Hood repository:

```powershell
cd D:\Experimentos\robin-hood-by-ethernium
pip install -e .
agentops health --strict
agentops scan --path adversarial_cases --source repo --fail-on-block
```

Optional MCP server:

```powershell
cd D:\Experimentos\robin-hood-by-ethernium
pip install -e .[mcp]
agentops-mcp
```

## Boundary

Do not import Robin Hood from Continuity Legacy runtime code.

Do not package Robin Hood into Continuity Legacy PyPI artifacts.
