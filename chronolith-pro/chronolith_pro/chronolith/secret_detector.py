from __future__ import annotations

import re
import subprocess
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

# Key material is the one thing the patterns above structurally cannot find.
# A raw Ed25519 seed is 32 bytes of binary in a `.priv` file: it matches no
# regex, and the extension filter skipped it before it was ever read.
#
# This is not hypothetical. `.chronolith/keys/sovereign.priv` sat tracked in
# this repository for three months while this very scanner reported clean.
KEY_FILE_SUFFIXES = {".priv", ".key", ".pem", ".p8", ".pfx"}
KEY_FILE_NAMES = {"id_rsa", "id_ed25519", "id_ecdsa", "id_dsa"}

# An Ed25519 seed is 32 bytes; an RSA-4096 DER key stays under 4KB. Anything
# larger and non-PEM is not raw key material.
_MAX_RAW_KEY_BYTES = 8192

# Markers proving the bytes are wrapped rather than raw.
_PROTECTED_MARKERS = (b"ENCRYPTED", b"scrypt", b'"salt"', b'"nonce"', b'"kdf"')


def _is_tracked(path: Path, repo_root: Path) -> bool:
    """True when git is following this file.

    This is the distinction that matters. A private key on a developer's disk
    is normal and expected — that is where keys live. A private key in the
    index is published the moment anyone pushes. Only the second is an
    incident, so only the second is reported as danger.
    """
    try:
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(path.relative_to(repo_root))],
            cwd=repo_root, capture_output=True, timeout=10,
        )
        return result.returncode == 0
    except (OSError, ValueError, subprocess.SubprocessError):
        # No git, or the path is outside the repo. Assume the worse case:
        # a scanner that stays silent when unsure is how this got missed.
        return True


def _classify_key_file(path: Path, repo_root: Path) -> dict | None:
    """Report a private-key file, and say whether the material is protected.

    Returns None for public keys and for anything that is not key material.
    """
    if path.suffix == ".pub" or path.stem.endswith(".pub"):
        return None
    if path.suffix not in KEY_FILE_SUFFIXES and path.name not in KEY_FILE_NAMES:
        return None
    try:
        blob = path.read_bytes()
    except (PermissionError, OSError):
        return None
    # PEM-shaped files announce what they hold. Trust the header: a CA bundle
    # (`certifi`'s cacert.pem is ~270KB of BEGIN CERTIFICATE) is public data,
    # and flagging it would train people to ignore this scanner.
    if b"-----BEGIN" in blob[:8192]:
        if b"PRIVATE KEY" not in blob:
            return None
    elif len(blob) > _MAX_RAW_KEY_BYTES:
        # Not PEM and far too large to be raw key material. An Ed25519 seed is
        # 32 bytes; even an RSA-4096 DER key is under 4KB.
        return None

    protected = any(marker in blob for marker in _PROTECTED_MARKERS)
    tracked = _is_tracked(path, repo_root)
    if protected:
        label = "Private Key File (passphrase-protected)"
    else:
        label = "Private Key Material (UNENCRYPTED)"
    return {
        "type": label + (" — TRACKED BY GIT" if tracked else " — untracked, local only"),
        "status": "danger" if tracked and not protected else "warning",
        "bytes": len(blob),
        "tracked": tracked,
    }


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

        # Key material first: this check must run BEFORE the extension filter,
        # because the extension filter is exactly what hid sovereign.priv.
        key_finding = _classify_key_file(path, repo_root)
        if key_finding is not None:
            findings.append({
                "file": str(path.relative_to(repo_root)),
                **key_finding,
            })
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

    # A local untracked key is a warning, not a failure: keys are supposed to
    # exist on the machine that owns them. Only danger blocks.
    if any(f["status"] == "danger" for f in findings):
        status = "danger"
    elif findings:
        status = "warning"
    else:
        status = "ok"
    return {
        "status": status,
        "findings": findings
    }


if __name__ == "__main__":
    root = Path(".")
    report = scan_for_secrets(root)
    import json
    print(json.dumps(report, indent=2))
