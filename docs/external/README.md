# External Tools

Continuity Legacy keeps external tools outside the repository root.

The Python runtime and governed release surface stay here. Visual dashboards, agent operations tools, token-frugality layers, and model-routing layers live in their own repositories or sibling workspaces.

## Tools

| Tool | Planned Repository | Local Path | Relationship |
| --- | --- | --- | --- |
| CONEKTA by Ethernium | `https://github.com/SteveBlackbeard/CONEKTA-by-Ethernium` | `D:\Experimentos\CONEKTA` | External visual control surface |
| ROBIN HOOD by Ethernium | `https://github.com/SteveBlackbeard/ROBIN-HOOD-by-Ethernium` | `D:\Experimentos\ROBIN-HOOD` | External agent-operations, token frugality, MCP, and capacity-routing layer |

## Rule

Continuity Legacy may document contracts with these tools, but it must not import their runtime code or package their files into the Python distributions.

See also:

- [ROBIN HOOD capacity broker contract](./ROBIN_HOOD_CAPACITY_BROKER.md)
