import os
import sys
import json
from pathlib import Path
from typing import Optional, List, Dict
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
import tiktoken

# Ethernium Token Sentinel (v1.0.0 - Industrial Telemetry)
# Purpose: Reverse-engineer LLM context usage and optimize cognitive density.

app = typer.Typer(help="Ethernium Token Sentinel: Telemetry & Context Audit")
console = Console()

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
    
    if total_tokens > 100000:
        console.print("[bold red][!] WARNING: High Context Weight. You are approaching LLM attention limits.[/bold red]")

@app.command()
def audit(file: str = typer.Argument(..., help="Specific file to audit")):
    """Deep audit of a single file to find 'Cognitive Waste'."""
    f_path = Path(file)
    if not f_path.exists():
        console.print(f"[red]Error: File {file} not found.[/red]")
        return
        
    stats = analyze_file_density(f_path)
    console.print(Panel(f"File: {file}\nTokens: {stats['tokens']}\nDensity: {stats['density']} T/L", title="File Insight"))

def main():
    app()

if __name__ == "__main__":
    main()
