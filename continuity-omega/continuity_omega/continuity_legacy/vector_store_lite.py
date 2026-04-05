from __future__ import annotations

import logging
from pathlib import Path

# Configure logging for professional audits
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CONTINUITY_LEGACY_VECTOR")

class ContinuityVectorStore:
    """
    A professional wrapper for vector-based memory stores.
    Targets ChromaDB for simplicity and local execution.
    """
    def __init__(self, db_path: str = ".continuity/vector_db"):
        self.db_path = db_path
        self._client = None
        self._collection = None

    def _ensure_chroma(self):
        """Lazy import of chromadb to maintain zero-deps core."""
        if self._client is None:
            try:
                import chromadb
                from chromadb.config import Settings
                self._client = chromadb.PersistentClient(path=self.db_path)
                self._collection = self._client.get_or_create_collection(name="continuity_memory")
            except ImportError:
                logger.error("[!] ChromaDB not installed. Run 'pip install chromadb' to use this extension.")
                raise ImportError("chromadb is required for this extension.")

    def index_document(self, path: Path):
        """Indexes a canonical document into the vector store."""
        self._ensure_chroma()
        if not path.exists():
            return
        
        content = path.read_text(encoding="utf-8")
        doc_id = str(path.relative_to(Path.cwd())).replace("\\", "/")
        
        # Simple upsert logic
        self._collection.upsert(
            documents=[content],
            metadatas=[{"path": doc_id}],
            ids=[doc_id]
        )
        logger.info(f"[✔] Indexed: {doc_id}")

    def query_memory(self, prompt: str, n_results: int = 3):
        """Performs a semantic search over the project's memory."""
        self._ensure_chroma()
        results = self._collection.query(
            query_texts=[prompt],
            n_results=n_results
        )
        return results


if __name__ == "__main__":
    # Example usage for auditing
    store = ContinuityVectorStore()
    try:
        # Index root project context as a test
        store.index_document(Path("PROJECT_CONTEXT.md"))
        print("\n[*] Memory indexed. Querying for 'Continuity Principles'...")
        res = store.query_memory("What are the main principles?")
        print(f"Results: {res['documents']}")
    except ImportError:
        pass
