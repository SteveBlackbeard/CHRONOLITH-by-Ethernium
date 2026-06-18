# Ethernium AgentOps

This folder is intentionally separate from Continuity Legacy.

It can live temporarily inside this repository for incubation, but it is designed to be extracted into its own repository or product.

## What This Tool Is

Ethernium AgentOps is a provider-neutral operating layer for reducing AI agent cost, context waste, retries, and coordination drift.

It focuses on:

- model routing
- local/cloud task splitting
- task packet templates
- context compaction
- credit usage tracking
- batch workflows
- clean-room reverse engineering of agent control patterns

## What This Tool Is Not

It is not:

- part of the Continuity Legacy runtime
- part of the PyPI package
- part of Continuity governance
- a copy of leaked prompts
- a provider bypass tool
- a storage place for proprietary hidden instructions

## Extraction Rule

This folder should be removable without breaking Continuity:

```text
AGENTOPS_TOOL/
```

## Clean-Room Rule

Reverse engineer the economics and control system, not proprietary text.

Allowed:

- study public behavior
- identify reusable control patterns
- rebuild them as local, provider-neutral primitives
- measure cost, retries, and context size

Not allowed:

- copying leaked prompts
- using hidden vendor policies as source material
- impersonating another provider's model behavior
- adding jailbreak collections

## Current Status

```text
status: incubation
relationship_to_continuity: none
safe_to_extract: true
```
