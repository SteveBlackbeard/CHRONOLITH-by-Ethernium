from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .automation_common import bootstrap_output_path, resolve_repo_root
    from .context_loader import build_context_snapshot, summarize_snapshot
except (ImportError, ValueError):
    from automation_common import bootstrap_output_path, resolve_repo_root
    from context_loader import build_context_snapshot, summarize_snapshot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a continuity snapshot for the current project.")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--output-json", default=None)
    parser.add_argument("--external-root", default=None)
    parser.add_argument("--no-print", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = resolve_repo_root(args.repo_root, __file__)
    snapshot = build_context_snapshot(repo_root, args.external_root)
    output_path = bootstrap_output_path(repo_root)
    if args.output_json:
        output_path = Path(args.output_json)
        if not output_path.is_absolute():
            output_path = repo_root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=True), encoding="utf-8")
    if not args.no_print:
        print(summarize_snapshot(snapshot))


if __name__ == "__main__":
    main()
