# 06. El Entorno Operativo (Estado v0.8.0)

**Misión de este Documento:** Proporcionar una guía técnica completa sobre la configuración, la gestión de secretos y el manejo de dependencias del `Praxis Heuristic Engine`. Este documento es esencial para cualquier persona responsable de desplegar, mantener u operar el motor en cualquier entorno, desde el desarrollo local hasta la producción.

**Audiencia:** Desarrolladores, Ingenieros de DevOps, Administradores de Sistemas.

---

## 1. Filosofía: Configuración como un Contrato Flexible

La filosofía operativa del motor se basa en el principio de **Desarrollo Guiado por Configuración**. El código del motor implementa *capacidades* genéricas (navegar, leer, validar), pero es la **configuración** la que le enseña la *misión* específica que debe ejecutar.

Esto significa que el motor está diseñado para ser adaptado a diferentes entornos (desarrollo, pruebas, producción) y a diferentes variaciones de una misión sin necesidad de modificar su código fuente. La configuración no es un simple ajuste; es el **contrato que define el comportamiento del motor en un contexto dado.**

## 2. El Sistema de Perfiles de Configuración

El motor no utiliza un único archivo de configuración monolítico. En su lugar, emplea un **sistema de perfiles** flexible para una máxima versatilidad.

### 2.1. Anatomía del Sistema

*   **Directorio Raíz:** `config/profiles/`
*   **Mecanismo:** Cada archivo `.ini` dentro de este directorio representa un perfil completo y autocontenido.
*   **Activación:** El perfil a utilizar en una ejecución se especifica en tiempo de ejecución a través del argumento de línea de comandos `--profile <nombre_del_perfil>`.

**Ejemplo de Ejecución:**
```bash
python src/main.py --profile dev_saf --input-file data/samples/facturacion_anonymized.xlsx
```
En este caso, el motor cargará y utilizará exclusivamente el archivo `config/profiles/dev_saf.ini`.

### 2.2. Propósito de los Perfiles Existentes

Este diseño permite una separación limpia de las configuraciones para diferentes propósitos:
*   **`dev_saf.ini`:** Configuración para ejecutar el motor contra el simulador SAF local.
*   **`dev_main.ini`:** Perfil de desarrollo genérico para pruebas preliminares.
*   **`produccion_cliente_xyz.ini`:** Un ejemplo de un perfil que podría usarse en un entorno de producción real, con mapeos de columnas y títulos de ventana específicos.

## 3. Estrategia de Gestión de Secretos y Entornos

Un "secreto" en el contexto de este proyecto es cualquier información que sea específica de un entorno o que pueda ser sensible. El ejemplo más claro en la `v0.8.0` es la clave `window_title` en la sección `[AutomationSettings]`.

La estrategia de seguridad del proyecto se basa en una configuración deliberada del archivo `.gitignore`.

### 3.1. El Patrón "Git-Ignore"

La estrategia se basa en dos reglas clave en el archivo `.gitignore`:
```gitignore
# Ignorar todos los perfiles de configuración para no subir datos sensibles.
config/profiles/*.ini

# EXCEPCIÓN: No ignorar el archivo de ejemplo para que sirva de plantilla.
!config/profiles/dev_example.ini
```
Esto implementa un flujo de trabajo seguro que previene la fuga accidental de información sensible al repositorio de Git.

### 3.2. Flujo de Trabajo para Configurar un Nuevo Entorno

1.  **Copiar la Plantilla:** Cree una copia de `config/profiles/dev_example.ini` y renómbrela según el nuevo entorno (ej. `mi_entorno_local.ini`).
2.  **Editar el Perfil Local:** Modifique el nuevo archivo con los valores específicos del entorno (ej. el `window_title` correcto). Este archivo no será rastreado por Git.
3.  **Ejecutar:** Invoque al motor especificando el nuevo perfil: `python src/main.py --profile mi_entorno_local ...`

## 4. Gestión de Dependencias: El Principio de Reproducibilidad

El proyecto utiliza **`pip-tools`** para una gestión de dependencias profesional, garantizando **entornos de ejecución idénticos y reproducibles** en todas las máquinas.

### 4.1. El Contrato de Dependencias

El sistema se basa en dos archivos con responsabilidades distintas:

*   **`requirements.in` (La Fuente de Verdad Abstracta):**
    *   Editado **manualmente por desarrolladores**.
    *   Lista las dependencias directas y de alto nivel del proyecto (ej. `pandas`, `pytest`).
    *   Define **"lo que el proyecto necesita"** de forma abstracta.

*   **`requirements.txt` (El Manifiesto de Compilación Congelado):**
    *   **Generado automáticamente** por `pip-compile`. **Nunca debe ser editado manualmente.**
    *   Contiene una lista completa de todas las dependencias, incluyendo las transitivas, con sus versiones **exactas y fijadas**.
    *   Define **"exactamente cómo construir un entorno funcional"**.

### 4.2. Flujo de Trabajo para la Gestión de Dependencias

*   **Para Instalar el Entorno (Todos):**
    ```bash
    pip install -r requirements.txt
    ```

*   **Para Añadir o Actualizar una Dependencia (Desarrolladores):**
    1.  Modifique el archivo `requirements.in`.
    2.  Recompile el manifiesto congelado:
        ```bash
        pip-compile requirements.in
        ```
    3.  Añada al commit de Git **ambos archivos**, `requirements.in` y el `requirements.txt` actualizado.

## 5. Gestión del Logging (Estado v0.8.0)

La observabilidad a través del logging es fundamental para el motor. En la `v0.8.0`, la configuración del logging está centralizada en `src/logger_setup.py`.

**Nivel de Log Codificado:**
Es crucial entender que el nivel de verbosidad de los logs está actualmente **fijado en `INFO` directamente en el código fuente**. No es posible cambiar la cantidad de detalle en los logs (ej. a `DEBUG` o `WARNING`) a través de un archivo de configuración.

*   **Implicación para Operadores:** Los logs proporcionarán un nivel de detalle estándar que incluye el inicio y fin de cada tarea, así como advertencias y errores.
*   **Implicación para Desarrolladores:** Para una depuración más profunda, es necesario modificar temporalmente el archivo `src/logger_setup.py` para cambiar el nivel a `logging.DEBUG`. Esta es una limitación reconocida y una candidata a ser externalizada a la configuración en futuras versiones.

## 6. Restricciones de Concurrencia

El diseño del motor en la `v0.8.0` está optimizado para la resiliencia en la interacción con una única GUI. Esto impone una restricción operativa crítica:

**El motor debe ser ejecutado como un proceso único por cada instancia de escritorio.**

Intentar ejecutar múltiples instancias del `Praxis Heuristic Engine` simultáneamente en la misma sesión de usuario (local o remota) resultará en fallos impredecibles y no soportados. Esto se debe a que las instancias entrarían en una **condición de carrera** por el control de recursos del sistema operativo que son inherentemente únicos, como el foco de la ventana de la aplicación de destino y el portapapeles del sistema.

## 7. Artefactos de Salida y Huella en el Sistema de Archivos

Durante su ejecución, el motor genera una serie de artefactos en el directorio `data/output/` para proporcionar observabilidad y diagnóstico. Todas las rutas de salida están actualmente codificadas en el código fuente.

A continuación se detalla la estructura y el propósito de estos artefactos:

| Directorio de Salida | Patrón de Archivo | Propósito y Audiencia |
| :--- | :--- | :--- |
| **`data/output/reports/`** | `summary_YYYYMMDD_HHMMSS.txt` | **Resumen Ejecutivo:** Generado al final de cada ejecución. Contiene estadísticas de alto nivel del lote. Destinado a la auditoría de la operación (Operadores, Gestión). |
| **`data/output/errors/`** | `error_report_YYYY-MM-DD_HHMMSS.xlsx` | **Reporte de Calidad de Datos:** Se genera solo si filas son rechazadas por el `DataValidator`. Contiene las filas rechazadas. Destinado al operador de negocio para la corrección de datos en origen. |
| **`data/output/screenshots/`** | `FAILURE_YYYYMMDD_HHMMSS_... .png` | **Diagnóstico de Fallo Crítico:** Se genera solo ante un error inesperado del motor. Contiene una captura del escritorio en el momento del fallo. Destinado al diagnóstico técnico (Desarrolladores). |

**Política de Mantenimiento:** El directorio `data/output/` puede ser archivado o limpiado de forma segura entre ejecuciones sin afectar el funcionamiento del motor.

---
`[ Volver al Índice de la Biblioteca ]`
