#!/usr/bin/env python3
"""
archive_manager.py — CONTINUITY LEGACY Pro
==========================================
Systemic Log Rotation & Context Archiving.

Moves historical outputs and oversized log files from .continuity/ 
to .continuity/archive/ to prevent context window saturation while 
preserving the project's 'Genetic Code'.
"""

import os
import json
import shutil
import datetime
from pathlib import Path

# Config
MAX_LOG_SIZE_BYTES = 50 * 1024  # 50KB threshold for rotation
ARCHIVE_DIR_NAME = "archive"

def rotate_logs(repo_root: Path):
    print(f"[*] Archive Manager: Evaluating log health in {repo_root}...")
    
    continuity_dir = repo_root / ".continuity"
    archive_dir = continuity_dir / ARCHIVE_DIR_NAME
    
    if not continuity_dir.exists():
        print("[!] No .continuity directory found. Skipping archiving.")
        return

    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Files to track for rotation
    targets = [
        "DECISIONS_LOG.md",
        "TIMELINE.md",
    ]
    
    for target in targets:
        file_path = continuity_dir / target
        if file_path.exists() and file_path.stat().st_size > MAX_LOG_SIZE_BYTES:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"{target.replace('.md', '')}_{timestamp}.md"
            dest_path = archive_dir / archive_name
            
            print(f"  [>] Rotating {target} (Size: {file_path.stat().st_size} bytes)")
            shutil.copy2(file_path, dest_path)
            
            # Reset the active file with a link to the archive
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# {target.replace('.md', '').replace('_', ' ')}\n")
                f.write(f"> [!] LOG ROTATED on {timestamp}. See archive/{archive_name} for history.\n\n")
            
    # Cleanup old cycle reports in outputs
    outputs_dir = repo_root / "outputs" / "continuity"
    if outputs_dir.exists():
        # Keep only the last 10 reports, archive the rest? Or just prune.
        # For '' we archive them.
        report_archive = archive_dir / "reports"
        report_archive.mkdir(exist_ok=True)
        
        all_reports = sorted(list(outputs_dir.glob("*.json")), key=os.path.getmtime)
        if len(all_reports) > 10:
            to_archive = all_reports[:-10]
            print(f"  [>] Archiving {len(to_archive)} historical reports...")
            for r in to_archive:
                shutil.move(str(r), str(report_archive / r.name))

    print("[✔] Archiving Cycle Complete.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Rotate and archive continuity logs.")
    parser.add_argument("--repo-root", default=".", help="Root directory of the project")
    args = parser.parse_args()
    rotate_logs(Path(args.repo_root).resolve())
