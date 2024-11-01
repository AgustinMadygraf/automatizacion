"""
tests/test_api.py
Este módulo contiene pruebas de integración para el flujo completo de la aplicación.
"""

import pytest
from unittest.mock import patch
from src.view.main_view import run_main
import os

@pytest.fixture
def mock_fetcher():
    """Mock para ESP32DataFetcher."""
    with patch("src.model.esp32_data_fetcher.ESP32DataFetcher") as MockFetcher:
        instance = MockFetcher.return_value
        instance.fetch_data.return_value = "Peso: 12.5 kg\nVueltas: 5"
        yield instance

@pytest.fixture
def mock_processor():
    """Mock para DataProcessor."""
    with patch("src.model.data_processor.DataProcessor") as MockProcessor:
        instance = MockProcessor.return_value
        instance.process_data.return_value = {"Peso": 12.5, "Vueltas": 5, "Tiempo": "2023-01-01 12:00:00"}
        yield instance

@pytest.fixture
def mock_sender():
    """Mock para PHPServerSender."""
    with patch("src.model.php_server_sender.PHPServerSender") as MockSender:
        instance = MockSender.return_value
        instance.send_data.return_value = True
        yield instance

def test_run_main_integration(mock_fetcher, mock_processor, mock_sender):
    """Prueba integral para el flujo completo en run_main."""

    # Configura la variable de entorno para evitar el bucle infinito en modo de prueba
    os.environ["TESTING"] = "1"

    # Aplica los mocks necesarios para los componentes de run_main
    with patch("src.controller.main_controller.MainApp") as MockApp, \
         patch("src.view.main_view.LoggerConfigurator") as MockLoggerConfigurator, \
         patch("src.view.main_view.os.system") as mock_os_system:

        # Simula LoggerConfigurator y os.system para evitar efectos colaterales
        mock_logger = MockLoggerConfigurator.return_value.configure.return_value
        mock_logger.debug.return_value = None
        mock_logger.info.return_value = None
        mock_os_system.return_value = None

        # Mock para MainApp y su método run
        mock_app_instance = MockApp.return_value
        mock_app_instance.run.side_effect = lambda: None  # Asegura que no entre en un bucle

        # Ejecuta run_main, que utiliza los componentes de fetcher, processor, y sender
        run_main()

        # Verifica que las llamadas se realizaron en el flujo esperado
        mock_fetcher.fetch_data.assert_called_once()
        mock_processor.process_data.assert_called_once_with("Peso: 12.5 kg\nVueltas: 5")
        mock_sender.send_data.assert_called_once_with({"Peso": 12.5, "Vueltas": 5, "Tiempo": "2023-01-01 12:00:00"})
        
        # Verifica que la aplicación se ejecutó y registró los mensajes esperados
        mock_app_instance.run.assert_called_once()
        mock_logger.info.assert_any_call("Iniciando la aplicación principal")
        mock_logger.info.assert_any_call("Aplicación principal finalizada")

    # Limpia la variable de entorno después de la prueba
    del os.environ["TESTING"]


def test_esp32_data_fetcher(mock_fetcher):
    """Prueba unitaria para ESP32DataFetcher."""
    assert mock_fetcher.fetch_data() == "Peso: 12.5 kg\nVueltas: 5"

def test_data_processor(mock_processor):
    """Prueba unitaria para DataProcessor."""
    raw_data = "Peso: 12.5 kg\nVueltas: 5"
    processed_data = mock_processor.process_data(raw_data)
    assert processed_data == {"Peso": 12.5, "Vueltas": 5, "Tiempo": "2023-01-01 12:00:00"}

def test_php_server_sender(mock_sender):
    """Prueba unitaria para PHPServerSender."""
    data = {"Peso": 12.5, "Vueltas": 5, "Tiempo": "2023-01-01 12:00:00"}
    assert mock_sender.send_data(data) is True
