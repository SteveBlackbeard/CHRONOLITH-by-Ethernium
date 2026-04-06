from __future__ import annotations

import argparse
import json

import automation_common
from automation_common import (
    ALLOWED_MEMBERSHIP_STATUSES,
    load_membership_registry,
    resolve_repo_root,
    utc_now_iso,
)


def check_system_membership(repo_root: str) -> dict:
    root = resolve_repo_root(repo_root, __file__)
    registry = load_membership_registry(root)
    errors: list[str] = []
    warnings: list[str] = []
    seen_paths: set[str] = set()
    missing_paths: list[str] = []

    for entry in registry.get("entries", []):
        rel_path = entry.get("path")
        status = entry.get("status")
        if not rel_path:
            errors.append("A membership entry is missing its path.")
            continue
        if rel_path in seen_paths:
            errors.append(f"Duplicate membership entry: {rel_path}")
        seen_paths.add(rel_path)

        if status not in ALLOWED_MEMBERSHIP_STATUSES:
            errors.append(f"Invalid membership status `{status}` for `{rel_path}`")

        full_path = root / rel_path
        if not full_path.exists():
            missing_paths.append(rel_path)
            errors.append(f"Registered membership path does not exist: {rel_path}")

    status = "ok" if not errors and not warnings else "attention_required"
    return {
        "generated_at": utc_now_iso(),
        "repo_root": str(root),
        "status": status,
        "entries_checked": len(registry.get("entries", [])),
        "missing_paths": missing_paths,
        "errors": errors,
        "warnings": warnings,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the continuity system-membership registry.")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = check_system_membership(str(resolve_repo_root(args.repo_root, __file__)))
    print(json.dumps(report, indent=2, ensure_ascii=True))
    if args.strict and report["status"] != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
