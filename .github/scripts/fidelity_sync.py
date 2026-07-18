import os
from pathlib import Path
import re

def get_header_sections(content):
    # Split content by H2 headers (##)
    sections = re.split(r'\n(?=## )', content)
    header_part = sections[0]
    body_sections = sections[1:] if len(sections) > 1 else []
    
    section_map = {}
    for s in body_sections:
        match = re.match(r'## (.*?)\n', s)
        if match:
            title = match.group(1).split('(')[0].strip() # Strip "(How to use)" etc
            section_map[title] = s
    return header_part, section_map

def sync_file(source_path, target_path, lang_prefix=""):
    if not source_path.exists() or not target_path.exists():
        return
    
    source_content = source_path.read_text(encoding='utf-8')
    target_content = target_path.read_text(encoding='utf-8')
    
    source_header, source_map = get_header_sections(source_content)
    target_header, target_map = get_header_sections(target_content)
    
    # We want to keep the target's first line (the title translated)
    # But we want to sync the badges and the banner structure
    target_title = target_content.splitlines()[0] if target_content.startswith('# ') else source_content.splitlines()[0]
    
    # Construct new content
    final_output = target_title + "\n" + "\n".join(source_header.splitlines()[1:])
    
    # Iterate through source sections to maintain order
    for title, content in source_map.items():
        # Do we have this section in target?
        # We try to find a matching section title in the target map
        found = False
        for t_title, t_content in target_map.items():
            if title.lower() in t_title.lower() or t_title.lower() in title.lower():
                final_output += "\n" + t_content
                found = True
                break
        
        if not found:
            # Add English section but maybe with a note or just the structure
            final_output += "\n" + content
            
    # Check for target sections NOT in source (User said: inform me, do not touch originals, but don't delete them from translations)
    for t_title, t_content in target_map.items():
        found_in_source = False
        for s_title in source_map.keys():
            if s_title.lower() in t_title.lower() or t_title.lower() in s_title.lower():
                found_in_source = True
                break
        if not found_in_source:
            if t_title not in ["Ediciones", "Idiomas"]: # Skip navigation sections
                print(f"[!] INFO: Section '{t_title}' in {target_path} is NOT in the English original.")
                final_output += "\n" + t_content

    target_path.write_text(final_output, encoding='utf-8')
    print(f"[✔] Synced {target_path}")

# --- EXECUTION ---
root_readme = Path("README.md")
root_release = Path("RELEASE_NOTES_MANIFEST.md")

# Sync Readmes
for rf in Path("OTHER_LANGUAGES").glob("README_*.md"):
    sync_file(root_readme, rf)

# Sync Releases
for rf in Path("OTHER_LANGUAGES").glob("RELEASE_*.md"):
    sync_file(root_release, rf)

# Sync sub-editions
sync_file(root_readme, Path("chronolith-lite/README.md"))
sync_file(root_readme, Path("chronolith-pro/README.md"))
sync_file(root_readme, Path("chronolith-omega/README.md"))

print("Sync completed.")
