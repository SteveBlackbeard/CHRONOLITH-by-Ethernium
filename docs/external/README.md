# External Tools

Continuity Legacy keeps external tools outside the repository root.

The Python runtime and governed release surface stay here. Visual dashboards, agent operations tools, token-frugality layers, and model-routing layers live in their own repositories or sibling workspaces.

## Tools

| Tool | Planned Repository | Local Path | Relationship |
| --- | --- | --- | --- |
| Conekta Dev by Ethernium | `https://github.com/SteveBlackbeard/conekta-dev-by-ethernium` | `D:\Experimentos\conekta-dev-by-ethernium` | External visual control surface |
| Robin Hood by Ethernium | `https://github.com/SteveBlackbeard/robin-hood-by-ethernium` | `D:\Experimentos\robin-hood-by-ethernium` | External agent-operations, token frugality, and MCP layer |

## Rule

Continuity Legacy may document contracts with these tools, but it must not import their runtime code or package their files into the Python distributions.
