## **Guía de Arquitectura y Desarrollo: Proyecto de Automatización de Facturación Médica**

**Versión:** 3.0 (Post-Hito 3 y 4.1: FSM y Reporte de Operabilidad)
**Propósito:** Este documento es la **fuente única de verdad** para la arquitectura del sistema. Consolida las decisiones de diseño, describe el estado actual de la implementación y guía el desarrollo de nuevas funcionalidades de manera coherente, robusta y escalable.

### **1. Filosofía y Principios Fundamentales**

*   **Separación de Responsabilidades (SoC):** Cada componente tiene una única y bien definida responsabilidad (ej. `Loader` carga, `Validator` valida, `Automator` automatiza).
*   **Bajo Acoplamiento, Alta Cohesión:** Los módulos interactúan a través de interfaces abstractas (`AutomatorInterface`) y contratos de datos explícitos (`TaskResult`), minimizando las dependencias directas.
*   **Inyección de Dependencias (DI):** Los componentes reciben sus dependencias desde un contexto externo (`Orchestrator` inyecta `ConfigParser` y `RemoteControlFacade` en los `Handlers`), lo que facilita las pruebas unitarias y el mocking.
*   **Desarrollo Guiado por Configuración:** El comportamiento operativo (títulos de ventana, tiempos de espera, secuencias de teclas, número de reintentos) se externaliza a archivos de configuración (`.ini`), permitiendo ajustes sin modificar el código fuente.
*   **Falla Rápido y de Forma Controlada:** El sistema está diseñado para fallar de manera explícita y temprana. Las **excepciones personalizadas** no son solo errores; actúan como **eventos** que dirigen el flujo de la Máquina de Estados, permitiendo una gestión de errores inteligente y centralizada.

### **2. Arquitectura General de la Solución**

#### **2.1. Arquitectura por Capas**

El sistema adopta una arquitectura de capas estricta para garantizar una clara separación de responsabilidades:

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

#### **2.2. Estructura de Componentes Clave (Implementados)**

| Componente | Ubicación | Responsabilidad Principal y Contrato Clave |
| :--- | :--- | :--- |
| **`exceptions.py`** | `src/core/exceptions.py` | Define `AutomationError` y un conjunto de excepciones personalizadas (`PatientIDMismatchError`, etc.) para un manejo de errores granular y dirigido por eventos. |
| **`states.py`** | `src/automation/common/states.py` | Define el `Enum` `TaskState` con los estados lógicos de la Máquina de Estados Finitos (FSM). |
| **`results.py`** | `src/automation/common/results.py`| Define el contrato de datos (`TaskResult`, `TaskResultStatus`) que comunica el resultado de cada tarea desde el `Automator` al `Orchestrator`. |
| **`RemoteControlFacade`**| `src/automation/strategies/remote/remote_control.py` | Abstrae las interacciones de bajo nivel con la ventana. **Métodos clave:** `find_and_focus_window()`, `type_keys()`, `read_clipboard_with_sentinel()`. |
| **`MainWindowHandler`** | `src/automation/strategies/remote/handlers/main_window_handler.py` | Implementa la lógica atómica para la ventana principal. **Métodos clave:** `ensure_initial_state()`, `find_patient()`, `validate_patient_loaded()`. |
| **`RemoteAutomator`** | `src/automation/strategies/remote/automator.py` | Orquesta la FSM, gestiona el estado actual, la lógica de reintentos y la recuperación de errores a alto nivel. **Devuelve:** `List[TaskResult]`. |
| **`Orchestrator`** | `src/core/orchestrator.py` | Coordina los pipelines de datos y automatización. **Responsabilidad clave:** Genera el reporte de resumen final a partir de los `TaskResult` recibidos. |

### **3. Estrategia de Automatización y Tácticas Implementadas**

#### **3.1. Restricción Fundamental: Interacción "Ciega"**

La estrategia se basa en controlar una ventana de escritorio remoto, lo que impone dos restricciones críticas:
1.  **Control Exclusivo por Teclado:** No hay acceso a los controles de la GUI. Toda interacción se realiza enviando pulsaciones de teclas (`keystrokes`).
2.  **Percepción Exclusiva por Portapapeles:** La única vía para recibir datos desde el SF es a través del portapapeles del sistema operativo.

#### **3.2. Tácticas de Interacción y Percepción**

Para operar de forma fiable bajo estas restricciones, se han implementado los siguientes patrones:

*   **Navegación Relativa por Teclado:** Se utilizan secuencias de teclas (`{TAB 2}`, `{ESC 3}`) para mover el foco entre campos. Aunque funcionales, estas secuencias son frágiles y candidatas a ser externalizadas a la configuración en el futuro.
*   **Principio de "Pre-condición de Foco":** El método `_ensure_focus()` de la `RemoteControlFacade` se invoca antes de cada interacción crítica. Si la ventana pierde el foco y no se puede recuperar, se lanza una `FocusError`.
*   **Patrón "Sentinel del Portapapeles":** El método `read_clipboard_with_sentinel()` distingue de forma inequívoca entre un campo de la GUI vacío y un fallo en la operación de copiado (`Ctrl+C`). Lanza `ClipboardError` si el comando de copia no tuvo efecto, eliminando ambigüedades.

### **4. Control de Flujo: La Máquina de Estados Finitos (FSM)**

#### **4.1. FSM Dirigida por Excepciones**

El `RemoteAutomator` implementa una FSM. En lugar de un script secuencial, el proceso para cada tarea es una serie de transiciones entre estados definidos en `TaskState`. **Las excepciones personalizadas actúan como los eventos** que desencadenan estas transiciones, moviendo el flujo hacia estados de reintento o de fallo controlado.

#### **4.2. Flujo de Búsqueda y Validación (Hito 3 Implementado)**

1.  **`ENSURING_INITIAL_STATE`:** Se resetea la GUI a un estado conocido.
2.  **`FINDING_PATIENT`:** Se busca al paciente y se invoca `validate_patient_loaded()`.
3.  **Gestión de Resultados de la Validación:**
    *   **Éxito:** Si el ID coincide, la FSM transiciona a `INITIATING_NEW_BILLING`.
    *   **Fallo de Datos (`PatientIDMismatchError`):** La FSM transiciona a `TASK_FAILED` (error irrecuperable).
    *   **Fallo Técnico (`ClipboardError`, `FocusError`):** La FSM reintenta la operación el número de veces configurado. Si los reintentos se agotan, transiciona a `TASK_FAILED`.
4.  **`TASK_SUCCESSFUL`:** Tras el último paso exitoso, la FSM alcanza su estado terminal y el `Automator` genera un `TaskResult` de éxito.

### **5. Operabilidad y Resiliencia**

#### **5.1. Características Implementadas (Hito 4.1)**

*   **Reporte de Resumen de Ejecución:** Al finalizar, el `Orchestrator` genera un archivo `summary_YYYYMMDD_HHMMSS.txt` en `data/output/reports/`. Este informe contiene estadísticas clave (tareas totales, exitosas, fallidas) y una lista detallada de los fallos, incluyendo el identificador de la tarea, el estado en que falló y el mensaje de error.

#### **5.2. Próximos Pasos y Hoja de Ruta**

*   **Mini-Hito 4.2: Observabilidad Visual en Fallos:** Implementar una "caja negra". Tomar una captura de pantalla del escritorio en caso de una excepción crítica e inesperada (`Exception` genérica) para facilitar el diagnóstico post-mortem.
*   **Mini-Hito 4.3: Idempotencia y Resumibilidad:** Implementar un "marcapáginas" (`.progress.log`) para registrar tareas completadas y poder reanudar ejecuciones interrumpidas sin duplicar trabajo.

*   **Visión a Futuro (Post-Hito 4):**
    *   **Patrón `Command` para Reversión:** Para flujos más complejos (ej. facturación en múltiples pestañas), encapsular cada acción en un objeto `Command` con métodos `execute()` y `undo()`. Esto permitiría revertir una secuencia de pasos de forma segura si uno de ellos falla.
    *   **De Esperas Estáticas a Sondeo Dinámico (Polling):** Reemplazar las últimas esperas fijas (`time.sleep()`) por bucles de sondeo que verifiquen activamente si la GUI está en el estado esperado antes de continuar.
    *   **Detección Heurística de Diálogos Modales:** Implementar una táctica para detectar pop-ups inesperados y manejarlos de forma controlada.

### **6. Calidad de Código y Evolución de la Arquitectura**

Esta sección describe las prácticas y los objetivos a corto y largo plazo para asegurar la calidad del código, facilitar el desarrollo y guiar la evolución sostenible de la arquitectura del proyecto.

*   **Estrategia de Pruebas y Mocking (Objetivo a Corto Plazo):**
    Nuestra arquitectura, basada en Inyección de Dependencias (DI), está diseñada para ser **altamente testeable**. El próximo paso clave en la madurez del proyecto es construir una suite de pruebas robusta que no dependa de una GUI real.
    *   **Plan de Acción:**
        1.  Crear un `MockRemoteControlFacade` que simule el comportamiento de la `RemoteControlFacade` real. Este mock podrá ser instruido para devolver valores específicos o lanzar excepciones (`PatientIDMismatchError`, `ClipboardError`) bajo demanda.
        2.  Implementar **pruebas unitarias** para los `Handlers` (ej. `MainWindowHandler`), verificando que llaman a los métodos correctos de la fachada con los parámetros esperados.
        3.  Implementar **pruebas de integración** para el `RemoteAutomator`, validando que la lógica de la FSM transiciona correctamente entre estados al recibir las excepciones simuladas desde el mock.
    *   **Beneficio:** Acelerar drásticamente el ciclo de desarrollo y depuración, permitiendo validar la lógica de la FSM sin necesidad de ejecutar el bot contra la aplicación real.

*   **Automatización del Desarrollo (CI/CD):**
    Para formalizar nuestro compromiso con la calidad, se planea implementar un pipeline de Integración Continua (CI) utilizando herramientas como GitHub Actions.
    *   **Propósito:** Automatizar la ejecución de la suite de pruebas y de linters (como `flake8` o `black`) en cada `push` al repositorio.
    *   **Beneficio:** Garantizar la estabilidad del código, prevenir regresiones de forma temprana y mantener un estilo de código consistente en todo el proyecto.

*   **Visión a Largo Plazo: Hacia un Motor de Automatización Configurable:**
    Actualmente, la FSM dentro del `RemoteAutomator` está diseñada específicamente para el flujo de trabajo de facturación. Una vez que este flujo esté completamente maduro y probado, la visión a largo plazo es evolucionar el `Automator` hacia un motor más genérico.
    *   **Concepto:** Abstraer la definición del flujo de trabajo (los estados, las acciones y las transiciones) fuera del código Python, moviéndola a un formato de configuración como **YAML o JSON**.
    *   **Ejemplo:** Un archivo YAML podría definir que desde el estado `FINDING_PATIENT`, una acción `validate_id` exitosa lleva al estado `INITIATING_BILLING`, mientras que una excepción `ID_MISMATCH` lleva al estado `TASK_FAILED`.
    *   **Beneficio:** Permitiría que el mismo bot automatizara **múltiples procesos de negocio distintos** dentro del mismo SF, simplemente cargando un archivo de definición de flujo diferente, sin necesidad de modificar la lógica central del `RemoteAutomator`. Esto representa la máxima expresión del principio de "Desarrollo Guiado por Configuración".