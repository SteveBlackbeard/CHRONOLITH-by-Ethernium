from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class Color:
    """Terminal color constants for standardized elite CLI feedback."""
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def echo(text: str, color: str = "") -> None:
    """Prints text to the console with optional color formatting.

    Args:
        text: The string to be printed.
        color: The ANSI color code to apply (e.g., Color.GREEN).
    """
    if color:
        print(f"{color}{text}{Color.END}")
    else:
        print(text)


DEFAULT_CONFIG = {
    "template_name": "CHRONOLITH",
    "project_name": "YOUR_PROJECT",
    "project_slug": "your_project",
    "context_file": "PROJECT_CONTEXT.md",
    "state_file": "STATE.json",
    "roadmap_file": "ROADMAP.md",
    "chronolith_dir": ".chronolith",
    "outputs_dir": "outputs/chronolith",
    "external_docs": {
        "enabled": False,
        "folder_name": "YOUR_PROJECTDEV",
        "root_override": "",
    },
    "metadata": {
        "generated_by": "Chronolith by Ethernium",
        "tool_version": "5.0.0",
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
        resolved = Path(repo_root).resolve()
    else:
        resolved = Path(current_file).resolve().parents[2]
        
    if not (resolved / "chronolith.json").exists() and not (resolved / ".chronolith").exists():
        raise ValueError(f"Security Warning: Path '{resolved}' does not appear to be a CHRONOLITH repository.")
        
    return resolved


def load_config(repo_root: Path) -> dict:
    """Loads and merges the chronolith.json configuration.

    Args:
        repo_root: The filesystem path to the root of the project.

    Returns:
        A dictionary containing the merged project configuration.
    """
    config_file = repo_root / "chronolith.json"
    payload = {}
    if config_file.exists():
        payload = json.loads(config_file.read_text(encoding="utf-8"))
    
    return _deep_merge(DEFAULT_CONFIG, payload)


def save_config(repo_root: Path, config: dict) -> None:
    """Saves the chronolith.json configuration to the repository root.

    Args:
        repo_root: The filesystem path to the root of the project.
        config: The configuration dictionary to persist.
    """
    config_file = repo_root / "chronolith.json"
    config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")


def config_path(repo_root: str | Path) -> Path:
    return Path(repo_root) / "chronolith.json"


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


def build_context_snapshot(repo_root: Path, external_root_override: Path | None = None) -> dict:
    """Builds a comprehensive snapshot of the project context from multiple sources.

    Args:
        repo_root: The root directory of the project.
        external_root_override: Optional path to an external documentation root.

    Returns:
        A dictionary containing the aggregated 'truth' of the project.
    """
    config = load_config(repo_root)
    state = read_json(state_path(repo_root, config), {})
    context_text = read_text(context_path(repo_root, config))
    roadmap_text = read_text(roadmap_path(repo_root, config))

    return {
        "project_name": config.get("project_name"),
        "project_slug": config.get("project_slug"),
        "phase": state.get("status", "unknown"),
        "next_actions": state.get("next_actions", []),
        "context_summary": context_text[:2000],
        "roadmap_summary": roadmap_text[:2000],
        "last_decision": state.get("last_decision", "none"),
        "timestamp": utc_now_iso(),
    }


def context_path(repo_root: str | Path, config: dict[str, Any] | None = None) -> Path:
    config = config or load_config(repo_root)
    return Path(repo_root) / config["context_file"]


def state_path(repo_root: str | Path, config: dict[str, Any] | None = None) -> Path:
    config = config or load_config(repo_root)
    return Path(repo_root) / config["state_file"]


def roadmap_path(repo_root: str | Path, config: dict[str, Any] | None = None) -> Path:
    config = config or load_config(repo_root)
    return Path(repo_root) / config["roadmap_file"]


def chronolith_dir(repo_root: str | Path, config: dict[str, Any] | None = None) -> Path:
    config = config or load_config(repo_root)
    return Path(repo_root) / config["chronolith_dir"]


def chronolith_doc_path(repo_root: str | Path, name: str, config: dict[str, Any] | None = None) -> Path:
    return chronolith_dir(repo_root, config) / name


def outputs_dir(repo_root: str | Path, config: dict[str, Any] | None = None) -> Path:
    config = config or load_config(repo_root)
    return Path(repo_root) / config["outputs_dir"]


def bootstrap_output_path(repo_root: str | Path, config: dict[str, Any] | None = None) -> Path:
    return outputs_dir(repo_root, config) / "context_bootstrap_summary.json"


def chronolith_report_path(repo_root: str | Path, config: dict[str, Any] | None = None) -> Path:
    return outputs_dir(repo_root, config) / "chronolith_cycle_report.json"


def dependency_map_path(repo_root: str | Path, config: dict[str, Any] | None = None) -> Path:
    return chronolith_dir(repo_root, config) / "registry" / "document_dependency_map.json"


def membership_registry_path(repo_root: str | Path, config: dict[str, Any] | None = None) -> Path:
    return chronolith_dir(repo_root, config) / "registry" / "system_membership_registry.json"


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


def is_ignored(repo_root: str | Path, rel_path: str) -> bool:
    ignore_file = Path(repo_root) / ".chronolithignore"
    if not ignore_file.exists():
        return False
    
    import fnmatch
    patterns = [line.strip() for line in ignore_file.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
    for pattern in patterns:
        if fnmatch.fnmatch(rel_path, pattern):
            return True
    return False


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


def calculate_sha256(path: str | Path) -> str:
    """Calculates the SHA-256 hash of a file for high-fidelity DNA synthesis."""
    import hashlib

    p = Path(path)
    if not p.exists():
        return ""
    return hashlib.sha256(p.read_bytes()).hexdigest()


def build_merkle_tree(hashes: list[str]) -> str:
    """RFC 6962 compliant Merkle Tree with leaf/node prefix hardening."""
    import hashlib

    if not hashes:
        return "0" * 64

    current_level = [hashlib.sha256(b"\x00" + h.encode("utf-8")).hexdigest() for h in sorted(hashes)]
    while len(current_level) > 1:
        next_level = []
        if len(current_level) % 2 != 0:
            current_level.append(current_level[-1])

        for i in range(0, len(current_level), 2):
            combined = b"\x01" + (current_level[i] + current_level[i + 1]).encode("utf-8")
            next_level.append(hashlib.sha256(combined).hexdigest())
        current_level = next_level

    return current_level[0]


build_merkle_root = build_merkle_tree
