import os
import re
from pathlib import Path

# THE SOVEREIGN AUDIT SCANNER (v2.4.2)
# -----------------------------------
# Purpose: Identify inconsistencies, bottlenecks, and contradictions.
# FIX: Corrected iteration logic for tonal check.

EXCLUDE_DIRS = [".git", "node_modules", ".continuity", "outputs", ".pytest_cache", "__pycache__", ".venv", ".github", ".idea", ".vscode"]

def scan_global():
    root = Path(".")
    issues = []
    
    print("\n[+] STARTING SOVEREIGN AUDIT SCAN...")
    
    # 1. MOJIBAKE & ENCODING CHECK (Ciberseguridad)
    for r, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if f.endswith((".md", ".json", ".py")):
                f_path = Path(r) / f
                try:
                    f_path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    issues.append(f"ENCODING: Mojibake detected in {f_path.as_posix()}")

    # 2. REDUNDANCY CHECK
    redundant_files = ["LIVE_HANDOFF.md"]
    for rf in redundant_files:
        if (root / rf).exists():
            issues.append(f"REDUNDANCY: {rf} is legacy. Consider merging into TIMELINE.md.")

    # 3. LINK INTEGRITY CHECK (Contradicciones)
    for r, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if f.endswith(".md"):
                f_path = Path(r) / f
                content = f_path.read_text(encoding="utf-8")
                links = re.findall(r'\[.*?\]\((.*?)\)', content)
                for link in links:
                    if link.startswith(".") and not link.startswith("http") and not link.startswith("#"):
                        # Basic relative path check
                        try:
                            l_path = (f_path.parent / link.split("#")[0]).resolve()
                            if not l_path.exists():
                                issues.append(f"DEAD LINK: {f_path.as_posix()} -> {link}")
                        except Exception:
                            pass

    # 4. TONAL CONSISTENCY (Enterprise Standard)
    forbidden_terms = ["military", "sovereign", "visceral"]
    for r, dirs, files in os.walk(root):
      dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
      for f in files:
        if f.endswith(".md") and ("README" in f or "RELEASE" in f):
          f_path = Path(r) / f
          content = f_path.read_text(encoding="utf-8").lower()
          for term in forbidden_terms:
            if term in content:
              issues.append(f"TONE: '{term}' found in {f_path.as_posix()}. Deprecated by Enterprise standard.")

    # REPORT
    if not issues:
        print("[✔] SYSTEM AUDIT: ABSOLUTE PARITY CONFIRMED.")
    else:
        print(f"\n[!] AUDIT FINDINGS: {len(issues)} issues identified.")
        for issue in issues:
            print(f"    - {issue}")

if __name__ == "__main__":
    scan_global()
