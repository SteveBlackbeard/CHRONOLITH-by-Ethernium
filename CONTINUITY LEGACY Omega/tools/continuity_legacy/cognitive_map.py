import sys
import os
from pathlib import Path
import re

# Cognitive MAP - CONTINUITY LEGACY Omega
# -------------------------------------
# This module uses NetworkX to visualize the lineage of decisions.

try:
    import networkx as nx
except ImportError:
    print("[!] OMEGA ALERT: Dependencies missing (networkx). Run: pip install networkx")
    sys.exit(1)

def extract_decisions(log_path):
    """Parses DECISIONS_LOG.md for decision nodes and their dates."""
    decisions = []
    if not os.path.exists(log_path): return decisions
    
    with open(log_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # Pattern: | Date | Decision | Reason | Actor |
    pattern = re.compile(r'\| ([\d\-\:]+) \| (.+?) \| (.+?) \|')
    
    for line in lines:
        match = pattern.search(line)
        if match:
            decisions.append({
                "date": match.group(1).strip(),
                "name": match.group(2).strip(),
                "reason": match.group(3).strip()
            })
    return decisions

def generate_cognitive_map(decisions):
    """Creates a Directed Acyclic Graph (DAG) of the project's logic."""
    G = nx.DiGraph()
    
    if not decisions:
        print("[!] OMEGA: No decisions found to map.")
        return G
        
    for i, dec in enumerate(decisions):
        node_id = f"DEC_{i}"
        G.add_node(node_id, label=dec["name"], date=dec["date"])
        
        # Link to previous decision (linear lineage as default)
        if i > 0:
            G.add_edge(f"DEC_{i-1}", node_id)
            
    return G

def export_map(G, output_path):
    """Exports the cognitive state as a JSON graph for visualization."""
    import json
    from networkx.readwrite import json_graph
    
    data = json_graph.node_link_data(G)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"[✔] OMEGA: Cognitive map exported to {output_path}.")

if __name__ == "__main__":
    # Test Run
    root = Path('.').resolve()
    log = root / ".continuity" / "DECISIONS_LOG.md"
    
    nodes = extract_decisions(str(log))
    graph = generate_cognitive_map(nodes)
    export_map(graph, str(root / "outputs" / "continuity" / "cognitive_map.json"))
