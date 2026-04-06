from __future__ import annotations

import re
from pathlib import Path

# Common patterns for secrets
SECRET_PATTERNS = {
    "OpenAI API Key": r"sk-[a-zA-Z0-9]{48}",
    "Anthropic API Key": r"ant-api-key-[a-zA-Z0-9]{20}",
    "AWS Access Key": r"AKIA[0-9A-Z]{16}",
    "Generic Secret": r"secret_key\s*=\s*['\"][a-zA-Z0-9]{16,}['\"]",
}


def scan_for_secrets(repo_root: Path, ignore_list: list[str] = None) -> dict:
    if ignore_list is None:
        ignore_list = [".git", "__pycache__", ".continuity/vector_db", "outputs"]

    findings = []
    
    # Generic recursive scan
    for path in repo_root.rglob("*"):
        if path.is_dir() or any(ign in str(path) for ign in ignore_list):
            continue
            
        try:
            content = path.read_text(encoding="utf-8")
            for name, pattern in SECRET_PATTERNS.items():
                if re.search(pattern, content):
                    findings.append({
                        "file": str(path.relative_to(repo_root)),
                        "type": name,
                        "status": "danger"
                    })
        except (UnicodeDecodeError, PermissionError):
            continue

    return {
        "status": "ok" if not findings else "danger",
        "findings": findings
    }


if __name__ == "__main__":
    # Test scan
    root = Path(".")
    report = scan_for_secrets(root)
    import json
    print(json.dumps(report, indent=2))
