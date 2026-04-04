import os
import sys
from pathlib import Path

# Proxy / Launcher for Continuity Lite (v1.3.1)
# This script ensures the README command 'python continuity-lite/run_continuity_lite.py' works
# without breaking the internal package structure.

# Add the internal package to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from continuity_lite.continuity_legacy.run_continuity_lite import main
    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"[!] Error: Could not launch Continuity Lite. {e}")
    sys.exit(1)
