import os
import sys
from pathlib import Path

# Proxy / Launcher for Chronolith Omega (v2.1.0)
# This script ensures the command 'python run_chronolith_omega.py' works
# from the root of the edition folder without breaking the internal package structure.

# Add the internal package to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from chronolith_omega.chronolith.run_chronolith_omega import main
    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"[!] Error: Could not launch Chronolith Omega. {e}")
    sys.exit(1)
