# El Taller del Artesano: Guía del Ecosistema de Herramientas de Desarrollo

**Versión del Documento:** 1.0 (para `Praxis Heuristic Engine v0.8.0`)
**Audiencia:** Desarrolladores

---

## Introducción: Más que Scripts, Principios en Acción

Bienvenida al taller del `Praxis Heuristic Engine`. Las herramientas que encontrarás en el directorio `scripts/` no son solo utilidades de conveniencia; son la **implementación de nuestra filosofía de ingeniería**.

Cada herramienta fue creada para resolver un problema específico del ciclo de vida del desarrollo de RPA, reforzando nuestros principios clave: "Desarrollo Guiado por Configuración", "Doctrina Simulation-First" y "Seguridad de Datos". Aprender a usarlas es aprender a pensar como un arquitecto de este motor.

## Herramienta 1: `find_windows.py` (El Explorador)

*   **El Problema que Resuelve:** "Necesito configurar un nuevo perfil `.ini` para interactuar con una aplicación real, pero no estoy segura de cuál es el título exacto de su ventana. Un solo caracter de diferencia hará que el motor falle."
*   **La Filosofía que Refuerza:** **Desarrollo Guiado por Configuración.** Facilita la creación de configuraciones precisas sin adivinar.

### Guía de Uso

Esta es la herramienta más simple y tu primer punto de contacto al configurar un nuevo entorno.

1.  **Asegúrate de que la aplicación** que quieres automatizar esté abierta y visible en tu escritorio (ya sea local o en la sesión de Escritorio Remoto).

2.  En una terminal con tu entorno virtual (`.venv`) activado, ejecuta el script:
    ```bash
    python scripts/find_windows.py
    ```

3.  **Analiza la Salida:** El script escaneará tu escritorio y listará los títulos de todas las ventanas visibles. La salida se verá así:
    ```
    ======================================================
          Buscando títulos de ventanas visibles...
    ======================================================

    Se encontraron 5 ventanas:

      - 'Guía del Ecosistema de Herramientas – MiEditorDeTexto'
      - 'Praxis-Heuristic-Engine - Terminal'
      - 'SF-PROD-REMOTO - Conexión a Escritorio Remoto'
      - 'Calculadora'
      - 'Explorador de archivos'

    ======================================================
                     Búsqueda completada.
    ======================================================
    ```
4.  **Acción:** Identifica el título exacto de la ventana de la aplicación de destino. Selecciónalo, cópialo y pégalo en la clave `window_title` de la sección `[AutomationSettings]` de tu perfil `.ini`.

## Herramienta 2: `generate_mapping_profile.py` (El Asistente Inteligente)

*   **El Problema que Resuelve:** "Tengo un nuevo archivo Excel de un cliente con docenas de columnas. Crear la sección `[ColumnMapping]` a mano es tedioso, propenso a errores tipográficos y consume mucho tiempo."
*   **La Filosofía que Refuerza:** **Desarrollo Guiado por Configuración** y **Reducción de Carga Cognitiva para el Desarrollador.**

### Guía de Uso

Este script es un asistente que utiliza heurísticas para adivinar el mapeo de columnas. No es magia, es un borrador inteligente que requiere tu revisión final.

1.  **Ejecuta el script** apuntando al nuevo archivo Excel y especificando la fila donde se encuentran los encabezados.
    ```bash
    python scripts/generate_mapping_profile.py --input-file ruta/al/nuevo/archivo.xlsx --header-row 6
    ```

2.  **Interpreta el Borrador Generado:** El script imprimirá en la consola una propuesta para tu sección `[ColumnMapping]`. La salida está diseñada para ser copiada y pegada directamente en tu nuevo perfil `.ini`.
    ```ini
    ==================== INICIO DEL BORRADOR DE MAPEADO ====================
    [ColumnMapping]

    # === Mapeos Adivinados con Alta Confianza (Revisar) ===
    diagnostico_principal = DIAG INGRESO
    empresa_aseguradora = EMPRESA:
    estrato = ESTRATO:
    fecha_ingreso = FEC/INGRESO:
    identificacion = IDENTIFIC:
    medico_tratante = MEDICO:
    numero_historia = HISTORIA:

    # === Requieren Atención Manual (Completar nombre lógico o eliminar) ===
    # Propuesta para: FEC/NACIM
    fec_nacim = FEC/NACIM

    # Propuesta para: Nro. Poliza
    nro_poliza = Nro. Poliza

    ====================  FIN DEL BORRADOR DE MAPEADO  ====================
    ```

3.  **Tu Trabajo (El Toque Humano):**
    *   Copia todo el bloque `[ColumnMapping]`.
    *   Pégalo en tu nuevo archivo de perfil.
    *   **Revisa la sección "Requieren Atención Manual".** El script propone un `nombre_lógico` saneado. Tu tarea es decidir si ese nombre es correcto o si necesitas ajustarlo a uno de los nombres lógicos estándar definidos en el Contrato de Datos. Si una columna no es necesaria, simplemente elimina esas líneas.

## Herramienta 3: `anonymize_data.py` (El Guardián de la Privacidad)

*   **El Problema que Resuelve:** "Necesito probar el motor con datos que tengan una estructura y un volumen realistas, pero bajo ninguna circunstancia puedo usar datos de pacientes reales en mi entorno de desarrollo o en el repositorio de Git."
*   **La Filosofía que Refuerza:** **Doctrina Simulation-First** y **Seguridad de Datos.**

### Guía de Uso

Este script toma un archivo de producción y un perfil que lo describe, y genera un conjunto de datos seguro y anónimo para usarlo en desarrollo y pruebas.

> **⚠️ ADVERTENCIA DE SEGURIDAD Y MANEJO DE DATOS**
> Este script está diseñado para ser ejecutado en un entorno local y seguro donde tengas autorización para manejar datos de producción. El archivo de entrada con datos reales **NUNCA** debe ser añadido al repositorio de Git. El único artefacto que se debe guardar es el archivo de salida **anonimizado**.

1.  **Prepara un Perfil de Producción:** Necesitas un archivo `.ini` (ej. `produccion_real.ini`, que estará en tu `.gitignore`) que describa correctamente el archivo de producción (su `sheet_name`, `header_row` y `ColumnMapping`).

2.  **Ejecuta el Script de Anonimización:** El comando más común especificará el perfil de producción, el archivo de entrada real, y los archivos de salida deseados (un Excel para análisis y un JSON para el SAF).
    ```bash
    python scripts/anonymize_data.py \
      --profile produccion_real \
      --input-file /ruta/segura/a/datos_de_produccion.xlsx \
      --output-excel data/samples/nueva_muestra_anonimizada.xlsx \
      --output-json saf/data/nuevo_escenario_saf.json \
      --sample-size 10
    ```

3.  **Utiliza los Artefactos Seguros:** Ahora tienes nuevos archivos de datos en `data/samples/` y `saf/data/` que puedes usar de forma segura y añadir al repositorio de Git para que otros desarrolladores los utilicen.

> **Para Desarrolladores: Extendiendo las Reglas de Anonimización**
> Las reglas que determinan cómo se anonimiza cada columna (ej. reemplazar un nombre con `Faker`, preservar un valor, etc.) están codificadas en el script `anonymize_data.py`, dentro del diccionario `self.rules` en la clase `AnonymizerEngine`. Para añadir o modificar reglas, edita este diccionario directamente.

## Herramienta 4: `pip-tools` (El Gestor de Dependencias)

*   **El Problema que Resuelve:** "¿Cómo me aseguro de que el entorno de dependencias en mi máquina es *exactamente* igual al de mis compañeros y al del servidor de producción? ¿Cómo añado o actualizo una librería de forma segura?"
*   **La Filosofía que Refuerza:** **Entornos Reproducibles y Deterministas.**

### Guía de Uso

Hay dos flujos de trabajo distintos. El 99% del tiempo usarás el primero.

#### Flujo 1: Para Instalar o Sincronizar tu Entorno
Este es el comando que ya usaste en la guía de inicio. Lo ejecutas para asegurarte de que tu entorno virtual coincide con el estado actual del proyecto.
```bash
pip install -r requirements.txt
```

#### Flujo 2: Para Añadir o Actualizar una Dependencia (¡Uso Cuidadoso!)
Este es el proceso que sigues cuando necesitas añadir una nueva librería al proyecto.

1.  **Declara la Intención:** Abre el archivo `requirements.in` y añade el nombre de la nueva librería (ej. `requests`).
2.  **Recompila el Manifiesto:** Ejecuta el compilador de `pip-tools`.
    ```bash
    pip-compile requirements.in
    ```
    `pip-tools` resolverá el árbol de dependencias completo y actualizará `requirements.txt` con las versiones exactas y congeladas.
3.  **Sincroniza tu Entorno:** `pip install -r requirements.txt`.
4.  **Añade al Commit:** **Debes añadir al commit de Git ambos archivos**, el `requirements.in` modificado y el `requirements.txt` actualizado.

## La Fuente de Verdad Siempre Actualizada: `--help`

> **Diseño para la Longevidad:**
> Esta guía es un excelente punto de partida, pero las herramientas evolucionan. La fuente de verdad definitiva sobre los argumentos y opciones de un script es **el propio script**.

Te enseñamos a "pescar". Antes de usar cualquier script, puedes (y debes) pedirle que te explique cómo funciona usando el flag `--help`.

**Ejemplo:**
```bash
python scripts/anonymize_data.py --help
```
Esto te mostrará siempre la lista más actualizada de todos sus posibles argumentos y una descripción de lo que hacen.

---
`[ Anterior: Guía de Inicio Rápido ]` `[ Índice de Guías ]` `[ Siguiente: Manual del Operador ]`
