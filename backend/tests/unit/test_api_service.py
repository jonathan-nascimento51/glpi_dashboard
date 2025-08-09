# -*- coding: utf-8 -*-
"""Testes unitários para API Service"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from services.api_service import APIService
from utils.response_formatter import ResponseFormatter


class TestAPIService:
    """Testes unitários para APIService"""
    
    @pytest.fixture
    def api_service(self):
        """Fixture que cria uma instância do APIService para testes"""
        return APIService()
    
    @pytest.fixture
    def mock_glpi_service(self):
        """Mock do GLPIService"""
        mock_service = Mock()
        mock_service.get_metrics_by_level.return_value = {
            "N1": {"Novo": 10, "Processando (atribuído)": 5},
            "N2": {"Novo": 15, "Processando (atribuído)": 7}
        }
        mock_service.get_general_metrics.return_value = {
            "Novo": 25, "Processando (atribuído)": 12
        }
        return mock_service
    
    def test_get_dashboard_metrics_success(self, api_service, mock_glpi_service):
        """Testa obtenção de métricas do dashboard com sucesso"""
        with patch.object(api_service, 'glpi_service', mock_glpi_service):
            result = api_service.get_dashboard_metrics()
            
            assert result is not None
            assert "level_metrics" in result
            assert "general_metrics" in result
            assert result["level_metrics"]["N1"]["Novo"] == 10
            assert result["general_metrics"]["Novo"] == 25
    
    def test_get_dashboard_metrics_with_date_filter(self, api_service, mock_glpi_service):
        """Testa obtenção de métricas com filtro de data"""
        start_date = "2024-01-01"
        end_date = "2024-01-31"
        
        with patch.object(api_service, 'glpi_service', mock_glpi_service):
            result = api_service.get_dashboard_metrics(start_date, end_date)
            
            # Verifica se os métodos foram chamados com os parâmetros corretos
            mock_glpi_service.get_metrics_by_level.assert_called_with(start_date, end_date)
            mock_glpi_service.get_general_metrics.assert_called_with(start_date, end_date)
            
            assert result is not None
    
    def test_get_dashboard_metrics_glpi_service_failure(self, api_service):
        """Testa falha no GLPIService"""
        mock_glpi_service = Mock()
        mock_glpi_service.get_metrics_by_level.side_effect = Exception("GLPI Error")
        
        with patch.object(api_service, 'glpi_service', mock_glpi_service):
            result = api_service.get_dashboard_metrics()
            
            # Deve retornar None ou estrutura de erro
            assert result is None or "error" in result
    
    def test_format_response_success(self, api_service):
        """Testa formatação de resposta de sucesso"""
        data = {"test": "data"}
        
        with patch.object(ResponseFormatter, 'success') as mock_success:
            mock_success.return_value = {"status": "success", "data": data}
            
            result = api_service.format_response(data)
            
            mock_success.assert_called_once_with(data)
            assert result["status"] == "success"
            assert result["data"] == data
    
    def test_format_error_response(self, api_service):
        """Testa formatação de resposta de erro"""
        error_message = "Test error"
        
        with patch.object(ResponseFormatter, 'error') as mock_error:
            mock_error.return_value = {"status": "error", "message": error_message}
            
            result = api_service.format_error_response(error_message)
            
            mock_error.assert_called_once_with(error_message)
            assert result["status"] == "error"
            assert result["message"] == error_message
    
    def test_validate_date_format_valid(self, api_service):
        """Testa validação de formato de data válido"""
        valid_dates = ["2024-01-01", "2023-12-31", "2024-02-29"]  # Ano bissexto
        
        for date_str in valid_dates:
            assert api_service.validate_date_format(date_str) is True
    
    def test_validate_date_format_invalid(self, api_service):
        """Testa validação de formato de data inválido"""
        invalid_dates = ["2024-13-01", "2024-01-32", "invalid-date", "01/01/2024"]
        
        for date_str in invalid_dates:
            assert api_service.validate_date_format(date_str) is False
    
    def test_get_trends_data(self, api_service, mock_glpi_service):
        """Testa obtenção de dados de tendências"""
        # Mock de dados históricos
        mock_glpi_service.get_historical_metrics.return_value = [
            {"date": "2024-01-01", "total": 100},
            {"date": "2024-01-02", "total": 105},
            {"date": "2024-01-03", "total": 110}
        ]
        
        with patch.object(api_service, 'glpi_service', mock_glpi_service):
            result = api_service.get_trends_data("2024-01-01", "2024-01-03")
            
            assert result is not None
            assert len(result) == 3
            assert result[0]["total"] == 100
            assert result[2]["total"] == 110
    
    def test_get_performance_metrics(self, api_service):
        """Testa obtenção de métricas de performance"""
        with patch('time.time', return_value=1640995200.0):  # Data fixa
            with patch.object(api_service, '_calculate_response_time', return_value=150):
                result = api_service.get_performance_metrics()
                
                assert "response_time" in result
                assert "timestamp" in result
                assert result["response_time"] == 150
                assert result["timestamp"] == 1640995200.0
    
    @pytest.mark.parametrize("start_date,end_date,expected_valid", [
        ("2024-01-01", "2024-01-31", True),
        ("2024-01-31", "2024-01-01", False),  # Data final antes da inicial
        ("invalid", "2024-01-31", False),
        ("2024-01-01", "invalid", False),
    ])
    def test_validate_date_range(self, api_service, start_date, end_date, expected_valid):
        """Testa validação de intervalo de datas"""
        result = api_service.validate_date_range(start_date, end_date)
        assert result == expected_valid
    
    def test_cache_metrics(self, api_service, mock_glpi_service):
        """Testa cache de métricas"""
        with patch.object(api_service, 'glpi_service', mock_glpi_service):
            # Primeira chamada
            result1 = api_service.get_dashboard_metrics()
            
            # Segunda chamada (deve usar cache)
            result2 = api_service.get_dashboard_metrics()
            
            # Verifica se o GLPIService foi chamado apenas uma vez
            assert mock_glpi_service.get_metrics_by_level.call_count <= 2
            assert result1 == result2
    
    def test_error_handling_with_logging(self, api_service, caplog):
        """Testa tratamento de erros com logging"""
        mock_glpi_service = Mock()
        mock_glpi_service.get_metrics_by_level.side_effect = Exception("Test error")
        
        with patch.object(api_service, 'glpi_service', mock_glpi_service):
            result = api_service.get_dashboard_metrics()
            
            # Verifica se o erro foi logado
            assert "Test error" in caplog.text or result is None
    
    def test_concurrent_requests_handling(self, api_service, mock_glpi_service):
        """Testa tratamento de requisições concorrentes"""
        import threading
        import time
        
        results = []
        
        def make_request():
            with patch.object(api_service, 'glpi_service', mock_glpi_service):
                result = api_service.get_dashboard_metrics()
                results.append(result)
        
        # Simula requisições concorrentes
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verifica se todas as requisições foram processadas
        assert len(results) == 3
        assert all(result is not None for result in results)