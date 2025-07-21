# saf/ui/main_window.py
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional

class MainWindow:
    """
    La Vista en nuestra arquitectura MVC.
    
    Responsabilidades:
    - Construir y disponer todos los widgets de la GUI (usando Tkinter).
    - Exponer métodos para actualizar el contenido de los widgets (ej. poblar datos del paciente).
    - Vincular eventos de los widgets (clics, pulsaciones de teclas) a los métodos del Controlador.
    - No contiene lógica de negocio. Es "tonta" por diseño.
    """
    WINDOW_TITLE = "SAF - Stunt Action Facsimile v0.1"

    def __init__(self, root: tk.Tk, handlers):
        self.root = root
        self.handlers = handlers
        self.root.title(self.WINDOW_TITLE)

        # Diccionario para mantener una referencia a nuestros widgets de datos de paciente
        self.patient_data_widgets: Dict[str, tk.Entry] = {}

        self._create_widgets()
        self._bind_events()

    def _create_widgets(self):
        """Crea y organiza todos los widgets en la ventana principal."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # --- Sección de Búsqueda ---
        search_frame = ttk.LabelFrame(main_frame, text="Búsqueda de Paciente")
        search_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        ttk.Label(search_frame, text="Nro. Historia:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_historia = ttk.Entry(search_frame, width=30)
        self.entry_historia.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # --- Sección de Datos del Paciente ---
        details_frame = ttk.LabelFrame(main_frame, text="Detalles del Paciente Cargado")
        details_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # PUNTO CIEGO DE DISEÑO #1: EL ORDEN DE CREACIÓN DETERMINA EL ORDEN DE TABULACIÓN.
        # Creamos los widgets en el orden exacto en que el bot espera navegar con TAB.
        # 1. Identificación
        # 2. Nombre1, Nombre2, Apellido1, Apellido2, etc.
        # Las claves deben coincidir con las del JSON `test_scenarios.json`.
        fields_to_display = [
            "IDENTIFIC:", "NOMBRE1:", "NOMBRE2:", "APELLIDO1:", "APELLIDO2:",
            "EMPRESA:", "CONTRATO EMP:", "ESTRATO:"
        ]
        
        for i, field_key in enumerate(fields_to_display):
            label_text = f"{field_key.replace(':', '').replace('EMP', '(Empresa)').strip()}:"
            ttk.Label(details_frame, text=label_text).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            
            # Usamos Entry en modo 'readonly' para poder darle foco y copiar de él,
            # a diferencia de un Label que no puede recibir foco.
            entry = ttk.Entry(details_frame, width=50, state='readonly')
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            self.patient_data_widgets[field_key] = entry
    
    def _bind_events(self):
        """Vincula los eventos de la GUI a los manejadores del controlador."""
        # Al presionar Enter en el campo de historia, se llama al manejador correspondiente.
        self.entry_historia.bind("<Return>", self.handlers.on_enter_pressed)

        # PUNTO CLAVE: Vinculamos Ctrl+C solo al campo de identificación.
        # Esto simula con precisión el flujo del bot: TAB, TAB, Ctrl+C.
        id_widget = self.patient_data_widgets.get("IDENTIFIC:")
        if id_widget:
            id_widget.bind("<Control-c>", self.handlers.on_copy_id)

    def update_patient_details(self, patient_data: Optional[Dict[str, Any]]):
        """Puebla o limpia los campos de detalles del paciente."""
        for key, widget in self.patient_data_widgets.items():
            # Habilitamos temporalmente para escribir, luego volvemos a deshabilitar.
            widget.config(state='normal')
            
            content = ""
            if patient_data and key in patient_data:
                content = patient_data[key]
            
            widget.delete(0, tk.END)
            widget.insert(0, str(content))
            widget.config(state='readonly')

    def start(self):
        """Inicia el bucle principal de la aplicación."""
        self.root.mainloop()