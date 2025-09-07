# Bot de Automatización de Facturación Médica

![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)
![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg) <!-- Placeholder: Conectar a CI/CD real -->
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg) <!-- Placeholder: Conectar a CI/CD real -->

## 🚀 Demostración Visual

![Demo del Bot en Acción](docs/demo.gif) <!-- **ACCIÓN REQUERIDA:** Reemplazar con un GIF real del bot interactuando con el SAF o el sistema real. -->

_Un breve GIF mostrando el bot automatizando la entrada de datos en el sistema de facturación._

## 🎯 El Desafío

En el sector de la facturación médica, la entrada manual de datos en sistemas legados o de escritorio es una tarea repetitiva, propensa a errores humanos y que consume una cantidad significativa de tiempo y recursos. Esto no solo ralentiza los procesos administrativos, sino que también puede llevar a discrepancias en la facturación y a una baja eficiencia operativa.

## ✨ La Solución: Automatización Inteligente

Este proyecto presenta un **Bot de Automatización de Procesos (RPA)** diseñado específicamente para abordar este desafío. El bot automatiza de manera inteligente el flujo de trabajo de facturación médica, desde la lectura y validación de datos hasta su inserción precisa en un software de facturación a través de la automatización de la interfaz de usuario (GUI) de un escritorio remoto.

**Beneficios Clave:**
- **Reducción Drástica de Errores:** Elimina la posibilidad de errores tipográficos y de transcripción.
- **Aumento de la Eficiencia:** Procesa grandes volúmenes de datos en una fracción del tiempo que tomaría manualmente.
- **Optimización de Recursos:** Libera al personal para tareas de mayor valor añadido.
- **Resiliencia y Fiabilidad:** Diseñado para ser robusto y manejar interrupciones inesperadas.

## 🏗️ Principios de Arquitectura y Diseño Clave

El diseño de este bot se basa en principios de ingeniería de software robustos para garantizar mantenibilidad, escalabilidad y resiliencia:

-   **Arquitectura Modular y por Capas:** El proyecto está estructurado en capas bien definidas (`data_handler`, `automation`, `core`), promoviendo una clara separación de responsabilidades, bajo acoplamiento y alta cohesión.
-   **Diseño Dirigido por Configuración:** El comportamiento operativo del bot se externaliza en archivos de configuración `.ini`. Esto permite una flexibilidad máxima, adaptando el bot a diferentes casos de uso sin modificar el código fuente.
-   **Inyección de Dependencias (DI):** Los componentes reciben sus dependencias desde un contexto externo, lo que mejora la testabilidad, facilita el mocking y promueve un diseño desacoplado.
-   **Desarrollo Guiado por Simulación (SAF):**
    -   **Desafío:** Depender del software real, remoto y lento para el desarrollo y las pruebas ralentiza el ciclo de vida, impide la automatización en pipelines de CI/CD y dificulta la reproducción de errores.
    -   **Solución:** Se ha desarrollado el **Stunt Action Facsimile (SAF)**, un simulador de GUI local de alta fidelidad. El SAF emula el comportamiento y la interfaz del software real, permitiendo desarrollar y ejecutar pruebas de integración de manera rápida, local y determinista.
-   **Evolución de "Ciego" a "Consciente":**
    -   **Estado Actual:** La interacción se basa en una **Máquina de Estados Finitos (FSM)** que ejecuta secuencias de teclas predefinidas, validando el éxito mediante técnicas como el "Clipboard Sentinel". Esta es una estrategia robusta pero "ciega".
    -   **Visión Futura:** La arquitectura está evolucionando para dotar al bot de un "mapa" explícito de la GUI (`GuiMap`) y un motor de navegación (`Navigator`), permitiéndole saber siempre *dónde* está y moverse con un propósito verificado.

## ⚙️ Características Principales (Estado Actual)

### Automatización y Flujo de Trabajo
-   **Máquina de Estados Finitos (FSM):** Controla el ciclo de vida de cada tarea, proporcionando un control de flujo preciso (búsqueda, validación, llenado, etc.).
-   **Manejo de Errores y Reintentos:** Utiliza una jerarquía de excepciones personalizadas (`PatientIDMismatchError`, `ClipboardError`) con un mecanismo de reintentos configurable para fallos transitorios.
-   **Validación Explícita ("Percepción"):** Implementa el patrón "Clipboard Sentinel" para verificar de manera fiable que los datos correctos se han cargado en la GUI.
-   **Pipeline de Datos Robusto:** Carga, filtra y valida datos de facturación desde archivos Excel (`.xlsx`), asegurando la integridad de la información.
-   **Interacción Cross-Platform con GUI:** Capacidad de controlar aplicaciones de escritorio en Windows (`pywinauto`) y Linux (`xdotool`).

### Desarrollo y Pruebas
-   **Stunt Action Facsimile (SAF) v0.2:** Un simulador de GUI local (basado en Tkinter) que:
    -   Replica la interfaz y el flujo de trabajo del software de facturación real.
    -   Utiliza una arquitectura MVC para una clara separación de estado, vista y lógica.
    -   Permite el desarrollo y la ejecución de pruebas de integración rápidas y fiables sin depender del sistema remoto.
-   **Reporte Detallado de Ejecución:** Genera un resumen (`.txt`) de tareas exitosas/fallidas y un informe de errores (`.xlsx`) para datos de entrada inválidos.

## 💻 Stack Tecnológico

-   **Lenguaje:** Python 3.9+
-   **Automatización GUI:**
    -   `pywinauto` (para Windows)
    -   `xdotool` (para Linux)
-   **Manejo de Datos:**
    -   `pandas`
    -   `openpyxl`
-   **Configuración:** `configparser`
-   **Logging:** Módulo `logging` estándar
-   **Testing:**
    -   `pytest` (framework de pruebas)
    -   `tkinter` (para el simulador SAF)

## 📂 Estructura del Proyecto

```
facturacion_medica_bot/
├── config/                 # Perfiles de configuración (.ini).
├── data/                   # Datos de entrada, salida y ejemplos.
├── docs/                   # Documentación del proyecto (ej. ARCHITECTURE.md).
├── saf/                    # Stunt Action Facsimile (simulador de GUI para pruebas).
├── src/                    # Código fuente principal de la aplicación.
│   ├── automation/         # Lógica de interacción con la GUI remota.
│   ├── core/               # Componentes centrales: orquestador, modelos de datos.
│   ├── data_handler/       # Módulos para cargar y validar datos.
│   ├── ui/                 # Interfaces de usuario (CLI).
│   ├── utils/              # Funciones de utilidad.
│   └── main.py             # Punto de entrada de la aplicación.
├── tests/                  # Pruebas unitarias y de integración.
├── .python-version         # Define la versión de Python para pyenv.
├── pytest.ini              # Configuración de Pytest.
├── requirements.txt        # Dependencias del proyecto.
└── README.md               # Este documento.
```

## 🚀 Guía de Inicio Rápido

### 1. Prerrequisitos
-   **Python 3.9+** (se recomienda `pyenv`).
-   **`pip`** y **`venv`**.
-   **En Linux:** `sudo apt-get install xdotool`.

### 2. Instalación
1.  **Clona el repositorio:** `git clone <URL_DEL_REPOSITORIO>`
2.  **Crea y activa un entorno virtual:**
    ```bash
    python3 -m venv .venv && source .venv/bin/activate
    ```
3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Configuración
Copia un perfil de `config/profiles/` (ej. `dev_nancy.ini`) y ajústalo a tus necesidades, especialmente el `window_title` de la aplicación a automatizar.

## 🏃 Uso

### Ejecutando el Bot
```bash
python src/main.py --profile <nombre_del_perfil> --input-file <ruta_al_excel>
```
**Ejemplo:**
```bash
python src/main.py --profile dev_nancy --input-file data/samples/facturacion_ejemplo.xlsx
```

### Ejecutando el Simulador (SAF)
Para desarrollo y pruebas, puedes ejecutar el simulador de GUI de forma independiente:
```bash
python saf/app.py
```

## ✅ Testing y Calidad de Código

El proyecto utiliza `pytest` para las pruebas. La piedra angular de nuestra estrategia de calidad es el **Stunt Action Facsimile (SAF)**, que nos permite ejecutar pruebas de integración completas en un entorno controlado y predecible. Esto valida el flujo de trabajo de extremo a extremo, desde la lectura de datos hasta la interacción con la GUI simulada, garantizando que la lógica del bot sea correcta antes de desplegarla en el entorno de producción.

Para ejecutar todas las pruebas:
```bash
pytest
```

## 🗺️ Hoja de Ruta Evolutiva: Hacia la Autonomía

El proyecto sigue una hoja de ruta clara para transformar al bot de un simple automatizador a un agente inteligente y resiliente.

### **Hito 5: El Cartógrafo y el Navegante Consciente (En Desarrollo)**
*   **Objetivo:** Eliminar la navegación "ciega" basada en secuencias de teclas fijas.
*   **Componentes Clave:**
    1.  **`GuiMap`:** Un mapa explícito de la topología de la GUI (pestañas, campos, puntos de referencia) externalizado a un archivo de configuración. El bot *aprenderá* la estructura de la aplicación.
    2.  **`Navigator`:** Un motor de navegación que utiliza el `GuiMap` para moverse de forma transaccional y verificada. Sabrá cómo ir del campo A al campo B y confirmará su llegada.
*   **Resultado:** El bot sabrá *dónde* está en todo momento, sentando las bases para una resiliencia sin precedentes.

### **Hito 6: El Agente Resiliente y Autocorregible (Planificado)**
*   **Objetivo:** Dotar al bot de la capacidad de detectar, diagnosticar y recuperarse de interrupciones inesperadas (ej. pop-ups de error, cambios en la GUI).
*   **Componentes Clave:**
    1.  **Léxico de Interrupciones:** El `GuiMap` se ampliará para catalogar anomalías conocidas y sus soluciones (ej. "Si aparece el pop-up 'Error de Conexión', presiona ENTER").
    2.  **Protocolo de Recuperación Jerárquico:** Cuando el `Navigator` falle, activará un protocolo:
        *   Primero, buscará interrupciones conocidas y las resolverá.
        *   Si no hay interrupciones, buscará "puntos de referencia" (`landmarks`) para reorientarse.
*   **Resultado:** Los fallos fatales se convertirán en contratiempos manejables. El bot no solo seguirá instrucciones, sino que se adaptará y autocorregirá.

## 📚 Documentación Detallada

Para una inmersión profunda en la visión arquitectónica, las decisiones de diseño y los patrones de implementación, consulte el documento:

-   **[Guía de Arquitectura y Desarrollo](./docs/ARCHITECTURE.md)**
