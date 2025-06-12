import argparse
import logging
import sys
from pathlib import Path

from src.logger_setup import setup_logging
from src.config_loader import ConfigLoader
from src.data_handler.loader import ExcelLoader
from src.data_handler.filter import DataFilterer
from src.data_handler.validator import DataValidator
from src.core.orchestrator import Orchestrator

def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="Bot de Automatización de Facturación Médica.")
    parser.add_argument(
        "--profile",
        type=str,
        required=True,
        help="Nombre del perfil de configuración a usar (ej. dev_nancy)."
    )
    parser.add_argument(
        "--input-file",
        type=Path,
        required=True,
        help="Ruta al archivo Excel de entrada."
    )
    args = parser.parse_args()

    logger.info(f"Aplicación iniciada con perfil '{args.profile}' y archivo '{args.input_file}'.")

    try:
        config_loader = ConfigLoader()
        excel_loader = ExcelLoader()
        data_filterer = DataFilterer()
        data_validator = DataValidator()
        
        orchestrator = Orchestrator(
            config_loader=config_loader,
            data_loader=excel_loader,
            data_filterer=data_filterer,
            data_validator=data_validator
        )

        orchestrator.run(
            profile_name=args.profile,
            input_file_path=args.input_file
        )
    except FileNotFoundError as e:
        logger.critical(f"Error de archivo no encontrado: {e}. Verifique que las rutas en los argumentos y el perfil son correctas.")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"La aplicación ha terminado con un error no controlado: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()