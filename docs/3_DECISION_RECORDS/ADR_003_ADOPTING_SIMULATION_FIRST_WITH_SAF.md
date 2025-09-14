# ADR-003: Adopción de la Doctrina "Simulation-First" mediante un Gemelo Digital (Stunt Action Facsimile)

**Fecha:** 13/09/2025
**Estado:** Aceptado

---

## 1. Contexto

A medida que el motor evolucionaba más allá de un simple script, su arquitectura interna ganaba en complejidad y resiliencia. La introducción de una FSM (`ADR-002`) y una jerarquía de excepciones (`ADR-001`) creó un sistema capaz de manejar errores de forma sofisticada. Sin embargo, el **proceso para validar estas capacidades se había convertido en el principal cuello de botella del proyecto.**

El ciclo de desarrollo estaba completamente acoplado a la ejecución del motor contra un entorno de **Escritorio Remoto real**, un proceso plagado de fricciones críticas que amenazaban con detener el progreso:

*   **Ciclos de Desarrollo Lentos y Frustrantes:** Cada cambio de código, por menor que fuera, requería una ejecución completa en un entorno con alta latencia. La depuración era un proceso arduo, basado en `logs` y capturas de pantalla, sin la posibilidad de una inspección interactiva en tiempo real.
*   **Imposibilidad de Pruebas de Integración Automatizadas:** La dependencia de una sesión de GUI remota hacía inviable y completamente inestable la creación de una suite de pruebas de integración automatizada. El proyecto estaba **condenado a no tener una red de seguridad contra regresiones**, limitando severamente la capacidad de refactorizar con confianza.
*   **Nula Reproducibilidad de Errores:** La depuración de fallos era una pesadilla. El estado del entorno remoto no podía ser controlado, versionado ni replicado de forma determinista, haciendo que los errores "escamosos" (flaky) fueran casi imposibles de diagnosticar y solucionar.

El proyecto había alcanzado un punto en el que la fiabilidad del entorno de pruebas era el principal limitante de la calidad del producto final. Un prerrequisito clave que hizo viable esta decisión fue la creación previa de un ecosistema de datos de prueba seguros y versionables (commit `cd7e3ba`), que proporcionó el "combustible" de alta calidad que el simulador necesitaría para operar.

---

## 2. Decisión

En lugar de intentar aplicar parches a los problemas del entorno real, se tomó la decisión estratégica de **eliminar por completo la dependencia de él durante el desarrollo y las pruebas**. La solución fue construir un **gemelo digital local**, el `Stunt Action Facsimile` (SAF), y adoptar formalmente la doctrina de desarrollo **"Simulation-First"**.

La materialización de esta decisión se encuentra en el commit `27917fe` (*feat(testing): Introduce Stunt Action Facsimile (SAF) v0.1*).

Los principios arquitectónicos clave del SAF demostraron la seriedad de esta decisión:

1.  **Arquitectura de Software Robusta:** El SAF fue diseñado desde su concepción como una aplicación de software seria, siguiendo el patrón **Modelo-Vista-Controlador (MVC)** para garantizar una clara separación de responsabilidades y una alta mantenibilidad.
2.  **Estado Explícito y Guiado por Datos:** El Modelo (`ApplicationState`) se alimenta de un archivo `test_scenarios.json` versionado en Git, haciendo que los escenarios de prueba sean explícitos, repetibles y parte del historial del proyecto.
3.  **Simulación Funcional, no Visual:** Se priorizó la replicación del **comportamiento funcional** de la aplicación de destino (respuesta a eventos de teclado, gestión del estado, orden de tabulación) sobre la fidelidad visual.

Esta no fue una decisión única, sino el comienzo de una **inversión continua**. La rápida evolución del SAF a su versión `v0.2` (commits `b5ae168` a `70d854e`) —incluyendo una refactorización a modelos de datos explícitos— demostró el compromiso del proyecto con el SAF como un activo estratégico a largo plazo.

---

## 3. Consecuencias

La adopción de la doctrina "Simulation-First" fue una elección deliberada que intercambió un costo de desarrollo inicial por beneficios exponenciales en velocidad, calidad y profesionalismo a largo plazo.

### Positivas:

*   **Revolución en la Experiencia del Desarrollador (DevEx):** El ciclo de feedback de "codificar -> probar -> depurar" se redujo de minutos a segundos. El desarrollo se desacopló por completo del acceso a la red o a entornos de producción, permitiendo una experimentación y refactorización rápidas y seguras.
*   **Transformación de la Estrategia de Calidad:** Esta decisión **desbloqueó la capacidad fundamental** de realizar pruebas de integración de extremo a extremo. Aunque en la `v0.8.0` estas pruebas aún se ejecutan de forma manual (ver `04_TESTING_AND_QUALITY.md`), la existencia del SAF es el **prerrequisito técnico indispensable** para su futura automatización y para cualquier ambición de Integración Continua (CI/CD).
*   **Profesionalización del Proyecto:** Este fue el hito que marcó la transición del proyecto de ser un "script" a ser un "sistema de software de ingeniería". Proporcionó la infraestructura para aplicar prácticas de calidad rigurosas y sentó las bases para la confianza necesaria para acometer refactorizaciones complejas, como la del futuro `Navigator`.

### Negativas o Riesgos (Los Costos de la Inversión):

*   **Introducción de una Nueva Superficie de Mantenimiento:** El SAF se convirtió en un **producto de software en sí mismo**. Requiere su propio ciclo de vida de desarrollo, mantenimiento y refactorización para seguir siendo útil, añadiendo una sobrecarga de trabajo al proyecto.
*   **Riesgo de "Deriva de Simulación" (Simulation Drift):** Este es el riesgo a largo plazo más significativo. Existe la posibilidad de que el comportamiento del SAF y el del SF real **diverjan con el tiempo** a medida que la aplicación de destino evolucione. Esto podría llevar a un falso sentido de seguridad, con una suite de pruebas "verde" que no refleja la realidad de producción.
    *   **Mitigación Futura Requerida:** Esta consecuencia implica la necesidad de establecer un nuevo proceso de **"calibración periódica"**, donde el comportamiento del SAF se valida y se ajusta contra el SF real para asegurar que la simulación sigue siendo fiel.
*   **Costo de Desarrollo Inicial (Trade-off Deliberado):** El tiempo y esfuerzo invertidos en construir y madurar el SAF fue una decisión consciente de "ir lento para ir rápido". Fue una inversión en la "fábrica" (la infraestructura de desarrollo y calidad) en lugar de directamente en el "producto" (la misión de facturación), con la expectativa de que la fábrica mejorada produciría un producto de mayor calidad y a mayor velocidad en el futuro.

---
`[ Anterior: ADR-002 ]` `[ Índice de Registros de Decisión ]` `[ Siguiente: ADR-004 ]`
