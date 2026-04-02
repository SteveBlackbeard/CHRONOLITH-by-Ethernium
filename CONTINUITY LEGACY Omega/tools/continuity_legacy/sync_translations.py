from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REGISTRY_PATH = ".continuity/registry/translation_hashes.json"
ROOT_FILES = ["README.md", "USE_CASES.md", "TROUBLESHOOTING.md"]
LANG_CODES = ["es", "ja", "ru", "zh", "fr", "it", "de", "nl", "en"]


def calculate_md5(path: Path) -> str:
    if not path.exists():
        return ""
    return hashlib.md5(path.read_bytes()).hexdigest()


def load_registry(repo_root: Path) -> dict:
    reg_file = repo_root / REGISTRY_PATH
    if reg_file.exists():
        return json.loads(reg_file.read_text(encoding="utf-8"))
    return {"version": "1.0", "hashes": {}}


def save_registry(repo_root: Path, registry: dict) -> None:
    reg_file = repo_root / REGISTRY_PATH
    reg_file.parent.mkdir(parents=True, exist_ok=True)
    reg_file.write_text(json.dumps(registry, indent=2, ensure_ascii=True), encoding="utf-8")


def check_sync(repo_root: Path) -> dict:
    registry = load_registry(repo_root)
    report = {"status": "ok", "stale_files": []}
    
    for filename in ROOT_FILES:
        root_path = repo_root / filename
        current_hash = calculate_md5(root_path)
        
        # Check against the recorded root hash
        last_recorded_hash = registry["hashes"].get(filename, {}).get("root")
        
        if current_hash != last_recorded_hash:
            report["status"] = "attention_required"
            report["stale_files"].append({
                "file": filename,
                "reason": "root_changed",
                "affected_languages": LANG_CODES
            })
            
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Synchronize translation hashes and detect drift.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--update-hashes", action="store_true", help="Mark current state as synchronized.")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    report = check_sync(root)
    
    if args.update_hashes:
        registry = load_registry(root)
        for filename in ROOT_FILES:
            current_hash = calculate_md5(root / filename)
            if filename not in registry["hashes"]:
                registry["hashes"][filename] = {}
            registry["hashes"][filename]["root"] = current_hash
        save_registry(root, registry)
        print("[✔] Translation hashes updated. State is now canonical.")
        return

    print(json.dumps(report, indent=2))
    if report["status"] != "ok":
        print("\n[!] DRIFT DETECTED: Documentation translations are out of sync with root.")
        print("[*] Please update 'OTHER_LANGUAGES/' and then run with --update-hashes.")


if __name__ == "__main__":
    main()
