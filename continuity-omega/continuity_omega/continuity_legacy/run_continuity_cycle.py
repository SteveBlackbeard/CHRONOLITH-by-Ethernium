import sys
import subprocess
from pathlib import Path

def main():
    repo_root = Path('.').resolve()
    # Path to the real script
    cycle_script = repo_root / 'tools' / 'continuity_legacy' / 'run_continuity_cycle.py'
    
    if not cycle_script.exists():
        print(f"[!] Error: Could not find cycle script at {cycle_script}")
        sys.exit(1)
        
    cmd = [sys.executable, str(cycle_script)] + sys.argv[1:]
    subprocess.run(cmd)

if __name__ == '__main__':
    main()
