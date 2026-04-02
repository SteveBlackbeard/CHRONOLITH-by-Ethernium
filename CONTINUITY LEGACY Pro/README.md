# CONTINUITY LEGACY Pro 🏛️

Esta es la versión completa y robusta de **CONTINUITY LEGACY**, diseñada para gestionar la memoria persistente en proyectos de desarrollo de software largos y complejos asistidos por inteligencia artificial.

## ¿Qué incluye la versión Pro?

- **Validación Estricta**: Comprueba la existencia y actualización de todos los documentos fundamentales (paridad documental y pertenencia al sistema).
- **Dashboard Visual**: Un Hub (Página web HTML) para ver de un vistazo el estado de la salud del proyecto.
- **Motor de Reglas**: Evita que tú o tu agente IA rompan reglas del proyecto o dejen tareas a medias escondiendo la deuda técnica.
- **Detector de Secretos**: Impide que se guarden API keys o contraseñas en los documentos de memoria pública.

## Estructura de esta versión

- `/.continuity`: La carpeta donde vive la memoria real, historial de decisiones y registros.
- `/tools/continuity_legacy`: Aquí están los comandos principales que corren la verificación.
- `/outputs`: Informes generados por la máquina en cada ciclo.

## Uso Principal

Para ejecutar el ciclo de seguridad y actualización estricto:

```bash
python tools/continuity_legacy/run_continuity_cycle.py --strict
```

Para abrir el dashboard, simplemente abre en tu navegador:
`continuity_dashboard.html`
