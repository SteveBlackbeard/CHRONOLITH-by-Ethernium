import pytest
import json
from pathlib import Path
import sys
import hashlib

# CHRONOLITH: Omega Logic Tests (v2.1.0)
# -----------------------------------------------
# Expert #4 (QA): First test suite for Omega edition. Tests cognitive map
# generation and decision extraction without requiring chromadb.

sys.path.insert(0, str(Path(__file__).parent.parent / 'chronolith_omega' / 'chronolith'))

from cognitive_map import extract_decisions, generate_cognitive_map


# --- Decision Extraction Tests ---

def test_extract_decisions_empty(tmp_path):
    """Empty file yields no decisions."""
    log = tmp_path / "empty.md"
    log.write_text("# Decisions Log\n\nNo decisions yet.", encoding="utf-8")
    assert extract_decisions(str(log)) == []

def test_extract_decisions_from_table(tmp_path):
    """Correctly parses markdown table format."""
    log = tmp_path / "decisions.md"
    log.write_text(
        "# Decisions\n\n"
        "| Date | Decision | Reason |\n"
        "| 2026-04-01 | Use Merkle Trees | Cryptographic integrity |\n"
        "| 2026-04-02 | Add Typer CLI | Professional UI |\n",
        encoding="utf-8"
    )
    decisions = extract_decisions(str(log))
    assert len(decisions) == 2
    assert decisions[0]["name"] == "Use Merkle Trees"
    assert decisions[1]["reason"] == "Professional UI"


def test_separator_row_is_not_a_decision(tmp_path):
    """A real markdown table has a `| :--- |` separator. The parser must skip it.

    Regression: the date group was `[\\d\\-\\:]+`, which matches ":---", so the
    separator row became a decision node labelled ":---". On a freshly
    initialised project — where the log holds nothing but a header and that
    separator — the generated map consisted of that one junk node.

    It survived because the fixture above writes a table with no separator
    row, which is not a table anyone actually writes.
    """
    log = tmp_path / "decisions.md"
    log.write_text(
        "# Decision Log\n\n"
        "| Date | Decision | Rationale | Actor |\n"
        "| :--- | :--- | :--- | :--- |\n"
        "| 2026-04-05 | Adopt Ed25519 | Small fast signatures | steve |\n",
        encoding="utf-8"
    )
    decisions = extract_decisions(str(log))
    assert len(decisions) == 1
    assert decisions[0]["name"] == "Adopt Ed25519"
    assert all(":---" not in d["date"] for d in decisions)


def test_empty_log_with_separator_yields_no_decisions(tmp_path):
    """What `init` actually writes: header plus separator, and nothing else."""
    log = tmp_path / "decisions.md"
    log.write_text(
        "# Decision Log\n\n"
        "| Date | Decision | Rationale | Actor |\n"
        "| :--- | :--- | :--- | :--- |\n",
        encoding="utf-8"
    )
    assert extract_decisions(str(log)) == []


def test_extract_decisions_missing_file():
    """Missing file returns empty list, not an exception."""
    result = extract_decisions("/nonexistent/phantom_log.md")
    assert result == []


# --- Cognitive Map Generation Tests ---

def test_generate_map_empty():
    """Empty decision list produces empty graph."""
    G = generate_cognitive_map([])
    assert len(G.nodes) == 0
    assert len(G.edges) == 0

def test_generate_map_single():
    """Single decision creates one node, no edges."""
    decisions = [{"date": "2026-01-01", "name": "Init", "reason": "Bootstrap"}]
    G = generate_cognitive_map(decisions)
    assert len(G.nodes) == 1
    assert len(G.edges) == 0

def test_generate_map_chain():
    """Multiple decisions form a linear chain."""
    decisions = [
        {"date": "2026-01-01", "name": "Alpha", "reason": "Start"},
        {"date": "2026-01-02", "name": "Beta", "reason": "Evolve"},
        {"date": "2026-01-03", "name": "Gamma", "reason": "Crystallize"},
    ]
    G = generate_cognitive_map(decisions)
    assert len(G.nodes) == 3
    assert len(G.edges) == 2
    # Verify chain: DEC_0 -> DEC_1 -> DEC_2
    assert G.has_edge("DEC_0", "DEC_1")
    assert G.has_edge("DEC_1", "DEC_2")
    assert not G.has_edge("DEC_0", "DEC_2")

def test_generate_map_preserves_metadata():
    """Node attributes are correctly stored."""
    decisions = [{"date": "2026-04-05", "name": "Industrialize", "reason": "Expert evaluation"}]
    G = generate_cognitive_map(decisions)
    node_data = G.nodes["DEC_0"]
    assert node_data["label"] == "Industrialize"
    assert node_data["date"] == "2026-04-05"
    assert node_data["reason"] == "Expert evaluation"
