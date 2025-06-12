# src/automation/strategies/remote/remote_control.py

import logging
import subprocess
import sys
import time

# --- Importación Condicional ---
# Solo importamos pywinauto si estamos en Windows.
if sys.platform == 'win32':
    try:
        from pywinauto.desktop import Desktop
        from pywinauto.findwindows import ElementNotFoundError
    except ImportError:
        # Si pywinauto no está instalado en Windows, es un error fatal.
        raise ImportError("pywinauto no está instalado. Por favor, instálalo con 'pip install pywinauto'")

class RemoteControlFacade:
    """
    Fachada que abstrae el control de ventanas para diferentes sistemas operativos.

    Proporciona una API unificada para interactuar con una ventana por su título,
    ocultando la complejidad de si se usa 'xdotool' (en Linux) o 'pywinauto'
    (en Windows).
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.window_id = None  # Para Linux (ID de xdotool)
        self.window_handle = None  # Para Windows (objeto de pywinauto)

    def find_and_focus_window(self, title: str) -> None:
        """
        Busca una ventana por su título y la trae al frente (le da el foco).

        Args:
            title: El título exacto de la ventana a buscar.

        Raises:
            RuntimeError: Si la ventana no se encuentra en el sistema operativo correspondiente.
        """
        self.logger.info(f"Buscando y enfocando ventana con título: '{title}' usando el método para '{sys.platform}'")

        if sys.platform.startswith('linux'):
            try:
                # 1. Buscar el ID de la ventana usando xdotool
                # El comando busca cualquier ventana cuyo nombre contenga el título.
                # --limit 1 devuelve solo el primer resultado.
                result = subprocess.run(
                    ['xdotool', 'search', '--limit', '1', '--name', title],
                    capture_output=True, text=True, check=True
                )
                self.window_id = result.stdout.strip()
                if not self.window_id:
                    raise FileNotFoundError # Provocamos un error para entrar en el except

                self.logger.info(f"Ventana encontrada en Linux con ID: {self.window_id}")

                # 2. Activar (enfocar) la ventana
                subprocess.run(['xdotool', 'windowactivate', self.window_id], check=True)
                time.sleep(0.5) # Pequeña pausa para asegurar que la ventana está activa

            except (FileNotFoundError, subprocess.CalledProcessError):
                self.logger.critical(f"'xdotool' no encontró la ventana o no está instalado.")
                raise RuntimeError(
                    f"No se pudo encontrar la ventana '{title}' usando xdotool. "
                    "Asegúrate de que xdotool esté instalado y que la ventana esté abierta."
                )

        elif sys.platform == 'win32':
            try:
                desktop = Desktop(backend='uia')
                self.window_handle = desktop.window(title=title)
                self.window_handle.wait("exists", timeout=10)
                self.window_handle.set_focus()
                self.logger.info("Ventana encontrada y enfocada en Windows.")
            except ElementNotFoundError:
                self.logger.critical(f"pywinauto no encontró la ventana.")
                raise RuntimeError(
                    f"No se pudo encontrar la ventana '{title}' usando pywinauto. "
                    "Asegúrate de que la ventana esté abierta."
                )
        else:
            raise NotImplementedError(f"El control remoto no está implementado para el sistema operativo: {sys.platform}")

    def type_keys(self, keys: str) -> None:
        """
        Envía una secuencia de teclas a la ventana que previamente fue enfocada.

        (Esta función se usará en el Hito 2)

        Args:
            keys: La cadena de texto o secuencia de teclas a enviar.
        """
        self.logger.info(f"Enviando teclas: '{keys}'")
        if sys.platform.startswith('linux'):
            if not self.window_id:
                raise RuntimeError("No hay ninguna ventana enfocada en Linux. Llama a 'find_and_focus_window' primero.")
            # --clearmodifiers resetea Ctrl, Alt, etc., antes de escribir.
            subprocess.run(['xdotool', 'type', '--window', self.window_id, '--clearmodifiers', keys], check=True)

        elif sys.platform == 'win32':
            if not self.window_handle:
                raise RuntimeError("No hay ninguna ventana enfocada en Windows. Llama a 'find_and_focus_window' primero.")
            # with_spaces=True es importante para manejar espacios correctamente.
            self.window_handle.type_keys(keys, with_spaces=True)
        else:
            raise NotImplementedError(f"El control remoto no está implementado para el sistema operativo: {sys.platform}")