#!/usr/bin/env python3
"""Every command the CLI advertises must actually run.

Origin: `chain` was dead from the rename until today. It used rich's Table
without importing it, so it raised NameError on every invocation — a
documented, shipped command that had never once worked. Nothing executed it,
so nothing noticed. Only flake8's F821 eventually surfaced it, months later.

That is a class of bug, not an incident. The same shape appeared three times
in one day across these repositories: a command exists, the docs promise it,
and no test ever runs the two together.

So this suite discovers commands from `--help` rather than listing them. A new
command is covered the moment it is added, without anyone remembering to come
back here — a checklist someone must maintain is a checklist that goes stale.
"""

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE = "chronolith_pro.chronolith.run_chronolith_cycle"
REPO = Path(__file__).resolve().parents[1]

# Commands that reach the network or mutate signing state. Their wiring is
# checked through --help; running them for real belongs in a manual release
# check, not in a suite that must pass offline and in seconds.
NETWORK_OR_DESTRUCTIVE = {"anchor", "upgrade-anchors", "verify-anchor", "sovereign-rotate"}


def run(args, cwd=None):
    return subprocess.run(
        [sys.executable, "-m", PACKAGE, *args],
        cwd=cwd or REPO, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=180,
    )


def discover_commands() -> list[str]:
    """Ask the Typer app what it registered.

    Parsing --help was the first attempt and it was wrong: rich wraps long
    descriptions into continuation lines that look exactly like command rows,
    so the list filled with words like "the" and "signature". The app object
    is the authority and cannot drift from what is actually wired.
    """
    sys.path.insert(0, str(REPO))
    from chronolith_pro.chronolith.run_chronolith_cycle import app

    names = []
    for command in app.registered_commands:
        name = command.name or (command.callback.__name__ if command.callback else None)
        if name:
            names.append(name.replace("_", "-"))
    return sorted(set(names))


class TestCliSurface(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.commands = discover_commands()

    def test_help_lists_commands(self):
        self.assertGreater(len(self.commands), 5,
                           f"expected a real command list, parsed {self.commands}")

    def test_every_command_has_working_help(self):
        """--help exercises the decorator and the signature.

        It does not prove the body runs, which is why the read-only commands
        below are executed for real. It does prove the command is wired.
        """
        broken = []
        for command in self.commands:
            result = run([command, "--help"])
            if result.returncode != 0:
                broken.append(f"{command}: exit {result.returncode}")
        self.assertEqual(broken, [], f"commands whose --help fails: {broken}")

    def test_read_only_commands_execute(self):
        """Run the safe commands against a real initialized project.

        This is the check that would have caught `chain`: --help passes on a
        command whose body raises NameError, because --help never enters it.
        """
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            root = Path(tmp)
            (root / "DOC.md").write_text("# Canonical\n", encoding="utf-8")
            subprocess.run(["git", "init"], cwd=root, capture_output=True)

            first = run(["init", "--repo-root", str(root)])
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            run(["check", "--repo-root", str(root), "--no-scan-source"])

            failures = []
            for command in self.commands:
                if command in NETWORK_OR_DESTRUCTIVE or command in {"init", "check"}:
                    continue
                result = run([command, "--repo-root", str(root)])
                output = result.stdout + result.stderr
                # A command may legitimately refuse (missing keys, nothing to
                # prove). It may not crash: a traceback is always a defect.
                if "Traceback" in output or "NameError" in output or "AttributeError" in output:
                    failures.append(f"{command}: {output.strip().splitlines()[-1][:120]}")
            self.assertEqual(failures, [], f"commands that crashed: {failures}")


if __name__ == "__main__":
    unittest.main()
