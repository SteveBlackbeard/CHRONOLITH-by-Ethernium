"""Phase 1 governance checks for Chronolith.

The guard is intentionally conservative in its first phase: it fails on
structural corruption and reports legacy cleanup issues as warnings unless
`--strict` is used.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RULEBOOK_PATH = ROOT / ".chronolith" / "rulebook.json"
REGISTRY_PATH = ROOT / ".chronolith" / "feature-registry.json"


@dataclass(frozen=True)
class Finding:
    severity: str
    message: str


def load_json(path: Path) -> tuple[dict[str, Any] | None, list[Finding]]:
    if not path.exists():
        return None, [Finding("error", f"Missing JSON file: {rel(path)}")]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, [Finding("error", f"Invalid JSON in {rel(path)}: {exc}")]
    except UnicodeDecodeError as exc:
        return None, [Finding("error", f"Invalid UTF-8 in {rel(path)}: {exc}")]
    if not isinstance(data, dict):
        return None, [Finding("error", f"JSON root must be an object: {rel(path)}")]
    return data, []


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def check_required_paths(rulebook: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    required = []
    required.extend(rulebook.get("required_documents", []))
    required.extend(rulebook.get("required_state_files", []))
    for item in required:
        path = ROOT / item
        if not path.exists():
            findings.append(Finding("error", f"Required path is missing: {item}"))
    return findings


def check_registry(registry: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    features = registry.get("features")
    if not isinstance(features, list) or not features:
        return [Finding("error", "Feature registry must contain a non-empty features list.")]

    seen: set[str] = set()
    required_fields = {"id", "title", "status", "owner", "modules", "rollback", "risk"}
    for index, feature in enumerate(features):
        if not isinstance(feature, dict):
            findings.append(Finding("error", f"Feature at index {index} must be an object."))
            continue
        missing = sorted(required_fields - set(feature))
        feature_id = str(feature.get("id", f"index-{index}"))
        if missing:
            findings.append(Finding("error", f"Feature {feature_id} missing fields: {', '.join(missing)}"))
        if feature_id in seen:
            findings.append(Finding("error", f"Duplicate feature id: {feature_id}"))
        seen.add(feature_id)
        modules = feature.get("modules")
        if not isinstance(modules, list) or not modules:
            findings.append(Finding("error", f"Feature {feature_id} must declare at least one module."))
    return findings


def check_json_state_files() -> list[Finding]:
    findings: list[Finding] = []
    for item in ("STATE.json", ".chronolith/STATE.json"):
        path = ROOT / item
        if path.exists():
            _, errors = load_json(path)
            findings.extend(errors)
    return findings


def read_text_with_bom(path: Path) -> str:
    data = path.read_bytes()
    if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
        return data.decode("utf-16")
    if data.startswith(b"\xef\xbb\xbf"):
        return data.decode("utf-8-sig")
    return data.decode("utf-8", errors="replace")


def check_version_consistency() -> list[Finding]:
    version_path = ROOT / "VERSION"
    pyproject_path = ROOT / "pyproject.toml"
    if not version_path.exists() or not pyproject_path.exists():
        return []

    version = read_text_with_bom(version_path).strip()
    pyproject = pyproject_path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"', pyproject)
    if not match:
        return [Finding("warning", "Could not find project.version in pyproject.toml.")]
    pyproject_version = match.group(1)
    if version != pyproject_version:
        return [
            Finding(
                "warning",
                f"VERSION ({version}) differs from pyproject.toml project.version ({pyproject_version}).",
            )
        ]
    return []


def check_mojibake(rulebook: dict[str, Any]) -> list[Finding]:
    policy = rulebook.get("encoding_policy", {})
    markers = policy.get("legacy_mojibake_markers", [])
    if not isinstance(markers, list) or not markers:
        return []

    findings: list[Finding] = []
    scanned_suffixes = {".md", ".txt", ".json", ".toml", ".yml", ".yaml", ".py", ".tsx", ".ts", ".css"}
    ignored_dirs = {
        ".git",
        ".venv",
        "__pycache__",
        ".pytest_cache",
        "dist",
        "node_modules",
        ".next",
        ".build-tmp",
        ".pypi-smoke",
        ".pypi-smoke-302",
        "outputs",
    }
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [
            dirname
            for dirname in dirnames
            if dirname not in ignored_dirs and not dirname.startswith(".pypi-smoke-")
        ]
        base = Path(dirpath)
        for filename in filenames:
            path = base / filename
            if path == RULEBOOK_PATH:
                continue
            if path.suffix.lower() not in scanned_suffixes:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                findings.append(Finding("warning", f"Non UTF-8 readable text file: {rel(path)}"))
                continue
            found = [marker for marker in markers if marker in text]
            if found:
                findings.append(Finding("warning", f"Possible mojibake markers {found} in {rel(path)}"))
    return findings


def check_line_endings() -> list[Finding]:
    findings: list[Finding] = []
    for item in (RULEBOOK_PATH, REGISTRY_PATH, ROOT / "scripts" / "health_guard.py"):
        if not item.exists():
            continue
        data = item.read_bytes()
        if b"\r\n" in data:
            findings.append(Finding("warning", f"CRLF line endings found in governed file: {rel(item)}"))
    return findings


def print_findings(findings: list[Finding]) -> None:
    if not findings:
        print("health-guard: ok")
        return
    for finding in findings:
        line = f"{finding.severity.upper()}: {finding.message}"
        print(line.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(sys.stdout.encoding or "utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Chronolith governance health guard.")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors.")
    args = parser.parse_args(argv)

    findings: list[Finding] = []
    rulebook, rulebook_errors = load_json(RULEBOOK_PATH)
    registry, registry_errors = load_json(REGISTRY_PATH)
    findings.extend(rulebook_errors)
    findings.extend(registry_errors)

    if rulebook is not None:
        findings.extend(check_required_paths(rulebook))
        findings.extend(check_mojibake(rulebook))
    if registry is not None:
        findings.extend(check_registry(registry))

    findings.extend(check_json_state_files())
    findings.extend(check_version_consistency())
    findings.extend(check_line_endings())

    print_findings(findings)
    has_error = any(finding.severity == "error" for finding in findings)
    has_warning = any(finding.severity == "warning" for finding in findings)
    if has_error or (args.strict and has_warning):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
