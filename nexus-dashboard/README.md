# Nexus Dashboard

`nexus-dashboard` is the visual command surface for CONTINUITY LEGACY. It renders the sovereign core, live telemetry, forensic rails, document reading, and the linked-system ecosystem around the central runtime.

## Runtime model

- `CONTINUITY LEGACY` remains the metacore at the center of the graph.
- Linked projects are modeled as sovereign spheres, not as a single merged blob.
- The default view is `ecosystem overview`: multiple linked systems remain visible while one system can be active and focused.
- Large linked systems expand with adaptive rings:
  - `DASHBOARD`
  - `AGENTS`
  - `DOCUMENTS`
  - `TOOLS`
  - `SYSTEM`

## Current capabilities

- Live dashboard signals derived from state, drift, chain integrity, actions, and linked-system count.
- Multi-system HUD inventory with active system selection and unlink controls.
- 3D ecosystem graph with active/inactive sphere hierarchy.
- Manual camera movement with focus, reset, next-document, and cycle-system controls.
- Best-effort document reading for text files that are resolvable by the local dashboard runtime.
- Per-system watch streams and per-system event labeling when the linked path is available to the backend.

## Development

Run the dashboard locally from `nexus-dashboard`:

```bash
npm install
npm run dev
```

Open `http://localhost:3000`.

Production validation:

```bash
npm run build
```

## Local AI bridge

The dashboard now includes a `CHAT` rail that can talk to a local conversational backend through `/api/chat/bridge`.

To move the dashboard by USB to another machine:

1. Copy the repo.
2. In `nexus-dashboard`, copy `.env.example` to `.env.local`.
3. Set `CONTINUITY_CHAT_PROVIDER` to one of:
   - `openclaw`
   - `ollama`
   - `moltbot`
4. Point the corresponding `*_BASE_URL` to the local service on that machine.
5. Start the dashboard with:

```bash
npm install
npm run start
```

Example `Ollama` setup:

```bash
CONTINUITY_CHAT_PROVIDER=ollama
CONTINUITY_OLLAMA_ENABLED=true
CONTINUITY_OLLAMA_BASE_URL=http://127.0.0.1:11434
CONTINUITY_OLLAMA_MODEL=llama3.1
```

Example `OpenClaw` setup:

```bash
CONTINUITY_CHAT_PROVIDER=openclaw
CONTINUITY_OPENCLAW_ENABLED=true
CONTINUITY_OPENCLAW_BASE_URL=http://127.0.0.1:3001
```

The bridge is intentionally local-first. Start in conversational/read-only mode, then expose action routing only after the local tool-calling layer is stable.

## Package/runtime boundary

`nexus-dashboard` should be treated as the control surface, not the source of truth for the runtime package.

If you publish `ethernium-continuity-legacy` (or `lite/pro/omega`) to PyPI, keep this rule:

- only claim package commands that the package CLI actually exposes
- do not assume every dashboard button already has a one-to-one package command
- prefer an explicit local adapter layer between dashboard and packaged runtime

## Notes

- Browser-linked directories do not expose absolute filesystem paths. When a linked system cannot be resolved directly by the backend, the dashboard falls back to a structural node model instead of failing visually.
- Inter-system bridges are intentionally not rendered unless a real operational or cryptographic relationship is modeled in runtime state.
- Public ecosystem behavior should be documented here only after the runtime behavior is stable enough to trust as a real capability.
