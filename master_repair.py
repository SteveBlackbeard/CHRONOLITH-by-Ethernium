import os
import subprocess

def fix_mojibake(text):
    # Dictionaries of known corrupt patterns across all languages
    replacements = {
        'ðŸ ¢': '🏛️', 'ðŸ💎': '💎', 'ðŸ§ ': '🧠', 'ðŸŒŒ': '🌌', 
        'ðŸš🚀': '🚀', 'âœ”]': '✔', 'â€œ': '“', 'â€ ': '”', 
        'â€”': '—', 'ðŸ§¬': '🧬', 'ðŸ ±ï¸': '⏳', 'ðŸ” ': '🔍', 
        'ðŸ§©': '🧩', 'ðŸš€': '🚀', 'ðŸ ·ï¸': '🏷️', 'Â ': '',
        'ðŸ§ ': '🧠', 'ðŸŒ🌍': '🌍', 'ðŸ”🔒': '🔒', 'ðŸ§ª': '🧪',
        'â ±ï¸': '⏱️', 'ðŸš€': '🚀', 'ðŸ’ª': '💪'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def restore_manifest():
    # 1. Recover beautiful v1.3.1 content from commit 5067149
    try:
        # Use binary then decode to avoid encoding issues
        raw = subprocess.check_output(['git', 'show', '5067149:RELEASE_NOTES_MANIFEST.md'])
        content = raw.decode('utf-8', 'ignore')
        
        # 2. Modernize version
        content = content.replace('v1.3.1', 'v2.1.0')
        content = content.replace('1.3.1', '2.1.0')
        
        # 3. Add Header if missing
        header = '<p align="center">\n  <img src="https://raw.githubusercontent.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/main/banners/ethernium_header.png?raw=true" alt="Ethernium Continuity Legacy Official Header">\n</p>\n\n'
        if 'ethernium_header' not in content:
            content = header + content
            
        # 4. Correct Language Ribbons (Surgical injection)
        base_url = 'https://github.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/blob/main/'
        l_row = '#### Languages\n'
        l_row += f'[![ES](https://img.shields.io/badge/ES-white)]({base_url}OTHER_LANGUAGES/RELEASE_v2.1.0_es.md) '
        l_row += f'[![EN](https://img.shields.io/badge/EN-white)]({base_url}RELEASE_NOTES_MANIFEST.md) '
        l_row += f'[![JA](https://img.shields.io/badge/JA-white)]({base_url}OTHER_LANGUAGES/RELEASE_v2.1.0_ja.md) '
        l_row += f'[![ZH](https://img.shields.io/badge/ZH-white)]({base_url}OTHER_LANGUAGES/RELEASE_v2.1.0_zh.md) '
        l_row += f'[![RU](https://img.shields.io/badge/RU-white)]({base_url}OTHER_LANGUAGES/RELEASE_v2.1.0_ru.md) '
        l_row += f'[![FR](https://img.shields.io/badge/FR-white)]({base_url}OTHER_LANGUAGES/RELEASE_v2.1.0_fr.md) '
        l_row += f'[![IT](https://img.shields.io/badge/IT-white)]({base_url}OTHER_LANGUAGES/RELEASE_v2.1.0_it.md) '
        l_row += f'[![DE](https://img.shields.io/badge/DE-white)]({base_url}OTHER_LANGUAGES/RELEASE_v2.1.0_de.md) '
        l_row += f'[![PT](https://img.shields.io/badge/PT-white)]({base_url}OTHER_LANGUAGES/RELEASE_v2.1.0_pt.md) \n\n'
        
        # Replace simple badges section or insert under title
        if 'Languages' not in content:
            lines = content.split('\n')
            lines.insert(lines.index('# Official Stable Release v2.1.0 - Global Continuity Framework 🧬🏛️🚀') + 1, '\n' + l_row)
            content = '\n'.join(lines)
            
        with open('RELEASE_NOTES_MANIFEST.md', 'w', encoding='utf-8') as f:
            f.write(content)
        print("[✔] Successfully restored beautiful manifest.")
    except Exception as e:
        print(f"[!] Error in manifestation: {e}")

def surgical_readme_update():
    path = 'README.md'
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        content = fix_mojibake(content)
        
        # New Sections
        new_content = """
---

## 🌌 The Future: Omega Dashboard 3D & Advanced Logic

### 🏛️ The Parity Cycle (Flow Diagram)
Continuity ensures that every human-AI handoff is backed by a deterministic validation loop:

```mermaid
graph LR
    A[Human Context] --> B{DNA Synthesis}
    B --> C[Merkle Root Verification]
    C -- Matched --> D[Secure Operation]
    C -- Drift Detected --> E[Self-Healing & Audit]
    E --> B
```

### ⚙️ Algorithm: DNA Nucleotide Guardian
The core logic in `doc_parity_check.py` uses a weighted hashing system to ensure that structural metadata (DNA) remains invariant across editions:

```python
def generate_nucleotide_hash(file_data):
    # Weighted normalization of markdown artifacts
    normalized = normalize_whitespace_and_bom(file_data)
    return hashlib.sha256(normalized).hexdigest()
```

### 🛰️ Omega Dashboard: 3D Cognitive Architecture
The upcoming **Omega Dashboard** (React-based) will feature a **3D Force-Graph View** of the entire repository ecosystem.
- **Rotatable Topology**: Manipulate the DNA nexus in 3D space with your cursor.
- **Node Interaction**: Click on "Nucleotides" (files) to inspect decision logs and health status.
- **Holographic HUD**: Real-time visual feedback on project parity and semantic drift.
"""
        if 'Omega Dashboard 3D' not in content:
            content = content.rstrip() + "\n" + new_content
            
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("[✔] README.md surgically updated with new sections.")
    except Exception as e:
        print(f"[!] Error in README update: {e}")

if __name__ == "__main__":
    restore_manifest()
    surgical_readme_update()
