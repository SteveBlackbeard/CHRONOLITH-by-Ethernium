import hashlib, json
from pathlib import Path

CANONICAL_AUDIT_DIRS = [".", "OTHER_LANGUAGES", "docs"]

def calculate_sha256(path):
    if not (path.exists() and path.is_file()): return ""
    try:
        content = path.read_text(encoding="utf-8")
    except:
        return ""
    lines = content.splitlines()
    filtered = []
    for l in lines:
        if "DNA CRYSTAL" in l or "img.shields.io/badge/DNA--Crystallized" in l:
            continue
        filtered.append(l.rstrip())
    return hashlib.sha256("\n".join(filtered).strip().encode("utf-8")).hexdigest()

def build_merkle(hashes):
    if not hashes: return "0"*64
    cur = [hashlib.sha256(b"\x00"+h.encode()).hexdigest() for h in sorted(hashes)]
    while len(cur)>1:
        nxt=[]
        if len(cur)%2: cur.append(cur[-1])
        for i in range(0,len(cur),2):
            nxt.append(hashlib.sha256(b"\x01"+(cur[i]+cur[i+1]).encode()).hexdigest())
        cur=nxt
    return cur[0]

root = Path(".").resolve()
all_md = []
for audit_dir in CANONICAL_AUDIT_DIRS:
    a_path = root / audit_dir
    if not a_path.exists(): continue
    if audit_dir == ".":
        for f in a_path.glob("*.md"):
            if "PROJECT_DNA" not in f.name:
                all_md.append(f)
    else:
        for f in a_path.rglob("*.md"):
            if "PROJECT_DNA" not in f.name:
                all_md.append(f)

# Crystal sorting: sorted(all_md_files) = sorts by full absolute path
crystal_sorted = sorted(all_md)
# LITE sorting: sorts by relative POSIX path
lite_sorted = sorted(all_md, key=lambda x: x.relative_to(root).as_posix())

print("=== CRYSTAL ORDER ===")
for f in crystal_sorted:
    print(f"  {f.relative_to(root).as_posix()} -> {calculate_sha256(f)[:12]}")

print()
print("=== LITE ORDER ===")
for f in lite_sorted:
    print(f"  {f.relative_to(root).as_posix()} -> {calculate_sha256(f)[:12]}")

print()
same = [f.name for f in crystal_sorted] == [f.name for f in lite_sorted]
print(f"Same order? {same}")

crystal_hashes = [calculate_sha256(f) for f in crystal_sorted]
lite_hashes = [calculate_sha256(f) for f in lite_sorted]

crystal_root = build_merkle(crystal_hashes)
lite_root = build_merkle(lite_hashes)

state = json.loads(Path("STATE.json").read_text())
mr = state["merkle_root"]
print(f"Crystal Merkle:  {crystal_root[:16]}")
print(f"LITE Merkle:     {lite_root[:16]}")
print(f"STATE.json:      {mr[:16]}")
print(f"Crystal==LITE? {crystal_root == lite_root}")
print(f"Crystal==STATE? {crystal_root == mr}")
