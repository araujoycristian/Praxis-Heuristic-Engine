# saf/state/application_state.py
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from .models import PatientData, InvoiceData

class ApplicationState:
    """
    El Modelo en la arquitectura MVC. Gestiona el estado de la simulación
    (paciente en contexto, factura activa) y contiene la lógica de negocio
    del simulador. Es completamente agnóstico a la UI.
    """
    def __init__(self, scenarios_path: Path):
        self.logger = logging.getLogger(self.__class__.__name__)
        # El diccionario almacena el modelo de paciente y los datos crudos para la factura.
        self._scenarios: Dict[str, Tuple[PatientData, Dict[str, Any]]] = self._load_scenarios(scenarios_path)
        
        self.context_patient: Optional[PatientData] = None
        self.active_invoice: Optional[InvoiceData] = None

    def _load_scenarios(self, path: Path) -> Dict[str, Tuple[PatientData, Dict[str, Any]]]:
        """
        Carga los datos del JSON y los indexa de forma resiliente, omitiendo
        registros inválidos que podrían detener la aplicación.
        """
        self.logger.info(f"Cargando escenarios de prueba desde: {path}")
        indexed_scenarios = {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                scenarios_list = json.load(f)
            
            for i, raw_scenario in enumerate(scenarios_list, 1):
                try:
                    # Validar y crear el modelo de paciente en el origen.
                    patient_model = PatientData.create_from_dict(raw_scenario)
                    indexed_scenarios[patient_model.numero_historia] = (patient_model, raw_scenario)
                except ValueError as e:
                    self.logger.warning(f"Omitiendo escenario inválido #{i} del JSON: {e}")
            
            self.logger.info(f"Se cargaron y se indexaron {len(indexed_scenarios)} escenarios válidos de {len(scenarios_list)} totales.")
            return indexed_scenarios
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.critical(f"Error fatal al cargar o parsear los escenarios: {e}")
            raise RuntimeError(f"No se pudieron cargar los escenarios del SAF. Error: {e}")

    def find_patient_by_history_id(self, history_id: str) -> bool:
        """
        Busca un paciente por su número de historia y actualiza el estado interno
        cargando tanto el modelo del paciente como el de la factura.
        """
        self.logger.info(f"Buscando paciente con ID de historia: '{history_id}'")
        scenario_data = self._scenarios.get(history_id)
        
        if scenario_data:
            patient_model, raw_data = scenario_data
            self.context_patient = patient_model
            self.active_invoice = InvoiceData.create_from_dict(raw_data)
            self.logger.info(f"Paciente encontrado y estado actualizado: {self.context_patient.nombre1}")
            return True
        else:
            self.context_patient = None
            self.active_invoice = None
            self.logger.warning(f"Paciente con ID de historia '{history_id}' no encontrado en los escenarios.")
            self.logger.info("Estado interno (paciente y factura) reseteado a nulo.")
            return False

    def reset_active_invoice(self):
        """
        Simula la acción de Ctrl+N. Resetea la factura activa a un estado
        inicial, pero mantiene intacto al paciente en contexto.
        """
        if self.context_patient:
            self.logger.info(f"Reseteando factura para el paciente en contexto ({self.context_patient.numero_historia}).")
            self.active_invoice = InvoiceData.get_initial_state()
        else:
            self.logger.warning("Intento de resetear factura sin paciente en contexto. Se ignora la acción.")

    def get_current_display_data(self) -> Optional[Dict[str, Any]]:
        """
        Actúa como una Fachada para la UI, fusionando los datos del paciente y
        la factura activa en un único diccionario plano para que la vista
        no necesite conocer los modelos internos.
        """
        if not self.context_patient:
            return None

        # Empezamos con los datos del paciente.
        display_data = self.context_patient.__dict__.copy()

        # Sobrescribimos o añadimos los datos de la factura activa.
        if self.active_invoice:
            display_data.update(self.active_invoice.__dict__)
        
        return display_data