# src/automation/strategies/remote/remote_control.py
"""
Este módulo define la Fachada de Control Remoto, una abstracción crucial
que proporciona una API unificada para interactuar con ventanas de escritorio
en diferentes sistemas operativos (Windows y Linux).
"""

import logging
import subprocess
import sys
import time
from pathlib import Path

import pyperclip
from pywinauto.keyboard import send_keys

from src.core.exceptions import ClipboardError, FocusError

# --- Importación Segura de Dependencias de Captura de Pantalla ---
try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None  # Permite que el módulo se importe sin fallar si Pillow no está.

# --- Importación Condicional Específica de Windows ---
if sys.platform == 'win32':
    try:
        from pywinauto import Desktop
        from pywinauto.findwindows import ElementNotFoundError
    except ImportError:
        # En Windows, pywinauto es una dependencia dura.
        raise ImportError("pywinauto no está instalado. Por favor, instálalo con 'pip install pywinauto'")


class RemoteControlFacade:
    """
    Fachada que abstrae el control de ventanas para diferentes S.O.
    Proporciona una API unificada y robusta para interactuar con una ventana.
    """

    def __init__(self):
        """Inicializa la fachada y sus propiedades de estado."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.window_id = None      # Para Linux (ID de ventana de xdotool)
        self.window_handle = None  # Para Windows (objeto de pywinauto)

    def find_and_focus_window(self, title: str) -> None:
        """
        Busca una ventana por su título y la trae al frente (le da el foco).

        Args:
            title: El título exacto de la ventana a buscar.

        Raises:
            FocusError: Si la ventana no puede ser encontrada tras el timeout.
            NotImplementedError: Si el sistema operativo no está soportado.
        """
        self.logger.info(f"Buscando y enfocando ventana con título: '{title}' en '{sys.platform}'")

        if sys.platform.startswith('linux'):
            try:
                result = subprocess.run(
                    ['xdotool', 'search', '--limit', '1', '--name', title],
                    capture_output=True, text=True, check=True, timeout=10
                )
                self.window_id = result.stdout.strip()
                if not self.window_id:
                    raise FileNotFoundError

                self.logger.info(f"Ventana encontrada en Linux con ID: {self.window_id}")
                # 'windowactivate' es más robusto que 'windowfocus'
                subprocess.run(['xdotool', 'windowactivate', self.window_id], check=True)
                self.wait(0.5)

            except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                self.logger.critical(f"No se pudo encontrar la ventana '{title}' con xdotool. Error: {e}")
                raise FocusError(f"No se pudo encontrar la ventana '{title}' con xdotool.") from e

        elif sys.platform == 'win32':
            try:
                desktop = Desktop(backend='uia')
                self.window_handle = desktop.window(title=title)
                self.window_handle.wait("exists", timeout=10)
                self.window_handle.set_focus()
                self.logger.info("Ventana encontrada y enfocada en Windows.")
            except ElementNotFoundError as e:
                self.logger.critical(f"pywinauto no encontró la ventana '{title}'.")
                raise FocusError(f"No se pudo encontrar la ventana '{title}' con pywinauto.") from e
        else:
            raise NotImplementedError(f"El control remoto no está implementado para: {sys.platform}")

    def _ensure_focus(self) -> None:
        """Valida y recupera el foco de la ventana antes de cada acción crítica."""
        self.logger.debug("Asegurando el foco de la ventana...")
        if self.window_handle is None and self.window_id is None:
            raise FocusError("La ventana no ha sido inicializada. Llama a 'find_and_focus_window' primero.")

        if sys.platform == 'win32':
            if not self.window_handle.is_active():
                self.logger.warning("Ventana perdió el foco. Intentando recuperarlo...")
                self.window_handle.set_focus()
                self.wait(0.1)
                if not self.window_handle.is_active():
                    raise FocusError("No se pudo recuperar el foco de la ventana en Windows.")
        elif sys.platform.startswith('linux'):
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
        
        self.logger.debug("Foco de la ventana asegurado.")

    def wait(self, seconds: float) -> None:
        """Pausa la ejecución durante un número determinado de segundos."""
        self.logger.debug(f"Pausando ejecución por {seconds:.2f} segundos.")
        time.sleep(seconds)

    def type_keys(self, keys: str) -> None:
        """
        Envía una secuencia de teclas a la ventana con foco garantizado.

        Delega la interpretación de teclas especiales (ej. {ENTER}, {TAB}, ^c)
        al módulo `pywinauto.keyboard`, que proporciona una implementación
        robusta y multiplataforma.

        Args:
            keys: La cadena de texto y secuencias a enviar.
        """
        self._ensure_focus()
        self.logger.info(f"Enviando teclas: '{keys}'")
        # send_keys se encarga de la lógica de backend y traduce las secuencias
        # especiales al comando correcto, solucionando el error original.
        send_keys(keys, with_spaces=True, pause=0.05)

    def read_clipboard_with_sentinel(self, delay_sec: float = 0.2) -> str:
        """
        Lee el portapapeles de forma fiable utilizando un valor centinela.

        Args:
            delay_sec: Pequeña pausa para permitir que la GUI procese la copia.

        Returns:
            El contenido del portapapeles.

        Raises:
            ClipboardError: Si la operación de copia/lectura falla.
        """
        self._ensure_focus()
        sentinel = f"__SENTINEL_{time.monotonic()}__"
        
        try:
            pyperclip.copy(sentinel)
        except pyperclip.PyperclipException as e:
            raise ClipboardError("Fallo técnico al copiar el centinela al portapapeles.") from e

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

    def take_screenshot(self, file_path: Path) -> None:
        """
        Toma una captura de pantalla del escritorio completo y la guarda.
        Actualmente soportado solo en Windows. En otros S.O., omite la acción.

        Args:
            file_path: La ruta completa donde se guardará la imagen.
        """
        self.logger.info(f"Intentando tomar captura de pantalla de diagnóstico. Destino: {file_path}")

        if sys.platform == 'win32':
            if not ImageGrab:
                self.logger.error("La librería Pillow (PIL) no está disponible. No se puede tomar la captura.")
                raise ImportError("Pillow no está instalado, imposible tomar captura de pantalla.")
            
            try:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                image = ImageGrab.grab(all_screens=True)
                image.save(file_path)
                self.logger.info("Captura de pantalla guardada exitosamente en Windows.")
            except Exception as e:
                self.logger.error(f"Falló la operación de tomar/guardar la captura de pantalla: {e}")
                raise
        else:
            self.logger.warning(
                f"La toma de capturas de pantalla no está implementada para el sistema operativo '{sys.platform}'. "
                "Se omite la acción."
            )