import unittest
import os
import sys
import json
from pathlib import Path

# Add the tools directory to the path so we can import the core logic
repo_root = Path(__file__).resolve().parents[1]
sys.path.append(str(repo_root / "tools" / "continuity_legacy"))

from core.context_loader import build_context_snapshot

class TestContextLoader(unittest.TestCase):
    def test_build_context_snapshot_structure(self):
        # We assume the current repo is a valid CONTINUITY LEGACY repo
        snapshot = build_context_snapshot(repo_root)
        
        self.assertIsInstance(snapshot, dict)
        self.assertIn("generated_at", snapshot)
        self.assertIn("repo_root", snapshot)
        self.assertEqual(snapshot["repo_root"], ".") # Should be relativized
        self.assertIn("documents", snapshot)
        
        # Check for mandatory documents in snapshot
        docs = snapshot["documents"]
        self.assertIn("context", docs)
        self.assertIn("state", docs)
        self.assertIn("roadmap", docs)
        
    def test_path_relativization_in_snapshot(self):
        snapshot = build_context_snapshot(repo_root)
        
        # Verify that all document paths are relative (no D:\Experimentos\...)
        for key, entry in snapshot["documents"].items():
            path_str = entry["path"]
            self.assertFalse(path_str.startswith("D:"), f"Path {path_str} for {key} is absolute!")
            self.assertFalse(path_str.startswith("/"), f"Path {path_str} for {key} is absolute!")

if __name__ == '__main__':
    unittest.main()
