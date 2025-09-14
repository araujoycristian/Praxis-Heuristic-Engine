# ADR-001: Adopción de un Modelo de Interacción "Ciego" Basado en Teclado y Portapapeles

**Fecha:** 14/09/2025
**Estado:** Aceptado

---

## 1. Contexto

El objetivo de negocio original del proyecto era automatizar un proceso de entrada de datos en una aplicación de escritorio Windows heredada. La restricción principal, y no negociable, era que toda la interacción debía ocurrir a través de una sesión de **Escritorio Remoto**.

Esta restricción invalidó de inmediato las técnicas de automatización de GUI más comunes y robustas, que dependen del acceso directo al sistema de destino para:
*   Inspeccionar la jerarquía de controles de la aplicación (el "DOM" de la aplicación).
*   Interactuar con los elementos de la GUI a través de sus identificadores internos.
*   Suscribirse a eventos de la aplicación.

El desafío, por lo tanto, era diseñar un modelo de interacción que pudiera operar de manera fiable bajo estas condiciones de "caja negra", donde la aplicación de destino es esencialmente una transmisión de vídeo con la que solo se puede interactuar a distancia.

La evidencia de la formalización de esta capa de interacción se puede ver en el commit `32a004b`, que introdujo la primera versión de la `RemoteControlFacade`, sentando las bases para abstraer esta lógica.

---

## 2. Decisión

Se decidió adoptar un modelo de interacción **"ciego"**, basado exclusivamente en los canales de entrada y salida más fundamentales y universales del sistema operativo: el teclado y el portapapeles.

Este modelo se dividió en dos responsabilidades lógicas, ambas encapsuladas dentro de la `RemoteControlFacade`:

1.  **Acción (Las "Manos"):** Toda modificación del estado de la GUI se realizaría a través de la **emulación de teclado a nivel de sistema operativo**. Se eligieron `pywinauto` para Windows y `xdotool` para Linux como las librerías subyacentes, proporcionando una capa de abstracción que permitía al resto del motor enviar secuencias de teclas (ej. texto, `{TAB}`, `{ENTER}`, `^c`) sin conocer los detalles de la plataforma.

2.  **Percepción (Los "Ojos"):** La lectura del estado de la GUI se realizaría utilizando el **portapapeles del sistema como único canal de datos de retorno**. El flujo de percepción consistiría en enviar una secuencia de teclas para seleccionar y copiar el contenido de un campo (`^a^c`) y luego leer el resultado del portapapeles usando la librería `pyperclip`.

La primera implementación funcional de este modelo para una tarea de negocio se materializó en el commit `ad9e6f4`, que implementó la búsqueda y validación de pacientes.

---

## 3. Consecuencias

Esta decisión fue pragmática y fundamental para poner en marcha el proyecto, pero introdujo una serie de consecuencias significativas, tanto positivas como negativas, que han moldeado toda la evolución posterior del motor.

### Positivas:

*   **Viabilidad y Velocidad Inicial:** Este enfoque permitió que el proyecto comenzara a entregar valor de forma extremadamente rápida. La barrera de entrada técnica fue baja y se pudo construir un prototipo funcional en un tiempo récord.
*   **No Intrusivo:** El modelo de interacción no requirió ninguna modificación, instalación o acceso especial en la máquina de destino, más allá del acceso estándar por Escritorio Remoto. Este es un requisito clave en muchos entornos corporativos.
*   **Base Funcional:** Creó una capa de interacción funcional, aunque frágil, sobre la cual se pudieron construir abstracciones de nivel superior más complejas y robustas, como la Máquina de Estados Finitos (ver `ADR-002`).

### Negativas (Introducción de Deuda Técnica y Fragilidad Estructural):

*   **Acoplamiento Fuerte al Layout de la GUI:** La consecuencia más severa. La fiabilidad de la navegación quedó directamente acoplada a la disposición visual y al orden de tabulación de los campos en la GUI. Cualquier cambio menor en la aplicación de destino, como añadir un nuevo campo de texto, podía romper las secuencias de navegación codificadas (ej. `"{TAB 2}"`) y causar un fallo catastrófico.

*   **Fiabilidad Inherente de los Canales:** Se descubrió rápidamente que tanto la acción como la percepción no eran fiables por sí mismas y requerían capas adicionales de resiliencia:
    *   **Percepción Ambigüa:** El uso del portapapeles introdujo una ambigüedad fatal: un portapapeles vacío podía significar un campo vacío o un fallo en la operación de copia. Esto obligó a la creación del patrón **"Sentinel del Portapapeles"** (introducido en el commit `9bfcfe4`) para hacer que la percepción fuera determinista.
    *   **Acción No Atómica:** El envío de secuencias de teclas especiales (`{ENTER}`) demostró ser problemático en la implementación inicial, lo que forzó una refactorización para delegar toda la lógica a la implementación más robusta de `pywinauto.keyboard.send_keys` (commit `b08f8fa`).

*   **El Catalizador para la Evolución:** La suma de estas fragilidades fue la **principal fuerza impulsora** detrás de la hoja de ruta estratégica post-v0.8.0. La necesidad de desacoplar el motor del layout de la GUI es la justificación directa para la concepción del **Hito 3: El Navegante Consciente** (con su `GuiMap` y `Navigator`). Esta decisión, aunque necesaria en su momento, alcanzó el límite de su vida útil y ahora debe ser reemplazada por una arquitectura más consciente y robusta.

---
`[ Volver al Índice de Registros de Decisión ]`
