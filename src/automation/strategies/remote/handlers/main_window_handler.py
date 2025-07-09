# src/automation/strategies/remote/handlers/main_window_handler.py

import logging
from configparser import ConfigParser

# AÑADIDO
from src.core.exceptions import PatientIDMismatchError
from src.core.models import FacturacionData

from src.automation.strategies.remote.remote_control import RemoteControlFacade

class MainWindowHandler:
    """
    Encapsula todas las interacciones de automatización con la ventana
    principal del Software de Facturación (SF).
    """

    def __init__(self, remote_control: RemoteControlFacade, config: ConfigParser):
        """
        Inicializa el handler con las dependencias necesarias.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.remote_control = remote_control
        self.config = config

        self._generic_delay = self.config.getfloat('AutomationTimeouts', 'generic_action_delay_ms', fallback=100) / 1000.0
        self._patient_load_wait = self.config.getfloat('AutomationTimeouts', 'patient_load_wait_ms', fallback=3000) / 1000.0

    # NUEVO MÉTODO
    def ensure_initial_state(self) -> None:
        """
        Asegura que la GUI esté en un estado inicial conocido antes de procesar una tarea.
        Intenta cerrar diálogos o menús inesperados enviando la tecla Escape.
        """
        self.logger.info("Reseteando la GUI a un estado inicial conocido...")
        self.remote_control.type_keys('{ESC 3}')
        self.remote_control.wait(0.5)
        self.logger.info("Estado inicial de la GUI preparado para la siguiente tarea.")

    # MÉTODO MODIFICADO
    def find_patient(self, task: FacturacionData) -> None:
        """
        Realiza la acción de buscar un paciente y VALIDA que se haya cargado correctamente.
        """
        self.logger.info(f"Buscando paciente con historia clínica: {task.numero_historia}")
        
        self.remote_control.type_keys(task.numero_historia)
        self.remote_control.wait(self._generic_delay)

        self.remote_control.type_keys('{ENTER}')

        self.logger.info(f"Esperando {self._patient_load_wait:.2f} segundos a que carguen los datos del paciente...")
        self.remote_control.wait(self._patient_load_wait)

        self.validate_patient_loaded(task)

        self.logger.info("Búsqueda y validación del paciente completadas.")

    # NUEVO MÉTODO
    def validate_patient_loaded(self, task: FacturacionData) -> None:
        """
        Valida que el paciente cargado en la GUI es el correcto.
        """
        self.logger.info(f"Iniciando validación para el paciente con ID: {task.identificacion}")

        self.remote_control.type_keys('{TAB 2}')
        self.remote_control.wait(0.2)

        found_id = self.remote_control.read_clipboard_with_sentinel()

        expected_id = task.identificacion.strip()
        if found_id.strip() != expected_id:
            self.logger.error(f"¡FALLO DE VALIDACIÓN! ID Esperado: '{expected_id}', Encontrado: '{found_id.strip()}'")
            raise PatientIDMismatchError(expected_id=expected_id, found_id=found_id.strip())

        self.logger.info(f"VALIDACIÓN EXITOSA: El paciente '{expected_id}' se ha cargado correctamente.")

    # MÉTODO MODIFICADO
    def initiate_new_billing(self) -> None:
        """
        Presiona la combinación de teclas para iniciar un nuevo proceso de facturación.
        """
        self.logger.info("Iniciando nuevo proceso de facturación (Ctrl+N)...")
        self.remote_control.type_keys('^n')
        self.remote_control.wait(1.5)
        self.logger.info("Comando para nuevo proceso de facturación enviado.")