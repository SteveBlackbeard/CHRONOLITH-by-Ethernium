#!/usr/bin/env python3
import json
import subprocess
import datetime
from pathlib import Path

REQUIRED_FILES = [
    "PROJECT_CONTEXT.md",
    "STATE.json",
    "LIVE_HANDOFF.md"
]

def run_cycle():
    root = Path(".")
    print("[*] CONTINUITY LEGACY Lite - Quick Sync")
    
    missing = []
    for f in REQUIRED_FILES:
        if not (root / f).exists():
            missing.append(f)
            
    if missing:
        print("[!] ERROR: Missing required core files:")
        for m in missing:
            print(f"    - {m}")
        print("Please create these files or run the appropriate initialization.")
        return False
        
    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
        commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        branch = "unknown"
        commit = "unknown"
        
    state_file = root / "STATE.json"
    try:
        with open(state_file, "r") as f:
            state = json.load(f)
            
        state["last_sync"] = datetime.datetime.now().isoformat()
        state["git_branch"] = branch
        state["git_commit"] = commit
        
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)
            
        print(f"[✔] STATE.json updated. Branch: {branch}, Commit: {commit}")
        print("[✔] Sync Complete. Ready for handoff.")
        return True
    except Exception as e:
        print(f"[!] Failed to update STATE.json: {e}")
        return False

if __name__ == "__main__":
    run_cycle()
