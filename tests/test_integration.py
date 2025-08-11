"""Testes de integração para validar fluxos completos."""

import pytest
import json
import time
from unittest.mock import patch, Mock
from concurrent.futures import ThreadPoolExecutor, as_completed


class TestIntegration:
    """Testes de integração para fluxos completos."""
    
    @pytest.mark.integration
    def test_complete_dashboard_flow(self, client, mock_glpi_service):
        """Testa fluxo completo do dashboard: métricas + ranking + status."""
        with patch('backend.api.routes.glpi_service', mock_glpi_service):
            # 1. Obter métricas do dashboard
            metrics_response = client.get('/api/dashboard/metrics')
            assert metrics_response.status_code == 200
            metrics_data = json.loads(metrics_response.data)
            assert metrics_data['success'] is True
            
            # 2. Obter ranking de técnicos
            ranking_response = client.get('/api/technicians/ranking')
            assert ranking_response.status_code == 200
            ranking_data = json.loads(ranking_response.data)
            assert ranking_data['success'] is True
            
            # 3. Verificar status do sistema
            status_response = client.get('/api/status')
            assert status_response.status_code == 200
            status_data = json.loads(status_response.data)
            assert status_data['success'] is True
            
            # 4. Validar consistência dos dados
            assert isinstance(metrics_data['data']['novos'], int)
            assert isinstance(ranking_data['data'], list)
            assert status_data['data']['status'] in ['online', 'offline']
    
    @pytest.mark.integration
    def test_date_filter_consistency(self, client, mock_glpi_service):
        """Testa consistência de filtros de data entre endpoints."""
        start_date = '2024-01-01'
        end_date = '2024-01-31'
        
        with patch('backend.api.routes.glpi_service', mock_glpi_service):
            # Testar métricas com filtro de data
            metrics_response = client.get(
                f'/api/dashboard/metrics?start_date={start_date}&end_date={end_date}'
            )
            assert metrics_response.status_code == 200
            
            # Testar ranking com mesmo filtro
            ranking_response = client.get(
                f'/api/technicians/ranking?start_date={start_date}&end_date={end_date}'
            )
            assert ranking_response.status_code == 200
            
            # Verificar que ambos os serviços foram chamados com os mesmos parâmetros
            metrics_call = mock_glpi_service.get_dashboard_metrics.call_args[1]
            ranking_call = mock_glpi_service.get_technician_ranking.call_args[1]
            
            assert metrics_call['start_date'] == start_date
            assert metrics_call['end_date'] == end_date
            assert ranking_call['start_date'] == start_date
            assert ranking_call['end_date'] == end_date
    
    @pytest.mark.integration
    def test_cache_behavior_across_endpoints(self, client, mock_glpi_service):
        """Testa comportamento do cache entre diferentes endpoints."""
        with patch('backend.api.routes.glpi_service', mock_glpi_service):
            # 1. Primeira requisição - deve popular cache
            response1 = client.get('/api/dashboard/metrics')
            assert response1.status_code == 200
            
            # 2. Segunda requisição - deve usar cache
            response2 = client.get('/api/dashboard/metrics')
            assert response2.status_code == 200
            
            # 3. Invalidar cache
            cache_response = client.post('/api/cache/invalidate')
            assert cache_response.status_code == 200
            
            # 4. Nova requisição - deve recarregar dados
            response3 = client.get('/api/dashboard/metrics')
            assert response3.status_code == 200
            
            # Verificar que invalidação foi chamada
            mock_glpi_service.invalidate_cache.assert_called_once()
    
    @pytest.mark.integration
    def test_error_propagation(self, client):
        """Testa propagação de erros através das camadas."""
        with patch('backend.api.routes.glpi_service') as mock_service:
            # Simular erro no serviço GLPI
            mock_service.get_dashboard_metrics.side_effect = Exception("GLPI connection failed")
            
            response = client.get('/api/dashboard/metrics')
            
            # Verificar que erro foi tratado adequadamente
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'error' in data
            assert 'GLPI' in data['error'] or 'connection' in data['error'].lower()
    
    @pytest.mark.integration
    def test_concurrent_requests_different_endpoints(self, client, mock_glpi_service):
        """Testa requisições concorrentes em endpoints diferentes."""
        endpoints = [
            '/api/dashboard/metrics',
            '/api/technicians/ranking',
            '/api/status',
            '/api/health'
        ]
        
        def make_request(endpoint):
            with patch('backend.api.routes.glpi_service', mock_glpi_service):
                return client.get(endpoint)
        
        # Executar requisições concorrentes
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(make_request, endpoint) for endpoint in endpoints]
            responses = [future.result() for future in as_completed(futures)]
        
        # Verificar que todas foram bem-sucedidas
        for response in responses:
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data.get('success', True) is True
    
    @pytest.mark.integration
    def test_data_validation_pipeline(self, client, mock_glpi_service):
        """Testa pipeline completo de validação de dados."""
        with patch('backend.api.routes.glpi_service', mock_glpi_service):
            # Testar com dados válidos
            response = client.get('/api/dashboard/metrics?start_date=2024-01-01&end_date=2024-01-31')
            assert response.status_code == 200
            
            # Testar com formato de data inválido
            response = client.get('/api/dashboard/metrics?start_date=invalid-date')
            assert response.status_code == 400
            
            # Testar com data de fim anterior à de início
            response = client.get('/api/dashboard/metrics?start_date=2024-01-31&end_date=2024-01-01')
            assert response.status_code == 400
            
            # Testar com parâmetros extras
            response = client.get('/api/dashboard/metrics?start_date=2024-01-01&extra_param=value')
            assert response.status_code == 200  # Parâmetros extras devem ser ignorados
    
    @pytest.mark.integration
    def test_performance_under_load(self, client, mock_glpi_service):
        """Testa performance sob carga."""
        def make_multiple_requests(count=10):
            times = []
            for _ in range(count):
                start_time = time.time()
                with patch('backend.api.routes.glpi_service', mock_glpi_service):
                    response = client.get('/api/dashboard/metrics')
                end_time = time.time()
                
                assert response.status_code == 200
                times.append(end_time - start_time)
            
            return times
        
        # Executar teste de carga
        response_times = make_multiple_requests(20)
        
        # Verificar métricas de performance
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        
        # Assertions de performance
        assert avg_time < 0.5  # Tempo médio < 500ms
        assert max_time < 1.0  # Tempo máximo < 1s
        assert all(t < 2.0 for t in response_times)  # Nenhuma requisição > 2s
    
    @pytest.mark.integration
    def test_memory_usage_stability(self, client, mock_glpi_service):
        """Testa estabilidade do uso de memória."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Fazer muitas requisições
        with patch('backend.api.routes.glpi_service', mock_glpi_service):
            for _ in range(100):
                response = client.get('/api/dashboard/metrics')
                assert response.status_code == 200
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Verificar que não houve vazamento significativo de memória
        # Permitir aumento de até 50MB
        assert memory_increase < 50 * 1024 * 1024
    
    @pytest.mark.integration
    def test_session_management(self, client, mock_glpi_service):
        """Testa gerenciamento de sessão."""
        with patch('backend.api.routes.glpi_service', mock_glpi_service):
            # Simular múltiplas sessões
            with client.session_transaction() as sess:
                sess['user_id'] = 'test_user'
            
            response1 = client.get('/api/dashboard/metrics')
            assert response1.status_code == 200
            
            # Nova sessão
            with client.session_transaction() as sess:
                sess.clear()
                sess['user_id'] = 'another_user'
            
            response2 = client.get('/api/dashboard/metrics')
            assert response2.status_code == 200
    
    @pytest.mark.integration
    def test_api_versioning_compatibility(self, client, mock_glpi_service):
        """Testa compatibilidade de versionamento da API."""
        with patch('backend.api.routes.glpi_service', mock_glpi_service):
            # Testar endpoint sem versão (padrão)
            response1 = client.get('/api/dashboard/metrics')
            assert response1.status_code == 200
            
            # Testar com header de versão (se implementado)
            headers = {'API-Version': 'v1'}
            response2 = client.get('/api/dashboard/metrics', headers=headers)
            assert response2.status_code == 200
            
            # Verificar estrutura de resposta consistente
            data1 = json.loads(response1.data)
            data2 = json.loads(response2.data)
            
            assert data1.keys() == data2.keys()
    
    @pytest.mark.integration
    def test_logging_and_monitoring_integration(self, client, caplog, mock_glpi_service):
        """Testa integração com logging e monitoramento."""
        with patch('backend.api.routes.glpi_service', mock_glpi_service):
            # Fazer requisições que devem gerar logs
            client.get('/api/dashboard/metrics')
            client.get('/api/technicians/ranking')
            client.post('/api/cache/invalidate')
            
            # Verificar que logs foram gerados
            log_messages = [record.message for record in caplog.records]
            
            # Deve haver logs de requisições
            assert any('metrics' in msg.lower() for msg in log_messages)
            assert any('ranking' in msg.lower() for msg in log_messages)
            assert any('cache' in msg.lower() for msg in log_messages)
    
    @pytest.mark.integration
    def test_graceful_degradation(self, client):
        """Testa degradação graciosa quando serviços estão indisponíveis."""
        with patch('backend.api.routes.glpi_service') as mock_service:
            # Simular falha parcial - métricas falham, mas status funciona
            mock_service.get_dashboard_metrics.side_effect = Exception("Service down")
            mock_service.get_system_status.return_value = {
                'status': 'degraded',
                'api': 'online',
                'glpi': 'offline',
                'last_update': '2024-01-01T00:00:00Z'
            }
            
            # Métricas devem falhar graciosamente
            metrics_response = client.get('/api/dashboard/metrics')
            assert metrics_response.status_code == 500
            
            # Status deve ainda funcionar
            status_response = client.get('/api/status')
            assert status_response.status_code == 200
            
            status_data = json.loads(status_response.data)
            assert status_data['data']['status'] == 'degraded'
    
    @pytest.mark.integration
    def test_data_consistency_across_time(self, client, mock_glpi_service):
        """Testa consistência de dados ao longo do tempo."""
        with patch('backend.api.routes.glpi_service', mock_glpi_service):
            # Coletar dados em intervalos
            snapshots = []
            
            for i in range(3):
                response = client.get('/api/dashboard/metrics')
                assert response.status_code == 200
                
                data = json.loads(response.data)
                snapshots.append(data['data'])
                
                time.sleep(0.1)  # Pequeno intervalo
            
            # Verificar que estrutura permanece consistente
            keys_set = set(snapshots[0].keys())
            for snapshot in snapshots[1:]:
                assert set(snapshot.keys()) == keys_set
            
            # Verificar que tipos de dados permanecem consistentes
            for key in keys_set:
                types = [type(snapshot[key]) for snapshot in snapshots]
                assert all(t == types[0] for t in types)
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_long_running_stability(self, client, mock_glpi_service):
        """Testa estabilidade em execução prolongada."""
        with patch('backend.api.routes.glpi_service', mock_glpi_service):
            # Executar por período prolongado
            start_time = time.time()
            request_count = 0
            errors = 0
            
            while time.time() - start_time < 10:  # 10 segundos
                try:
                    response = client.get('/api/health')
                    if response.status_code != 200:
                        errors += 1
                    request_count += 1
                    time.sleep(0.1)
                except Exception:
                    errors += 1
            
            # Verificar estabilidade
            error_rate = errors / request_count if request_count > 0 else 1
            assert error_rate < 0.01  # Taxa de erro < 1%
            assert request_count > 50  # Pelo menos 50 requisições
    
    @pytest.mark.integration
    def test_cross_origin_requests(self, client, mock_glpi_service):
        """Testa requisições cross-origin (CORS)."""
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        # Testar preflight request
        response = client.options('/api/dashboard/metrics', headers=headers)
        
        # Verificar headers CORS
        assert 'Access-Control-Allow-Origin' in response.headers
        assert 'Access-Control-Allow-Methods' in response.headers
        
        # Testar requisição real
        with patch('backend.api.routes.glpi_service', mock_glpi_service):
            response = client.get('/api/dashboard/metrics', headers={'Origin': 'http://localhost:3000'})
            assert response.status_code == 200
            assert 'Access-Control-Allow-Origin' in response.headers