# src/automation/strategies/remote/automator.py

import logging
from configparser import ConfigParser, NoOptionError, NoSectionError
from datetime import datetime
from pathlib import Path
from typing import List

from src.automation.abc.automator_interface import AutomatorInterface
from src.automation.common.results import TaskResult, TaskResultStatus
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
        self.main_window_handler: MainWindowHandler | None = None
        self.max_retries: int = 0

    def initialize(self, config: ConfigParser) -> None:
        """
        Establece la conexión con la aplicación de destino y, si tiene éxito,
        inicializa todos los handlers necesarios, inyectando sus dependencias.
        """
        self.logger.info("Inicializando el automator remoto...")
        self.config = config

        try:
            window_title = self.config.get(
                ConfigSections.AUTOMATION, "window_title"
            )
            self.facade.find_and_focus_window(window_title)
            self.logger.info(
                "Conexión con la ventana de destino establecida exitosamente."
            )

            self.main_window_handler = MainWindowHandler(
                remote_control=self.facade, config=self.config
            )
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
            raise

    def process_billing_tasks(self, tasks: List[FacturacionData]) -> List[TaskResult]:
        task_count = len(tasks)
        self.logger.info(f"Iniciando el procesamiento de {task_count} tarea{'s' if task_count != 1 else ''}.")
        
        results: List[TaskResult] = []

        if not self.main_window_handler:
            raise RuntimeError("El automator no puede procesar tareas porque el handler principal no fue inicializado.")

        for i, task in enumerate(tasks, 1):
            self.logger.info(
                f"--- [ Tarea {i}/{task_count} ] Procesando Historia Clínica: {task.numero_historia} ---"
            )

            current_state = TaskState.READY_FOR_NEW_TASK
            retry_count = 0
            
            while True:
                self.logger.debug(f"Estado actual: {current_state.name}, Reintentos: {retry_count}")
                
                try:
                    if current_state == TaskState.READY_FOR_NEW_TASK:
                        retry_count = 0
                        current_state = TaskState.ENSURING_INITIAL_STATE

                    elif current_state == TaskState.ENSURING_INITIAL_STATE:
                        self.main_window_handler.ensure_initial_state()
                        current_state = TaskState.FINDING_PATIENT

                    elif current_state == TaskState.FINDING_PATIENT:
                        self.main_window_handler.find_patient(task)
                        current_state = TaskState.INITIATING_NEW_BILLING

                    elif current_state == TaskState.INITIATING_NEW_BILLING:
                        self.main_window_handler.initiate_new_billing()
                        current_state = TaskState.TASK_SUCCESSFUL

                    elif current_state == TaskState.TASK_SUCCESSFUL:
                        self.logger.info(f"Tarea para la historia {task.numero_historia} COMPLETADA con éxito.")
                        results.append(TaskResult(
                            status=TaskResultStatus.SUCCESS,
                            task_identifier=task.numero_historia
                        ))
                        break

                    elif current_state == TaskState.TASK_FAILED:
                        self.logger.error(f"Tarea para la historia {task.numero_historia} FALLÓ y no se pudo recuperar.")
                        break

                except (ApplicationStateNotReadyError, ClipboardError) as e:
                    self.logger.warning(f"Error REINTENTABLE en estado {current_state.name}: {e}")
                    if retry_count < self.max_retries:
                        retry_count += 1
                        self.logger.info(f"Intentando de nuevo... (Intento {retry_count}/{self.max_retries})")
                        self.facade.wait(1.0)
                    else:
                        self.logger.error(f"Se alcanzó el máximo de reintentos ({self.max_retries}). La tarea ha fallado.")
                        results.append(TaskResult(
                            status=TaskResultStatus.FAILED_RETRY_LIMIT,
                            task_identifier=task.numero_historia,
                            message=str(e),
                            failed_at_state=current_state
                        ))
                        current_state = TaskState.TASK_FAILED
                
                except PatientIDMismatchError as e:
                    self.logger.critical(f"Error CRÍTICO NO REINTENTABLE en estado {current_state.name}: {e}")
                    results.append(TaskResult(
                        status=TaskResultStatus.FAILED_UNRECOVERABLE,
                        task_identifier=task.numero_historia,
                        message=str(e),
                        failed_at_state=current_state
                    ))
                    current_state = TaskState.TASK_FAILED

                except Exception as e:
                    self.logger.critical(
                        f"Error INESPERADO en estado {current_state.name}. La tarea ha fallado. Error: {e}",
                        exc_info=True,
                    )

                    # --- INICIO: LÓGICA DE CAPTURA DE PANTALLA ---
                    try:
                        # Define una ruta base para las capturas, consistente con la estructura del proyecto.
                        screenshot_dir = Path("data/output/screenshots")
                        
                        # Limpia el identificador de la tarea para crear un nombre de archivo seguro.
                        safe_task_id = "".join(
                            c for c in task.numero_historia if c.isalnum() or c in ('-', '_')
                        ).rstrip()

                        # Construye un nombre de archivo descriptivo para el diagnóstico.
                        filename = (
                            f"FAILURE_{datetime.now().strftime('%Y%m%d_%H%M%S')}_"
                            f"{safe_task_id}_{current_state.name}.png"
                        )
                        file_path = screenshot_dir / filename
                        
                        # Delega la acción a la fachada.
                        self.facade.take_screenshot(file_path)

                    except Exception as screenshot_err:
                        # Si la captura falla, no debe detener el flujo principal de reporte de errores.
                        self.logger.warning(
                            "ATENCIÓN: Falló el intento de tomar la captura de pantalla de diagnóstico. "
                            f"El proceso de reporte continuará. Error de captura: {screenshot_err}"
                        )
                    # --- FIN: LÓGICA DE CAPTURA DE PANTALLA ---

                    results.append(
                        TaskResult(
                            status=TaskResultStatus.FAILED_UNEXPECTED_ERROR,
                            task_identifier=task.numero_historia,
                            message=str(e),
                            failed_at_state=current_state,
                        )
                    )
                    current_state = TaskState.TASK_FAILED

        self.logger.info("Procesamiento de todas las tareas finalizado.")
        return results

    def shutdown(self) -> None:
        self.logger.info("Finalizando el automator remoto y liberando recursos.")
        self.config = None
        self.main_window_handler = None