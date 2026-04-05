import logging
import hashlib
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

# CONTINUITY LEGACY Pro (v2.1.0) - Solemne Evolution DNA Guardian
# -------------------------------------------------------------
# [!] Industrial Grade Refactor: Typer CLI, Rich UI, SHA-256 Signatures, Structured Logs.

app = typer.Typer(
    help="🏛️ Continuity Legacy Pro: The sovereign AI continuity framework for industrial handoffs.",
    add_completion=False,
    no_args_is_help=True
)
console = Console()

ASCII_ART = """
[bold magenta]
   ______ ____   _   __ ______ ____ _   __ _   __ ____ ______  __  __
  / ____// __ \\ / | / //_  __//  _// | / // /  / //_  __//_  __/ \\ \\/ /
 / /    / / / //  |/ /  / /   / / /  |/ // /  / /  / /    / /     \\  / 
/ /___ / /_/ // /|  /  / /  _/ / / /|  // /__/ /  / /    / /      / /  
\\____/ \\____//_/ |_/  /_/  /___//_/ |_/ \\____/  /_/    /_/      /_/   
                                                                       
      LEGACY [bold white]v2.1.0[/bold white] | [italic magenta]Solemne Industrial Evolution Guardian[/italic magenta]
[/bold magenta]
"""

# Import internal modules - pip-compatible relative imports with direct-exec fallback
try:
    from . import automation_common
    from . import doc_parity_check
    from . import system_membership_check
    from . import secret_detector
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import automation_common
    import doc_parity_check
    import system_membership_check
    import secret_detector


def setup_logger(repo_root: Path):
    log_dir = repo_root / ".continuity" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"pro_continuity_{datetime.now().strftime('%Y%m%d')}.jsonl"
    
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            log_record = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "level": record.levelname,
                "module": "pro_engine",
                "message": record.getMessage()
            }
            return json.dumps(log_record)

    logger = logging.getLogger("continuity_pro")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        fh = logging.FileHandler(log_file)
        fh.setFormatter(JsonFormatter())
        logger.addHandler(fh)
    return logger

def sign_state(data: dict) -> str:
    serialized = json.dumps({k: v for k, v in data.items() if k != "signature"}, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

def crystallize_readme(repo_root: Path, merkle_root: str):
    readme_path = repo_root / "README.md"
    if not readme_path.exists(): return
    content = readme_path.read_text(encoding="utf-8")
    marker = "<!-- DNA_CRYSTAL -->"
    if marker in content:
        import re
        crystal_text = (
            f"\n> [!IMPORTANT]\n"
            f"> **DNA CRYSTAL (Pro)**: `v2.1.0-{merkle_root[:16]}`\n"
            f"> [![Merkle Root](https://img.shields.io/badge/DNA--Crystallized-{merkle_root[:8]}-magenta)](https://github.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium)\n"
        )
        # Strip old crystal block if exists
        content = re.sub(r"\n> \[!IMPORTANT\].*?blueviolet|magenta\)\n", "", content, flags=re.DOTALL)
        parts = content.split(marker)
        new_content = parts[0] + marker + crystal_text + marker.join(parts[1:])
        readme_path.write_text(new_content, encoding="utf-8")
        console.log(f"[bold magenta][✔][/bold magenta] README Crystallized: {merkle_root[:8]}")

@app.command()
def init(
    repo_root: Path = typer.Option(".", "--repo-root", help="Project root directory."),
    no_hook: bool = typer.Option(False, "--no-hook", help="Disable automatic Git-Hook installation.")
):
    """Initialize the Pro memory core and install sovereign hooks."""
    console.print(ASCII_ART)
    root = repo_root.resolve()
    logger = setup_logger(root)
    logger.info("Initializing Pro Core")
    
    files = {
        "PROJECT_CONTEXT.md": "# Project Context\n\n- Industrial Grade strategy.",
        "ROADMAP.md": "# Industrial Roadmap\n\n- Milestones here.",
        ".continuity/STATE.json": '{"phase": "pro", "last_update": "' + datetime.utcnow().isoformat() + '"}',
        ".continuity/DECISIONS_LOG.md": "# Decision Log\n\n| Date | Decision | Rationale | Actor |\n| :--- | :--- | :--- | :--- |\n",
        ".continuity/TIMELINE.md": "# Project Timeline\n\n- Strategic events.",
    }
    
    for filename, template in files.items():
        path = root / filename
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(template, encoding="utf-8")
            console.log(f"    [green][✔][/green] Crystallized: [italic]{filename}[/italic]")

    if not no_hook:
        hook_path = root / ".git" / "hooks" / "pre-push"
        hook_path.parent.mkdir(parents=True, exist_ok=True)
        hook_content = f"#!/bin/sh\n# Continuity Pro Evolution Hook\necho '[*] Guarding Pro DNA...'\npython \"{Path(__file__).resolve()}\" check --strict || exit 1\n"
        hook_path.write_text(hook_content, encoding="utf-8")
        if os.name != "nt": os.chmod(hook_path, 0o755)
        console.log(f"[bold green][✔][/bold green] Pro Push Hook installed.")

@app.command()
def check(
    repo_root: Path = typer.Option(".", "--repo-root", help="Project root directory."),
    strict: bool = typer.Option(False, "--strict", help="Fail with exit code 1 if drift detected.")
):
    """Validate full project parity, doc-immunity, and security audits."""
    console.print(ASCII_ART)
    root = repo_root.resolve()
    logger = setup_logger(root)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Scanning Nucleotides (Pro)...", total=None)
        
        doc_parity = doc_parity_check.check_doc_parity(str(root))
        membership = system_membership_check.check_system_membership(str(root))
        secret_scan = secret_detector.scan_for_secrets(root)
        
        # DNA Synthesis (Merkle Tree via automation_common)
        md_files = []
        for r, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in [".git", "node_modules", ".continuity", "outputs", "assets", "banners"]]
            for f in files:
                if f.endswith(".md") and "PROJECT_DNA" not in f:
                    md_files.append(Path(r) / f)
        
        nucleotides = [automation_common.calculate_sha256(f) for f in sorted(md_files)]
        merkle_root = automation_common.build_merkle_tree(nucleotides)
        entropy = automation_common.calculate_context_entropy("".join([f.read_text(errors='ignore') for f in md_files]))

    crystallize_readme(root, merkle_root)
    
    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "merkle_root": merkle_root,
        "entropy": entropy,
        "doc_parity": doc_parity["status"],
        "security": "ok" if not secret_scan["findings"] else "danger"
    }
    
    # Save Report
    report_path = root / ".continuity" / "pro_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    logger.info("Cycle complete", extra={"merkle_root": merkle_root})
    
    console.print(Panel(f"[bold magenta]Pro Status:[/bold magenta] Status: OK | Merkle: `{merkle_root[:16]}...`", title="Solemne Guardian", expand=False))
    
    if report["security"] == "danger":
        console.print("[bold red][!][/bold red] SECURITY ALERT: Secrets detected in lineage!")
    
    if (report["doc_parity"] != "ok" or report["security"] == "danger") and strict:
        raise typer.Exit(code=1)

@app.command()
def log(
    intent: str = typer.Argument(..., help="Detailed session intent capture."),
    repo_root: Path = typer.Option(".", "--repo-root", help="Project root directory.")
):
    """Log a design decision or strategic intent to the Decision Log."""
    root = repo_root.resolve()
    log_path = root / ".continuity" / "DECISIONS_LOG.md"
    
    if not log_path.exists():
        log_path.write_text("# Decision Log\n\n| Date | Decision | Rationale | Actor |\n| :--- | :--- | :--- | :--- |\n", encoding="utf-8")
    
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"| {datetime.utcnow().strftime('%Y-%m-%d')} | Intent: {intent} | Developer Session | Solemne Admin |\n")
    
    console.log(f"[bold magenta][✔][/bold magenta] Intent logged into [italic]DECISIONS_LOG.md[/italic]")

def main():
    app()

if __name__ == "__main__":
    main()
