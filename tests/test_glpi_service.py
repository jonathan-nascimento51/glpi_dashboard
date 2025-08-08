"""Testes unitários para o serviço GLPI."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json

from backend.services.glpi_service import GLPIService


class TestGLPIService:
    """Testes para a classe GLPIService."""
    
    @pytest.fixture
    def glpi_service(self, mock_redis, mock_requests):
        """Instância do GLPIService para testes."""
        with patch.dict('os.environ', {
            'GLPI_URL': 'http://test-glpi.com',
            'GLPI_USER_TOKEN': 'test_user_token',
            'GLPI_APP_TOKEN': 'test_app_token'
        }):
            service = GLPIService()
            service.redis_client = mock_redis
            return service
    
    def test_init_with_environment_variables(self):
        """Testa inicialização com variáveis de ambiente."""
        with patch.dict('os.environ', {
            'GLPI_URL': 'http://test.com',
            'GLPI_USER_TOKEN': 'user123',
            'GLPI_APP_TOKEN': 'app123'
        }):
            service = GLPIService()
            assert service.base_url == 'http://test.com'
            assert service.user_token == 'user123'
            assert service.app_token == 'app123'
    
    def test_init_without_environment_variables(self):
        """Testa inicialização sem variáveis de ambiente."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="GLPI_URL não configurada"):
                GLPIService()
    
    @pytest.mark.unit
    def test_authenticate_success(self, glpi_service, mock_requests):
        """Testa autenticação bem-sucedida."""
        # Configurar mock da resposta
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'session_token': 'test_session_token'}
        mock_requests.post.return_value = mock_response
        
        # Executar autenticação
        result = glpi_service._authenticate()
        
        # Verificar resultado
        assert result is True
        assert glpi_service.session_token == 'test_session_token'
        
        # Verificar chamada da API
        mock_requests.post.assert_called_once()
        call_args = mock_requests.post.call_args
        assert 'initSession' in call_args[0][0]
    
    @pytest.mark.unit
    def test_authenticate_failure(self, glpi_service, mock_requests):
        """Testa falha na autenticação."""
        # Configurar mock da resposta de erro
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {'error': 'Invalid credentials'}
        mock_requests.post.return_value = mock_response
        
        # Executar autenticação
        result = glpi_service._authenticate()
        
        # Verificar resultado
        assert result is False
        assert glpi_service.session_token is None
    
    @pytest.mark.unit
    def test_get_cache_key(self, glpi_service):
        """Testa geração de chaves de cache."""
        key = glpi_service._get_cache_key('test_method', param1='value1', param2='value2')
        expected = 'glpi:test_method:param1=value1:param2=value2'
        assert key == expected
    
    @pytest.mark.unit
    def test_cache_get_hit(self, glpi_service, mock_redis):
        """Testa recuperação de dados do cache (cache hit)."""
        # Configurar cache
        test_data = {'test': 'data'}
        mock_redis.get.return_value = json.dumps(test_data).encode()
        
        # Testar recuperação
        result = glpi_service._cache_get('test_key')
        
        # Verificar resultado
        assert result == test_data
        mock_redis.get.assert_called_once_with('test_key')
    
    @pytest.mark.unit
    def test_cache_get_miss(self, glpi_service, mock_redis):
        """Testa recuperação de dados do cache (cache miss)."""
        # Configurar cache vazio
        mock_redis.get.return_value = None
        
        # Testar recuperação
        result = glpi_service._cache_get('test_key')
        
        # Verificar resultado
        assert result is None
        mock_redis.get.assert_called_once_with('test_key')
    
    @pytest.mark.unit
    def test_cache_set(self, glpi_service, mock_redis):
        """Testa armazenamento de dados no cache."""
        test_data = {'test': 'data'}
        
        # Testar armazenamento
        glpi_service._cache_set('test_key', test_data, 300)
        
        # Verificar chamada
        mock_redis.set.assert_called_once_with(
            'test_key',
            json.dumps(test_data),
            ex=300
        )
    
    @pytest.mark.unit
    def test_is_dtic_technician_true(self, glpi_service):
        """Testa identificação de técnico da DTIC (positivo)."""
        with patch.object(glpi_service, '_get_user_groups') as mock_groups:
            mock_groups.return_value = [10, 11, 12]  # IDs dos grupos DTIC
            
            result = glpi_service._is_dtic_technician('123')
            assert result is True
    
    @pytest.mark.unit
    def test_is_dtic_technician_false(self, glpi_service):
        """Testa identificação de técnico da DTIC (negativo)."""
        with patch.object(glpi_service, '_get_user_groups') as mock_groups:
            mock_groups.return_value = [20, 21, 22]  # IDs de outros grupos
            
            result = glpi_service._is_dtic_technician('123')
            assert result is False
    
    @pytest.mark.unit
    def test_calculate_technician_score(self, glpi_service):
        """Testa cálculo do score do técnico."""
        # Dados de teste
        tickets_data = {
            'abertos': 5,
            'fechados': 20,
            'tempo_medio': 2.5  # dias
        }
        
        score = glpi_service._calculate_technician_score(tickets_data)
        
        # Verificar que o score é calculado corretamente
        assert isinstance(score, (int, float))
        assert score > 0
        
        # Score deve ser maior para mais tickets fechados e menor tempo médio
        tickets_data_better = {
            'abertos': 3,
            'fechados': 25,
            'tempo_medio': 1.5
        }
        
        better_score = glpi_service._calculate_technician_score(tickets_data_better)
        assert better_score > score
    
    @pytest.mark.integration
    def test_get_technician_ranking_with_cache(self, glpi_service, mock_redis):
        """Testa obtenção do ranking com cache."""
        # Configurar dados em cache
        cached_data = [
            {'id': '1', 'name': 'Técnico 1', 'score': 100},
            {'id': '2', 'name': 'Técnico 2', 'score': 90}
        ]
        mock_redis.get.return_value = json.dumps(cached_data).encode()
        
        # Executar método
        result = glpi_service.get_technician_ranking()
        
        # Verificar resultado
        assert result == cached_data
        mock_redis.get.assert_called_once()
    
    @pytest.mark.integration
    def test_get_technician_ranking_without_cache(self, glpi_service, mock_redis, mock_requests):
        """Testa obtenção do ranking sem cache."""
        # Configurar cache vazio
        mock_redis.get.return_value = None
        
        # Configurar autenticação
        auth_response = Mock()
        auth_response.status_code = 200
        auth_response.json.return_value = {'session_token': 'test_token'}
        
        # Configurar resposta dos usuários
        users_response = Mock()
        users_response.status_code = 200
        users_response.json.return_value = [
            {'id': '1', 'name': 'Técnico 1'},
            {'id': '2', 'name': 'Técnico 2'}
        ]
        
        # Configurar respostas dos tickets
        tickets_response = Mock()
        tickets_response.status_code = 200
        tickets_response.json.return_value = [
            {'id': '1', 'users_id_assign': '1', 'status': '5'},
            {'id': '2', 'users_id_assign': '1', 'status': '6'},
            {'id': '3', 'users_id_assign': '2', 'status': '5'}
        ]
        
        mock_requests.post.return_value = auth_response
        mock_requests.get.side_effect = [users_response, tickets_response]
        
        # Mock dos métodos internos
        with patch.object(glpi_service, '_is_dtic_technician', return_value=True), \
             patch.object(glpi_service, '_get_user_level', return_value='N1'), \
             patch.object(glpi_service, '_calculate_technician_score', return_value=85):
            
            result = glpi_service.get_technician_ranking()
        
        # Verificar que dados foram processados
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Verificar que dados foram salvos no cache
        mock_redis.set.assert_called()
    
    @pytest.mark.unit
    def test_get_dashboard_metrics_structure(self, glpi_service, sample_metrics_data):
        """Testa estrutura dos dados de métricas do dashboard."""
        with patch.object(glpi_service, '_fetch_dashboard_data') as mock_fetch:
            mock_fetch.return_value = sample_metrics_data
            
            result = glpi_service.get_dashboard_metrics()
            
            # Verificar estrutura
            assert 'novos' in result
            assert 'pendentes' in result
            assert 'progresso' in result
            assert 'resolvidos' in result
            assert 'total' in result
            assert 'niveis' in result
            assert 'tendencias' in result
            
            # Verificar tipos
            assert isinstance(result['novos'], int)
            assert isinstance(result['niveis'], dict)
            assert isinstance(result['tendencias'], dict)
    
    @pytest.mark.unit
    def test_get_system_status(self, glpi_service, mock_requests):
        """Testa obtenção do status do sistema."""
        # Configurar resposta de sucesso
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'version': '10.0.15'}
        mock_response.elapsed = timedelta(milliseconds=150)
        mock_requests.get.return_value = mock_response
        
        result = glpi_service.get_system_status()
        
        # Verificar estrutura da resposta
        assert 'status' in result
        assert 'api' in result
        assert 'glpi' in result
        assert 'glpi_response_time' in result
        assert 'version' in result
        assert 'last_update' in result
        
        # Verificar valores
        assert result['status'] == 'online'
        assert result['api'] == 'active'
        assert result['glpi'] == 'connected'
        assert result['version'] == '10.0.15'
    
    @pytest.mark.unit
    def test_get_system_status_offline(self, glpi_service, mock_requests):
        """Testa status do sistema quando offline."""
        # Configurar erro de conexão
        mock_requests.get.side_effect = Exception("Connection error")
        
        result = glpi_service.get_system_status()
        
        # Verificar resposta de erro
        assert result['status'] == 'offline'
        assert result['api'] == 'error'
        assert result['glpi'] == 'disconnected'
        assert 'error' in result['glpi_message']
    
    @pytest.mark.cache
    def test_cache_invalidation(self, glpi_service, mock_redis):
        """Testa invalidação do cache."""
        # Simular chaves no cache
        mock_redis.keys.return_value = [
            b'glpi:ranking:',
            b'glpi:metrics:',
            b'other:key:'
        ]
        
        # Executar invalidação
        glpi_service.invalidate_cache()
        
        # Verificar que apenas chaves GLPI foram deletadas
        assert mock_redis.delete.call_count == 2
        deleted_keys = [call[0][0] for call in mock_redis.delete.call_args_list]
        assert b'glpi:ranking:' in deleted_keys
        assert b'glpi:metrics:' in deleted_keys
        assert b'other:key:' not in deleted_keys
    
    @pytest.mark.slow
    def test_performance_with_large_dataset(self, glpi_service):
        """Testa performance com grande volume de dados."""
        # Simular grande dataset
        large_dataset = [
            {'id': str(i), 'name': f'Técnico {i}', 'score': 100 - i}
            for i in range(1000)
        ]
        
        with patch.object(glpi_service, '_fetch_technician_data') as mock_fetch:
            mock_fetch.return_value = large_dataset
            
            start_time = datetime.now()
            result = glpi_service.get_technician_ranking(limit=100)
            end_time = datetime.now()
            
            # Verificar que processamento foi rápido (< 1 segundo)
            processing_time = (end_time - start_time).total_seconds()
            assert processing_time < 1.0
            
            # Verificar que limite foi respeitado
            assert len(result) <= 100
    
    @pytest.mark.unit
    def test_error_handling_and_logging(self, glpi_service, mock_requests, caplog):
        """Testa tratamento de erros e logging."""
        # Configurar erro na requisição
        mock_requests.get.side_effect = Exception("Network error")
        
        # Executar método que deve tratar erro
        result = glpi_service.get_system_status()
        
        # Verificar que erro foi tratado graciosamente
        assert result['status'] == 'offline'
        
        # Verificar que erro foi logado
        assert "Network error" in caplog.text
        assert "ERROR" in caplog.text