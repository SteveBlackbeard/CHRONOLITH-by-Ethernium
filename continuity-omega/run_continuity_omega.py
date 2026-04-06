import os
import sys
from pathlib import Path

# Proxy / Launcher for Continuity Omega (v2.1.0)
# This script ensures the command 'python run_continuity_omega.py' works
# from the root of the edition folder without breaking the internal package structure.

# Add the internal package to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from continuity_omega.continuity_legacy.run_continuity_omega import main
    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"[!] Error: Could not launch Continuity Omega. {e}")
    sys.exit(1)
