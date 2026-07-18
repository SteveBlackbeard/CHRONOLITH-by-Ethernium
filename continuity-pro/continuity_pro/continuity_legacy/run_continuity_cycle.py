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

# Corrected figlet (the old one dropped letters — it read with a single T);
# {version} is filled from _get_version() at print time so the banner never
# goes stale again.
ASCII_ART = """
[bold magenta]
   __________  _   _____________   ____  ______________  __
  / ____/ __ \\/ | / /_  __/  _/ | / / / / /  _/_  __/\\ \\/ /
 / /   / / / /  |/ / / /  / //  |/ / / / // /  / /    \\  /
/ /___/ /_/ / /|  / / / _/ // /|  / /_/ // /  / /     / /
\\____/\\____/_/ |_/ /_/ /___/_/ |_/\\____/___/ /_/     /_/

      LEGACY [bold white]v{version}[/bold white] | [italic magenta]Solemne Industrial Evolution Guardian[/italic magenta]
[/bold magenta]
"""


def _banner() -> str:
    return ASCII_ART.format(version=_get_version())

# Import internal modules - pip-compatible relative imports with direct-exec fallback
try:
    from . import automation_common
    from . import doc_parity_check
    from . import secret_detector
    from . import sovereign_vault
    from . import anchor as anchor_mod
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import automation_common
    import doc_parity_check
    import secret_detector
    import sovereign_vault
    import anchor as anchor_mod


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


def _compute_leaves(root: Path, scan_source: bool) -> tuple[list[Path], list[Path], dict[str, str]]:
    """Shared leaf computation for check/prove: path-bound leaves keyed by
    relative path, hashed through the incremental mtime+size cache."""
    doc_files, source_files = _resolve_scan_paths(root, scan_source)
    cache = automation_common.load_hash_cache(root)
    leaves: dict[str, str] = {}
    for f in sorted(doc_files + source_files):
        rel = f.relative_to(root).as_posix()
        leaves[rel] = automation_common.path_bound_leaf(
            rel, automation_common.calculate_sha256_cached(f, cache)
        )
    automation_common.save_hash_cache(root, cache)
    return doc_files, source_files, leaves


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
    console.print(_banner())
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
    scan_source: bool = typer.Option(True, "--scan-source/--no-scan-source", help="Scan source code files alongside documentation."),
    accept: bool = typer.Option(False, "--accept", help="Accept the current content as the new canonical baseline (like `git commit`): advances the signed baseline and appends a transparency-chain entry even though the root changed. Without this, an intentional edit is reported as drift and the baseline is NOT advanced."),
):
    """Validate full project parity, doc-immunity, and security audits."""
    console.print(_banner())
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
        # Path-bound leaves (rename/content-swap change the root), incremental cache.
        doc_files, source_files, leaves = _compute_leaves(root, scan_source)
        all_nucleotides = doc_files + source_files
        nucleotide_hashes = list(leaves.values())
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

    # v3.0.4: REAL DNA drift detection. Previously the Merkle root was computed and
    # crystallized but never compared to a baseline, so document drift was never
    # actually caught — the guardian only halted on secrets/doc-parity. Now the
    # signed baseline in .continuity/STATE.json is verified and compared.
    state_path = root / ".continuity" / "STATE.json"
    dna_drift = False
    signature_tampered = False
    private_bytes, public_bytes = automation_common.load_sovereign_keys(root)
    trusted_keys = (
        sovereign_vault.historically_valid_pubkeys(root / ".continuity" / "keys", public_bytes)
        if public_bytes else None
    )
    if state_path.exists():
        try:
            stored_state = json.loads(state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            stored_state = {}
        if not automation_common.verify_signature(stored_state):
            signature_tampered = True
            console.print("[bold red][!] STATE.json signature invalid — the DNA baseline was tampered with.[/bold red]")
        # Ed25519 layer: the checksum only catches accidents; a real signature
        # cannot be recomputed by an attacker. Trust anchor = local public key.
        sovereign_ok = automation_common.verify_sovereign_state(stored_state, trusted_public=trusted_keys)
        if sovereign_ok is False:
            signature_tampered = True
            console.print("[bold red][!] Sovereign Ed25519 signature INVALID — baseline not signed by this repository's key.[/bold red]")
        elif sovereign_ok is None and public_bytes and stored_state.get("merkle_root"):
            console.print("[yellow][i] Sovereign key present but baseline unsigned; it will be sovereign-signed on this crystallization.[/yellow]")
        stored_root = stored_state.get("merkle_root")
        if (
            not signature_tampered
            and stored_root
            and stored_state.get("leaf_format") == automation_common.LEAF_FORMAT
            and stored_root != merkle_root
        ):
            if accept:
                # Operator asserts the change is intentional: advance the
                # baseline and grow the chain (this is the legitimate way the
                # transparency log gains entries). Signature tamper is NOT
                # acceptable this way — that path already set signature_tampered.
                console.print("[green][✔] Root changed — accepted as the new canonical baseline (--accept).[/green]")
            else:
                dna_drift = True
                console.print("[bold yellow][!] DNA DRIFT DETECTED:[/bold yellow]")
                console.print(f"    Current:  [cyan]{merkle_root[:16]}...[/cyan]")
                console.print(f"    Expected: [magenta]{stored_root[:16]}...[/magenta]")
                console.print("[dim]    If this change is intentional, re-run with --accept to advance the baseline.[/dim]")
    else:
        stored_state = {}

    # Update the signed baseline only when the lineage is intact (no drift / no
    # tamper), so a drifting repo keeps its original baseline for the fail-closed
    # decision below instead of silently re-crystallizing the drift as canonical.
    chain_ok, chain_issues = automation_common.verify_chain(root, trusted_public=trusted_keys)
    if not chain_ok:
        console.print("[bold red][!] DNA transparency chain BROKEN:[/bold red]")
        for issue in chain_issues[:5]:
            console.print(f"    [red]{issue}[/red]")
    # Red-team A4: a valid chain can still be truncated. The existing chain head
    # must record the existing baseline; a mismatch means entries were dropped.
    _chain = automation_common.read_chain(root)
    if chain_ok and _chain and stored_state.get("merkle_root") and _chain[-1].get("merkle_root") != stored_state.get("merkle_root"):
        chain_ok = False
        console.print("[bold red][!] Transparency chain HEAD does not match the baseline — chain truncated or tampered.[/bold red]")

    if not dna_drift and not signature_tampered and chain_ok:
        stored_state.update({
            "merkle_root": merkle_root,
            "leaf_format": automation_common.LEAF_FORMAT,
            "last_check": _utcnow().isoformat(),
        })
        stored_state["signature"] = automation_common.sign_state(stored_state)
        if private_bytes and public_bytes:
            automation_common.sovereign_sign_state(stored_state, private_bytes, public_bytes)
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(stored_state, indent=2), encoding="utf-8")
        # Record the crystallization event in the append-only transparency chain
        # (no-op when the root is unchanged), so lineage history is verifiable.
        # Once a sovereign identity exists, ONLY signed entries may enter the
        # chain — appending unsigned while the vault is locked would poison
        # verification forever. Postpone instead.
        if private_bytes or not public_bytes:
            automation_common.append_chain_entry(root, merkle_root, private_bytes=private_bytes)
        else:
            console.print("[yellow][i] Vault locked (CONTINUITY_PASSPHRASE unset): chain entry postponed until the key is available.[/yellow]")

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
        "dna_drift": dna_drift,
        "signature_tampered": signature_tampered,
        "chain": "ok" if chain_ok else "broken",
        "chain_length": len(automation_common.read_chain(root)),
        "signing": "ed25519" if (private_bytes and public_bytes) else "checksum-only",
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
    has_issues = report["doc_parity"] != "ok" or report["security"] == "danger" or dna_drift or signature_tampered or not chain_ok
    if has_issues:
        if PERMISSIVE_MODE:
            console.print("[bold yellow][!][/bold yellow] PERMISSIVE MODE: Drift detected but pipeline continues. Set CONTINUITY_MODE=strict for fail-closed.")
        elif strict:
            console.print("[bold red][!][/bold red] FAIL-CLOSED: Project state inconsistent. Halting.")
            raise typer.Exit(code=1)


@app.command()
def sovereign_init(
    repo_root: Path = typer.Option(".", "--repo-root", help="Project root directory."),
    encrypt: bool = typer.Option(False, "--encrypt", help="Protect the private keys at rest with a passphrase (CONTINUITY_PASSPHRASE env var; scrypt + ChaCha20-Poly1305)."),
):
    """Generate the sovereign identity: Ed25519 signing keys + X25519 encryption
    keys. From then on baselines/chain entries are REALLY signed and context can
    be REALLY encrypted (the checksum alone only detects accidents)."""
    root = repo_root.resolve()
    key_dir = root / ".continuity" / "keys"
    priv, _pub = automation_common.load_sovereign_keys(root)
    if priv or (key_dir / "sovereign.priv.enc").exists():
        console.print("[yellow][i] Sovereign keypair already exists — not overwriting. Use `sovereign-rotate` to renew.[/yellow]")
        raise typer.Exit(code=0)
    try:
        priv_path, pub_path = automation_common.generate_sovereign_keys(root)
        seal_priv, seal_pub = sovereign_vault.generate_x25519_keys(key_dir)
    except ImportError:
        console.print("[bold red][!] The 'cryptography' package is required: pip install cryptography[/bold red]")
        raise typer.Exit(code=1)

    vault_note = "plaintext on disk (pass --encrypt for an at-rest vault)"
    if encrypt:
        passphrase = os.environ.get("CONTINUITY_PASSPHRASE", "")
        if not passphrase:
            console.print("[bold red][!] --encrypt requires the CONTINUITY_PASSPHRASE environment variable.[/bold red]")
            raise typer.Exit(code=1)
        for plain in (priv_path, seal_priv):
            payload = sovereign_vault.encrypt_private_key(plain.read_bytes(), passphrase)
            plain.with_suffix(plain.suffix + ".enc").write_text(json.dumps(payload, indent=2), encoding="utf-8")
            plain.unlink()
        vault_note = "ENCRYPTED at rest (scrypt + ChaCha20-Poly1305; unlock via CONTINUITY_PASSPHRASE)"

    console.print(Panel(
        f"[bold green]Sovereign identity forged.[/bold green]\n"
        f"Signing (Ed25519):    [italic]{pub_path.name}[/italic]\n"
        f"Encryption (X25519):  [italic]{seal_pub.name}[/italic]\n"
        f"Private keys: {vault_note}\n"
        f"[dim]Keep .priv/.enc files out of Git (gitignored as *.priv).[/dim]",
        title="Sovereign Vault", expand=False,
    ))


@app.command()
def sovereign_rotate(
    repo_root: Path = typer.Option(".", "--repo-root", help="Project root directory."),
):
    """Rotate the Ed25519 signing key: the OLD key signs a hand-off statement to
    the NEW key, so history signed by retired keys remains verifiable (mini-PKI).
    Compromised-key recovery: rotate, then re-run `check` to re-sign the baseline."""
    root = repo_root.resolve()
    key_dir = root / ".continuity" / "keys"
    old_priv, old_pub = automation_common.load_sovereign_keys(root)
    if not (old_priv and old_pub):
        console.print("[bold red][!] No unlockable sovereign keypair to rotate (missing keys or locked vault without CONTINUITY_PASSPHRASE).[/bold red]")
        raise typer.Exit(code=1)
    from cryptography.hazmat.primitives.asymmetric import ed25519 as _ed
    from cryptography.hazmat.primitives import serialization as _ser
    new_key = _ed.Ed25519PrivateKey.generate()
    new_priv = new_key.private_bytes(_ser.Encoding.Raw, _ser.PrivateFormat.Raw, _ser.NoEncryption())
    new_pub = new_key.public_key().public_bytes(_ser.Encoding.Raw, _ser.PublicFormat.Raw)
    sovereign_vault.record_rotation(key_dir, old_priv, old_pub, new_pub, _utcnow().isoformat())
    (key_dir / "sovereign.priv").write_bytes(new_priv)
    (key_dir / "sovereign.pub").write_bytes(new_pub)
    enc = key_dir / "sovereign.priv.enc"
    if enc.exists():
        passphrase = os.environ.get("CONTINUITY_PASSPHRASE", "")
        payload = sovereign_vault.encrypt_private_key(new_priv, passphrase)
        enc.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        (key_dir / "sovereign.priv").unlink()
    console.print(Panel(
        f"[bold green]Key rotated.[/bold green]\n"
        f"Old: [dim]{old_pub.hex()[:16]}…[/dim] -> New: [bold]{new_pub.hex()[:16]}…[/bold]\n"
        f"Hand-off signed by the old key in [italic]{sovereign_vault.ROTATIONS_FILENAME}[/italic].\n"
        f"Run `check` to re-sign the baseline with the new key.",
        title="Sovereign Rotation", expand=False,
    ))


@app.command()
def attest(
    file: Path = typer.Option(..., "--file", help="File to attest (relative to repo root)."),
    repo_root: Path = typer.Option(".", "--repo-root", help="Project root directory."),
    output: Path = typer.Option(None, "--output", help="Write the attestation JSON here (default: stdout)."),
):
    """Sign a provenance attestation for one file: WHO (which key) states that
    THIS content existed at THIS time. The building block for multi-agent
    provenance over THE_CHOSEN_ONES."""
    root = repo_root.resolve()
    priv, pub = automation_common.load_sovereign_keys(root)
    if not (priv and pub):
        console.print("[bold red][!] Sovereign private key required (run `sovereign-init`, or unlock the vault).[/bold red]")
        raise typer.Exit(code=1)
    target = (root / file) if not file.is_absolute() else file
    if not target.exists():
        console.print(f"[bold red][!] File not found: {target}[/bold red]")
        raise typer.Exit(code=1)
    rel = target.resolve().relative_to(root).as_posix()
    att = sovereign_vault.build_attestation(
        rel, automation_common.calculate_sha256(target), pub, _utcnow().isoformat()
    )
    sovereign_vault.sign_attestation(att, priv)
    text = json.dumps(att, indent=2, sort_keys=True)
    if output:
        output.write_text(text, encoding="utf-8")
        console.print(f"[bold green][✔][/bold green] Attestation written: [italic]{output}[/italic]")
    else:
        print(text)


@app.command()
def verify_attest(
    attestation: Path = typer.Option(..., "--attestation", help="Attestation JSON produced by `attest`."),
    repo_root: Path = typer.Option(".", "--repo-root", help="Project root directory."),
):
    """Verify an attestation: signature valid, signer authorized (current
    sovereign, a legitimately rotated-out key, or one of THE_CHOSEN_ONES), and
    file content unchanged since it was attested."""
    root = repo_root.resolve()
    key_dir = root / ".continuity" / "keys"
    att = json.loads(attestation.read_text(encoding="utf-8"))
    _priv, pub = automation_common.load_sovereign_keys(root)

    authorized = sovereign_vault.historically_valid_pubkeys(key_dir, pub)
    chosen_file = key_dir / "chosen_ones.json"
    if chosen_file.exists():
        authorized += [bytes.fromhex(item) for item in json.loads(chosen_file.read_text(encoding="utf-8"))]

    ok, reason = sovereign_vault.verify_attestation(att, authorized)
    if not ok:
        console.print(f"[bold red][✘] ATTESTATION REJECTED:[/bold red] {reason}")
        raise typer.Exit(code=1)
    target = root / att["file"]
    current = automation_common.calculate_sha256(target)
    if current != att.get("sha256"):
        console.print(f"[bold red][✘] CONTENT CHANGED since attestation:[/bold red] '{att['file']}' no longer matches the attested hash.")
        raise typer.Exit(code=1)
    console.print(f"[bold green][✔] ATTESTATION VALID:[/bold green] '{att['file']}' attested by {att['signer_pub'][:16]}… at {att['ts'][:19]} — content unchanged.")


@app.command()
def chain(
    repo_root: Path = typer.Option(".", "--repo-root", help="Project root directory."),
    verify: bool = typer.Option(True, "--verify/--no-verify", help="Verify linkage, hashes and signatures."),
):
    """Show and verify the DNA transparency chain (append-only lineage of roots)."""
    root = repo_root.resolve()
    entries = automation_common.read_chain(root)
    if not entries:
        console.print("[yellow]Transparency chain is empty — run `check` to crystallize the first entry.[/yellow]")
        raise typer.Exit(code=0)
    table = Table(title=f"DNA Transparency Chain ({len(entries)} entries)", header_style="bold magenta")
    table.add_column("Seq", justify="right")
    table.add_column("Timestamp", style="dim")
    table.add_column("Merkle Root")
    table.add_column("Signed")
    for e in entries:
        table.add_row(str(e.get("seq")), str(e.get("timestamp", ""))[:19],
                      str(e.get("merkle_root", ""))[:16] + "…",
                      "ed25519" if e.get("sovereign_signature") else "—")
    console.print(table)
    if verify:
        _priv, pub = automation_common.load_sovereign_keys(root)
        keys = sovereign_vault.historically_valid_pubkeys(root / ".continuity" / "keys", pub) if pub else None
        ok, issues = automation_common.verify_chain(root, trusted_public=keys)
        if ok:
            console.print("[bold green][✔] Chain verified: linkage, hashes and signatures intact.[/bold green]")
        else:
            for issue in issues:
                console.print(f"[bold red][!][/bold red] {issue}")
            raise typer.Exit(code=1)


@app.command()
def prove(
    file: Path = typer.Option(..., "--file", help="File to prove inclusion for (relative to repo root)."),
    repo_root: Path = typer.Option(".", "--repo-root", help="Project root directory."),
    scan_source: bool = typer.Option(True, "--scan-source/--no-scan-source"),
    output: Path = typer.Option(None, "--output", help="Write the proof JSON here (default: stdout)."),
):
    """Emit a Merkle inclusion proof: verify ONE file belongs to the DNA root in
    O(log n) hashes, without rehashing the repository."""
    root = repo_root.resolve()
    _docs, _src, leaves = _compute_leaves(root, scan_source)
    rel = file.as_posix() if not file.is_absolute() else file.resolve().relative_to(root).as_posix()
    if rel not in leaves:
        console.print(f"[bold red][!] '{rel}' is not a scanned nucleotide (docs/source under the root).[/bold red]")
        raise typer.Exit(code=1)
    leaf = leaves[rel]
    proof = automation_common.merkle_inclusion_proof(list(leaves.values()), leaf)
    payload = {
        "file": rel,
        "leaf": leaf,
        "leaf_format": automation_common.LEAF_FORMAT,
        "merkle_root": automation_common.build_merkle_tree(list(leaves.values())),
        "proof": proof,
    }
    text = json.dumps(payload, indent=2)
    if output:
        output.write_text(text, encoding="utf-8")
        console.print(f"[bold green][✔][/bold green] Proof written: [italic]{output}[/italic] ({len(proof)} steps)")
    else:
        print(text)


@app.command()
def verify_proof(
    proof_file: Path = typer.Option(..., "--proof", help="Proof JSON produced by `prove`."),
    repo_root: Path = typer.Option(".", "--repo-root", help="Project root directory."),
    root_hash: str = typer.Option(None, "--root", help="Expected root (default: signed STATE baseline)."),
):
    """Verify a Merkle inclusion proof against the current file content and the
    signed baseline root. Detects both file tampering and forged proofs."""
    root = repo_root.resolve()
    payload = json.loads(proof_file.read_text(encoding="utf-8"))
    rel = payload["file"]
    target = root / rel
    # Recompute the leaf from the CURRENT file (not the stored leaf) so a
    # tampered file fails even with a valid proof for the old content.
    current_leaf = automation_common.path_bound_leaf(rel, automation_common.calculate_sha256(target))
    expected_root = root_hash
    if not expected_root:
        state_file = root / ".continuity" / "STATE.json"
        if state_file.exists():
            expected_root = json.loads(state_file.read_text(encoding="utf-8")).get("merkle_root", "")
    if not expected_root:
        console.print("[bold red][!] No root to verify against (no baseline; pass --root).[/bold red]")
        raise typer.Exit(code=1)
    ok = automation_common.verify_inclusion_proof(current_leaf, payload["proof"], expected_root)
    if ok:
        console.print(f"[bold green][✔] INCLUSION VERIFIED:[/bold green] '{rel}' belongs to root {expected_root[:16]}…")
    else:
        console.print(f"[bold red][✘] VERIFICATION FAILED:[/bold red] '{rel}' does not match root {expected_root[:16]}… (file tampered, proof forged, or baseline moved)")
        raise typer.Exit(code=1)


@app.command()
def verify(
    repo_root: Path = typer.Option(".", "--repo-root", help="Project root directory."),
    scan_source: bool = typer.Option(True, "--scan-source/--no-scan-source"),
    expect_fingerprint: str = typer.Option(None, "--expect-fingerprint", help="Pin the sovereign public-key fingerprint you obtained OUT OF BAND. Fails if the repo's key does not match."),
    strict: bool = typer.Option(False, "--strict", help="Skeptic mode: require BOTH a matched fingerprint and a confirmed Bitcoin anchor, else fail."),
    as_json: bool = typer.Option(False, "--json", help="Emit a machine-readable JSON report (for CI/automation) instead of the panel."),
):
    """Third-party verification — one read-only command a skeptic runs to answer
    'is this repo's DNA authentic?'. Recomputes the Merkle root and checks it
    against the signed baseline, verifies the Ed25519 signature and the whole
    transparency chain, pins the key fingerprint, and reports the Bitcoin anchor.
    Writes nothing."""
    root = repo_root.resolve()
    ok = True
    report: dict = {"checks": {}, "warnings": []}
    def say(msg):
        if not as_json:
            console.print(msg)

    _priv, pub = automation_common.load_sovereign_keys(root)
    fingerprint = sovereign_vault.key_fingerprint(pub) if pub else None
    report["fingerprint"] = fingerprint
    if fingerprint:
        say(f"Sovereign key fingerprint: [bold]{fingerprint}[/bold]")
    if expect_fingerprint:
        matched = fingerprint == expect_fingerprint.strip()
        report["checks"]["fingerprint_pin"] = matched
        say(f"  fingerprint pin: {'[green]MATCH[/green]' if matched else '[bold red]MISMATCH[/bold red]'}")
        ok = ok and matched

    # 1. Content vs signed baseline.
    _docs, _src, leaves = _compute_leaves(root, scan_source)
    computed_root = automation_common.build_merkle_tree(list(leaves.values()))
    state_path = root / ".continuity" / "STATE.json"
    if not state_path.exists():
        if as_json:
            print(json.dumps({"ok": False, "error": "no baseline (STATE.json)"}, indent=2))
        else:
            console.print("[bold red][✘] no baseline (STATE.json) — nothing to verify.[/bold red]")
        raise typer.Exit(code=1)
    state = json.loads(state_path.read_text(encoding="utf-8"))
    root_match = state.get("merkle_root") == computed_root
    report["checks"]["root_matches_baseline"] = root_match
    report["merkle_root"] = computed_root
    say(f"  merkle root vs baseline: {'[green]MATCH[/green]' if root_match else '[bold red]DRIFT[/bold red]'}")
    ok = ok and root_match

    # 2. Baseline signatures.
    checksum_ok = automation_common.verify_signature(state)
    trusted = sovereign_vault.historically_valid_pubkeys(root / ".continuity" / "keys", pub) if pub else None
    sov = automation_common.verify_sovereign_state(state, trusted_public=trusted)
    report["checks"]["baseline_checksum"] = checksum_ok
    report["checks"]["baseline_ed25519"] = ("ok" if sov else ("unsigned" if sov is None else "invalid"))
    say(f"  baseline checksum: {'[green]ok[/green]' if checksum_ok else '[bold red]TAMPERED[/bold red]'}"
        f" | ed25519: {'[green]ok[/green]' if sov else ('[dim]unsigned[/dim]' if sov is None else '[bold red]INVALID[/bold red]')}")
    ok = ok and checksum_ok and (sov is not False)

    # 3. Transparency chain — internal integrity AND binding to the baseline.
    chain_ok, chain_issues = automation_common.verify_chain(root, trusted_public=trusted)
    report["checks"]["chain_intact"] = chain_ok
    report["chain_issues"] = chain_issues
    say(f"  transparency chain: {'[green]intact[/green]' if chain_ok else '[bold red]BROKEN[/bold red]'}")
    for issue in chain_issues[:3]:
        say(f"      [red]{issue}[/red]")
    ok = ok and chain_ok
    # Red-team A4: a chain can be internally valid yet truncated. Bind the chain
    # HEAD to the current baseline — the newest entry must record this root.
    entries = automation_common.read_chain(root)
    report["chain_length"] = len(entries)
    if entries:
        head_bound = entries[-1].get("merkle_root") == state.get("merkle_root")
        report["checks"]["chain_head_bound"] = head_bound
        say(f"  chain head vs baseline: {'[green]bound[/green]' if head_bound else '[bold red]MISMATCH (chain truncated or state rolled forward)[/bold red]'}")
        ok = ok and head_bound

    # 4. External witness (informational unless --strict).
    anchor_confirmed = False
    anchors = sorted((root / ".continuity" / anchor_mod.ANCHOR_DIRNAME).glob("*.json.ots")) if (root / ".continuity" / anchor_mod.ANCHOR_DIRNAME).exists() else []
    if anchors:
        anchor_confirmed, msg = anchor_mod.try_ots_verify(anchors[-1])
        say(f"  bitcoin anchor: {'[green]confirmed[/green]' if anchor_confirmed else '[yellow]' + msg + '[/yellow]'}")
    else:
        say("  bitcoin anchor: [dim]none (run `anchor` for an external witness)[/dim]")
    report["anchor_confirmed"] = anchor_confirmed

    # Honesty about scope. Red-team A3a/A5: internal consistency is NOT
    # authenticity. Without a pinned fingerprint a key-swapped fork verifies;
    # without a confirmed anchor a rollback to an older signed state verifies.
    authenticity_checked = bool(expect_fingerprint)
    if not authenticity_checked:
        report["warnings"].append("authenticity_not_verified: no fingerprint pin; a key-swapped fork would pass")
        say("[yellow]  ! authenticity NOT verified: no --expect-fingerprint. This proves internal[/yellow]")
        say("[yellow]    integrity only; a fork that swapped the whole key set would still pass.[/yellow]")
    if not anchor_confirmed:
        report["warnings"].append("rollback_not_externally_detectable: no confirmed anchor")
        say("[yellow]  ! rollback NOT externally detectable: no confirmed Bitcoin anchor.[/yellow]")

    if strict and ok and not (authenticity_checked and anchor_confirmed):
        say("[bold red]  --strict requires a matched fingerprint AND a confirmed anchor.[/bold red]")
        ok = False

    report["ok"] = ok
    report["verdict"] = ("failed" if not ok else ("authentic" if authenticity_checked else "integrity-only"))
    if as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        verdict = {
            "failed": "[bold red]VERIFICATION FAILED[/bold red]",
            "authentic": "[bold green]DNA AUTHENTIC[/bold green]  (key fingerprint pinned)",
            "integrity-only": "[bold yellow]INTEGRITY OK[/bold yellow]  (authenticity unverified — pass --expect-fingerprint)",
        }[report["verdict"]]
        console.print(Panel(verdict, title="Third-Party Verify", expand=False))
    if not ok:
        raise typer.Exit(code=1)


@app.command()
def upgrade_anchors(
    repo_root: Path = typer.Option(".", "--repo-root", help="Project root directory."),
):
    """Complete any pending anchors: fetch Bitcoin attestations from the calendars
    for every .ots that is still awaiting confirmation. Safe to run on a schedule
    (nightly cron / CI) — it is a no-op once a proof is confirmed, so you never
    have to remember to come back hours after stamping."""
    root = repo_root.resolve()
    directory = root / ".continuity" / anchor_mod.ANCHOR_DIRNAME
    proofs = sorted(directory.glob("*.ots")) if directory.exists() else []
    if not proofs:
        console.print("[yellow]No anchor proofs found — run `anchor` first.[/yellow]")
        raise typer.Exit(code=0)

    confirmed = pending = 0
    for proof in proofs:
        was_confirmed, message = anchor_mod.verify_via_library(proof)
        if was_confirmed:
            confirmed += 1
            console.print(f"  [green][✔][/green] {proof.name}: {message}")
        else:
            pending += 1
            console.print(f"  [yellow][·][/yellow] {proof.name}: {message}")
    console.print(Panel(
        f"[bold]{confirmed} confirmed[/bold] · {pending} still pending "
        f"(of {len(proofs)} proof(s))\n"
        f"[dim]Commit any upgraded .ots files — the upgrade is what makes them independently verifiable.[/dim]",
        title="Anchor Upgrade", expand=False,
    ))


@app.command()
def anchor(
    repo_root: Path = typer.Option(".", "--repo-root", help="Project root directory."),
):
    """Anchor the DNA transparency chain head in Bitcoin via OpenTimestamps —
    an EXTERNAL witness. The signed chain proves lineage to anyone who trusts the
    key; the anchor proves it to a skeptic who trusts no one, and survives key
    compromise (a past timestamp cannot be forged). If the `ots` client is not
    installed, a local sovereign record is still written."""
    root = repo_root.resolve()
    entries = automation_common.read_chain(root)
    state_path = root / ".continuity" / "STATE.json"
    merkle_root = ""
    if state_path.exists():
        merkle_root = json.loads(state_path.read_text(encoding="utf-8")).get("merkle_root", "")
    if not entries and not merkle_root:
        console.print("[yellow]Nothing to anchor yet — run `check` to crystallize a baseline first.[/yellow]")
        raise typer.Exit(code=0)

    _priv, pub = automation_common.load_sovereign_keys(root)
    record = anchor_mod.build_anchor_record(entries[-1] if entries else None, merkle_root, pub.hex() if pub else None)
    anchor_path = anchor_mod.write_anchor(root, record)
    console.print(f"[bold green][✔][/bold green] Sovereign anchor record: [italic]{anchor_path}[/italic]")

    # Prefer the Python library (works where the ots CLI hits its Windows DLL
    # issue); fall back to the CLI; then to the local-record-only path.
    stamped, message = False, ""
    if anchor_mod.library_available():
        stamped, message = anchor_mod.stamp_with_library(anchor_path)
    if not stamped:
        cli_ok, cli_msg = anchor_mod.try_ots_stamp(anchor_path)
        if cli_ok:
            stamped, message = True, cli_msg
        elif not message:
            message = cli_msg
    if stamped:
        console.print(Panel(
            f"[bold green]Anchored to Bitcoin (OpenTimestamps).[/bold green]\n"
            f"Proof: [italic]{message}[/italic]\n"
            f"Confirmation takes hours. Verify later: [cyan]continuity-pro verify-anchor --proof {str(anchor_path) + '.ots'}[/cyan]\n"
            f"[dim]Commit the .ots proof so anyone can verify the timestamp independently.[/dim]",
            title="External Witness", expand=False,
        ))
    else:
        console.print(f"[yellow][i] Blockchain stamp pending: {message}[/yellow]")
        console.print("[dim]Frictionless stamp:  pip install continuity-pro[anchor]  (pure-Python, no ots CLI)")
        console.print("[dim]The local record is already sovereign-signed via the chain; the .ots adds the external witness.[/dim]")


@app.command()
def verify_anchor(
    proof: Path = typer.Option(..., "--proof", help="The .ots proof file produced by `anchor`."),
):
    """Verify a Bitcoin anchor proof. Prefers the opentimestamps library
    (upgrades from the calendars and reports confirmation — works where the `ots`
    CLI crashes on Windows); uses the CLI only if the library is unavailable."""
    if anchor_mod.library_available():
        ok, message = anchor_mod.verify_via_library(proof)
    else:
        ok, message = anchor_mod.try_ots_verify(proof)
    if ok:
        console.print(f"[bold green][✔] ANCHOR CONFIRMED on Bitcoin:[/bold green]\n{message}")
    else:
        console.print(f"[yellow][i] Not confirmed:[/yellow] {message}")
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
