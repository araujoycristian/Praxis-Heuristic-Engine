# saf/handlers/event_handlers.py

"""
Este módulo define el Controlador (Controller) en la arquitectura MVC del SAF.

Contiene la clase EventHandlers, que actúa como el intermediario entre la
Vista (la GUI) y el Modelo (el estado de la aplicación), manejando todas
las interacciones del usuario (en este caso, el bot).
"""

import logging
import pyperclip

class EventHandlers:
    """
    El Controlador en nuestra arquitectura MVC.

    Responsabilidades:
    - Contener los métodos callback para los eventos de la GUI (ej. on_enter_pressed).
    - Recibir eventos de la Vista (ej. una pulsación de tecla).
    - Interactuar con el Modelo para cambiar el estado de la simulación.
    - Indicar a la Vista que se actualice para reflejar los cambios en el Modelo.
    """
    def __init__(self, model, view):
        """
        Inicializa el controlador.

        Args:
            model: Una instancia del Modelo (ApplicationState).
            view: Una instancia de la Vista (MainWindow). Se puede inyectar
                  después de la inicialización para romper dependencias circulares.
        """
        self.model = model
        self.view = view
        self.logger = logging.getLogger(self.__class__.__name__)

    def on_enter_pressed(self, event):
        """
        Manejador para el evento <Return> en el campo de búsqueda de historia clínica.
        
        Args:
            event: El objeto de evento de Tkinter (no se usa directamente).
        """
        # 1. Obtiene la entrada del usuario desde la Vista.
        history_id = self.view.entry_historia.get().strip()
        self.logger.info(f"Evento <Return> detectado. Buscando ID: '{history_id}'")

        # 2. Interactúa con el Modelo para actualizar el estado.
        if self.model.find_patient_by_history_id(history_id):
            # 3a. Paciente encontrado: indica a la Vista que se actualice con los datos.
            self.view.update_patient_details(self.model.current_patient)
        else:
            # 3b. Paciente no encontrado: indica a la Vista que limpie los campos.
            self.view.update_patient_details(None)

    def on_copy_id(self, event):
        """
        Manejador para el evento <Control-c> en el campo de identificación.
        Utiliza `pyperclip` para asegurar la compatibilidad con el bot.

        Args:
            event: El objeto de evento de Tkinter que contiene el widget de origen.
        
        Returns:
            "break": Una cadena especial que le indica a Tkinter que detenga
                     la propagación del evento, evitando comportamientos por defecto.
        """
        widget = event.widget
        content = widget.get()
        self.logger.info(f"Evento <Control-c> detectado. Usando pyperclip para copiar: '{content}'")

        try:
            # PUNTO CLAVE: Se usa la misma librería que el bot para eliminar conflictos
            # de acceso al recurso del portapapeles del sistema operativo.
            pyperclip.copy(content)
        except pyperclip.PyperclipException as e:
            # Es una buena práctica registrar si el propio SAF tiene problemas.
            self.logger.error(f"SAF falló al intentar copiar al portapapeles con pyperclip: {e}")

        # Detiene el procesamiento posterior del evento por parte de Tkinter.
        return "break"