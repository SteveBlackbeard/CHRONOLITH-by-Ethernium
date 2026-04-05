import os
from pathlib import Path

# THE UNIVERSAL SLOGAN INJECTOR
# -----------------------------
# Purpose: Maintain absolute identity parity across 101+ documentation nodes.

SLOGAN = """

---
*Continuity: Protecting the logical lineage of your software.*
"""

EXCLUDE_DIRS = [".git", "node_modules", ".continuity", "outputs", ".pytest_cache", ".venv", "__pycache__", ".idea"]

def inject():
    root = Path(".")
    count = 0
    for r, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if f.endswith(".md") and "PROJECT_DNA" not in f:
                f_path = Path(r) / f
                content = f_path.read_text(encoding="utf-8")
                
                # Check if slogan already exists (to avoid duplicates)
                if "*Continuity: Protecting the logical lineage of your software.*" not in content:
                    new_content = content.rstrip() + SLOGAN
                    f_path.write_text(new_content, encoding="utf-8")
                    count += 1
                    print(f"    [✔] {f_path.as_posix()}")

    print(f"\n[*] INJECTION COMPLETE: {count} cells synthesized.")

if __name__ == "__main__":
    inject()
