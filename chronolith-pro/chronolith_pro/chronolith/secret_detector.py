from __future__ import annotations

import re
from pathlib import Path

# Comprehensive secret detection patterns (v2.1.0 Industrial Hardening)
# Expert #1 (Cybersecurity): Expanded from 4 to 15 patterns
SECRET_PATTERNS = {
    # v3.0.3: Updated to cover legacy (sk-...T3BlbkFJ...) and new (sk-proj-...) OpenAI key formats
    "OpenAI API Key": r"sk-(?:proj-)?[a-zA-Z0-9]{20,}(?:T3BlbkFJ[a-zA-Z0-9]{20,})?",
    "OpenAI Org Key": r"org-[a-zA-Z0-9]{20,}",
    "Anthropic API Key": r"sk-ant-[a-zA-Z0-9\-]{20,}",
    "AWS Access Key": r"AKIA[0-9A-Z]{16}",
    "AWS Secret Key": r"(?i)aws_secret_access_key\s*[=:]\s*['\"]?[A-Za-z0-9/+=]{40}",
    "GitHub Token (classic)": r"ghp_[a-zA-Z0-9]{36}",
    "GitHub OAuth Token": r"gho_[a-zA-Z0-9]{36}",
    "GitHub Fine-Grained PAT": r"github_pat_[a-zA-Z0-9_]{22,}",
    "Google Cloud API Key": r"AIza[0-9A-Za-z\-_]{35}",
    "Slack Webhook": r"https://hooks\.slack\.com/services/T[a-zA-Z0-9_]+/B[a-zA-Z0-9_]+/[a-zA-Z0-9_]+",
    "JWT Token": r"eyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]+",
    "Private Key (PEM)": r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----",
    "Database Connection String": r"(?i)(?:mysql|postgres|mongodb|redis)://[^\s\"']+:[^\s\"']+@[^\s\"']+",
    "Generic Secret Assignment": r"(?i)(?:secret|password|token|api[_-]?key)\s*[=:]\s*['\"][a-zA-Z0-9]{16,}['\"]",
}

# Expert #8 (Performance): Only scan known text extensions instead of all files
SAFE_EXTENSIONS = {".md", ".py", ".txt", ".json", ".yml", ".yaml", ".toml", ".cfg", ".ini", ".env", ".sh", ".ps1"}


def scan_for_secrets(repo_root: Path, ignore_list: list[str] = None) -> dict:
    """Scans the repository for leaked secrets and credentials.
    
    Uses regex pattern matching against 15 known secret formats.
    Only scans text-based files for performance (Expert #8 recommendation).
    """
    if ignore_list is None:
        ignore_list = [".git", "__pycache__", ".chronolith/vector_db", "outputs", "node_modules", ".venv"]

    findings = []
    
    for path in repo_root.rglob("*"):
        if path.is_dir() or any(ign in str(path) for ign in ignore_list):
            continue
        if path.suffix not in SAFE_EXTENSIONS:
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
    root = Path(".")
    report = scan_for_secrets(root)
    import json
    print(json.dumps(report, indent=2))
