# Chronolith

![Version](https://img.shields.io/badge/version-3.2.0-blue.svg)

Chronolith es una capa de integridad criptográfica para los documentos que transportan la intención de un proyecto entre sesiones asistidas por IA. Convierte tus documentos canónicos en un árbol de Merkle, registra una línea base firmada y falla en cerrado cuando el estado actual deja de coincidir con ella.

No garantiza que una IA "recuerde". Te da un registro verificable de lo que el contexto acordado *era*, y una parada en seco cuando deriva.

## Ediciones

- **Lite**: traspaso local mínimo y comprobaciones de estado firmadas.
- **Pro**: el guardián completo — líneas base firmadas con Ed25519, cadena de transparencia de solo adición, pruebas de inclusión Merkle, cifrado, rotación de claves y anclaje en Bitcoin.
- **Omega**: mapeo cognitivo orientado a RAG y análisis de impacto.

## Instalación

```bash
pip install chronolith
chronolith --help
```

Paquetes individuales:

```bash
pip install chronolith-lite
pip install chronolith-pro
pip install chronolith-omega
```

## Evidencia verificable

Un estado de este proyecto está sellado en el **bloque 958484 de Bitcoin**. No tienes que confiar en este repositorio ni en su autor: compruébalo tú mismo:

```bash
pip install "chronolith-pro[anchor]"
chronolith-pro verify-anchor --proof docs/evidence/ANCHOR_3647dd737ee8.json.ots
```

Lo que demuestra: que esos datos exactos existían antes de que se minara ese bloque. Lo que no demuestra: quién los escribió, ni que sean correctos. Esos límites están documentados, no ocultos.

## Alcance del producto

Chronolith es el runtime en Python y el núcleo de gobernanza. Seneschal es una herramienta separada y extraíble para frugalidad de tokens y concesiones de capacidad firmadas.
