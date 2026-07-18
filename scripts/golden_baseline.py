"""Golden baseline verifier for Chronolith.

The baseline records hashes for a small set of canonical files. It is not a
full-repository lockfile; it protects release-critical governance and identity
surfaces from accidental drift.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = ROOT / ".chronolith" / "golden-baseline.json"

DEFAULT_PATHS = [
    "LICENSE",
    "VERSION",
    "pyproject.toml",
    "README.md",
    "PROJECT_CONTEXT.md",
    "PROJECT_DNA.md",
    "GOVERNANCE.md",
    "STATE.json",
    "PROJECT_DNA.ene.md.locked",
    ".chronolith/rulebook.json",
    ".chronolith/feature-registry.json",
    ".github/workflows/industrial_guardian.yml",
    "scripts/health_guard.py",
    "scripts/autophagy_report.py",
    "scripts/golden_baseline.py",
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_baseline(paths: list[str], contract: str | None = None) -> dict[str, Any]:
    files: dict[str, dict[str, Any]] = {}
    missing: list[str] = []
    for item in paths:
        path = ROOT / item
        if not path.exists() or not path.is_file():
            missing.append(item)
            continue
        files[item] = {
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        }

    if missing:
        missing_text = ", ".join(missing)
        raise FileNotFoundError(f"Cannot create baseline; missing files: {missing_text}")

    return {
        "version": "1.0.0",
        "scope": "chronolith-legacy-golden-baseline",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "generated_by": "python scripts/golden_baseline.py refresh",
        "change_contract": contract,
        "policy": {
            "destructive": False,
            "tracks_release_critical_files_only": True,
            "refresh_requires_human_intent": True,
            "refresh_requires_contract_when_existing": True,
        },
        "files": files,
    }


def load_baseline() -> dict[str, Any]:
    if not BASELINE_PATH.exists():
        raise FileNotFoundError(f"Missing baseline: {rel(BASELINE_PATH)}")
    data = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Baseline root must be a JSON object.")
    files = data.get("files")
    if not isinstance(files, dict) or not files:
        raise ValueError("Baseline must contain a non-empty files object.")
    return data


def verify() -> int:
    baseline = load_baseline()
    files = baseline["files"]
    failures: list[str] = []

    for item, expected in files.items():
        path = ROOT / item
        if not path.exists() or not path.is_file():
            failures.append(f"missing: {item}")
            continue
        actual_hash = sha256_file(path)
        expected_hash = expected.get("sha256") if isinstance(expected, dict) else None
        if actual_hash != expected_hash:
            failures.append(f"changed: {item}")

    if failures:
        print("golden-baseline: drift detected")
        for failure in failures:
            print(f"ERROR: {failure}")
        print("Use `python scripts/golden_baseline.py refresh` only after reviewing a change contract.")
        return 1

    print("golden-baseline: ok")
    return 0


def validate_contract(contract: str | None) -> str | None:
    if not BASELINE_PATH.exists():
        return contract
    if not contract:
        raise ValueError("Refreshing an existing baseline requires --contract PATH.")

    contract_path = ROOT / contract
    if not contract_path.exists() or not contract_path.is_file():
        raise FileNotFoundError(f"Change contract not found: {contract}")
    if not contract_path.resolve().is_relative_to((ROOT / "docs" / "change-contracts").resolve()):
        raise ValueError("Change contract must live under docs/change-contracts/.")
    return rel(contract_path)


def refresh(contract: str | None) -> int:
    contract_ref = validate_contract(contract)
    baseline = build_baseline(DEFAULT_PATHS, contract_ref)
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    BASELINE_PATH.write_text(json.dumps(baseline, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"golden-baseline: refreshed {rel(BASELINE_PATH)}")
    if contract_ref:
        print(f"golden-baseline: contract {contract_ref}")
    return 0


def list_files() -> int:
    for item in DEFAULT_PATHS:
        print(item)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify or refresh the Chronolith golden baseline.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("verify", help="Verify tracked files against the golden baseline.")
    refresh_parser = subparsers.add_parser("refresh", help="Refresh the golden baseline after human-approved changes.")
    refresh_parser.add_argument("--contract", help="Reviewed contract under docs/change-contracts/ for existing baseline refreshes.")
    subparsers.add_parser("list", help="List files tracked by the golden baseline.")
    args = parser.parse_args(argv)

    try:
        if args.command == "verify":
            return verify()
        if args.command == "refresh":
            return refresh(args.contract)
        if args.command == "list":
            return list_files()
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
