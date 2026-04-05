import os

def fix_content(content):
    # Mapping exhaustive de mojibake detectado en los escaneos
    replacements = {
        'ðŸ ¢': '🏛️', # Building
        'ðŸ💎': '💎', # Diamond
        'ðŸ§ ': '🧠', # Brain
        'ðŸŒŒ': '🌌', # Galaxy
        'ðŸš🚀': '🚀', # Rocket
        'âœ”]': '✔', 
        'â€œ': '“', 'â€ ': '”', 'â€”': '—',
        'ðŸ§¬': '🧬', 'ðŸ ±ï¸': '⏳', 'ðŸ” ': '🔍',
        'ðŸ§©': '🧩', 'ðŸš€': '🚀', 'ðŸ ·ï¸': '🏷️',
        'Â ': '', # Ghost space
        'ðŸŒ🌍': '🌍', 'ðŸ”🔒': '🔒', 'ðŸ§ª': '🧪',
        'â ±ï¸': '⏱️', 'ðŸ’ª': '💪', 'ðŸ§ª': '🧪',
        'ðŸ ¢': '🏛️',
        'ðŸ§': '🎨', # Design
        'ðŸ”': '🔍'
    }
    for old, new in replacements.items():
        content = content.replace(old, new)
    return content

def heal_all():
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.md'):
                p = os.path.join(root, file)
                try:
                    with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                        data = f.read()
                    fixed = fix_content(data)
                    if fixed != data:
                        with open(p, 'w', encoding='utf-8') as f:
                            f.write(fixed)
                        print(f"Healed: {p}")
                except Exception as e:
                    print(f"Error: {p} {e}")

if __name__ == "__main__":
    heal_all()
