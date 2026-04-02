from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime

# Standard paths
DECISIONS_LOG = ".continuity/DECISIONS_LOG.md"
ARCHIVE_LOG = ".continuity/ARCHIVE_LOG.md"
MAX_ENTRIES = 10


def update_memory(repo_root: Path):
    log_path = repo_root / DECISIONS_LOG
    archive_path = repo_root / ARCHIVE_LOG
    
    if not log_path.exists():
        print(f"[!] {DECISIONS_LOG} not found. Nothing to update.")
        return

    content = log_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    
    # Identify Table Rows (entries)
    # Decisions are usually in a table: | Date | Decision | Rationale | Operator |
    entries = [l for l in lines if l.startswith("|") and not l.startswith("| Date |") and not l.startswith("| --- |")]
    
    if len(entries) <= MAX_ENTRIES:
        print(f"[✔] Memory is still compact ({len(entries)} entries). No archiving needed.")
        return

    # Split into Keep and Archive
    to_keep = entries[-MAX_ENTRIES:]
    to_archive = entries[:-MAX_ENTRIES]
    
    print(f"[*] Archiving {len(to_archive)} historical entries to {ARCHIVE_LOG}.")
    
    # Write to Archive
    archive_header = f"\n## Archived on {datetime.now().isoformat()}\n"
    if not archive_path.exists():
        archive_path.write_text("# CONTINUITY LEGACY: ARCHIVE LOG 🏛️\n\n| Date | Decision | Rationale | Operator |\n| --- | --- | --- | --- |\n", encoding="utf-8")
    
    with open(archive_path, "a", encoding="utf-8") as f:
        f.write(archive_header)
        for e in to_archive:
            f.write(e + "\n")
            
    # Rewrite Decisions Log (keeping header and table structure)
    new_log = ["# DECISIONS LOG ⚖️\n", "| Date | Decision | Rationale | Operator |\n", "| --- | --- | --- | --- |\n"]
    new_log.extend([e + "\n" for e in to_keep])
    
    log_path.write_text("".join(new_log), encoding="utf-8")
    print(f"[✔] Memory consolidated. Active log reduced to {MAX_ENTRIES} entries.")


def main():
    parser = argparse.ArgumentParser(description="Update and consolidate project memory.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    update_memory(root)


if __name__ == "__main__":
    main()
