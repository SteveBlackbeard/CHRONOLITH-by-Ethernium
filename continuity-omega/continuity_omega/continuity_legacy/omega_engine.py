import sys
import os
from pathlib import Path
from datetime import datetime

# Core Omega Engine (v1.3.0) - Enterprise Insight & Project DNA
# -------------------------------------------------------------

def _get_client(repo_root):
    import chromadb
    persist_path = Path(repo_root) / ".continuity" / "omega_index"
    return chromadb.PersistentClient(path=str(persist_path))

def initialize_omega_store(repo_root, external_roots=None):
    from chromadb.utils import embedding_functions
    client = _get_client(repo_root)
    emb_fn = embedding_functions.DefaultEmbeddingFunction()
    
    collection = client.get_or_create_collection(
        name="project_continuity",
        embedding_function=emb_fn,
        metadata={"hnsw:space": "cosine"}
    )
    
    if external_roots:
        for ext_path in external_roots:
            ext_path = Path(ext_path).resolve()
            if (ext_path / ".continuity" / "omega_index").exists():
                print(f"[*] OMEGA: Shared memory entanglement with {ext_path.name}...")
                index_workspace(ext_path, collection, label=f"External: {ext_path.name}")
                
    return collection

def index_workspace(repo_root, collection, label="Local"):
    print(f"[*] OMEGA: Processing workspace metabolism for {label} at {repo_root}...")
    md_files = list(Path(repo_root).rglob("*.md"))
    
    for md in md_files:
        if ".git" in str(md) or "outputs" in str(md): continue
        with open(md, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if not content.strip(): continue
            
        collection.upsert(
            documents=[content],
            metadatas=[{"path": str(md), "filename": md.name, "source": label, "type": "DNA_NUCLEOTIDE"}],
            ids=[f"{label}_{md}"]
        )
    print(f"[✔] OMEGA: Workspace indexed ({len(md_files)} nucleotides).")
    
    # Generate Project DNA automatically after local index
    if label == "Local":
        generate_project_dna(repo_root, collection)

def check_impact_analysis(collection, new_intent):
    """
    Contrastive Pattern Recognition: Finds the design principles that MOST 
    strongly conflict with the current session intent.
    """
    print(f"[*] OMEGA: Performing contrastive impact analysis...")
    
    # Search for constraints and rules
    results = collection.query(
        query_texts=[new_intent],
        n_results=10
    )
    
    conflicts = []
    # Heuristic: Detect 'forbidden' patterns in similar documents
    forbidden_patterns = ["NEVER", "FORBIDDEN", "MUST NOT", "ALWAYS", "RULE", "CONSTRAINT"]
    
    for i, doc in enumerate(results['documents'][0]):
        doc_upper = doc.upper()
        if any(p in doc_upper for p in forbidden_patterns):
            # If a rule is found, we extract the relevant sentence
            for sentence in doc.split('.'):
                if any(p in sentence.upper() for p in forbidden_patterns):
                    conflicts.append({
                        "file": results['metadatas'][0][i]['filename'],
                        "rule": sentence.strip()
                    })
    return conflicts

def generate_project_dna(repo_root, collection):
    """v2.1.0 Evolution: Synthesizes a cryptographically verifiable Merkle DNA Manifest."""
    print("[*] OMEGA: Synthesizing Merkle DNA Tree (Enterprise Standard)...")
    
    # 1. Cryptographic Layer: Merkle Tree of all project Markdown files
    # This maintains strict parity with Lite and Pro editions.
    try:
        from core.automation_common import build_merkle_tree, calculate_sha256
        md_files = sorted(list(Path(repo_root).rglob("*.md")))
        nucleotides = []
        md_hashes = {}
        for md in md_files:
            if ".git" in str(md) or "PROJECT_DNA.md" in md.name or "outputs" in str(md):
                continue
            h = calculate_sha256(md)
            nucleotides.append(h)
            md_hashes[md.name] = h
        merkle_root = build_merkle_tree(nucleotides)
    except ImportError:
        merkle_root = "ImportError: core.automation_common missing"
        md_hashes = {}

    # 2. Semantic Layer: Query for core architectural documents
    results = collection.query(
        query_texts=["Architecture, Mission, Core Principles, Tech Stack"],
        n_results=5
    )
    
    dna_path = Path(repo_root) / ".continuity" / "PROJECT_DNA.md"
    dna_content = [
        f"# Project DNA Manifest (Omega Evolution) 🧬🏛️\n",
        f"*Synthesized on: {datetime.now().isoformat()}*\n",
        f"*Algorithm: SHA-256 Merkle Tree + Semantic RAG*\n\n",
        f"> **MERKLE ROOT (Structural Integrity)**: `{merkle_root}`\n\n",
        "## 🧬 Foundational Nucleotides (Semantic Essence)\n"
    ]
    
    for i, doc in enumerate(results['documents'][0]):
        filename = results['metadatas'][0][i]['filename']
        summary = doc[:200].replace('\n', ' ') + "..."
        integrity = md_hashes.get(filename, "Not hashed")[:16] + "..."
        dna_content.append(f"- **[{filename}]**: {summary} (Integrity: `{integrity}`)\n")
    
    dna_content.append("\n---\n*This manifest represents the cognitive and cryptographic fusion of the project's logic.*")
    
    with open(dna_path, 'w', encoding='utf-8') as f:
        f.write("".join(dna_content))
    print(f"[✔] OMEGA: Merkle Root generated: {merkle_root[:16]}...")
    print(f"[✔] OMEGA: Project DNA synthesized at {dna_path}")

def query_continuity(collection, query_text):
    return collection.query(query_texts=[query_text], n_results=5)
