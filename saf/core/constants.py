# saf/core/constants.py

class JsonFields:
    """
    Define las claves literales usadas en el archivo test_scenarios.json.
    Sirve como única fuente de verdad para el parseo de datos crudos,
    evitando "strings mágicos" y facilitando el mantenimiento.
    """
    # --- Campos de Paciente (Persistentes) ---
    HISTORIA = "HISTORIA:"
    IDENTIFICACION = "IDENTIFIC:"
    NOMBRE1 = "NOMBRE1:"
    NOMBRE2 = "NOMBRE2:"
    APELLIDO1 = "APELLIDO1:"
    APELLIDO2 = "APELLIDO2:"

    # --- Campos de Factura (Reseteables) ---
    EMPRESA = "EMPRESA:"
    CONTRATO_EMP = "CONTRATO EMP:"
    ESTRATO = "ESTRATO:"
    MEDICO = "MEDICO:"
    DIAG_INGRESO = "DIAG INGRESO"