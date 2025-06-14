# src/automation/strategies/remote/automator.py

import logging
from configparser import ConfigParser, NoOptionError, NoSectionError
from typing import List

from src.automation.abc.automator_interface import AutomatorInterface
from src.automation.strategies.remote.handlers.main_window_handler import (
    MainWindowHandler,
)
from src.automation.strategies.remote.remote_control import RemoteControlFacade
from src.core.constants import ConfigSections
from src.core.models import FacturacionData


class RemoteAutomator(AutomatorInterface):
    """
    Orquesta el flujo de trabajo de automatización delegando tareas a handlers
    especializados (ej. MainWindowHandler). Actúa como el "director de orquesta"
    para el proceso de interacción con la GUI.
    """

    def __init__(self):
        """
        Prepara el automator, inicializando sus componentes principales.
        En esta fase, los handlers aún no se instancian, ya que dependen
        de una conexión exitosa con la ventana de destino.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.facade = RemoteControlFacade()
        self.config: ConfigParser | None = None

        # Los handlers se inicializarán en la fase de `initialize`.
        # Se definen aquí con type hints para claridad y autocompletado.
        self.main_window_handler: MainWindowHandler | None = None

    def initialize(self, config: ConfigParser) -> None:
        """
        Establece la conexión con la aplicación de destino y, si tiene éxito,
        inicializa todos los handlers necesarios, inyectando sus dependencias.
        Este método debe ser llamado antes de procesar cualquier tarea.

        Args:
            config: El objeto de configuración del perfil cargado.

        Raises:
            RuntimeError: Si la configuración es inválida o si la ventana
                          de destino no se puede encontrar.
        """
        self.logger.info("Inicializando el automator remoto...")
        self.config = config

        try:
            # 1. Obtener el título de la ventana desde la configuración.
            window_title = self.config.get(
                ConfigSections.AUTOMATION, "window_title"
            )

            # 2. Usar la fachada para encontrar y enfocar la ventana.
            # Si esto falla, lanzará una excepción y detendrá la inicialización.
            self.facade.find_and_focus_window(window_title)
            self.logger.info(
                "Conexión con la ventana de destino establecida exitosamente."
            )

            # 3. Una vez conectados, instanciar los handlers.
            # Se aplica el principio de Inyección de Dependencias, pasando a cada
            # handler las herramientas que necesita para trabajar.
            self.main_window_handler = MainWindowHandler(
                remote_control=self.facade, config=self.config
            )

            # En el futuro, aquí se instanciarían otros handlers:
            # self.ingreso_handler = IngresoHandler(...)
            # self.suministros_handler = SuministrosHandler(...)

            self.logger.info("Todos los handlers de automatización han sido inicializados.")

        except (NoSectionError, NoOptionError) as e:
            self.logger.critical(
                f"La configuración de automatización es inválida. "
                f"Asegúrese de que la sección '[{ConfigSections.AUTOMATION}]' y la clave 'window_title' existan en el perfil."
            )
            raise RuntimeError("Configuración de automatización incompleta.") from e
        except Exception as e:
            self.logger.critical(
                f"Falló la inicialización del automator: {e}", exc_info=True
            )
            # Re-lanzamos la excepción para que el orquestador principal la capture y termine la ejecución.
            raise

    def process_billing_tasks(self, tasks: List[FacturacionData]) -> None:
        """
        Itera sobre una lista de tareas y ejecuta el flujo de automatización
        completo para cada una, delegando las acciones a los handlers.

        Incluye un manejo de errores robusto para que el fallo en una tarea no
        detenga el procesamiento del resto de la lista.

        Args:
            tasks: La lista de objetos FacturacionData a procesar.
        """
        task_count = len(tasks)
        self.logger.info(f"Iniciando el procesamiento de {task_count} tarea{'s' if task_count != 1 else ''}.")

        # Guard Clause: Verifica que la inicialización fue exitosa antes de continuar.
        if not self.main_window_handler:
            raise RuntimeError(
                "El automator no puede procesar tareas porque el handler principal no fue inicializado. "
                "Verifique los logs de la fase de inicialización."
            )

        for i, task in enumerate(tasks, 1):
            self.logger.info(
                f"--- [ Tarea {i}/{task_count} ] Procesando Historia Clínica: {task.numero_historia} ---"
            )
            try:
                # El flujo de trabajo se define aquí, llamando a los métodos de los handlers en secuencia.
                # Para el Hito 2, el flujo es simple: buscar paciente e iniciar nueva factura.
                self.main_window_handler.find_patient(task)
                self.main_window_handler.initiate_new_billing()

                # Aquí se añadirían más pasos en el futuro:
                # self.ingreso_handler.fill_data(task)
                # self.suministros_handler.process_medicines(task)
                # ... etc.

                self.logger.info(
                    f"Tarea para la historia {task.numero_historia} completada exitosamente."
                )

            except Exception as e:
                # Si ocurre un error en CUALQUIER paso de la tarea actual, se captura aquí.
                # Se registra el error detalladamente, pero el bucle `for` continuará con la siguiente tarea.
                self.logger.error(
                    f"Falló la tarea para la historia {task.numero_historia}. Error: {e}",
                    exc_info=True,
                )
                # En el futuro, este bloque podría tomar una captura de pantalla del error
                # y añadir la tarea a un reporte de fallos.
                self.logger.warning(
                    f"Saltando a la siguiente tarea debido al error anterior."
                )

        self.logger.info("Procesamiento de todas las tareas finalizado.")

    def shutdown(self) -> None:
        """
        Libera los recursos y limpia el estado del automator.
        Es buena práctica limpiar las referencias para ayudar al recolector
        de basura y evitar estados inconsistentes si se reutilizara el objeto.
        """
        self.logger.info("Finalizando el automator remoto y liberando recursos.")
        self.config = None
        self.main_window_handler = None
        # self.ingreso_handler = None ... etc.