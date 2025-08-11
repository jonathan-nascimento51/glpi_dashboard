"""Testes para as rotas da API."""

import pytest
import json
from unittest.mock import patch, Mock
from flask import url_for


class TestAPIRoutes:
    """Testes para as rotas da API."""
    
    @pytest.mark.api
    def test_health_check_endpoint(self, client):
        """Testa endpoint de health check."""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
    
    @pytest.mark.api
    def test_test_endpoint(self, client):
        """Testa endpoint de teste simples."""
        response = client.get('/api/test')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Teste funcionando'
        assert data['success'] is True
    
    @pytest.mark.api
    def test_metrics_simple_endpoint(self, client):
        """Testa endpoint de métricas simplificado."""
        response = client.get('/api/metrics/simple')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        
        metrics = data['data']
        assert 'novos' in metrics
        assert 'pendentes' in metrics
        assert 'progresso' in metrics
        assert 'resolvidos' in metrics
        assert 'niveis' in metrics
        assert 'tendencias' in metrics
    
    @pytest.mark.api
    def test_dashboard_metrics_endpoint(self, client, mock_glpi_service):
        """Testa endpoint principal de métricas do dashboard."""
        with patch('backend.api.routes.glpi_service', mock_glpi_service):
            response = client.get('/api/dashboard/metrics')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'data' in data
            
            metrics = data['data']
            assert isinstance(metrics['novos'], int)
            assert isinstance(metrics['niveis'], dict)
            assert 'n1' in metrics['niveis']
            assert 'n2' in metrics['niveis']
    
    @pytest.mark.api
    def test_dashboard_metrics_with_date_filters(self, client, mock_glpi_service):
        """Testa endpoint de métricas com filtros de data."""
        with patch('backend.api.routes.glpi_service', mock_glpi_service):
            response = client.get('/api/dashboard/metrics?start_date=2024-01-01&end_date=2024-01-31')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            
            # Verificar que o serviço foi chamado com os parâmetros corretos
            mock_glpi_service.get_dashboard_metrics.assert_called_once()
            call_kwargs = mock_glpi_service.get_dashboard_metrics.call_args[1]
            assert 'start_date' in call_kwargs
            assert 'end_date' in call_kwargs
    
    @pytest.mark.api
    def test_dashboard_metrics_invalid_date_format(self, client):
        """Testa endpoint com formato de data inválido."""
        response = client.get('/api/dashboard/metrics?start_date=invalid-date')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
        assert 'formato de data' in data['error'].lower()
    
    @pytest.mark.api
    def test_technician_ranking_endpoint(self, client, mock_glpi_service):
        """Testa endpoint de ranking de técnicos."""
        with patch('backend.api.routes.glpi_service', mock_glpi_service):
            response = client.get('/api/technicians/ranking')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'data' in data
            
            ranking = data['data']
            assert isinstance(ranking, list)
            assert len(ranking) > 0
            
            # Verificar estrutura do primeiro técnico
            first_tech = ranking[0]
            assert 'id' in first_tech
            assert 'name' in first_tech
            assert 'score' in first_tech
            assert 'rank' in first_tech
    
    @pytest.mark.api
    def test_technician_ranking_with_limit(self, client, mock_glpi_service):
        """Testa endpoint de ranking com limite."""
        with patch('backend.api.routes.glpi_service', mock_glpi_service):
            response = client.get('/api/technicians/ranking?limit=5')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            # Verificar que o limite foi passado para o serviço
            mock_glpi_service.get_technician_ranking.assert_called_once()
            call_kwargs = mock_glpi_service.get_technician_ranking.call_args[1]
            assert call_kwargs.get('limit') == 5
    
    @pytest.mark.api
    def test_technician_ranking_with_date_filters(self, client, mock_glpi_service):
        """Testa endpoint de ranking com filtros de data."""
        with patch('backend.api.routes.glpi_service', mock_glpi_service):
            response = client.get('/api/technicians/ranking?start_date=2024-01-01&end_date=2024-01-31')
            
            assert response.status_code == 200
            
            # Verificar parâmetros passados
            call_kwargs = mock_glpi_service.get_technician_ranking.call_args[1]
            assert 'start_date' in call_kwargs
            assert 'end_date' in call_kwargs
    
    @pytest.mark.api
    def test_system_status_endpoint(self, client, mock_glpi_service):
        """Testa endpoint de status do sistema."""
        with patch('backend.api.routes.glpi_service', mock_glpi_service):
            response = client.get('/api/status')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'data' in data
            
            status = data['data']
            assert 'status' in status
            assert 'api' in status
            assert 'glpi' in status
            assert 'last_update' in status
    
    @pytest.mark.api
    def test_cache_invalidation_endpoint(self, client, mock_glpi_service):
        """Testa endpoint de invalidação de cache."""
        with patch('backend.api.routes.glpi_service', mock_glpi_service):
            response = client.post('/api/cache/invalidate')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'message' in data
            
            # Verificar que o método de invalidação foi chamado
            mock_glpi_service.invalidate_cache.assert_called_once()
    
    @pytest.mark.api
    def test_error_handling_service_unavailable(self, client):
        """Testa tratamento de erro quando serviço está indisponível."""
        with patch('backend.api.routes.glpi_service') as mock_service:
            mock_service.get_dashboard_metrics.side_effect = Exception("Service unavailable")
            
            response = client.get('/api/dashboard/metrics')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'error' in data
    
    @pytest.mark.api
    def test_cors_headers(self, client):
        """Testa se headers CORS estão configurados."""
        response = client.get('/api/health')
        
        # Verificar headers CORS
        assert 'Access-Control-Allow-Origin' in response.headers
    
    @pytest.mark.api
    def test_content_type_json(self, client):
        """Testa se Content-Type é application/json."""
        response = client.get('/api/health')
        
        assert response.content_type == 'application/json'
    
    @pytest.mark.api
    def test_rate_limiting(self, client):
        """Testa limitação de taxa de requisições (se implementada)."""
        # Fazer múltiplas requisições rapidamente
        responses = []
        for _ in range(10):
            response = client.get('/api/health')
            responses.append(response.status_code)
        
        # Verificar que pelo menos algumas requisições foram bem-sucedidas
        success_count = sum(1 for status in responses if status == 200)
        assert success_count > 0
    
    @pytest.mark.api
    def test_endpoint_not_found(self, client):
        """Testa endpoint inexistente."""
        response = client.get('/api/nonexistent')
        
        assert response.status_code == 404
    
    @pytest.mark.api
    def test_method_not_allowed(self, client):
        """Testa método HTTP não permitido."""
        response = client.post('/api/health')  # GET endpoint
        
        assert response.status_code == 405
    
    @pytest.mark.api
    def test_request_validation(self, client):
        """Testa validação de parâmetros de requisição."""
        # Testar limite inválido
        response = client.get('/api/technicians/ranking?limit=invalid')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
    
    @pytest.mark.api
    def test_response_time(self, client, mock_glpi_service):
        """Testa tempo de resposta dos endpoints."""
        import time
        
        with patch('backend.api.routes.glpi_service', mock_glpi_service):
            start_time = time.time()
            response = client.get('/api/dashboard/metrics')
            end_time = time.time()
            
            assert response.status_code == 200
            
            # Verificar que resposta foi rápida (< 1 segundo)
            response_time = end_time - start_time
            assert response_time < 1.0
    
    @pytest.mark.api
    def test_concurrent_requests(self, client, mock_glpi_service):
        """Testa requisições concorrentes."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            with patch('backend.api.routes.glpi_service', mock_glpi_service):
                response = client.get('/api/health')
                results.put(response.status_code)
        
        # Criar múltiplas threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Aguardar conclusão
        for thread in threads:
            thread.join()
        
        # Verificar resultados
        status_codes = []
        while not results.empty():
            status_codes.append(results.get())
        
        # Todas as requisições devem ter sido bem-sucedidas
        assert all(status == 200 for status in status_codes)
        assert len(status_codes) == 5
    
    @pytest.mark.api
    def test_data_consistency(self, client, mock_glpi_service):
        """Testa consistência dos dados entre requisições."""
        with patch('backend.api.routes.glpi_service', mock_glpi_service):
            # Fazer duas requisições idênticas
            response1 = client.get('/api/dashboard/metrics')
            response2 = client.get('/api/dashboard/metrics')
            
            assert response1.status_code == 200
            assert response2.status_code == 200
            
            data1 = json.loads(response1.data)
            data2 = json.loads(response2.data)
            
            # Dados devem ser consistentes (assumindo cache)
            assert data1['data'] == data2['data']
    
    @pytest.mark.api
    def test_logging_integration(self, client, caplog):
        """Testa integração com sistema de logging."""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        
        # Verificar que requisição foi logada
        assert any('health' in record.message.lower() for record in caplog.records)