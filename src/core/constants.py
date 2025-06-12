# src/core/constants.py

class ConfigSections:
    """Nombres de las secciones en los archivos de perfil .ini."""
    DATA_SOURCE = 'DataSource'
    COLUMN_MAPPING = 'ColumnMapping'
    FILTER_CRITERIA = 'FilterCriteria'

class ConfigKeys:
    """Nombres de las claves dentro de las secciones del .ini."""
    SHEET_NAME = 'sheet_name'
    HEADER_ROW = 'header_row'

class LogicalFields:
    """
    Nombres lógicos internos que usamos en el código para referirnos a los datos.
    Estos son los nombres que se mapean a las columnas del Excel en [ColumnMapping].
    """
    # --- Campos Obligatorios ---
    NUMERO_HISTORIA = 'numero_historia'
    DIAGNOSTICO_PRINCIPAL = 'diagnostico_principal'
    FECHA_INGRESO = 'fecha_ingreso'
    MEDICO_TRATANTE = 'medico_tratante'
    EMPRESA_ASEGURADORA = 'empresa_aseguradora'
    CONTRATO_EMPRESA = 'contrato_empresa'
    ESTRATO = 'estrato'

    # --- Campos Opcionales ---
    DIAGNOSTICO_ADICIONAL_1 = 'diagnostico_adicional_1'
    DIAGNOSTICO_ADICIONAL_2 = 'diagnostico_adicional_2'
    DIAGNOSTICO_ADICIONAL_3 = 'diagnostico_adicional_3'

    # --- Campos usados solo para filtrado ---
    USER_FOR_FILTER = 'user_for_filter'
    PYP_FOR_FILTER = 'pyp_for_filter'
    CUPS_FOR_FILTER = 'cups_for_filter'
    SPECIALTY_FOR_FILTER = 'specialty_for_filter'