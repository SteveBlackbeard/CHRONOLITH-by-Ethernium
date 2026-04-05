import os

def final_heal(text):
    # Mapping exact byte-level artifacts back to clean UTF-8
    # These are common mojibake patterns for UTF-8 Emojis in Latin-1 environments
    corruption_map = {
        '\xc3\xb0\xc5\xb8\xc2\xa2': '🏛️', # 1.3.1 Building
        '\xc3\xb0\xc5\xb8\xc2\x98': '💎', # Diamond
        '\xc3\xb0\xc5\xb8\xc2\xa7\xc2\xa0': '🧠', # Brain
        '\xc3\xb0\xc5\xb8\xc2\x8c\xc2\x8c': '🌌', # Galaxy
        '\xc3\xa2\xc2\x80\xc2\x9c': '“', # Quote
        '\xc3\xa2\xc2\x80\xc2\x9d': '”', # Quote
        '\xc3\xa2\xc2\x80\xc2\x94': '—', # Dash
        'ðŸ ¢': '🏛️',
        'ðŸ§©': '🧩',
        'ðŸ ±ï¸': '⏳',
        'ðŸš€': '🚀',
        'ðŸ ·ï¸': '🏷️'
    }
    for old, new in corruption_map.items():
        text = text.replace(old, new)
    return text

def process_repo():
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'rb') as f:
                        raw = f.read()
                    
                    # Try to decode as utf-8, if fails, it's definitely mojibake'd
                    try:
                        decoded = raw.decode('utf-8')
                        content = final_heal(decoded)
                        if content != decoded:
                            with open(path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            print(f"[✔] Corrected: {path}")
                    except UnicodeDecodeError:
                        # If it's not valid UTF-8, it's likely the tool mangled it to ANSI
                        decoded = raw.decode('latin-1')
                        content = final_heal(decoded)
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"[⚠] Recovered from Latin-1: {path}")
                except Exception as e:
                    print(f"Error {path}: {e}")

if __name__ == "__main__":
    process_repo()
