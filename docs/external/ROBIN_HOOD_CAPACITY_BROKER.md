# ROBIN HOOD Capacity Broker Contract

## Purpose

The capacity broker is a planned ROBIN HOOD by Ethernium layer for routing AI work across local models, cloud APIs, LoRA-served variants, and compatible provider endpoints.

Its purpose is not to exploit free tokens. Its purpose is to spend the minimum responsible compute while preserving quality, privacy, and reliability.

## Why It Belongs Outside Continuity Legacy

Continuity Legacy is the governed Python continuity runtime:

- baseline verification
- rulebook and feature registry
- release gates
- state integrity
- Lite / Pro / Omega packages

The capacity broker is operational infrastructure:

- provider credentials
- quota status
- pricing
- local model availability
- failover
- quality telemetry
- API invocation

Those concerns change quickly and may involve secrets. They should not be embedded into the Continuity Legacy PyPI runtime.

## Relationship

```text
Continuity Legacy -> governance contracts, state, release integrity
ROBIN HOOD       -> token economy, context selection, provider routing
CONEKTA          -> visual command surface
```

Continuity may define the contract. ROBIN HOOD executes the routing.

## Routing Inputs

A route decision should accept:

- task objective
- task class
- context token estimate
- selected files or changed-context packet
- privacy mode
- max escalation level
- minimum quality class
- max cost per run
- preferred latency
- allowed providers
- blocked providers
- required capabilities

## Provider Profile

Each provider/model/adapter should be represented as data:

```json
{
  "id": "local-llama-code",
  "provider": "ollama",
  "endpoint": "http://127.0.0.1:11434",
  "model": "codellama",
  "privacy": "local",
  "context_window": 32768,
  "input_cost_per_million": 0,
  "output_cost_per_million": 0,
  "quota_policy": "local-capacity",
  "capabilities": ["code", "summarize", "local"],
  "quality_class": "medium",
  "enabled": true
}
```

Secrets must come from environment variables or local secret stores, never committed config.

## Route Score

The broker should select a route using a transparent score:

```text
score =
  quality_fit
  + context_fit
  + privacy_fit
  + reliability
  - estimated_cost
  - latency_penalty
  - quota_pressure
  - security_risk
```

Free or promotional APIs are allowed only if they pass quality, privacy, quota, and terms checks.

## Failover

Failover should trigger on:

- quota exhausted
- rate limit
- repeated timeout
- provider health failure
- context too large
- blocked privacy mode
- quality gate failure

Failover must be logged with the reason.

## Minimum First Version

Build in ROBIN HOOD, not Continuity:

- `providers.json`
- provider profile loader
- dry-run route command
- quota/capacity fields
- failover recommendation
- no real API calls by default
- optional adapters only after dry-run is stable

Suggested CLI:

```powershell
robinhood providers
robinhood route --objective "release review" --privacy local-first
robinhood broker dry-run --objective "fix bug" --changed agentops/cli.py
```

## Acceptance

The first useful version should:

- run without network
- never require API keys
- explain why one route was selected
- explain why other routes were rejected
- integrate with `snapshot`, `select`, `budget`, `route`, and `savings`
- keep Continuity Legacy free of provider runtime code
