# saf/state/application_state.py
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

class ApplicationState:
    """
    El Modelo en nuestra arquitectura MVC.
    
    Responsabilidades:
    - Cargar y mantener los escenarios de prueba desde el archivo JSON.
    - Contener la lógica de negocio del simulador (ej. buscar un paciente).
    - Mantener el estado actual de la simulación (qué paciente está cargado).
    - No tiene conocimiento alguno sobre Tkinter o la GUI.
    """
    def __init__(self, scenarios_path: Path):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._scenarios: Dict[str, Dict[str, Any]] = self._load_scenarios(scenarios_path)
        self.current_patient: Optional[Dict[str, Any]] = None

    def _load_scenarios(self, path: Path) -> Dict[str, Dict[str, Any]]:
        """Carga los datos del JSON y los indexa por número de historia para búsquedas rápidas."""
        self.logger.info(f"Cargando escenarios de prueba desde: {path}")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                scenarios_list = json.load(f)
            
            # PUNTO CLAVE: Indexamos los datos en un diccionario para un acceso O(1).
            # La clave es el 'numero_historia' ('HISTORIA:'), que es el identificador
            # que nuestro bot usará para las búsquedas.
            indexed_scenarios = {
                scenario["HISTORIA:"]: scenario for scenario in scenarios_list
            }
            self.logger.info(f"Se cargaron y se indexaron {len(indexed_scenarios)} escenarios.")
            return indexed_scenarios
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            self.logger.critical(f"Error fatal al cargar o parsear los escenarios de prueba: {e}")
            # --- CAMBIO CLAVE DE ROBUSTEZ ---
            # Implementamos el principio de "fallar rápido". Si los datos esenciales
            # no están disponibles, es mejor detener la aplicación que dejarla en un
            # estado "zombi" no funcional.
            raise RuntimeError(f"No se pudieron cargar los escenarios del SAF desde '{path}'. Error: {e}")

    def find_patient_by_history_id(self, history_id: str) -> bool:
        """
        Busca un paciente por su número de historia y actualiza el estado interno.
        
        Args:
            history_id: El número de historia a buscar.

        Returns:
            True si el paciente fue encontrado y el estado actualizado, False en caso contrario.
        """
        self.logger.info(f"Buscando paciente con ID de historia: '{history_id}'")
        patient_data = self._scenarios.get(history_id)
        
        if patient_data:
            self.current_patient = patient_data
            self.logger.info(f"Paciente encontrado: {self.current_patient.get('NOMBRE1:')}")
            return True
        else:
            self.current_patient = None
            self.logger.warning(f"Paciente con ID de historia '{history_id}' no encontrado en los escenarios.")
            return False