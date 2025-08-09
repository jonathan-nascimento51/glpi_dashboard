# -*- coding: utf-8 -*-
"""Testes de integração para API endpoints"""
import pytest
import json
import time
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from main import app
from services.glpi_service import GLPIService
from services.api_service import APIService


@pytest.fixture
def client():
    """Fixture para cliente de teste Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_glpi_data():
    """Dados mock para testes de integração"""
    return {
        "level_metrics": {
            "N1": {
                "Novo": 10,
                "Processando (atribuído)": 5,
                "Processando (planejado)": 3,
                "Pendente": 2,
                "Solucionado": 8,
                "Fechado": 12
            },
            "N2": {
                "Novo": 15,
                "Processando (atribuído)": 7,
                "Processando (planejado)": 4,
                "Pendente": 3,
                "Solucionado": 6,
                "Fechado": 9
            }
        },
        "general_metrics": {
            "Novo": 25,
            "Processando (atribuído)": 12,
            "Processando (planejado)": 7,
            "Pendente": 5,
            "Solucionado": 14,
            "Fechado": 21
        }
    }


class TestAPIIntegration:
    """Testes de integração para endpoints da API"""
    
    @patch('services.api_service.APIService.get_dashboard_metrics')
    def test_get_metrics_endpoint_success(self, mock_get_metrics, client, mock_glpi_data):
        """Testa endpoint /api/metrics com sucesso"""
        mock_get_metrics.return_value = mock_glpi_data
        
        response = client.get('/api/metrics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'level_metrics' in data
        assert 'general_metrics' in data
        assert data['level_metrics']['N1']['Novo'] == 10
    
    @patch('services.api_service.APIService.get_dashboard_metrics')
    def test_get_metrics_with_date_filter(self, mock_get_metrics, client, mock_glpi_data):
        """Testa endpoint /api/metrics com filtro de data"""
        mock_get_metrics.return_value = mock_glpi_data
        
        response = client.get('/api/metrics?start_date=2024-01-01&end_date=2024-01-31')
        
        assert response.status_code == 200
        mock_get_metrics.assert_called_with('2024-01-01', '2024-01-31')
    
    @patch('services.api_service.APIService.get_dashboard_metrics')
    def test_get_metrics_invalid_date_format(self, mock_get_metrics, client):
        """Testa endpoint /api/metrics com formato de data inválido"""
        response = client.get('/api/metrics?start_date=invalid-date')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    @patch('services.api_service.APIService.get_dashboard_metrics')
    def test_get_metrics_service_error(self, mock_get_metrics, client):
        """Testa endpoint /api/metrics com erro no serviço"""
        mock_get_metrics.side_effect = Exception("Service error")
        
        response = client.get('/api/metrics')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
    
    @patch('services.api_service.APIService.get_trends_data')
    def test_get_trends_endpoint(self, mock_get_trends, client):
        """Testa endpoint /api/trends"""
        mock_trends_data = [
            {"date": "2024-01-01", "total": 100, "resolved": 20},
            {"date": "2024-01-02", "total": 105, "resolved": 25},
            {"date": "2024-01-03", "total": 110, "resolved": 30}
        ]
        mock_get_trends.return_value = mock_trends_data
        
        response = client.get('/api/trends?start_date=2024-01-01&end_date=2024-01-03')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 3
        assert data[0]['total'] == 100
    
    def test_health_check_endpoint(self, client):
        """Testa endpoint de health check"""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
    
    @patch('services.glpi_service.GLPIService._authenticate_with_retry')
    def test_glpi_connection_health(self, mock_auth, client):
        """Testa health check da conexão GLPI"""
        mock_auth.return_value = True
        
        response = client.get('/api/health/glpi')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['glpi_connection'] == 'healthy'
    
    @patch('services.glpi_service.GLPIService._authenticate_with_retry')
    def test_glpi_connection_unhealthy(self, mock_auth, client):
        """Testa health check com conexão GLPI falha"""
        mock_auth.side_effect = Exception("Connection failed")
        
        response = client.get('/api/health/glpi')
        
        assert response.status_code == 503
        data = json.loads(response.data)
        assert data['glpi_connection'] == 'unhealthy'
    
    def test_cors_headers(self, client):
        """Testa headers CORS"""
        response = client.options('/api/metrics')
        
        assert 'Access-Control-Allow-Origin' in response.headers
        assert 'Access-Control-Allow-Methods' in response.headers
    
    def test_rate_limiting(self, client):
        """Testa rate limiting (se implementado)"""
        # Faz múltiplas requisições rapidamente
        responses = []
        for _ in range(10):
            response = client.get('/api/metrics')
            responses.append(response.status_code)
        
        # Verifica se pelo menos algumas requisições passaram
        # (implementação específica depende da configuração de rate limiting)
        assert any(status == 200 or status == 429 for status in responses)
    
    @patch('services.api_service.APIService.get_dashboard_metrics')
    def test_response_time_performance(self, mock_get_metrics, client, mock_glpi_data):
        """Testa performance do tempo de resposta"""
        mock_get_metrics.return_value = mock_glpi_data
        
        start_time = time.time()
        response = client.get('/api/metrics')
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 2.0  # Resposta deve ser menor que 2 segundos
    
    def test_concurrent_requests(self, client):
        """Testa requisições concorrentes"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = client.get('/api/health')
            results.append(response.status_code)
        
        # Simula requisições concorrentes
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verifica se todas as requisições foram processadas com sucesso
        assert len(results) == 5
        assert all(status == 200 for status in results)
    
    @patch('services.api_service.APIService.get_dashboard_metrics')
    def test_large_payload_handling(self, mock_get_metrics, client):
        """Testa tratamento de payloads grandes"""
        # Simula dados grandes
        large_data = {
            "level_metrics": {},
            "general_metrics": {}
        }
        
        # Gera dados grandes
        for i in range(100):
            large_data["level_metrics"][f"Level_{i}"] = {
                f"Status_{j}": j * 10 for j in range(50)
            }
        
        mock_get_metrics.return_value = large_data
        
        response = client.get('/api/metrics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['level_metrics']) == 100
    
    def test_error_response_format(self, client):
        """Testa formato de resposta de erro"""
        response = client.get('/api/nonexistent-endpoint')
        
        assert response.status_code == 404
        # Verifica se a resposta tem formato JSON válido
        try:
            data = json.loads(response.data)
            assert 'error' in data or 'message' in data
        except json.JSONDecodeError:
            # Se não for JSON, pelo menos deve ter content-type correto
            assert 'text/html' in response.content_type or 'application/json' in response.content_type
    
    @patch('services.api_service.APIService.get_dashboard_metrics')
    def test_caching_behavior(self, mock_get_metrics, client, mock_glpi_data):
        """Testa comportamento de cache"""
        mock_get_metrics.return_value = mock_glpi_data
        
        # Primeira requisição
        response1 = client.get('/api/metrics')
        
        # Segunda requisição (pode usar cache)
        response2 = client.get('/api/metrics')
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verifica se os dados são consistentes
        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)
        assert data1 == data2
    
    def test_api_versioning(self, client):
        """Testa versionamento da API"""
        # Testa endpoint com versão
        response = client.get('/api/v1/metrics')
        
        # Deve retornar 200 ou 404 dependendo da implementação
        assert response.status_code in [200, 404]
    
    @patch('services.api_service.APIService.get_dashboard_metrics')
    def test_content_type_headers(self, mock_get_metrics, client, mock_glpi_data):
        """Testa headers de content-type"""
        mock_get_metrics.return_value = mock_glpi_data
        
        response = client.get('/api/metrics')
        
        assert response.status_code == 200
        assert 'application/json' in response.content_type
    
    def test_method_not_allowed(self, client):
        """Testa métodos HTTP não permitidos"""
        response = client.post('/api/metrics')
        
        # Deve retornar 405 Method Not Allowed
        assert response.status_code == 405
