# src/automation/strategies/remote/automator.py

import logging
from configparser import ConfigParser, NoOptionError, NoSectionError
from typing import List

from src.automation.abc.automator_interface import AutomatorInterface
from src.automation.common.states import TaskState
from src.automation.strategies.remote.handlers.main_window_handler import (
    MainWindowHandler,
)
from src.automation.strategies.remote.remote_control import RemoteControlFacade
from src.core.constants import ConfigSections
from src.core.exceptions import (
    ApplicationStateNotReadyError,
    ClipboardError,
    PatientIDMismatchError,
)
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

        # NUEVA LÍNEA: Inicializa el valor
        self.max_retries: int = 0

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

            # NUEVAS LÍNEAS: Lee el valor de reintentos desde el config
            self.max_retries = self.config.getint(
                "AutomationRetries", "max_retries", fallback=1
            )
            self.logger.info(
                f"Configuración de reintentos cargada: {self.max_retries} reintentos máximos por acción."
            )

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
        task_count = len(tasks)
        self.logger.info(f"Iniciando el procesamiento de {task_count} tarea{'s' if task_count != 1 else ''}.")

        if not self.main_window_handler:
            raise RuntimeError("El automator no puede procesar tareas porque el handler principal no fue inicializado.")

        for i, task in enumerate(tasks, 1):
            self.logger.info(
                f"--- [ Tarea {i}/{task_count} ] Procesando Historia Clínica: {task.numero_historia} ---"
            )

            # --- Motor de la Máquina de Estados para UNA Tarea ---
            current_state = TaskState.READY_FOR_NEW_TASK
            retry_count = 0
            
            # Este bucle representa el ciclo de vida de una única tarea.
            while True:
                self.logger.debug(f"Estado actual: {current_state.name}, Reintentos: {retry_count}")
                
                try:
                    # ---- Definición de Transiciones de Estado ----
                    if current_state == TaskState.READY_FOR_NEW_TASK:
                        retry_count = 0 # Resetea reintentos para la nueva tarea
                        current_state = TaskState.ENSURING_INITIAL_STATE

                    elif current_state == TaskState.ENSURING_INITIAL_STATE:
                        self.main_window_handler.ensure_initial_state()
                        current_state = TaskState.FINDING_PATIENT

                    elif current_state == TaskState.FINDING_PATIENT:
                        # find_patient ahora incluye la validación.
                        self.main_window_handler.find_patient(task)
                        current_state = TaskState.INITIATING_NEW_BILLING

                    elif current_state == TaskState.INITIATING_NEW_BILLING:
                        self.main_window_handler.initiate_new_billing()
                        # Por ahora, este es el último paso exitoso del Hito 3.
                        current_state = TaskState.TASK_SUCCESSFUL

                    # ---- Estados Terminales ----
                    elif current_state == TaskState.TASK_SUCCESSFUL:
                        self.logger.info(f"Tarea para la historia {task.numero_historia} COMPLETADA con éxito.")
                        break  # Sale del bucle `while` y pasa a la siguiente tarea en el `for`.

                    elif current_state == TaskState.TASK_FAILED:
                        self.logger.error(f"Tarea para la historia {task.numero_historia} FALLÓ y no se pudo recuperar.")
                        # Aquí se podría añadir la tarea a un reporte de fallos.
                        break # Sale del bucle `while` y pasa a la siguiente tarea.

                # ---- Manejo de Errores y Transiciones a Fallo/Reintento ----
                except (ApplicationStateNotReadyError, ClipboardError) as e:
                    self.logger.warning(f"Error REINTENTABLE en estado {current_state.name}: {e}")
                    if retry_count < self.max_retries:
                        retry_count += 1
                        self.logger.info(f"Intentando de nuevo... (Intento {retry_count}/{self.max_retries})")
                        self.remote_control.wait(1.0) # Pequeña pausa antes de reintentar
                    else:
                        self.logger.error(f"Se alcanzó el máximo de reintentos ({self.max_retries}). La tarea ha fallado.")
                        current_state = TaskState.TASK_FAILED
                
                except PatientIDMismatchError as e:
                    # Este error no es reintentable, va directo al fallo.
                    self.logger.critical(f"Error CRÍTICO NO REINTENTABLE en estado {current_state.name}: {e}")
                    current_state = TaskState.TASK_FAILED

                except Exception as e:
                    # Captura cualquier otro error inesperado para evitar que el script se detenga.
                    self.logger.critical(
                        f"Error INESPERADO en estado {current_state.name}. La tarea ha fallado. Error: {e}",
                        exc_info=True # Proporciona el traceback completo en los logs.
                    )
                    current_state = TaskState.TASK_FAILED

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