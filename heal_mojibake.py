import os
import re

def heal_mojibake(content):
    # Mapping corrupted patterns back to their original UTF-8
    # Ethernium Symbols & Emojis
    replacements = {
        'ðŸ ¢': '🏛️', # Building
        'ðŸ💎': '💎', # Diamond
        'ðŸ§ ': '🧠', # Brain
        'ðŸŒŒ': '🌌', # Galaxy
        'ðŸš🚀': '🚀', # Rocket
        'âœ”]': '✔',  # Check mark
        'â€œ': '“',   # Smart quote Left
        'â€': '”',   # Smart quote Right
        'â€”': '—',   # Em dash
        'ðŸ§¬': '🧬', # DNA
        'ðŸ ±ï¸': '⏳', # Hourglass
        'ðŸ” ': '🔍', # Search
        'ðŸ§©': '🧩', # Puzzle
        'ðŸš€': '🚀', # Rocket
        'ðŸ§ ': '🧠', # Brain
        'ðŸ ·ï¸': '🏷️', # Label
    }
    for old, new in replacements.items():
        content = content.replace(old, new)
    return content

def fix_all_md(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                try:
                    # Attempt to read as UTF-8
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        original = f.read()
                    
                    healed = heal_mojibake(original)
                    
                    if healed != original:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(healed)
                        print(f"[✔] HEALED: {path}")
                except Exception as e:
                    print(f"[!] ERROR processing {path}: {e}")

if __name__ == "__main__":
    fix_all_md(".")
