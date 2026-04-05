from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

# Mapping of indicators to project chassis
CHASSIS_MAP = {
    "package.json": "Node.js / JavaScript Ecosystem",
    "pyproject.toml": "Python (Modern)",
    "requirements.txt": "Python (Legacy/Simple)",
    "go.mod": "Go (Golang)",
    "pom.xml": "Java (Maven)",
    "build.gradle": "Java/Kotlin (Gradle)",
    "Cargo.toml": "Rust",
    "composer.json": "PHP",
    "Gemfile": "Ruby",
    "tsconfig.json": "TypeScript",
    "docker-compose.yml": "Docker Containerized Environment",
    ".eslintrc": "ESLint Governance",
    "pytest.ini": "PyTest Testing Suite",
    "jest.config.js": "Jest Testing Suite",
}


def discover_chassis(repo_root: Path) -> list[str]:
    found = []
    for filename, description in CHASSIS_MAP.items():
        if (repo_root / filename).exists():
            found.append(description)
    return found


def detect_naming_style(repo_root: Path) -> str:
    # Sample files to detect snake_case vs camelCase
    # Focus on .py, .js, .ts files in root or first level of src/
    sample_files = list(repo_root.glob("*.py")) + list(repo_root.glob("src/*.py"))[:2]
    sample_files += list(repo_root.glob("*.js")) + list(repo_root.glob("src/*.js"))[:2]
    
    snake_count = 0
    camel_count = 0
    
    for f in sample_files:
        if f.is_file():
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                # Simple heuristic: find assignments or function defs
                snake_count += len(re.findall(r"[a-z]+_[a-z]+", content))
                camel_count += len(re.findall(r"[a-z]+[A-Z][a-z]+", content))
            except Exception:
                continue
                
    if snake_count > camel_count:
        return "snake_case (Detected)"
    elif camel_count > snake_count:
        return "camelCase (Detected)"
    return "undetermined (Default to snake_case)"


def generate_context_draft(repo_root: Path, project_name: str) -> str:
    chassis = discover_chassis(repo_root)
    naming = detect_naming_style(repo_root)
    
    draft = f"""# PROJECT CONTEXT: {project_name} (DISCOVERY DRAFT) 🔍

## SYSTEM ROLE:
This project is identified as a **{", ".join(chassis) if chassis else "Generic"}** environment.
The primary naming convention detected is **{naming}**.

## CONTEXT CONTINUITY RULES:
- **Rule 1**: Maintain the {naming} style across all new developments.
"""
    if "TypeScript" in str(chassis):
        draft += "- **Rule 2**: Ensure all documentation reflects any changes in the Type system.\n"
    if "Docker" in str(chassis):
        draft += "- **Rule 3**: Document infrastructure changes in the `DECISIONS_LOG.md` before applying to Docker Compose.\n"
        
    draft += """- **General**: Every significant change must be reflected in the `.continuity/` surfaces.
- **Verification**: Run `python tools/continuity_legacy/run_continuity_cycle.py` before any push.

## ARCHITECTURE OVERVIEW:
- **Entrypoint**: (To be defined)
- **Primary Stack**: {chassis}
- **Testing**: {", ".join([c for c in chassis if "Testing" in c]) if chassis else "To be defined"}
"""
    return draft


def main() -> None:
    parser = argparse.ArgumentParser(description="Discover project context and suggest rules.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--name", default="Unnamed Project")
    parser.add_argument("--output", default="PROJECT_CONTEXT.md.draft")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    print(f"[*] Discovering project structure in: {root}")
    
    draft = generate_context_draft(root, args.name)
    
    output_path = Path(args.output)
    output_path.write_text(draft, encoding="utf-8")
    print(f"[✔] Discovery complete! Draft generated at: {args.output}")
    print("[!] Review the draft and merge it into your main PROJECT_CONTEXT.md")


if __name__ == "__main__":
    main()
