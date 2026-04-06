from __future__ import annotations

import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CONTINUITY_LEGACY_GRAPH")

class MemoryGraph:
    """
    Knowledge Graph wrapper for structural project memory.
    Uses NetworkX for relationship mapping.
    """
    def __init__(self):
        self.graph = None

    def _ensure_networkx(self):
        """Lazy import of networkx to maintain zero-deps core."""
        if self.graph is None:
            try:
                import networkx as nx
                self.nx = nx
                self.graph = nx.DiGraph()
            except ImportError:
                logger.error("[!] NetworkX not installed. Run 'pip install networkx' to use this extension.")
                raise ImportError("networkx is required for this extension.")

    def add_relationship(self, source: str, target: str, relation_type: str = "governs"):
        """Adds a directed edge between memory nodes."""
        self._ensure_networkx()
        self.graph.add_edge(source, target, relation=relation_type)
        logger.info(f"[✔] Relationship added: {source} --({relation_type})--> {target}")

    def get_audit_trail(self, start_node: str):
        """Returns the downstream nodes governed by a specific rule or context."""
        self._ensure_networkx()
        if start_node not in self.graph:
            return []
        return list(self.nx.descendants(self.graph, start_node))

    def save_graph_json(self, output_path: str = "outputs/continuity/memory_graph.json"):
        """Exports the graph to a JSON file for the visual dashboard."""
        self._ensure_networkx()
        from networkx.readwrite import json_graph
        data = json_graph.node_link_data(self.graph)
        
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        import json
        out.write_text(json.dumps(data, indent=2), encoding="utf-8")
        logger.info(f"[✔] Memory Graph exported to: {output_path}")


if __name__ == "__main__":
    # Example usage for auditing
    m_graph = MemoryGraph()
    try:
        # Map a Context Rule to a Decision
        m_graph.add_relationship("PROJECT_CONTEXT", "DECISION_001", "governs")
        m_graph.add_relationship("DECISION_001", "MILESTONE_A", "implements")
        print(f"Audit Trail for Context: {m_graph.get_audit_trail('PROJECT_CONTEXT')}")
        m_graph.save_graph_json()
    except ImportError:
        pass
