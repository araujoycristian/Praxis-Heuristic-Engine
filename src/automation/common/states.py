# src/automation/common/states.py
from enum import Enum, auto

class TaskState(Enum):
    """Define los estados posibles para el ciclo de vida de una tarea de automatización."""

    # Estado de preparación y transición
    READY_FOR_NEW_TASK = auto()

    # Estados de ejecución de acciones
    ENSURING_INITIAL_STATE = auto()
    FINDING_PATIENT = auto()
    INITIATING_NEW_BILLING = auto()
    # En futuros hitos, añadiríamos: NAVIGATING_TO_INGRESO, FILLING_INGRESO_DATA, etc.

    # Estados terminales (final del ciclo para una tarea)
    TASK_SUCCESSFUL = auto()
    TASK_FAILED = auto()
