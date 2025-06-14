from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass(frozen=True)
class FacturacionData:
    """
    Representa el "contrato de datos" limpio y validado para una única tarea de facturación.
    Es un objeto inmutable que fluye desde el orquestador hacia la capa de automatización,
    desacoplando la lógica de la fuente de datos original (Excel).
    """
    
    # --- Datos clave y obligatorios ---
    numero_historia: str
    identificacion: str
    diagnostico_principal: str
    fecha_ingreso: date
    medico_tratante: str
    empresa_aseguradora: str
    contrato_empresa: str
    estrato: str

    # --- Diagnósticos opcionales ---
    diagnostico_adicional_1: Optional[str]
    diagnostico_adicional_2: Optional[str]
    diagnostico_adicional_3: Optional[str]