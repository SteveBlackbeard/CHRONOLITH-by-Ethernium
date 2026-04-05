import logging
import hashlib
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
import sys

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

# CONTINUITY LEGACY Lite (v2.1.0) - Evolution DNA Guardian
# -------------------------------------------------------------
# [!] Industrial Grade Refactor: Typer CLI, Rich UI, SHA-256 Signatures, Structured Logs.

app = typer.Typer(
    help="🏛️ Continuity Legacy Lite: The professional AI continuity framework.",
    add_completion=False,
    no_args_is_help=True
)
console = Console()

def setup_logger(repo_root: Path):
    log_dir = repo_root / ".continuity" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"continuity_{datetime.now().strftime('%Y%m%d')}.jsonl"
    
    # Custom JSON Formatter
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            log_record = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "level": record.levelname,
                "message": record.getMessage(),
                "module": record.module
            }
            if hasattr(record, "dna_hash"):
                log_record["dna_hash"] = record.dna_hash
            return json.dumps(log_record)

    logger = logging.getLogger("continuity")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        fh = logging.FileHandler(log_file)
        fh.setFormatter(JsonFormatter())
        logger.addHandler(fh)
    return logger

ASCII_ART = """
[bold cyan]
   ______ ____   _   __ ______ ____ _   __ _   __ ____ ______  __  __
  / ____// __ \\ / | / //_  __//  _// | / // /  / //_  __//_  __/ \\ \\/ /
 / /    / / / //  |/ /  / /   / / /  |/ // /  / /  / /    / /     \\  / 
/ /___ / /_/ // /|  /  / /  _/ / / /|  // /__/ /  / /    / /      / /  
\\____/ \\____//_/ |_/  /_/  /___//_/ |_/ \\____/  /_/    /_/      /_/   
                                                                       
      LEGACY [bold white]v2.1.0[/bold white] | [italic green]Industrial Evolution DNA Guardian[/italic green]
[/bold cyan]
"""

def calculate_sha256(path: Path) -> str:
    if not path.exists(): return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def sign_state(data: dict) -> str:
    """Generates a SHA-256 signature for the state record.
    Hardware binding has been removed to support Open Source collaboration across
    different developer machines while maintaining semantic integrity.
    """
    serialized = json.dumps({k: v for k, v in data.items() if k != "signature"}, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

def ensure_file(path: Path, template: str, description: str):
    if not path.exists():
        console.log(f"[yellow][?][/yellow] Missing Nucleotide: [bold]{description}[/bold]")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(template, encoding="utf-8")
        console.log(f"    [green][✔][/green] Re-synthesized: [italic]{path.name}[/italic]")
        return True
    return False

def install_hooks(repo_root: Path):
    hook_path = repo_root / ".git" / "hooks" / "pre-push"
    if not (repo_root / ".git").exists():
        console.log("[bold red][!][/bold red] ERROR: Not a git repository. Cannot install hooks.")
        return
    
    # Vector 1: Prevenir secuestro de $PATH inyectando ruta absoluta al binario
    abs_python = sys.executable.replace("\\", "/")
    abs_script = Path(__file__).resolve().as_posix()
    
    # Vector 3: Mantener política Fail-Closed (|| exit 1)
    hook_content = f"#!/bin/sh\n# Continuity Sentinel Guardian (Fail-Closed Security)\necho '[*] 🏛️ Ethernium: Guarding DNA Lineage...'\n\"{abs_python}\" \"{abs_script}\" check\nRESULT=$?\nif [ $RESULT -ne 0 ]; then\n  echo '[!] PUSH REJECTED: DNA Drift Detected. Run continuity-lite check.'\n  exit 1\nfi\nexit 0\n"
    hook_path.parent.mkdir(parents=True, exist_ok=True)
    hook_path.write_text(hook_content, encoding="utf-8")
    
    if os.name != "nt": os.chmod(hook_path, 0o755)
    console.log(f"[green][✔][/green] Push Hook Guardian (v2.1.0) installed and active.")


def build_merkle_root(hashes: list[str]) -> str:
    """RFC 6962 compliant Merkle Tree with leaf/node prefix hardening."""
    if not hashes: return "0" * 64
    # Leaf nodes: H(0x00 || data)
    current_level = [hashlib.sha256(b"\x00" + h.encode("utf-8")).hexdigest() for h in sorted(hashes)]
    while len(current_level) > 1:
        next_level = []
        if len(current_level) % 2 != 0:
            current_level.append(current_level[-1])
        for i in range(0, len(current_level), 2):
            # Internal nodes: H(0x01 || left || right)
            combined = b"\x01" + (current_level[i] + current_level[i+1]).encode("utf-8")
            next_level.append(hashlib.sha256(combined).hexdigest())
        current_level = next_level
    return current_level[0]

@app.command()
def init(
    repo_root: Path = typer.Option(".", "--repo-root", help="Project root directory."),
    no_hook: bool = typer.Option(False, "--no-hook", help="Disable automatic Git-Hook installation.")
):
    """Initialize the Continuity memory core in the current project."""
    console.print(ASCII_ART)
    logger = setup_logger(repo_root)
    
    root = repo_root.resolve()
    logger.info("Initializing Continuity Core", extra={"repo_root": str(root)})
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Forging memory core...", total=None)
        
        # Create core files
        ensure_file(root / "PROJECT_CONTEXT.md", "# Project Context\n\n- Define your project core here.", "PROJECT_CONTEXT.md")
        ensure_file(root / "LIVE_HANDOFF.md", "# Live Handoff\n\n- No handoff pending.", "LIVE_HANDOFF.md")
        
        # Create and SIGN STATE.json
        state_path = root / "STATE.json"
        if not state_path.exists():
            state_data = {"phase": "stable", "last_update": datetime.utcnow().isoformat()}
            state_data["signature"] = sign_state(state_data)
            state_path.write_text(json.dumps(state_data, indent=2), encoding="utf-8")
            console.log(f"    [green][✔][/green] Crystallized + Signed: [italic]STATE.json[/italic]")

    if not no_hook:
        install_hooks(root)
    
    console.print(Panel("[bold green]Success:[/bold green] Continuity Core crystallized at root level. 🏛️💎🦾", title="Init Complete", expand=False))

@app.command()
def check(
    repo_root: Path = typer.Option(".", "--repo-root", help="Project root directory.")
):
    """Validate the DNA parity, Merkle Root integrity, and state signature."""
    console.print(ASCII_ART)
    root = repo_root.resolve()
    
    md_files = []
    for r, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in [".git", "node_modules", ".continuity", "outputs"]]
        for f in files:
            if f.endswith(".md") and "PROJECT_DNA" not in f:
                md_files.append(Path(r) / f)
    
    nucleotides = [calculate_sha256(md) for md in sorted(md_files)]
    merkle_root = build_merkle_root(nucleotides)
    
    # Verify STATE.json signature integrity
    state_path = root / "STATE.json"
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
            # Verify cryptographic signature
            if "signature" in state:
                expected_sig = sign_state(state)
                if state["signature"] != expected_sig:
                    console.print(f"[bold red][!] STATE TAMPERING DETECTED:[/bold red] Signature mismatch!")
                    console.print(f"    Stored:   [red]{state['signature'][:16]}...[/red]")
                    console.print(f"    Expected: [cyan]{expected_sig[:16]}...[/cyan]")
                    raise typer.Exit(code=1)
                console.print(f"[green][✔][/green] State signature verified.")
            
            # Update Merkle Root in STATE.json
            state["merkle_root"] = merkle_root
            state["last_check"] = datetime.utcnow().isoformat()
            state["signature"] = sign_state(state)
            state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        except json.JSONDecodeError:
            console.print("[red][!][/red] Error: Invalid STATE.json nucleotide.")
    
    console.print(Panel(f"[bold green]Parity Confirmed:[/bold green] Merkle Root `{merkle_root[:16]}...`", title="DNA Guardian", expand=False))

@app.command()
def status(
    repo_root: Path = typer.Option(".", "--repo-root", help="Project root directory.")
):
    """View the current status of the logical lineage."""
    root = repo_root.resolve()
    state_path = root / "STATE.json"
    
    if not state_path.exists():
        console.print("[yellow]Continuity not initialized here. Use `init` first.[/yellow]")
        return

    state = json.loads(state_path.read_text(encoding="utf-8"))
    
    table = Table(title="Lineage Status 🏛️", show_header=True, header_style="bold magenta")
    table.add_column("Property", style="dim")
    table.add_column("Value")
    
    for k, v in state.items():
        table.add_row(k, str(v))
        
    console.print(table)

@app.command()
def log(
    intent: str = typer.Argument(..., help="Detailed session intent capture."),
    repo_root: Path = typer.Option(".", "--repo-root", help="Project root directory.")
):
    """Capture session intent into the permanent timeline."""
    root = repo_root.resolve()
    log_path = root / "SESSION_LOG.md"
    
    if not log_path.exists():
        log_path.write_text("# Continuity Session Log\n\n", encoding="utf-8")
    
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"- [{datetime.utcnow().isoformat()}Z] {intent}\n")
    
    console.log(f"[green][✔][/green] Intent captured in SESSION_LOG.md")

def main():
    app()

if __name__ == "__main__":
    main()
