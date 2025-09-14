# Guía de Inicio Rápido: De Cero a la Primera Ejecución

**Misión de este Documento:** Guiarte paso a paso a través de la configuración de tu entorno de desarrollo y la ejecución del motor contra su simulador local (SAF). Al final de esta guía, tendrás un entorno de trabajo funcional y habrás visto el `Praxis Heuristic Engine` en acción por primera vez.

**Audiencia:** Nuevos Desarrolladores.

---

## Introducción: El Contrato con el Lector

Bienvenida al `Praxis Heuristic Engine`. Esta guía es tu primer paso práctico para convertirte en una contribuidora del proyecto.

Nuestra promesa es simple: si sigues estos pasos, en menos de 30 minutos tendrás el motor funcionando en tu máquina local. No solo te daremos los comandos, sino que te explicaremos el **"porqué"** de cada paso fundamental para que construyas una comprensión sólida del ecosistema desde el principio.

## Sección 1: El Contrato de Entorno (Prerrequisitos y Verificación)

Antes de instalar nada, debemos asegurarnos de que tu máquina tiene las herramientas base necesarias. Un entorno de trabajo limpio y verificado es la mejor prevención contra futuros dolores de cabeza.

### 1.1. Prerrequisitos

*   Un terminal o línea de comandos (como `Terminal`, `PowerShell` o `Git Bash`).
*   `git` instalado.
*   `Python` en la versión `3.11.x`.

### 1.2. Verificación de Entorno (¡No te saltes esto!)

Abre tu terminal y ejecuta los siguientes comandos. Compara tu salida con la esperada para asegurarte de que todo está en orden.

1.  **Verificar `git`:**
    ```bash
    git --version
    ```
    *   _Salida Esperada:_ Deberías ver algo como `git version 2.34.1`. Si recibes un error de "comando no encontrado", necesitarás instalar Git.

2.  **Verificar `python`:**
    ```bash
    python --version
    # O si tienes múltiples versiones, podrías necesitar:
    # python3 --version
    ```
    *   _Salida Esperada:_ `Python 3.11.9`. Una versión menor diferente (ej. `3.11.8`) está bien. Si es `3.10` o `3.12`, podrías encontrar problemas. Si no se encuentra, necesitas instalar Python 3.11.

> **Práctica Recomendada: Gestores de Versiones**
> Para evitar conflictos entre las versiones de Python de diferentes proyectos, recomendamos encarecidamente usar un gestor de versiones como `pyenv` (para Linux/macOS) o `pyenv-win` (para Windows). Sin embargo, no es estrictamente necesario para esta guía.

## Sección 2: Instalación y Configuración del Taller

Ahora que hemos verificado las herramientas base, vamos a construir tu taller de desarrollo local para el motor.

### Paso 1: Clonar el Repositorio

Usa `git` para crear una copia local del código fuente del motor.
```bash
git clone <URL_DEL_REPOSITORIO_DEL_PROYECTO>
cd Praxis-Heuristic-Engine
```

### Paso 2: Crear el Entorno Virtual Aislado

> **Contexto (Lo que está sucediendo aquí):**
> Vamos a crear una "caja de arena" para las dependencias de este proyecto, llamada **entorno virtual**. Esto es crucial porque evita que las librerías del motor (`pandas`, `pytest`, etc.) interfieran con otros proyectos en tu máquina. Cada proyecto debe tener su propio entorno aislado.

*   **Para Linux / macOS:**
    ```bash
    python3 -m venv .venv
    ```

*   **Para Windows:**
    ```bash
    python -m venv .venv
    ```
    Este comando creará un nuevo directorio llamado `.venv` dentro del proyecto.

### Paso 3: Activar el Entorno Virtual

> **Contexto (Lo que está sucediendo aquí):**
> La activación le dice a tu terminal que, a partir de ahora, debe usar la versión de Python y las herramientas de esta "caja de arena" (`.venv`), no las del sistema global. Notarás que el prompt de tu terminal cambia para indicarte que estás "dentro" del entorno virtual.

*   **Para Linux / macOS:**
    ```bash
    source .venv/bin/activate
    ```
    *   _Tu prompt cambiará a algo como:_ `(.venv) tu-usuario@tu-maquina:~/Praxis-Heuristic-Engine$`

*   **Para Windows:**
    ```bash
    .\.venv\Scripts\activate
    ```
    *   _Tu prompt cambiará a algo como:_ `(.venv) C:\ruta\a\Praxis-Heuristic-Engine>`

### Paso 4: Instalar las Dependencias Congeladas

Ahora que estás dentro del entorno virtual, instalaremos todas las librerías que el motor necesita.

> **Contexto (La Fuente de Verdad):**
> Usamos el archivo `requirements.txt`. Este archivo es un manifiesto generado automáticamente que contiene la lista **exacta y congelada** de cada librería y sus dependencias, garantizando que todos los desarrolladores trabajen con un entorno idéntico.

```bash
pip install -r requirements.txt
```
Este proceso puede tardar un par de minutos. Si todo va bien, ¡tu entorno de desarrollo ya está listo!

## Sección 3: La Primera Ejecución (El "Momento de la Verdad")

> **Conexión con la Filosofía (Doctrina "Simulation-First"):**
> Para tu primera ejecución, no necesitas acceso a la aplicación real. Usaremos el `Stunt Action Facsimile` (SAF), nuestro gemelo digital, que nos permite probar el 100% de la lógica del motor de forma local y rápida. Este flujo de trabajo de dos terminales es el que usarás el 99% del tiempo durante el desarrollo.

### Paso 1: Iniciar el Simulador (SAF)

En tu terminal actual (con el entorno virtual activado), inicia el SAF.
```bash
python saf/app.py
```
*   Debería aparecer una nueva ventana en tu escritorio titulada **"SAF - Stunt Action Facsimile v0.2"**.
*   **Importante:** Esta terminal ahora estará ocupada por el proceso del SAF. Déjala abierta.

### Paso 2: Iniciar el Motor

Abre una **segunda terminal**, navega al directorio del proyecto y **activa el entorno virtual de nuevo** en esta nueva terminal (repite el Paso 3).

Ahora, ejecuta el motor, diciéndole que use el perfil de configuración del SAF y el archivo de datos de muestra.
```bash
python src/main.py --profile dev_saf --input-file data/samples/facturacion_anonymized.xlsx
```

## Sección 4: Verificación del Éxito (¿Ha funcionado?)

Si todo ha ido bien, habrás sido testigo de tu primera automatización. Vamos a verificarlo con una checklist:

1.  **[ ] En la Ventana del SAF:** Deberías haber visto los campos de la ventana llenarse y limpiarse rápidamente a medida que el motor procesaba cada paciente del archivo de muestra.
2.  **[ ] En la Terminal del Motor:** La ejecución debería terminar sin errores. La última línea del log debería ser algo como: `... INFO ... Orquestación finalizada exitosamente.`
3.  **[ ] En tu Sistema de Archivos (La Evidencia):**
    *   Navega al directorio `data/output/reports/`.
    *   Debería haber un nuevo archivo de texto, como `summary_20250913_103000.txt`.
    *   Ábrelo. Debería contener un resumen confirmando que se procesaron varias tareas con éxito.

Si has marcado las tres casillas, ¡felicidades! Has completado exitosamente la configuración y tu primera ejecución.

## Sección 5: Solución de Problemas Comunes

*   **Error: `python: command not found` o `git: command not found`**
    *   **Causa:** La herramienta no está instalada o no está en el `PATH` de tu sistema.
    *   **Solución:** Vuelve a la Sección 1 y asegúrate de que las herramientas base están correctamente instaladas.

*   **Error: `ModuleNotFoundError: No module named 'pandas'` (o cualquier otra librería)**
    *   **Causa:** Casi siempre, esto significa que tu entorno virtual **no está activado** en la terminal desde la que intentas ejecutar el script.
    *   **Solución:** Ejecuta el comando de activación de la Sección 2, Paso 3. Asegúrate de que `(.venv)` aparece en tu prompt.

*   **Error: El motor se inicia pero falla con `FocusError: No se pudo encontrar la ventana ...`**
    *   **Causa:** El motor no puede encontrar la ventana del SAF.
    *   **Solución:** Verifica que el SAF esté corriendo. Luego, abre `config/profiles/dev_saf.ini` y asegúrate de que la clave `window_title` coincide exactamente con el título de la ventana del SAF.

## Conclusión y Próximos Pasos

Has construido y verificado tu entorno de desarrollo para el `Praxis Heuristic Engine`. Ahora estás en una posición perfecta para empezar a explorar el código y contribuir.

Tu siguiente paso recomendado es familiarizarte con las herramientas de soporte que acelerarán tu flujo de trabajo.

---
`[ Anterior: Índice de la Biblioteca ]` &nbsp;&nbsp;&nbsp; `[ Siguiente: Guía del Ecosistema de Herramientas ]`
