# ROBIN HOOD by Ethernium

ROBIN HOOD by Ethernium is the externalized successor to the AgentOps incubation folder.

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
- token budget estimation
- context packing under a token budget
- frugal model route recommendation
- changed-context snapshots
- token/cost savings estimates
- relevance selection for changed files and neighboring context
- future provider adapters for OpenAI-compatible APIs, local LLM servers, and LoRA-served variants
- future capacity broker / provider failover layer

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
robinhood health --strict
robinhood scan --path adversarial_cases --source repo --fail-on-block
robinhood snapshot --path . --input-cost-per-million 2 --runs 100
robinhood select --path . --changed agentops/cli.py --max-tokens 4000
```

Optional MCP server:

```powershell
cd D:\Experimentos\ROBIN-HOOD
pip install -e .[mcp]
robinhood-mcp
```

## Capacity Broker Direction

The next external layer should be a provider-neutral capacity broker connected to ROBIN HOOD.

It should not chase "free tokens" blindly. It should choose the cheapest sufficient route that preserves quality, privacy, quota health, and failure safety.

Target capability:

```text
task + context + privacy + budget -> recommended provider/model/adapter route
```

Allowed provider classes:

- OpenAI-compatible APIs
- Anthropic-compatible APIs
- local LLM servers
- Ollama
- LM Studio
- llama.cpp server
- vLLM
- LoRA-served variants
- promotional/free-tier APIs, only when terms, quality, privacy, and quota are acceptable

Routing constraints:

- never store provider secrets in repository files
- never send secret-like material to cloud providers
- prefer local routes for private or low-risk tasks
- use cloud routes only when quality, context length, or release/security risk justifies escalation
- fail over when quota, latency, errors, or quality gates degrade
- log estimated cost, selected route, fallback reason, and outcome

## Boundary

Do not import ROBIN HOOD from Continuity Legacy runtime code.

Do not package ROBIN HOOD into Continuity Legacy PyPI artifacts.

Continuity Legacy may publish governance schemas, contracts, and adapters that external tools consume, but provider routing and API invocation should remain outside the Continuity Legacy runtime package.
