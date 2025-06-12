import logging
import pandas as pd
from configparser import ConfigParser
from src.utils.dataframe_helpers import sanitize_column_name
from src.core.constants import ConfigSections

class DataFilterer:
    """
    Aplica criterios de filtro a un DataFrame.
    Traduce los nombres de columna "sucios" del perfil a sus equivalentes "limpios"
    antes de interactuar con el DataFrame pre-saneado.
    """
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def apply_criteria(self, data: pd.DataFrame, profile_config: ConfigParser) -> pd.DataFrame:
        if ConfigSections.FILTER_CRITERIA not in profile_config:
            self.logger.warning(f"No se encontró la sección [{ConfigSections.FILTER_CRITERIA}] en el perfil. Devolviendo datos sin filtrar.")
            return data

        self.logger.info("Iniciando aplicación de criterios de filtro.")
        filtered_df = data.copy()
        
        criteria = profile_config[ConfigSections.FILTER_CRITERIA]
        mapping = profile_config[ConfigSections.COLUMN_MAPPING]

        for key, value in criteria.items():
            if key not in mapping:
                self.logger.warning(f"La clave de filtro '{key}' no tiene un mapeo de columna en [{ConfigSections.COLUMN_MAPPING}]. Se omitirá.")
                continue

            original_excel_col = mapping[key]
            sanitized_col = sanitize_column_name(original_excel_col)

            if sanitized_col not in filtered_df.columns:
                self.logger.warning(f"La columna '{sanitized_col}' (de '{original_excel_col}') no existe en el DataFrame. Se omitirá este filtro.")
                continue
            
            initial_rows = len(filtered_df)
            column_series = filtered_df[sanitized_col].astype(str).str.upper().str.strip()
            criterion_value = str(value).upper().strip()
            
            filtered_df = filtered_df[column_series == criterion_value]
            
            self.logger.info(
                f"Filtro '{original_excel_col}' == '{criterion_value}': {initial_rows} -> {len(filtered_df)} filas."
            )

        self.logger.info(f"Filtrado completado. {len(filtered_df)} filas cumplen todos los criterios.")
        return filtered_df