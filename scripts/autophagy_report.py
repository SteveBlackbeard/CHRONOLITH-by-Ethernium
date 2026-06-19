"""Non-destructive cognitive weight report for Continuity Legacy.

Autophagy does not delete files. It classifies repository context so humans and
agents can decide what should stay canonical, be frozen, be summarized, or move
to archival storage.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".json",
    ".toml",
    ".yml",
    ".yaml",
    ".py",
    ".ts",
    ".tsx",
    ".css",
}

IGNORED_DIRS = {
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
    "AGENTOPS_TOOL",
    "CONTINUITY_CONEKTA",
}

KEEP_PATHS = {
    "README.md",
    "PROJECT_CONTEXT.md",
    "PROJECT_DNA.md",
    "GOVERNANCE.md",
    "docs/process/REPO_AND_PYPI_RELEASE_CHECKLIST.md",
    "pyproject.toml",
    "VERSION",
    ".continuity/rulebook.json",
    ".continuity/feature-registry.json",
    "docs/CONTINUITY_GOVERNANCE_KERNEL.md",
    "docs/CHANGE_CONTRACT_TEMPLATE.md",
}

FREEZE_PATHS = {
    "LICENSE",
    "PROJECT_DNA.ene.md.locked",
    "STATE.json",
}

ARCHIVE_MARKERS = (
    "SESSION",
    "REPORT",
    "RELEASE_NOTES",
    "CHANGELOG",
)


@dataclass(frozen=True)
class Entry:
    path: str
    bytes: int
    lines: int
    classification: str
    reason: str


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def iter_text_files() -> list[Path]:
    paths: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [
            dirname
            for dirname in dirnames
            if dirname not in IGNORED_DIRS and not dirname.startswith(".pypi-smoke-")
        ]
        base = Path(dirpath)
        for filename in filenames:
            path = base / filename
            if path.suffix.lower() in TEXT_SUFFIXES:
                paths.append(path)
    return sorted(paths)


def count_lines(path: Path) -> int:
    try:
        return len(path.read_text(encoding="utf-8", errors="replace").splitlines())
    except OSError:
        return 0


def classify(path: Path, size: int, lines: int) -> tuple[str, str]:
    relative = rel(path)
    name = path.name.upper()

    if relative in FREEZE_PATHS:
        return "FREEZE", "approved baseline or legal/state artifact"
    if relative in KEEP_PATHS:
        return "KEEP", "canonical active context"
    if "_tmp_" in relative or relative.startswith("outputs/"):
        return "DELETE_CANDIDATE", "temporary or generated output; human review required"
    if any(marker in name for marker in ARCHIVE_MARKERS) and size > 12_000:
        return "ARCHIVE", "large historical/report artifact"
    if lines > 400 or size > 24_000:
        return "SUMMARIZE", "large context surface"
    if relative.startswith("OTHER_LANGUAGES/") or "/OTHER_LANGUAGES/" in relative:
        return "ARCHIVE", "translation pack; load only when needed"
    return "KEEP", "small active text artifact"


def build_report() -> dict[str, object]:
    entries: list[Entry] = []
    for path in iter_text_files():
        size = path.stat().st_size
        lines = count_lines(path)
        classification, reason = classify(path, size, lines)
        entries.append(Entry(rel(path), size, lines, classification, reason))

    totals: dict[str, int] = {}
    bytes_by_class: dict[str, int] = {}
    for entry in entries:
        totals[entry.classification] = totals.get(entry.classification, 0) + 1
        bytes_by_class[entry.classification] = bytes_by_class.get(entry.classification, 0) + entry.bytes

    attention = [
        entry
        for entry in entries
        if entry.classification in {"SUMMARIZE", "ARCHIVE", "DELETE_CANDIDATE"}
    ]
    attention = sorted(attention, key=lambda item: item.bytes, reverse=True)

    return {
        "version": "1.0.0",
        "scope": "continuity-legacy-autophagy",
        "destructive": False,
        "totals": totals,
        "bytes_by_class": bytes_by_class,
        "attention": [asdict(entry) for entry in attention[:40]],
    }


def print_text(report: dict[str, object]) -> None:
    print("autophagy-report: non-destructive")
    print(f"totals: {json.dumps(report['totals'], sort_keys=True)}")
    print(f"bytes_by_class: {json.dumps(report['bytes_by_class'], sort_keys=True)}")
    print("")
    print("attention:")
    for item in report["attention"]:  # type: ignore[index]
        print(
            f"- {item['classification']}: {item['path']} "
            f"({item['bytes']} bytes, {item['lines']} lines) - {item['reason']}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a non-destructive Continuity autophagy report.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    report = build_report()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
