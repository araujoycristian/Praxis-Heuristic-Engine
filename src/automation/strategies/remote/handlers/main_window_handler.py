# src/automation/strategies/remote/handlers/main_window_handler.py

"""
Este módulo define el MainWindowHandler, un componente esencial que encapsula
toda la lógica de interacción con la ventana principal del software de facturación.
"""

import logging
from configparser import ConfigParser, NoSectionError

from src.automation.strategies.remote.remote_control import RemoteControlFacade
from src.core.exceptions import PatientIDMismatchError
from src.core.models import FacturacionData


class MainWindowHandler:
    """
    Encapsula la lógica de negocio para las acciones realizadas en la ventana
    principal del Software de Facturación (SF), como la búsqueda y validación
    de pacientes.
    """

    def __init__(self, remote_control: RemoteControlFacade, config: ConfigParser):
        """
        Inicializa el handler con sus dependencias y carga la configuración
        específica para la automatización desde el perfil.

        Args:
            remote_control: La fachada para interactuar con la GUI.
            config: El objeto de configuración cargado desde el perfil .ini.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.remote_control = remote_control
        self.config = config

        # Carga de parámetros de temporización desde la configuración.
        self._generic_delay = self.config.getfloat('AutomationTimeouts', 'generic_action_delay_ms', fallback=100) / 1000.0
        self._patient_load_wait = self.config.getfloat('AutomationTimeouts', 'patient_load_wait_ms', fallback=3000) / 1000.0

        # --- MEJORA CLAVE: Carga de Secuencias de Teclas desde Configuración ---
        # Se externaliza la lógica de navegación a los perfiles .ini para
        # desacoplar al bot de los cambios en el layout de la GUI.
        try:
            self._nav_to_id_sequence = self.config.get(
                'AutomationSequences',
                'nav_to_id_field',
                fallback='{TAB}'  # Valor por defecto seguro si la clave no existe.
            )
            self.logger.info(f"Secuencia de navegación al campo ID cargada: '{self._nav_to_id_sequence}'")
        except NoSectionError:
            self.logger.warning(
                "La sección [AutomationSequences] no se encontró en el perfil. "
                "Usando valores de navegación por defecto. Se recomienda añadirla."
            )
            self._nav_to_id_sequence = '{TAB}'

    def ensure_initial_state(self) -> None:
        """
        Asegura que la GUI esté en un estado inicial conocido antes de
        procesar una nueva tarea, intentando cerrar diálogos inesperados.
        """
        self.logger.info("Reseteando la GUI a un estado inicial conocido...")
        self.remote_control.type_keys('{ESC 3}')
        self.remote_control.wait(0.5)
        self.logger.info("Estado inicial de la GUI preparado para la siguiente tarea.")

    def find_patient(self, task: FacturacionData) -> None:
        """
        Orquesta el flujo completo de búsqueda y validación de un paciente.
        """
        self.logger.info(f"Buscando paciente con historia clínica: {task.numero_historia}")

        self.remote_control.type_keys(task.numero_historia)
        self.remote_control.wait(self._generic_delay)

        self.remote_control.type_keys('{ENTER}')

        self.logger.info(f"Esperando {self._patient_load_wait:.2f} segundos a que carguen los datos del paciente...")
        self.remote_control.wait(self._patient_load_wait)

        # La validación ahora usará la secuencia de navegación cargada desde el .ini
        self.validate_patient_loaded(task)

        self.logger.info("Búsqueda y validación del paciente completadas.")

    def validate_patient_loaded(self, task: FacturacionData) -> None:
        """
        Valida que el paciente correcto se ha cargado en la GUI.
        Navega al campo de ID y compara su contenido con los datos esperados.
        """
        self.logger.info(f"Iniciando validación para el paciente con ID: {task.identificacion}")

        # Se utiliza la secuencia de navegación leída desde el perfil en lugar de un valor codificado.
        self.remote_control.type_keys(self._nav_to_id_sequence)
        self.remote_control.wait(0.2)

        found_id = self.remote_control.read_clipboard_with_sentinel()
        expected_id = task.identificacion.strip()

        if found_id.strip() != expected_id:
            self.logger.error(f"¡FALLO DE VALIDACIÓN! ID Esperado: '{expected_id}', Encontrado: '{found_id.strip()}'")
            raise PatientIDMismatchError(expected_id=expected_id, found_id=found_id.strip())

        self.logger.info(f"VALIDACIÓN EXITOSA: El paciente '{expected_id}' se ha cargado correctamente.")

    def initiate_new_billing(self) -> None:
        """
        Envía la combinación de teclas para iniciar un nuevo proceso de facturación.
        """
        self.logger.info("Iniciando nuevo proceso de facturación (Ctrl+N)...")
        self.remote_control.type_keys('^n')
        self.remote_control.wait(1.5)
        self.logger.info("Comando para nuevo proceso de facturación enviado.")