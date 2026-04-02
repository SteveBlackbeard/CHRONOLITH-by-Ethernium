from __future__ import annotations

import argparse
from pathlib import Path

CORE_FILES = [
    "PROJECT_CONTEXT.md",
    "ROADMAP.md",
    ".continuity/LIVE_HANDOFF.md",
    ".continuity/DECISIONS_LOG.md",
]


def extract_summary(path: Path, max_lines: int = 50) -> str:
    if not path.exists():
        return f"File {path.name} not found."
    
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()
    
    # Simple extraction: take title and first relevant section
    header = f"### {path.name} ###\n"
    body = "\n".join(lines[:max_lines])
    if len(lines) > max_lines:
        body += "\n[... Content Truncated ...]"
    
    return f"{header}{body}\n"


def generate_consolidated_summary(repo_root: Path) -> str:
    outputs = ["# CONTINUITY LEGACY: Memory Summary (Consolidated) 🧠\n"]
    outputs.append(f"Generated at: (Use UTC if possible)\n")
    
    for rel_path in CORE_FILES:
        outputs.append(extract_summary(repo_root / rel_path))
        
    outputs.append("\n--- END OF SUMMARY ---\n")
    return "\n".join(outputs)


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize canonical memory files.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output", default="outputs/continuity/memory_summary.md")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    summary = generate_consolidated_summary(root)
    
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(summary, encoding="utf-8")
    
    print(f"[✔] Memory summarized at: {args.output}")


if __name__ == "__main__":
    main()
