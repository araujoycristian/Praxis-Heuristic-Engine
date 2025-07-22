# saf/ui/views/billing_form_view.py
"""
Este módulo define el componente de la Vista 'BillingFormView'.

Actuando como un bloque de construcción fundamental en la arquitectura MVC del
Stunt Action Facsimile (SAF), este componente encapsula todos los widgets
relacionados con la visualización de los detalles del paciente y de la factura.

Su diseño promueve la reutilización y el aislamiento, permitiendo que la
ventana principal (MainWindow) lo contenga sin necesidad de conocer los
detalles de su implementación interna. Es un componente "tonto" por diseño,
cuya única responsabilidad es mostrar los datos que se le proporcionan.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional

class BillingFormView(ttk.Frame):
    """
    Un Frame de Tkinter que agrupa y gestiona los campos de entrada y etiquetas
    para los detalles de facturación.
    
    Este componente se construye de forma data-driven a partir de un mapeo
    explícito (FIELD_MAPPING), lo que desacopla la lógica interna del modelo
    de la presentación visual en la interfaz de usuario.
    """
    
    # Este diccionario es la única fuente de verdad para la construcción de la UI.
    # Desacopla el nombre del atributo en el modelo de datos (la clave) del texto
    # que se muestra en la etiqueta de la UI (el valor). Esta decisión de diseño
    # mejora drásticamente la claridad y la mantenibilidad a largo plazo.
    FIELD_MAPPING: Dict[str, str] = {
        "identificacion": "Identificación:",
        "nombre1": "Primer Nombre:",
        "nombre2": "Segundo Nombre:",
        "apellido1": "Primer Apellido:",
        "apellido2": "Segundo Apellido:",
        "empresa": "Empresa:",
        "contrato": "Contrato (Empresa):",
        "estrato": "Estrato:",
        "medico": "Médico Tratante:",
        "diagnostico_principal": "Diagnóstico Principal:"
    }

    def __init__(self, parent: tk.Widget, *args, **kwargs):
        """
        Inicializa el Frame del formulario de facturación.

        Args:
            parent: El widget padre (normalmente la ventana principal) que contendrá este frame.
            *args: Argumentos posicionales para el constructor de ttk.Frame.
            **kwargs: Argumentos de palabra clave para el constructor de ttk.Frame.
        """
        super().__init__(parent, *args, **kwargs)
        
        # Diccionario para mantener referencias a los widgets de entrada,
        # usando la clave lógica del modelo como identificador.
        self.patient_data_widgets: Dict[str, tk.Entry] = {}
        
        # Llama al método privado que construye la interfaz de usuario.
        self._create_widgets()

    def _create_widgets(self) -> None:
        """
        Construye y posiciona todos los widgets (etiquetas y campos de entrada)
        dentro de este componente, basándose en la estructura definida en FIELD_MAPPING.
        """
        details_frame = ttk.LabelFrame(self, text="Detalles del Paciente Cargado")
        details_frame.grid(row=0, column=0, padx=0, pady=0, sticky="ew")

        # Se itera sobre el mapeo para construir la UI de forma programática.
        # Esto asegura que la UI y la lógica de datos estén siempre sincronizadas.
        for i, (field_key, label_text) in enumerate(self.FIELD_MAPPING.items()):
            
            # Creación de la etiqueta (Label)
            ttk.Label(details_frame, text=label_text).grid(
                row=i, column=0, padx=5, pady=5, sticky="w"
            )
            
            # Creación del campo de entrada (Entry)
            # Se usa 'readonly' para que el usuario (el bot) pueda seleccionarlo
            # y copiar de él, pero no modificarlo directamente.
            entry = ttk.Entry(details_frame, width=50, state='readonly')
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            
            # Se almacena una referencia al widget usando su clave lógica.
            self.patient_data_widgets[field_key] = entry

    def update_view(self, data: Optional[Dict[str, Any]]) -> None:
        """
        Puebla o limpia todos los campos de entrada con la información proporcionada.

        Este método actúa como la API principal para que el mundo exterior (el
        controlador) actualice el estado visual de este componente.

        Args:
            data: Un diccionario donde las claves coinciden con las definidas en
                  FIELD_MAPPING. Si es None, todos los campos se limpiarán.
        """
        for key, widget in self.patient_data_widgets.items():
            # Se habilita el widget temporalmente para poder modificar su contenido.
            widget.config(state='normal')
            
            # Si `data` existe, se busca la clave; de lo contrario, el contenido es vacío.
            content = str(data.get(key, "")) if data else ""
            
            widget.delete(0, tk.END)
            widget.insert(0, content)
            
            # Se vuelve a poner en modo 'readonly' para el usuario.
            widget.config(state='readonly')
            
    def get_id_widget(self) -> Optional[tk.Widget]:
        """
        Expone una referencia directa al widget del campo de identificación.

        Este método es necesario para que la ventana principal pueda vincular
        eventos específicos (como <Control-c>) a este widget en particular.

        Returns:
            El widget de Tkinter para el campo 'identificacion', o None si no existe.
        """
        return self.patient_data_widgets.get("identificacion")