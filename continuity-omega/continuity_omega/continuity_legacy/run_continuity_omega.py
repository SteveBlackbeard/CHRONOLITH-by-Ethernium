import logging
import hashlib
import os
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

def _configure_stdio_for_unicode() -> bool:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is not None and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass
    encoding = ((getattr(sys.stdout, "encoding", None) or "") + (getattr(sys.stderr, "encoding", None) or "")).lower()
    return "utf" in encoding

UNICODE_OK = _configure_stdio_for_unicode()

OMEGA_ICON = "OMEGA"

# CONTINUITY LEGACY OMEGA (v2.1.0) - Celestial Cognitive Oracle
# -------------------------------------------------------------
# [!] Industrial Grade Refactor: Typer CLI, Rich UI, RAG, Cognitive Maps.

app = typer.Typer(
    help=f"{OMEGA_ICON} Continuity Legacy Omega: The pinnacle AI oracle. Advanced RAG and cognitive mapping.",
    add_completion=False,
    no_args_is_help=True,
)
console = Console(emoji=False)
ASCII_ART = """
[bold blue]
   ______ ____   _   __ ______ ____ _   __ _   __ ____ ______  __  __
  / ____// __ \\ / | / //_  __//  _// | / // /  / //_  __//_  __/ \\ \\/ /
 / /    / / / //  |/ /  / /   / / /  |/ // /  / /  / /    / /     \\  / 
/ /___ / /_/ // /|  /  / /  _/ / / /|  // /__/ /  / /    / /      / /  
\\____/ \\____//_/ |_/  /_/  /___//_/ |_/ \\____/  /_/    /_/      /_/   
                                                                       
      LEGACY [bold white]v2.1.0[/bold white] | [italic cyan]Celestial Cognitive Oracle (Omega)[/italic cyan]
[/bold blue]
"""

# Lazy loading of heavy modules
try:
    import omega_engine
    import cognitive_map
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).resolve().parent))
    import omega_engine
    import cognitive_map

def setup_logger(repo_root: Path):
    log_dir = repo_root / ".continuity" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"omega_continuity_{datetime.now().strftime('%Y%m%d')}.jsonl"
    
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            log_record = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "level": record.levelname,
                "module": "omega_engine",
                "message": record.getMessage()
            }
            return json.dumps(log_record)

    logger = logging.getLogger("continuity_omega")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        fh = logging.FileHandler(log_file)
        fh.setFormatter(JsonFormatter())
        logger.addHandler(fh)
    return logger

@app.command()
def init(
    repo_root: Path = typer.Option(".", "--repo-root", help="Project root directory."),
    no_hook: bool = typer.Option(False, "--no-hook", help="Disable automatic Git-Hook installation.")
):
    """Initialize the Celestial Omega memory core and install cognitive hooks."""
    console.print(ASCII_ART)
    root = repo_root.resolve()
    logger = setup_logger(root)
    logger.info("Initializing Omega Core")
    
    files = {
        ".continuity/STATE.json": '{"phase": "omega", "last_update": "' + datetime.utcnow().isoformat() + '"}',
        "PROJECT_CONTEXT.md": "# Project Context\n\n- Celestial Strategic Oracle intent.",
        ".continuity/DECISIONS_LOG.md": "# Decision Log\n\n| Date | Decision | Rationale | Actor |\n| :--- | :--- | :--- | :--- |\n"
    }
    
    for filename, template in files.items():
        path = root / filename
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(template, encoding="utf-8")
            console.log(f"    [cyan][âœ”][/cyan] Crystallized: [italic]{filename}[/italic]")

    if not no_hook:
        hook_path = root / ".git" / "hooks" / "pre-push"
        hook_path.parent.mkdir(parents=True, exist_ok=True)
        hook_content = f"#!/bin/sh\n# Continuity Omega Evolution Hook\necho '[*] Guarding Celestial DNA...'\npython \"{Path(__file__).resolve()}\" index || exit 1\n"
        hook_path.write_text(hook_content, encoding="utf-8")
        if os.name != "nt": os.chmod(hook_path, 0o755)
        console.log(f"[bold blue][âœ”][/bold blue] Omega Push Hook (Auto-Index) installed.")

@app.command()
def index(
    repo_root: Path = typer.Option(".", "--repo-root", help="Project root directory."),
    connect: Optional[List[str]] = typer.Option(None, "--connect", help="Connect shared memory repositories.")
):
    """Index the current workspace into the Omega RAG Vector Store."""
    console.print(ASCII_ART)
    root = repo_root.resolve()
    logger = setup_logger(root)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Indexing Cognitive Nucleotides...", total=None)
        store = omega_engine.initialize_omega_store(root, external_roots=connect)
        omega_engine.index_workspace(root, store)
    
    logger.info("Indexing complete", extra={"repo_root": str(root)})
    console.print(Panel(f"[bold blue]Success:[/bold blue] Omega Oracle indexed `{root.name}`. Semantic search now online.", title="Celestial Indexer", expand=False))

@app.command()
def query(
    q: str = typer.Argument(..., help="Semantic query to search project history."),
    repo_root: Path = typer.Option(".", "--repo-root", help="Project root directory.")
):
    """Query project history semantically via Omega Oracle."""
    root = repo_root.resolve()
    store = omega_engine.initialize_omega_store(root)
    results = omega_engine.query_continuity(store, q)
    
    console.print(f"\n[bold cyan][*] OMEGA Results for: '{q}'[/bold cyan]")
    for i, doc in enumerate(results['documents'][0]):
        filename = results['metadatas'][0][i]['filename']
        console.print(Panel(doc[:500] + "...", title=f"Result {i+1} ({filename})", border_style="cyan"))

@app.command()
def map(
    repo_root: Path = typer.Option(".", "--repo-root", help="Project root directory.")
):
    """Generate an interactive 3D cognitive map of decisions."""
    root = repo_root.resolve()
    output_dir = root / "outputs" / "continuity"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    log = root / ".continuity" / "DECISIONS_LOG.md"
    if not log.exists():
        console.print("[yellow]No DECISIONS_LOG found. Use `log` to create one.[/yellow]")
        return
        
    nodes = cognitive_map.extract_decisions(str(log))
    graph = cognitive_map.generate_cognitive_map(nodes)
    cognitive_map.export_map(graph, str(output_dir / "cognitive_map.json"))
    
    console.print(Panel(f"[bold cyan]Map Generated:[/bold cyan] [italic]{output_dir / 'cognitive_map.json'}[/italic]", border_style="cyan"))

@app.command()
def log(
    intent: str = typer.Argument(..., help="Detailed session intent capture."),
    repo_root: Path = typer.Option(".", "--repo-root", help="Project root directory.")
):
    """Log an intent with automatic cognitive impact analysis."""
    root = repo_root.resolve()
    store = omega_engine.initialize_omega_store(root)
    conflicts = omega_engine.check_impact_analysis(store, intent)
    
    if conflicts:
        console.print("\n[bold red][!] OMEGA IMPACT ALERT:[/bold red] Contradiction detected:")
        for c in conflicts:
            console.print(f"    - [{c['file']}]: [italic]\"{c['rule']}\"[/italic]")
        
        console.print("\n[bold cyan][?] CONTEXTUAL CHOICE:[/bold cyan]")
        console.print("  1. [RECONCILE] I will follow the rules.")
        console.print("  2. [OVERRIDE] Concious evolution (PIVOT).")
        console.print("  3. [CANCEL] Cancel operation.")
        
        choice = typer.prompt("Select [1/2/3]", default="1")
        if choice == "2":
            intent = f"[PIVOT] {intent}"
        elif choice == "3":
            raise typer.Exit()
            
    log_path = root / "SESSION_LOG.md"
    if not log_path.exists():
            log_path.write_text("# Continuity Session Log\n\n", encoding="utf-8")
        
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"- [{datetime.now().isoformat()}Z] {intent}\n")
    
    console.log(f"[bold blue][âœ”][/bold blue] Intent captured in SESSION_LOG.md")

def main():
    app()

if __name__ == "__main__":
    main()
