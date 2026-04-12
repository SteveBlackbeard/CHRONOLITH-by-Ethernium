import os
import re
from pathlib import Path

# THE ENTERPRISE AUDIT SCANNER (v2.5.0)
# -----------------------------------
# Purpose: Identify inconsistencies, encoding anomalies, and contradictions
# without crashing on mixed-encoding documentation.

EXCLUDE_DIRS = {
    ".git",
    "node_modules",
    ".continuity",
    "outputs",
    ".pytest_cache",
    ".pytest_tmp",
    "__pycache__",
    ".venv",
    ".github",
    ".idea",
    ".vscode",
    ".next",
    "dist",
}
TEXT_EXTENSIONS = {".md", ".json", ".py", ".txt", ".yml", ".yaml", ".toml", ".cfg", ".ini"}
SUSPICIOUS_MARKERS = ("Ã", "â", "ð", "ï»¿", "Î", "Â", "\ufffd")
BOM_ENCODINGS = (
    (b"\xef\xbb\xbf", "utf-8-sig"),
    (b"\xff\xfe\x00\x00", "utf-32"),
    (b"\x00\x00\xfe\xff", "utf-32"),
    (b"\xff\xfe", "utf-16"),
    (b"\xfe\xff", "utf-16"),
)


def iter_text_files(root: Path):
    for current_root, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for filename in files:
            path = Path(current_root) / filename
            if path.suffix.lower() in TEXT_EXTENSIONS:
                yield path


def decode_text_file(path: Path) -> tuple[str, str]:
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


def has_mojibake_markers(text: str) -> bool:
    return any(marker in text for marker in SUSPICIOUS_MARKERS)


def scan_global():
    root = Path(".")
    issues = []

    print("\n[+] STARTING ENTERPRISE AUDIT SCAN...")

    decoded_cache: dict[Path, tuple[str, str]] = {}

    for path in iter_text_files(root):
        try:
            content, encoding = decode_text_file(path)
            decoded_cache[path] = (content, encoding)

            if encoding not in {"utf-8", "utf-8-sig"}:
                issues.append(f"ENCODING: {path.as_posix()} is stored as {encoding}. Normalize to UTF-8.")

            if has_mojibake_markers(content):
                issues.append(f"MOJIBAKE: Suspicious encoding markers found in {path.as_posix()}")
        except Exception as exc:
            issues.append(f"ENCODING: Could not decode {path.as_posix()} ({exc})")

    redundant_files = ["LIVE_HANDOFF.md"]
    for redundant in redundant_files:
        if (root / redundant).exists():
            issues.append(f"REDUNDANCY: {redundant} is legacy. Consider merging into TIMELINE.md.")

    for path, (content, _) in decoded_cache.items():
        if path.suffix.lower() != ".md":
            continue

        links = re.findall(r"\[.*?\]\((.*?)\)", content)
        for link in links:
            if link.startswith(("http", "#", "mailto:")):
                continue
            if not link.startswith((".", "..")):
                continue

            try:
                target = (path.parent / link.split("#")[0]).resolve()
                if not target.exists():
                    issues.append(f"DEAD LINK: {path.as_posix()} -> {link}")
            except Exception:
                issues.append(f"DEAD LINK: {path.as_posix()} -> {link}")

    forbidden_terms = ["military", "sovereign", "visceral"]
    for path, (content, _) in decoded_cache.items():
        if path.suffix.lower() != ".md":
            continue
        if "README" not in path.name and "RELEASE" not in path.name:
            continue

        lowered = content.lower()
        for term in forbidden_terms:
            if term in lowered:
                issues.append(f"TONE: '{term}' found in {path.as_posix()}. Deprecated by Enterprise standard.")

    if not issues:
        print("[OK] SYSTEM AUDIT: ABSOLUTE PARITY CONFIRMED.")
    else:
        print(f"\n[!] AUDIT FINDINGS: {len(issues)} issues identified.")
        for issue in issues:
            print(f"    - {issue}")


if __name__ == "__main__":
    scan_global()
