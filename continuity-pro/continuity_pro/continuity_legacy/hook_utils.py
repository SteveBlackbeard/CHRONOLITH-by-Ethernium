from __future__ import annotations
import os
import sys
from pathlib import Path

def get_abs_python() -> str:
    return sys.executable.replace("\\", "/")

def get_abs_script() -> str:
    # Resolve the CLI entrypoint for Pro
    script_path = Path(__file__).resolve().parent.parent / "run_continuity_pro.py"
    if not script_path.exists():
        # Fallback to local dev path
        script_path = Path(__file__).resolve().parent / "run_continuity_cycle.py"
    return script_path.as_posix()

def get_pre_commit_content() -> str:
    return f"""#!/bin/sh
# CONTINUITY LEGACY PRE-COMMIT HOOK (Militarized Fail-Closed)

echo "[*] CONTINUITY LEGACY: Validating project state..."

"{get_abs_python()}" "{get_abs_script()}" check
RESULT=$?

if [ $RESULT -ne 0 ]; then
  echo "[!] CONTINUITY ERROR: Project state has drift."
  echo "[!] Recommendation: Run the check script manually to align your state before pushing."
  exit 1
fi
exit 0
"""

def get_pre_push_content() -> str:
    return f"""#!/bin/sh
# CONTINUITY LEGACY PRE-PUSH HOOK (Militarized Fail-Closed)

echo "[*] CONTINUITY LEGACY: Mandatory border control validate before push..."

"{get_abs_python()}" "{get_abs_script()}" check --strict
RESULT=$?

if [ $RESULT -ne 0 ]; then
  echo "[!] CONTINUITY ERROR: Project state is inconsistent. Push blocked."
  exit 1
fi

echo "[✔] CONTINUITY OK: Project state is valid. Proceeding with push."
exit 0
"""

def _install_hook(repo_root: str | Path, hook_name: str, content_func) -> bool:
    repo_root = Path(repo_root).resolve()
    git_dir = repo_root / ".git"
    
    if not git_dir.exists():
        return False
        
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    
    hook_file = hooks_dir / hook_name
    
    try:
        hook_file.write_text(content_func(), encoding="utf-8")
        if os.name != 'nt':
            os.chmod(hook_file, 0o755)
        return True
    except Exception as e:
        print(f"Error installing git hook '{hook_name}': {e}")
        return False

def install_pre_commit_hook(repo_root: str | Path) -> bool:
    return _install_hook(repo_root, "pre-commit", get_pre_commit_content)

def install_pre_push_hook(repo_root: str | Path) -> bool:
    return _install_hook(repo_root, "pre-push", get_pre_push_content)

if __name__ == "__main__":
    if install_pre_commit_hook(".") and install_pre_push_hook("."):
        print("Git hooks installed successfully.")
    else:
        print("Failed to install git hooks (Are you in a git repo?).")
