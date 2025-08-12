# -*- coding: utf-8 -*-
"""Testes de integracao para API endpoints"""

import pytest
import time
from fastapi.testclient import TestClient

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from main import app


@pytest.fixture
def client():
    """Fixture para cliente de teste FastAPI"""
    return TestClient(app)


@pytest.fixture
def mock_glpi_data():
    """Dados mock para testes de integracao"""
    return {
        "level_metrics": {
            "N1": {"Novo": 10, "Pendente": 5, "Em Progresso": 3, "Resolvido": 15},
            "N2": {"Novo": 8, "Pendente": 4, "Em Progresso": 2, "Resolvido": 12},
        },
        "tickets": [
            {
                "id": 1,
                "title": "Teste Ticket 1",
                "status": "Novo",
                "priority": "Alta",
                "date": "2024-01-15",
            },
            {
                "id": 2,
                "title": "Teste Ticket 2",
                "status": "Pendente",
                "priority": "Media",
                "date": "2024-01-16",
            },
        ],
    }


class TestAPIIntegration:
    """Testes de integracao para endpoints da API"""

    def test_health_endpoint(self, client):
        """Testa o endpoint de health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_kpis_endpoint(self, client):
        """Testa o endpoint de KPIs"""
        response = client.get("/v1/kpis")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "data" in data

    def test_tickets_new_endpoint(self, client):
        """Testa o endpoint de tickets novos"""
        response = client.get("/v1/tickets/new")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "data" in data

    def test_tickets_new_with_limit(self, client):
        """Testa o endpoint de tickets novos com limite"""
        response = client.get("/v1/tickets/new?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "data" in data

    def test_invalid_endpoint(self, client):
        """Testa endpoint invalido"""
        response = client.get("/v1/invalid")
        assert response.status_code == 404

    def test_response_time_performance(self, client):
        """Testa performance de tempo de resposta"""
        start_time = time.time()
        response = client.get("/v1/kpis")
        end_time = time.time()

        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 2.0  # Menos de 2 segundos

    def test_concurrent_requests(self, client):
        """Testa requisicoes concorrentes"""
        import threading
        import queue

        results = queue.Queue()

        def make_request():
            response = client.get("/v1/kpis")
            results.put(response.status_code)

        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Verificar se todas as requisicoes foram bem-sucedidas
        status_codes = []
        while not results.empty():
            status_codes.append(results.get())

        assert len(status_codes) == 5
        assert all(code == 200 for code in status_codes)

    def test_large_payload_handling(self, client):
        """Testa manipulacao de payloads grandes"""
        # Simular uma requisicao com parametros grandes
        large_params = {"filter": "x" * 1000}
        response = client.get("/v1/tickets/new", params=large_params)
        assert response.status_code in [
            200,
            400,
        ]  # Aceitar tanto sucesso quanto erro de validacao

    def test_error_response_format(self, client):
        """Testa formato de resposta de erro"""
        response = client.get("/v1/invalid")
        assert response.status_code == 404
        # FastAPI retorna formato padrao de erro

    def test_caching_behavior(self, client):
        """Testa comportamento de cache"""
        # Fazer duas requisicoes identicas
        response1 = client.get("/v1/kpis")
        response2 = client.get("/v1/kpis")

        assert response1.status_code == 200
        assert response2.status_code == 200
        # Verificar se as respostas sao consistentes
        assert response1.json().keys() == response2.json().keys()

    def test_api_versioning(self, client):
        """Testa versionamento da API"""
        response = client.get("/v1/kpis")
        assert response.status_code == 200

        # Testar versao inexistente
        response_v2 = client.get("/v2/kpis")
        assert response_v2.status_code == 404

    def test_content_type_headers(self, client):
        """Testa headers de content-type"""
        response = client.get("/v1/kpis")
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")

    def test_method_not_allowed(self, client):
        """Testa metodo nao permitido"""
        response = client.post("/v1/kpis")
        assert response.status_code == 405
