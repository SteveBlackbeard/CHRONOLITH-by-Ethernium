# CONEKTA

CONEKTA is the externalized dashboard/control-surface successor to Chronolith Conekta.

Planned repository:

```text
https://github.com/SteveBlackbeard/CONEKTA-by-Ethernium
```

Local extracted path:

```text
D:\Experimentos\CONEKTA
```

## Role

CONEKTA owns:

- web dashboard
- visual control surface
- 3D ecosystem graph
- operator UI
- local chat bridge UI
- browser/runtime adapters

Chronolith owns:

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
CONEKTA UI -> local adapter/API -> Chronolith CLI/runtime -> STATE.json / reports
```

## Bootstrap

The local bootstrap script can point at the external CONEKTA path:

```powershell
.\scripts\bootstrap-local-machine.ps1 -ConektaPath ..\CONEKTA
```

## Boundary

Do not reinsert the dashboard into Chronolith.

Do not make the Python packages depend on the CONEKTA web runtime.
