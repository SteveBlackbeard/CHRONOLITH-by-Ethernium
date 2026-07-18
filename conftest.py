"""Root pytest configuration.

The three editions each vendor a package named ``chronolith``. Under a single
pytest process the first one imported wins ``sys.modules["chronolith"]``, so
every later edition's tests run against the wrong edition's code and fail —
around 34 of them, all false negatives on a perfectly healthy tree.

CI never hit this because it runs each edition in a separate job. A person who
clones the repo and types ``pytest`` did hit it, and had no way to tell a real
break from this artifact.

So the edition directories are not collected from the root. Bare ``pytest``
here runs only the cross-edition tests, which are process-safe, and points at
the runner that does the full job in isolated processes.
"""

from __future__ import annotations

collect_ignore_glob = ["chronolith-*"]


def pytest_report_header(config) -> str:
    return (
        "chronolith: edition suites are NOT collected from the repo root "
        "(same-named packages would shadow each other).\n"
        "            full run -> python scripts/audit_all.py"
    )
