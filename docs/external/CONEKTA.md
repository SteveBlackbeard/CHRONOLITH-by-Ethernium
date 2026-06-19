# Conekta Dev by Ethernium

Conekta Dev by Ethernium is the externalized dashboard/control-surface successor to Continuity Conekta.

Planned repository:

```text
https://github.com/SteveBlackbeard/conekta-dev-by-ethernium
```

Local extracted path:

```text
D:\Experimentos\conekta-dev-by-ethernium
```

## Role

Conekta Dev owns:

- web dashboard
- visual control surface
- 3D ecosystem graph
- operator UI
- local chat bridge UI
- browser/runtime adapters

Continuity Legacy owns:

- Python package runtime
- Lite / Pro / Omega editions
- Merkle and state integrity
- governance kernel
- release safety

## Integration

The integration contract remains in:

```text
docs/CONEKTA_ADAPTER_CONTRACT.md
```

Recommended bridge:

```text
Conekta Dev UI -> local adapter/API -> Continuity Legacy CLI/runtime -> STATE.json / reports
```

## Bootstrap

The local bootstrap script can point at the external Conekta Dev path:

```powershell
.\scripts\bootstrap-local-machine.ps1 -ConektaPath ..\conekta-dev-by-ethernium
```

## Boundary

Do not reinsert the dashboard into Continuity Legacy.

Do not make the Python packages depend on the Conekta Dev web runtime.
