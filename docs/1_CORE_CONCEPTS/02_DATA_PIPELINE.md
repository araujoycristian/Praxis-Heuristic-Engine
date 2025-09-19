# 02. El Pipeline de Datos

**Versión del Documento:** Corresponde a la implementación v0.8.0 del código fuente.

**Misión de este Documento:** Trazar el viaje completo de los datos a través del `Praxis Heuristic Engine`, desde su estado crudo y no confiable en un archivo externo hasta convertirse en un "contrato de datos" inmutable y verificado, listo para ser consumido de forma segura por el motor de workflow.

**Audiencia:** Desarrolladores, Arquitectos.

---

## 1. Filosofía: "Caos Afuera, Orden Adentro"

El diseño del pipeline de datos se fundamenta en un principio de defensa central: **el motor no confía en ninguna fuente de datos externa.** Se asume que los archivos de entrada (como hojas de cálculo de Excel) son inherentemente caóticos, con inconsistencias en los nombres de las columnas, datos faltantes y formatos impredecibles.

Por lo tanto, el pipeline actúa como una **frontera de seguridad y purificación**. Su única misión es aplicar una serie de transformaciones y validaciones rigurosas para convertir este caos externo en un orden interno predecible. El objetivo final es producir un "combustible" de la más alta calidad para el motor: un conjunto de **contratos de datos inmutables y verificados**.

## 2. Diagrama del Flujo del Pipeline

El viaje de los datos a través del sistema se compone de cuatro etapas secuenciales y bien definidas, cada una con una responsabilidad única.

```mermaid
graph TD
    subgraph "Frontera Externa"
        A[Archivo Excel<br/><i>(Fuente no confiable)</i>]
    end

    subgraph "Pipeline de Datos del Motor"
        B(<b>Etapa 1: Ingesta y Saneamiento</b><br/><i>ExcelLoader</i>)
        C(<b>Etapa 2: Filtrado Semántico</b><br/><i>DataFilterer</i>)
        D(<b>Etapa 3: Validación de Integridad</b><br/><i>DataValidator</i>)
        E(<b>Etapa 4: Transformación y Sellado</b><br/><i>Orchestrator</i>)
    end

    subgraph "Núcleo del Motor"
        F[Lista de Dataclasses Inmutables<br/><i>(Combustible seguro y verificado)</i>]
    end

    subgraph "Salidas de Observabilidad"
        G[Reporte de Errores<br/><i>(Datos rechazados)</i>]
    end

    A --> B;
    B --> C;
    C --> D;
    D -- Datos Válidos --> E;
    D -- Datos Inválidos --> G;
    E --> F;
```

## 3. Etapa 1: Ingesta y Saneamiento Estructural (`Loader`)

*   **Componente Responsable:** `src/data_handler/loader.py`
*   **Principio de Diseño:** **"Frontera Segura"**

La primera acción del pipeline, inmediatamente después de cargar el archivo Excel en un DataFrame de `pandas`, es invocar al método `_sanitize_columns`. Este método utiliza la utilidad `sanitize_column_name` para forzar los nombres de las columnas a un formato interno, estándar y predecible.

Esta es la primera línea de defensa. Asegura que el resto del pipeline opere con identificadores de columna limpios, independientemente de cuán inconsistentes sean en el archivo original. Nótese que el saneamiento preserva las mayúsculas/minúsculas originales del nombre de la columna.

**Ejemplo de Transformación:**
*   `'  CONTRATO EMP: '` se convierte en `CONTRATO_EMP`
*   `'fec/ingreso:'` se convierte en `fec_ingreso`

## 4. Etapa 2: Filtrado Semántico (`Filterer`)

*   **Componente Responsable:** `src/data_handler/filter.py`
*   **Principio de Diseño:** **"Inteligencia Externalizada"**

Una vez que la estructura de los datos ha sido saneada, el `DataFilterer` aplica las reglas de negocio para seleccionar solo el subconjunto de filas que son relevantes para la misión actual.

La lógica del filtro es completamente genérica. No contiene nombres de columnas ni valores codificados. En su lugar, es "enseñado" por el archivo de configuración `.ini`. Para funcionar, realiza una triangulación de información:
1.  Lee los criterios de la sección `[FilterCriteria]` (ej. `specialty_for_filter = MEDICINA GENERAL`).
2.  Usa la sección `[ColumnMapping]` para traducir el nombre lógico (`specialty_for_filter`) al nombre real de la columna en Excel (`ESPECIALIDAD:`).
3.  Aplica el filtro a la columna correspondiente en el DataFrame saneado (`ESPECIALIDAD`).

Este desacoplamiento permite adaptar el filtro a diferentes archivos y criterios sin modificar una sola línea de código Python.

> **Nota de Implementación: Comparación Robusta**
> Una característica clave de esta etapa es que la comparación de valores es **insensible a mayúsculas y minúsculas y a espacios en blanco circundantes**. Antes de aplicar el filtro, tanto el valor de la columna en los datos como el valor del criterio en el archivo `.ini` son convertidos a un formato normalizado (mayúsculas y sin espacios). Esto hace que el filtro sea más robusto y tolerante a pequeñas variaciones introducidas por el usuario en el archivo de configuración.

## 5. Etapa 3: Validación de Integridad (`Validator`)

*   **Componente Responsable:** `src/data_handler/validator.py`
*   **Principio de Diseño:** **"Segregación Activa para la Observabilidad"**

Esta etapa actúa como el guardián de calidad del motor. Su función es hacer cumplir el **Contrato de Datos**, asegurando que cada registro posea la información mínima indispensable para ser procesado. La lista de campos lógicos obligatorios está definida directamente en la clase `DataValidator`, sirviendo como la fuente de verdad para la validación en tiempo de ejecución.

La validación se realiza en dos niveles:

1.  **Validación Estructural:** Primero, comprueba que todas las columnas mapeadas como obligatorias existan realmente en el DataFrame. Si falta una sola columna esencial, considera que toda la estructura de los datos es inválida y rechaza el lote completo.
2.  **Validación de Contenido:** Para los datos que pasan la validación estructural, comprueba la presencia de valores. Cualquier fila que contenga un valor nulo en una de las columnas obligatorias es marcada como inválida.

Una decisión de diseño clave es que el `DataValidator` no descarta silenciosamente los registros inválidos. En su lugar, devuelve **dos DataFrames separados**:
*   `valid_df`: Contiene las filas que pasan ambas validaciones.
*   `invalid_df`: Contiene las filas que fallan en cualquiera de los dos niveles.

Esta segregación activa es lo que permite al `Orchestrator` generar un `error_report.xlsx` detallado, informando al usuario exactamente qué registros necesitan ser corregidos en la fuente.

## 6. Etapa 4: Transformación y Sellado (`Orchestrator`)

*   **Componente Responsable:** `src/core/orchestrator.py` (método `_transform_to_dataclasses`)
*   **Principio de Diseño:** **"El Núcleo Inmutable"**

Este es el paso final y más crítico del pipeline. Los datos, ya filtrados y validados, sufren una transformación fundamental: dejan de ser filas en un DataFrame de `pandas` flexible y se convierten en una lista de objetos **`FacturacionData` fuertemente tipados e inmutables (`@dataclass(frozen=True)`)**.

Durante este proceso, se aplican las siguientes garantías de robustez:
*   **Coerción de Tipos:** Se fuerza activamente la conversión de cada campo al tipo de dato definido en el contrato (ej. `str`, `date`), eliminando cualquier ambigüedad residual del DataFrame.
*   **Manejo Seguro de Nulos:** Los campos opcionales son procesados de forma segura, asegurando que los valores faltantes se conviertan en `None` sin causar errores.
*   **Resiliencia por Fila:** La transformación de cada fila está aislada. Si una fila individual falla durante la conversión (ej. por un formato de fecha inválido), se registra un error y el proceso continúa con el resto de los datos, evitando que un solo registro corrupto detenga todo el lote.

Este "sellado" de los datos en un formato inmutable es una piedra angular de la robustez del motor:
*   **Seguridad:** Garantiza que el motor de workflow y los `Handlers` no puedan modificar accidentalmente los datos de una tarea mientras la procesan.
*   **Predictibilidad:** Elimina por completo los errores por efectos secundarios, haciendo que el comportamiento del sistema sea mucho más fácil de razonar y depurar.

Una vez que los datos se convierten en `dataclasses`, se consideran el "combustible" purificado y seguro, listo para ser inyectado en el motor de workflow.

## 7. Limitaciones y Hoja de Ruta (v0.8.0)

La principal limitación del pipeline en su versión `v0.8.0` es que su validación es **sintáctica, no semántica**. Es decir, comprueba si un campo *existe*, pero no si su contenido *tiene sentido* (ej. una fecha de ingreso en el futuro).

Esta debilidad es la justificación directa para el **Hito 1: El Guardián de la Entrada** en la hoja de ruta estratégica del proyecto. Este hito introducirá una nueva capa de `SanityValidator` que aplicará reglas de negocio configurables para detectar y rechazar datos lógicamente absurdos, elevando aún más la calidad y la fiabilidad del motor.

---
`[ Volver al Índice de la Biblioteca ]`
---
