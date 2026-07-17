#!/usr/bin/env python3
"""Cross-edition core parity.

Lite / Pro / Omega each vendor their own copy of the DNA core primitives
(`build_merkle_*`, `calculate_sha256`). Vendoring is a deliberate product
decision — every edition installs standalone from PyPI with no shared base
package — but silent drift between the copies is the real risk (a fix landing in
one edition and not another). This test governs that: it runs each edition in an
ISOLATED subprocess (the editions share module names, so importing them in one
process collides in sys.modules) and asserts the shared primitives are
behaviourally identical. If an edition's core changes, this fails until the
change is reconciled or the parity expectation is updated on purpose.
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

EDITIONS = {
    "lite": REPO / "continuity-lite" / "continuity_lite" / "continuity_legacy",
    "pro": REPO / "continuity-pro" / "continuity_pro" / "continuity_legacy",
    "omega": REPO / "continuity-omega" / "continuity_omega" / "continuity_legacy",
}

# Runs inside each edition's own interpreter path. Resolves the Merkle builder
# (Lite exposes it in run_continuity_lite, Pro/Omega in automation_common) and
# emits its outputs for a fixed input vector.
#
# NOTE: `calculate_sha256` is deliberately NOT compared. It diverges by design —
# Lite filters the volatile DNA-badge lines out of markdown before hashing so
# self-crystallizing the badge doesn't trip drift, while Pro/Omega hash raw
# bytes. The shared, must-not-drift primitive is the Merkle algorithm itself,
# which operates on a list of leaf hashes and is identical across editions.
PROBE = r"""
import sys, json
sys.path.insert(0, sys.argv[1])
try:
    import automation_common as m
    fn = getattr(m, "build_merkle_tree", None) or getattr(m, "build_merkle_root", None)
except Exception:
    import run_continuity_lite as m
    fn = m.build_merkle_root
out = {
    "merkle_empty": fn([]),
    "merkle_odd": fn(["a", "b", "c"]),
    "merkle_even": fn(["z", "a", "m", "q"]),
    "merkle_order_independent": fn(["x", "y", "z"]) == fn(["z", "y", "x"]),
}
print(json.dumps(out))
"""


def _probe(edition_dir: Path) -> dict:
    result = subprocess.run(
        [sys.executable, "-c", PROBE, str(edition_dir)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"probe failed for {edition_dir}:\n{result.stderr}")
    return json.loads(result.stdout.strip().splitlines()[-1])


class TestEditionParity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = {name: _probe(path) for name, path in EDITIONS.items() if path.exists()}

    def test_all_three_editions_present(self):
        self.assertEqual(set(self.results), {"lite", "pro", "omega"},
                         f"missing editions: {set(EDITIONS) - set(self.results)}")

    def test_merkle_primitive_is_identical(self):
        for key in ("merkle_empty", "merkle_odd", "merkle_even"):
            values = {name: res[key] for name, res in self.results.items()}
            self.assertEqual(len(set(values.values())), 1,
                             f"Merkle core drifted across editions on {key}: {values}")

    def test_merkle_is_order_independent_everywhere(self):
        for name, res in self.results.items():
            self.assertTrue(res["merkle_order_independent"], f"{name} lost order-independence")


if __name__ == "__main__":
    unittest.main()
