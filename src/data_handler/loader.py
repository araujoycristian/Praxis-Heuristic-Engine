import logging
import pandas as pd
from pathlib import Path
from src.utils.dataframe_helpers import sanitize_column_name

class ExcelLoader:
    """
    Responsable única de cargar datos desde un archivo Excel a un DataFrame.
    Sanea los nombres de las columnas inmediatamente después de la carga para
    garantizar un estado interno limpio y predecible.
    """
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def _sanitize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Renombra las columnas del DataFrame utilizando la utilidad de saneamiento central.
        """
        rename_map = {col: sanitize_column_name(col) for col in df.columns}
        df = df.rename(columns=rename_map)
        self.logger.info("Nombres de columnas saneados para uso interno.")
        self.logger.debug(f"Nuevas columnas: {df.columns.tolist()}")
        return df

    def load_data(self, file_path: Path, sheet_name: str, header_row: int) -> pd.DataFrame:
        """
        Carga los datos de una hoja de cálculo y sanea sus columnas.
        """
        self.logger.info(f"Iniciando carga de datos desde '{file_path}', hoja '{sheet_name}'.")
        try:
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                header=header_row - 1,
                engine='openpyxl'
            )
            self.logger.info(f"Carga exitosa. Se leyeron {len(df)} filas en total.")
            df = self._sanitize_columns(df)
            return df
        except FileNotFoundError:
            self.logger.error(f"Error: El archivo '{file_path}' no fue encontrado.")
            raise
        except ValueError as e:
            if f"Worksheet named '{sheet_name}' not found" in str(e):
                self.logger.error(f"Error: La hoja '{sheet_name}' no existe en '{file_path}'.")
            else:
                self.logger.error(f"Error de valor al leer el Excel: {e}")
            raise