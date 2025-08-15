# -*- coding: utf-8 -*-
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import requests
import logging

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.services.glpi_service import GLPIService
from app.core.config import active_config


class TestGLPIService:
    """Testes unitários para GLPIService"""
    
    @pytest.fixture
    def glpi_service(self):
        """Fixture que cria uma instância do GLPIService para testes"""
        return GLPIService(
            glpi_url="http://test.glpi.com/apirest.php",
            app_token="test_app_token",
            user_token="test_user_token",
            config={
                'GLPI_URL': 'http://test.glpi.com/apirest.php',
                'GLPI_APP_TOKEN': 'test_app_token',
                'GLPI_USER_TOKEN': 'test_user_token',
                'API_TIMEOUT': 30
            }
        )
    
    @pytest.fixture
    def mock_response(self):
        """Fixture que cria um mock de resposta HTTP"""
        mock = Mock()
        mock.status_code = 200
        mock.ok = True
        mock.json.return_value = {"session_token": "test_session_token"}
        return mock
    
    @pytest.fixture
    def mock_authenticated_service(self, glpi_service):
        """Fixture que cria um serviço já autenticado"""
        glpi_service.session_token = "test_session_token"
        glpi_service.token_expires_at = datetime.now() + timedelta(hours=1)
        return glpi_service


class TestGetTicketCount:
    """Testes para o método get_ticket_count"""
    
    @patch('app.services.glpi_service.requests')
    def test_get_ticket_count_success(self, mock_requests, mock_authenticated_service):
        """Testa contagem de tickets com sucesso"""
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.headers = {"Content-Range": "tickets 0-0/42"}
        mock_response.status_code = 200
        mock_response.ok = True
        mock_requests.get.return_value = mock_response
        
        # Mock do método _make_authenticated_request
        mock_authenticated_service._make_authenticated_request = Mock(return_value=mock_response)
        mock_authenticated_service.field_ids = {"GROUP": "8", "STATUS": "12"}
        
        result = mock_authenticated_service.get_ticket_count(89, 1)
        assert result == 42
    
    @patch('app.services.glpi_service.requests')
    def test_get_ticket_count_with_date_filter(self, mock_requests, mock_authenticated_service):
        """Testa contagem de tickets com filtro de data"""
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.headers = {"Content-Range": "tickets 0-0/15"}
        mock_response.status_code = 200
        mock_response.ok = True
        mock_requests.get.return_value = mock_response
        
        # Mock do método _make_authenticated_request
        mock_authenticated_service._make_authenticated_request = Mock(return_value=mock_response)
        mock_authenticated_service.field_ids = {"GROUP": "8", "STATUS": "12"}
        
        # Testa com filtro de data
        start_date = "2024-01-01"
        end_date = "2024-01-31"
        result = mock_authenticated_service.get_ticket_count(
            89, 1, start_date=start_date, end_date=end_date
        )
        
        assert result == 15
        
        # Verifica se o filtro de data foi aplicado na chamada
        call_args = mock_authenticated_service._make_authenticated_request.call_args
        assert "searchText[date]" in call_args[1]['params']
    
    def test_get_ticket_count_no_field_ids(self, mock_authenticated_service):
        """Testa comportamento quando field_ids náo está disponível"""
        mock_authenticated_service.field_ids = None
        
        with patch.object(mock_authenticated_service.logger, 'error') as mock_logger:
            result = mock_authenticated_service.get_ticket_count(89, 1)
            
            assert result == 0
            mock_logger.assert_called_with(
                "Field IDs náo disponíveis. Execute get_field_ids() primeiro."
            )
    
    def test_get_ticket_count_request_failure(self, mock_authenticated_service):
        """Testa falha na requisiçáo"""
        mock_authenticated_service._make_authenticated_request = Mock(return_value=None)
        mock_authenticated_service.field_ids = {"GROUP": "8", "STATUS": "12"}
        
        result = mock_authenticated_service.get_ticket_count(89, 1)
        assert result == 0
    
    def test_get_ticket_count_authentication_failure(self, mock_authenticated_service):
        """Testa falha de autenticaçáo"""
        mock_authenticated_service.field_ids = {"GROUP": "8", "STATUS": "12"}
        mock_authenticated_service._make_authenticated_request = Mock(side_effect=Exception("Auth failed"))
        
        result = mock_authenticated_service.get_ticket_count(89, 1)
        assert result == 0
    
    def test_get_ticket_count_invalid_json_response(self, mock_authenticated_service):
        """Testa resposta com JSON inválido"""
        mock_response = Mock()
        mock_response.headers = {}  # Sem Content-Range
        mock_response.status_code = 200
        mock_response.ok = True
        
        mock_authenticated_service._make_authenticated_request = Mock(return_value=mock_response)
        mock_authenticated_service.field_ids = {"GROUP": "8", "STATUS": "12"}
        
        with patch.object(mock_authenticated_service.logger, 'warning') as mock_logger:
            result = mock_authenticated_service.get_ticket_count(89, 1)
            
            assert result == 0
            mock_logger.assert_called_with(
                "Header Content-Range náo encontrado na resposta da API GLPI"
            )


class TestGetMetricsByLevelInternal:
    """Testes para o método _get_metrics_by_level_internal"""
    
    def test_get_metrics_by_level_internal_success(self, mock_authenticated_service):
        """Testa obtençáo de métricas por nível com sucesso"""
        # Mock do método get_ticket_count para retornar valores diferentes
        def mock_get_ticket_count(group_id, status_id, **kwargs):
            # Simula diferentes contagens baseadas nos parâmetros
            if group_id == 89:  # N1
                if status_id == 1:  # Novo
                    return 5
                elif status_id == 2:  # Em andamento
                    return 3
                elif status_id == 4:  # Pendente
                    return 2
                elif status_id == 5:  # Resolvido
                    return 10
                elif status_id == 6:  # Fechado
                    return 8
            elif group_id == 90:  # N2
                if status_id == 1:
                    return 3
                elif status_id == 2:
                    return 2
                elif status_id == 4:
                    return 1
                elif status_id == 5:
                    return 7
                elif status_id == 6:
                    return 5
            return 0
        
        mock_authenticated_service.get_ticket_count = Mock(side_effect=mock_get_ticket_count)
        
        result = mock_authenticated_service._get_metrics_by_level_internal()
        
        expected = {
            "N1": {
                "novos": 5,
                "em_andamento": 3,
                "pendentes": 2,
                "resolvidos": 10,
                "fechados": 8,
                "total": 28
            },
            "N2": {
                "novos": 3,
                "em_andamento": 2,
                "pendentes": 1,
                "resolvidos": 7,
                "fechados": 5,
                "total": 18
            }
        }
        
        assert result == expected
    
    def test_get_metrics_by_level_internal_with_date_filter(self, mock_authenticated_service):
        """Testa obtençáo de métricas com filtro de data"""
        mock_authenticated_service.get_ticket_count = Mock(return_value=5)
        
        start_date = "2024-01-01"
        end_date = "2024-01-31"
        
        result = mock_authenticated_service._get_metrics_by_level_internal(
            start_date=start_date, end_date=end_date
        )
        
        # Verifica se o filtro de data foi passado para get_ticket_count
        call_args_list = mock_authenticated_service.get_ticket_count.call_args_list
        for call_args in call_args_list:
            assert call_args[1]['start_date'] == start_date
            assert call_args[1]['end_date'] == end_date
    
    def test_get_metrics_by_level_internal_ticket_count_failure(self, mock_authenticated_service):
        """Testa comportamento quando get_ticket_count falha"""
        mock_authenticated_service.get_ticket_count = Mock(side_effect=Exception("API Error"))
        
        with patch.object(mock_authenticated_service.logger, 'error') as mock_logger:
            result = mock_authenticated_service._get_metrics_by_level_internal()
            
            # Deve retornar estrutura vazia em caso de erro
            expected = {
                "N1": {"novos": 0, "em_andamento": 0, "pendentes": 0, "resolvidos": 0, "fechados": 0, "total": 0},
                "N2": {"novos": 0, "em_andamento": 0, "pendentes": 0, "resolvidos": 0, "fechados": 0, "total": 0},
                "N3": {"novos": 0, "em_andamento": 0, "pendentes": 0, "resolvidos": 0, "fechados": 0, "total": 0},
                "N4": {"novos": 0, "em_andamento": 0, "pendentes": 0, "resolvidos": 0, "fechados": 0, "total": 0}
            }
            
            assert result == expected
            mock_logger.assert_called()
    
    def test_get_metrics_by_level_internal_partial_failure(self, mock_authenticated_service):
        """Testa comportamento com falha parcial"""
        def mock_get_ticket_count(group_id, status_id, **kwargs):
            if group_id == 89 and status_id == 1:  # N1 Novo
                raise Exception("Specific error")
            return 5
        
        mock_authenticated_service.get_ticket_count = Mock(side_effect=mock_get_ticket_count)
        
        with patch.object(mock_authenticated_service.logger, 'error') as mock_logger:
            result = mock_authenticated_service._get_metrics_by_level_internal()
            
            # N1 deve ter 'novos' = 0 devido ao erro, mas outros valores devem ser 5
            assert result["N1"]["novos"] == 0
            assert result["N1"]["em_andamento"] == 5
            mock_logger.assert_called()


class TestGetDashboardMetricsWithDateFilter:
    """Testes para o método get_dashboard_metrics_with_date_filter"""
    
    def test_get_dashboard_metrics_with_date_filter_success(self, mock_authenticated_service):
        """Testa obtençáo de métricas do dashboard com filtro de data"""
        # Mock dos métodos internos
        mock_metrics = {
            "N1": {"novos": 5, "em_andamento": 3, "pendentes": 2, "resolvidos": 10, "fechados": 8, "total": 28},
            "N2": {"novos": 3, "em_andamento": 2, "pendentes": 1, "resolvidos": 7, "fechados": 5, "total": 18}
        }
        
        mock_authenticated_service._get_metrics_by_level_internal = Mock(return_value=mock_metrics)
        mock_authenticated_service._calculate_trends = Mock(return_value={
            "novos": {"valor": 8, "percentual": 5.2},
            "pendentes": {"valor": 3, "percentual": -2.1}
        })
        
        start_date = "2024-01-01"
        end_date = "2024-01-31"
        
        result = mock_authenticated_service.get_dashboard_metrics_with_date_filter(
            start_date=start_date, end_date=end_date
        )
        
        assert "niveis" in result
        assert "total" in result
        assert "novos" in result
        assert "pendentes" in result
        assert "resolvidos" in result
        assert "tendencias" in result
        assert result["success"] is True
    
    def test_get_dashboard_metrics_with_date_filter_cache_hit(self, mock_authenticated_service):
        """Testa hit no cache"""
        # Simula dados no cache
        cached_data = {"niveis": {}, "total": 100, "success": True}
        mock_authenticated_service._get_cached_data = Mock(return_value=cached_data)
        
        start_date = "2024-01-01"
        end_date = "2024-01-31"
        
        result = mock_authenticated_service.get_dashboard_metrics_with_date_filter(
            start_date=start_date, end_date=end_date
        )
        
        assert result == cached_data
        # Verifica que os métodos internos náo foram chamados
        assert not hasattr(mock_authenticated_service, '_get_metrics_by_level_internal') or \
               not mock_authenticated_service._get_metrics_by_level_internal.called
    
    def test_get_dashboard_metrics_with_date_filter_authentication_failure(self, mock_authenticated_service):
        """Testa falha de autenticaçáo"""
        mock_authenticated_service._ensure_authenticated = Mock(return_value=False)
        
        result = mock_authenticated_service.get_dashboard_metrics_with_date_filter()
        
        assert result["success"] is False
        assert "error" in result
    
    def test_get_dashboard_metrics_with_date_filter_field_ids_failure(self, glpi_service):
        """Testa falha ao obter field_ids"""
        service = glpi_service
        service._ensure_authenticated = Mock(return_value=True)
        service._ensure_field_ids = Mock(return_value=False)
        
        with patch.object(service.logger, 'error') as mock_logger:
            result = service.get_dashboard_metrics_with_date_filter()
            
            assert result["success"] is False
            assert "error" in result
            mock_logger.assert_called()
    
    def test_get_dashboard_metrics_with_date_filter_exception(self, mock_authenticated_service):
        """Testa tratamento de exceçáo geral"""
        mock_authenticated_service._get_metrics_by_level_internal = Mock(side_effect=Exception("Test error"))
        
        result = mock_authenticated_service.get_dashboard_metrics_with_date_filter()
        
        assert result["success"] is False
        assert "error" in result
    
    def test_get_dashboard_metrics_with_date_filter_no_dates(self, mock_authenticated_service):
        """Testa comportamento sem filtro de data"""
        mock_metrics = {
            "N1": {"novos": 5, "em_andamento": 3, "pendentes": 2, "resolvidos": 10, "fechados": 8, "total": 28}
        }
        
        mock_authenticated_service._get_metrics_by_level_internal = Mock(return_value=mock_metrics)
        mock_authenticated_service._calculate_trends = Mock(return_value={
            "novos": {"valor": 5, "percentual": 0.0}
        })
        
        result = mock_authenticated_service.get_dashboard_metrics_with_date_filter()
        
        # Verifica que foi chamado sem parâmetros de data
        mock_authenticated_service._get_metrics_by_level_internal.assert_called_with()
        assert result["success"] is True
    
    def test_get_dashboard_metrics_with_date_filter_cache_storage(self, mock_authenticated_service):
        """Testa armazenamento no cache"""
        mock_metrics = {
            "N1": {"novos": 5, "em_andamento": 3, "pendentes": 2, "resolvidos": 10, "fechados": 8, "total": 28}
        }
        
        mock_authenticated_service._get_cached_data = Mock(return_value=None)  # Cache miss
        mock_authenticated_service._get_metrics_by_level_internal = Mock(return_value=mock_metrics)
        mock_authenticated_service._calculate_trends = Mock(return_value={})
        mock_authenticated_service._store_cached_data = Mock()
        
        start_date = "2024-01-01"
        end_date = "2024-01-31"
        
        result = mock_authenticated_service.get_dashboard_metrics_with_date_filter(
            start_date=start_date, end_date=end_date
        )
        
        # Verifica que os dados foram armazenados no cache
        mock_authenticated_service._store_cached_data.assert_called_once()
        assert result["success"] is True


class TestTokenManagement:
    """Testes para gerenciamento de tokens"""
    
    def test_token_expiration_check(self, glpi_service):
        """Testa verificaçáo de expiraçáo do token"""
        service = glpi_service
        
        # Token expirado
        service.token_expires_at = datetime.now() - timedelta(minutes=1)
        assert service._is_token_expired() is True
        
        # Token válido
        service.token_expires_at = datetime.now() + timedelta(hours=1)
        assert service._is_token_expired() is False
        
        # Token náo definido
        service.token_expires_at = None
        assert service._is_token_expired() is True
    
    def test_ensure_authenticated_with_expired_token(self, glpi_service):
        """Testa autenticaçáo com token expirado"""
        service = glpi_service
        service.session_token = "old_token"
        service.token_expires_at = datetime.now() - timedelta(minutes=1)
        
        with patch.object(service, '_authenticate_with_retry', return_value=True) as mock_auth:
            result = service._ensure_authenticated()
            
            assert result is True
            mock_auth.assert_called_once()
    
    def test_ensure_authenticated_with_valid_token(self, mock_authenticated_service):
        """Testa comportamento com token válido"""
        service = mock_authenticated_service
        
        with patch.object(service, '_authenticate_with_retry') as mock_auth:
            result = service._ensure_authenticated()
            
            assert result is True
            mock_auth.assert_not_called()  # Náo deve tentar autenticar novamente


class TestErrorHandling:
    """Testes para tratamento de erros"""
    
    def test_authentication_retry_mechanism(self, glpi_service):
        """Testa mecanismo de retry na autenticaçáo"""
        # Arrange
        service = glpi_service
        
        with patch.object(service, '_perform_authentication', side_effect=[False, False, True]):
            with patch('time.sleep') as mock_sleep:
                # Act
                result = service._authenticate_with_retry()
                
                # Assert
                assert result is True
                assert mock_sleep.call_count == 2  # Duas tentativas falharam
    
    def test_authentication_max_retries_exceeded(self, glpi_service):
        """Testa falha após esgotar tentativas de autenticaçáo"""
        # Arrange
        service = glpi_service
        
        with patch.object(service, '_perform_authentication', return_value=False):
            with patch('time.sleep'):
                with patch.object(service.logger, 'error') as mock_logger:
                    # Act
                    result = service._authenticate_with_retry()
                    
                    # Assert
                    assert result is False
                    mock_logger.assert_called()
    
    def test_missing_tokens_configuration(self, glpi_service):
        """Testa comportamento com tokens náo configurados"""
        # Arrange
        service = glpi_service
        service.app_token = None
        service.user_token = None
        
        with patch.object(service.logger, 'error') as mock_logger:
            # Act
            result = service._perform_authentication()
            
            # Assert
            assert result is False
            mock_logger.assert_called_with(
                "Tokens de autenticaçáo do GLPI (GLPI_APP_TOKEN, GLPI_USER_TOKEN) náo estáo configurados."
            )
    
    def test_network_timeout_handling(self, glpi_service):
        """Testa tratamento de timeout de rede"""
        # Arrange
        service = glpi_service
        
        with patch('app.services.glpi_service.requests.post', side_effect=requests.Timeout("Timeout")):
            with patch.object(service.logger, 'error') as mock_logger:
                # Act
                result = service._perform_authentication()
                
                # Assert
                assert result is False
                mock_logger.assert_called()
    
    def test_connection_error_handling(self, glpi_service):
        """Testa tratamento de erro de conexáo"""
        # Arrange
        service = glpi_service
        
        with patch('app.services.glpi_service.requests.post', side_effect=requests.ConnectionError("Connection failed")):
            with patch.object(service.logger, 'error') as mock_logger:
                # Act
                result = service._perform_authentication()
                
                # Assert
                assert result is False
                mock_logger.assert_called()


class TestCacheManagement:
    """Testes para gerenciamento de cache"""
    
    def test_cache_validity_check(self, glpi_service):
        """Testa verificaçáo de validade do cache"""
        service = glpi_service
        
        # Cache válido
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "data": {"test": "value"}
        }
        
        with patch.object(service, '_get_cache_data', return_value=cache_data):
            result = service._get_cached_data("test_key")
            assert result == {"test": "value"}
        
        # Cache expirado
        old_cache_data = {
            "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
            "data": {"test": "value"}
        }
        
        with patch.object(service, '_get_cache_data', return_value=old_cache_data):
            result = service._get_cached_data("test_key", max_age_minutes=30)
            assert result is None
    
    def test_cache_data_operations(self, glpi_service):
        """Testa operações de dados do cache"""
        service = glpi_service
        test_data = {"metrics": {"N1": {"total": 100}}}
        
        # Mock das operações de cache
        with patch.object(service, '_set_cache_data') as mock_set:
            with patch.object(service, '_get_cache_data', return_value=None) as mock_get:
                # Testa armazenamento
                service._store_cached_data("test_key", test_data)
                mock_set.assert_called_once()
                
                # Testa recuperaçáo (cache miss)
                result = service._get_cached_data("test_key")
                assert result is None
                mock_get.assert_called_once()
    
    def test_cache_sub_key_operations(self, glpi_service):
        """Testa operações com sub-chaves do cache"""
        service = glpi_service
        
        # Testa geraçáo de chave com filtros de data
        key1 = service._generate_cache_key("metrics", start_date="2024-01-01", end_date="2024-01-31")
        key2 = service._generate_cache_key("metrics", start_date="2024-02-01", end_date="2024-02-28")
        
        assert key1 != key2
        assert "2024-01-01" in key1
        assert "2024-01-31" in key1
        
        # Testa chave sem filtros
        key3 = service._generate_cache_key("metrics")
        assert key3 != key1
        assert "metrics" in key3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
