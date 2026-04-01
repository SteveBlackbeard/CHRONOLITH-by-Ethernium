import sys
import os
import json
from pathlib import Path
import re

# Cognitive MAP - CONTINUITY LEGACY Omega (v1.2.0)
# -----------------------------------------------
# Advanced visualization using NetworkX and Vis-Network.js.

try:
    import networkx as nx
except ImportError:
    print("[!] OMEGA ALERT: Dependencies missing (networkx). Run: pip install networkx")
    sys.exit(1)

def extract_decisions(log_path):
    decisions = []
    if not os.path.exists(log_path): return decisions
    with open(log_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Simple regex for Markdown table extraction
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
    G = nx.DiGraph()
    if not decisions: return G
    
    for i, dec in enumerate(decisions):
        node_id = f"DEC_{i}"
        G.add_node(node_id, label=dec["name"], date=dec["date"], reason=dec["reason"])
        if i > 0:
            G.add_edge(f"DEC_{i-1}", node_id)
    return G

def export_interactive_map(G, output_path):
    """Generates a standalone HTML file with an interactive Vis-Network visualization."""
    nodes = []
    edges = []
    
    for node, data in G.nodes(data=True):
        nodes.append({
            "id": node,
            "label": data.get("label", node),
            "title": f"Date: {data.get('date')}\nReason: {data.get('reason')}",
            "color": "#4fc3f7" if "DEC_0" in node else "#1976d2",
            "font": {"color": "white"}
        })
        
    for u, v in G.edges():
        edges.append({"from": u, "to": v, "arrows": "to", "color": "#90caf9"})
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Continuity: Cognitive Lineage Graph</title>
        <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
        <style type="text/css">
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0d1117; color: white; margin: 0; }}
            #mynetwork {{ width: 100%; height: 90vh; border: 1px solid #30363d; }}
            .header {{ padding: 15px; background: #161b22; border-bottom: 1px solid #30363d; }}
            h1 {{ margin: 0; font-size: 1.5rem; color: #58a6ff; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Continuity Omega: Cognitive Lineage Graph 🧠🔭</h1>
            <p>Visualizing the historical decision tree and logical evolution of your project.</p>
        </div>
        <div id="mynetwork"></div>
        <script type="text/javascript">
            const nodes = new vis.DataSet({json.dumps(nodes)});
            const edges = new vis.DataSet({json.dumps(edges)});
            const container = document.getElementById('mynetwork');
            const data = {{ nodes: nodes, edges: edges }};
            const options = {{
                layout: {{ hierarchical: {{ direction: 'UD', sortMethod: 'directed' }} }},
                interaction: {{ hover: true, tooltipDelay: 200 }},
                physics: {{ enabled: false }}
            }};
            const network = new vis.Network(container, data, options);
        </script>
    </body>
    </html>
    """
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    print(f"[✔] OMEGA: Interactive MAP generated at {output_path}")

def export_map(G, output_path):
    """Standard JSON export (legacy)"""
    from networkx.readwrite import json_graph
    data = json_graph.node_link_data(G)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    # Trigger Interactive Export as well
    html_path = output_path.replace(".json", ".html")
    export_interactive_map(G, html_path)
