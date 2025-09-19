# 05. El Contrato de Datos (Estado v0.8.0)

**Misión de este Documento:** Servir como la especificación técnica formal e inequívoca de los datos de entrada requeridos por el `Praxis Heuristic Engine` para ejecutar la misión de facturación. Este documento es el **puente** entre los operadores de negocio que preparan los datos y los desarrolladores que mantienen y extienden el motor.

**Audiencia:** Operadores de Negocio, Analistas de Datos, Desarrolladores, Arquitectos.

---

## 1. Propósito y Audiencia

Este documento es la **única fuente de verdad** sobre la estructura y los requisitos de los datos de entrada. Define un contrato estricto que los datos deben cumplir para ser aceptados y procesados por el motor.

*   **Para Operadores de Negocio:** Esta es su guía para preparar el archivo Excel de entrada. Seguir este contrato garantiza que el motor pueda procesar los datos de manera eficiente y sin errores de validación.
*   **Para Desarrolladores:** Esta es la especificación del "esquema de datos" con el que trabaja el núcleo del motor. Define la estructura de las `dataclasses` internas y las reglas que el `DataValidator` debe hacer cumplir.

## 2. Terminología Clave: El Flujo de Nombres de Columnas

Para que el motor sea flexible, utiliza un sistema de mapeo de tres pasos. Es crucial entender estos conceptos:

1.  **Nombre en Excel:** Es el encabezado de la columna **tal como aparece en su archivo Excel** (ej. `'HISTORIA:'`, `'Nro. Historia'`, etc.). Este puede variar entre diferentes archivos o clientes.

2.  **Nombre Saneado:** Inmediatamente después de la carga, el motor **sanea** todos los `Nombres en Excel` a un formato interno consistente y predecible (minúsculas, sin espacios ni caracteres especiales, ej. `historia_`). Este es un paso automático.

3.  **Nombre Lógico:** Es el identificador **estable y en `minusculas_con_guion_bajo`** que el motor utiliza en su código (ej. `numero_historia`). Es el "apodo" interno que nunca cambia.

**El Puente:** La sección `[ColumnMapping]` en su archivo de perfil `.ini` es el "diccionario de traducción" que conecta el **Nombre Lógico** con el **Nombre en Excel**. El motor lo usa para saber a qué columna saneada corresponde cada campo lógico.

```ini
# Ejemplo de la sección [ColumnMapping] en un perfil .ini
# El motor sabe que el Nombre Lógico `numero_historia` corresponde al Nombre en Excel `HISTORIA:`.
# Al validar, buscará la columna saneada `historia_` en los datos.
[ColumnMapping]
numero_historia = HISTORIA:
identificacion = IDENTIFIC:
# ... el resto de los mapeos
```

## 3. Especificación de Campos Obligatorios

Las siguientes columnas **deben existir** en el archivo de entrada y **no pueden contener valores vacíos** para ninguna fila que se desee procesar. El incumplimiento de este contrato para una fila resultará en su rechazo automático.

| Nombre Lógico | Obligatorio | Tipo de Dato Esperado | Descripción y Reglas de Validación (v0.8.0) | Ejemplo de Mapeo en `.ini` |
| :--- | :--- | :--- | :--- | :--- |
| `numero_historia` | **Sí** | `string` | Identificador único de la historia clínica del paciente. Usado para la búsqueda inicial. <br/> **Validación v0.8.0: No debe ser nulo.** | `numero_historia = HISTORIA:` |
| `diagnostico_principal`| **Sí** | `string` | Código del diagnóstico principal del paciente (ej. CIE-10). <br/> **Validación v0.8.0: No debe ser nulo.** | `diagnostico_principal = DIAG INGRESO` |
| `fecha_ingreso` | **Sí** | `date` | Fecha de ingreso. Se recomienda `YYYY-MM-DD` para evitar ambigüedades. <br/> **Validación v0.8.0: No debe ser nulo y debe ser una fecha válida.** | `fecha_ingreso = FEC/INGRESO:` |
| `medico_tratante` | **Sí** | `string` | Nombre del médico que atiende al paciente. <br/> **Validación v0.8.0: No debe ser nulo.** | `medico_tratante = MEDICO:` |
| `empresa_aseguradora`| **Sí** | `string` | Nombre de la entidad aseguradora del paciente. <br/> **Validación v0.8.0: No debe ser nulo.** | `empresa_aseguradora = EMPRESA:` |
| `contrato_empresa` | **Sí** | `string` | Nombre o código del contrato con la aseguradora. <br/> **Validación v0.8.0: No debe ser nulo.** | `contrato_empresa = CONTRATO EMP:` |
| `estrato` | **Sí** | `string` | Nivel socioeconómico del paciente. <br/> **Validación v0.8.0: No debe ser nulo.** | `estrato = ESTRATO:` |

## 4. Especificación de Campos Opcionales

Las siguientes columnas pueden o no estar presentes en el archivo de entrada. Si existen, el motor las utilizará; si no, continuará el proceso sin ellas. Una celda vacía en estas columnas no causará que una fila sea rechazada.

| Nombre Lógico | Obligatorio | Tipo de Dato Esperado | Descripción y Reglas de Validación (v0.8.0) | Ejemplo de Mapeo en `.ini` |
| :--- | :--- | :--- | :--- | :--- |
| `identificacion` | No | `string` | Número de identificación legal del paciente (ej. Cédula). Usado para la validación crítica post-búsqueda. <br/> **Validación v0.8.0: Ninguna (puede estar vacío).** | `identificacion = IDENTIFIC:` |
| `diagnostico_adicional_1` | No | `string` | Primer código de diagnóstico adicional. <br/> **Validación v0.8.0: Ninguna (puede estar vacío).** | `diagnostico_adicional_1 = DX ADICIONAL1:` |
| `diagnostico_adicional_2` | No | `string` | Segundo código de diagnóstico adicional. <br/> **Validación v0.8.0: Ninguna (puede estar vacío).** | `diagnostico_adicional_2 = DX ADICIONAL2:` |
| `diagnostico_adicional_3` | No | `string` | Tercer código de diagnóstico adicional. <br/> **Validación v0.8.0: Ninguna (puede estar vacío).** | `diagnostico_adicional_3 = DX ADICIONAL3:` |

## 5. Cumplimiento del Contrato y Consecuencias

Este contrato no es una simple guía; es un conjunto de reglas que el motor hace cumplir algorítmicamente.

*   **Componente de Cumplimiento:** El `DataValidator` (`src/data_handler/validator.py`), como parte del Pipeline de Datos, es el componente de software responsable de verificar que cada fila de datos cumpla con las reglas de los campos obligatorios definidas en este documento.

*   **Consecuencias del Incumplimiento:** Si una fila del archivo de entrada tiene un valor vacío o nulo en cualquiera de los campos marcados como **`Obligatorio: Sí`**, esa fila será considerada **inválida**.
    *   **No será procesada por el motor de automatización.**
    *   **Será segregada y registrada en el reporte de errores (`error_report_YYYY-MM-DD_HHMMSS.xlsx`)** que se genera en el directorio `data/output/errors/`.

Este mecanismo asegura que solo los datos completos y de alta calidad lleguen al motor de workflow, maximizando la tasa de éxito y proporcionando una retroalimentación clara para la corrección de los datos en su origen.

---
`[ Anterior: 04. Estrategia de Calidad y Pruebas ]` `[ Índice de la Biblioteca ]` `[ Siguiente: 06. El Entorno Operativo ]`
---
