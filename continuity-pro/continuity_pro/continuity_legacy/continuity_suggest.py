from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

try:
    from .automation_common import Color, echo, resolve_repo_root
except (ImportError, ValueError):
    from automation_common import Color, echo, resolve_repo_root


def get_git_diff_summary(root: Path) -> str:
    try:
        # Get list of changed files
        files = subprocess.check_output(
            ["git", "diff", "--name-status", "HEAD"], 
            cwd=root, 
            text=True
        ).strip()
        if not files:
            return "No changes detected in Git."
        
        # Get brief diff summary
        diff = subprocess.check_output(
            ["git", "diff", "--stat", "HEAD"], 
            cwd=root, 
            text=True
        ).strip()
        
        return f"Changes:\n{files}\n\nStats:\n{diff}"
    except Exception as e:
        return f"Error reading git diff: {e}\n(Make sure you are in a git repo and have changes staged or committed locally)."


def main() -> None:
    parser = argparse.ArgumentParser(description="Suggest continuity updates based on recent changes.")
    parser.add_argument("--repo-root", default=None)
    args = parser.parse_args()

    root = resolve_repo_root(args.repo_root, __file__)
    diff_summary = get_git_diff_summary(root)

    echo(f"\n{Color.BOLD}--- CONTINUITY SUGGESTION ENGINE ---{Color.END}")
    echo("Analyzing your recent work to help you update the handoff...", Color.CYAN)

    echo(f"\n{Color.UNDERLINE}Detected Changes:{Color.END}")
    echo(diff_summary)

    prompt = f"""
[CONTINUITY PROMPT TEMPLATE]
I have made the following changes in the project:
{diff_summary}

Based on this, please help me update my continuity files:
1. Suggest a 2-3 sentence update for 'LIVE_HANDOFF.md' including the Next Exact Action.
2. Suggest a 1-sentence entry for 'TIMELINE.md'.
3. Suggest any new decisions for 'DECISIONS_LOG.md' if applicable.
"""

    echo(f"\n{Color.GREEN}{Color.BOLD}--- PASTE THIS TO YOUR AI ASSISTANT ---{Color.END}")
    echo(prompt, Color.WHITE)
    echo(f"{Color.BOLD}----------------------------------------{Color.END}")


if __name__ == "__main__":
    main()
