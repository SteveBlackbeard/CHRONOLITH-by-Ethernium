import os
import sys
from pathlib import Path

# Proxy / Launcher for Chronolith Lite (v2.1.0)
# This script ensures the README command 'python chronolith-lite/run_chronolith_lite.py' works
# without breaking the internal package structure.

# Add the internal package to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from chronolith_lite.chronolith.run_chronolith_lite import main
    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"[!] Error: Could not launch Chronolith Lite. {e}")
    sys.exit(1)
