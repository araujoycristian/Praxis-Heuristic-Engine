# src/core/exceptions.py

"""
Define el conjunto de excepciones personalizadas para la aplicación.

Este módulo centraliza todos los errores controlados que pueden ocurrir
durante el proceso de automatización. El uso de excepciones personalizadas
permite un manejo de errores más granular y explícito en las capas superiores,
como el `RemoteAutomator`.

La arquitectura de estas excepciones se basa en tres pilares:
1.  **Metadatos de Accionabilidad:** Cada excepción se autodescribe (¿es reintentable?).
2.  **Payloads Estructurados:** Transportan datos del error de forma limpia para su consumo
    programático (ej. en logs o reportes), no solo como un string.
3.  **Códigos de Error:** Un identificador único para cada tipo de error.
"""

class AutomationError(Exception):
    """
    Clase base para todas las excepciones de automatización del proyecto.

    Atributos:
        is_retryable (bool): Indica si la acción que causó este error puede ser
                             reintentada de forma segura. Por defecto es `False`.
        error_code (str): Un código único que identifica el tipo de error.
    """
    is_retryable: bool = False
    error_code: str = "E0000_UNKNOWN_AUTOMATION_ERROR"

    def __init__(self, message: str):
        # Prepend el código de error al mensaje para una identificación rápida en los logs.
        super().__init__(f"[{self.error_code}] {message}")
        self.payload = {}


# --- Excepciones de Lógica de Negocio y Estado (Generalmente no reintentables) ---

class ApplicationStateNotReadyError(AutomationError):
    """
    Lanzada si el estado de la aplicación no es el adecuado para iniciar una acción.
    Se considera reintentable, ya que el estado podría estar en transición (ej. la app está lenta).
    """
    is_retryable: bool = True
    error_code: str = "E1001_INVALID_STATE"


class PatientIDMismatchError(AutomationError):
    """
    Lanzada cuando la identificación en la GUI no coincide con los datos de entrada.
    Este error no es reintentable, ya que indica una discrepancia fundamental en los datos.
    """
    is_retryable: bool = False
    error_code: str = "E2001_ID_MISMATCH"

    def __init__(self, expected_id: str, found_id: str):
        message = (
            f"Incongruencia en la identificación del paciente. "
            f"Esperado: '{expected_id}', Encontrado: '{found_id}'."
        )
        super().__init__(message)
        # El payload contiene los datos estructurados para logging y análisis.
        self.payload = {
            'expected_id': expected_id,
            'found_id': found_id,
        }


class UnexpectedPopupError(AutomationError):
    """
    Lanzada al detectar un diálogo modal o pop-up inesperado que interrumpe el flujo.
    No es reintentable, ya que requiere una acción de manejo específica.
    """
    is_retryable: bool = False
    error_code: str = "E2002_UNEXPECTED_POPUP"

    def __init__(self, popup_text: str):
        message = f"Se ha detectado un pop-up inesperado. Texto: '{popup_text}'."
        super().__init__(message)
        self.payload = {'popup_text': popup_text}


# --- Excepciones de Interacción Técnica (Potencialmente reintentables) ---

class ClipboardError(AutomationError):
    """
    Lanzada cuando el mecanismo de copia/lectura del portapapeles falla.
    Este es un error técnico transitorio y, por lo tanto, es un candidato ideal para reintento.
    """
    is_retryable: bool = True
    error_code: str = "E3001_CLIPBOARD_FAILURE"


class FocusError(AutomationError):
    """
    Lanzada cuando no se puede establecer el foco en la ventana de destino.
    Es reintentable, ya que otra ventana podría haber robado el foco temporalmente.
    """
    is_retryable: bool = True
    error_code: str = "E3002_FOCUS_FAILURE"