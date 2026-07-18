#!/usr/bin/env python3
"""
update_memory.py — CHRONOLITH Pro
========================================
Anti-amnesia engine. Automatically consolidates recent branch actions,
completed tests, and resolved debt into the DECISIONS_LOG.md and
TIMELINE.md files to ensure nothing is lost during handoffs.
"""

import json
import datetime
from pathlib import Path

import subprocess

def extract_git_decisions(repo_root: Path):
    """Fetch recent git commits and extract strategic decisions."""
    print("  [>] Syncing history from Git...")
    try:
        # Get last 24 hours of log
        cmd = ["git", "log", "--since='24 hours ago'", "--pretty=format:%s"]
        output = subprocess.check_output(cmd, cwd=repo_root, stderr=subprocess.DEVNULL).decode(errors="ignore")
        
        decisions_file = repo_root / ".chronolith" / "DECISIONS_LOG.md"
        if not decisions_file.exists():
            return

        lines = output.splitlines()
        extracted = []
        for line in lines:
            if line.startswith("[DEC]") or line.startswith("dec:"):
                extracted.append(line.replace("[DEC]", "").replace("dec:", "").strip())
        
        if extracted:
            now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d UTC")
            with open(decisions_file, "a", encoding="utf-8") as f:
                f.write(f"\n### Git Auto-Decisions ({now_str})\n")
                for e in extracted:
                    f.write(f"- {e}\n")
            print(f"  [✔] Extracted {len(extracted)} decisions from git logs.")
    except Exception:
        print("  [!] Git log not available or failed. Skipping extraction.")

def consolidate_memory(repo_root: Path):
    print(f"[*] Memory Consolidator: Updating project logs in {repo_root}...")
    
    chronolith_dir = repo_root / ".chronolith"
    state_file = repo_root / "STATE.json"
    timeline_file = chronolith_dir / "TIMELINE.md"
    decisions_file = chronolith_dir / "DECISIONS_LOG.md"
    
    if not (repo_root / "STATE.json").exists():
        # Fallback for Lite where state is in root
        state_file = repo_root / "STATE.json"
        
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception:
        return
        
    now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d UTC")
    action = state.get("last_action", "Automated sync.")
    
    # Update Timeline
    if timeline_file.exists():
        content = timeline_file.read_text(encoding="utf-8")
        if now_str not in content:
            new_entry = f"\n- **{now_str}**: {action}"
            timeline_file.write_text(content + new_entry, encoding="utf-8")
            print("  [✔] Updated TIMELINE.")
            
    # Automated Extraction
    extract_git_decisions(repo_root)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Consolidate chronolith memory.")
    parser.add_argument("--repo-root", default=".", help="Root directory of the project")
    args = parser.parse_args()
    consolidate_memory(Path(args.repo_root).resolve())
