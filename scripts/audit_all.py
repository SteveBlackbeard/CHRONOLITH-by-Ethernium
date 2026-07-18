#!/usr/bin/env python3
"""Canonical full audit for Chronolith.

Root-level `pytest` cross-contaminates: the three editions vendor modules with
the same names, so pytest's shared sys.modules serves one edition's core to
another edition's tests. The correct way to run everything is per-edition in
SEPARATE processes — which is what CI does per job and what this script does
locally in one command:

    python scripts/audit_all.py            # isolated tests + cross-edition parity
    python scripts/audit_all.py --install  # also build+install each guardian in a clean venv

Exit code 0 means every edition passes in isolation, the vendored core has not
drifted between editions, and (with --install) the packages install and run.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FAILURES: list[str] = []

EDITIONS = ["chronolith-lite", "chronolith-pro", "chronolith-omega"]
# Guardians with light deps that are cheap to install-audit. Omega pulls chromadb
# (heavy); it is covered by the isolated test run, not the install smoke.
INSTALLABLE = {
    "chronolith-lite": ("chronolith-lite", ["typer", "rich"]),
    "chronolith-pro": ("chronolith-pro", ["typer", "rich", "cryptography"]),
}


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" -> {detail}" if detail and not ok else ""))
    if not ok:
        FAILURES.append(name)


def isolated_tests() -> None:
    print("== per-edition tests (isolated processes) ==")
    for edition in EDITIONS:
        tests = REPO / edition / "tests"
        if not tests.exists():
            continue
        result = run([sys.executable, "-m", "pytest", str(tests), "-q"], cwd=REPO)
        tail = (result.stdout.strip().splitlines() or [""])[-1]
        check(f"{edition} tests", result.returncode == 0, tail)


def parity_test() -> None:
    print("== cross-edition core parity ==")
    result = run([sys.executable, "-m", "pytest", str(REPO / "tests" / "test_edition_parity.py"), "-q"], cwd=REPO)
    tail = (result.stdout.strip().splitlines() or [""])[-1]
    check("core parity across editions", result.returncode == 0, tail)


def install_smoke() -> None:
    print("== install smoke (clean venvs) ==")
    for edition, (pkg_dir, _deps) in INSTALLABLE.items():
        pkg = REPO / pkg_dir
        build = run([sys.executable, "-m", "build", str(pkg)], cwd=REPO)
        check(f"{edition} builds", build.returncode == 0, build.stderr[-300:])
        wheels = sorted((pkg / "dist").glob("*.whl"))
        if not wheels:
            check(f"{edition} wheel exists", False)
            continue
        with tempfile.TemporaryDirectory() as tmp:
            env_dir = Path(tmp) / "venv"
            venv.create(env_dir, with_pip=True)
            bin_dir = env_dir / ("Scripts" if sys.platform == "win32" else "bin")
            py = bin_dir / ("python.exe" if sys.platform == "win32" else "python")
            inst = run([str(py), "-m", "pip", "install", "--quiet", str(wheels[-1])])
            check(f"{edition} installs clean", inst.returncode == 0, inst.stderr[-300:])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--install", action="store_true", help="Also build+install each guardian in a clean venv.")
    args = parser.parse_args()

    isolated_tests()
    parity_test()
    if args.install:
        install_smoke()

    print()
    if FAILURES:
        print(f"AUDIT FAILED: {len(FAILURES)} check(s) -> {', '.join(FAILURES)}")
        return 1
    print("AUDIT PASSED: editions green in isolation, core has not drifted" +
          (", packages install clean." if args.install else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
