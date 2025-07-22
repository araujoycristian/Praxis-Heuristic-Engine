# saf/state/models.py
from dataclasses import dataclass
from typing import Optional, Dict, Any

from saf.core.constants import JsonFields

@dataclass
class PatientData:
    """
    Representa los datos inmutables de un paciente.
    Estos datos NO se resetean al iniciar una nueva factura (Ctrl+N).
    """
    numero_historia: str
    identificacion: str
    nombre1: Optional[str]
    nombre2: Optional[str]
    apellido1: Optional[str]
    apellido2: Optional[str]

    @classmethod
    def create_from_dict(cls, data: Dict[str, Any]) -> "PatientData":
        """
        Método fábrica que valida la presencia de campos clave.
        Lanza ValueError si los identificadores esenciales faltan.
        """
        historia = data.get(JsonFields.HISTORIA)
        identificacion = data.get(JsonFields.IDENTIFICACION)

        if not historia or not identificacion:
            raise ValueError(f"El registro de escenario es inválido. Faltan 'HISTORIA:' o 'IDENTIFIC:'. Registro: {data}")

        return cls(
            numero_historia=historia,
            identificacion=identificacion,
            nombre1=data.get(JsonFields.NOMBRE1),
            nombre2=data.get(JsonFields.NOMBRE2),
            apellido1=data.get(JsonFields.APELLIDO1),
            apellido2=data.get(JsonFields.APELLIDO2),
        )

@dataclass
class InvoiceData:
    """
    Representa los datos de una factura específica, que son volátiles.
    Estos datos SÍ se resetean al presionar Ctrl+N.
    """
    empresa: Optional[str]
    contrato: Optional[str]
    estrato: Optional[str]
    medico: Optional[str]
    diagnostico_principal: Optional[str]

    @classmethod
    def create_from_dict(cls, data: Dict[str, Any]) -> "InvoiceData":
        """Método fábrica para poblar la factura usando constantes centralizadas."""
        return cls(
            empresa=data.get(JsonFields.EMPRESA),
            contrato=data.get(JsonFields.CONTRATO_EMP),
            estrato=data.get(JsonFields.ESTRATO),
            medico=data.get(JsonFields.MEDICO),
            diagnostico_principal=data.get(JsonFields.DIAG_INGRESO),
        )

    @classmethod
    def get_initial_state(cls) -> "InvoiceData":
        """Devuelve una instancia limpia con valores por defecto, simulando una nueva factura."""
        return cls(
            empresa="",
            contrato="",
            estrato="",
            medico="",
            diagnostico_principal=""
        )