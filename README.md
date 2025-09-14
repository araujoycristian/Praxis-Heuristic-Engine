# **Praxis Heuristic Engine**

![Version](https://img.shields.io/badge/Version-0.8.0-orange)
![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue)
![License](https://img.shields.io/badge/License-Apache_2.0-blue)
[![Tests](https://img.shields.io/badge/Tests-Foundation_Ready-brightgreen)](tests/) 
[![Code Style](https://img.shields.io/badge/Code_Style-Black-black)](https://github.com/psf/black)

El `Praxis Heuristic Engine` es un motor de **Robotic Process Automation (RPA)** de alta resiliencia, diseñado para interactuar con software de escritorio Windows heredado, especialmente en entornos remotos. Su nombre refleja su filosofía de diseño: **`Praxis`** (la aplicación de la teoría a la práctica) y **`Heuristic`** (la resolución inteligente de problemas en entornos inciertos).

Aunque su misión inicial valida su capacidad en la facturación médica, su arquitectura es fundamentalmente la de un **motor de automatización genérico, guiado por configuración, capaz de ejecutar diversas "misiones" (workflows de negocio).**

## 🚀 Demostración Visual

![Demo of the Engine in Action](docs/demo.gif)
_El motor en acción, interactuando con el Stunt Action Facsimile (SAF) para procesar un lote de facturas._

---

## 🎯 El Desafío: El Costo Oculto de los Procesos Manuales

> La entrada manual de datos en sistemas heredados es un cuello de botella operativo crítico. Es un proceso repetitivo y de alto riesgo que conduce inevitablemente a:
> -   **Errores Críticos:** Un solo error de transcripción puede causar el rechazo de reclamaciones, retrasando los ingresos durante semanas y exigiendo una costosa reelaboración.
> -   **Potencial Humano Desperdiciado:** Horas de personal cualificado se consumen en tareas de bajo valor en lugar de en la resolución de problemas complejos.
> -   **Escalabilidad Inhibida:** La capacidad de procesamiento está directamente limitada por el número de personas, lo que frena el crecimiento del negocio.

## ✨ La Solución: Un Motor Práctico e Inteligente

Esto no es un simple script de "copiar y pegar". Es un agente de software construido sobre robustos pilares arquitectónicos para garantizar un funcionamiento estable, mantenible y adaptable.

## 🏗️ Principios Arquitectónicos Fundamentales

1.  **Doctrina "Simulation-First":** La calidad y la velocidad del desarrollo se garantizan a través de un gemelo digital (`Stunt Action Facsimile - SAF`), permitiendo un desarrollo desacoplado y una suite de pruebas de integración totalmente automatizada.
2.  **Motor de Workflows Genérico:** La lógica de negocio está diseñada para ser externalizada a "Manifiestos de Misión" declarativos. El motor no está acoplado a un único proceso.
3.  **Manejo de Errores como Flujo de Control:** La lógica del agente es gobernada por una **Máquina de Estados Finitos (FSM)** que, a su vez, es dirigida por una jerarquía de excepciones personalizadas. Los errores no son fallos terminales; son **eventos de negocio** que guían inteligentemente al motor.
4.  **Filosofía de "Caos Afuera, Orden Adentro":** El sistema asume que las fuentes de datos externas son impredecibles. En el punto de entrada, todos los datos son inmediatamente saneados, validados y transformados en **modelos de datos internos inmutables (`dataclasses`)**.
5.  **Comportamiento Guiado por Configuración:** El motor no tiene lógica de negocio codificada. Sus parámetros operativos, mapeos de datos y (en el futuro) su conocimiento del entorno (`GuiMap`) se externalizan a archivos `.ini`. **El motor aprende de su configuración.**
6.  **Experiencia del Desarrollador (DevEx) como Pilar:** El motor está acompañado por un ecosistema de herramientas (`scripts/`) y simuladores (`SAF`) diseñados para hacer que la configuración, las pruebas y la depuración de nuevas misiones sean un proceso rápido, intuitivo y fiable.

---

## 🚀 Guía de Inicio Rápido

### 1. Prerrequisitos

-   **Python 3.11+**
-   **`pip`** y **`venv`** (incluidos con las instalaciones modernas de Python).
-   **En Linux:** `xdotool` es necesario para la interacción con la GUI (`sudo apt-get install xdotool` o equivalente para su distribución).

### 2. Instalación

1.  **Clona el repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd Praxis-Heuristic-Engine
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

---

## 🏃 Uso

Para ejecutar el motor, especifica el perfil de configuración y la ruta al archivo Excel de entrada desde la raíz del proyecto:

```bash
python src/main.py --profile <nombre_de_tu_perfil> --input-file <ruta/a/tu/archivo.xlsx>
```

**Ejemplo (ejecutando contra el simulador SAF):**
```bash
python src/main.py --profile dev_saf --input-file data/samples/facturacion_anonymized.xlsx
```

---

## 🛠️ El Ecosistema DevEx: Nuestra "Planta de Producción"

Más allá del propio agente, el proyecto es un ecosistema completo de herramientas y prácticas diseñadas para acelerar el desarrollo, garantizar la seguridad de los datos y mantener una alta calidad de código.

*   **`Stunt Action Facsimile` (SAF): El Dojo Digital**
    El SAF es la piedra angular de nuestra estrategia de calidad. Es un **gemelo digital** de la aplicación de destino, escrito en `tkinter`, que permite un ciclo de desarrollo y depuración ultrarrápido sin depender de conexiones remotas.

*   **El Taller del Artesano (`scripts/`)**
    Una suite de herramientas de línea de comandos que profesionalizan el flujo de trabajo, incluyendo utilidades para la **anonimización de datos de producción**, la **generación asistida de perfiles de configuración** y el **descubrimiento de ventanas**.

*   **Gestión Profesional de Dependencias**
    El proyecto utiliza `pip-tools` (`requirements.in`/`.txt`) para una gestión de dependencias determinista y segura, garantizando entornos idénticos desde el desarrollo hasta la producción.

---

## ✅ Estrategia de Calidad y Pruebas

Nuestra estrategia de calidad está centrada en nuestra **Doctrina "Simulation-First"**.

En la `v0.8.0`, esto se logra mediante una combinación de:
1.  **Pruebas Unitarias** para la lógica de negocio pura y aislada.
2.  **Validación Manual de Extremo a Extremo (E2E)** contra el SAF.

El siguiente paso inmediato en nuestra hoja de ruta de calidad es **automatizar completamente el ciclo de vida del SAF dentro de nuestra suite de pruebas** (utilizando `fixtures` de `pytest`), lo que habilitará una verdadera Integración Continua (CI/CD) y una red de seguridad contra regresiones.

```bash
# Ejecutar la suite de pruebas actual
pytest
```

## 📂 Estructura del Proyecto
```
Praxis-Heuristic-Engine/
├── config/                 # Perfiles de configuración (.ini) y el futuro GuiMap.
├── data/                   # Datos de entrada, salida, muestras y reportes.
├── docs/                   # La Biblioteca del Proyecto (nuestra fuente de verdad).
├── saf/                    # El Stunt Action Facsimile (nuestro gemelo digital).
├── scripts/                # El Taller del Artesano (herramientas de DevEx).
├── src/                    # El código fuente del motor.
│   ├── automation/         # Lógica de automatización, FSM y futuro motor de navegación.
│   ├── core/               # Orquestador, modelos de datos y excepciones personalizadas.
│   ├── data_handler/       # Pipeline de carga, filtrado y validación de datos.
│   └── main.py             # Punto de entrada de la aplicación.
├── tests/                  # Pruebas unitarias y de integración.
├── requirements.in         # Dependencias abstractas (para pip-tools).
├── requirements.txt        # Dependencias congeladas (generadas).
└── README.md               # Este documento.
```

## 🗺️ El Camino hacia la Autonomía: Nuestra Hoja de Ruta Estratégica

El proyecto está en un camino deliberado para evolucionar de un autómata que sigue secuencias a un agente inteligente con conciencia situacional.

### **Nivel 1: El Aprendiz (Las Reglas del Juego) - Hitos 0 & 1**
*   **Misión:** Desacoplar el motor de un único workflow y enseñarle a validar la lógica de negocio de los datos que procesa.
*   **Resultado:** Un `WorkflowEngine` genérico que lee "Manifiestos de Misión" y un `SanityValidator` que rechaza datos lógicamente absurdos.

### **Nivel 2: El Técnico (Dominio del Entorno Físico) - Hitos 2 & 3**
*   **Misión:** Reemplazar la interacción "ciega" y frágil con un sistema que comprende la estructura de la GUI.
*   **Resultado:** Un `Navigator` que utiliza un `GuiMap` para planificar y **verificar** cada movimiento, y una `PerceptionInterface` que permite añadir nuevos "sentidos" (como OCR) en el futuro.

### **Nivel 3: El Veterano (Manejo del Caos) - Hito 4**
*   **Misión:** Capacitar al motor para manejar lo inesperado.
*   **Resultado:** Un protocolo de recuperación que permite al `Navigator` detectar, diagnosticar y recuperarse de interrupciones (ej. pop-ups), pasando de **fallar ante un error** a **resolverlo activamente**.

## 📚 Biblioteca Completa del Proyecto

Para una inmersión profunda en las decisiones de diseño, los conceptos fundamentales, las guías prácticas y el manual de operaciones, consulte nuestra biblioteca de documentación completa.

-   **[Entrar a la Biblioteca del Praxis Heuristic Engine](./docs/README.md)**

## ⚖️ Licencia
Este proyecto está licenciado bajo la **Licencia Apache 2.0**.
