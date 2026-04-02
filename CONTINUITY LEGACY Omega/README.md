# CONTINUITY LEGACY: Omega Edition 🏛️🧬💎

The **Omega Edition** is the pinnacle of the Continuity Legacy framework. It is designed for high-stake, large-scale projects where "just reading the logs" is no longer enough.

## Advanced Cognitive Features

### 1. Semantic RAG (Retrieval-Augmented Generation)
Using **ChromaDB**, Omega indexes every markdown file in your workspace into a persistent vector store. This allows you to perform semantic queries across the project's entire history.
- **Command**: `python tools/continuity_legacy/run_continuity_omega.py --index`
- **Query**: `python tools/continuity_legacy/run_continuity_omega.py --query "What were the main architectural decisions in Phase 4?"`

### 2. Cognitive Lineage Graphs
Omega uses **NetworkX** to parse your `DECISIONS_LOG.md` and visualize how every tactical decision branches from the project's original intent.
- **Command**: `python tools/continuity_legacy/run_continuity_omega.py --map`
- **Output**: Generates a `cognitive_map.json` in the `outputs/continuity/` folder for visualization in modern graph tools.

## Installation & Requirements

The Omega Edition is performance-heavy and requires the following AI/ML dependencies:
- `chromadb` (Vector Store)
- `networkx` (Graph Logic)
- `sentence-transformers` (Local Embeddings)

```bash
# Install Omega Dependencies
pip install -e "CONTINUITY LEGACY Omega"
```

## When to use Omega?
- When you have **hundreds of files** and cannot remember where a specific decision was documented.
- When you need to provide a **semantic context injection** to a new AI agent.
- When the **logical complexity** of the project requires graph-based visualization to maintain continuity.

---
*CONTINUITY LEGACY: Professional. Autonomic. Omega.*
