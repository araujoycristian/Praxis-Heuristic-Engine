# 04. Estrategia de Calidad y Pruebas (Estado v0.8.0)

**Misión de este Documento:** Formalizar la estrategia de calidad del `Praxis Heuristic Engine`, estableciendo la Doctrina "Simulation-First" como el pilar central que garantiza la robustez, la fiabilidad y la velocidad del ciclo de desarrollo. Describe el estado de las capacidades de prueba en la `v0.8.0` y define la hoja de ruta para su evolución.

**Audiencia:** Desarrolladores, Arquitectos.

---

## 1. La Doctrina "Simulation-First": Nuestra Respuesta a la Fragilidad del RPA

El desarrollo y las pruebas de automatización de GUI de escritorio son notoriamente difíciles. La dependencia de entornos de ejecución reales, que pueden ser lentos, inestables o no estar disponibles, conduce a ciclos de desarrollo largos y a pruebas "escamosas" (flaky tests) que erosionan la confianza en el sistema.

El `Praxis Heuristic Engine` aborda este desafío fundamental adoptando la **Doctrina "Simulation-First"** como un principio arquitectónico no negociable.

> **La doctrina establece:** "El motor debe ser desarrollado y probado primariamente contra un gemelo digital de alta fidelidad. La interacción con el entorno real es la fase final de despliegue, no el centro del ciclo de desarrollo."

Esta filosofía nos permite construir y validar la lógica del motor en un entorno local, rápido, determinista y totalmente controlado, convirtiendo la calidad de un anhelo a una garantía de ingeniería.

## 2. El Pilar Central: El `Stunt Action Facsimile` (SAF)

El SAF es la encarnación física de nuestra doctrina. No es un simple *mock* o un script de prueba; es un **gemelo digital** de la aplicación de destino, una aplicación de software completa por derecho propio.

### 2.1. Beneficios Estratégicos

El SAF es la ventaja competitiva más significativa del proyecto. Nos proporciona:
*   **Desacoplamiento Total:** Libera el desarrollo de la dependencia del software de facturación real y de las conexiones de escritorio remoto.
*   **Ciclos de Desarrollo Ultra-rápidos:** Permite depurar y probar la lógica del motor en segundos de forma local, en lugar de minutos a través de una conexión remota.
*   **Habilitación de Pruebas de Integración Automatizadas:** Hace posible lo que es casi imposible en el RPA tradicional: una suite de pruebas de integración de extremo a extremo que puede ejecutarse en un entorno de Integración Continua (CI/CD).
*   **Entorno de Falla Controlado:** Permite simular escenarios de error y comportamientos anómalos de la GUI de forma predecible para desarrollar y probar la resiliencia del motor.

### 2.2. Arquitectura del SAF (Versión v0.2)

El SAF es una aplicación `tkinter` bien estructurada que sigue el patrón **Modelo-Vista-Controlador (MVC)**, lo que garantiza su mantenibilidad y extensibilidad.
*   **Modelo (`saf/state/`):** La clase `ApplicationState` gestiona el estado de la simulación, cargando los escenarios desde el archivo `data/test_scenarios.json`. Utiliza modelos de datos explícitos (`PatientData`, `InvoiceData`) para una gestión de estado limpia.
*   **Vista (`saf/ui/`):** Los componentes `MainWindow` y `BillingFormView` construyen la interfaz de usuario con la que interactúa el motor.
*   **Controlador (`saf/handlers/`):** La clase `EventHandlers` contiene la lógica de negocio del simulador, respondiendo a las acciones del motor (ej. `on_enter_pressed`).

### 2.3. Fidelidad y Limitaciones en v0.8.0

Contrario a una suposición inicial, el SAF `v0.2` **no es un simulador puramente optimista**. Sí posee una lógica para simular escenarios de fallo, aunque de forma limitada.

*   **Capacidad Implementada:** La auditoría del código (`saf/handlers/event_handlers.py`) confirma que si se busca un `numero_historia` que no existe en sus escenarios de datos, el SAF responde vaciando los campos del formulario (`self.view.update_patient_details(None)`). Esto simula correctamente el comportamiento de una búsqueda de paciente fallida.
*   **Limitación Real:** La verdadera limitación del SAF en `v0.8.0` no es que no pueda simular fallos, sino la **falta de variedad y de control programático** sobre ellos. Solo simula un tipo de fallo (búsqueda inválida) y no hay una API para que un script de prueba pueda instruir al SAF para que simule otros comportamientos anómalos (ej. un pop-up, un campo deshabilitado, etc.).

## 3. La Jerarquía de Pruebas (Estado v0.8.0)

Nuestra estrategia de pruebas en la `v0.8.0` se compone de dos niveles implementados y una brecha reconocida en el tercero.

### 3.1. Nivel 1: Pruebas Unitarias

*   **Propósito:** Validar la lógica de negocio pura y aislada de funciones y clases que no tienen dependencias externas.
*   **Ejemplo en Código (`tests/utils/test_dataframe_helpers.py`):** Este archivo prueba la función `sanitize_column_name` contra un conjunto diverso de entradas y salidas esperadas, utilizando `@pytest.mark.parametrize` para una cobertura eficiente. Son rápidas, deterministas y forman la base de nuestra pirámide de pruebas.

### 3.2. Nivel 2: Pruebas de Integración de Componentes Aislados

*   **Propósito:** Validar la lógica de colaboración entre un componente y sus dependencias directas, sin ejecutar el sistema completo.
*   **Ejemplo en Código (`tests/automation/strategies/remote/test_automator.py`):** Esta suite de pruebas no interactúa con ninguna GUI. En su lugar, utiliza `pytest-mock` para reemplazar `RemoteControlFacade` y `MainWindowHandler` con dobles de prueba. Su objetivo es validar la lógica interna de la FSM del `RemoteAutomator` (ej. verificar que una excepción genérica realmente invoca a `take_screenshot`).

### 3.3. Brecha en v0.8.0: La Ausencia de Pruebas de Integración E2E Automatizadas

*   **El Objetivo Estratégico:** La razón de ser del SAF es permitir pruebas de integración de extremo a extremo (E2E) totalmente automatizadas.
*   **La Realidad en v0.8.0:** La investigación del código revela que, aunque los componentes existen, **no hay un script de prueba E2E automatizado** en el directorio `tests/`. No existe un `conftest.py` que gestione el ciclo de vida del SAF.
*   **Punto Ciego:** La validación de que todos los componentes del sistema (`ConfigLoader`, `DataPipeline`, `Orchestrator`, `Automator`) funcionan juntos correctamente es, en la `v0.8.0`, un **proceso manual**. Requiere que el desarrollador inicie el SAF en un terminal y ejecute el bot (`main.py`) en otro. Esta brecha es una pieza de deuda técnica reconocida y el principal obstáculo para una verdadera Integración Continua.

## 4. Fronteras Futuras en Calidad (Post-v0.8.0)

Para alcanzar el nivel de profesionalismo al que aspira el `Praxis Heuristic Engine`, la siguiente fase de desarrollo debe abordar directamente las brechas identificadas en este documento.

1.  **Prioridad 1: Automatizar las Pruebas de Integración E2E.**
    *   **Acción:** Crear un archivo `conftest.py` con un `fixture` de `pytest` que gestione el ciclo de vida del SAF (iniciarlo en un subproceso, esperar a que esté listo y terminarlo al final de la sesión de pruebas).
    *   **Acción:** Crear el primer script de prueba E2E (`test_billing_workflow_happy_path.py`) que utilice este `fixture` para validar el flujo completo.

2.  **Prioridad 2: Evolucionar el SAF para Simular Fallos de Forma Programática.**
    *   **Acción:** Refactorizar el SAF para que pueda ser "instruido" por los scripts de prueba para simular escenarios de error (ej. "finge que este paciente no existe", "lanza un pop-up de error"). Esto podría lograrse a través de una simple API o un archivo de configuración de escenario de prueba.

3.  **Prioridad 3: Adoptar un Estándar de Calidad de Código Estático.**
    *   **Acción:** Integrar herramientas como `Black` y `Flake8` en el entorno de desarrollo y en un futuro pipeline de CI para garantizar un código consistente, legible y libre de errores comunes.

---
`[ Volver al Índice de la Biblioteca ]`
