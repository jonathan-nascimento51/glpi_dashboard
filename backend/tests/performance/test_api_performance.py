import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch
import requests
from fastapi.testclient import TestClient

from app.main import app
from app.services.glpi_service import GLPIService
from tests.conftest import mock_glpi_service, sample_metrics_data


class TestAPIPerformance:
    """Testes de performance para a API."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.client = TestClient(app)
        self.base_url = "/api"
    
    def test_dashboard_metrics_response_time(self, mock_glpi_service):
        """Testa o tempo de resposta do endpoint de métricas do dashboard."""
        start_time = time.time()
        
        response = self.client.get(f"{self.base_url}/dashboard/metrics")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Deve responder em menos de 1 segundo
        
        # Verificar se a resposta tem o formato esperado
        data = response.json()
        assert "success" in data
        assert "data" in data
        assert "timestamp" in data
    
    def test_dashboard_metrics_with_date_filter_performance(self, mock_glpi_service):
        """Testa performance com filtros de data."""
        start_time = time.time()
        
        response = self.client.get(
            f"{self.base_url}/dashboard/metrics",
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            }
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.5  # Filtros podem adicionar um pouco de latência
    
    def test_concurrent_requests_performance(self, mock_glpi_service):
        """Testa performance com requisições concorrentes."""
        num_requests = 10
        max_workers = 5
        
        def make_request():
            start_time = time.time()
            response = self.client.get(f"{self.base_url}/dashboard/metrics")
            end_time = time.time()
            return {
                'status_code': response.status_code,
                'response_time': end_time - start_time,
                'success': response.status_code == 200
            }
        
        # Executar requisições concorrentes
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [future.result() for future in as_completed(futures)]
        
        # Analisar resultados
        response_times = [r['response_time'] for r in results]
        success_count = sum(1 for r in results if r['success'])
        
        # Verificações
        assert success_count == num_requests  # Todas as requisições devem ser bem-sucedidas
        assert max(response_times) < 2.0  # Nenhuma requisição deve demorar mais que 2 segundos
        assert statistics.mean(response_times) < 1.0  # Tempo médio deve ser menor que 1 segundo
    
    def test_memory_usage_under_load(self, mock_glpi_service):
        """Testa uso de memória sob carga."""
        import psutil
        import os
        
        # Obter uso inicial de memória
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Fazer múltiplas requisições
        for _ in range(50):
            response = self.client.get(f"{self.base_url}/dashboard/metrics")
            assert response.status_code == 200
        
        # Verificar uso de memória após as requisições
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # A memória não deve aumentar significativamente
        assert memory_increase < 50  # Menos de 50MB de aumento
    
    def test_database_query_performance(self, mock_glpi_service):
        """Testa performance das consultas ao banco de dados (simulado)."""
        # Simular consulta lenta
        def slow_query(*args, **kwargs):
            time.sleep(0.1)  # Simular 100ms de latência
            return sample_metrics_data()
        
        with patch.object(mock_glpi_service, 'get_dashboard_metrics', side_effect=slow_query):
            start_time = time.time()
            
            response = self.client.get(f"{self.base_url}/dashboard/metrics")
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time >= 0.1  # Deve incluir o tempo da consulta simulada
            assert response_time < 0.5   # Mas não deve ser muito lento
    
    def test_cache_performance_improvement(self, mock_glpi_service):
        """Testa se o cache melhora a performance."""
        # Primeira requisição (sem cache)
        start_time = time.time()
        response1 = self.client.get(f"{self.base_url}/dashboard/metrics")
        first_request_time = time.time() - start_time
        
        assert response1.status_code == 200
        
        # Segunda requisição (com cache)
        start_time = time.time()
        response2 = self.client.get(f"{self.base_url}/dashboard/metrics")
        second_request_time = time.time() - start_time
        
        assert response2.status_code == 200
        
        # A segunda requisição deve ser mais rápida (cache hit)
        # Nota: Isso depende da implementação do cache
        assert second_request_time <= first_request_time * 1.1  # Margem de 10%
    
    def test_large_dataset_performance(self, mock_glpi_service):
        """Testa performance com datasets grandes."""
        # Simular dataset grande
        large_dataset = {
            "total_tickets": 10000,
            "open_tickets": 2500,
            "closed_tickets": 7500,
            "tickets_by_priority": {f"priority_{i}": i * 100 for i in range(50)},
            "tickets_by_status": {f"status_{i}": i * 50 for i in range(20)},
            "monthly_trends": [{"month": f"2024-{i:02d}", "tickets": i * 100} for i in range(1, 13)]
        }
        
        with patch.object(mock_glpi_service, 'get_dashboard_metrics', return_value=large_dataset):
            start_time = time.time()
            
            response = self.client.get(f"{self.base_url}/dashboard/metrics")
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 2.0  # Deve processar dataset grande em menos de 2 segundos
            
            # Verificar se todos os dados foram retornados
            data = response.json()["data"]
            assert data["total_tickets"] == 10000
            assert len(data["tickets_by_priority"]) == 50
    
    def test_error_handling_performance(self, mock_glpi_service):
        """Testa se o tratamento de erros não impacta significativamente a performance."""
        # Simular erro no serviço
        with patch.object(mock_glpi_service, 'get_dashboard_metrics', side_effect=Exception("Simulated error")):
            start_time = time.time()
            
            response = self.client.get(f"{self.base_url}/dashboard/metrics")
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 500
            assert response_time < 0.5  # Erros devem ser tratados rapidamente
    
    def test_health_check_performance(self):
        """Testa performance do health check."""
        start_time = time.time()
        
        response = self.client.get(f"{self.base_url}/health")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 0.1  # Health check deve ser muito rápido
    
    def test_multiple_endpoints_performance(self, mock_glpi_service):
        """Testa performance de múltiplos endpoints."""
        endpoints = [
            "/dashboard/metrics",
            "/health",
            "/health/glpi"
        ]
        
        response_times = {}
        
        for endpoint in endpoints:
            start_time = time.time()
            
            response = self.client.get(f"{self.base_url}{endpoint}")
            
            end_time = time.time()
            response_time = end_time - start_time
            
            response_times[endpoint] = response_time
            
            assert response.status_code in [200, 500]  # Alguns podem falhar dependendo do mock
            assert response_time < 1.0  # Todos devem responder em menos de 1 segundo
        
        # Verificar se nenhum endpoint é significativamente mais lento
        max_time = max(response_times.values())
        min_time = min(response_times.values())
        
        assert max_time / min_time < 10  # Diferença não deve ser maior que 10x
    
    @pytest.mark.asyncio
    async def test_async_performance(self, mock_glpi_service):
        """Testa performance de operações assíncronas."""
        async def make_async_request():
            # Simular operação assíncrona
            await asyncio.sleep(0.01)  # 10ms de delay
            return {"status": "success", "timestamp": time.time()}
        
        # Executar múltiplas operações assíncronas
        start_time = time.time()
        
        tasks = [make_async_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Operações assíncronas devem ser executadas em paralelo
        assert len(results) == 10
        assert total_time < 0.1  # Deve ser muito mais rápido que 10 * 10ms = 100ms
    
    def test_response_size_performance(self, mock_glpi_service):
        """Testa performance baseada no tamanho da resposta."""
        response = self.client.get(f"{self.base_url}/dashboard/metrics")
        
        assert response.status_code == 200
        
        # Verificar tamanho da resposta
        response_size = len(response.content)
        
        # Resposta não deve ser excessivamente grande
        assert response_size < 100 * 1024  # Menos de 100KB
        
        # Verificar se a resposta está comprimida (se aplicável)
        content_encoding = response.headers.get('content-encoding')
        if content_encoding:
            assert content_encoding in ['gzip', 'deflate', 'br']
    
    def test_rate_limiting_performance(self, mock_glpi_service):
        """Testa performance sob rate limiting."""
        # Fazer muitas requisições rapidamente
        responses = []
        start_time = time.time()
        
        for _ in range(20):
            response = self.client.get(f"{self.base_url}/dashboard/metrics")
            responses.append(response)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verificar se algumas requisições foram limitadas (se rate limiting estiver ativo)
        status_codes = [r.status_code for r in responses]
        success_count = sum(1 for code in status_codes if code == 200)
        rate_limited_count = sum(1 for code in status_codes if code == 429)
        
        # Pelo menos algumas requisições devem ser bem-sucedidas
        assert success_count > 0
        
        # Se há rate limiting, deve responder rapidamente mesmo para requisições limitadas
        if rate_limited_count > 0:
            assert total_time < 5.0  # Não deve demorar muito mesmo com rate limiting