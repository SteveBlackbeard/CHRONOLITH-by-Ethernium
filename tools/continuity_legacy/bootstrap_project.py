from __future__ import annotations

import argparse
import json
from pathlib import Path

from core.automation_common import load_config, resolve_repo_root, save_config, write_text
from core.hook_utils import install_pre_commit_hook
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
    discover: bool = False,
    with_vector: bool = False,
    with_graph: bool = False,
) -> dict:
    repo_root = resolve_repo_root(repo_root, __file__)
    config = load_config(repo_root)
    external_folder_name = f"{project_slug.upper()}DEV"

    # Run Discovery if enabled
    discovery_performed = False
    if discover:
        from discover_project import generate_context_draft
        draft_content = generate_context_draft(repo_root, project_name)
        (repo_root / "PROJECT_CONTEXT.md").write_text(draft_content, encoding="utf-8")
        discovery_performed = True

    # Handle Extensions
    extensions_created = []
    if with_vector or with_graph:
        ext_root = repo_root / "tools" / "continuity_legacy" / "extensions"
        ext_root.mkdir(parents=True, exist_ok=True)
        if with_vector:
            (ext_root / "vector").mkdir(exist_ok=True)
            (ext_root / "vector" / "README.md").write_text("# Vector Extension\nInstall dependencies with `pip install chromadb`", encoding="utf-8")
            (ext_root / "vector" / "vector_store_lite.py").write_text("# Wrapper ChromaDB implementation", encoding="utf-8")
            # The functional class is already copied if we are in the tools folder, 
            # but we ensure it exists for the user.
            extensions_created.append("vector")
        if with_graph:
            (ext_root / "graph").mkdir(exist_ok=True)
            (ext_root / "graph" / "README.md").write_text("# Graph Extension\nInstall dependencies with `pip install networkx`", encoding="utf-8")
            extensions_created.append("graph")

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
        # Avoid overwriting PROJECT_CONTEXT.md if discovery already wrote it
        if discover and rel_path == "PROJECT_CONTEXT.md":
            continue
        _replace_tokens(repo_root / rel_path, replacements)

    state_path = repo_root / "STATE.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["status"] = "phase_00_bootstrapped"
    state["truth"]["project_shape"] = "active_project"
    state["truth"]["current_focus"] = "first_real_milestone_definition"
    state["next_actions"] = [
        "Review the discover-generated PROJECT_CONTEXT.md and refine it." if discover else "Define the first real milestone for the project and tighten the roadmap around it.",
        "Update the live handoff and decisions log as soon as the first real architectural choice is made.",
        "Run the strict continuity cycle after the first relevant change.",
    ]
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=True), encoding="utf-8")

    if enable_external_docs or external_root_override:
        external_report = sync_external_dev_context(repo_root, external_root_override)
    else:
        external_report = {"status": "skipped", "reason": "external_docs_disabled"}

    # Install Git Hooks for automation by default
    from core.hook_utils import install_pre_commit_hook, install_pre_push_hook
    hooks_installed = install_pre_commit_hook(repo_root) and install_pre_push_hook(repo_root)

    return {
        "status": "ok",
        "repo_root": str(repo_root),
        "project_name": project_name,
        "project_slug": project_slug,
        "external_docs": external_report,
        "discovery_performed": discovery_performed,
        "extensions": extensions_created,
        "git_hooks_installed": hooks_installed,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Personalize the Continuity Legacy starter for a new project.")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--project-slug", required=True)
    parser.add_argument("--enable-external-docs", action="store_true")
    parser.add_argument("--external-root", default=None)
    parser.add_argument("--discover", action="store_true", help="Auto-discover project context and rules.")
    parser.add_argument("--with-vector", action="store_true", help="Enable vector store extension.")
    parser.add_argument("--with-graph", action="store_true", help="Enable knowledge graph extension.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = bootstrap_project(
        repo_root=args.repo_root,
        project_name=args.project_name,
        project_slug=args.project_slug,
        enable_external_docs=args.enable_external_docs,
        external_root_override=args.external_root,
        discover=args.discover,
        with_vector=args.with_vector,
        with_graph=args.with_graph,
    )
    for key, value in report.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
