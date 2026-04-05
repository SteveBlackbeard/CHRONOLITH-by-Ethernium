# Example 2: DNA Guardian Hook Setup
# This demonstrates how to activate automated protection for your repository.

import os
import subprocess
from pathlib import Path

def run_guardian_setup():
    print("--- Continuity Lite: Example 2 (Hook Setup) ---")
    print("Command: python run_continuity_lite.py --hook")
    
    # Simulate installation logic
    print("Simulating hook installation...")
    print("[✔] Push Hook (v2.1.0) installed at .git/hooks/pre-push")
    print("\nNext time you 'git push', your lineage will be validated automatically.")

if __name__ == "__main__":
    run_guardian_setup()
