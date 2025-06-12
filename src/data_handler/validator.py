import logging
import pandas as pd
from configparser import ConfigParser
from src.utils.dataframe_helpers import sanitize_column_name
from src.core.constants import ConfigSections, LogicalFields

class DataValidator:
    """
    Valida la integridad de los datos, asegurando que las columnas esenciales no sean nulas.
    """
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.required_logical_fields = [
            LogicalFields.NUMERO_HISTORIA,
            LogicalFields.DIAGNOSTICO_PRINCIPAL,
            LogicalFields.FECHA_INGRESO,
            LogicalFields.MEDICO_TRATANTE,
            LogicalFields.EMPRESA_ASEGURADORA,
            LogicalFields.CONTRATO_EMPRESA,
            LogicalFields.ESTRATO
        ]

    def validate_data(self, data: pd.DataFrame, profile_config: ConfigParser) -> tuple[pd.DataFrame, pd.DataFrame]:
        self.logger.info("Iniciando validación de datos para columnas requeridas.")
        if data.empty:
            self.logger.info("El DataFrame de entrada está vacío, no hay nada que validar.")
            return data, data.copy()
            
        mapping = profile_config[ConfigSections.COLUMN_MAPPING]
        
        required_sanitized_cols = [
            sanitize_column_name(mapping[key]) for key in self.required_logical_fields if key in mapping
        ]
        
        missing_cols = [col for col in required_sanitized_cols if col not in data.columns]
        if missing_cols:
            self.logger.error(f"Faltan columnas esenciales para la validación en el DataFrame: {missing_cols}")
            return pd.DataFrame(columns=data.columns), data

        invalid_mask = data[required_sanitized_cols].isnull().any(axis=1)
        valid_df = data[~invalid_mask]
        invalid_df = data[invalid_mask]

        self.logger.info(f"Validación completada. Filas válidas: {len(valid_df)}. Filas inválidas: {len(invalid_df)}.")
        return valid_df, invalid_df