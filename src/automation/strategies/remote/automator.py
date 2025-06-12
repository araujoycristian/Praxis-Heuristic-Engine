# src/automation/strategies/remote/automator.py

import logging
from configparser import ConfigParser, NoSectionError, NoOptionError
from typing import List

from src.automation.abc.automator_interface import AutomatorInterface
from src.core.constants import ConfigSections
from src.core.models import FacturacionData
from src.automation.strategies.remote.remote_control import RemoteControlFacade # <-- NUEVA IMPORTACIÓN


class RemoteAutomator(AutomatorInterface):
    """
    Implementación de la estrategia de automatización que delega el control
    de bajo nivel a una fachada, permitiendo la compatibilidad multiplataforma.
    """

    def __init__(self):
        """Inicializa el RemoteAutomator y su fachada de control."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.facade = RemoteControlFacade() # <-- INSTANCIAMOS LA FACHADA
        self.config = None

    def initialize(self, config: ConfigParser) -> None:
        """
        Inicializa el automator utilizando la fachada para encontrar y enfocar
        la ventana de destino.
        """
        self.logger.info("Inicializando el automator remoto...")
        self.config = config

        try:
            window_title = self.config.get(
                ConfigSections.AUTOMATION,
                'window_title'
            )
            # La complejidad del SO está ahora oculta detrás de esta simple llamada
            self.facade.find_and_focus_window(window_title)
            self.logger.info("El automator se ha conectado exitosamente a la ventana de destino.")

        except (NoSectionError, NoOptionError) as e:
            self.logger.critical(
                f"La configuración de automatización falta o está incompleta en el perfil. "
                f"Asegúrate de que la sección '[{ConfigSections.AUTOMATION}]' y la clave 'window_title' existan."
            )
            raise RuntimeError("Configuración de automatización incompleta.") from e
        except Exception as e:
            self.logger.critical(f"Ocurrió un error inesperado durante la inicialización: {e}", exc_info=True)
            # Re-lanzamos la excepción para que el orquestador la capture.
            raise

    def process_billing_tasks(self, tasks: List[FacturacionData]) -> None:
        """
        Marcador de posición para la lógica de automatización de tareas.
        (La implementación real se construirá en los siguientes hitos)
        """
        task_count = len(tasks)
        self.logger.info(
            f"Listo para procesar {task_count} tarea{'s' if task_count != 1 else ''}. "
            f"(La interacción con la GUI se implementará en el Hito 2)."
        )
        # Ejemplo de cómo se usará en el futuro:
        # for task in tasks:
        #     self.facade.type_keys(task.numero_historia)
        #     self.facade.type_keys("{ENTER}")
        #     time.sleep(2)
        pass

    def shutdown(self) -> None:
        """
        Finaliza el automator. En este caso no hay recursos que liberar
        explícitamente, pero mantenemos el método por contrato.
        """
        self.logger.info("Automator remoto finalizando.")
        self.config = None