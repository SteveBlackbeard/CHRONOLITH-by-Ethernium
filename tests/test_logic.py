import unittest
from pathlib import Path
import os
import sys

# Add tools to path for testing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../tools/continuity_legacy')))

from doc_parity_check import check_doc_parity
# from run_continuity_cycle import check_logical_immunity # (Need to refactor for easier import)

class TestContinuityLogic(unittest.TestCase):
    def setUp(self) -> None:
        self.test_root = Path("tmp_test_repo")
        self.test_root.mkdir(exist_ok=True)
        (self.test_root / ".continuity" / "registry").mkdir(parents=True, exist_ok=True)
        
    def tearDown(self) -> None:
        import shutil
        if self.test_root.exists():
            shutil.rmtree(self.test_root)

    def test_doc_parity_missing_file(self):
        # Create a mock map
        map_content = {
            "documents": [
                {"path": "MISSING.md", "required_strings": ["test"], "severity": "error"}
            ]
        }
        import json
        (self.test_root / ".continuity" / "registry" / "document_dependency_map.json").write_text(json.dumps(map_content))
        
        report = check_doc_parity(str(self.test_root))
        self.assertEqual(report["status"], "attention_required")
        self.assertIn("Missing parity-tracked document: MISSING.md", report["errors"])

    def test_doc_parity_marker_missing(self):
        (self.test_root / "EXISTING.md").write_text("Hello World")
        map_content = {
            "documents": [
                {"path": "EXISTING.md", "required_strings": ["MANDATORY"], "severity": "error"}
            ]
        }
        import json
        (self.test_root / ".continuity" / "registry" / "document_dependency_map.json").write_text(json.dumps(map_content))
        
        report = check_doc_parity(str(self.test_root))
        self.assertEqual(report["status"], "attention_required")
        self.assertTrue(any("missing 1 required markers" in e for e in report["errors"]))

if __name__ == "__main__":
    unittest.main()
