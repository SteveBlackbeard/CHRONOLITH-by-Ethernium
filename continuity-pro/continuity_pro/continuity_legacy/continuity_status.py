from __future__ import annotations

import argparse
from pathlib import Path

try:
    from .automation_common import (
        Color,
        continuity_report_path,
        echo,
        load_config,
        read_json,
        resolve_repo_root,
    )
except (ImportError, ValueError):
    from automation_common import (
        Color,
        continuity_report_path,
        echo,
        load_config,
        read_json,
        resolve_repo_root,
    )


def display_status(repo_root: str | Path) -> None:
    root = resolve_repo_root(repo_root, __file__)
    config = load_config(root)
    report = read_json(continuity_report_path(root, config))

    if not report:
        echo("No continuity report found. Please run 'python tools/continuity_legacy/run_continuity_cycle.py' first.", Color.YELLOW)
        return

    echo(f"\n{Color.BOLD}--- {config.get('project_name')} CONTINUITY DASHBOARD ---{Color.END}")
    
    # Phase & Action
    phase = report.get("phase", "Unknown")
    echo(f"Phase: {Color.CYAN}{phase}{Color.END}")
    
    next_action = report.get("next_action_1", "None defined")
    echo(f"Next Action: {Color.GREEN}{next_action}{Color.END}")
    
    # Grid status
    echo(f"\n{Color.UNDERLINE}System Health:{Color.END}")
    
    def format_status(val: str) -> str:
        if val == "ok":
            return f"{Color.GREEN}✔ OK{Color.END}"
        if val == "attention_required":
            return f"{Color.RED}✘ ATTENTION REQUIRED{Color.END}"
        return f"{Color.YELLOW}⚠ {val.upper()}{Color.END}"

    echo(f"Overall Status:       {format_status(report.get('status', 'unknown'))}")
    echo(f"Document Parity:      {format_status(report.get('doc_parity_status', 'unknown'))}")
    echo(f"System Membership:    {format_status(report.get('membership_status', 'unknown'))}")
    echo(f"Internal Files:       {format_status(report.get('internal_paths_status', 'unknown'))}")
    
    if report.get("external_sync_status") != "skipped":
        echo(f"External Sync:       {format_status(report.get('external_sync_status', 'unknown'))}")
        echo(f"External Phase:      {format_status(report.get('external_phase_status', 'unknown'))}")

    # Missing items
    missing = report.get("internal_missing_paths", [])
    if missing:
        echo(f"\n{Color.RED}Missing Mandatory Files:{Color.END}")
        for path in missing:
            echo(f"  - {path}", Color.RED)

    echo(f"\n{Color.BOLD}Report generated at:{Color.END} {report.get('generated_at')}")
    echo("-" * 40)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="View the current project continuity status.")
    parser.add_argument("--repo-root", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    display_status(args.repo_root)


if __name__ == "__main__":
    main()
