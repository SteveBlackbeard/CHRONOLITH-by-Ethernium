import unittest
import os
import sys
from pathlib import Path

# Add the tools directory to the path so we can import the core logic
repo_root = Path(__file__).resolve().parents[1]
sys.path.append(str(repo_root / "tools" / "continuity_legacy"))

from core.automation_common import resolve_repo_root, utc_now_iso

class TestAutomationCommon(unittest.TestCase):
    def test_utc_now_iso_format(self):
        now = utc_now_iso()
        self.assertIsInstance(now, str)
        self.assertIn("T", now)
        self.assertTrue(now.endswith("+00:00") or now.endswith("Z"))

    def test_resolve_repo_root_valid(self):
        # Resolve the current repo root
        resolved = resolve_repo_root(repo_root, __file__)
        self.assertEqual(resolved.resolve(), repo_root.resolve())

    def test_resolve_repo_root_security_warning(self):
        # Try to resolve a non-repo directory (like the parent of Experimentos)
        parent_dir = repo_root.parents[1]
        with self.assertRaises(ValueError) as cm:
            resolve_repo_root(parent_dir, __file__)
        self.assertIn("Security Warning", str(cm.exception))

if __name__ == '__main__':
    unittest.main()
