Claro. Procedo a redactar la versión final y verificada del artefacto `docs/1_CORE_CONCEPTS/03_INTERACTION_LAYER.md`, asegurando que su contenido y forma sean precisos, profesionales y estén perfectamente alineados con el estado del código en la `v0.8.0`.

---

# 03. La Capa de Interacción (Estado v0.8.0)

**Misión de este Documento:** Describir la arquitectura y los mecanismos de la capa responsable de la interacción directa con la GUI externa. En la `v0.8.0` del `Praxis Heuristic Engine`, esta capa es el conjunto de **"manos y ojos"** del motor, diseñada para operar de forma fiable en un entorno "ciego" y restrictivo.

**Audiencia:** Desarrolladores, Arquitectos.

---

## 1. Contexto: El Desafío de la "Caja Negra"

La arquitectura de esta capa es una consecuencia directa de la restricción más fundamental del proyecto: la necesidad de operar a través de un **escritorio remoto**. Este entorno trata a la aplicación de destino como una "caja negra", imponiendo dos limitaciones severas:

1.  **Sin Acceso Interno:** Es imposible inspeccionar o interactuar con los controles de la GUI (botones, campos de texto) a través de sus identificadores internos.
2.  **Comunicación Limitada:** El flujo de información entre el motor y la GUI está restringido a los canales más básicos del sistema operativo.

La capa de interacción fue diseñada desde cero para superar estos desafíos, permitiendo al motor operar de manera predecible en un mundo inherentemente impredecible. Para un contexto más profundo sobre esta decisión, consulte [`ADR-001`](../3_DECISION_RECORDS/ADR_001_REMOTE_FIRST_BLIND_INTERACTION.md).

## 2. Arquitectura: La Fachada de Control Remoto

Toda la lógica de interacción de bajo nivel está encapsulada en un único componente: `RemoteControlFacade` (`src/automation/strategies/remote/remote_control.py`).

Este componente actúa como la **Capa de Abstracción de Hardware (HAL)** del motor. Su propósito es traducir los comandos abstractos del resto del sistema en acciones concretas del sistema operativo, aislando al motor de los detalles de implementación de `pywinauto` (para Windows) o `xdotool` (para Linux).

En la `v0.8.0`, esta fachada tiene una **doble responsabilidad crítica**:

*   **Acción (Las Manos):** Ejecuta comandos que modifican el estado de la GUI, principalmente a través de la emulación de teclado (`type_keys`).
*   **Percepción (Los Ojos):** Implementa los mecanismos para leer el estado de la GUI, dependiendo exclusivamente del portapapeles del sistema.

## 3. Mecanismos de Resiliencia Clave

Para operar de forma fiable a pesar de ser "ciego", el motor no confía en la suerte. La `RemoteControlFacade` implementa dos protocolos de resiliencia que son fundamentales para su éxito.

### 3.1. El Principio de "Foco Garantizado"

*   **El Problema:** En un entorno de escritorio, múltiples aplicaciones compiten por la atención. La ventana de destino puede perder el foco en cualquier momento. Enviar una pulsación de tecla a una ventana sin foco es el equivalente a gritar en una habitación vacía.
*   **La Solución:** El método privado `_ensure_focus()` se invoca **antes de cada acción crítica** (`type_keys`, `read_clipboard...`). Este método verifica si la ventana objetivo sigue siendo la ventana activa. Si no lo es, intenta activamente traerla de vuelta al frente antes de proceder. Si no puede recuperar el foco, lanza una `FocusError`, un evento reintentable que la FSM del motor puede gestionar.

Este mecanismo transforma cada interacción de una apuesta a una operación con pre-condiciones validadas.

### 3.2. El Patrón "Sentinel del Portapapeles"

*   **El Problema:** Al usar el portapapeles para "ver", surge una ambigüedad fatal: si después de una operación de copia el portapapeles está vacío, ¿significa que el campo de la GUI estaba realmente vacío o que la operación de copia (`Ctrl+C`) falló por alguna razón (latencia, un pop-up, etc.)?
*   **La Solución:** `read_clipboard_with_sentinel()` implementa un protocolo ingenioso para resolver esta ambigüedad de forma inequívoca.

El flujo del protocolo es el siguiente:

```mermaid
graph TD
    A[Inicio] --> B{1. Copiar un valor 'Sentinel' único al portapapeles};
    B --> C{2. Enviar la secuencia de copia ('^c') a la GUI};
    C --> D{3. Esperar un instante para que la GUI procese};
    D --> E{4. Leer el contenido actual del portapapeles};
    E --> F{5. ¿El contenido es igual al 'Sentinel'?};
    F -- Sí --> G[Error: La copia falló. Lanzar ClipboardError];
    F -- No --> H[Éxito: El contenido es el valor real del campo. Devolver contenido];
```

Este patrón es el pilar de la capacidad de "percepción" del motor en la `v0.8.0`. Elimina las suposiciones y permite al motor tomar decisiones basadas en información verificada.

## 4. El Contrato de Interacción (API v0.8.0)

La siguiente tabla resume los métodos públicos clave que `RemoteControlFacade` ofrece al resto del sistema.

| Método | Propósito | Responsabilidad |
| :--- | :--- | :--- |
| **`find_and_focus_window(title)`**| Localiza la ventana de destino por su título y la activa. Es el punto de entrada de la interacción. | Acción |
| **`type_keys(keys)`** | Envía una secuencia de pulsaciones de teclas a la ventana con foco garantizado. | Acción |
| **`read_clipboard_with_sentinel()`**| Lee el contenido de un campo de la GUI de forma fiable utilizando el protocolo Sentinel. | Percepción |
| **`wait(seconds)`** | Realiza una pausa estática. (Usado con moderación para permitir que la GUI se actualice). | Sincronización |
| **`take_screenshot(file_path)`**| Captura la pantalla completa para diagnóstico en caso de un error inesperado. | Diagnóstico |

## 5. Limitaciones y Deuda Técnica (v0.8.0)

1.  **Acoplamiento de Responsabilidades:** La fachada viola el Principio de Responsabilidad Única al mezclar la lógica de **Acción** y **Percepción**. Esto la hace menos cohesiva y más difícil de mantener o extender.
2.  **Estrategia de Percepción Única:** El motor está completamente acoplado al portapapeles como su único "sentido". Es imposible integrar una estrategia de percepción alternativa (como OCR) sin modificar esta clase fundamental.
3.  **Navegación Externalizada:** La fachada es un ejecutor "tonto". No tiene conocimiento de la estructura de la GUI. La inteligencia para decidir *qué* teclas enviar (ej. `"{TAB 2}"`) reside en los `Handlers`, lo que hace que la lógica de navegación esté dispersa y sea frágil.

## 6. Hoja de Ruta y Evolución

Las limitaciones de esta capa son un impulsor clave de la hoja de ruta estratégica del motor.

*   **Hito 2 (La Abstracción de la Percepción):** Abordará directamente el **Acoplamiento de Responsabilidades** y la **Estrategia de Percepción Única**. Se dividirá la `RemoteControlFacade` en una `ActionFacade` y una `PerceptionInterface`, con `ClipboardPerceptionStrategy` como su primera implementación. Esto creará el "enchufe" para futuras herramientas.
*   **Hito 3 (El Navegante Consciente):** Resolverá el problema de la **Navegación Externalizada**. La inteligencia de movimiento se centralizará en un nuevo componente `Navigator` que planificará las rutas, y la `ActionFacade` volverá a su rol correcto de ser un simple ejecutor de esas órdenes.

---
`[ Anterior: 02. El Pipeline de Datos ]` `[ Índice de Conceptos Fundamentales ]` `[ Siguiente: 04. Estrategia de Calidad y Pruebas ]`
