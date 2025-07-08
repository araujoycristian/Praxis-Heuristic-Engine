# Bot de Automatización de Facturación Médica

Este proyecto es un bot de software diseñado para automatizar el proceso de facturación médica. Su objetivo es leer datos de pacientes desde un archivo Excel, validarlos según reglas de negocio configurables y, finalmente, introducirlos en un software de facturación a través de la automatización de una interfaz de escritorio remoto.

## Características Principales

- **Carga de Datos desde Excel:** Lee los datos de facturación desde archivos `.xlsx`.
- **Procesamiento Basado en Perfiles:** Utiliza archivos de configuración (`.ini`) para adaptar el comportamiento del bot a diferentes clientes o casos de uso sin modificar el código.
- **Validación de Datos:** Comprueba la integridad y el formato de los datos de entrada antes de procesarlos.
- **Filtrado Dinámico:** Permite filtrar los registros del archivo de entrada según los criterios definidos en el perfil.
- **Automatización de GUI:** Controla aplicaciones de escritorio en Windows (usando `pywinauto`) y Linux (usando `xdotool`) para simular la entrada de datos manual.
- **Generación de Reportes:** Exporta un informe de los registros que no pasaron la validación.

## Estructura del Proyecto

```
facturacion_medica_bot/
├── config/             # Contiene los perfiles de configuración (.ini)
├── data/               # Almacena datos de entrada, salida y ejemplos
├── docs/               # Documentación del proyecto (como este README y la guía de arquitectura)
├── src/                # Código fuente principal de la aplicación
│   ├── automation/     # Lógica de interacción con la GUI remota
│   ├── core/           # Componentes centrales (orquestador, modelos)
│   ├── data_handler/   # Módulos para cargar, filtrar y validar datos
│   └── main.py         # Punto de entrada de la aplicación
├── tests/              # Pruebas unitarias y de integración
└── requirements.txt    # Dependencias de Python
```

## Guía de Inicio Rápido

### 1. Prerrequisitos

- Python 3.9 o superior.
- `pip` y `venv`.
- En Linux: `xdotool` (`sudo apt-get install xdotool`).

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

El comportamiento del bot se controla mediante perfiles ubicados en `config/profiles/`.

1.  Copia el perfil de ejemplo: `cp config/profiles/dev_nancy.ini config/profiles/mi_perfil.ini`.
2.  Edita `mi_perfil.ini` para ajustar la configuración a tus necesidades (ej. nombre de la ventana, mapeo de columnas, etc.).

## Uso

Para ejecutar el bot, utiliza el script `src/main.py` desde la raíz del proyecto, especificando el perfil a usar y el archivo de entrada.

```bash
python src/main.py --profile <nombre_del_perfil> --input-file <ruta_al_archivo_excel>
```

**Ejemplo:**

```bash
python src/main.py --profile dev_nancy --input-file data/samples/facturacion_ejemplo.xlsx
```

## Desarrollo y Arquitectura

Para una guía detallada sobre la arquitectura del sistema, las decisiones de diseño, los patrones de codificación y la hoja de ruta técnica, consulta el siguiente documento:

- **[Guía de Arquitectura y Desarrollo](./docs/ARCHITECTURE.md)**