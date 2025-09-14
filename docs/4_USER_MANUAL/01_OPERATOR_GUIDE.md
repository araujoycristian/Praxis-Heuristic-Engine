# Manual de Operaciones del Praxis Heuristic Engine

**Versión del Documento:** 1.0 (para `Praxis Heuristic Engine v0.8.0`)
**Audiencia:** Operadores de Negocio, Analistas de Datos (no desarrolladores)

---

## Sección 1: Introducción - Su Asistente Digital

¡Bienvenida al `Praxis Heuristic Engine`!

Piense en este motor como su nuevo **asistente digital personal**. Su única misión es encargarse de la tarea repetitiva y propensa a errores de copiar datos desde un archivo Excel al software de facturación. Al delegarle este trabajo, usted queda libre para concentrarse en tareas más importantes que requieren su experiencia y juicio.

#### ¿Qué Hace Exactamente Este Motor?

El motor lee la información de su hoja de cálculo y la introduce en el software de facturación simulando las acciones que usted haría (escribir en el teclado, copiar, etc.), pero lo hace a gran velocidad y sin cometer los errores de transcripción que pueden ocurrir por cansancio o distracción.

#### ¿Es Seguro?

**Absolutamente.** Su confianza es nuestra máxima prioridad. Por diseño, el motor:
*   ✅ **Solo tiene permiso de LECTURA** sobre su archivo Excel. Sus datos originales nunca serán modificados.
*   ✅ **No almacena información sensible.** Una vez que termina su trabajo, olvida los datos que ha procesado.

#### Una Nota Sobre Paciencia y Realismo

Su asistente digital es extremadamente preciso, pero no es mágico. Para ser fiable, trabaja a una velocidad controlada, a veces haciendo pausas para asegurarse de que el software de facturación ha respondido correctamente. Un lote de 100 tareas no será instantáneo. Piense en él como un colega diligente, no como un truco de magia. Su fortaleza es la **precisión y la fiabilidad**, no una velocidad irreal.

---

## Sección 2: Las Tres Reglas de Oro para el Éxito

Para tener una colaboración exitosa con su asistente, solo necesita recordar tres ideas simples:

1.  **Regla #1: Datos de Calidad Producen Resultados de Calidad.**
    El motor es un experto en copiar y pegar, pero no puede adivinar o corregir información incorrecta. La calidad de la automatización siempre comenzará con la calidad y limpieza de su archivo Excel.

2.  **Regla #2: El Perfil `.ini` es el Panel de Control.**
    El archivo de configuración `.ini` contiene las instrucciones que el motor seguirá. Le dice qué columnas leer, cómo filtrar los datos y a qué ventana conectarse. Usted tiene el control de este panel.

3.  **Regla #3: El Motor Siempre Informa de su Trabajo.**
    Al final de cada ejecución, el motor le entregará un reporte claro y conciso de lo que hizo, lo que tuvo éxito y, lo más importante, qué tareas podrían necesitar su atención.

---

## Sección 3: Paso 1 - Preparando su Archivo de Datos (El Excel)

Antes de ejecutar el motor, una revisión rápida de su archivo Excel puede ahorrarle mucho tiempo.

#### Checklist de Preparación

*   **[ ] Hoja de Cálculo Correcta:** Asegúrese de que los datos que quiere procesar están en la hoja de cálculo correcta (ej. "Hoja1", "Proced", etc.).
*   **[ ] Encabezados Visibles:** La fila con los títulos de las columnas debe estar presente y ser la correcta.
*   **[ ] Columnas Obligatorias Completas:** Cada fila que quiera procesar debe tener información en las columnas esenciales. Consulte el **[Contrato de Datos](../1_CORE_CONCEPTS/05_DATA_CONTRACT.md)** para saber cuáles son obligatorias.

#### Guía de Higiene de Datos (Pro Tips)

A veces, los problemas en Excel son invisibles. Aquí tiene cómo solucionar los más comunes:

*   **Problema: Espacios Ocultos.** Para el motor, `' Juan'` y `'Juan'` son dos personas diferentes.
    *   **Solución:** Use la función `ESPACIOS()` (o `TRIM()`) de Excel en una columna nueva para limpiar los espacios extra de sus datos.
*   **Problema: Números que son Texto (y viceversa).**
    *   **Solución:** Seleccione toda la columna (ej. la de identificación), vaya a `Formato de Celdas` y asegúrese de que esté definida como **Texto**. Esto previene que Excel elimine ceros a la izquierda.
*   **Problema: Celdas Combinadas.**
    *   **Solución:** El motor no puede leer correctamente las celdas combinadas. Por favor, asegúrese de que no haya ninguna en su hoja de datos.

---

## Sección 4: Paso 2 - Configurando la Misión (El Archivo de Perfil `.ini`)

El archivo de perfil `.ini` es el cerebro de la misión. Le recomendamos tener una copia por cada tipo de archivo Excel que procese.

#### Las Secciones que Usted Controla

*   **`[ColumnMapping]` (El Diccionario de Traducción):**
    Esta es la sección más importante. Le dice al motor cómo se llaman las columnas en *su* archivo Excel.
    ```ini
    [ColumnMapping]
    # Nombre Lógico del Motor = Nombre Exacto en su Excel
    numero_historia = HISTORIA:
    identificacion = IDENTIFIC:
    ```

*   **`[FilterCriteria]` (Los Filtros de Trabajo):**
    Use esta sección para decirle al motor que procese solo un subconjunto de los datos. Si deja esta sección vacía o la comenta (con `#`), el motor procesará todas las filas.
    ```ini
    [FilterCriteria]
    # Procesar solo las filas donde la columna USUARIO: sea NANCY
    user_for_filter = NANCY
    ```

#### ⚠️ ZONA DE EXPERTOS: NO MODIFICAR ⚠️

Las siguientes secciones contienen ajustes técnicos. Modificarlas puede hacer que el motor deje de funcionar. Por favor, no las altere a menos que un técnico se lo indique.
*   `[AutomationSettings]`
*   `[AutomationTimeouts]`
*   `[AutomationRetries]`

#### Para Usuarios Avanzados: Cómo Crear un Nuevo Perfil

Si recibe un nuevo tipo de archivo Excel con diferentes columnas, puede crear un nuevo perfil fácilmente:
1.  En la carpeta `config/profiles/`, haga una copia de `dev_example.ini`.
2.  Renombre la copia (ej. `reporte_mensual.ini`).
3.  Abra el nuevo archivo y ajuste las secciones `[ColumnMapping]` y `[FilterCriteria]` para que coincidan con su nuevo archivo.

---

## Sección 5: Paso 3 - Ejecutando el Motor (El Método del Doble Clic)

Olvídese de la compleja línea de comandos. Hemos creado un lanzador simple para usted.

1.  **Localice el archivo `run_engine.bat`** en la carpeta principal del proyecto.
2.  **Haga doble clic en él.**
3.  Aparecerá una ventana de terminal que le hará dos preguntas:
    *   Le pedirá el **nombre de su perfil** (ej. `reporte_mensual`).
    *   Le pedirá la **ruta a su archivo Excel**.
4.  Responda a las preguntas, presione `Enter`, ¡y su asistente digital se pondrá a trabajar!

> **💡 Método Alternativo (para Técnicos):** Si lo prefiere, puede ejecutar el motor desde la línea de comandos usando la plantilla:
> `python src/main.py --profile <perfil> --input-file <archivo>`

---

## Sección 6: Paso 4 - Interpretando los Resultados (Los Reportes)

La misión no termina hasta que el informe está entregado. El motor siempre le informará de su trabajo. Su punto de partida es siempre el archivo de resumen.

#### 1. `reports/summary_...txt` (El Resumen Ejecutivo)

Este es el primer y más importante archivo que debe revisar. Le da una visión general de la misión.

**Ejemplo de Reporte de Resumen:**
```
==================================================
  Reporte de Ejecución - 2025-09-13 11:45:00
==================================================
Tareas iniciales en Excel: 150
Tareas tras filtro/validación: 25
Tareas procesadas por el automator: 25
  - Exitosas: 23
  - Fallidas: 2
--------------------------------------------------
Detalle de Tareas Fallidas:
  - ID: HC-ERROR-001 | Paso: FINDING_PATIENT | Motivo: FAILED_UNRECOVERABLE | Error: [E2001_ID_MISMATCH] Incongruencia en la identificación...
  - ID: HC-ERROR-002 | Paso: INITIATING_NEW_BILLING | Motivo: FAILED_RETRY_LIMIT | Error: [E3001_CLIPBOARD_FAILURE] La operación de copia no tuvo efecto...
--------------------------------------------------
[ PRÓXIMOS PASOS RECOMENDADOS ]

ATENCIÓN: Se detectaron 2 fallos durante la automatización.
Por favor, envíe este archivo de resumen (`summary_...txt`) al
equipo de soporte técnico para su análisis.
==================================================
```
**Su Foco Principal: La Sección de "Próximos Pasos Recomendados"**
Esta sección le dirá exactamente qué hacer a continuación. Confíe en ella.

#### 2. `errors/error_report_...xlsx` (Su Lista de Tareas)

Este archivo **solo se crea si sus datos no pasaron el control de calidad inicial.**

*   **¿Cuándo lo reviso?** Cuando la sección de "Próximos Pasos" del resumen se lo indique.
*   **¿Qué contiene?** Las filas exactas de su Excel que el motor no pudo procesar porque les faltaba información obligatoria.
*   **Su Acción:** Ábralo, use la información para corregir los datos en su archivo Excel original y vuelva a ejecutar el motor.

#### 3. `screenshots/FAILURE_...png` (Para los Técnicos)

**Usted puede ignorar esta carpeta.** Si el motor encuentra un error muy grave e inesperado, tomará una "foto" de la pantalla para ayudar a los desarrolladores a diagnosticar el problema.

---

## Sección 7: Guía Rápida de Solución de Problemas (FAQ)

*   **Problema:** "El motor se cierra inmediatamente y no hace nada."
    *   **Solución:** Verifique la ortografía del nombre del perfil y la ruta del archivo que introdujo en el lanzador. Un `FileNotFoundError` es la causa más común.

*   **Problema:** "El reporte dice '0 tareas procesadas' después del filtro."
    *   **Solución:** Esto casi siempre significa que los criterios en la sección `[FilterCriteria]` de su perfil no coinciden con ninguna fila en su Excel. Revíselos cuidadosamente.

*   **Problema:** "Todas o muchas tareas fallaron con el error `PatientIDMismatchError`."
    *   **Causa:** Esto indica un problema de desajuste entre los datos esperados y lo que el motor "ve" en la pantalla. Las causas más comunes son:
        1.  **Mapeo Incorrecto:** Vaya a su perfil `.ini` y asegúrese de que en `[ColumnMapping]`, el `nombre_lógico` `identificacion` está correctamente asignado a la columna de la cédula en su Excel.
        2.  **Problema de Datos:** El número de identificación en su Excel no coincide con el que está registrado en el software de facturación para esa historia clínica.
    *   **Solución:** Revise primero el mapeo. Si es correcto, verifique la calidad de los datos para la primera tarea fallida.

*   **Cuándo Contactar a Soporte:** Si ha verificado los puntos anteriores y el problema persiste, por favor, contacte al equipo técnico. **Adjunte siempre el archivo `summary_...txt`** en su comunicación; es la herramienta de diagnóstico más importante para ellos.

---
`[ Anterior: Guía del Ecosistema de Herramientas ]` `[ Índice de la Biblioteca ]`
