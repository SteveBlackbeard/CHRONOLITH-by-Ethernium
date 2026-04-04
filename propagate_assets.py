import re
from pathlib import Path

HEADER_HTML = """<p align="center">
  <img src="https://raw.githubusercontent.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/main/banners/ethernium_header.png?raw=true" alt="Ethernium Continuity Legacy Official Header">
</p>"""

PNG_BANNERS_INJECTION = """Continuity is now structured into three specialized editions to provide the right level of governance for every project:

[![LITE](https://raw.githubusercontent.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/main/banners/LEGACYlite.png?raw=true)](https://github.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/blob/main/continuity-lite/)
[![PRO](https://raw.githubusercontent.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/main/banners/LEGACYpro.png?raw=true)](https://github.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/blob/main/continuity-pro/)
[![OMEGA](https://raw.githubusercontent.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/main/banners/LEGACYomega.png?raw=true)](https://github.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/blob/main/continuity-omega/)
"""

def fix_file(filepath):
    content = Path(filepath).read_text(encoding='utf-8')
    
    # 1. Limpiar encabezados antiguos y la imagen duplicada (1280x640)
    content = re.sub(r'^<p align="center">.*?</p>\s*', '', content, flags=re.DOTALL)
    content = re.sub(r'<img width="1280" height="640" alt="ethernium".*?/>\s*', '', content)
    
    # Inyectar el nuevo encabezado
    content = f"{HEADER_HTML}\n\n" + content
    
    # 2. Reemplazar la sección "#### Editions" con Shields genéricos por los Banners PNG
    p_shields_editions = r'#### Editions\s*\[\!\[LITE\].*?OMEGA-black.*?omega/\)'
    content = re.sub(p_shields_editions, PNG_BANNERS_INJECTION, content, flags=re.DOTALL)
    
    # 3. Eliminar la antigua sección redundante de banners locales (si existe) para evitar duplicados
    p_local_banners = r'## 🏢 Choose Your Edition.*?(?=### 🧠|\n---|\n## )'
    content = re.sub(p_local_banners, '', content, flags=re.DOTALL)
    
    # Verificar que no haya parámetros raw duplicados
    content = content.replace('?raw=true?raw=true', '?raw=true')
    
    Path(filepath).write_text(content, encoding='utf-8')
    print(f'Soberanía Visual Propagada en: {filepath.name}')

if __name__ == "__main__":
    for f in Path('OTHER_LANGUAGES').glob('*.md'):
        fix_file(f)
    print("¡Propagación completada en todos los espejos!")
