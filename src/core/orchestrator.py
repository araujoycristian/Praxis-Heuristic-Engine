# src/core/orchestrator.py

import logging
from configparser import ConfigParser, NoOptionError, NoSectionError
from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd

from src.automation.abc.automator_interface import AutomatorInterface
from src.config_loader import ConfigLoader
from src.core.constants import ConfigKeys, ConfigSections, LogicalFields
from src.core.models import FacturacionData
from src.data_handler.filter import DataFilterer
from src.data_handler.loader import ExcelLoader
from src.data_handler.validator import DataValidator
from src.utils.dataframe_helpers import sanitize_column_name


class Orchestrator:
    """
    El cerebro de la aplicación. Coordina las diferentes capas para ejecutar
    el flujo completo del proceso de facturación.

    Responsabilidades:
    1. Cargar la configuración del perfil.
    2. Orquestar el pipeline de datos (cargar, filtrar, validar, transformar).
    3. Invocar la capa de automatización con las tareas validadas.
    4. Manejar errores de alto nivel y el flujo general de la aplicación.
    """

    def __init__(
        self,
        config_loader: ConfigLoader,
        data_loader: ExcelLoader,
        data_filterer: DataFilterer,
        data_validator: DataValidator,
        automator: AutomatorInterface = None,
    ):
        """
        Inicializa el Orchestrator con sus dependencias.

        Args:
            config_loader: Objeto para cargar perfiles de configuración.
            data_loader: Objeto para cargar datos desde Excel.
            data_filterer: Objeto para filtrar los datos cargados.
            data_validator: Objeto para validar la integridad de los datos.
            automator: Objeto que implementa la interfaz de automatización.
        """
        self.config_loader = config_loader
        self.data_loader = data_loader
        self.data_filterer = data_filterer
        self.data_validator = data_validator
        self.automator = automator
        self.logger = logging.getLogger(self.__class__.__name__)
        self.output_dir = Path("data/output")

    def run(self, profile_name: str, input_file_path: Path):
        """
        Ejecuta el proceso completo de orquestación.

        Args:
            profile_name: El nombre del perfil de configuración a utilizar.
            input_file_path: La ruta al archivo Excel de entrada.
        """
        self.logger.info(
            f"Iniciando orquestación con perfil '{profile_name}' y archivo '{input_file_path}'."
        )

        try:
            # --- Fase de Datos ---
            profile_config = self.config_loader.load_profile(profile_name)
            self._validate_profile_config(profile_config, profile_name)

            raw_df = self.data_loader.load_data(
                file_path=input_file_path,
                sheet_name=profile_config.get(
                    ConfigSections.DATA_SOURCE, ConfigKeys.SHEET_NAME
                ),
                header_row=profile_config.getint(
                    ConfigSections.DATA_SOURCE, ConfigKeys.HEADER_ROW
                ),
            )
            filtered_df = self.data_filterer.apply_criteria(raw_df, profile_config)
            valid_df, invalid_df = self.data_validator.validate_data(
                filtered_df, profile_config
            )

            if not invalid_df.empty:
                self.logger.warning(
                    f"{len(invalid_df)} filas fueron descartadas por datos inválidos/faltantes."
                )
                self._export_error_report(invalid_df, profile_config)

            if valid_df.empty:
                self.logger.info(
                    "No se encontraron registros válidos para procesar. Finalizando."
                )
                return

            facturacion_tasks = self._transform_to_dataclasses(valid_df, profile_config)
            self.logger.info(
                f"Se han preparado {len(facturacion_tasks)} tareas de facturación listas para automatizar."
            )

            # --- Fase de Automatización ---
            if self.automator and facturacion_tasks:
                self.logger.info("Iniciando la fase de automatización...")
                try:
                    self.automator.initialize(profile_config)
                    self.automator.process_billing_tasks(facturacion_tasks)
                except Exception as e:
                    self.logger.critical(
                        f"Error fatal en la fase de automatización: {e}", exc_info=True
                    )
                finally:
                    # Garantiza que los recursos del automator se liberen siempre.
                    self.automator.shutdown()
                self.logger.info("Fase de automatización finalizada.")
            else:
                self.logger.info(
                    "Omitiendo fase de automatización: no hay tareas válidas o no se configuró un automator."
                )

            self.logger.info("Orquestación finalizada exitosamente.")

        except (ValueError, NoSectionError, NoOptionError) as e:
            self.logger.critical(f"Error de configuración en el perfil '{profile_name}': {e}")
            raise
        except Exception as e:
            self.logger.critical(
                f"Ha ocurrido un error fatal durante la orquestación: {e}", exc_info=True
            )
            raise

    def _validate_profile_config(self, config: ConfigParser, profile_name: str):
        """Valida que el perfil de configuración contenga las secciones y claves necesarias."""
        self.logger.info(f"Validando la estructura del perfil '{profile_name}'.")

        required_sections = [
            ConfigSections.DATA_SOURCE,
            ConfigSections.COLUMN_MAPPING,
        ]
        for section in required_sections:
            if not config.has_section(section):
                raise NoSectionError(
                    f"La sección requerida '[{section}]' falta en el perfil."
                )

        required_keys_in_datasource = [ConfigKeys.SHEET_NAME, ConfigKeys.HEADER_ROW]
        for key in required_keys_in_datasource:
            if not config.has_option(ConfigSections.DATA_SOURCE, key):
                raise NoOptionError(
                    f"La clave requerida '{key}' falta en la sección '[{ConfigSections.DATA_SOURCE}]'.",
                    ConfigSections.DATA_SOURCE,
                )

        self.logger.info("La estructura del perfil es válida.")

    def _export_error_report(
        self, invalid_df: pd.DataFrame, profile_config: ConfigParser
    ):
        """Genera un archivo Excel con las filas inválidas y el motivo del rechazo."""
        error_dir = self.output_dir / "errors"
        error_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        report_path = error_dir / f"error_report_{timestamp}.xlsx"

        self.logger.info(f"Generando reporte de errores en: {report_path}")

        report_df = invalid_df.copy()
        report_df["Motivo_Rechazo"] = "Faltan datos en una o más columnas requeridas."

        mapping = profile_config[ConfigSections.COLUMN_MAPPING]
        reverse_rename_map = {
            sanitize_column_name(v): v for k, v in mapping.items()
        }
        cols_to_rename = {
            k: v for k, v in reverse_rename_map.items() if k in report_df.columns
        }
        report_df.rename(columns=cols_to_rename, inplace=True)

        try:
            report_df.to_excel(report_path, index=False, engine="openpyxl")
            self.logger.info("Reporte de errores guardado exitosamente.")
        except Exception as e:
            self.logger.error(f"No se pudo guardar el reporte de errores: {e}")

    def _transform_to_dataclasses(
        self, dataframe: pd.DataFrame, profile_config: ConfigParser
    ) -> List[FacturacionData]:
        """Transforma un DataFrame validado en una lista de objetos FacturacionData."""
        self.logger.info(
            f"Iniciando transformación de {len(dataframe)} filas de DataFrame a Dataclasses."
        )
        tasks = []
        mapping = profile_config[ConfigSections.COLUMN_MAPPING]
        sane_mapping = {key: sanitize_column_name(val) for key, val in mapping.items()}

        for row in dataframe.itertuples(index=False):
            try:
                task_data = {
                    LogicalFields.NUMERO_HISTORIA: str(
                        getattr(row, sane_mapping[LogicalFields.NUMERO_HISTORIA])
                    ),
                    LogicalFields.DIAGNOSTICO_PRINCIPAL: str(
                        getattr(row, sane_mapping[LogicalFields.DIAGNOSTICO_PRINCIPAL])
                    ),
                    LogicalFields.FECHA_INGRESO: pd.to_datetime(
                        getattr(row, sane_mapping[LogicalFields.FECHA_INGRESO])
                    ).date(),
                    LogicalFields.MEDICO_TRATANTE: str(
                        getattr(row, sane_mapping[LogicalFields.MEDICO_TRATANTE])
                    ),
                    LogicalFields.EMPRESA_ASEGURADORA: str(
                        getattr(row, sane_mapping[LogicalFields.EMPRESA_ASEGURADORA])
                    ),
                    LogicalFields.CONTRATO_EMPRESA: str(
                        getattr(row, sane_mapping[LogicalFields.CONTRATO_EMPRESA])
                    ),
                    LogicalFields.ESTRATO: str(
                        getattr(row, sane_mapping[LogicalFields.ESTRATO])
                    ),
                    LogicalFields.DIAGNOSTICO_ADICIONAL_1: self._get_optional_field(
                        row, sane_mapping.get(LogicalFields.DIAGNOSTICO_ADICIONAL_1)
                    ),
                    LogicalFields.DIAGNOSTICO_ADICIONAL_2: self._get_optional_field(
                        row, sane_mapping.get(LogicalFields.DIAGNOSTICO_ADICIONAL_2)
                    ),
                    LogicalFields.DIAGNOSTICO_ADICIONAL_3: self._get_optional_field(
                        row, sane_mapping.get(LogicalFields.DIAGNOSTICO_ADICIONAL_3)
                    ),
                }
                tasks.append(FacturacionData(**task_data))
            except AttributeError as e:
                self.logger.error(
                    f"Error de atributo al transformar fila. Es probable que falte un mapeo en [ColumnMapping] del perfil. Error: {e}"
                )
            except Exception as e:
                self.logger.error(
                    f"Error inesperado al transformar una fila. Fila: {row._asdict()}. Error: {e}"
                )

        self.logger.info(
            f"Transformación completada. Se crearon {len(tasks)} objetos FacturacionData."
        )
        return tasks

    def _get_optional_field(
        self, row: tuple, sane_col_name: str | None
    ) -> str | None:
        """Obtiene el valor de un campo opcional de una fila, manejando valores nulos."""
        if not sane_col_name:
            return None
        value = getattr(row, sane_col_name, None)
        return None if pd.isna(value) else str(value)