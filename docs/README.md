# Biblioteca de Documentación del Praxis Heuristic Engine

¡Bienvenida a la biblioteca del `Praxis Heuristic Engine`!

Este directorio es la **fuente única de verdad (Single Source of Truth)** para todo el conocimiento técnico, de diseño y operativo del motor. Es una **biblioteca viva**, diseñada para evolucionar junto con el software, asegurando que nuestra comprensión colectiva se mantenga tan robusta como nuestro código.

La documentación está organizada intencionadamente para diferentes audiencias. Para ayudarte a navegar por ella de la manera más eficiente posible, hemos creado una serie de recorridos sugeridos.

---

## ¿Quién Eres? Recorridos Sugeridos

Para evitar que te sientas abrumada, encuentra tu rol a continuación y sigue la ruta de aprendizaje que hemos diseñado para ti.

### Si eres una Nueva Desarrolladora...
**Tu objetivo:** Llevarte de cero a tu primera contribución de código, entendiendo no solo el "qué" sino el "porqué" de nuestra forma de trabajar.

| Paso | Documento | Propósito |
| :--- | :--- | :--- |
| **1** | [`01_SETTING_UP_AND_RUNNING.md`](./2_HOW_TO_GUIDES/01_SETTING_UP_AND_RUNNING.md) | **Construye tu taller.** Te guiará para configurar tu entorno y ejecutar el motor en menos de 30 minutos. |
| **2** | [`04_TESTING_AND_QUALITY.md`](./1_CORE_CONCEPTS/04_TESTING_AND_QUALITY.md) | **Domina nuestra filosofía de calidad.** Entiende la Doctrina "Simulation-First" y el rol vital del SAF. |
| **3** | [`ARCHITECTURE.md`](./ARCHITECTURE.md) | **Obtén la visión de 30,000 pies.** Comprende el estado actual, las limitaciones y la visión estratégica del motor. |
| **4** | [`02_DEV_ECOSYSTEM_TOOLCHAIN.md`](./2_HOW_TO_GUIDES/02_DEV_ECOSYSTEM_TOOLCHAIN.md) | **Afila tus herramientas.** Aprende a usar el ecosistema de scripts que acelerará tu desarrollo. |

### Si eres una Arquitecta o Desarrolladora Senior...
**Tu objetivo:** Proporcionarte el contexto estratégico y las decisiones de diseño fundamentales que definen el motor.

| Paso | Documento | Propósito |
| :--- | :--- | :--- |
| **1** | [`ARCHITECTURE.md`](./ARCHITECTURE.md) | **Empieza con la visión estratégica.** Entiende dónde estamos y hacia dónde vamos. |
| **2** | `Serie de Registros de Decisión` | **Comprende el "porqué".** Sumérgete en los ADRs para entender las decisiones clave que nos trajeron hasta aquí. |
| | [`ADR_001`](./3_DECISION_RECORDS/ADR_001_REMOTE_FIRST_BLIND_INTERACTION.md) | La decisión de la interacción "ciega". |
| | [`ADR_002`](./3_DECISION_RECORDS/ADR_002_FINITE_STATE_MACHINE_FOR_RESILIENCE.md) | La adopción de la FSM para la resiliencia. |
| | [`ADR_003`](./3_DECISION_RECORDS/ADR_003_ADOPTING_SIMULATION_FIRST_WITH_SAF.md) | El pivote hacia la doctrina "Simulation-First". |
| | [`ADR_004`](./3_DECISION_RECORDS/ADR_004_CONFIGURATION_FORMAT_CHOICE.md) | La elección pragmática del formato `.ini`. |
| **3** | [`01_WORKFLOW_ENGINE.md`](./1_CORE_CONCEPTS/01_WORKFLOW_ENGINE.md) | **Analiza el corazón del motor.** Estudia la implementación de la FSM y su acoplamiento actual. |

### Si eres una Operadora de Negocio...
**Tu objetivo:** Empoderarte para usar el motor de forma autónoma, segura y eficaz en tus tareas diarias.

| Paso | Documento | Propósito |
| :--- | :--- | :--- |
| **1** | [`01_OPERATOR_GUIDE.md`](./4_USER_MANUAL/01_OPERATOR_GUIDE.md) | **Tu manual de operaciones completo.** Te enseña a preparar datos, ejecutar el motor e interpretar los resultados. |
| **2** | [`05_DATA_CONTRACT.md`](./1_CORE_CONCEPTS/05_DATA_CONTRACT.md) | **Tu referencia técnica.** Consulta este documento para entender en detalle los requisitos de cada columna de tu Excel. |

### Si eres una Ingeniera de DevOps o Administradora de Sistemas...
**Tu objetivo:** Darte la información necesaria para desplegar, configurar, asegurar y mantener el motor en cualquier entorno.

| Paso | Documento | Propósito |
| :--- | :--- | :--- |
| **1. Urgente** | [`06_OPERATIONAL_ENVIRONMENT.md`](./1_CORE_CONCEPTS/06_OPERATIONAL_ENVIRONMENT.md) | **Tu guía de operaciones técnicas.** Detalla la configuración, gestión de secretos y dependencias. |
| **2. Contexto**| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | **La visión general del sistema.** Te proporciona el contexto arquitectónico del motor que vas a desplegar. |

---

## Índice Completo de la Biblioteca

Para una referencia directa, aquí está el catálogo completo de toda la documentación disponible para la `v0.8.0`.

### Documento Maestro
*   **[`ARCHITECTURE.md`](./ARCHITECTURE.md)**: La estrella polar del proyecto. Describe la filosofía, la arquitectura `v0.8.0`, sus limitaciones y la hoja de ruta estratégica.
    *   _Audiencia: Todos_

### 1. Conceptos Fundamentales (`1_CORE_CONCEPTS/`)
*   **[`01_WORKFLOW_ENGINE.md`](./1_CORE_CONCEPTS/01_WORKFLOW_ENGINE.md)**: Explica el cerebro del motor, la FSM, y su acoplamiento al workflow en `v0.8.0`.
    *   _Audiencia: Desarrolladores, Arquitectos_
*   **[`02_DATA_PIPELINE.md`](./1_CORE_CONCEPTS/02_DATA_PIPELINE.md)**: Detalla el viaje de los datos, desde el caos externo hasta el núcleo inmutable y seguro del motor.
    *   _Audiencia: Desarrolladores_
*   **[`03_INTERACTION_LAYER.md`](./1_CORE_CONCEPTS/03_INTERACTION_LAYER.md)**: Describe la capa de interacción "ciega", sus mecanismos de resiliencia y sus limitaciones.
    *   _Audiencia: Desarrolladores_
*   **[`04_TESTING_AND_QUALITY.md`](./1_CORE_CONCEPTS/04_TESTING_AND_QUALITY.md)**: Formaliza nuestra Doctrina "Simulation-First" y la estrategia de calidad.
    *   _Audiencia: Desarrolladores, Arquitectos_
*   **[`05_DATA_CONTRACT.md`](./1_CORE_CONCEPTS/05_DATA_CONTRACT.md)**: La especificación formal de los datos de entrada, el puente entre el negocio y la tecnología.
    *   _Audiencia: Desarrolladores, Operadores de Negocio_
*   **[`06_OPERATIONAL_ENVIRONMENT.md`](./1_CORE_CONCEPTS/06_OPERATIONAL_ENVIRONMENT.md)**: Guía técnica para la configuración, seguridad y gestión de dependencias del motor.
    *   _Audiencia: Desarrolladores, DevOps, Administradores de Sistemas_

### 2. Guías Prácticas (`2_HOW_TO_GUIDES/`)
*   **[`01_SETTING_UP_AND_RUNNING.md`](./2_HOW_TO_GUIDES/01_SETTING_UP_AND_RUNNING.md)**: Tutorial de instalación y primera ejecución del motor contra el SAF.
    *   _Audiencia: Desarrolladores_
*   **[`02_DEV_ECOSYSTEM_TOOLCHAIN.md`](./2_HOW_TO_GUIDES/02_DEV_ECOSYSTEM_TOOLCHAIN.md)**: Manual de uso para el conjunto de herramientas de soporte en la carpeta `scripts/`.
    *   _Audiencia: Desarrolladores_

### 3. Registros de Decisión (`3_DECISION_RECORDS/`)
*   **[`ADR_001_...`](./3_DECISION_RECORDS/ADR_001_REMOTE_FIRST_BLIND_INTERACTION.md)**: Explica el "porqué" de la adopción del modelo de interacción "ciego".
*   **[`ADR_002_...`](./3_DECISION_RECORDS/ADR_002_FINITE_STATE_MACHINE_FOR_RESILIENCE.md)**: Documenta la decisión de usar una FSM para la resiliencia del motor.
*   **[`ADR_003_...`](./3_DECISION_RECORDS/ADR_003_ADOPTING_SIMULATION_FIRST_WITH_SAF.md)**: Registra el pivote estratégico hacia la Doctrina "Simulation-First".
*   **[`ADR_004_...`](./3_DECISION_RECORDS/ADR_004_CONFIGURATION_FORMAT_CHOICE.md)**: Detalla el trade-off pragmático de elegir el formato `.ini` para la configuración.
    *   _Audiencia de todos los ADRs: Arquitectos, Desarrolladores (actuales y futuros)_

### 4. Manual de Usuario (`4_USER_MANUAL/`)
*   **[`01_OPERATOR_GUIDE.md`](./4_USER_MANUAL/01_OPERATOR_GUIDE.md)**: El manual de operaciones completo para el usuario final no técnico.
    *   _Audiencia: Operadores de Negocio_

---

## Cómo Contribuir a esta Biblioteca

*   **La Documentación es Código:** Tratamos esta biblioteca con el mismo rigor que el código fuente. Se versiona, se revisa y se mantiene.
*   **Las Decisiones se Inmortalizan:** Si una decisión de diseño es lo suficientemente importante como para debatirla, es lo suficientemente importante como para documentarla en un nuevo Registro de Decisión Arquitectónica (ADR).
*   **El Flujo es a través de Pull Requests:** Todos los cambios y nuevas adiciones a la documentación deben pasar por el mismo proceso de revisión de Pull Requests que el código del motor.

---
`[ Volver al README Principal del Proyecto](../README.md) ]` &nbsp;&nbsp;&nbsp; `[ Volver al Inicio de este Documento ]`
