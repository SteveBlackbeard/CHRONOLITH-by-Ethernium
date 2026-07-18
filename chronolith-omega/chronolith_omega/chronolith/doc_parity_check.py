from __future__ import annotations

import json
import argparse
from pathlib import Path

try:
    from .automation_common import (
        is_ignored,
        load_dependency_map,
        read_text,
        resolve_repo_root,
        utc_now_iso,
    )
except (ImportError, ValueError):
    from automation_common import (
        is_ignored,
        load_dependency_map,
        read_text,
        resolve_repo_root,
        utc_now_iso,
    )


def check_doc_parity(repo_root: str | Path) -> dict:
    """Analyzes the repository for document synchronization and parity.

    Args:
        repo_root: The filesystem path to the project root.

    Returns:
        A dictionary containing the parity report, including health status,
        missing files, and marker synchronization errors.
    """
    root = resolve_repo_root(repo_root, __file__)
    dependency_map = load_dependency_map(root)
    errors: list[str] = []
    warnings: list[str] = []
    infos: list[str] = []
    stale_references: list[dict] = []
    docs_requiring_refresh: list[dict] = []

    for document in dependency_map.get("documents", []):
        rel_path = document.get("path")
        if is_ignored(root, rel_path):
            continue
            
        severity = document.get("severity", "warning")
        full_path = root / rel_path
        if not full_path.exists():
            issue = {"path": rel_path, "reason": "missing_document"}
            docs_requiring_refresh.append(issue)
            message = f"Missing parity-tracked document: {rel_path}"
            if severity == "error":
                errors.append(message)
            elif severity == "info":
                infos.append(message)
            else:
                warnings.append(message)
            continue

        content = read_text(full_path)
        missing_required = [item for item in document.get("required_strings", []) if item not in content]
        forbidden_hits = [item for item in document.get("forbidden_strings", []) if item in content]

        if missing_required:
            docs_requiring_refresh.append(
                {
                    "path": rel_path,
                    "reason": "missing_required_strings",
                    "missing": missing_required,
                }
            )
            message = f"Document parity drift in `{rel_path}`: missing {len(missing_required)} required markers."
            if severity == "error":
                errors.append(message)
            elif severity == "info":
                infos.append(message)
            else:
                warnings.append(message)

        if forbidden_hits:
            stale_references.append(
                {
                    "path": rel_path,
                    "reason": "forbidden_strings_present",
                    "matches": forbidden_hits,
                }
            )
            message = f"Document parity drift in `{rel_path}`: found {len(forbidden_hits)} forbidden markers."
            if severity == "error":
                errors.append(message)
            elif severity == "info":
                infos.append(message)
            else:
                warnings.append(message)

    status = "ok" if not errors and not warnings else "attention_required"
    return {
        "generated_at": utc_now_iso(),
        "repo_root": str(root),
        "status": status,
        "documents_checked": len(dependency_map.get("documents", [])),
        "errors": errors,
        "warnings": warnings,
        "infos": infos,
        "stale_references": stale_references,
        "docs_requiring_refresh": docs_requiring_refresh,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate chronolith document parity.")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = check_doc_parity(str(resolve_repo_root(args.repo_root, __file__)))
    print(json.dumps(report, indent=2, ensure_ascii=True))
    if args.strict and report["status"] != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
