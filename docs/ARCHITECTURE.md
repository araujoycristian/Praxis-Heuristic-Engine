---

### **`ARCHITECTURE.md` (Versión Actualizada)**

---

## **Guía de Referencia de Arquitectura y Desarrollo**
### **Proyecto: Automatización de Facturación Médica**

**Versión:** 2.0 (Post-Hito 3: Implementación de FSM Robusta)
**Propósito:** Este documento es la **fuente de verdad** para la arquitectura del sistema. Consolida las decisiones de diseño, describe el estado actual de la implementación y guía el desarrollo de nuevas funcionalidades de manera coherente, robusta y escalable.

### **1. Filosofía y Principios Fundamentales**

*   **Separación de Responsabilidades (SoC):** Cada componente tiene una única y bien definida responsabilidad.
*   **Bajo Acoplamiento, Alta Cohesión:** Los módulos interactúan a través de interfaces abstractas, minimizando las dependencias directas.
*   **Inyección de Dependencias (DI):** Los componentes reciben sus dependencias (como `RemoteControlFacade` o `ConfigParser`) desde un contexto externo, lo que facilita las pruebas unitarias y el mocking.
*   **Desarrollo Guiado por Configuración:** El comportamiento operativo (títulos de ventana, tiempos de espera, secuencias de teclas) se externaliza a archivos de configuración (`.ini`), permitiendo ajustes sin modificar el código fuente.
*   **Falla Rápido y de Forma Controlada:** El sistema está diseñado para fallar de manera explícita y temprana, lanzando **excepciones personalizadas** que actúan como eventos. Esto permite una gestión de errores inteligente y centralizada en lugar de comprobaciones `if/else` anidadas.

### **2. Arquitectura General de la Solución**

#### **2.1. Arquitectura por Capas**

El sistema adopta una arquitectura de capas estricta:

```
   [ UI (main.py, CLI/GUI) ]              <-- Capa de Interfaz de Usuario
             ↓
   [ Core (Orchestrator) ]                <-- Capa de Orquestación
             ↓
   --------------------------------------
   |                                    |
[ Data Pipeline ]     [ Automation Pipeline ]  <-- Capas de Lógica de Negocio
(Loader, Filterer,      (Automator, Handlers,
 Validator, etc.)       RemoteControl, etc.)
```
*   **Data Pipeline:** Responsable de cargar, filtrar y validar los datos de entrada.
*   **Automation Pipeline:** Contiene la lógica para interactuar con el sistema externo (SF).

#### **2.2. Estructura de Componentes Clave**

| Componente | Ubicación Actual | Responsabilidad Principal y Métodos Clave |
| :--- | :--- | :--- |
| **`exceptions.py`** | `src/core/exceptions.py` | Define `AutomationError` y un conjunto de excepciones personalizadas para un manejo de errores granular y dirigido por eventos. |
| **`states.py`** | `src/automation/common/states.py` | Define un `Enum` (`TaskState`) con los estados lógicos de la Máquina de Estados Finitos (FSM). |
| **`RemoteControlFacade`**| `src/automation/strategies/remote/remote_control.py` | Abstrae las interacciones de bajo nivel con la ventana. **Métodos clave:** `find_and_focus_window()`, `type_keys()`, `read_clipboard_with_sentinel()`. |
| **`MainWindowHandler`** | `src/automation/strategies/remote/handlers/main_window_handler.py` | Implementa la lógica atómica para la ventana principal. **Métodos clave:** `ensure_initial_state()`, `find_patient()`, `validate_patient_loaded()`. |
| **`RemoteAutomator`** | `src/automation/strategies/remote/automator.py` | Orquesta la FSM, gestiona el estado actual y la lógica de reintentos y recuperación de errores a alto nivel. |

### **3. Estrategia de Automatización y Tácticas Implementadas**

#### **3.1. Restricción Fundamental: Interacción "Ciega"**

La estrategia se basa en controlar una ventana de escritorio remoto, lo que impone dos restricciones:
1.  **Control Exclusivo por Teclado:** No hay acceso a los controles de la GUI. Toda interacción se realiza enviando pulsaciones de teclas (`keystrokes`).
2.  **Percepción Exclusiva por Portapapeles:** La única vía para recibir datos desde el SF es a través del portapapeles del sistema operativo.

#### **3.2. Tácticas de Interacción y Percepción**

Para operar de forma fiable bajo estas restricciones, se han implementado los siguientes patrones:

*   **Navegación Relativa por Teclado:** Se utilizan secuencias de teclas predecibles (`Tab`, `Enter`, atajos) para mover el foco entre campos, partiendo de un estado conocido. Estas secuencias, aunque frágiles, están externalizadas en el `handler` y son candidatas a moverse a la configuración.
*   **Principio de "Pre-condición de Foco":** El método `_ensure_focus()` de la `RemoteControlFacade` se invoca antes de cada interacción. Si la ventana pierde el foco y no se puede recuperar, se lanza una `FocusError`.
*   **Patrón "Sentinel del Portapapeles":** El método `read_clipboard_with_sentinel()` distingue de forma inequívoca entre un campo vacío y un fallo de copiado (`Ctrl+C`). Lanza `ClipboardError` si el comando de copia no tuvo efecto, eliminando ambigüedades.

### **4. Control de Flujo y Manejo de Errores: La FSM**

#### **4.1. Máquina de Estados Finitos (FSM) Dirigida por Excepciones**

El `RemoteAutomator` implementa una FSM. En lugar de un script secuencial, el proceso es una serie de transiciones entre estados definidos en `TaskState`. **Las excepciones personalizadas actúan como los eventos** que desencadenan estas transiciones, moviendo el flujo hacia estados de reintento o de fallo controlado.

#### **4.2. Implementación del Hito 3: Búsqueda y Validación Robusta**

El flujo implementado para cada tarea es el siguiente:
1.  **`ENSURING_INITIAL_STATE`:** Se resetea la GUI a un estado conocido (ej. enviando `{ESC}`).
2.  **`FINDING_PATIENT`:**
    *   Se escribe el N.º de Historia y se presiona `Enter`.
    *   Se espera a que el paciente cargue.
    *   Se invoca `validate_patient_loaded()`, que navega al campo de ID y utiliza el **patrón Sentinel** para leer su valor.
3.  **Gestión de Resultados:**
    *   **Éxito:** Si el ID coincide, la FSM transiciona a `INITIATING_NEW_BILLING`.
    *   **Fallo de Datos (`PatientIDMismatchError`):** La FSM transiciona directamente a `TASK_FAILED` (error no reintentable).
    *   **Fallo Técnico (`ClipboardError`, `FocusError`):** La FSM reintenta la operación el número de veces configurado en `max_retries`. Si los reintentos se agotan, transiciona a `TASK_FAILED`.
4.  **`INITIATING_NEW_BILLING`:** Se envía `Ctrl+N` para iniciar la nueva factura.
5.  **`TASK_SUCCESSFUL`:** La FSM alcanza su estado terminal de éxito para este hito y el ciclo de la tarea finaliza.

### **5. Visión Arquitectónica y Próximos Pasos**

Si bien el motor de la FSM es robusto, hay varias áreas clave para la evolución del sistema.

*   **Operabilidad y Diagnóstico:**
    *   **Reporte de Ejecución:** Generar un archivo de resumen (`resumen.txt`) con estadísticas de éxito/fallo.
    *   **Observabilidad Visual:** Tomar una captura de pantalla del escritorio en caso de una excepción crítica no controlada.
    *   **Idempotencia:** Implementar un archivo `.progress.log` para registrar tareas completadas y poder reanudar ejecuciones interrumpidas sin duplicar trabajo.

*   **Refinamiento de la Automatización:**
    *   **Detección de Diálogos Modales:** Implementar la táctica de detección heurística de pop-ups para manejar alertas inesperadas del SF.
    *   **Patrón `Command` para Reversión:** Para flujos más complejos, encapsular cada acción en un objeto `Command` con métodos `execute()` y `undo()`. Esto permitiría revertir una secuencia de pasos de forma segura si uno de ellos falla.
    *   **De Esperas Estáticas a Sondeo Dinámico (Polling):** Reemplazar `time.sleep()` por bucles de sondeo que verifiquen activamente si la GUI está en el estado esperado antes de continuar, o fallar tras un `timeout`.

*   **Testing y Estrategias Futuras:**
    *   **Mocking Avanzado:** Crear un `MockRemoteControlFacade` para probar la lógica de la FSM y los `Handlers` sin depender de una GUI real.
    *   **Estrategia `local`:** Implementar una nueva estrategia en `src/automation/strategies/local/` que interactúe directamente con la GUI del SF si se ejecuta en la misma máquina, aprovechando la `AutomatorInterface` para un cambio transparente.