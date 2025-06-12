# src/automation/abc/automator_interface.py

from abc import ABC, abstractmethod
from configparser import ConfigParser
from typing import List

from src.core.models import FacturacionData


class AutomatorInterface(ABC):
    """
    Define el contrato abstracto que todas las estrategias de automatización
    (ej. remota, local, de prueba) deben implementar.

    Este enfoque, basado en el Patrón de Diseño Strategy, permite al Orchestrator
    trabajar con cualquier automator sin conocer sus detalles internos,
    promoviendo un bajo acoplamiento y alta cohesión.
    """

    @abstractmethod
    def initialize(self, config: ConfigParser) -> None:
        """
        Prepara el automator para la ejecución.

        Esta fase es responsable de establecer la conexión con la aplicación
        de destino, ya sea encontrando su ventana, iniciando el proceso o
        cualquier otra configuración inicial necesaria.

        Args:
            config: El objeto ConfigParser que contiene los ajustes del perfil,
                    permitiendo al automator leer su propia configuración.

        Raises:
            Exception: Si la inicialización falla (ej. la ventana no se encuentra).
        """
        pass

    @abstractmethod
    def process_billing_tasks(self, tasks: List[FacturacionData]) -> None:
        """
        Ejecuta el bucle principal de automatización para una lista de tareas.

        Recibe una lista de objetos de datos limpios y validados y debe
        iterar sobre ellos, realizando las acciones de GUI correspondientes
        para cada uno.

        Args:
            tasks: Una lista de objetos FacturacionData, cada uno representando
                   una fila del Excel a procesar.
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """
        Realiza la limpieza de recursos al final del proceso.

        Es responsable de cerrar conexiones, liberar manejadores de ventanas
        o cualquier otra acción necesaria para terminar de forma elegante.
        Este método debe ser llamado incluso si la automatización falla.
        """
        pass