import json
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime
from .sovereign_identity import get_identity
from .ene_optimizer import ENEOptimizer

# ETHERNIUM ZIP BRIDGE (v1.0.0 - DUAL PORTAL)
# ------------------------------------------
# Purpose: Symmetric Identity for Compressed Projects.
# Outside: Ethernium_Portal_Outside.json
# Inside:  Ethernium_Portal_Inside.json

def get_file_hash(path: Path) -> str:
    if not path.is_file(): return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def create_portal_zip(folder_path: str, output_name: str = None):
    root = Path(folder_path).resolve()
    if not root.exists(): return f"[!] Folder {folder_path} not found."
    
    output_name = output_name or f"{root.name}_Portal.zip"
    identity = get_identity()
    optimizer = ENEOptimizer()
    
    # 1. Gather DNA (Merkle Root of contents)
    files = [f for f in root.rglob("*") if f.is_file() and ".chronolith" not in f.parts]
    hashes = [get_file_hash(f) for f in sorted(files)]
    
    # Simple Merkle Root for the portal
    merkle_root = hashlib.sha256("".join(hashes).encode("utf-8")).hexdigest()
    
    # 2. Extract Logical Ghost (ENE Summary)
    # We summarize the first few lines of main files for context
    summary_text = f"Ethernium Portal: {root.name}\nFiles: {len(files)}\nRoot: {merkle_root[:16]}"
    ghost_map = optimizer.compress(summary_text)
    
    portal_data = {
        "portal_name": root.name,
        "version": "1.0.0 (Nexus)",
        "timestamp": datetime.now().isoformat(),
        "merkle_root": merkle_root,
        "ghost_map": ghost_map,
        "identity_claimed": "SteveBlackbeard (Sovereign Root)"
    }
    
    # 3. Create Internal Portal (Signed)
    signed_portal = identity.sign_json(portal_data)
    
    # 4. Packaging
    zip_path = Path(output_name)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add internal portal
        zf.writestr("Ethernium_Portal_Inside.json", json.dumps(signed_portal, indent=2))
        # Add all files
        for f in files:
            zf.write(f, f.relative_to(root))
            
    # 5. Create External Portal (Symmetric Ghost)
    outside_portal_path = zip_path.with_name("Ethernium_Portal_Outside.json")
    outside_portal_path.write_text(json.dumps(signed_portal, indent=2), encoding="utf-8")
    
    return f"[✔] Portal {output_name} Created. Symmetry: Ethernium_Portal_Outside.json generated."

def verify_portal(zip_path: str) -> dict:
    zip_p = Path(zip_path)
    if not zip_p.exists(): return {"error": "Zip not found."}
    
    identity = get_identity()
    try:
        with zipfile.ZipFile(zip_p, "r") as zf:
            if "Ethernium_Portal_Inside.json" not in zf.namelist():
                return {"error": "No Ethernium Portal found inside."}
            
            raw_inside = zf.read("Ethernium_Portal_Inside.json")
            inside_data = json.loads(raw_inside)
            
            # Verify Signature
            is_valid = identity.verify_json(inside_data)
            return {
                "valid": is_valid,
                "portal_name": inside_data.get("portal_name"),
                "merkle_root": inside_data.get("merkle_root"),
                "ghost_map": inside_data.get("ghost_map")
            }
    except Exception as e:
        return {"error": str(e)}
