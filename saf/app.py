# saf/app.py
import tkinter as tk
import logging
from pathlib import Path

from saf.state.application_state import ApplicationState
from saf.ui.main_window import MainWindow
from saf.handlers.event_handlers import EventHandlers

# Configuración centralizada del logging para el SAF.
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
        
        # 3. Ensamblar la arquitectura mediante Inyección de Dependencias.
        handlers = EventHandlers(model, None)
        view = MainWindow(root, handlers)
        handlers.view = view # Completar el ciclo inyectando la vista en el controlador.

        # --- Lanzamiento de la Aplicación ---
        view.start()

    except RuntimeError as e:
        # Si ApplicationState lanza un error al no poder cargar los datos,
        # lo capturamos aquí, lo mostramos en la consola y salimos limpiamente.
        logging.critical(f"No se pudo iniciar la aplicación SAF. Error: {e}")

if __name__ == "__main__":
    main()