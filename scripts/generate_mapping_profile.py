# scripts/generate_mapping_profile.py

import argparse
import configparser
import logging
import re
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

# NOTA DE DISEÑO: Esta utilidad es deliberadamente autónoma y no importa desde `src/`
# para evitar acoplamientos no deseados entre las herramientas de script y la aplicación.

def sanitize_for_logical_name(header: str) -> str:
    """Sanea un encabezado para proponer un nombre lógico en Python."""
    if not isinstance(header, str):
        header = str(header)
    sanitized = header.strip().lower()
    sanitized = re.sub(r'[^a-z0-9_]', '_', sanitized)
    sanitized = re.sub(r'_+', '_', sanitized)
    return sanitized.strip('_')

def guess_logical_name(header: str, rules: dict) -> str | None:
    """
    Intenta adivinar el nombre lógico canónico basado en un conjunto de reglas de palabras clave.
    """
    header_lower = header.lower()
    for keyword, logical_name in rules.items():
        if keyword in header_lower:
            return logical_name
    return None

def main():
    """
    Punto de entrada del script.
    """
    # Configuración de logging a stderr para no contaminar la salida del .ini (stdout)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stderr)

    parser = argparse.ArgumentParser(
        description="Asistente inteligente que genera un borrador de la sección [ColumnMapping] de un perfil .ini a partir de un archivo Excel.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--input-file", required=True, type=Path, help="Ruta al archivo Excel que se va a analizar.")
    parser.add_argument("--profile", type=str, help="[Opcional] Nombre del perfil .ini del cual leer [DataSource] (ej. produccion_cliente_xyz).")
    parser.add_argument("--sheet-name", type=str, help="[Opcional] Nombre de la hoja a analizar. Anula el valor del perfil si se especifica.")
    parser.add_argument("--header-row", type=int, help="[Opcional] Número de la fila del encabezado (1-indexed). Anula el valor del perfil.")
    parser.add_argument("--output-file", type=Path, help="[Opcional] Ruta del archivo donde guardar el borrador. Si no se especifica, se imprime en consola.")
    
    args = parser.parse_args()

    # --- REGLAS HEURÍSTICAS: El "cerebro" del asistente ---
    # Mapea palabras clave (en minúsculas) a nuestros nombres lógicos canónicos.
    # El orden importa: reglas más específicas deben ir primero.
    KEYWORD_RULES = {
        'historia': 'numero_historia',
        'identif': 'identificacion', # Captura 'IDENTIFIC:'
        'cédula': 'identificacion',
        'cedula': 'identificacion',
        'médico': 'medico_tratante',
        'medico': 'medico_tratante',
        'profesional': 'medico_tratante',
        'diag ingreso': 'diagnostico_principal', # Captura 'DIAG INGRESO'
        'dx principal': 'diagnostico_principal',
        'dx adic1': 'diagnostico_adicional_1', # Captura 'DX ADICIONAL1:'
        'dx adic 2': 'diagnostico_adicional_2',
        'dx adic2': 'diagnostico_adicional_2',
        'dx adic 3': 'diagnostico_adicional_3',
        'dx adic3': 'diagnostico_adicional_3',
        'fec/ingreso': 'fecha_ingreso', # Captura 'FEC/INGRESO:'
        'fecha ing': 'fecha_ingreso',
        'empresa': 'empresa_aseguradora',
        'entidad': 'empresa_aseguradora',
        'contrato': 'contrato_empresa',
        'estrato': 'estrato',
        'pyp': 'pyp_for_filter',
        'cups': 'cups_for_filter',
        'especialidad': 'specialty_for_filter',
        'usuario': 'user_for_filter',
    }
    
    # --- LÓGICA HÍBRIDA PARA DETERMINAR LA CONFIGURACIÓN DE LECTURA ---
    sheet_name_to_use = args.sheet_name
    header_row_to_use = args.header_row

    if args.profile:
        try:
            profile_path = Path(f'config/profiles/{args.profile}.ini')
            if not profile_path.exists():
                raise FileNotFoundError(f"El archivo de perfil '{profile_path}' no fue encontrado.")
            
            config = configparser.ConfigParser()
            config.read(profile_path)
            
            logging.info(f"Leyendo [DataSource] del perfil '{args.profile}'...")
            
            # Solo se usan los valores del perfil si no fueron anulados por la CLI
            if not sheet_name_to_use and config.has_option('DataSource', 'sheet_name'):
                sheet_name_to_use = config.get('DataSource', 'sheet_name')
            if not header_row_to_use and config.has_option('DataSource', 'header_row'):
                header_row_to_use = config.getint('DataSource', 'header_row')

        except (FileNotFoundError, configparser.Error) as e:
            logging.error(f"No se pudo cargar la configuración desde el perfil: {e}. Abortando.")
            sys.exit(1)

    # Validar que tenemos la información necesaria para leer el Excel
    if header_row_to_use is None:
        logging.error("No se ha especificado la fila del encabezado. Usa --header-row o defínelo en un perfil con --profile.")
        sys.exit(1)

    # --- LECTURA DEL EXCEL Y ANÁLISIS ---
    try:
        logging.info(f"Analizando encabezados de '{args.input_file}'...")
        logging.info(f"Usando Hoja: '{sheet_name_to_use or 'Primera por defecto'}' | Fila de Encabezado: {header_row_to_use}")
        
        df = pd.read_excel(
            args.input_file,
            sheet_name=sheet_name_to_use, # pandas maneja None para la primera hoja
            header=header_row_to_use - 1, # pandas es 0-indexed
            nrows=0 # Solo leemos los encabezados, muy eficiente
        )
        
        if df.columns.duplicated().any():
            duplicates = df.columns[df.columns.duplicated()].tolist()
            logging.error(f"FATAL: El archivo Excel contiene nombres de columna duplicados: {duplicates}")
            logging.error("Esto indica un problema en los datos de origen que debe ser corregido. Abortando.")
            sys.exit(1)

        headers = df.columns.dropna().astype(str)
        
        # --- LÓGICA DE MAPEO Y DETECCIÓN DE CONFLICTOS ---
        guessed_mappings = {}
        unmapped_headers = []
        conflicts = defaultdict(list)
        
        for header in headers:
            guess = guess_logical_name(header, KEYWORD_RULES)
            if guess:
                if guess in guessed_mappings.values():
                    conflicts[guess].append(header)
                    original_header = [k for k, v in guessed_mappings.items() if v == guess]
                    if original_header:
                        conflicts[guess].append(original_header[0])
                        del guessed_mappings[original_header[0]]
                else:
                    guessed_mappings[header] = guess
            else:
                unmapped_headers.append(header)
        
        # --- GENERACIÓN DE LA SALIDA ESTRUCTURADA ---
        output_lines = ["[ColumnMapping]"]
        
        if guessed_mappings:
            output_lines.append("\n# === Mapeos Adivinados con Alta Confianza (Revisar) ===")
            for header, logical_name in sorted(guessed_mappings.items()):
                output_lines.append(f"{logical_name} = {header}")
        
        manual_review_needed = sorted(list(set(unmapped_headers + [h for sublist in conflicts.values() for h in sublist])))
        if manual_review_needed:
            output_lines.append("\n# === Requieren Atención Manual (Completar nombre lógico o eliminar) ===")
            for header in manual_review_needed:
                conflict_note = ""
                for logical, headers_in_conflict in conflicts.items():
                    if header in headers_in_conflict:
                        conflict_note = f" # ¡CONFLICTO! También coincide con '{logical}'"
                        break
                
                sanitized_proposal = sanitize_for_logical_name(header)
                output_lines.append(f"# Propuesta para: {header}{conflict_note}")
                output_lines.append(f"{sanitized_proposal} = {header}\n")

        output_content = "\n".join(output_lines)
        
        # --- RESUMEN EJECUTIVO (a stderr) ---
        logging.info("-" * 50)
        logging.info("Análisis de Mapeo Completado")
        logging.info(f"  - Total de columnas analizadas: {len(headers)}")
        logging.info(f"  - Mapeos automáticos exitosos: {len(guessed_mappings)}")
        logging.info(f"  - Columnas que requieren atención manual: {len(manual_review_needed)}")
        if conflicts:
            logging.warning("Se detectaron conflictos de mapeo:")
            for logical, headers_in_conflict in conflicts.items():
                logging.warning(f"  - El nombre lógico '{logical}' fue adivinado para: {list(set(headers_in_conflict))}")
        logging.info("-" * 50)

        # --- SALIDA FINAL (a stdout o archivo) ---
        if args.output_file:
            args.output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(args.output_file, 'w', encoding='utf-8') as f:
                f.write(output_content)
            logging.info(f"Borrador de mapeo guardado en: {args.output_file}")
        else:
            print("\n" + "="*20 + " INICIO DEL BORRADOR DE MAPEADO " + "="*20)
            print(output_content)
            print("="*20 + "  FIN DEL BORRADOR DE MAPEADO  " + "="*20)
            logging.info("\nCopia y pega este bloque en tu .ini. Edita los nombres lógicos (izquierda del '=') en la sección de atención manual.")

    except Exception as e:
        logging.error(f"Ha ocurrido un error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()