# scripts/anonymize_data.py

import argparse
import configparser
import logging
import re
import sys
from pathlib import Path

import pandas as pd
from faker import Faker

# --- UTILITIES ---
# NOTA DE DISEÑO: Estas funciones son una copia deliberada de las utilidades en `src/`
# para mantener este script autónomo y desacoplado del código fuente de la aplicación.
# Esto es una decisión consciente de diseño. Si se actualiza la versión en `src/`,
# esta también debe ser revisada.

def sanitize_column_name(col_name: str) -> str:
    """Sanea un nombre de columna para que sea un identificador válido y predecible."""
    if not isinstance(col_name, str):
        col_name = str(col_name)
    sanitized = col_name.strip()
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', sanitized)
    sanitized = re.sub(r'_+', '_', sanitized)
    return sanitized.rstrip('_')


class AnonymizerEngine:
    """
    Motor de anonimización que contiene la lógica y las reglas para transformar
    los datos de un DataFrame.
    """
    def __init__(self, seed=None):
        """
        Inicializa el motor con una instancia de Faker y las reglas de anonimización.
        Args:
            seed: Una semilla opcional para que los datos generados sean reproducibles.
        """
        self.fake = Faker('es_CO')  # Usar una localización mejora el realismo de los datos
        if seed:
            Faker.seed(seed)
        
        # Estado interno para contadores, asegurando IDs únicos en la muestra
        self._id_counter = 0

        # El "Libro de Reglas": mapea nombres lógicos a funciones de transformación.
        # Este es el corazón de la inteligencia del anonimizador.
        self.rules = {
            # --- Categoría 1: Identificadores Únicos (Sensibles) ---
            'numero_historia': self._next_id('HC-ANON'),
            'identificacion': self._next_id('CC-ANON'),

            # --- Categoría 2: Nombres Propios (Sensibles) ---
            'medico_tratante': lambda val: self.fake.name(),
            'nombre1': lambda val: self.fake.first_name(),
            'nombre2': lambda val: self.fake.first_name(),
            'apellido1': lambda val: self.fake.last_name(),
            'apellido2': lambda val: self.fake.last_name(),

            # --- Categoría 3: Datos de Contacto y Ubicación (Sensibles) ---
            'direccion': lambda val: self.fake.street_address(),
            'barrio': lambda val: self.fake.neighborhood(),
            'municipio_residencia': lambda val: self.fake.city(),
            'correo': lambda val: self.fake.email(),
            'tel_paciente': lambda val: self.fake.phone_number(),

            # --- Categoría 4: Fechas (Potencialmente Sensibles) ---
            'fecha_ingreso': lambda val: self.fake.date_between(start_date='-90d', end_date='today').strftime('%Y-%m-%d'),
            'fecha_nac': lambda val: self.fake.date_of_birth(minimum_age=1, maximum_age=90).strftime('%Y-%m-%d'),
            
            # --- Categoría 5: Códigos (Preservar formato) ---
            'diagnostico_principal': lambda val: self.fake.bothify(text='?###').upper(),
            'diagnostico_adicional_1': lambda val: self.fake.bothify(text='?###').upper(),
            'diagnostico_adicional_2': lambda val: self.fake.bothify(text='?###').upper(),
            'diagnostico_adicional_3': lambda val: self.fake.bothify(text='?###').upper(),
            'diag_egreso': lambda val: self.fake.bothify(text='?###').upper(),

            # --- Categoría 6: Datos a Preservar (Críticos para filtros y lógica) ---
            'user_for_filter': lambda val: val,
            'pyp_for_filter': lambda val: val,
            'cups_for_filter': lambda val: val,
            'specialty_for_filter': lambda val: val,
            'estrato': lambda val: val,
            'empresa_aseguradora': lambda val: val, 
            'contrato_empresa': lambda val: val,

            # --- Categoría 7: Regla por defecto para cualquier otra columna no especificada ---
            'default': lambda val: '[DATO_ANONIMIZADO]'
        }

    def _next_id(self, prefix: str):
        """Función de orden superior que devuelve un generador de IDs secuenciales."""
        def generator():
            self._id_counter += 1
            return f"{prefix}-{self._id_counter:04d}"
        return generator

    def anonymize(self, logical_col_name: str, original_value):
        """
        Aplica la regla de anonimización correcta a un valor basado en el nombre
        lógico de su columna.
        """
        rule_func = self.rules.get(logical_col_name, self.rules['default'])
        try:
            # Intenta llamar a la regla pasando el valor original, para las reglas de preservación.
            return rule_func(original_value)
        except TypeError:
            # Si la regla no acepta argumentos (la mayoría), la llama sin ellos.
            return rule_func()


def get_column_maps(config: configparser.ConfigParser) -> tuple[dict, dict]:
    """
    Crea los diccionarios de mapeo desde la configuración para traducir
    nombres de columnas.
    """
    mapping = config['ColumnMapping']
    # Mapea: Nombre Lógico -> Nombre en Excel
    logical_to_excel = dict(mapping)
    # Mapea: Nombre en Excel -> Nombre Lógico
    excel_to_logical = {v: k for k, v in mapping.items()}
    return logical_to_excel, excel_to_logical


def filter_dataframe(df: pd.DataFrame, config: configparser.ConfigParser) -> pd.DataFrame:
    """
    Aplica los criterios de filtro de la configuración al DataFrame.
    Esta función es una versión autónoma de la lógica en `src/data_handler/filter.py`.
    """
    if 'FilterCriteria' not in config:
        logging.warning("No se encontró la sección [FilterCriteria] en el perfil. Se omitirá el filtrado.")
        return df

    logging.info("Aplicando criterios de filtro para crear una muestra de alta calidad...")
    filtered_df = df.copy()
    criteria = config['FilterCriteria']
    mapping = config['ColumnMapping']

    for key, value in criteria.items():
        if key not in mapping:
            logging.warning(f"La clave de filtro '{key}' no tiene un mapeo de columna. Se omitirá.")
            continue

        excel_col = mapping[key]
        if excel_col not in filtered_df.columns:
            logging.warning(f"La columna de filtro '{excel_col}' no existe en el DataFrame. Se omitirá este filtro.")
            continue
        
        initial_rows = len(filtered_df)
        column_series = filtered_df[excel_col].astype(str).str.strip().str.upper()
        criterion_value = str(value).strip().upper()
        
        filtered_df = filtered_df[column_series == criterion_value]
        
        logging.info(f"  - Filtro '{excel_col}' == '{value}': {initial_rows} -> {len(filtered_df)} filas.")
    
    return filtered_df


def main():
    """
    Punto de entrada principal para orquestar el proceso de anonimización.
    """
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", stream=sys.stdout)
    
    parser = argparse.ArgumentParser(
        description="Herramienta para crear una muestra de datos anonimizada desde un Excel de producción.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--profile", required=True, help="Nombre del perfil .ini que describe el archivo de entrada (ej. produccion_cliente_xyz).")
    parser.add_argument("--input-file", required=True, type=Path, help="Ruta al archivo Excel de entrada con datos REALES.")
    parser.add_argument("--output-excel", type=Path, help="[Opcional] Ruta de destino para el archivo Excel anonimizado.")
    parser.add_argument("--output-json", type=Path, help="[Opcional] Ruta de destino para el archivo JSON anonimizado (para el SAF).")
    parser.add_argument("--sample-size", type=int, default=50, help="Número de filas a incluir en la muestra (por defecto: 50).")
    parser.add_argument("--seed", type=int, help="[Opcional] Semilla para Faker para obtener resultados reproducibles.")
    
    args = parser.parse_args()

    if not args.output_excel and not args.output_json:
        parser.error("Debes especificar al menos una ruta de salida (--output-excel o --output-json).")

    # --- FASE 1: CARGA Y VALIDACIÓN INICIAL ---
    try:
        logging.info(f"Cargando perfil '{args.profile}' desde 'config/profiles/{args.profile}.ini'...")
        profile_path = Path(f'config/profiles/{args.profile}.ini')
        if not profile_path.exists():
            raise FileNotFoundError(f"El archivo de perfil '{profile_path}' no fue encontrado.")
        config = configparser.ConfigParser()
        config.read(profile_path)

        logging.info(f"Cargando datos desde '{args.input_file}'...")
        df_full = pd.read_excel(
            args.input_file,
            sheet_name=config.get('DataSource', 'sheet_name'),
            header=config.getint('DataSource', 'header_row') - 1
        )
        logging.info(f"Se cargaron {len(df_full)} filas del archivo de entrada.")
        
        _, excel_to_logical_map = get_column_maps(config)
        
        # MITIGACIÓN DE PUNTO CIEGO #1: POLÍTICA DE "LISTA BLANCA ESTRICTA"
        # Nos aseguramos de que solo las columnas definidas en el perfil sobrevivan.
        allowed_cols = list(excel_to_logical_map.keys())
        df = df_full[allowed_cols].copy() # Usar .copy() para evitar SettingWithCopyWarning
        
        dropped_cols_count = len(df_full.columns) - len(df.columns)
        if dropped_cols_count > 0:
            logging.info(f"Política de Lista Blanca: Se descartaron {dropped_cols_count} columnas no definidas en el perfil.")

        # MITIGACIÓN DE PUNTO CIEGO #2: COERCIÓN DE TIPO TEMPRANA
        # Forzamos los identificadores clave a ser strings para evitar problemas de tipo.
        id_logical_names = ['numero_historia', 'identificacion']
        for logical_name in id_logical_names:
            if logical_name in config['ColumnMapping']:
                excel_col_name = config['ColumnMapping'][logical_name]
                if excel_col_name in df.columns:
                    logging.info(f"Forzando la columna '{excel_col_name}' a tipo string para consistencia.")
                    df[excel_col_name] = df[excel_col_name].astype(str)

    except (FileNotFoundError, ValueError, KeyError, configparser.Error) as e:
        logging.error(f"Error durante la carga y configuración: {e}")
        sys.exit(1)

    # --- FASE 2: FILTRADO INTELIGENTE ---
    df_filtered = filter_dataframe(df, config)

    # MITIGACIÓN DE PUNTO CIEGO #3: Manejar el caso de cero resultados tras el filtro.
    if df_filtered.empty:
        logging.warning("ADVERTENCIA: Ninguna fila cumple los criterios de filtro. No se generará ninguna muestra. Revisa [FilterCriteria].")
        sys.exit(0)
    
    # --- FASE 3: MUESTREO ---
    df_sample = df_filtered.head(args.sample_size).copy() # Usar .copy()
    logging.info(f"Se ha creado una muestra de {len(df_sample)} filas para anonimizar.")

    # --- FASE 4: ANONIMIZACIÓN ---
    logging.info("Iniciando el proceso de anonimización...")
    engine = AnonymizerEngine(seed=args.seed)
    df_anonymized = df_sample.copy()

    for excel_col, logical_col in excel_to_logical_map.items():
        if excel_col in df_anonymized.columns:
            logging.debug(f"Anonimizando columna '{excel_col}' (lógica: '{logical_col}')...")
            # Usar .apply en la columna para la transformación
            df_anonymized[excel_col] = df_sample[excel_col].apply(
                lambda original_value: engine.anonymize(logical_col, original_value)
            )

    # --- FASE 5: GENERACIÓN DE SALIDAS ---
    try:
        if args.output_excel:
            logging.info(f"Guardando archivo Excel anonimizado en: {args.output_excel}")
            args.output_excel.parent.mkdir(parents=True, exist_ok=True)
            df_anonymized.to_excel(args.output_excel, index=False)
        
        if args.output_json:
            logging.info(f"Guardando archivo JSON anonimizado en: {args.output_json}")
            args.output_json.parent.mkdir(parents=True, exist_ok=True)
            df_anonymized.to_json(args.output_json, orient='records', indent=2, force_ascii=False)
            
        logging.info("¡Proceso de anonimización completado exitosamente!")

    except IOError as e:
        logging.error(f"Error al escribir los archivos de salida: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()