# Bot de Automatización de Facturación Médica

![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg) <!-- Placeholder: Conectar a CI/CD real -->
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg) <!-- Placeholder: Conectar a CI/CD real -->

## 🚀 Demostración Visual

![Demo del Bot en Acción](docs/demo.gif) <!-- **ACCIÓN REQUERIDA:** Reemplazar con un GIF real del bot en funcionamiento. -->

_Un breve GIF mostrando el bot automatizando la entrada de datos en el sistema de facturación._

## 🎯 El Desafío

En el sector de la facturación médica, la entrada manual de datos en sistemas legados o de escritorio es una tarea repetitiva, propensa a errores humanos y que consume una cantidad significativa de tiempo y recursos. Esto no solo ralentiza los procesos administrativos, sino que también puede llevar a discrepancias en la facturación y a una baja eficiencia operativa.

## ✨ La Solución: Automatización Inteligente

Este proyecto presenta un **Bot de Automatización de Procesos (RPA)** diseñado específicamente para abordar este desafío. El bot automatiza de manera inteligente el flujo de trabajo de facturación médica, desde la lectura y validación de datos hasta su inserción precisa en un software de facturación a través de la automatización de la interfaz de usuario (GUI) de un escritorio remoto.

**Beneficios Clave:**
- **Reducción Drástica de Errores:** Elimina la posibilidad de errores tipográficos y de transcripción.
- **Aumento de la Eficiencia:** Procesa grandes volúmenes de datos en una fracción del tiempo que tomaría manualmente.
- **Optimización de Recursos:** Libera al personal para tareas de mayor valor añadido.
- **Escalabilidad:** Fácilmente adaptable a diferentes volúmenes de trabajo y configuraciones de sistemas.

## 🏗️ Principios de Arquitectura y Diseño Clave

El diseño de este bot se basa en principios de ingeniería de software robustos para garantizar mantenibilidad, escalabilidad y resiliencia:

-   **Arquitectura Modular y por Capas:** El proyecto está estructurado en capas bien definidas (`data_handler`, `automation`, `core`, `ui`), promoviendo una clara separación de responsabilidades, bajo acoplamiento y alta cohesión. Esto facilita el desarrollo, las pruebas y la evolución independiente de cada componente.
-   **Diseño Dirigido por Configuración:** El comportamiento operativo del bot (ej. criterios de filtrado, mapeo de columnas, valores de validación) se externaliza en archivos de configuración `.ini`. Esto permite una flexibilidad máxima, adaptando el bot a diferentes clientes o casos de uso sin necesidad de modificar o recompilar el código fuente.
-   **Inyección de Dependencias (DI):** Los componentes reciben sus dependencias desde un contexto externo (ej. el `Orchestrator` recibe el `Automator`), lo que mejora la testabilidad, facilita el mocking y promueve un diseño más desacoplado y flexible.
-   **Estrategia de Automatización Resiliente ("Ciega"):**
    -   **Desafío:** La interacción se realiza con una GUI remota sin acceso directo a los elementos internos, dependiendo exclusivamente de pulsaciones de teclas y el portapapeles.
    -   **Solución:** Se emplea un patrón **Facade** (`RemoteControlFacade`) para abstraer las complejidades de la interacción con el sistema operativo subyacente (Windows con `pywinauto`, Linux con `xdotool`), proporcionando una API unificada.
    -   **Robustez y Resiliencia:** Se ha implementado una **Máquina de Estados Finitos (FSM)** que gobierna el ciclo de vida de la automatización. Esta FSM, combinada con un sistema de **excepciones personalizadas**, permite un control de flujo robusto, manejo de errores granular y una lógica de reintentos configurable para fallos recuperables (ej. `ClipboardError`).

## ⚙️ Características Principales (Estado Actual)

-   **Máquina de Estados Finitos (FSM):** El flujo de automatización es controlado por una FSM robusta que gestiona el ciclo de vida de cada tarea, proporcionando un control preciso y estados bien definidos (búsqueda, validación, etc.).
-   **Manejo de Errores y Reintentos:** Utiliza una jerarquía de excepciones personalizadas para identificar errores específicos (`PatientIDMismatchError`, `ClipboardError`). Incluye un mecanismo de reintentos configurable para fallos transitorios.
-   **Validación Explícita ("Percepción"):** Implementa el patrón "Clipboard Sentinel" para verificar de manera fiable que los datos correctos se han cargado en la GUI, eliminando las frágiles esperas de tiempo fijo.
-   **Reporte de Ejecución y Errores:**
    -   Genera un **reporte de resumen** (`.txt`) al final de cada ejecución, detallando las tareas exitosas y fallidas con el motivo del error.
    -   Genera un **informe de errores** (`.xlsx`) para los registros que no cumplen con los criterios de validación inicial, facilitando la depuración de los datos de entrada.
-   **Pipeline de Datos Robusto:** Carga, filtra y valida datos de facturación desde archivos Excel (`.xlsx`), asegurando la integridad de la información antes de la automatización.
-   **Interacción Cross-Platform con GUI:** Capacidad de controlar aplicaciones de escritorio tanto en entornos Windows (utilizando `pywinauto`) como Linux (utilizando `xdotool`).


## 💻 Stack Tecnológico

-   **Lenguaje:** Python 3.9+
-   **Automatización GUI:**
    -   `pywinauto` (para Windows)
    -   `xdotool` (para Linux)
-   **Manejo de Datos:**
    -   `pandas` (para manipulación y análisis de DataFrames)
    -   `openpyxl` (para lectura/escritura de archivos Excel)
-   **Configuración:** `configparser`
-   **Logging:** Módulo `logging` estándar de Python
-   **Testing:** `pytest`

## 📂 Estructura del Proyecto

```
facturacion_medica_bot/
├── config/                 # Perfiles de configuración (.ini) para diferentes escenarios.
│   └── profiles/
├── data/                   # Contiene datos de entrada, salida y ejemplos.
│   ├── input/
│   ├── output/
│   └── samples/
├── docs/                   # Documentación del proyecto, incluyendo la guía de arquitectura.
│   └── ARCHITECTURE.md
├── src/                    # Código fuente principal de la aplicación.
│   ├── automation/         # Lógica de interacción con la GUI remota y estrategias de automatización.
│   │   ├── abc/            # Interfaces abstractas.
│   │   ├── common/         # Utilidades comunes para automatización.
│   │   └── strategies/     # Implementaciones de estrategias (ej. 'remote').
│   ├── core/               # Componentes centrales: orquestador, modelos de datos, constantes.
│   ├── data_handler/       # Módulos para cargar, filtrar y validar datos de entrada.
│   ├── ui/                 # Interfaces de usuario (CLI, GUI).
│   ├── utils/              # Funciones de utilidad generales.
│   ├── config_loader.py    # Carga y gestión de configuraciones.
│   ├── logger_setup.py     # Configuración centralizada del sistema de logging.
│   └── main.py             # Punto de entrada principal de la aplicación.
├── tests/                  # Pruebas unitarias y de integración para asegurar la calidad del código.
├── .python-version         # Define la versión de Python para pyenv.
├── pytest.ini              # Configuración de Pytest.
├── requirements.in         # Dependencias del proyecto (para pip-compile).
├── requirements.txt        # Dependencias instalables (generado desde requirements.in).
└── README.md               # Este documento.
```

## 🚀 Guía de Inicio Rápido

### 1. Prerrequisitos

-   **Python 3.9+** (se recomienda usar `pyenv` o `conda` para gestionar versiones).
-   **`pip`** y **`venv`** (incluidos con Python).
-   **En Linux:** `xdotool` (instalar con `sudo apt-get install xdotool` o equivalente para tu distribución).

### 2. Instalación

1.  **Clona el repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd facturacion_medica_bot
    ```

2.  **Crea y activa un entorno virtual:**
    ```bash
    # Para Linux / macOS
    python3 -m venv .venv
    source .venv/bin/activate

    # Para Windows
    python -m venv .venv
    .\.venv\Scripts\activate
    ```

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Configuración

El comportamiento del bot se controla mediante perfiles de configuración (`.ini`) ubicados en `config/profiles/`.

1.  **Copia un perfil de ejemplo:** Puedes usar `dev_nancy.ini` como base.
    ```bash
    cp config/profiles/dev_nancy.ini config/profiles/mi_perfil.ini
    ```
2.  **Edita tu perfil:** Abre `config/profiles/mi_perfil.ini` y ajusta los parámetros según tus necesidades (ej. `window_title` para el software de facturación, `sheet_name`, `column_mapping`, etc.).

## 🏃 Uso

Para ejecutar el bot, utiliza el script `src/main.py` desde la raíz del proyecto, especificando el nombre del perfil de configuración a usar y la ruta al archivo Excel de entrada.

```bash
python src/main.py --profile <nombre_del_perfil> --input-file <ruta_al_archivo_excel>
```

**Ejemplo:**

```bash
python src/main.py --profile dev_nancy --input-file data/samples/facturacion_ejemplo.xlsx
```

## ✅ Testing y Calidad de Código

El proyecto utiliza `pytest` para su suite de pruebas, asegurando la funcionalidad de los componentes y previniendo regresiones. Se promueve un enfoque de desarrollo guiado por pruebas (TDD) para las nuevas funcionalidades críticas, garantizando la robustez y la fiabilidad del sistema.

Para ejecutar las pruebas:
```bash
pytest
```

## 🗺️ Hoja de Ruta (Roadmap)

El proyecto está en constante evolución. Los próximos pasos clave para mejorar la robustez y la funcionalidad incluyen:

-   **Observabilidad Mejorada:** Integrar capturas de pantalla automáticas en caso de un fallo crítico para facilitar el diagnóstico post-mortem.
-   **Patrón Command para Reversión:** Implementar el patrón `Command` para encapsular cada acción, permitiendo operaciones de `undo` para devolver la GUI a un estado seguro en caso de fallo en flujos complejos.
-   **Sondeo Dinámico de GUI:** Reemplazar las esperas estáticas (`time.sleep()`) por bucles de sondeo que verifiquen el estado real de la GUI antes de proceder, mejorando la fiabilidad.
-   **Idempotencia y Reanudación:** Implementar un log de progreso para poder reanudar ejecuciones interrumpidas sin duplicar trabajo en tareas ya completadas.
-   **Expansión de la Cobertura de Pruebas:** Aumentar la cobertura de pruebas, incluyendo mocking avanzado para simular interacciones con la GUI sin depender de un entorno real.

## 📚 Documentación Detallada

Para una inmersión profunda en la visión arquitectónica, las decisiones de diseño, los patrones de implementación y la hoja de ruta técnica detallada del proyecto, consulte el documento de arquitectura:

-   **[Guía de Arquitectura y Desarrollo](./docs/ARCHITECTURE.md)**
