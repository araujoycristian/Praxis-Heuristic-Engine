# src/automation/strategies/remote/remote_control.py

import logging
import subprocess
import sys
import time

import pyperclip
from src.core.exceptions import ClipboardError, FocusError

# --- Importación Condicional ---
if sys.platform == 'win32':
    try:
        from pywinauto import Desktop
        from pywinauto.findwindows import ElementNotFoundError
    except ImportError:
        raise ImportError("pywinauto no está instalado. Por favor, instálalo con 'pip install pywinauto'")

class RemoteControlFacade:
    """
    Fachada que abstrae el control de ventanas para diferentes sistemas operativos.
    Proporciona una API unificada y robusta para interactuar con una ventana remota.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.window_id = None      # Para Linux (ID de xdotool)
        self.window_handle = None  # Para Windows (objeto de pywinauto)

    def find_and_focus_window(self, title: str) -> None:
        """
        Busca una ventana por su título y la trae al frente (le da el foco).
        """
        self.logger.info(f"Buscando y enfocando ventana con título: '{title}' en '{sys.platform}'")

        if sys.platform.startswith('linux'):
            try:
                result = subprocess.run(
                    ['xdotool', 'search', '--limit', '1', '--name', title],
                    capture_output=True, text=True, check=True
                )
                self.window_id = result.stdout.strip()
                if not self.window_id:
                    raise FileNotFoundError

                self.logger.info(f"Ventana encontrada en Linux con ID: {self.window_id}")
                subprocess.run(['xdotool', 'windowactivate', self.window_id], check=True)
                self.wait(0.5)

            except (FileNotFoundError, subprocess.CalledProcessError):
                self.logger.critical(f"No se pudo encontrar la ventana '{title}' con xdotool.")
                raise FocusError(f"No se pudo encontrar la ventana '{title}' con xdotool.")

        elif sys.platform == 'win32':
            try:
                desktop = Desktop(backend='uia')
                self.window_handle = desktop.window(title=title)
                self.window_handle.wait("exists", timeout=10)
                self.window_handle.set_focus()
                self.logger.info("Ventana encontrada y enfocada en Windows.")
            except ElementNotFoundError:
                self.logger.critical(f"pywinauto no encontró la ventana '{title}'.")
                raise FocusError(f"No se pudo encontrar la ventana '{title}' con pywinauto.")
        else:
            raise NotImplementedError(f"El control remoto no está implementado para: {sys.platform}")

    def _ensure_focus_windows(self) -> None:
        """Helper para asegurar el foco en un entorno Windows."""
        if not self.window_handle.is_active():
            self.logger.warning("Ventana perdió el foco. Intentando recuperarlo...")
            self.window_handle.set_focus()
            self.wait(0.1)
            if not self.window_handle.is_active():
                raise FocusError("No se pudo recuperar el foco de la ventana en Windows.")

    def _ensure_focus_linux(self) -> None:
        """Helper para asegurar el foco en un entorno Linux."""
        try:
            active_window_id = subprocess.check_output(['xdotool', 'getactivewindow']).strip().decode()
            if self.window_id != active_window_id:
                self.logger.warning("Ventana perdió el foco. Intentando recuperarlo...")
                subprocess.run(['xdotool', 'windowactivate', self.window_id], check=True)
                self.wait(0.1)
                active_window_id = subprocess.check_output(['xdotool', 'getactivewindow']).strip().decode()
                if self.window_id != active_window_id:
                    raise FocusError("No se pudo recuperar el foco de la ventana en Linux.")
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            raise FocusError("Falló la dependencia 'xdotool' al verificar el foco.") from e

    def _ensure_focus(self) -> None:
        """Valida y recupera el foco de la ventana antes de cada acción."""
        self.logger.debug("Asegurando el foco de la ventana...")
        if self.window_handle is None and self.window_id is None:
            raise FocusError("La ventana no ha sido inicializada. Llama a 'find_and_focus_window' primero.")

        if sys.platform == 'win32':
            self._ensure_focus_windows()
        elif sys.platform.startswith('linux'):
            self._ensure_focus_linux()
        
        self.logger.debug("Foco de la ventana asegurado.")

    def wait(self, seconds: float) -> None:
        """Pausa la ejecución durante un número determinado de segundos."""
        self.logger.debug(f"Pausando ejecución por {seconds:.2f} segundos.")
        time.sleep(seconds)

    def type_keys(self, keys: str) -> None:
        """Envía una secuencia de teclas a la ventana con foco garantizado."""
        self._ensure_focus()
        self.logger.info(f"Enviando teclas: '{keys}'")
        if sys.platform.startswith('linux'):
            subprocess.run(['xdotool', 'type', '--window', self.window_id, '--clearmodifiers', keys], check=True)
        elif sys.platform == 'win32':
            self.window_handle.type_keys(keys, with_spaces=True)
        else:
            raise NotImplementedError(f"type_keys no implementado para: {sys.platform}")

    def read_clipboard_with_sentinel(self, delay_sec: float = 0.2) -> str:
        """
        Lee el portapapeles de forma fiable utilizando un valor centinela.
        """
        self._ensure_focus()
        sentinel = f"__SENTINEL_{time.monotonic()}__"
        
        try:
            pyperclip.copy(sentinel)
        except pyperclip.PyperclipException as e:
            raise ClipboardError("Fallo técnico al copiar el centinela al portapapeles.") from e

        # Envía la copia a través de un método que ya garantiza el foco
        self.type_keys('^c')
        self.wait(delay_sec)

        try:
            content = pyperclip.paste()
        except pyperclip.PyperclipException as e:
            raise ClipboardError("Fallo técnico al leer el contenido del portapapeles.") from e

        if content == sentinel:
            raise ClipboardError("La operación de copia no tuvo efecto (el centinela persiste).")
            
        self.logger.debug(f"Lectura de portapapeles exitosa. Contenido: '{content[:50]}...'")
        return content