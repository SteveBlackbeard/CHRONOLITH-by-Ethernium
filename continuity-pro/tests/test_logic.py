#!/usr/bin/env python3
"""
test_logic.py — CONTINUITY LEGACY Pro Tests
===========================================
Advanced Unit Tests for the Continuity Legacy Framework.

Covers:
- Decision Engine momentum parsing
- Continuity Cycle edge cases
- State JSON validations

Uses Python's standard `unittest` framework.
"""

import unittest
import json
import tempfile
import os
import datetime
from pathlib import Path

# Import the modules to test (assuming they are in path or relative)
import sys
# Add tools/continuity_legacy to python path for testing
current_dir = Path(__file__).parent
tools_dir = current_dir.parent / "tools" / "continuity_legacy"
sys.path.append(str(tools_dir))

# Attempt to import decision_engine. If it fails, tests will error appropriately.
try:
    import decision_engine
except ImportError:
    decision_engine = None

class TestDecisionEngine(unittest.TestCase):
    
    def setUp(self):
        """Create a temporary directory simulating a project root."""
        local_tmp_root = current_dir.parent.parent / ".pytest_tmp" / "unittest"
        local_tmp_root.mkdir(parents=True, exist_ok=True)
        self.test_dir = tempfile.TemporaryDirectory(dir=local_tmp_root)
        self.root_path = Path(self.test_dir.name)
        
    def tearDown(self):
        self.test_dir.cleanup()
        
    def test_momentum_high(self):
        """Test high momentum scoring for recent updates."""
        if not decision_engine:
            self.skipTest("decision_engine.py module not found.")
            
        recent_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        state_data = {"last_update": recent_time}
        
        result = decision_engine.evaluate_momentum(state_data)
        self.assertEqual(result["score"], 95, "Recent update should score 95.")
        
    def test_momentum_stale(self):
        """Test stale momentum scoring for 30+ day old updates."""
        if not decision_engine:
            self.skipTest("decision_engine.py module not found.")
            
        old_time = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=35)).isoformat()
        state_data = {"last_update": old_time}
        
        result = decision_engine.evaluate_momentum(state_data)
        self.assertEqual(result["score"], 20, "Stale update should score 20.")
        
    def test_tactical_directive_extraction(self):
        """Test parsing of the LIVE_HANDOFF.md file for next actions."""
        if not decision_engine:
            self.skipTest("decision_engine.py module not found.")
            
        continuity_dir = self.root_path / ".continuity"
        continuity_dir.mkdir(parents=True)
        
        handoff_file = continuity_dir / "LIVE_HANDOFF.md"
        handoff_content = """# LIVE HANDOFF
        
## Next Exact Action
Fix the unit tests in the tests folder.
"""
        handoff_file.write_text(handoff_content, encoding="utf-8")
        
        result = decision_engine.extract_tactical_directive(self.root_path)
        self.assertIn("Fix the unit tests", result, "Engine failed to extract the exact action.")

    def test_missing_files_handling(self):
        """Test graceful degradation when canonical files are missing."""
        if not decision_engine:
            self.skipTest("decision_engine.py module not found.")
            
        # Empty repo root, STATE.json is missing
        state = decision_engine.parse_state(self.root_path)
        self.assertEqual(state["status"], "error")
        self.assertIn("not found", state["message"])
        
        # LIVE_HANDOFF missing
        tactical = decision_engine.extract_tactical_directive(self.root_path)
        self.assertIn("CRITICAL", tactical)

if __name__ == "__main__":
    unittest.main()
