## **Guía de Arquitectura y Desarrollo: Proyecto de Automatización de Facturación Médica**

**Versión:** 4.5 (Hoja de Ruta Estratégica para Hitos 4.5+)
**Propósito:** Este documento es un **artefacto vivo** que consolida las decisiones de diseño, describe el estado actual de la implementación y, fundamentalmente, traza la **hoja de ruta evolutiva** del proyecto. Su objetivo es guiar el desarrollo de manera coherente, robusta y escalable.

### **1. Filosofía y Principios Fundamentales**

El diseño del sistema se rige por un conjunto de principios que priorizan la resiliencia, la mantenibilidad y la adaptabilidad a largo plazo.

*   **Separación de Responsabilidades (SoC):** Cada componente tiene una única y bien definida responsabilidad (ej. `Loader` carga, `Validator` valida, `Navigator` navega).
*   **Bajo Acoplamiento, Alta Cohesión:** Los módulos interactúan a través de interfaces abstractas y contratos de datos explícitos, minimizando las dependencias directas y permitiendo su evolución independiente.
*   **Inyección de Dependencias (DI):** Los componentes son "ensamblados" en un punto de composición central (`Orchestrator`), lo que facilita las pruebas unitarias, el mocking y la sustitución de implementaciones.
*   **Desarrollo Guiado por Configuración:** El comportamiento operativo y el conocimiento del entorno (títulos de ventana, timeouts, y crucialmente, el mapa de la GUI) se externalizan a archivos `.ini`. El bot **aprende de su configuración**, no se codifica para un solo escenario.
*   **Inmutabilidad y Flujo de Datos Unidireccional:** Los datos de entrada, una vez validados, se transforman en modelos inmutables (`dataclasses(frozen=True)`). Estos objetos fluyen a través del sistema sin ser modificados, garantizando la predictibilidad y eliminando una clase entera de errores por efectos secundarios.
*   **Falla Rápido, Falla Inteligentemente:** Las **excepciones personalizadas** no son meros errores; actúan como **eventos de negocio** que dirigen el flujo de la Máquina de Estados, permitiendo una gestión de errores granular y estratégica (reintentar, abortar, reportar).
*   **Desarrollo Guiado por Simulación:** El desarrollo y las pruebas se desacoplan del entorno de producción real mediante el **Stunt Action Facsimile (SAF)**, un gemelo digital que permite un ciclo de vida de desarrollo rápido y fiable.

### **2. Arquitectura General y Componentes Clave**

El sistema adopta una arquitectura de capas estricta para garantizar una clara separación de responsabilidades:

```
   [ UI (main.py, CLI) ]                    <-- Capa de Interfaz de Usuario
             ↓
   [ Core (Orchestrator) ]                  <-- Capa de Orquestación y Composición
             ↓
   ---------------------------------------------------------------------
   |                                       |                           |
[ Data Pipeline ]     [ Automation Pipeline ]     [ Navigation Engine (FUTURO) ] <-- Capas de Lógica de Negocio
(Loader, Filterer,      (Automator, FSM,            (GuiMap, Navigator,
 Validator)             Handlers)                   FieldInteractor)
```

| Componente Clave | Responsabilidad Principal |
| :--- | :--- |
| **`Orchestrator`** | Cerebro de la aplicación. Ensambla y coordina los pipelines. Genera los reportes finales de ejecución. |
| **`Data Pipeline`** | Ingesta de datos: carga, sanea, filtra y valida los datos de entrada, produciendo `dataclasses` inmutables y limpias. |
| **`RemoteAutomator`** | Orquesta la **Máquina de Estados Finitos (FSM)** que gobierna el ciclo de vida de cada tarea, manejando el flujo, los reintentos y la recuperación de errores. |
| **`Handlers`** | Encapsulan la **lógica de negocio de un workflow específico** (ej. búsqueda de paciente, selección de suministros). Delegan la interacción física a otros componentes. |
| **`RemoteControlFacade`**| **Capa de Abstracción de Hardware (HAL).** Traduce comandos abstractos a acciones del SO (`pywinauto`, `xdotool`), aislando al resto del sistema de la implementación específica de la plataforma. |
| **`Navigator` (Futuro)** | El **GPS** del bot. Utilizará el `GuiMap` para calcular y ejecutar rutas de navegación de forma transaccional y verificada. |
| **`GuiMap` (Futuro)** | El **modelo de datos del mundo**. Una representación en memoria, inmutable y validada, de la topología de la GUI. |

### **3. La Arquitectura de Interacción: Una Evolución Estratégica**

La estrategia de interacción del bot con la GUI ha evolucionado para superar las restricciones del entorno. Comprender esta evolución es clave para entender la hoja de ruta actual.

#### **Fase 1: Interacción Ciega y Robusta (Estado Actual)**

La arquitectura inicial fue diseñada para operar de forma "ciega" en un entorno remoto. Esta restricción forzó un diseño robusto basado en:
1.  **Control Exclusivo por Teclado:** Toda interacción se realiza enviando pulsaciones de teclas.
2.  **Percepción Exclusiva por Portapapeles:** La validación se logra mediante el patrón "Sentinel del Portapapeles" para leer el estado de los campos.
3.  **Navegación Relativa:** El movimiento entre campos se basa en secuencias de teclas predefinidas (ej. `{TAB 2}`).

**Evaluación:** Este enfoque es funcional y resiliente a fallos transitorios (gracias a la FSM y los reintentos), pero su **principal debilidad es la fragilidad**. Un cambio menor en el layout de la GUI (ej. un nuevo campo) puede romper las secuencias de navegación y requerir una caza de errores y una modificación del código.

### **4. Revisión Estratégica y Hoja de Ruta Evolutiva (Post-Hito 4.1)**

Tras la implementación exitosa de la FSM y el sistema de reportes, se ha realizado una revisión estratégica. La conclusión es que para alcanzar el siguiente nivel de autonomía y mantenibilidad, debemos abordar proactivamente la fragilidad de la navegación "ciega".

Se ha definido una hoja de ruta multi-hito diseñada para gestionar el riesgo y la complejidad, transformando al bot de un autómata a un **agente con consciencia situacional**.

---

### **5. Detalle de la Hoja de Ruta**

#### **Hito 4.5: La Fundación del Navegante Consciente (Enfoque Actual)**

*   **Misión Estratégica:** Este hito es una decisión deliberada de **gestión de riesgos** para evitar una refactorización "big bang" del sistema de navegación. Su filosofía es **desacoplar la construcción de la integración**. Construimos y validamos el nuevo motor de navegación de forma completamente aislada, garantizando **cero regresiones** en el sistema existente durante esta fase. Es la construcción y prueba del andamiaje antes de tocar el edificio.
*   **Enfoque Táctico:**
    1.  **Modelado y Carga (Fases 1 y 2):** Se crea y prueba unitariamente la infraestructura para cargar el `GuiMap` desde `config/gui_map.ini`, estableciendo una fuente de verdad del entorno.
    2.  **Validación de Cero Impacto (Fase 3 - Integración Pasiva):** El `GuiMap` se carga en memoria en el `RemoteAutomator` sin ser utilizado. El objetivo de este paso es **probar y garantizar** que el nuevo componente puede coexistir con el sistema actual sin introducir efectos secundarios.
    3.  **Construcción Aislada del Motor (Fase 4):** Se desarrollan y prueban unitariamente los componentes `Navigator` y `FieldInteractor` contra *mocks*. Esto nos permite forjar un motor de navegación robusto y fiable en un entorno de laboratorio controlado, antes de que interactúe con el sistema real.
*   **Resultado Esperado:** Al final de este hito, tendremos un **motor de navegación completo, probado y listo para ser usado**, pero el bot principal seguirá funcionando con su lógica de navegación original. Habremos reducido el riesgo del Hito 5 a casi cero.

#### **Hito 5: El Cartógrafo y el Navegante Consciente (Refactorización y Activación)**

*   **Misión:** Reemplazar por completo la lógica de navegación "ciega" en los `Handlers` con el nuevo motor de navegación construido en el Hito 4.5.
*   **Enfoque Táctico:**
    1.  **Inyección de Dependencias:** El `RemoteAutomator` inyectará la instancia del `FieldInteractor` en todos los `Handlers` relevantes.
    2.  **Refactorización de Handlers:** Se reescribirá el código de los `Handlers` para que dejen de enviar secuencias de teclas y, en su lugar, utilicen la API semántica del `FieldInteractor` (ej. `interactor.write_to('numero_historia', ...)`).
    3.  **Creación del `UIStateVerifier`:** Se implementará el nuevo handler responsable de asegurar el estado inicial, utilizando el `Navigator` para posicionarse y verificar el estado de la GUI de forma explícita.
    4.  **Evolución del SAF (v0.3):** El SAF se actualizará para reflejar la estructura de pestañas y las anomalías de la GUI real, proporcionando un entorno de alta fidelidad para las pruebas de integración.
    5.  **Nuevas Excepciones:** Se introducirá una nueva familia de excepciones (`NavigationError`, `LandmarkNotFoundError`) para comunicar fallos específicos del motor de navegación a la FSM.
*   **Resultado Esperado:** El bot será funcionalmente idéntico al anterior, pero su código interno será drásticamente más simple, legible y **exponencialmente más robusto ante cambios en la GUI**. Toda la lógica de navegación estará centralizada, probada y será reutilizable.

#### **Hito 6: El Agente Resiliente y Autocorregible (Planificado)**

*   **Misión:** Dotar al bot de la capacidad de detectar, diagnosticar y recuperarse de interrupciones inesperadas del entorno, transformando fallos fatales en contratiempos manejables.
*   **Enfoque Táctico:**
    1.  **Léxico de Interrupciones:** El `GuiMap` se ampliará para catalogar anomalías conocidas (ej. pop-ups de error) y sus respectivas acciones de recuperación.
    2.  **Protocolo de Recuperación Jerárquico:** El `Navigator` será mejorado con una lógica que, en caso de fallo de navegación:
        *   **Nivel 1 (Caza de Anomalías):** Buscará activamente interrupciones conocidas y ejecutará su solución.
        *   **Nivel 2 (Reorientación por Landmarks):** Si no hay anomalías, el bot concluirá que está "perdido" e intentará reorientarse buscando un `landmark` conocido.
*   **Resultado Esperado:** El bot pasará de **fallar ante un error** a **intentar resolverlo activamente**. Su fiabilidad para operaciones no supervisadas aumentará significativamente.

### **6. Estrategia de Calidad y Experiencia de Desarrollador (DevEx)**

#### **6.1. Estrategia de Pruebas Jerárquica**

Nuestra estrategia de calidad se basa en una jerarquía de pruebas automatizadas que garantiza la robustez en cada nivel.
*   **Pruebas Unitarias:** Se utilizan para la lógica de negocio pura y aislada (ej. `DataFilterer`, `GuiMapLoader`). Hacen uso extensivo de `pytest-mock` para aislar dependencias y garantizar que cada unidad de código funciona como se espera.
*   **Pruebas de Integración:** Validan la colaboración entre los componentes del sistema. Nuestro enfoque principal es ejecutar el **flujo de automatización completo de extremo a extremo contra el SAF**. Esto nos permite verificar el comportamiento real del bot en un entorno controlado y repetible.
*   **Automatización de Pruebas:** Usamos `fixtures` en `conftest.py` para gestionar el ciclo de vida del SAF (levantarlo antes de las pruebas, derribarlo después), permitiendo que toda la suite de pruebas se ejecute con un solo comando (`pytest`), lo que es ideal para la Integración Continua (CI/CD).

#### **6.2. El Pilar Central: El Stunt Action Facsimile (SAF)**

El SAF es la pieza central de nuestra estrategia de calidad y DevEx. Es un **gemelo digital** de la aplicación real que nos permite:
*   **Desacoplar el Desarrollo:** Permite desarrollar y depurar el 99% de la lógica del bot de forma local y rápida.
*   **Habilitar Pruebas de Integración Automatizadas:** Hace posible ejecutar la suite de pruebas completa en un pipeline de CI/CD.
*   **Simular Escenarios de Falla:** Permite desarrollar y probar la lógica de resiliencia (Hito 6) de forma determinista.

#### **6.3. Ecosistema de Herramientas de Soporte**

El proyecto incluye un conjunto de scripts (`scripts/`) para profesionalizar el flujo de trabajo, incluyendo herramientas para la **anonimización de datos de producción** y la **generación asistida de perfiles de configuración**.

### **7. Visión a Largo Plazo: Hacia un Motor de Workflows Configurable**

La arquitectura actual, con su FSM, y la futura, con el `Navigator` y `GuiMap`, son los cimientos para la visión a largo plazo del proyecto: un **motor de automatización genérico y configurable**.

Una vez maduros, la definición de los "workflows" (las misiones o secuencias de negocio) se podrá abstraer de los `Handlers` de Python y moverse a un formato declarativo (ej. YAML o JSON). El `Automator` simplemente leería un archivo de workflow que define los estados, las acciones (`interactor.write_to(...)`) y las transiciones, permitiendo al mismo bot ejecutar **múltiples procesos de negocio distintos** sin modificar su código base. El Hito 5 es el paso más crítico hacia esta visión.
