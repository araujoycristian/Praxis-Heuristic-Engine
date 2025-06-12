import logging
import sys

def setup_logging():
    """
    Configura el sistema de logging para toda la aplicación.
    Establece un formato consistente y dirige la salida a la consola.
    Debe ser llamada una sola vez al inicio de la aplicación desde main.py.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)-25s - %(levelname)-8s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )
    # Silenciar logs demasiado verbosos de librerías de terceros si es necesario
    # logging.getLogger("nombre_de_libreria_ruidosa").setLevel(logging.WARNING)