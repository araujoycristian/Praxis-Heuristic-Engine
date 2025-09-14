# ADR-004: Adopción del Formato `.ini` y un Sistema de Perfiles para la Configuración Externalizada

**Fecha:** 14/09/2025
**Estado:** Aceptado

---

## 1. Contexto

La necesidad de un sistema de configuración robusto no fue un requisito de diseño inicial, sino una necesidad arquitectónica que emergió como respuesta directa a la creciente fragilidad del motor. El `git log` del proyecto revela una evolución clara desde un sistema con valores codificados a uno que depende de una configuración flexible para su adaptabilidad.

*   **Necesidad Inicial:** Las primeras externalizaciones fueron simples, como la configuración de `timeouts` para las operaciones de la GUI.
*   **Necesidad Creciente:** La introducción de la FSM (ver `ADR-002`) requirió que parámetros de resiliencia, como el número de `max_retries`, fueran configurables por entorno.
*   **El Punto de Inflexión:** El commit `4749b15` (*feat(automation): Externalize GUI navigation sequences to config*) marcó el momento en que la configuración dejó de ser un simple ajuste y se convirtió en un **componente crítico para la supervivencia del motor**. La necesidad de adaptar las secuencias de navegación (`{TAB}s`) a diferentes entornos (producción vs. SAF) hizo imperativa la elección de un formato de configuración estándar para todo el proyecto.

Se evaluaron las siguientes alternativas:

*   **JSON:**
    *   *Pros:* Soporte nativo para estructuras jerárquicas y tipos de datos; universalmente soportado.
    *   *Contras:* Sintaxis estricta (comas, llaves) propensa a errores para usuarios no técnicos; falta de soporte nativo para comentarios, lo cual es crucial para la auto-documentación de los perfiles.
*   **YAML:**
    *   *Pros:* Alta legibilidad humana; soporta comentarios y estructuras de datos complejas.
    *   *Contras:* Requiere una dependencia externa (`PyYAML`), lo cual iba en contra del objetivo de mantener el núcleo del motor ligero. Su sintaxis basada en la indentación puede ser una fuente de errores sutiles.
*   **Variables de Entorno (`.env`):**
    *   *Pros:* Estándar de la industria para la gestión de secretos.
    *   *Contras:* Inadecuado para configuraciones estructurales como mapeos de columnas o secuencias de FSM; solo es viable para valores planos.

## 2. Decisión

Se tomó la decisión de adoptar un sistema de configuración multifacético basado en el formato `.ini`, priorizando la simplicidad, la accesibilidad para no desarrolladores y la ausencia de dependencias externas.

Los componentes clave de esta decisión fueron:

1.  **Formato Estándar:** Se eligió el formato `.ini` como el estándar para toda la configuración del motor.
2.  **Librería de la Biblioteca Estándar:** Se decidió utilizar exclusivamente la librería `configparser` de la biblioteca estándar de Python, evitando la introducción de dependencias de terceros para esta funcionalidad central.
3.  **Sistema de Perfiles:** Se implementó un sistema de "perfiles" donde cada archivo `.ini` en el directorio `config/profiles/` representa una configuración de entorno completa y autónoma. El perfil a usar se selecciona en tiempo de ejecución.
4.  **Capa de Abstracción:** Se creó la clase `ConfigLoader` para actuar como la única puerta de entrada a la configuración, centralizando la lógica de carga y parseo.

## 3. Consecuencias

La elección del formato `.ini` fue una decisión con beneficios inmediatos y claros, pero también con costos a largo plazo que ahora informan nuestra hoja de ruta estratégica.

### Positivas:

*   **Accesibilidad y Baja Fricción:** Este es el principal beneficio. Los archivos `.ini` son extremadamente intuitivos y pueden ser editados de forma segura por operadores de negocio para ajustar mapeos de columnas o criterios de filtro, empoderando al usuario final y reduciendo la carga sobre el equipo de desarrollo.
*   **Cero Dependencias:** Mantenerse dentro de la biblioteca estándar mantuvo el núcleo del motor ligero, fácil de desplegar y con una superficie de ataque de seguridad mínima.
*   **Habilitador de la Seguridad Simple:** El modelo de "un archivo por perfil" permitió la implementación de una estrategia de seguridad simple pero efectiva basada en `.gitignore`, previniendo la fuga de información sensible (ver `06_OPERATIONAL_ENVIRONMENT.md`).
*   **Velocidad de Desarrollo:** La simplicidad de `configparser` permitió una implementación rápida que no ralentizó el desarrollo de las características de negocio en las fases iniciales del proyecto.

### Negativas o Riesgos (Deuda Técnica Estructural):

*   **Expresividad Estructural Limitada:** Esta es la consecuencia más significativa y de mayor alcance. El formato `.ini` es fundamentalmente plano (secciones con pares clave-valor) y carece de soporte nativo para:
    *   **Listas:** (ej. una lista de valores válidos para un filtro).
    *   **Jerarquías/Anidamiento:** (ej. la estructura natural de un `GuiMap` con Pestañas que contienen Campos).
    *   **Tipos de Datos:** Todo se lee como un string. El código es responsable de la coerción de tipos (`config.getint()`, `config.getfloat()`), lo que traslada la carga de la validación del formato al código Python.

*   **El Anti-Patrón de "Lógica en Strings":** La limitación estructural obligó a la adopción de un anti-patrón para representar datos complejos, como se evidencia en la externalización de las secuencias de navegación (`nav_to_id_field = {TAB}`). Esto es **lógica de programación codificada dentro de un string de configuración**, una señal clara de que el formato está siendo forzado más allá de su capacidad natural.

*   **Impacto Directo en la Hoja de Ruta Futura:**
    *   **Conflicto con el `Manifiesto de la Misión` (Hito 0):** Es **prácticamente inviable** definir una FSM compleja (estados, transiciones, condiciones) de forma declarativa y legible en un archivo `.ini`. Este ADR sirve como **evidencia** de que, para el Hito 0, probablemente se deba adoptar un formato más expresivo (como JSON o YAML) *específicamente para la definición del workflow*, creando un sistema de configuración híbrido.
    *   **Conflicto con el `GuiMap` (Hito 3):** La estructura jerárquica del `GuiMap` (Pestañas → Campos → Atributos) chocará con la naturaleza plana del `.ini`. Aunque se puede simular con convenciones de nombres (ej. `Facturacion.numero_historia.type`), esto **traslada la complejidad del archivo de configuración al código del `GuiMapLoader`**, que tendrá que implementar una lógica de parseo no trivial para reconstruir la jerarquía. Estamos intercambiando la simplicidad de la configuración por la complejidad del código que la lee.

---
`[ Volver al Índice de la Biblioteca ]`
