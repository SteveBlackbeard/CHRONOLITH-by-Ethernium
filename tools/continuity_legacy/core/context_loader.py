from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .automation_common import (
    context_path,
    continuity_doc_path,
    external_root,
    load_config,
    read_text,
    roadmap_path,
    state_path,
)


EXTERNAL_BOOT_DOCS = [
    ("external_readme", "README.txt", "text"),
    ("external_boot", "00_BOOT/BOOT_SEQUENCE.txt", "text"),
    ("external_state", "01_STATE/CURRENT_STATE.txt", "text"),
    ("external_handoff", "01_STATE/LIVE_HANDOFF.txt", "text"),
    ("external_actions", "01_STATE/NEXT_ACTIONS.txt", "text"),
]


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _tail_lines(path: Path, limit: int = 40) -> str:
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    return "\n".join(lines[-limit:])


def _iter_internal_docs(repo_root: Path, config: dict) -> list[tuple[str, Path, str]]:
    return [
        ("context", context_path(repo_root, config), "text"),
        ("state", state_path(repo_root, config), "json"),
        ("roadmap", roadmap_path(repo_root, config), "text"),
        ("continuity", continuity_doc_path(repo_root, "CONTEXT_CONTINUITY.md", config), "text"),
        ("boot", continuity_doc_path(repo_root, "BOOT_SEQUENCE.md", config), "text"),
        ("handoff", continuity_doc_path(repo_root, "LIVE_HANDOFF.md", config), "text"),
        ("decisions_log", continuity_doc_path(repo_root, "DECISIONS_LOG.md", config), "text"),
        ("timeline", continuity_doc_path(repo_root, "TIMELINE.md", config), "text"),
    ]


def build_context_snapshot(
    repo_root: str | Path,
    external_root_override: str | Path | None = None,
) -> dict:
    repo_root = Path(repo_root).resolve()
    config = load_config(repo_root)
    documents: dict[str, dict] = {}

    for key, full_path, mode in _iter_internal_docs(repo_root, config):
        entry = {"path": str(full_path), "exists": full_path.exists(), "mode": mode}
        if full_path.exists():
            if mode == "json":
                entry["parsed"] = _read_json(full_path)
            else:
                entry["excerpt"] = read_text(full_path)[:4000]
                if key in {"decisions_log", "timeline"}:
                    entry["tail"] = _tail_lines(full_path)
        documents[key] = entry

    ext_root = external_root(repo_root, config, external_root_override)
    if ext_root and Path(ext_root).exists():
        for key, rel_path, mode in EXTERNAL_BOOT_DOCS:
            full_path = Path(ext_root) / rel_path
            entry = {"path": str(full_path), "exists": full_path.exists(), "mode": mode}
            if full_path.exists():
                entry["excerpt"] = read_text(full_path)[:4000]
            documents[key] = entry

    state = documents.get("state", {}).get("parsed", {})
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "date": state.get("date"),
        "phase": state.get("status"),
        "next_actions": state.get("next_actions", []),
        "priority_zones": state.get("priority_zones", []),
        "truth": state.get("truth", {}),
        "documents": documents,
        "template_name": config.get("template_name"),
        "project_name": config.get("project_name"),
        "project_slug": config.get("project_slug"),
        "external_root": str(ext_root) if ext_root else "",
    }


def summarize_snapshot(snapshot: dict) -> str:
    phase = snapshot.get("phase", "unknown")
    next_actions = snapshot.get("next_actions", [])
    priority_zones = snapshot.get("priority_zones", [])
    lines = [
        "CONTINUITY LEGACY BOOTSTRAP",
        f"project: {snapshot.get('project_name', 'unknown')}",
        f"phase: {phase}",
        f"next_action_1: {next_actions[0] if next_actions else 'none'}",
    ]
    if priority_zones:
        zone = priority_zones[0]
        lines.append(f"priority_zone: {zone.get('path')} ({zone.get('role')})")
    return "\n".join(lines)
