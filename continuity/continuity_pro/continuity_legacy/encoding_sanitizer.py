#!/usr/bin/env python3
"""
encoding_sanitizer.py — CONTINUITY LEGACY v5.1
================================================
Detects and auto-corrects mojibake (UTF-8 data misread as Latin-1/Windows-1252)
across all documentation and source files in the project.

Can be run standalone or called from run_continuity_cycle.py --sanitize.

Google-style docstrings. Zero external dependencies.
"""
import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Known mojibake replacement map (latin-1 misread → correct UTF-8)
# ---------------------------------------------------------------------------
MOJIBAKE_MAP = {
    "Ã©": "é", "Ã¡": "á", "Ã­": "í", "Ã³": "ó", "Ãº": "ú",
    "Ã±": "ñ", "Ã": "Á", "â€™": "'", "â€œ": "\u201c", "â€": "\u201d",
    "Â»": "»", "Â«": "«", "Ã‰": "É", "â€¦": "…", 'â€”': "—",
    "Ã§": "ç", "Ã¼": "ü", "â€˜": "\u2018", "Â·": "·", "Â¡": "¡",
}

SCAN_EXTENSIONS = {".md", ".py", ".txt", ".json", ".yml", ".yaml", ".html"}


def scan_file(path: Path) -> list[str]:
    """Scans a single file for known mojibake patterns.

    Args:
        path: The file path to scan.

    Returns:
        A list of mojibake patterns found in the file.
    """
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        return [m for m in MOJIBAKE_MAP if m in content]
    except Exception:
        return []


def fix_file(path: Path) -> bool:
    """Replaces all known mojibake patterns in a file with correct UTF-8 characters.

    Args:
        path: The file path to sanitize.

    Returns:
        True if the file was modified, False otherwise.
    """
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        original = content
        for bad, good in MOJIBAKE_MAP.items():
            content = content.replace(bad, good)
        if content != original:
            path.write_text(content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"  [!] Could not fix {path.name}: {e}")
        return False


def run_sanitizer(repo_root: Path, fix: bool = False) -> dict:
    """Scans (and optionally fixes) all text files for mojibake corruption.

    Args:
        repo_root: Root of the project to scan.
        fix: If True, automatically repairs detected mojibake.

    Returns:
        A report dict with counts of files scanned, affected, and fixed.
    """
    affected = []
    fixed = []
    scanned = 0

    for f in repo_root.rglob("*"):
        if f.is_file() and f.suffix in SCAN_EXTENSIONS:
            # Skip hidden dirs and __pycache__
            if any(p.startswith(".") or p == "__pycache__" for p in f.parts):
                continue
            scanned += 1
            found = scan_file(f)
            if found:
                affected.append({"file": str(f.relative_to(repo_root)), "patterns": found})
                if fix:
                    if fix_file(f):
                        fixed.append(str(f.relative_to(repo_root)))

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scanned": scanned,
        "affected": len(affected),
        "fixed": len(fixed),
        "files": affected,
    }
    return report


def main():
    """CLI entry point for the encoding sanitizer."""
    fix_mode = "--fix" in sys.argv
    repo_root = Path(__file__).parent.parent.parent  # tools/continuity_legacy/ → project root

    print(f"[*] Encoding Sanitizer — {'FIX MODE' if fix_mode else 'SCAN MODE'}")
    print(f"[*] Root: {repo_root}")

    report = run_sanitizer(repo_root, fix=fix_mode)
    out_path = repo_root / "outputs" / "continuity" / "encoding_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    if report["affected"] == 0:
        print(f"[✔] All {report['scanned']} files clean. No mojibake detected.")
    else:
        print(f"[!] {report['affected']} files with mojibake out of {report['scanned']} scanned.")
        for item in report["files"]:
            print(f"    → {item['file']}: {item['patterns']}")
        if not fix_mode:
            print("[→] Run with --fix to auto-correct all issues.")
        else:
            print(f"[✔] Fixed {report['fixed']} files.")
    print(f"[✔] Report saved to: {out_path}")


if __name__ == "__main__":
    main()
