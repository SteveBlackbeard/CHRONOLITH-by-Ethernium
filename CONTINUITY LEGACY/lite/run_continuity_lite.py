#!/usr/bin/env python3
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# --- CONFIGURATION (Zero-Deps) ---
CORE_FILES = ["PROJECT_CONTEXT.md", "STATE.json", "LIVE_HANDOFF.md"]

def get_git_info():
    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()
        last_commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
        return branch, last_commit
    except:
        return "none", "no-git"

def validate_lite(root):
    missing = [f for f in CORE_FILES if not (root / f).exists()]
    return missing

def update_state(root):
    state_path = root / "STATE.json"
    branch, commit = get_git_info()
    
    if state_path.exists():
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
    else:
        state = {"status": "setup", "next_actions": ["Complete PROJECT_CONTEXT.md"]}

    state["last_updated"] = datetime.now(timezone.utc).isoformat()
    state["git_branch"] = branch
    state["git_commit"] = commit
    
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    return state

def run_cycle():
    root = Path.cwd()
    print(f"[*] CONTINUITY LITE: Syncing {root.name}...")
    
    missing = validate_lite(root)
    if missing:
        print(f"[!] Warning: Missing core files: {', '.join(missing)}")
        if "STATE.json" in missing:
            print("[+] Creating default STATE.json...")
            update_state(root)
    else:
        state = update_state(root)
        print(f"[✔] State Synchronized on branch '{state['git_branch']}'")
        print(f"[✔] Current Phase: {state.get('status', 'unknown')}")
        print(f"[→] Next Action: {state.get('next_actions', ['none'])[0]}")

if __name__ == "__main__":
    run_cycle()
