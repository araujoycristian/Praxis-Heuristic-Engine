** Documento guía para el desarrollo:**

---

## **Guía de Referencia de Arquitectura y Desarrollo**
### **Proyecto: Automatización de Facturación Médica**

**Versión:** 10.0 (Final)
**Propósito:** Este documento consolida la visión arquitectónica, las decisiones de diseño y la hoja de ruta técnica del proyecto. Actúa como la única fuente de verdad para alinear al equipo de desarrollo, validar el estado actual del sistema y guiar la implementación de nuevas funcionalidades de manera coherente, robusta y escalable.

### **1. Filosofía y Principios Fundamentales**

La arquitectura y el código se rigen por un conjunto de principios clave para garantizar la mantenibilidad, resiliencia y escalabilidad del sistema:

*   **Separación de Responsabilidades (SoC):** Cada componente tiene una única y bien definida responsabilidad, reduciendo la complejidad y facilitando las modificaciones.
*   **Bajo Acoplamiento, Alta Cohesión:** Los módulos interactúan a través de interfaces estables y abstractas, minimizando las dependencias directas entre ellos.
*   **Inyección de Dependencias (DI):** Los componentes reciben sus dependencias desde un contexto externo en lugar de crearlas internamente, lo que facilita las pruebas, el mocking y la reconfiguración.
*   **Desarrollo Guiado por Configuración:** El comportamiento operativo (ej. criterios de filtrado, valores de validación, palabras clave de diálogos) se externaliza en archivos de configuración (`.ini`), permitiendo ajustes sin modificar el código fuente.
*   **Falla Rápido y de Forma Controlada:** El sistema está diseñado para fallar de manera explícita y temprana ante una condición inesperada, lanzando excepciones personalizadas que proveen información clara para una gestión de errores inteligente y dirigida por eventos.

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

*   **Capa de Interfaz de Usuario:** Punto de entrada para el usuario.
*   **Capa de Orquestación:** El `Orchestrator` actúa como el cerebro, coordinando el flujo entre los pipelines.
*   **Capas de Lógica de Negocio:**
    *   **Data Pipeline:** Responsable de cargar (ej. desde un archivo Excel), filtrar y validar los datos de entrada.
    *   **Automation Pipeline:** Contiene la lógica para interactuar con el sistema externo (SF) vía escritorio remoto.

#### **2.2. Estructura Detallada de Componentes**

La siguiente tabla detalla los componentes clave del sistema, su ubicación y su responsabilidad principal:

| Componente | Ubicación Propuesta | Responsabilidad Principal y Métodos Clave |
| :--- | :--- | :--- |
| **`ConfigValidator`** | `src/core/config_validator.py` | Validar la estructura y el contenido de los perfiles de configuración (`.ini`). |
| **`exceptions.py`** | `src/core/exceptions.py` | Definir la clase base `AutomationError` y un conjunto de excepciones personalizadas para un manejo de errores granular. |
| **`command.py`** | `src/automation/common/command.py` | Definir la interfaz abstracta `Command` con los métodos `execute()` y `undo()`. |
| **`states.py`** | `src/automation/common/states.py` | Definir un `Enum` con los estados lógicos de la Máquina de Estados Finitos (FSM). |
| **`RemoteControlFacade`**| `src/automation/strategies/remote/remote_control.py` | Abstraer las interacciones de bajo nivel con la ventana remota. **Métodos clave:** `ensure_focus()`, `read_clipboard_with_sentinel()`. |
| **`MainWindowHandler`** | `src/automation/strategies/remote/handlers/main_window_handler.py` | Implementar la lógica de negocio atómica para una sección específica de la GUI. Sus métodos devuelven objetos `Command` o lanzan excepciones. |
| **`RemoteAutomator`** | `src/automation/strategies/remote/automator.py` | Orquestar la FSM, gestionar el estado, el historial de comandos y la lógica de recuperación de errores a alto nivel. |

### **3. Estrategia de Automatización y Tácticas de Resiliencia**

#### **3.1. Restricción Fundamental: Interacción "Ciega"**

La estrategia de automatización se basa en controlar una ventana de escritorio remoto que muestra el software a automatizar (SF). Esto impone dos restricciones críticas:

1.  **Interacción "Ciega":** No hay acceso directo a los elementos de la GUI. El control se ejerce exclusivamente mediante el envío de pulsaciones de teclas (`keystrokes`).
2.  **Comunicación Unidireccional:** La única vía para recibir datos desde el SF es a través del portapapeles del sistema operativo.

Estas limitaciones dictan todas las tácticas de percepción, control y validación del estado de la aplicación.

#### **3.2. Tácticas de Interacción y Percepción**

Para operar de forma fiable bajo estas restricciones, se han definido los siguientes patrones y tácticas:

*   **Navegación Relativa por Teclado:** La navegación se basa en secuencias predecibles de pulsaciones de teclas (**`Tab`**, **`Shift+Tab`**, **`Enter`**, atajos) para mover el foco entre los campos de la GUI, partiendo siempre de un estado conocido.
*   **Principio de "Pre-condición de Foco":** Antes de cualquier interacción crítica, se invoca a `remote_control.ensure_focus()`. Si la ventana remota pierde el foco y no se puede recuperar, se lanza `FocusLostError`.
*   **Patrón "Sentinel del Portapapeles":** Para distinguir de forma inequívoca entre un campo vacío y un fallo en la operación de copiado (**`Ctrl+C`**), se implementa el método `read_clipboard_with_sentinel()`, que lanza `ClipboardError` en caso de fallo.
*   **Detección Heurística de Diálogos Modales:** Tras una acción que podría generar un pop-up (ej. pulsar **`Enter`**), se realiza una operación **`Ctrl+C`**. Si el portapapeles contiene texto inesperado (palabras clave definidas en la configuración), se lanza `UnexpectedPopupError`.

### **4. Control de Flujo y Manejo de Errores**

#### **4.1. Máquina de Estados Finitos (FSM) Dirigida por Eventos**

El `RemoteAutomator` implementa una FSM para dirigir el flujo de ejecución. El proceso es una serie de transiciones entre estados bien definidos. Las excepciones personalizadas actúan como los **eventos** que desencadenan estas transiciones, moviendo el flujo hacia estados de recuperación o finalización.

#### **4.2. Excepciones Personalizadas para el Control de Flujo**

Se establece un vocabulario de errores preciso. Todas las excepciones heredan de `AutomationError(Exception)` y son:

*   `ApplicationStateNotReadyError`: La GUI no está en el estado inicial requerido.
*   `PatientIDMismatchError`: El ID del paciente en la GUI no coincide con el esperado.
*   `ClipboardError`: Fallo técnico en la operación de copia/lectura del portapapeles.
*   `UnexpectedPopupError`: Se detectó un diálogo modal inesperado.
*   `FocusLostError`: La ventana de la aplicación remota ha perdido el foco.

#### **4.3. Patrón `Command` para Reversión de Operaciones**

Cada acción que modifica el estado de la GUI se encapsula en un objeto `Command` que implementa `execute()` y `undo()`. Si un paso falla, el `Automator` invoca `undo()` en el historial de comandos para devolver la GUI a un estado limpio y conocido.

### **5. Operabilidad y Robustez del Sistema**

*   **Observabilidad Visual en Fallos:** En caso de una excepción no controlada, el sistema tomará una captura de pantalla del escritorio, guardándola con un nombre informativo (ej. `failure_HC12345_timestamp.png`) para diagnóstico post-mortem.
*   **Prevención de Fallos Silenciosos:** Si el `Data Pipeline` filtra todos los registros de entrada, el `Orchestrator` emitirá una `WARNING` de alta visibilidad.
*   **Reporte de Resumen de Ejecución:** Al finalizar, se generará un archivo de resumen (`resumen_YYYY-MM-DD_HHMMSS.txt`) con estadísticas clave.
*   **Idempotencia y Resumibilidad:** El sistema registrará las tareas completadas en `.progress.log` para omitirlas en ejecuciones posteriores.

### **6. Plan de Implementación: Hito 3**

#### **6.1. Objetivo del Hito**

Automatizar el flujo de trabajo de facturación para un paciente, desde la búsqueda hasta la navegación a la pestaña "Datos de Ingreso", utilizando una Máquina de Estados Finitos (FSM) que implemente todas las tácticas de robustez definidas.

#### **6.2. Flujo de Negocio Detallado**

El flujo para cada tarea individual se ejecutará de la siguiente manera:

1.  **Verificación de Tarea:** Se comprueba el archivo `.progress.log`. Si la tarea actual ya fue completada, se omite.
2.  **Validación de Estado Inicial del SF:** Se asegura que la GUI del SF está en la pantalla y pestaña correctas ("Facturación") y el foco está en el campo "N. de Historia". Si no, se lanza `ApplicationStateNotReadyError`.
3.  **Búsqueda de Paciente:** Se escribe el "N. de Historia" del archivo de datos y se presiona **`Enter`**.
4.  **Detección y Manejo de Diálogos:** Inmediatamente después, se ejecuta la heurística de detección de pop-ups. Si se encuentra uno, se lanza `UnexpectedPopupError`.
5.  **Validación de Carga del Paciente:** Se navega al campo de identificación del paciente y se lee su contenido con el **patrón "Sentinel del Portapapeles"**. Si el valor no coincide con el esperado del archivo de datos, se lanza `PatientIDMismatchError`.
6.  **Inicio de Proceso de Facturación:** Si la validación fue exitosa, se envía el atajo **`Ctrl+N`**.
7.  **Navegación a "Datos de Ingreso":** Se envía el atajo **`Ctrl+T`** dos veces para navegar a la pestaña requerida.
8.  **Finalización de Tarea:** Al llegar al estado objetivo, se registra el éxito en `.progress.log` y se prepara la GUI para la siguiente tarea, asegurando que regresa a su estado inicial.

#### **6.3. Plan de Implementación Técnica por Fases**

##### **Fase 1: Cimientos y Herramientas ("Kit de Supervivencia")**

**Objetivo:** Forjar las herramientas atómicas y reutilizables que la FSM necesitará.

*   **Artefacto 1.1: Vocabulario de Errores (`exceptions.py`)**
    *   **Ubicación:** `src/core/exceptions.py`
    *   **Implementación:** Crear la clase base `AutomationError` y las excepciones específicas detalladas en la sección 4.2.

*   **Artefacto 1.2: El Ojo Fiable (`RemoteControlFacade`)**
    *   **Ubicación:** `src/automation/strategies/remote/remote_control.py`
    *   **Implementación:** Añadir `pyperclip` a `requirements.in`. Crear el método `def read_clipboard_with_sentinel(self) -> str:` que implementa el patrón Sentinel.
        *   **Contrato:** Lanza `ClipboardError` si la copia falla; de lo contrario, devuelve el contenido leído.

*   **Artefacto 1.3: Integración de Herramientas (`MainWindowHandler`)**
    *   **Ubicación:** `src/automation/strategies/remote/handlers/main_window_handler.py`
    *   **Implementación:** Crear `def validate_patient_loaded(self, task) -> None:` que utiliza `read_clipboard_with_sentinel()` y lanza `PatientIDMismatchError` si la validación falla. La excepción `ClipboardError` se deja "burbujear" para ser gestionada centralmente por el `Automator`.

##### **Fase 2: Implementación de Lógica en Handlers**

*   Implementar `ensure_initial_state(self)` en `MainWindowHandler`, aplicando las tácticas de navegación y validación.

##### **Fase 3: Transformación a Máquina de Estados Finitos (FSM)**

*   Crear `src/automation/common/states.py` con un `Enum` para los estados del proceso.
*   Reimplementar `RemoteAutomator` con un bucle `while` controlado por la FSM y bloques `try...except` para gestionar las transiciones de estado basadas en excepciones.

##### **Fase 4: Integración del Flujo Completo**

*   Añadir las transiciones y acciones para los pasos de inicio de facturación y navegación.
*   Al alcanzar "Datos de Ingreso", la FSM debe transitar a un estado que delegue el control a futuros componentes (ej. `AWAITING_INGRESO_HANDLER`).

### **7. Visión Arquitectónica a Largo Plazo**

*   **De Esperas Estáticas a Sondeo Dinámico (Polling):** Las esperas fijas (`time.sleep()`) serán reemplazadas por bucles de sondeo que verifiquen el estado de la GUI antes de proceder.
*   **Testing y Mocking Avanzado:** La arquitectura desacoplada permitirá crear un `MockRemoteControlFacade` para probar la lógica de negocio sin depender de una GUI real, acelerando el ciclo de desarrollo.
*   **Evolución hacia la Estrategia `local`:** Se contempla la futura implementación de una estrategia que se ejecute en la misma máquina que el SF. Gracias a las abstracciones, esto se logrará creando un nuevo conjunto de componentes en `src/automation/strategies/local/` sin impactar el resto del sistema.
