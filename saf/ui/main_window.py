# saf/ui/main_window.py
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional

from .views.billing_form_view import BillingFormView

class MainWindow:
    """
    La Vista principal (root). Actúa como un simple contenedor ("shell") para
    los componentes de UI más complejos. Es responsable de la estructura general
    de la ventana y de la vinculación de eventos globales.
    """
    WINDOW_TITLE = "SAF - Stunt Action Facsimile v0.2"

    def __init__(self, root: tk.Tk, handlers):
        self.root = root
        self.handlers = handlers
        self.root.title(self.WINDOW_TITLE)

        self.billing_form: Optional[BillingFormView] = None
        self.entry_historia: Optional[ttk.Entry] = None

        self._create_widgets()
        self._bind_events()

    def _create_widgets(self):
        """
        Construye la estructura principal de la ventana delegando la creación
        de sus componentes a métodos especializados.
        """
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self._create_search_frame(main_frame)
        self._create_billing_form_frame(main_frame)

    def _create_search_frame(self, parent_container: ttk.Frame):
        """Crea el componente de búsqueda de paciente."""
        search_frame = ttk.LabelFrame(parent_container, text="Búsqueda de Paciente")
        search_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        ttk.Label(search_frame, text="Nro. Historia:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        self.entry_historia = ttk.Entry(search_frame, width=30)
        self.entry_historia.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    def _create_billing_form_frame(self, parent_container: ttk.Frame):
        """Crea la instancia del formulario de detalles."""
        self.billing_form = BillingFormView(parent_container)
        self.billing_form.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
    
    def _bind_events(self):
        """Vincula los eventos de la GUI a los manejadores del controlador de forma segura."""
        if self.entry_historia:
            self.entry_historia.bind("<Return>", self.handlers.on_enter_pressed)

        if self.billing_form:
            id_widget = self.billing_form.get_id_widget()
            if id_widget:
                id_widget.bind("<Control-c>", self.handlers.on_copy_id)

        self.root.bind("<Control-n>", self.handlers.on_new_billing_request)

    def update_patient_details(self, patient_data: Optional[Dict[str, Any]]):
        """Delega la actualización de la vista al componente de formulario."""
        if self.billing_form:
            self.billing_form.update_view(patient_data)

    def get_history_entry_widget(self) -> Optional[ttk.Entry]:
        """Expone el campo de historia para control de foco externo."""
        return self.entry_historia
        
    def start(self):
        """Inicia el bucle principal de la aplicación."""
        if self.entry_historia:
            self.entry_historia.focus_set()
        self.root.mainloop()