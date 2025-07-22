# saf/handlers/event_handlers.py
import logging
import pyperclip

class EventHandlers:
    """
    El Controlador en la arquitectura MVC. Orquesta la interacción
    entre el Modelo (estado) y la Vista (UI), manejando la lógica de eventos
    de forma robusta y centralizada.
    """
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.logger = logging.getLogger(self.__class__.__name__)

    def on_enter_pressed(self, event):
        """
        Manejador para el evento <Return> en el campo de búsqueda.
        Orquesta la búsqueda, la actualización de la UI y, crucialmente,
        gestiona el foco del cursor para un comportamiento predecible.
        """
        history_entry = self.view.get_history_entry_widget()
        if not history_entry:
            self.logger.error("No se pudo procesar <Return>, el widget de entrada no existe.")
            return

        history_id = history_entry.get().strip()
        self.logger.info(f"Evento <Return> detectado. Buscando ID: '{history_id}'")

        if self.model.find_patient_by_history_id(history_id):
            display_data = self.model.get_current_display_data()
            self.view.update_patient_details(display_data)
        else:
            self.view.update_patient_details(None)
        
        # Aseguramos que el foco regrese al campo de entrada SIN IMPORTAR
        # si la búsqueda fue exitosa o no. Esto crea un estado de UI
        # final consistente y predecible para el bot.
        history_entry.focus_set()
        self.logger.info("Foco mantenido en el campo de Nro. Historia después de la búsqueda.")

    def on_new_billing_request(self, event=None):
        """
        Manejador para el evento <Control-n> que resetea la factura.
        La firma incluye 'event=None' para poder recibir el objeto Event
        de Tkinter sin causar un TypeError, aunque no lo usemos.
        """
        self.logger.info("Evento <Control-n> detectado. Iniciando nueva factura.")
        
        self.model.reset_active_invoice()
        display_data = self.model.get_current_display_data()
        self.view.update_patient_details(display_data)

        history_entry = self.view.get_history_entry_widget()
        if history_entry:
            history_entry.focus_set()
            self.logger.info("Foco devuelto al campo de Nro. Historia.")
        
        # Detiene la propagación del evento, evitando comportamientos por defecto.
        return "break"

    def on_copy_id(self, event):
        """Manejador para el evento <Control-c> en el campo de identificación."""
        widget = event.widget
        content = widget.get()
        self.logger.info(f"Evento <Control-c> detectado. Usando pyperclip para copiar: '{content}'")

        try:
            pyperclip.copy(content)
        except pyperclip.PyperclipException as e:
            self.logger.error(f"SAF falló al copiar al portapapeles: {e}")

        return "break"