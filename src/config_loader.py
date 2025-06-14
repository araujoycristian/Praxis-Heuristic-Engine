import configparser
import logging
from pathlib import Path

class ConfigLoader:
    """
    Responsable de leer y parsear archivos de perfil .ini usando pathlib.
    Abstrae la interacción con el sistema de archivos y la librería configparser.
    """
    def __init__(self, profiles_dir: str | Path = 'config/profiles'):
        self.profiles_dir = Path(profiles_dir)
        self.logger = logging.getLogger(self.__class__.__name__)

    def load_profile(self, profile_name: str) -> configparser.ConfigParser:
        """
        Carga un perfil de configuración específico por su nombre.

        Args:
            profile_name: El nombre del perfil sin la extensión .ini.

        Returns:
            Un objeto ConfigParser con los datos del perfil cargado.

        Raises:
            FileNotFoundError: Si el archivo de perfil no se encuentra.
        """
        profile_path = self.profiles_dir / f"{profile_name}.ini"
        self.logger.info(f"Cargando perfil de configuración desde: {profile_path}")

        if not profile_path.exists():
            self.logger.error(f"El archivo de perfil '{profile_path}' no fue encontrado.")
            raise FileNotFoundError(f"El archivo de perfil '{profile_path}' no fue encontrado.")

        parser = configparser.ConfigParser()
        parser.read(profile_path, encoding='utf-8')
        self.logger.info(f"Perfil '{profile_name}' cargado exitosamente.")
        return parser