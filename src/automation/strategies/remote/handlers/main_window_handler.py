# src/automation/strategies/remote/handlers/main_window_handler.py

import logging
from configparser import ConfigParser

from src.core.models import FacturacionData
from src.automation.strategies.remote.remote_control import RemoteControlFacade
from src.core.constants import ConfigSections

class MainWindowHandler:
    """
    Encapsula todas las interacciones de automatización con la ventana
    principal del Software de Facturación (SF).
    """

    def __init__(self, remote_control: RemoteControlFacade, config: ConfigParser):
        """
        Inicializa el handler con las dependencias necesarias.

        Args:
            remote_control: La fachada para el control de bajo nivel (teclado, foco).
            config: El objeto de configuración para acceder a timeouts y otros parámetros.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.remote_control = remote_control
        self.config = config

        # Cargamos los timeouts desde la configuración para usarlos después
        self._generic_delay = self.config.getfloat('AutomationTimeouts', 'generic_action_delay_ms', fallback=100) / 1000.0
        self._patient_load_wait = self.config.getfloat('AutomationTimeouts', 'patient_load_wait_ms', fallback=3000) / 1000.0

    def find_patient(self, task: FacturacionData) -> None:
        """
        Realiza la acción de buscar un paciente en el SF.

        Args:
            task: El objeto de datos que contiene el número de historia a buscar.
        """
        self.logger.info(f"Buscando paciente con historia clínica: {task.numero_historia}")
        
        # 1. Aseguramos que el foco esté en la ventana correcta
        #    (El automator ya se encarga de esto al inicio, pero es una buena práctica
        #    si el flujo se vuelve más complejo).
        
        # 2. Escribir el número de historia en el campo correspondiente
        #    Usamos pywinauto (a través de la fachada) para teclear.
        self.remote_control.type_keys(task.numero_historia)
        self.remote_control.wait(self._generic_delay) # Pequeña pausa

        # 3. Presionar Enter para que el SF cargue los datos del paciente
        self.remote_control.type_keys('{ENTER}')

        # 4. ESPERAR a que el SF procese y cargue la información. ¡Este paso es CRÍTICO!
        self.logger.info(f"Esperando {self._patient_load_wait:.2f} segundos a que carguen los datos del paciente...")
        self.remote_control.wait(self._patient_load_wait)

        # Por ahora, no implementamos la validación con Ctrl+C que mencionaste.
        # Primero aseguramos que el flujo básico funcione. La añadiremos después.
        self.logger.info("Búsqueda de paciente completada.")

    def initiate_new_billing(self) -> None:
        """
        Presiona la combinación de teclas para iniciar un nuevo proceso de facturación.
        """
        self.logger.info("Iniciando nuevo proceso de facturación (Ctrl+N)...")
        # El símbolo '^' en pywinauto representa la tecla Ctrl.
        self.remote_control.type_keys('^n')
        self.remote_control.wait(self._patient_load_wait) # Esperamos a que la nueva ventana/pestaña aparezca
        self.logger.info("Comando para nuevo proceso de facturación enviado.")