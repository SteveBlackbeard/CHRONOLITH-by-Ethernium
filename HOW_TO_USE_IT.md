# Continuity Legacy: Guía Maestra de Operación 🛰️

Esta guía detalla el despliegue industrial de **Continuity Legacy**, desde la instalación base hasta el enlace de paridad con proyectos soberanos (nuevos o existentes).

## 1. 🏛️ Requisitos del Sistema
- **Python**: 3.10 o superior.
- **Git**: Configurado en el entorno local.
- **Shell**: PowerShell (recomendado) o Bash.

## 2. 🚀 Instalación y Preparación (Recomendado)
El método industrial predeterminado es a través de PyPI para garantizar la integridad de las versiones:

```bash
# Instalar el ecosistema completo (Legacy + Pro + Lite + Omega)
pip install continuity-legacy

# O instalar solo los módulos necesarios:
pip install continuity-lite
pip install continuity-pro
pip install continuity-omega
```

Alternativamente, para desarrolladores del núcleo:
```bash
git clone https://github.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium.git
cd CONTINUITY-LEGACY-by-Ethernium
pip install -e .
```

## 3. 🧬 Enlazando Continuity a un Proyecto
Puedes proteger el "Linaje Lógico" de cualquier proyecto (nuevo o ya empezado) siguiendo estos pasos:

### Escenario A: Proyecto Nuevo
1. Crea el directorio de tu proyecto.
2. Inicializa el sistema Guardian:
```bash
continuity-lite init
```

### Escenario B: Proyecto Existente (Cold Start)
1. Navega a la raíz de tu repositorio actual.
2. Ejecuta la inicialización de alineamiento:
```bash
continuity init
```
3. **Crystallize**: Si el proyecto ya tiene documentación, el sistema detectará un "DNA Drift". Debes cristalizar el estado inicial:
```bash
continuity status --fix
```

## 4. 🛰️ Operación del Sentinel Guardian
Una vez enlazado, el sistema protege cada cambio mediante un bucle de auditoría:

1. **Escritura**: El desarrollador modifica archivos `.md` o `.json`.
2. **Pre-push Audit**: Al intentar hacer `git push`, el hook local de Continuity verifica la integridad del ADN.
3. **Falla de Paridad**: Si el ADN ha derivado (cambios no registrados), el `push` será bloqueado.
4. **Sincronización**: Debes actualizar el `STATE.json` y el badge del `README` usando la herramienta de cristalización antes de enviar:
```powershell
python .github/scripts/crystalize.py
```

## 🛠️ Herramientas de Mantenimiento
Ubicadas en `.github/scripts/`:
- `crystalize.py`: Sincroniza el estado de ADN local con el Merkle Root global.
- `audit_comparison.py`: Analiza bit a bit las discrepancias entre tu máquina y el Industrial Guardian de GitHub.

---
*Continuity Legacy: Protecting the logical lineage of your software.*
