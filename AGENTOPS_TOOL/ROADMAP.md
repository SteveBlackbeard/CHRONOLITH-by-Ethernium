# AgentOps Roadmap

## Phase 0: Incubation

Status: complete.

Deliverables:

- README
- governance seed
- rulebook
- frugality doctrine
- threat model
- extraction contract
- manifest

Acceptance:

- no leaked prompts
- no runtime dependency on Continuity Legacy
- clear value thesis: reduce cost, risk, and drift

## Phase 1: Minimal Executable Tool

Status: complete.

Build:

- `agentops/health_guard.py`
- `agentops/context_packet.py`
- `agentops/frugality_ledger.py`
- `agentops/prompt_firewall.py`
- `agentops/capability_broker.py`
- `agentops/cli.py`
- `tests/`

Acceptance:

- validates manifest and docs
- writes JSONL usage entries
- emits a context packet from a template
- scans text/files for basic prompt risk
- checks scoped capabilities
- runs locally without network

## Phase 2: Defensive Intelligence

Status: current.

Build:

- `adversarial_cases/`
- stronger prompt firewall detectors
- machine-readable mitigation reports

Acceptance:

- labels untrusted inputs
- detects common injection markers
- flags zero-width and suspicious Unicode
- checks tool permission scope
- runs tests against benign adversarial cases

## Phase 3: Provider-Neutral Scorecard

Build:

- `provider_profiles.json`
- scorecard command
- routing recommendations

Acceptance:

- compares model cost, latency, context, and reliability
- stores observations without proprietary prompts
- recommends local/cloud routing

## Phase 4: Standalone Repository

Build:

- `pyproject.toml`
- CI
- release notes
- installation docs

Acceptance:

- AgentOps is extracted from Continuity Legacy
- tests pass in its own repo
- no private Continuity file is required

## Deferred

Do not build until later:

- dashboard
- database
- blockchain anchoring
- autonomous multi-agent daemon
- provider-specific prompt emulation
- complex self-healing loops
