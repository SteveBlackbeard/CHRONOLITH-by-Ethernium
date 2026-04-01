from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from core.automation_common import (
    bootstrap_output_path,
    continuity_report_path,
    load_config,
    read_text,
    resolve_repo_root,
    state_path,
    utc_now_iso,
)
from core.context_loader import build_context_snapshot
from doc_parity_check import check_doc_parity
from sync_external_dev_context import sync_external_dev_context
from system_membership_check import check_system_membership


INTERNAL_REQUIRED = [
    "PROJECT_CONTEXT.md",
    "STATE.json",
    "ROADMAP.md",
    ".continuity/CONTEXT_CONTINUITY.md",
    ".continuity/BOOT_SEQUENCE.md",
    ".continuity/LIVE_HANDOFF.md",
    ".continuity/DECISIONS_LOG.md",
    ".continuity/TIMELINE.md",
]

EXTERNAL_REQUIRED = [
    "README.txt",
    "00_BOOT/BOOT_SEQUENCE.txt",
    "01_STATE/CURRENT_STATE.txt",
    "01_STATE/LIVE_HANDOFF.txt",
    "01_STATE/NEXT_ACTIONS.txt",
    "02_GUIDES/DEVELOPER_WORKFLOW.txt",
    "02_GUIDES/CANONICAL_PATHS.txt",
    "02_GUIDES/AUTOMATION_CYCLE.txt",
    "03_HISTORY/DECISIONS_LOG.txt",
    "03_HISTORY/TIMELINE.txt",
]


def _extract_prefixed_value(text: str, prefix: str) -> str | None:
    prefix = prefix.lower()
    for line in text.splitlines():
        if line.lower().startswith(prefix):
            return line.split(":", 1)[1].strip()
    return None


def _extract_first_numbered_action(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("1. "):
            return stripped[3:].strip()
    return None


def _collect_path_status(base_root: Path, repo_root: Path, rel_paths: list[str]) -> list[dict]:
    import os
    return [
        {
            "path": os.path.relpath(base_root / rel_path, repo_root).replace("\\", "/"),
            "relative_path": rel_path,
            "exists": (base_root / rel_path).exists(),
        }
        for rel_path in rel_paths
    ]


def run_continuity_cycle(repo_root: str | Path, external_root_override: str | Path | None = None) -> dict:
    repo_root = resolve_repo_root(repo_root, __file__)
    config = load_config(repo_root)
    snapshot = build_context_snapshot(repo_root, external_root_override)

    bootstrap_path = bootstrap_output_path(repo_root, config)
    bootstrap_path.parent.mkdir(parents=True, exist_ok=True)
    bootstrap_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=True), encoding="utf-8")

    doc_parity = check_doc_parity(str(repo_root))
    membership = check_system_membership(str(repo_root))
    external_sync = sync_external_dev_context(repo_root, external_root_override)

    internal_paths = _collect_path_status(repo_root, repo_root, INTERNAL_REQUIRED)
    internal_missing = [item["relative_path"] for item in internal_paths if not item["exists"]]

    external_paths: list[dict] = []
    external_missing: list[str] = []
    external_phase_status = "skipped"
    external_next_action_status = "skipped"

    if external_sync.get("status") == "ok":
        ext_root = Path(external_sync["external_root"])
        external_paths = _collect_path_status(ext_root, repo_root, EXTERNAL_REQUIRED)
        external_missing = [item["relative_path"] for item in external_paths if not item["exists"]]
        state = json.loads(state_path(repo_root, config).read_text(encoding="utf-8"))
        current_state_text = read_text(ext_root / "01_STATE" / "CURRENT_STATE.txt")
        next_actions_text = read_text(ext_root / "01_STATE" / "NEXT_ACTIONS.txt")
        external_phase = _extract_prefixed_value(current_state_text, "phase:")
        external_next_action = _extract_first_numbered_action(next_actions_text)
        external_phase_status = "ok" if external_phase == state.get("status") else "attention_required"
        expected_next_action = state.get("next_actions", [None])[0]
        external_next_action_status = "ok" if external_next_action == expected_next_action else "attention_required"

    statuses = {
        "doc_parity_status": doc_parity["status"],
        "membership_status": membership["status"],
        "internal_paths_status": "ok" if not internal_missing else "attention_required",
        "external_sync_status": external_sync["status"],
        "external_paths_status": "ok" if not external_missing else ("skipped" if not external_paths else "attention_required"),
        "external_phase_status": external_phase_status,
        "external_next_action_status": external_next_action_status,
    }

    blocking_statuses = [
        statuses["doc_parity_status"],
        statuses["membership_status"],
        statuses["internal_paths_status"],
    ]
    if statuses["external_sync_status"] == "ok":
        blocking_statuses.extend(
            [
                statuses["external_paths_status"],
                statuses["external_phase_status"],
                statuses["external_next_action_status"],
            ]
        )

    overall_status = "ok" if all(status == "ok" for status in blocking_statuses) else "attention_required"
    report = {
        "generated_at": utc_now_iso(),
        "status": overall_status,
        "phase": snapshot.get("phase", "unknown"),
        "next_action_1": snapshot.get("next_actions", ["none"])[0],
        "project_name": snapshot.get("project_name"),
        "doc_parity_status": doc_parity["status"],
        "membership_status": membership["status"],
        "internal_paths_status": statuses["internal_paths_status"],
        "external_sync_status": statuses["external_sync_status"],
        "external_paths_status": statuses["external_paths_status"],
        "external_phase_status": statuses["external_phase_status"],
        "external_next_action_status": statuses["external_next_action_status"],
        "internal_missing_paths": internal_missing,
        "external_missing_paths": external_missing,
        "bootstrap_summary": os.path.relpath(bootstrap_path, repo_root).replace("\\", "/"),
        "report": os.path.relpath(continuity_report_path(repo_root, config), repo_root).replace("\\", "/"),
    }
    metadata = config.get("metadata", {})
    if metadata.get("include_in_reports"):
        report["metadata"] = {
            "generated_by": metadata.get("generated_by"),
            "tool_version": metadata.get("tool_version"),
            "creator": metadata.get("creator"),
        }

    report_path = continuity_report_path(repo_root, config)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the strict continuity closeout for this project.")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--external-root", default=None)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_continuity_cycle(args.repo_root, args.external_root)
    
    from core.automation_common import Color, echo
    
    echo("\nCONTINUITY LEGACY: Cycle completed.", Color.BOLD)
    echo(f"Status: {report['status'].upper()}")
    echo(f"Phase:  {report['phase']}")
    echo(f"Report: {report['report']}")

    if report["status"] != "ok":
        if args.strict:
            echo("\n[!] STRICT MODE: Inconsistencies detected. Blocking execution.", Color.RED)
            raise SystemExit(1)
        else:
            echo("\n[⚠] WARNING: Project state has drift. Run with --strict to enforce parity.", Color.YELLOW)
            echo("[*] Use 'python tools/continuity_legacy/continuity_status.py' for details.")
    else:
        echo("\n[✔] Project state is canonical and valid.", Color.GREEN)


if __name__ == "__main__":
    main()
