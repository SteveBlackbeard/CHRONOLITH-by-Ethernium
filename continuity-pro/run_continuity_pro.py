import os
import sys
from pathlib import Path

# Proxy / Launcher for Continuity Pro (v2.1.0)
# This script ensures the command 'python run_continuity_pro.py' works
# from the root of the edition folder without breaking the internal package structure.

# Add the internal package to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from continuity_pro.continuity_legacy.run_continuity_cycle import main
    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"[!] Error: Could not launch Continuity Pro. {e}")
    sys.exit(1)
