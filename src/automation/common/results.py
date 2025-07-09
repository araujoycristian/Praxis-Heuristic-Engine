# src/automation/common/results.py

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from src.automation.common.states import TaskState


class TaskResultStatus(Enum):
    """Define el resultado final de una tarea de automatización."""
    SUCCESS = auto()
    FAILED_RETRY_LIMIT = auto()
    FAILED_UNRECOVERABLE = auto()
    FAILED_UNEXPECTED_ERROR = auto()


@dataclass(frozen=True)
class TaskResult:
    """
    Representa el resultado final de una única tarea de automatización.
    Es un objeto inmutable que comunica el desenlace desde el Automator
    hacia el Orchestrator.
    """
    status: TaskResultStatus
    task_identifier: str
    message: Optional[str] = None
    failed_at_state: Optional[TaskState] = None