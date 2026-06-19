# Conekta Dev Adapter Contract

Conekta Dev by Ethernium is an external control surface. Continuity Legacy must expose stable, local-first integration points without depending on the Conekta Dev web app at package runtime.

## Boundary

Continuity Legacy owns:

- package commands
- state integrity
- Merkle/DNA checks
- governance checks
- release readiness

Conekta Dev owns:

- browser UI
- 3D graph
- local chat bridge presentation
- linked project visualization
- operator workflows

## Recommended Local API

The Conekta Dev adapter should use explicit endpoints or CLI wrappers:

```text
GET  /state
GET  /events
POST /actions/audit
POST /actions/scan
POST /actions/seal
POST /actions/crystallize
```

## Fail-Closed Rules

The adapter must fail closed when:

- Continuity Legacy is not installed
- `STATE.json` is invalid
- governance health check fails
- requested action is not available in the installed package version
- a command would mutate protected state without explicit confirmation

## Release Rule

Continuity Legacy releases must not require the Conekta Dev app to build or run. Conekta Dev has its own repository, checks, lint debt, and release process.
