import sys
import argparse
import os
from pathlib import Path

# CONTINUITY LEGACY OMEGA - Main Entry Point
# ----------------------------------------
# This utility provides access to the deep cognitive features (RAG and Graphs).

def parse_args():
    parser = argparse.ArgumentParser(description="CONTINUITY LEGACY Omega - Advanced AI Interface")
    parser.add_argument("--index", action="store_true", help="Index the current workspace into the vector store.")
    parser.add_argument("--query", type=str, help="Search the project history semantically (RAG).")
    parser.add_argument("--map", action="store_true", help="Generate the cognitive lineage graph.")
    parser.add_argument("--repo-root", type=str, default=".", help="Root directory of the repository.")
    return parser.parse_args()

def main():
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    
    # Check dependencies and data folders
    output_dir = repo_root / "outputs" / "continuity"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    import omega_engine
    import cognitive_map
    
    if args.index:
        store = omega_engine.initialize_omega_store(repo_root)
        omega_engine.index_workspace(repo_root, store)
        
    if args.query:
        store = omega_engine.initialize_omega_store(repo_root)
        results = omega_engine.query_continuity(store, args.query)
        print(f"\n[*] OMEGA Results for: '{args.query}'")
        for i, doc in enumerate(results['documents'][0]):
            path = results['metadatas'][0][i]['filename']
            print(f"--- Result {i+1} ({path}) ---")
            print(doc[:300] + "...")
            
    if args.map:
        log = repo_root / ".continuity" / "DECISIONS_LOG.md"
        nodes = cognitive_map.extract_decisions(str(log))
        graph = cognitive_map.generate_cognitive_map(nodes)
        cognitive_map.export_map(graph, str(output_dir / "cognitive_map.json"))

    if not any([args.index, args.query, args.map]):
        print("[!] OMEGA: No action specified. Use --index, --query, or --map.")

if __name__ == "__main__":
    main()
