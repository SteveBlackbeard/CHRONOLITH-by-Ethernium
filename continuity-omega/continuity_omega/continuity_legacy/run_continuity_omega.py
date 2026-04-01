import sys
import argparse
import os
from pathlib import Path
from datetime import datetime

# CONTINUITY LEGACY OMEGA (v1.3.0) - The Cognitive Oracle (Enterprise)
# ------------------------------------------------------------------
# Advanced AI Interface with Semantic RAG, Cognitive Graphs, and Impact Analysis.
# [!] v1.3: Superior Metabolism, DNA Synthesis, and Proactive Alerts.

def install_hooks(repo_root: Path):
    hook_path = repo_root / ".git" / "hooks" / "pre-push"
    if not (repo_root / ".git").exists():
        print("[!] ERROR: Not a git repository. Cannot install hooks.")
        return
    
    hook_content = f"#!/bin/sh\n# Continuity Omega Auto-Hook\npython {Path(__file__).resolve()} --index || exit 1\n"
    hook_path.parent.mkdir(parents=True, exist_ok=True)
    hook_path.write_text(hook_content, encoding="utf-8")
    
    if os.name != "nt": os.chmod(hook_path, 0o755)
    print(f"[✔] Push Hook (with auto-indexing) installed at {hook_path}")

def log_session(repo_root: Path, collection=None):
    log_path = repo_root / "SESSION_LOG.md"
    print("\n[*] [OPTIONAL] Session intent capture")
    intent = input("    -> What did you achieve in this session? (Enter to skip): ").strip()
    
    if intent:
        # PROACTIVE IMPACT ANALYSIS (v1.3)
        if collection:
            import omega_engine
            conflicts = omega_engine.check_impact_analysis(collection, intent)
            if conflicts:
                print("\n[!] OMEGA IMPACT ALERT: This intent may contradict historical design:")
                for c in conflicts:
                    print(f"    - [{c['file']}]: \"{c['rule']}\"")
                
                print("\n[?] CONTEXTUAL CHOICE (Psychology-based Resolution):")
                print("    1. [RECONCILE] I understand. I will adjust the intent to follow rules.")
                print("    2. [OVERRIDE] This is a conscious evolution. Log it as a design pivot.")
                print("    3. [CANCEL] Stop action.")
                choice = input("    -> Select [1/2/3]: ").strip()
                
                if choice == "2":
                    intent = f"[PIVOT] {intent}"
                elif choice != "1":
                    print("[!] Action aborted by Operator.")
                    return

        if not log_path.exists():
            log_path.write_text("# Continuity Session Log\n\n", encoding="utf-8")
        
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"- [{datetime.utcnow().isoformat()}Z] {intent}\n")
        print("    [✔] Intent logged.")

def parse_args():
    parser = argparse.ArgumentParser(description="CONTINUITY LEGACY Omega - Advanced AI Interface")
    parser.add_argument("--index", action="store_true", help="Index the current workspace.")
    parser.add_argument("--query", type=str, help="Search project history semantically.")
    parser.add_argument("--map", action="store_true", help="Generate interactive cognitive maps.")
    parser.add_argument("--hook", action="store_true", help="Install Git pre-push hook.")
    parser.add_argument("--connect", type=str, nargs="+", help="Connect shared memory repositories.")
    parser.add_argument("--repo-root", type=str, default=".", help="Root directory.")
    return parser.parse_args()

def main():
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    
    if args.hook:
        install_hooks(repo_root)
        return

    # LAZY LOADING (Metabolism Optimization)
    import omega_engine
    import cognitive_map
    
    # Self-Healing Environment
    files = {
        ".continuity/STATE.json": '{"phase": "omega", "last_update": "' + datetime.utcnow().isoformat() + '"}',
        "PROJECT_CONTEXT.md": "# Project Context\n\n- Define your strategic intent here.",
        ".continuity/DECISIONS_LOG.md": "# Decision Log\n\n| Date | Decision | Rationale | Actor |\n| :--- | :--- | :--- | :--- |\n"
    }
    for filename, template in files.items():
        if not (repo_root / filename).exists():
            print(f"[?] Missing Nucleotide: {filename}")
            # Non-interactive template auto-creation for quick starts
            (repo_root / filename).parent.mkdir(parents=True, exist_ok=True)
            (repo_root / filename).write_text(template, encoding="utf-8")
            print(f"    [✔] Re-synthesized core file: {filename}")

    output_dir = repo_root / "outputs" / "continuity"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    store = omega_engine.initialize_omega_store(repo_root, external_roots=args.connect)
    action_taken = False

    if args.index:
        omega_engine.index_workspace(repo_root, store)
        action_taken = True
        
    if args.query:
        results = omega_engine.query_continuity(store, args.query)
        print(f"\n[*] OMEGA Results for: '{args.query}'")
        for i, doc in enumerate(results['documents'][0]):
            filename = results['metadatas'][0][i]['filename']
            print(f"--- Result {i+1} ({filename}) ---")
            print(doc[:300] + "...")
        action_taken = True
            
    if args.map:
        log = repo_root / ".continuity" / "DECISIONS_LOG.md"
        nodes = cognitive_map.extract_decisions(str(log))
        graph = cognitive_map.generate_cognitive_map(nodes)
        cognitive_map.export_map(graph, str(output_dir / "cognitive_map.json"))
        action_taken = True

    if action_taken:
        log_session(repo_root, collection=store)

    if not action_taken:
        print("[!] OMEGA: No action specified. Use --index, --query, or --map.")

if __name__ == "__main__":
    main()
