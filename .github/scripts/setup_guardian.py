import sys
import os
import subprocess
from pathlib import Path

# CHRONOLITH: Guardian Setup (v1.0.0)
# -------------------------------------------------------------
# Automated "Sentinel" installation and DNA crystallization.

def run_step(description: str, command: list[str], shell: bool = False):
    print(f"[*] {description}...")
    try:
        subprocess.check_call(command, shell=shell)
        print(f"    [✔] Success.")
    except Exception as e:
        print(f"    [!] Error: {e}")
        sys.exit(1)

def main():
    print("==========================================================")
    print(" CHRONOLITH: SENTINEL GUARDIAN SETUP ")
    print("==========================================================")
    
    repo_root = Path(__file__).parent.resolve()
    
    # 1. Install Dependencies
    run_step("Installing industrial dependencies (Typer, Rich)", 
             [sys.executable, "-m", "pip", "install", "typer[all]", "rich"])
    
    # 2. Install Lite Edition as Editable
    run_step("Initializing Lite Edition", 
             [sys.executable, "-m", "pip", "install", "-e", "chronolith-lite"])
    
    # 3. Forge Memory Core & Auto-Hooks
    # We call the newly refactored Typer CLI directly
    cli_path = repo_root / "chronolith-lite" / "chronolith_lite" / "chronolith" / "run_chronolith_lite.py"
    
    run_step("Crystallizing DNA and Active Hooks", 
             [sys.executable, str(cli_path), "init", "--repo-root", str(repo_root)])
    
    print("\n[✔] CHRONOLITH SYSTEM SOBERANO ACTIVADO.")
    print("[*] Your logical lineage is now guarded by the Sentinel (Git-Hooks).")
    print("[*] Use 'chronolith-lite status' to view your current DNA parity.")
    print("==========================================================")

if __name__ == "__main__":
    main()
