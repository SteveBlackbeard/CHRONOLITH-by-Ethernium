# 🪐 CORE PRO: CONSTITUCIÓN TÁCTICA
**Clasificación**: `ESPECIALIZACIÓN MODULAR INDUSTRIAL`

Esta es la extensión constitucional aplicable única y exclusivamente para la refactorización e interacción con el motor **Chronolith Pro** (`chronolith-pro/`).

Adicional a las 7 Leyes Generales del Protocolo Ethernium Core, este motor responde a las siguientes directrices severas:

### 1. Robustez Industrial Corporativa (Pydantic Enforcement)
El propósito de *Pro* es funcionar como un "Guardia Fronterizo" y validador de datos en el intercambio entre entornos y repositorios humanos robustos. Por tanto:
- Toda estructura de datos de entrada/salida o manipulación en memoria estructurada (JSON, Configs) **tiene la obligación de ser validada y parcheada a través de Modelos Pydantic (v2)**. Si el dato carece de Schema Pydantic validado dinámicamente, se rechaza la inclusión conceptual.

### 2. Telemetría y Experiencia Terminal (Typer/Rich)
Las interfaces de CLI y logs que arroja Pro no son para depuración oscura, son para auditorías empresariales visibles. 
- Todo comando será encapsulado sistemáticamente con la sintaxis rigurosa de `typer`.
- Los flujos de stdout y reportes estarán recubiertos de UI clara, de clase Solemne e Industrial a través del framework `rich` (ej. Paneles, Árboles, Tablas formateadas). 

### 3. Aislamiento Aséptico Direccional
Bajo ninguna circunstancia Pro invocará mecánicas exclusivas de la capa pesada `omega/` a menos que sea a través de inyecciones abstractas autorizadas. Se debe respetar la barrera de desacoplamiento modular en todo momento.

---
*Chronolith: Protecting the logical lineage of your software.*
