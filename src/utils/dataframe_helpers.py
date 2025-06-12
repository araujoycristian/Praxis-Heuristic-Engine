import re

def sanitize_column_name(col_name: str) -> str:
    """
    Sanea un nombre de columna para que sea un identificador válido en Python.

    Esta función es crucial para que `itertuples` funcione correctamente.
    La lógica es:
    1. Elimina espacios en blanco al principio y al final.
    2. Reemplaza cualquier caracter que no sea letra, número o guion bajo por '_'.
    3. Colapsa múltiples guiones bajos en uno solo.
    4. Elimina guiones bajos SOLO del final del nombre, no del principio.

    Ejemplos:
        '  FEC/INGRESO:  ' -> 'FEC_INGRESO'
        '  CONTRATO EMP: ' -> 'CONTRATO_EMP'
        '_internal:' -> '_internal'
    """
    if not isinstance(col_name, str):
        col_name = str(col_name)
    
    # PASO 1: Limpiar espacios en blanco de los extremos
    sanitized = col_name.strip()
    
    # PASO 2: Reemplazar caracteres no válidos
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', sanitized)

    # PASO 3: Colapsar guiones bajos múltiples
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # PASO 4: Eliminar guiones bajos del final
    return sanitized.rstrip('_')