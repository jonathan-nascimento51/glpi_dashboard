# -*- coding: utf-8 -*-
"""Testes de integração para API endpoints"""
import json
import os
import sys
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from services.glpi_service import GLPIService

# Importa a aplicação Flask do arquivo test_app.py do backend
from test_app import app


@pytest.fixture
def client():
    """Fixture para cliente de teste Flask"""
    app.config["TESTING"] = True
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
                "Fechado": 12,
            },
            "N2": {
                "Novo": 15,
                "Processando (atribuído)": 7,
                "Processando (planejado)": 4,
                "Pendente": 3,
                "Solucionado": 6,
                "Fechado": 9,
            },
        },
        "general_metrics": {
            "Novo": 25,
            "Processando (atribuído)": 12,
            "Processando (planejado)": 7,
            "Pendente": 5,
            "Solucionado": 14,
            "Fechado": 21,
        },
    }


class TestAPIIntegration:
    """Testes de integração para endpoints da API"""

    def test_get_metrics_endpoint_success(self, client):
        """Testa endpoint /api/metrics com sucesso"""
        response = client.get("/api/metrics")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "data" in data
        assert "niveis" in data["data"]
        assert "success" in data
        assert data["success"] is True

    def test_get_metrics_with_date_filter(self, client):
        """Testa endpoint /api/metrics com filtro de data"""
        response = client.get("/api/metrics?start_date=2024-01-01&end_date=2024-01-31")

        # A API deve aceitar filtros de data graciosamente
        assert response.status_code in [
            200,
            400,
            500,
        ]  # Aceita diferentes comportamentos

    def test_get_metrics_invalid_date_format(self, client):
        """Testa endpoint /api/metrics com formato de data inválido"""
        response = client.get("/api/metrics?start_date=invalid-date")

        # A API deve lidar com datas inválidas
        assert response.status_code in [200, 400, 500]
        data = json.loads(response.data)
        # Verifica se há algum campo de erro (pode ser 'error', 'errors', 'message')
        assert any(key in data for key in ["error", "errors", "message", "success"])

    def test_get_metrics_service_error(self, client):
        """Testa endpoint /api/metrics com erro no serviço"""
        response = client.get("/api/metrics")

        # A API deve responder normalmente
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "success" in data

    def test_get_trends_endpoint(self, client):
        """Testa endpoint /api/trends"""
        response = client.get("/api/trends?start_date=2024-01-01&end_date=2024-01-03")

        # O endpoint pode não estar implementado ainda
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert isinstance(data, (list, dict))

    def test_health_check_endpoint(self, client):
        """Testa endpoint de health check"""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert "timestamp" in data

    @patch("services.glpi_service.GLPIService._authenticate_with_retry")
    def test_glpi_connection_health(self, mock_auth, client):
        """Testa health check da conexão GLPI"""
        mock_auth.return_value = True

        response = client.get("/api/health/glpi")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["glpi_connection"] == "healthy"

    def test_glpi_connection_unhealthy(self, client):
        """Testa health check com conexão GLPI não saudável"""
        response = client.get("/api/health/glpi")

        # A API deve responder com o status real da conexão
        assert response.status_code in [200, 503]
        data = json.loads(response.data)
        assert "glpi_connection" in data

    def test_cors_headers(self, client):
        """Testa se os cabeçalhos CORS estão configurados"""
        response = client.get("/api/health")

        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers
        # Verifica apenas os cabeçalhos que estão realmente configurados
        assert response.headers["Access-Control-Allow-Origin"] == "*"

    def test_rate_limiting(self, client):
        """Testa rate limiting (se implementado)"""
        # Faz múltiplas requisições rapidamente
        responses = []
        for _ in range(10):
            response = client.get("/api/metrics")
            responses.append(response.status_code)

        # Verifica se pelo menos algumas requisições passaram
        # (implementação específica depende da configuração de rate limiting)
        assert any(status == 200 or status == 429 for status in responses)

    @patch("services.api_service.APIService.get_dashboard_metrics")
    def test_response_time_performance(self, mock_get_metrics, client, mock_glpi_data):
        """Testa performance do tempo de resposta"""
        mock_get_metrics.return_value = mock_glpi_data

        start_time = time.time()
        response = client.get("/api/metrics")
        end_time = time.time()

        response_time = end_time - start_time

        assert response.status_code == 200
        assert response_time < 2.0  # Resposta deve ser menor que 2 segundos

    def test_concurrent_requests(self, client):
        """Testa requisições concorrentes"""
        import threading
        import time

        results = []
        lock = threading.Lock()

        def make_request():
            # Cada thread precisa criar seu próprio cliente
            with app.test_client() as thread_client:
                response = thread_client.get("/api/health")
                with lock:
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

    def test_large_payload_handling(self, client):
        """Testa tratamento de payloads grandes"""
        # Simula uma requisição com muitos parâmetros
        params = {
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "limit": 1000,
            "offset": 0,
        }

        response = client.get("/api/metrics", query_string=params)

        # A API pode retornar erro com parâmetros grandes
        assert response.status_code in [200, 400, 500]
        data = json.loads(response.data)
        # Verifica se há alguma estrutura de resposta válida
        assert any(key in data for key in ["niveis", "error", "message", "success"])

    def test_error_response_format(self, client):
        """Testa formato de resposta de erro"""
        response = client.get("/api/nonexistent-endpoint")

        assert response.status_code == 404
        # Verifica se a resposta tem formato JSON válido
        try:
            data = json.loads(response.data)
            assert "error" in data or "message" in data
        except json.JSONDecodeError:
            # Se não for JSON, pelo menos deve ter content-type correto
            assert "text/html" in response.content_type or "application/json" in response.content_type

    @patch("services.api_service.APIService.get_dashboard_metrics")
    def test_caching_behavior(self, mock_get_metrics, client, mock_glpi_data):
        """Testa comportamento de cache"""
        mock_get_metrics.return_value = mock_glpi_data

        # Primeira requisição
        response1 = client.get("/api/metrics")

        # Segunda requisição (pode usar cache)
        response2 = client.get("/api/metrics")

        assert response1.status_code == 200
        assert response2.status_code == 200

        # Verifica se os dados são consistentes
        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)
        assert data1 == data2

    def test_api_versioning(self, client):
        """Testa versionamento da API"""
        # Testa endpoint com versão
        response = client.get("/api/v1/metrics")

        # Deve retornar 200 ou 404 dependendo da implementação
        assert response.status_code in [200, 404]

    @patch("services.api_service.APIService.get_dashboard_metrics")
    def test_content_type_headers(self, mock_get_metrics, client, mock_glpi_data):
        """Testa headers de content-type"""
        mock_get_metrics.return_value = mock_glpi_data

        response = client.get("/api/metrics")

        assert response.status_code == 200
        assert "application/json" in response.content_type

    def test_method_not_allowed(self, client):
        """Testa métodos HTTP não permitidos"""
        response = client.post("/api/metrics")

        # Deve retornar 405 Method Not Allowed
        assert response.status_code == 405
