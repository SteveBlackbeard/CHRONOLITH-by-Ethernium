from __future__ import annotations

import argparse
from pathlib import Path

try:
    from .automation_common import external_root, load_config, read_text, resolve_repo_root
    from .context_loader import build_context_snapshot
except (ImportError, ValueError):
    from automation_common import external_root, load_config, read_text, resolve_repo_root
    from context_loader import build_context_snapshot


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def _snapshot_date(snapshot: dict) -> str:
    return str(snapshot.get("date") or "unknown")


def _build_current_state(snapshot: dict) -> str:
    truth = snapshot.get("truth", {})
    priority_zones = snapshot.get("priority_zones", [])
    next_actions = snapshot.get("next_actions", [])
    lines = [
        f"{snapshot.get('project_name', 'PROJECT')}DEV CURRENT STATE",
        f"date: {_snapshot_date(snapshot)}",
        f"phase: {snapshot.get('phase', 'unknown')}",
        "",
        "TRUTH",
    ]
    for key in sorted(truth):
        lines.append(f"- {key}: {truth[key]}")
    lines.extend(["", "PRIORITY ZONES"])
    for zone in priority_zones:
        lines.append(f"- {zone.get('path')} :: {zone.get('role')} -> {zone.get('next_phase')}")
    lines.extend(["", "NEXT ACTIONS"])
    for action in next_actions:
        lines.append(f"- {action}")
    return "\n".join(lines)


def _build_next_actions(snapshot: dict) -> str:
    lines = [f"{snapshot.get('project_name', 'PROJECT')}DEV NEXT ACTIONS", f"date: {_snapshot_date(snapshot)}", ""]
    for idx, action in enumerate(snapshot.get("next_actions", []), start=1):
        lines.append(f"{idx}. {action}")
    return "\n".join(lines)


def _build_readme(snapshot: dict, ext_name: str) -> str:
    next_action = snapshot.get("next_actions", ["none"])[0]
    return "\n".join(
        [
            ext_name,
            "",
            "Purpose:",
            "- external developer chronolith layer",
            "- plain-text handoff for any new human or AI operator",
            "",
            "Current phase:",
            f"- {snapshot.get('phase', 'unknown')}",
            "",
            "Next exact action:",
            f"- {next_action}",
            "",
            "Read first:",
            "- 00_BOOT\\BOOT_SEQUENCE.txt",
            "- 01_STATE\\CURRENT_STATE.txt",
            "- 01_STATE\\LIVE_HANDOFF.txt",
            "- 01_STATE\\NEXT_ACTIONS.txt",
            "- 02_GUIDES\\DEVELOPER_WORKFLOW.txt",
            "- 02_GUIDES\\CANONICAL_PATHS.txt",
            "- 02_GUIDES\\AUTOMATION_CYCLE.txt",
            "- 03_HISTORY\\DECISIONS_LOG.txt",
            "- 03_HISTORY\\TIMELINE.txt",
        ]
    )


def _build_boot_sequence(snapshot: dict) -> str:
    project_name = snapshot.get("project_name", "PROJECT")
    return "\n".join(
        [
            f"{project_name}DEV BOOT SEQUENCE",
            "",
            "READ ORDER FOR A NEW DEVELOPER OR AI",
            "1. README.txt",
            "2. 01_STATE\\CURRENT_STATE.txt",
            "3. 01_STATE\\LIVE_HANDOFF.txt",
            "4. 01_STATE\\NEXT_ACTIONS.txt",
            "5. 02_GUIDES\\DEVELOPER_WORKFLOW.txt",
            "6. 02_GUIDES\\CANONICAL_PATHS.txt",
            "7. 02_GUIDES\\AUTOMATION_CYCLE.txt",
            "8. 03_HISTORY\\DECISIONS_LOG.txt",
            "9. 03_HISTORY\\TIMELINE.txt",
            "10. Then read inside the repo:",
            "   - PROJECT_CONTEXT.md",
            "   - STATE.json",
            "   - ROADMAP.md",
            "   - .chronolith/CONTEXT_CHRONOLITH.md",
            "   - .chronolith/LIVE_HANDOFF.md",
            "   - .chronolith/DECISIONS_LOG.md",
            "   - .chronolith/TIMELINE.md",
            "",
            "FIRST RESPONSE MUST INCLUDE",
            "- current phase",
            "- last completed milestone",
            "- next exact action",
            "- current target zone",
            "- active risks",
        ]
    )


def _build_workflow() -> str:
    return "\n".join(
        [
            "DEVELOPER WORKFLOW",
            "",
            "MANDATORY ORDER",
            "1. scan",
            "2. analyze",
            "3. classify",
            "4. implement",
            "5. verify",
            "6. chronolith closeout",
            "",
            "MANDATORY RULES",
            "- analyze before improving or innovating",
            "- update canonical memory with relevant changes",
            "- prefer reversible changes",
            "- do not trust chat memory as canonical context",
        ]
    )


def _build_canonical_paths(repo_root: Path, ext_root: Path) -> str:
    lines = [
        "CANONICAL PATHS",
        "",
        "ROOT",
        f"- {repo_root}",
        "",
        "CANONICAL MEMORY",
        f"- {repo_root / 'PROJECT_CONTEXT.md'}",
        f"- {repo_root / 'STATE.json'}",
        f"- {repo_root / 'ROADMAP.md'}",
        f"- {repo_root / '.chronolith'}",
        "",
        "OUTPUTS",
        f"- {repo_root / 'outputs' / 'chronolith' / 'context_bootstrap_summary.json'}",
        f"- {repo_root / 'outputs' / 'chronolith' / 'chronolith_cycle_report.json'}",
        "",
        "EXTERNAL DOCS",
        f"- {ext_root}",
    ]
    return "\n".join(lines)


def _build_automation_cycle(repo_root: Path) -> str:
    command = f"python tools/chronolith/run_chronolith_cycle.py --repo-root {repo_root} --strict"
    return "\n".join(
        [
            "AUTOMATION CYCLE",
            "",
            "PRIMARY COMMAND",
            f"- {command}",
            "",
            "WHAT IT DOES",
            "1. rebuilds the internal chronolith bootstrap snapshot",
            "2. syncs external developer docs if enabled",
            "3. validates document parity",
            "4. validates system membership",
            "5. checks internal and external phase parity when external docs are enabled",
            "6. writes a chronolith report",
        ]
    )


def _build_external_handoff(repo_root: Path, snapshot: dict) -> str:
    handoff_path = repo_root / ".chronolith" / "LIVE_HANDOFF.md"
    handoff_excerpt = read_text(handoff_path).splitlines()[:24] if handoff_path.exists() else []
    lines = [f"{snapshot.get('project_name', 'PROJECT')}DEV LIVE HANDOFF", ""]
    lines.extend(handoff_excerpt or ["No internal handoff found."])
    return "\n".join(lines)


def _build_history_copy(repo_root: Path, rel_path: str, title: str) -> str:
    source = repo_root / rel_path
    if not source.exists():
        return title + "\n"
    return read_text(source)


def sync_external_dev_context(repo_root: str | Path, external_root_override: str | Path | None = None) -> dict:
    repo_root = resolve_repo_root(repo_root, __file__)
    config = load_config(repo_root)
    ext_root = external_root(repo_root, config, external_root_override)
    if ext_root is None:
        return {"status": "skipped", "reason": "external_docs_disabled"}

    snapshot = build_context_snapshot(repo_root, ext_root)
    ext_name = Path(ext_root).name

    _write_text(Path(ext_root) / "README.txt", _build_readme(snapshot, ext_name))
    _write_text(Path(ext_root) / "00_BOOT" / "BOOT_SEQUENCE.txt", _build_boot_sequence(snapshot))
    _write_text(Path(ext_root) / "01_STATE" / "CURRENT_STATE.txt", _build_current_state(snapshot))
    _write_text(Path(ext_root) / "01_STATE" / "LIVE_HANDOFF.txt", _build_external_handoff(repo_root, snapshot))
    _write_text(Path(ext_root) / "01_STATE" / "NEXT_ACTIONS.txt", _build_next_actions(snapshot))
    _write_text(Path(ext_root) / "02_GUIDES" / "DEVELOPER_WORKFLOW.txt", _build_workflow())
    _write_text(Path(ext_root) / "02_GUIDES" / "CANONICAL_PATHS.txt", _build_canonical_paths(repo_root, Path(ext_root)))
    _write_text(Path(ext_root) / "02_GUIDES" / "AUTOMATION_CYCLE.txt", _build_automation_cycle(repo_root))
    _write_text(Path(ext_root) / "03_HISTORY" / "DECISIONS_LOG.txt", _build_history_copy(repo_root, ".chronolith/DECISIONS_LOG.md", "DECISIONS LOG"))
    _write_text(Path(ext_root) / "03_HISTORY" / "TIMELINE.txt", _build_history_copy(repo_root, ".chronolith/TIMELINE.md", "TIMELINE"))

    return {"status": "ok", "external_root": str(ext_root)}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync optional external developer chronolith docs.")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--external-root", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = sync_external_dev_context(args.repo_root, args.external_root)
    for key, value in report.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
