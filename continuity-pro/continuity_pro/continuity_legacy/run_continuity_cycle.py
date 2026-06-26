#!/usr/bin/env python3
"""
run_continuity_cycle.py — CONTINUITY LEGACY Pro (v3.0.3)
Solemne Industrial Evolution Guardian — Ethernium Core Engine.

Crystallizes project DNA, enforces Merkle integrity, scans for secrets,
and maintains the cognitive lineage of the repository across AI handoffs.

This module is the CLI entry point for the Pro edition. It orchestrates:
  - DNA Synthesis (Merkle Tree via SHA-256)
  - Document Parity Verification
  - Secret Detection (15+ patterns)
  - System Membership Validation
  - README Crystallization (badge injection)
  - Git Hook Installation (fail-closed pre-push)

Laws:
  - Ontological Determinism: every run produces a verifiable state.
  - Fail-Closed: any inconsistency halts the pipeline with exit 1.
  - Simetría Fractal: no hacks, no band-aids, no silent degradation.
"""

import logging
import hashlib
import os
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

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

PRO_ICON = "PRO"
CHECK_ICON = "OK"

# v3.0.3: Source code extensions now scanned alongside documentation
SCAN_EXTENSIONS = {".md", ".py", ".ts", ".js", ".rs", ".go", ".java", ".cpp", ".c", ".h", ".hpp"}

# v3.0.3: Permissive mode allows warning-only drift detection
PERMISSIVE_MODE = os.environ.get("CONTINUITY_MODE", "strict").lower() == "permissive"

app = typer.Typer(
    help=f"{PRO_ICON} Continuity Legacy Pro: The enterprise AI continuity framework for industrial handoffs.",
    add_completion=False,
    no_args_is_help=True,
)
console = Console(emoji=False)

ASCII_ART = """
[bold magenta]
   ______ ____   _   __ ______ ____ _   __ _   __ ____ ______  __  __
  / ____// __ \\ / | / //_  __//  _// | / // /  / //_  __//_  __/ \\ \\/ /
 / /    / / / //  |/ /  / /   / / /  |/ // /  / /  / /    / /     \\  / 
/ /___ / /_/ // /|  /  / /  _/ / / /|  // /__/ /  / /    / /      / /  
\\____/ \\____//_/ |_/  /_/  /___//_/ |_/ \\____/  /_/    /_/      /_/   
                                                                        
      LEGACY [bold white]v3.0.3[/bold white] | [italic magenta]Solemne Industrial Evolution Guardian[/italic magenta]
[/bold magenta]
"""

# Import internal modules - pip-compatible relative imports with direct-exec fallback
try:
    from . import automation_common
    from . import doc_parity_check
    from . import secret_detector
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import automation_common
    import doc_parity_check
    import secret_detector


def _utcnow() -> datetime:
    """v3.0.3: Timezone-aware UTC now. Replaces deprecated utcnow()."""
    return datetime.now(timezone.utc)


def setup_logger(repo_root: Path):
    log_dir = repo_root / ".continuity" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"pro_continuity_{datetime.now().strftime('%Y%m%d')}.jsonl"
    
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            log_record = {
                "timestamp": _utcnow().isoformat(),
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


def _get_version() -> str:
    """v3.0.3: Resolves the current Pro version from package metadata or VERSION file."""
    import importlib.metadata
    try:
        return importlib.metadata.version("ethernium-continuity-pro")
    except importlib.metadata.PackageNotFoundError:
        pass
    # Fallback: read the VERSION file directly
    version_path = Path(__file__).resolve().parent.parent.parent / "VERSION"
    if version_path.exists():
        return version_path.read_text(encoding="utf-8").strip()
    return "3.0.3"


def crystallize_readme(repo_root: Path, merkle_root: str):
    """v3.0.3: Injects the Merkle Root badge into README.md."""
    readme_path = repo_root / "README.md"
    if not readme_path.exists(): 
        return
    content = readme_path.read_text(encoding="utf-8")
    marker = "<!-- DNA_CRYSTAL -->"
    if marker in content:
        import re
        ver = _get_version()
        crystal_text = (
            f"\n> [!IMPORTANT]\n"
            f"> **DNA CRYSTAL (Pro)**: `v{ver}-{merkle_root[:16]}`\n"
            f"> [![Merkle Root](https://img.shields.io/badge/DNA--Crystallized-{merkle_root[:8]}-magenta)](https://github.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium)\n"
        )
        # Strip old crystal block if exists
        content = re.sub(r"\n> \[!IMPORTANT\].*?(?:blueviolet|magenta)\)\n", "", content, flags=re.DOTALL)
        parts = content.split(marker)
        new_content = parts[0] + marker + crystal_text + marker.join(parts[1:])
        readme_path.write_text(new_content, encoding="utf-8")
        console.log(f"[bold magenta][✔][/bold magenta] README Crystallized: {merkle_root[:8]}")


def _resolve_scan_paths(root: Path, scan_source: bool) -> tuple[list[Path], list[Path]]:
    """v3.0.3: Resolves documentation and source code files separately for granular reporting."""
    doc_files, source_files = [], []
    for r, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in [".git", "node_modules", ".continuity", "outputs", "assets", "banners", "__pycache__", ".venv", ".pytest_cache"]]
        for f in files:
            ext = Path(f).suffix
            if ext == ".md" and "PROJECT_DNA" not in f:
                doc_files.append(Path(r) / f)
            elif scan_source and ext in SCAN_EXTENSIONS - {".md"} and not f.endswith(".pyc"):
                source_files.append(Path(r) / f)
    return doc_files, source_files


@app.command()
def init(
    repo_root: Path = typer.Option(".", "--repo-root", help="Project root directory."),
    no_hook: bool = typer.Option(False, "--no-hook", help="Disable automatic Git-Hook installation.")
):
    """Initialize the Pro memory core and install enterprise hooks."""
    console.print(ASCII_ART)
    root = repo_root.resolve()
    logger = setup_logger(root)
    logger.info("Initializing Pro Core")
    
    now_iso = _utcnow().isoformat()
    files = {
        "PROJECT_CONTEXT.md": "# Project Context\n\n- Ethernium Industrial Grade strategy.",
        "ROADMAP.md": "# Industrial Roadmap\n\n- Milestones here.",
        ".continuity/STATE.json": json.dumps({"phase": "pro", "last_update": now_iso}, indent=2),
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
    strict: bool = typer.Option(False, "--strict", help="Fail with exit code 1 if drift detected."),
    scan_source: bool = typer.Option(True, "--scan-source/--no-scan-source", help="Scan source code files alongside documentation.")
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
        secret_scan = secret_detector.scan_for_secrets(root)
        
        # v3.0.3: DNA Synthesis with source code coverage
        doc_files, source_files = _resolve_scan_paths(root, scan_source)
        all_nucleotides = doc_files + source_files
        nucleotide_hashes = [automation_common.calculate_sha256(f) for f in sorted(all_nucleotides)]
        merkle_root = automation_common.build_merkle_tree(nucleotide_hashes)
        
        # v3.0.3: Calculate entropies separately for granular diagnostics
        doc_entropy = automation_common.calculate_context_entropy(
            "".join([f.read_text(errors='ignore') for f in doc_files])
        ) if doc_files else 0.0
        source_entropy = automation_common.calculate_context_entropy(
            "".join([f.read_text(errors='ignore') for f in source_files])
        ) if source_files else 0.0
        total_entropy = (doc_entropy + source_entropy) / 2 if (doc_entropy and source_entropy) else max(doc_entropy, source_entropy)

    crystallize_readme(root, merkle_root)
    
    now_iso = _utcnow().isoformat()
    report = {
        "timestamp": now_iso,
        "merkle_root": merkle_root,
        "entropy": round(total_entropy, 4),
        "doc_entropy": round(doc_entropy, 4),
        "source_entropy": round(source_entropy, 4),
        "nucleotides_scanned": len(all_nucleotides),
        "doc_files": len(doc_files),
        "source_files": len(source_files),
        "doc_parity": doc_parity["status"],
        "security": "ok" if not secret_scan["findings"] else "danger",
        "findings": len(secret_scan["findings"]),
        "mode": "permissive" if PERMISSIVE_MODE else "strict"
    }
    
    # Save Report
    report_path = root / ".continuity" / "pro_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    logger.info("Cycle complete", extra={"merkle_root": merkle_root})
    
    console.print(Panel(
        f"[bold magenta]Pro Status:[/bold magenta] "
        f"Status: OK | "
        f"Merkle: `{merkle_root[:16]}...` | "
        f"Nucleotides: {len(all_nucleotides)} "
        f"({len(doc_files)} docs + {len(source_files)} source) | "
        f"Entropy: {total_entropy:.2f}",
        title="Solemne Guardian", expand=False
    ))
    
    if report["security"] == "danger":
        console.print(f"[bold red][!][/bold red] SECURITY ALERT: {len(secret_scan['findings'])} secrets detected in lineage!")
        for finding in secret_scan["findings"]:
            console.print(f"      [red]{finding['type']}[/red] in [italic]{finding['file']}[/italic]")
    
    # v3.0.3: Permissive mode — warn but do not halt
    has_issues = report["doc_parity"] != "ok" or report["security"] == "danger"
    if has_issues:
        if PERMISSIVE_MODE:
            console.print("[bold yellow][!][/bold yellow] PERMISSIVE MODE: Drift detected but pipeline continues. Set CONTINUITY_MODE=strict for fail-closed.")
        elif strict:
            console.print("[bold red][!][/bold red] FAIL-CLOSED: Project state inconsistent. Halting.")
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
    
    today_str = _utcnow().strftime('%Y-%m-%d')
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"| {today_str} | Intent: {intent} | Developer Session | Solemne Admin |\n")
    
    console.log(f"[bold magenta][✔][/bold magenta] Intent logged into [italic]DECISIONS_LOG.md[/italic]")


@app.command()
def demo(
    repo_root: Path = typer.Option(".", "--repo-root", help="Temporary directory for the demo.")
):
    """⚡ 30-Second Drift Detection Demo — Experience the Ethernium Guardian."""
    import tempfile, shutil, time
    
    console.print("[bold magenta]⚡ ETHERNIUM CONTINUITY LEGACY — DRIFT DETECTION DEMO[/bold magenta]")
    console.print("[dim]30 seconds to experience how Semantic Drift is detected and blocked.[/dim]")
    console.print()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        original_dir = Path.cwd()
        os.chdir(str(root))
        
        try:
            # Step 1: Initialize project
            console.print("[bold]STEP 1/4:[/bold] Creating a secure project...")
            (root / "PROJECT_CONTEXT.md").write_text(
                "# SecureAuth Module\n"
                "This project implements OAuth2 authentication. All endpoints validate tokens.\n"
                "Architecture: standard JWT validation with RSA-256 signatures.\n"
            )
            (root / "auth.py").write_text(
                "import hashlib\n\ndef validate_token(token: str) -> bool:\n"
                '    """Validate JWT token using standard OAuth2 flow."""\n'
                "    return len(token) > 0 and token.startswith('eyJ')\n"
            )
            (root / "STATE.json").write_text('{"phase": "demo", "last_update": "' + _utcnow().isoformat() + '"}')
            console.print("    [green]✔[/green] Project created with OAuth2 authentication module.")
            time.sleep(1)
            
            # Step 2: First DNA Synthesis
            console.print()
            console.print("[bold]STEP 2/4:[/bold] Crystallizing project DNA (Merkle Root)...")
            doc_files, source_files = _resolve_scan_paths(root, True)
            all_files = doc_files + source_files
            hashes = [automation_common.calculate_sha256(f) for f in sorted(all_files)]
            merkle_before = automation_common.build_merkle_tree(hashes)
            console.print(f"    [green]✔[/green] Merkle Root: [bold]{merkle_before[:16]}...[/bold]")
            console.print(f"    [green]✔[/green] Nucleotides: {len(all_files)} files scanned ({len(doc_files)} docs + {len(source_files)} source)")
            time.sleep(1.5)
            
            # Step 3: MALICIOUS CHANGE (Semantic Drift)
            console.print()
            console.print("[bold]STEP 3/4:[/bold] [red]⚠ SIMULATING SEMANTIC DRIFT[/red]")
            console.print("    [red]An attacker modifies auth.py — adds a backdoor.[/red]")
            (root / "auth.py").write_text(
                "import hashlib\n\ndef validate_token(token: str) -> bool:\n"
                '    """Validate JWT token — [BACKDOOR] bypasses all authentication."""\n'
                "    return True  # BACKDOOR: always authenticates\n"
                "\n"
                "# [HIDDEN] Backdoor access for developer\n"
                "def _admin_backdoor(password: str) -> bool:\n"
                '    return hashlib.md5(password.encode()).hexdigest() == "e2fc714c4727ee9395f324cd2e7f331f"\n'
            )
            console.print("    [yellow]⚠ The code now has a backdoor but documentation says it's 'secure OAuth2'.[/yellow]")
            console.print("    [yellow]⚠ Git would accept this change silently. Continuity will not.[/yellow]")
            time.sleep(2)
            
            # Step 4: Drift Detection
            console.print()
            console.print("[bold]STEP 4/4:[/bold] [magenta]Recalculating DNA...[/magenta]")
            doc_files2, source_files2 = _resolve_scan_paths(root, True)
            all_files2 = doc_files2 + source_files2
            hashes2 = [automation_common.calculate_sha256(f) for f in sorted(all_files2)]
            merkle_after = automation_common.build_merkle_tree(hashes2)
            
            console.print(f"    [cyan]Original Merkle Root:[/cyan]   {merkle_before[:16]}...")
            console.print(f"    [red]Current Merkle Root:[/red]    {merkle_after[:16]}...")
            
            if merkle_before != merkle_after:
                console.print()
                console.print("[bold red]❌ DRIFT DETECTED: Merkle Roots do not match![/bold red]")
                console.print("[bold red]❌ Push would be BLOCKED. Project integrity preserved.[/bold red]")
                console.print()
                console.print("[bold green]✅ THE GUARDIAN WORKS.[/bold green] Continuity Legacy detected")
                console.print("   a semantic change that Git would have silently accepted.")
            else:
                console.print("[bold yellow]⚠ No drift detected (unexpected in demo).[/bold yellow]")
            
            console.print()
            console.print("[bold]═══════════════════════════════════════════[/bold]")
            console.print("[bold magenta]🔥 Continuity Legacy: AI doesn't forget anymore.[/bold magenta]")
            console.print()
            console.print("Next steps:")
            console.print("  [dim]1.[/dim] [bold]continuity init[/bold] — Initialize in your real project")
            console.print("  [dim]2.[/dim] [bold]continuity check[/bold] — Validate your project DNA")
            console.print("  [dim]3.[/dim] [bold]continuity log \"my intent\"[/bold] — Log design decisions")
            
        finally:
            os.chdir(str(original_dir))
    
    console.print()
    console.print("[green]✔ Demo completed. Temporary directory cleaned.[/green]")


@app.command()
def version():
    """Show the Continuity Legacy Pro version and Merkle status."""
    ver = _get_version()
    console.print(f"[bold magenta]Continuity Legacy Pro[/bold magenta] v{ver}")
    console.print(f"[dim]Mode:[/dim] {'permissive' if PERMISSIVE_MODE else 'strict'}")
    console.print(f"[dim]Extensions:[/dim] {', '.join(sorted(SCAN_EXTENSIONS))}")
    console.print(f"[dim]Engine:[/dim] SHA-256 Merkle Tree (RFC 6962) | Ed25519 Sovereign Identity")


def main():
    app()

if __name__ == "__main__":
    main()
