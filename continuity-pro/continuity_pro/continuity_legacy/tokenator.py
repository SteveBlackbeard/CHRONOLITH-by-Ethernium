import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
import tiktoken
from continuity_pro.continuity_legacy.ene_optimizer import ENEOptimizer
from continuity_pro.continuity_legacy.zip_bridge import create_portal_zip, verify_portal
from continuity_pro.continuity_legacy.sovereign_identity import get_identity
import math

app = typer.Typer(help="Ethernium Tokenator: Autonomic Context Telemetry & Optimization")
console = Console()

# ETHERNIUM TOKENATOR (v1.0.4 - NEXUS)
# Purpose: Reverse-engineer LLM context usage and automate cognitive density.

def count_tokens(text: str, model: str = "gpt-4-0613") -> int:
    """Estimates token count using tiktoken (Industry Standard)."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base") # Fallback for modern models
    return len(encoding.encode(text))

def analyze_file_density(file_path: Path) -> Dict:
    """Calculates Semantic Density (Tokens per Line)."""
    try:
        content = file_path.read_text(encoding="utf-8")
        tokens = count_tokens(content)
        lines = len(content.splitlines()) or 1
        density = tokens / lines
        return {
            "tokens": tokens,
            "lines": lines,
            "density": round(density, 2),
            "size_kb": round(len(content.encode("utf-8")) / 1024, 2)
        }
    except Exception as e:
        return {"error": str(e)}

@app.command()
def scan(
    path: str = typer.Argument(".", help="Path to scan (defaults to current dir)"),
    exclude: Optional[str] = typer.Option(".git,.venv,__pycache__,node_modules,dist", help="Comma-separated dirs to exclude")
):
    """Recursively scans the project to measure its Cognitive Weight."""
    root = Path(path).resolve()
    exclude_list = exclude.split(",")
    results = []
    total_tokens = 0
    total_files = 0
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Scanning DNA...", total=None)
        
        for file in root.rglob("*.md"):
            if any(ex in str(file) for ex in exclude_list): continue
            
            stats = analyze_file_density(file)
            if "error" in stats: continue
            
            results.append((file.relative_to(root), stats))
            total_tokens += stats["tokens"]
            total_files += 1
            progress.update(task, advance=1)
            
        for file in root.rglob("*.py"):
            if any(ex in str(file) for ex in exclude_list): continue
            stats = analyze_file_density(file)
            if "error" in stats: continue
            results.append((file.relative_to(root), stats))
            total_tokens += stats["tokens"]
            total_files += 1

    # Display Results
    table = Table(title=f"🪐 Ethernium Cognitive Audit: {root.name}")
    table.add_column("Nucleotide (File)", style="cyan")
    table.add_column("Tokens", justify="right", style="magenta")
    table.add_column("LoC", justify="right", style="green")
    table.add_column("Density (T/L)", justify="right", style="yellow")
    
    # Sort by token count (descending) to find the "Context Heavy" files
    for f_path, s in sorted(results, key=lambda x: x[1]["tokens"], reverse=True)[:15]:
        table.add_row(
            str(f_path),
            str(s["tokens"]),
            str(s["lines"]),
            str(s["density"])
        )
        
    console.print(table)
    
    msg = f"Total Files: {total_files} | [bold cyan]Total Cognitive Weight: {total_tokens} tokens[/bold cyan]"
    console.print(Panel(msg, title="[bold]Summary[/bold]", border_style="green"))
    
    if total_tokens > 20000:
        console.print("[bold yellow][!] SUGGESTION: Run 'continuity-tokens optimize' to apply Ethernium Nucleotide Encoding (ENE) (x10 efficiency).[/bold yellow]")

@app.command()
def optimize(
    path: str = typer.Argument(".", help="Path to optimize")
):
    """Applies ENE (Ethernium Nucleotide Encoding) to the project to reduce token cost."""
    optimizer = ENEOptimizer()
    console.print("[bold cyan]Applying ENE optimization...[/bold cyan]")
    # Logic to optimize specific large files like PROJECT_DNA.md
    dna_path = Path(path) / "PROJECT_DNA.md"
    if dna_path.exists():
        original = dna_path.read_text(encoding="utf-8")
        compressed = optimizer.compress(original)
        # We save it as a nucleotide version to not overwrite the human README yet
        ene_path = dna_path.with_suffix(".ene.md")
        ene_path.write_text(compressed, encoding="utf-8")
        console.print(f"[✔] PROJECT_DNA.md optimized! Saved to {ene_path.name}")
        console.print(f"    Reduction: {len(original)} -> {len(compressed)} chars.")

def update_md_report(task: str, tokens: int):
    """Updates the SESSION_TOKEN_REPORT.md with the latest interaction."""
    report_path = Path("SESSION_TOKEN_REPORT.md")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_row = f"| {timestamp} | {task} | {tokens} | [DONE] |\n"
    
    if report_path.exists():
        content = report_path.read_text(encoding="utf-8")
        if "## 🛰️ Interaction Log (Timeline)" in content:
            parts = content.split("## 🛰️ Interaction Log (Timeline)")
            header = parts[0]
            log = parts[1]
            # Add entry to log
            # Simple append at the end of the table
            updated_content = header + "## 🛰️ Interaction Log (Timeline)" + log + new_row
            report_path.write_text(updated_content, encoding="utf-8")

@app.command()
def measure_interaction(
    scope: str = typer.Option("current", help="Scope: 'current' (active edits) or 'last' (previous commit)")
):
    """IA-T (AI Telemetry): Measures the real-time token cost and symbolic ROI of your turn."""
    console.print("[bold cyan]ℳᵣ Analyzing IA-T (Interaction Telemetry)...[/bold cyan]")
    try:
        import subprocess
        # Scope selection
        cmd = "git diff HEAD" if scope == "current" else "git diff HEAD^ HEAD"
        
        result = subprocess.check_output(cmd, shell=True, text=True)
        raw_tokens = count_tokens(result)
        
        # Calculate symbolic potential (v2.8.5)
        savings = 0.0
        symbolic_tokens = 0
        if raw_tokens > 0:
            optimizer = ENEOptimizer()
            symbolic_version = optimizer.compress(result)
            symbolic_tokens = count_tokens(symbolic_version)
            savings = (1 - (symbolic_tokens / raw_tokens)) * 100
        else:
            # If no diff, we report the cost of the session files edited
            console.print("[yellow][!] No changes detected in diff. Audit of staged area...[/yellow]")
            cmd_staged = "git diff --cached"
            result = subprocess.check_output(cmd_staged, shell=True, text=True)
            raw_tokens = count_tokens(result)
            if raw_tokens > 0:
                optimizer = ENEOptimizer()
                symbolic_version = optimizer.compress(result)
                symbolic_tokens = count_tokens(symbolic_version)
                savings = (1 - (symbolic_tokens / raw_tokens)) * 100

        table = Table(title=f"🪐 IA-T (Interaction Telemetry) - {scope.upper()}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_row("Turn Impact Tokens", str(raw_tokens))
        table.add_row("Symbolic Optimization", str(symbolic_tokens))
        table.add_row("Efficiency ROI", f"{savings:.1f}%")
        console.print(table)
        
        if raw_tokens > 0:
            update_md_report(f"IA-T: {scope} Scan (ROI: {savings:.1f}%)", raw_tokens)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@app.command()
def log_session(
    task: str = typer.Argument(..., help="Description of task"),
    tokens: int = typer.Argument(..., help="Tokens spent")
):
    """🆔ₛ Autonomic Session Logger (NEXUS v2.8.0)."""
    console.print(Panel(f"Task: {task}\nSpend: [bold magenta]{tokens} tokens[/bold magenta]", title="📊 Tokenator Live (IA-T)"))
    update_md_report(task, tokens)
    console.print("[green][✔] Token telemetry updated in SESSION_TOKEN_REPORT.md[/green]")

@app.command()
def zip(
    folder: str = typer.Argument(..., help="Folder to package into a Sovereign Portal"),
    output: Optional[str] = typer.Option(None, help="Output zip name")
):
    """Creates a Sovereign Ethernium Portal (ZIP) with Dual Bridge Identity."""
    console.print(f"[bold cyan]Creating Sovereign Portal for: {folder}...[/bold cyan]")
    result = create_portal_zip(folder, output)
    if "[✔]" in result:
        console.print(f"[green]{result}[/green]")
    else:
        console.print(f"[bold red]{result}[/bold red]")

@app.command()
def scan_zip(
    zip_path: str = typer.Argument(..., help="Zip file to scan via Portal Bridge")
):
    """Scans a Sovereign Portal without extraction to report its logical weight."""
    console.print(f"[bold cyan]Scanning Portal: {zip_path}...[/bold cyan]")
    info = verify_portal(zip_path)
    if "error" in info:
        console.print(f"[bold red]Error: {info['error']}[/bold red]")
        return
        
    status = "[green]VALID[/green]" if info["valid"] else "[bold red]INVALID/UNSIGNED[/bold red]"
    console.print(Panel(
        f"Portal: {info['portal_name']}\n"
        f"Sovereignty: {status}\n"
        f"Merkle Root: {info['merkle_root'][:16]}...\n"
        f"Ghost Map (Tokens): [bold magenta]{len(info['ghost_map'])}[/bold magenta]",
        title="Portal Insight (Dual Bridge)"
    ))

@app.command()
def audit(file: str = typer.Argument(..., help="Specific file to audit")):
    """Deep audit of a single file to find 'Cognitive Waste'."""
    f_path = Path(file)
    if not f_path.exists():
        console.print(f"[red]Error: File {file} not found.[/red]")
        return
        
    stats = analyze_file_density(f_path)
    console.print(Panel(f"File: {file}\nTokens: {stats['tokens']}\nDensity: {stats['density']} T/L", title="File Insight"))

@app.command()
def physics(path: str = typer.Argument(".", help="Path to audit")):
    """Φ_ENTROPY: Measures Shannon Entropy and Information Density of the DNA."""
    p_path = Path(path)
    if not p_path.exists(): return
    
    def shannon_entropy(data: str) -> float:
        if not data: return 0.0
        probabilities = [data.count(c) / len(data) for c in set(data)]
        return -sum(p * math.log2(p) for p in probabilities)

    results = []
    for f in p_path.rglob("*.md"):
        content = f.read_text(encoding="utf-8")
        h = shannon_entropy(content)
        results.append((f.name, h, len(content)))

    table = Table(title="⚛️ Ethernium Physics Dashboard (Information Theory)")
    table.add_column("Nucleotide", style="cyan")
    table.add_column("Entropy (H)", justify="right", style="magenta")
    table.add_column("Density (bits/char)", justify="right", style="green")
    
    for name, h, size in sorted(results, key=lambda x: x[1]):
        table.add_row(name, f"{h:.4f}", f"{h/8:.4f}")
    
    console.print(table)
    console.print(Panel("Lower Entropy (H) = Higher Logic Purity. Goal: < 5.0 for ENE scripts.", title="Physics Insight"))

@app.command()
def authorize(pubkey: str = typer.Argument(..., help="Public key hex to authorize")):
    """👑_CHOSEN: Authorizes a new collaborator in THE_CHOSEN_ONES."""
    identity = get_identity()
    identity.authorize_collaborator(pubkey)
    console.print(f"[green][✔] Identity {pubkey[:16]}... authorized in THE_CHOSEN_ONES.[/green]")

@app.command()
def seal(file: str = typer.Argument(..., help="File to seal using SDK")):
    """🔐_CTX: Seals a file into a Ghost State using Sovereign Identity."""
    f_path = Path(file)
    if not f_path.exists(): return
    identity = get_identity()
    original = f_path.read_bytes()
    sealed = identity.seal_context(original)
    
    sealed_path = f_path.with_suffix(".locked")
    sealed_path.write_text(sealed)
    console.print(f"[green][✔] File {file} sealed into {sealed_path.name}. (Identity Lock Active)[/green]")

@app.command()
def open_ctx(file: str = typer.Argument(..., help="Sealed file to open")):
    """🔓_CTX: Opens a Ghost State file using Sovereign Identity."""
    f_path = Path(file)
    if not f_path.exists(): return
    identity = get_identity()
    sealed = f_path.read_text()
    try:
        opened = identity.open_context(sealed)
        original_path = f_path.with_suffix(".restored.md")
        original_path.write_bytes(opened)
        console.print(f"[green][✔] Context opened! Restored to {original_path.name}.[/green]")
    except Exception as e:
        console.print(f"[bold red]{e}[/bold red]")

def main():
    app()

if __name__ == "__main__":
    main()
