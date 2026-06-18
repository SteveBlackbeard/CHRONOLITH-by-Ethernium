# AgentOps Governance Seed

AgentOps is an incubated tool, not part of Continuity Legacy.

## Golden Rules

- Keep AgentOps extractable as a standalone repository.
- Do not import AgentOps from Continuity Legacy runtime code.
- Do not package AgentOps into Continuity Legacy PyPI artifacts.
- Use clean-room engineering only: patterns, economics, routing, and measurement are allowed; leaked prompts or proprietary hidden instructions are not.
- Prefer measurable credit/context reduction over narrative expansion.

## Health Gate

AgentOps is considered healthy when:

- `TOOL_MANIFEST.json` is valid JSON.
- `README.md` states the boundary from Continuity Legacy.
- `BLUEPRINT.md` describes the workflow without provider-specific hidden text.
- No leaked prompt text, jailbreak collections, or vendor-imitation instructions are stored in this folder.

## Extraction Contract

This directory must remain removable:

```text
AGENTOPS_TOOL/
```

Removing it must not break:

- Python package imports
- tests
- build
- golden baseline verification
- Continuity Conekta

## Maturity Levels

- `incubation`: docs and manifest only.
- `prototype`: local scripts exist and have tests.
- `tool`: installable package or executable exists.
- `product`: separate repo, CI, release notes, and user docs exist.

Current level:

```text
incubation
```
