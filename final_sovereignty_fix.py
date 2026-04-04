# -*- coding: utf-8 -*-
import re
import os

BANNER_HEADER = """<p align="center">
  <img src="https://raw.githubusercontent.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/main/banners/ethernium_header.png" alt="Ethernium Continuity Legacy Official Header">
</p>

"""

# Banners PNG Originales (Referencia absoluta de GitHub para máxima visibilidad corporativa)
PNG_LITE = '[![LITE](https://raw.githubusercontent.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/main/banners/LEGACYlite.png)](https://github.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/blob/main/continuity-lite/)'
PNG_PRO = '[![PRO](https://raw.githubusercontent.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/main/banners/LEGACYpro.png)](https://github.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/blob/main/continuity-pro/)'
PNG_OMEGA = '[![OMEGA](https://raw.githubusercontent.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/main/banners/LEGACYomega.png)](https://github.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/blob/main/continuity-omega/)'

def finalize_sovereignty(filepath):
    print(f"Sellando Soberanía Visual en {filepath}...")
    if not os.path.exists(filepath):
        return
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Aseguramos el Header (eliminando duplicados previos)
    content = re.sub(r'^<p align="center">.*?</p>', '', content, flags=re.DOTALL | re.MULTILINE).strip()
    content = BANNER_HEADER + content
    
    # 2. Sustituimos Badges Shields.io por PNGs Originales
    # Patrones para badges simplificados que introduje por error
    p_lite = r'<a href=\".*?lite\"><img src=\"https://img.shields.io/badge/Edition-Lite.*?\"></a>'
    p_pro = r'<a href=\".*?(?:pro|continuity)\"><img src=\"https://img.shields.io/badge/Edition-Pro.*?\"></a>'
    p_omega = r'<a href=\".*?omega\"><img src=\"https://img.shields.io/badge/Edition-Omega.*?\"></a>'
    
    content = re.sub(p_lite, PNG_LITE, content)
    content = re.sub(p_pro, PNG_PRO, content)
    content = re.sub(p_omega, PNG_OMEGA, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"ÉXITO: {filepath} sellado v2.1.5.")

if __name__ == "__main__":
    finalize_sovereignty('RELEASE_NOTES_MANIFEST.md')
    finalize_sovereignty('README.md')
    if os.path.exists('restore_dna.py'):
        os.remove('restore_dna.py')
