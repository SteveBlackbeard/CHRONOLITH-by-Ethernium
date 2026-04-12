#!/usr/bin/env python3
"""
encoding_sanitizer.py - CONTINUITY LEGACY v5.2
==============================================
Detects and auto-corrects mojibake and mixed encodings across documentation
and source files. It also normalizes UTF-16/UTF-8 BOM content to UTF-8.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


SCAN_EXTENSIONS = {".md", ".py", ".txt", ".json", ".yml", ".yaml", ".html", ".toml", ".ini", ".cfg"}
SKIP_PARTS = {
    ".git",
    ".github",
    ".continuity",
    ".next",
    ".pytest_cache",
    ".pytest_tmp",
    ".venv",
    "__pycache__",
    "dist",
    "node_modules",
    "outputs",
}
SUSPICIOUS_MARKERS = ("\u00c3", "\u00e2", "\u00f0", "\u00ef\u00bb\u00bf", "\u00ce", "\u00c2", "\ufffd")
BOM_ENCODINGS = (
    (b"\xef\xbb\xbf", "utf-8-sig"),
    (b"\xff\xfe\x00\x00", "utf-32"),
    (b"\x00\x00\xfe\xff", "utf-32"),
    (b"\xff\xfe", "utf-16"),
    (b"\xfe\xff", "utf-16"),
)


def _should_scan(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in SCAN_EXTENSIONS and not any(part in SKIP_PARTS for part in path.parts)


def _decode_text(path: Path) -> tuple[str, str]:
    raw = path.read_bytes()

    for bom, encoding in BOM_ENCODINGS:
        if raw.startswith(bom):
            return raw.decode(encoding), encoding

    try:
        return raw.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        for encoding in ("cp1252", "latin-1"):
            try:
                return raw.decode(encoding), encoding
            except UnicodeDecodeError:
                continue
    return raw.decode("utf-8", errors="replace"), "utf-8-replace"


def _score_text(text: str) -> int:
    return sum(text.count(marker) for marker in SUSPICIOUS_MARKERS)


def _repair_text(text: str) -> str:
    best = text.replace("\ufeff", "")
    best_score = _score_text(best)
    frontier = [best]

    for _ in range(2):
        next_frontier: list[str] = []
        for candidate in frontier:
            for encoding in ("cp1252", "latin-1"):
                try:
                    repaired = candidate.encode(encoding).decode("utf-8")
                except UnicodeError:
                    continue
                repaired = repaired.replace("\ufeff", "")
                if repaired == candidate:
                    continue
                next_frontier.append(repaired)
                repaired_score = _score_text(repaired)
                if repaired_score < best_score:
                    best = repaired
                    best_score = repaired_score
        if not next_frontier:
            break
        frontier = next_frontier

    return best


def scan_file(path: Path) -> list[str]:
    try:
        content, encoding = _decode_text(path)
        findings = []
        if encoding not in {"utf-8", "utf-8-sig"}:
            findings.append(f"encoding:{encoding}")
        if _score_text(content) > 0:
            findings.append("mojibake")
        return findings
    except Exception:
        return []


def fix_file(path: Path) -> bool:
    try:
        original_text, original_encoding = _decode_text(path)
        repaired_text = _repair_text(original_text)
        normalized_text = repaired_text.replace("\r\n", "\n").replace("\r", "\n")

        if normalized_text == original_text and original_encoding in {"utf-8", "utf-8-sig"}:
            return False

        path.write_text(normalized_text, encoding="utf-8", newline="\n")
        return True
    except Exception as exc:
        print(f"  [!] Could not fix {path.name}: {exc}")
        return False


def run_sanitizer(repo_root: Path, fix: bool = False) -> dict:
    affected = []
    fixed = []
    scanned = 0

    for path in repo_root.rglob("*"):
        if not _should_scan(path):
            continue

        scanned += 1
        findings = scan_file(path)
        if findings:
            relative = str(path.relative_to(repo_root))
            affected.append({"file": relative, "patterns": findings})
            if fix and fix_file(path):
                fixed.append(relative)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scanned": scanned,
        "affected": len(affected),
        "fixed": len(fixed),
        "files": affected,
    }


def main():
    fix_mode = "--fix" in sys.argv
    repo_root = Path(__file__).resolve().parents[3]

    print(f"[*] Encoding Sanitizer - {'FIX MODE' if fix_mode else 'SCAN MODE'}")
    print(f"[*] Root: {repo_root}")

    report = run_sanitizer(repo_root, fix=fix_mode)
    out_path = repo_root / "outputs" / "continuity" / "encoding_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    if report["affected"] == 0:
        print(f"[OK] All {report['scanned']} files clean. No mojibake detected.")
    else:
        print(f"[!] {report['affected']} files with encoding anomalies out of {report['scanned']} scanned.")
        for item in report["files"]:
            print(f"    -> {item['file']}: {item['patterns']}")
        if not fix_mode:
            print("[->] Run with --fix to auto-correct all issues.")
        else:
            print(f"[OK] Fixed {report['fixed']} files.")
    print(f"[OK] Report saved to: {out_path}")


if __name__ == "__main__":
    main()
