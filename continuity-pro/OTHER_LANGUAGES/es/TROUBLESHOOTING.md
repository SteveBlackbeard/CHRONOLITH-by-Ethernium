# CONTINUITY LEGACY: Guía de Solución de Problemas (Troubleshooting) 🛠️

¿Algo no cuadra? No entres en pánico. Aquí tienes las soluciones a los problemas más comunes de continuidad.

---

## 1. El ciclo de paridad falla (`doc_parity_check`) ✘

*   **Problema**: Recibes un error de "Document parity drift" indicando que faltan marcadores obligatorios.
*   **Causa**: Editaste un archivo (ej: README o Handoff) y borraste accidentalmente una línea que el sistema monitoriza para asegurar la coherencia.
*   **Solución**:
    1.  Revisa el reporte en `outputs/continuity/continuity_cycle_report.json` para ver qué "required_string" falta.
    2.  Añade el marcador de paridad de nuevo en el documento.
    3.  Vuelve a ejecutar `python tools/continuity_legacy/run_continuity_cycle.py`.

---

## 2. El Git Hook bloquea mi commit o push 🛡️

*   **Problema**: Git no te deja guardar o subir cambios.
*   **Causa**: Estás en modo estricto (`--strict`) y tu `STATE.json` no coincide con el estado real de los archivos.
*   **Solución**:
    1.  Ejecuta `python tools/continuity_legacy/continuity_status.py` para ver el Dashboard de salud.
    2.  Sincroniza el estado usando `python tools/continuity_legacy/run_continuity_cycle.py`.
    3.  Si es una emergencia, puedes usar `git commit -m "msg" --no-verify` (¡No recomendado!).

---

## 3. Mi agente de IA parece "perdido" o ignora el contexto 🤖

*   **Problema**: La IA empieza a inventar cosas o no sabe dónde se quedó la sesión anterior.
*   **Causa**: No has entregado el paquete de inicio canónico o el `LIVE_HANDOFF.md` está vacío/desfasado.
*   **Solución**:
    1.  Asegúrate de entregar el archivo **`AGENT_START.md`** al principio de la sesión.
    2.  Usa `python tools/continuity_legacy/continuity_suggest.py` para generar un buen resumen de lo que ha pasado y dárselo a la IA.
    3.  Pídele a la IA: *"Reconstruye tu estado actual leyendo el STATE.json raíz y dime cuál es tu Siguiente Acción Exacta (Next Exact Action)"*.

---

## 4. Error de "Security Warning" al iniciar ⚠️

*   **Problema**: Los scripts de Python lanzan un error de seguridad al intentar resolver la ruta raíz.
*   **Causa**: Estás intentando ejecutar los scripts fuera de un repositorio válido de **CONTINUITY LEGACY**.
*   **Solución**:
    1.  Asegúrate de estar en la raíz del proyecto.
    2.  Comprueba que existe el archivo `continuity_legacy.json` o la carpeta `.continuity`.
    3.  Si copiaste el proyecto manualmente, asegúrate de ejecutar `bootstrap_project.py` primero.

---

## 5. El Dashboard (`continuity_status`) muestra "Unknown" o "Skipped" ❓

*   **Problema**: Alguna sección del sistema de salud no muestra datos.
*   **Causa**: No has completado un ciclo completo de continuidad o la función "External Docs" está desactivada.
*   **Solución**:
    1.  Ejecuta el ciclo: `python tools/continuity_legacy/run_continuity_cycle.py`.
    2.  Si usas una carpeta externa (ej: `MYPROJECTDEV`), asegúrate de haberla habilitado en el bootstrap con `--enable-external-docs`.
