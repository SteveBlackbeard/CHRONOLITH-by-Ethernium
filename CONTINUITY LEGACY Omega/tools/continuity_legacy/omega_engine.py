import sys
import os
from pathlib import Path

# Core Omega Engine - Deep RAG & Semantic Insights
# -----------------------------------------------
# This module integrates ChromaDB for vector-based continuity search.

try:
    import chromadb
    from chromadb.utils import embedding_functions
except ImportError:
    print("[!] OMEGA ALERT: Dependencies missing (chromadb). Run: pip install chromadb")
    sys.exit(1)

def initialize_omega_store(repo_root):
    # Persistent store in .continuity/omega_index/
    persist_path = Path(repo_root) / ".continuity" / "omega_index"
    client = chromadb.PersistentClient(path=str(persist_path))
    
    # Default embedding (Sentence Transformers)
    emb_fn = embedding_functions.DefaultEmbeddingFunction()
    
    collection = client.get_or_create_collection(
        name="project_continuity",
        embedding_function=emb_fn,
        metadata={"hnsw:space": "cosine"}
    )
    return collection

def index_workspace(repo_root, collection):
    print(f"[*] OMEGA: Indexing workspace at {repo_root}...")
    # Index all markdown files for semantic RAG
    md_files = list(Path(repo_root).rglob("*.md"))
    
    for md in md_files:
        if ".git" in str(md): continue
        with open(md, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if not content.strip(): continue
            
        collection.upsert(
            documents=[content],
            metadatas=[{"path": str(md), "filename": md.name}],
            ids=[str(md)]
        )
    print(f"[✔] OMEGA: Workspace indexed ({len(md_files)} files).")

def query_continuity(collection, query_text):
    results = collection.query(
        query_texts=[query_text],
        n_results=3
    )
    return results

if __name__ == "__main__":
    # Test Run
    root = Path('.').resolve()
    store = initialize_omega_store(root)
    index_workspace(root, store)
    
    # Example semantic query
    test_query = "What is the mission of this project?"
    print(f"\n[*] OMEGA QUERY: '{test_query}'")
    hits = query_continuity(store, test_query)
    for i, doc in enumerate(hits['documents'][0]):
        print(f"--- MATCH {i+1} ({hits['metadatas'][0][i]['filename']}) ---")
        print(doc[:200] + "...")
