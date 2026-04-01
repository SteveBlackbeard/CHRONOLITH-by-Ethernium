# CONTINUITY LEGACY por Ethernium

`CONTINUITY LEGACY` es un kit de inicio independiente diseñado para construir proyectos con continuidad persistente, memoria canónica y una transferencia (handoff) repetible entre humanos y operadores de IA.

Este toolkit prioriza la continuidad: proporciona una disciplina reutilizable para la persistencia del contexto, la paridad de documentos y una transferencia gobernada sin depender de marcos de trabajo externos.

## Qué incluye
- una superficie de memoria canónica mínima
- un instantánea de arranque de continuidad (snapshot)
- comprobaciones de paridad de documentos
- comprobaciones de membresía del sistema
- una capa externa opcional para desarrolladores (ej: `PROJECTDEV/`)
- un comando de cierre de continuidad estricto
- un gestor de arranque (bootstrapper) para personalizar la plantilla

## Inicio Rápido

### 1. La Vía "Pro" (CLI) - RECOMENDADO
Instala la interfaz de línea de comandos global para inicializar proyectos en un solo paso:

```powershell
pip install continuity-legacy
continuity-legacy init "Mi Proyecto"
```

### 2. Manual (Copiar/Pegar)
1. Copia esta carpeta en la raíz de tu nuevo proyecto.
2. Ejecuta el gestor de arranque:

```powershell
python tools/continuity_legacy/bootstrap_project.py --repo-root . --project-name "Mi Proyecto" --project-slug mi_proyecto
```

3. Si deseas una capa de continuidad externa:

```powershell
python tools/continuity_legacy/bootstrap_project.py --repo-root . --project-name "Mi Proyecto" --project-slug mi_proyecto --enable-external-docs
```

## Protección Automática (Continuity Guard)
Para asegurar que el proyecto permanezca coherente sin esfuerzo manual, incluye un sistema de seguridad de doble capa:

1. **Guardia Local (`pre-commit`)**: Te avisa de desviaciones o falta de marcadores mientras trabajas, sin bloquear tu flujo creativo.
2. **Guardia de Frontera (`pre-push`)**: Bloquea el `push` a GitHub si el ciclo de continuidad no es 100% válido.

## Archivos Principales
- `PROJECT_CONTEXT.md`
- `STATE.json`
- `ROADMAP.md`
- `.continuity/LIVE_HANDOFF.md`
- `AGENT_START.md` (Qué entregarle a una nueva IA)

---
**Para más detalles, consulta los casos de uso y la guía de solución de problemas en la carpeta raíz.**
