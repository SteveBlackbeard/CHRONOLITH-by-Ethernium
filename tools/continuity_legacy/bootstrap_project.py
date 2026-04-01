from __future__ import annotations

import argparse
import json
from pathlib import Path

from core.automation_common import load_config, resolve_repo_root, save_config, write_text
from sync_external_dev_context import sync_external_dev_context


TOKEN_FILES = [
    "README.md",
    "PROJECT_CONTEXT.md",
    "ROADMAP.md",
    ".continuity/BOOT_SEQUENCE.md",
    ".continuity/CONTEXT_CONTINUITY.md",
    ".continuity/LIVE_HANDOFF.md",
    ".continuity/DECISIONS_LOG.md",
    ".continuity/TIMELINE.md",
]


def _replace_tokens(path: Path, replacements: dict[str, str]) -> None:
    if not path.exists():
        return
    content = path.read_text(encoding="utf-8")
    for old, new in replacements.items():
        content = content.replace(old, new)
    write_text(path, content)


def bootstrap_project(
    repo_root: str | Path,
    project_name: str,
    project_slug: str,
    enable_external_docs: bool = False,
    external_root_override: str | Path | None = None,
) -> dict:
    repo_root = resolve_repo_root(repo_root, __file__)
    config = load_config(repo_root)
    external_folder_name = f"{project_slug.upper()}DEV"

    config["project_name"] = project_name
    config["project_slug"] = project_slug
    config["external_docs"]["enabled"] = enable_external_docs
    config["external_docs"]["folder_name"] = external_folder_name
    config["external_docs"]["root_override"] = str(external_root_override or "")
    save_config(repo_root, config)

    replacements = {
        "YOUR_PROJECTDEV": external_folder_name,
        "YOUR_PROJECT": project_name,
    }
    for rel_path in TOKEN_FILES:
        _replace_tokens(repo_root / rel_path, replacements)

    state_path = repo_root / "STATE.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["status"] = "phase_00_bootstrapped"
    state["truth"]["project_shape"] = "active_project"
    state["truth"]["current_focus"] = "first_real_milestone_definition"
    state["next_actions"] = [
        "Define the first real milestone for the project and tighten the roadmap around it.",
        "Update the live handoff and decisions log as soon as the first real architectural choice is made.",
        "Run the strict continuity cycle after the first relevant change.",
    ]
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=True), encoding="utf-8")

    if enable_external_docs or external_root_override:
        external_report = sync_external_dev_context(repo_root, external_root_override)
    else:
        external_report = {"status": "skipped", "reason": "external_docs_disabled"}

    return {
        "status": "ok",
        "repo_root": str(repo_root),
        "project_name": project_name,
        "project_slug": project_slug,
        "external_docs": external_report,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Personalize the Continuity Legacy starter for a new project.")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--project-slug", required=True)
    parser.add_argument("--enable-external-docs", action="store_true")
    parser.add_argument("--external-root", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = bootstrap_project(
        repo_root=args.repo_root,
        project_name=args.project_name,
        project_slug=args.project_slug,
        enable_external_docs=args.enable_external_docs,
        external_root_override=args.external_root,
    )
    for key, value in report.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
