import pytest
from src.utils.dataframe_helpers import sanitize_column_name

# Usamos parametrize para probar múltiples casos de forma limpia y eficiente.
# Cada tupla contiene (entrada, salida_esperada).
@pytest.mark.parametrize("input_name, expected_output", [
    # Caso simple: solo eliminar dos puntos
    ('HISTORIA:', 'HISTORIA'),
    # Caso con espacios y dos puntos
    ('CONTRATO EMP:', 'CONTRATO_EMP'),
    # Caso con barra inclinada
    ('FEC/INGRESO:', 'FEC_INGRESO'),
    # Caso ya limpio
    ('medico_tratante', 'medico_tratante'),
    # Caso con múltiples espacios y símbolos
    ('  Columna   Con  Mucho // Ruido!! ', 'Columna_Con_Mucho_Ruido'),
    # Caso con número
    ('DX ADICIONAL1:', 'DX_ADICIONAL1'),
    # Caso que empieza con guion bajo después de sanear
    ('_columna', '_columna'),
    # Caso que podría terminar con guion bajo
    ('columna_', 'columna'),
])
def test_sanitize_column_name(input_name, expected_output):
    """
    Verifica que la función sanitize_column_name funciona correctamente
    para una variedad de casos de entrada.
    """
    assert sanitize_column_name(input_name) == expected_output

def test_sanitize_column_name_non_string_input():
    """
    Verifica que la función maneja entradas no-string (como números) sin fallar.
    """
    assert sanitize_column_name(12345) == '12345'