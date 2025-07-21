# saf/app.py
import tkinter as tk
import logging
from pathlib import Path

from saf.state.application_state import ApplicationState
from saf.ui.main_window import MainWindow
from saf.handlers.event_handlers import EventHandlers

# Configuración básica de logging para poder ver lo que hace el SAF en la terminal.
logging.basicConfig(level=logging.INFO, format="%(asctime)s - SAF - %(name)-20s - %(levelname)-8s - %(message)s")

def main():
    """
    Punto de entrada principal para la aplicación Stunt Action Facsimile.
    Orquesta la creación e interconexión de los componentes MVC.
    """
    try:
        # --- Ensamblaje de Componentes ---
        
        # 1. Crear el Modelo: Carga los datos de prueba. Si falla, la app no se inicia.
        scenarios_path = Path(__file__).parent / "data" / "test_scenarios.json"
        model = ApplicationState(scenarios_path)
        
        # 2. Crear la Vista (la ventana raíz de Tkinter).
        root = tk.Tk()
        
        # --- INICIO: LÓGICA DE INYECCIÓN DE DEPENDENCIAS MVC ---
        # El siguiente bloque resuelve la dependencia circular (Vista necesita conocer
        # al Controlador para vincular eventos, y el Controlador necesita conocer a la
        # Vista para leer datos de ella).

        # 3. Crear el Controlador. Se le pasa una referencia `None` a la vista
        #    inicialmente para romper la dependencia circular.
        handlers = EventHandlers(model, None)
        
        # 4. Crear la instancia completa de la Vista, pasándole la raíz y los manejadores
        #    ya instanciados. La Vista ahora conoce a su Controlador.
        view = MainWindow(root, handlers)
        
        # 5. Completar el círculo: ahora que la vista existe, se la inyectamos
        #    al controlador. El Controlador ahora conoce a su Vista.
        handlers.view = view
        # --- FIN: LÓGICA DE INYECCIÓN DE DEPENDENCIAS MVC ---

        # --- Lanzamiento de la Aplicación ---
        view.start()

    except RuntimeError as e:
        # Si ApplicationState lanza un error al no poder cargar los datos,
        # lo capturamos aquí, lo mostramos en la consola y salimos limpiamente.
        logging.critical(f"No se pudo iniciar la aplicación SAF. Error: {e}")
        # Opcional: Mostrar una ventana de error simple si se quisiera.
        # import tkinter.messagebox
        # tkinter.messagebox.showerror("Error Crítico del SAF", str(e))

if __name__ == "__main__":
    main()