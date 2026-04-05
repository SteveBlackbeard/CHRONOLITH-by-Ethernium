from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Canonical Headers for standard documents
CANONICAL_HEADERS = {
    "AGENT_START.md": "# AGENT START (Immediate Read Order) 🧠🛡️🤖",
    ".continuity/BOOT_SEQUENCE.md": "# BOOT SEQUENCE (Required First Response Pattern) 🚀",
    "PROJECT_CONTEXT.md": "# PROJECT CONTEXT (SYSTEM ROLE: Context Continuity Rules) 📜",
}


def heal_document(path: Path, required_markers: list[str]) -> bool:
    if not path.exists():
        print(f"[!] Skipping {path.name}: File does not exist.")
        return False
    
    content = path.read_text(encoding="utf-8")
    missing = [m for m in required_markers if m not in content]
    
    if not missing:
        print(f"[✔] {path.name} is already healthy.")
        return True
    
    print(f"\n[!] HEALING REQUIRED for {path.name}:")
    for m in missing:
        print(f"  - Missing: '{m}'")
        
    # Attempt to use a canonical header if available
    filename = path.name
    if filename in CANONICAL_HEADERS:
        header = CANONICAL_HEADERS[filename]
        print(f"[*] Suggested fix: Prepend canonical header: '{header}'")
        
        # In a real tool, we would ask for confirmation.
        # Here we follow the Glass Box principle: show what will happen.
        lines = content.splitlines()
        if lines and lines[0].startswith("#"):
            # Replace existing header
            lines[0] = header
        else:
            lines.insert(0, header)
            
        new_content = "\n".join(lines)
        
        # Verification
        if all(m in new_content for m in missing):
            path.write_text(new_content, encoding="utf-8")
            print(f"[✔] {path.name} has been healed successfully.")
            return True
        else:
            print(f"[✘] Failed to heal {path.name} automatically. Manual intervention required.")
            return False
    else:
        print(f"[?] No canonical header found for {path.name}. Please add missing markers manually.")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Heal standard documentation parity markers.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    print(f"[*] Starting Manual Healing Engine in: {root}")
    
    # In a full implementation, we would load the dependency map.
    # For now, let's target the known constitutional files.
    
    heal_document(root / "AGENT_START.md", ["Immediate Read Order"])
    heal_document(root / ".continuity/BOOT_SEQUENCE.md", ["BOOT SEQUENCE", "Required First Response Pattern"])
    heal_document(root / "PROJECT_CONTEXT.md", ["PROJECT_CONTEXT", "SYSTEM ROLE:", "CONTEXT CONTINUITY RULES:"])


if __name__ == "__main__":
    main()
