# tests/automation/strategies/remote/test_automator.py

import pytest
from unittest.mock import MagicMock, ANY
from pathlib import Path
from datetime import date

# Importaciones de nuestro código fuente
from src.automation.strategies.remote.automator import RemoteAutomator
from src.automation.common.results import TaskResult, TaskResultStatus
from src.automation.common.states import TaskState
from src.core.models import FacturacionData

# Este fixture simula un objeto ConfigParser para no depender de archivos .ini reales.
@pytest.fixture
def mock_config(mocker):
    """Crea un mock de ConfigParser con los valores necesarios para inicializar el automator."""
    config = mocker.MagicMock()
    # Simulamos la llamada a config.get(...) y config.getint(...)
    config.get.return_value = "Mocked Window Title"
    config.getint.return_value = 2  # max_retries
    return config

# Este fixture crea el "doble de prueba" para la fachada de control remoto.
@pytest.fixture
def mock_facade(mocker):
    """Crea un mock para RemoteControlFacade."""
    return mocker.MagicMock()

# Este fixture crea el "doble de prueba" para el manejador de la ventana principal.
@pytest.fixture
def mock_handler(mocker):
    """Crea un mock para MainWindowHandler."""
    return mocker.MagicMock()

# Este es el fixture más importante. Prepara nuestro "System Under Test" (SUT),
# el RemoteAutomator, inyectándole todos los mocks para aislarlo.
@pytest.fixture
def automator_sut(mocker, mock_config, mock_facade, mock_handler):
    """
    Crea una instancia de RemoteAutomator (SUT) y le inyecta sus dependencias mockeadas.
    SUT = System Under Test.
    """
    # 1. "Interceptamos" la creación de RemoteControlFacade y MainWindowHandler
    #    para que cuando RemoteAutomator los cree, use nuestros mocks en su lugar.
    mocker.patch(
        'src.automation.strategies.remote.automator.RemoteControlFacade',
        return_value=mock_facade
    )
    mocker.patch(
        'src.automation.strategies.remote.automator.MainWindowHandler',
        return_value=mock_handler
    )

    # 2. Creamos la instancia real de RemoteAutomator.
    sut = RemoteAutomator()

    # 3. Lo inicializamos. Esto hará que internamente se usen los mocks que
    #    hemos interceptado arriba.
    sut.initialize(mock_config)
    return sut

# Creamos un dato de prueba que usaremos en ambos tests.
@pytest.fixture
def sample_task():
    """Crea un objeto FacturacionData de ejemplo para las pruebas."""
    return FacturacionData(
        numero_historia="ID-12345",
        identificacion="CC-98765",
        diagnostico_principal="A001",
        fecha_ingreso=date(2025, 7, 14),
        medico_tratante="Dr. Mock",
        empresa_aseguradora="Test Aseguradora",
        contrato_empresa="Contrato 1",
        estrato="2",
        diagnostico_adicional_1=None,
        diagnostico_adicional_2=None,
        diagnostico_adicional_3=None,
    )

# --- INICIO DE LAS PRUEBAS ---

def test_screenshot_is_taken_on_unexpected_error(automator_sut, mock_facade, mock_handler, sample_task):
    """
    ESCENARIO 1: El Caso Ideal del Fallo.
    Verifica que se llama a `take_screenshot` cuando ocurre una excepción genérica
    durante el procesamiento de una tarea.
    """
    # GIVEN (Dado que...)
    # Configuramos el mock del handler para que, cuando se llame a su método
    # `initiate_new_billing`, lance un error inesperado (ValueError).
    error_message = "Fallo deliberado para la prueba"
    mock_handler.initiate_new_billing.side_effect = ValueError(error_message)

    # WHEN (Cuando...)
    # Ejecutamos el método que queremos probar con la tarea de ejemplo.
    results = automator_sut.process_billing_tasks([sample_task])

    # THEN (Entonces...)
    # Verificamos que se cumplieron nuestras expectativas.
    # 1. El método `take_screenshot` del mock de la fachada fue llamado exactamente una vez.
    mock_facade.take_screenshot.assert_called_once()
    
    # 2. Verificamos que el nombre del archivo de la captura es correcto.
    #    `call_args` nos da acceso a los argumentos con los que fue llamado el método.
    #    Usamos ANY (de unittest.mock) para no depender de la fecha/hora exacta.
    call_args, _ = mock_facade.take_screenshot.call_args
    screenshot_path = call_args[0]
    
    assert isinstance(screenshot_path, Path)
    assert "FAILURE" in screenshot_path.name
    assert "ID-12345" in screenshot_path.name # El ID de nuestra tarea de prueba
    assert TaskState.INITIATING_NEW_BILLING.name in screenshot_path.name
    assert screenshot_path.name.endswith(".png")

    # 3. Verificamos que el resultado de la tarea refleja el fallo.
    assert len(results) == 1
    task_result = results[0]
    assert task_result.status == TaskResultStatus.FAILED_UNEXPECTED_ERROR
    assert task_result.task_identifier == sample_task.numero_historia
    assert error_message in task_result.message


def test_screenshot_failure_is_handled_gracefully(automator_sut, mock_facade, mock_handler, sample_task, caplog):
    """
    ESCENARIO 2: Fallo en la Propia Captura.
    Verifica que si `take_screenshot` falla, el sistema lo registra como una advertencia
    pero no crashea, y el reporte final refleja el error original.
    """
    # GIVEN (Dado que...)
    # 1. El handler lanza el error original.
    original_error_msg = "Error original del handler"
    mock_handler.initiate_new_billing.side_effect = ValueError(original_error_msg)

    # 2. El método `take_screenshot` de la fachada TAMBIÉN lanza un error.
    screenshot_error_msg = "Permiso de escritura denegado"
    mock_facade.take_screenshot.side_effect = IOError(screenshot_error_msg)

    # WHEN (Cuando...)
    # Ejecutamos el método.
    results = automator_sut.process_billing_tasks([sample_task])

    # THEN (Entonces...)
    # 1. Verificamos que se INTENTÓ tomar la captura (aunque falló).
    mock_facade.take_screenshot.assert_called_once()
    
    # 2. Verificamos que el log de advertencia fue emitido.
    #    `caplog` es un fixture de pytest que captura los logs.
    assert "ATENCIÓN: Falló el intento de tomar la captura de pantalla de diagnóstico" in caplog.text
    assert screenshot_error_msg in caplog.text # El log debe incluir el error de la captura

    # 3. **CRUCIAL**: Verificamos que el resultado de la tarea reporta el error ORIGINAL, no el de la captura.
    assert len(results) == 1
    task_result = results[0]
    assert task_result.status == TaskResultStatus.FAILED_UNEXPECTED_ERROR
    assert original_error_msg in task_result.message
    assert screenshot_error_msg not in task_result.message # No debe estar contaminado.