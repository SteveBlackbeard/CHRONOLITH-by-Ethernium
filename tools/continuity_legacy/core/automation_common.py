from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = {
    "template_name": "CONTINUITY LEGACY",
    "project_name": "YOUR_PROJECT",
    "project_slug": "your_project",
    "context_file": "PROJECT_CONTEXT.md",
    "state_file": "STATE.json",
    "roadmap_file": "ROADMAP.md",
    "continuity_dir": ".continuity",
    "outputs_dir": "outputs/continuity",
    "external_docs": {
        "enabled": False,
        "folder_name": "YOUR_PROJECTDEV",
        "root_override": "",
    },
    "metadata": {
        "generated_by": "Continuity Legacy by Ethernium",
        "tool_version": "1.0.0",
        "creator": "@Steveblackbeard",
        "include_in_reports": True,
    },
}

ALLOWED_MEMBERSHIP_STATUSES = [
    "canonical",
    "bridge",
    "archive_source",
    "external_optional",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_repo_root(repo_root: str | Path | None, current_file: str | Path) -> Path:
    if repo_root:
        return Path(repo_root).resolve()
    return Path(current_file).resolve().parents[2]


def config_path(repo_root: str | Path) -> Path:
    return Path(repo_root) / "continuity_legacy.json"


def read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8", errors="ignore")


def write_text(path: str | Path, content: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.rstrip() + "\n", encoding="utf-8")


def read_json(path: str | Path, default: Any | None = None) -> Any:
    file_path = Path(path)
    if not file_path.exists():
        return deepcopy(default)
    return json.loads(file_path.read_text(encoding="utf-8"))


def write_json(path: str | Path, payload: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(repo_root: str | Path) -> dict[str, Any]:
    payload = read_json(config_path(repo_root), DEFAULT_CONFIG)
    if not payload:
        payload = deepcopy(DEFAULT_CONFIG)
    return _deep_merge(DEFAULT_CONFIG, payload)


def save_config(repo_root: str | Path, payload: dict[str, Any]) -> None:
    write_json(config_path(repo_root), payload)


def context_path(repo_root: str | Path, config: dict[str, Any] | None = None) -> Path:
    config = config or load_config(repo_root)
    return Path(repo_root) / config["context_file"]


def state_path(repo_root: str | Path, config: dict[str, Any] | None = None) -> Path:
    config = config or load_config(repo_root)
    return Path(repo_root) / config["state_file"]


def roadmap_path(repo_root: str | Path, config: dict[str, Any] | None = None) -> Path:
    config = config or load_config(repo_root)
    return Path(repo_root) / config["roadmap_file"]


def continuity_dir(repo_root: str | Path, config: dict[str, Any] | None = None) -> Path:
    config = config or load_config(repo_root)
    return Path(repo_root) / config["continuity_dir"]


def continuity_doc_path(repo_root: str | Path, name: str, config: dict[str, Any] | None = None) -> Path:
    return continuity_dir(repo_root, config) / name


def outputs_dir(repo_root: str | Path, config: dict[str, Any] | None = None) -> Path:
    config = config or load_config(repo_root)
    return Path(repo_root) / config["outputs_dir"]


def bootstrap_output_path(repo_root: str | Path, config: dict[str, Any] | None = None) -> Path:
    return outputs_dir(repo_root, config) / "context_bootstrap_summary.json"


def continuity_report_path(repo_root: str | Path, config: dict[str, Any] | None = None) -> Path:
    return outputs_dir(repo_root, config) / "continuity_cycle_report.json"


def dependency_map_path(repo_root: str | Path, config: dict[str, Any] | None = None) -> Path:
    return continuity_dir(repo_root, config) / "registry" / "document_dependency_map.json"


def membership_registry_path(repo_root: str | Path, config: dict[str, Any] | None = None) -> Path:
    return continuity_dir(repo_root, config) / "registry" / "system_membership_registry.json"


def load_dependency_map(repo_root: str | Path, config: dict[str, Any] | None = None) -> dict[str, Any]:
    return read_json(dependency_map_path(repo_root, config), {"version": "1.0", "documents": []}) or {
        "version": "1.0",
        "documents": [],
    }


def load_membership_registry(repo_root: str | Path, config: dict[str, Any] | None = None) -> dict[str, Any]:
    return read_json(
        membership_registry_path(repo_root, config),
        {
            "version": "1.0",
            "allowed_statuses": ALLOWED_MEMBERSHIP_STATUSES,
            "entries": [],
        },
    ) or {
        "version": "1.0",
        "allowed_statuses": ALLOWED_MEMBERSHIP_STATUSES,
        "entries": [],
    }


def external_root(
    repo_root: str | Path,
    config: dict[str, Any] | None = None,
    override: str | Path | None = None,
) -> Path | None:
    config = config or load_config(repo_root)
    external_cfg = config.get("external_docs", {})
    if override:
        return Path(override).resolve()
    root_override = str(external_cfg.get("root_override") or "").strip()
    if root_override:
        return Path(root_override).resolve()
    if not external_cfg.get("enabled"):
        return None
    return Path(repo_root).resolve().parent / str(external_cfg.get("folder_name") or "PROJECTDEV")
