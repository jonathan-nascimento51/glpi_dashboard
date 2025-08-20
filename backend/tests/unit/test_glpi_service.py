# -*- coding: utf-8 -*-
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from config.settings import active_config
from services.glpi_service import GLPIService


class TestGLPIService:
    """Testes unitários para GLPIService"""

    @pytest.fixture
    def glpi_service(self):
        """Fixture que cria uma instância do GLPIService para testes"""
        with patch("services.glpi_service.active_config") as mock_config:
            mock_config.GLPI_URL = "https://test-glpi.com/apirest.php"
            mock_config.GLPI_APP_TOKEN = "test_app_token"
            mock_config.GLPI_USER_TOKEN = "test_user_token"
            service = GLPIService()
            service.field_ids = {"STATUS": "12", "GROUP": "8", "TECHNICIAN": "5"}
            return service

    @pytest.fixture
    def mock_response(self):
        """Fixture que cria um mock de resposta HTTP"""
        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = {"session_token": "test_session_token"}
        return response

    @pytest.fixture
    def mock_authenticated_service(self, glpi_service):
        """Fixture que cria um serviço já autenticado"""
        glpi_service.session_token = "test_session_token"
        glpi_service.token_created_at = time.time()
        return glpi_service


class TestGetTicketCount:
    """Testes para o método get_ticket_count"""

    @patch("services.glpi_service.requests")
    def test_get_ticket_count_success(self, mock_requests, mock_authenticated_service):
        """Testa contagem de tickets com sucesso"""
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.headers = {"Content-Range": "tickets 0-0/42"}
        mock_response.status_code = 200
        mock_response.ok = True
        mock_requests.get.return_value = mock_response

        # Mock dos métodos necessários
        mock_authenticated_service._make_authenticated_request = Mock(return_value=mock_response)
        mock_authenticated_service._ensure_authenticated = Mock(return_value=True)
        mock_authenticated_service.field_ids = {"GROUP": "8", "STATUS": "12"}

        result = mock_authenticated_service.get_ticket_count(89, 1)
        assert result == 42

    @patch("services.glpi_service.requests")
    def test_get_ticket_count_with_date_filter(self, mock_requests, mock_authenticated_service):
        """Testa contagem de tickets com filtro de data"""
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.headers = {"Content-Range": "tickets 0-0/15"}
        mock_response.status_code = 200
        mock_response.ok = True
        mock_requests.get.return_value = mock_response

        # Mock dos métodos necessários
        mock_authenticated_service._make_authenticated_request = Mock(return_value=mock_response)
        mock_authenticated_service._ensure_authenticated = Mock(return_value=True)
        mock_authenticated_service.field_ids = {"GROUP": "8", "STATUS": "12"}

        result = mock_authenticated_service.get_ticket_count(
            group_id=89, status_id=1, start_date="2024-01-01", end_date="2024-01-31"
        )

        assert result == 15

    def test_get_ticket_count_no_field_ids(self, mock_authenticated_service):
        """Testa quando não consegue descobrir field IDs"""
        # Simula field_ids vazios e falha na descoberta
        mock_authenticated_service.field_ids = {}
        mock_authenticated_service.discover_field_ids = Mock(return_value=False)
        mock_authenticated_service._ensure_authenticated = Mock(return_value=True)

        result = mock_authenticated_service.get_ticket_count(group_id=89, status_id=1)

        assert result == 0  # Agora retorna 0 em vez de None para fallback gracioso
        mock_authenticated_service.discover_field_ids.assert_called_once()

    def test_get_ticket_count_request_failure(self, mock_authenticated_service):
        """Testa falha na requisição"""
        # Mock falha na requisição
        mock_authenticated_service._make_authenticated_request = Mock(return_value=None)
        mock_authenticated_service._ensure_authenticated = Mock(return_value=True)
        mock_authenticated_service.field_ids = {"GROUP": "8", "STATUS": "12"}

        result = mock_authenticated_service.get_ticket_count(group_id=89, status_id=1)

        assert result == 0  # Agora retorna 0 em vez de None para fallback gracioso

    def test_get_ticket_count_authentication_failure(self, mock_authenticated_service):
        """Testa falha de autenticação"""
        # Mock falha de autenticação
        mock_authenticated_service._make_authenticated_request = Mock(side_effect=Exception("Authentication failed"))
        mock_authenticated_service._ensure_authenticated = Mock(return_value=True)
        mock_authenticated_service.field_ids = {"GROUP": "8", "STATUS": "12"}

        result = mock_authenticated_service.get_ticket_count(group_id=89, status_id=1)

        assert result == 0  # Agora retorna 0 em vez de None para fallback gracioso

    def test_get_ticket_count_invalid_json_response(self, mock_authenticated_service):
        """Testa resposta sem Content-Range header"""
        # Mock resposta sem Content-Range header
        mock_response = Mock()
        mock_response.headers = {}  # Sem Content-Range
        mock_response.status_code = 200
        mock_response.ok = True

        mock_authenticated_service._make_authenticated_request = Mock(return_value=mock_response)
        mock_authenticated_service._ensure_authenticated = Mock(return_value=True)
        mock_authenticated_service.field_ids = {"GROUP": "8", "STATUS": "12"}

        result = mock_authenticated_service.get_ticket_count(group_id=89, status_id=1)

        assert result == 0  # Retorna 0 quando não há Content-Range mas status é 200


class TestGetMetricsByLevelInternal:
    """Testes para o método _get_metrics_by_level_internal"""

    def test_get_metrics_by_level_internal_success(self, mock_authenticated_service):
        """Testa obtenção de métricas por nível com sucesso"""
        # Arrange
        service = mock_authenticated_service
        service._ensure_authenticated = Mock(return_value=True)
        
        # Mock dos atributos necessários para evitar validações que retornam 0
        service.glpi_url = "http://test-glpi.com"
        service.field_ids = {"GROUP": "8", "STATUS": "12"}
        service.discover_field_ids = Mock(return_value=True)

        # Mock dos atributos necessários
        service.service_levels = {"N1": 89, "N2": 90, "N3": 91, "N4": 92}
        service.status_map = {
            "Novo": 1,
            "Processando (atribuído)": 2,
            "Processando (planejado)": 3,
            "Pendente": 4,
            "Solucionado": 5,
            "Fechado": 6,
        }

        # Mock do get_ticket_count para retornar valores diferentes para cada combinação
        def mock_get_ticket_count(group_id, status_id, start_date=None, end_date=None, correlation_id=None):
            # Simula contagens diferentes baseadas no grupo e status
            counts = {
                (89, 1): 10,  # N1, Novo
                (89, 2): 5,  # N1, Processando (atribuído)
                (89, 3): 3,  # N1, Processando (planejado)
                (89, 4): 2,  # N1, Pendente
                (89, 5): 8,  # N1, Solucionado
                (89, 6): 12,  # N1, Fechado
                (90, 1): 15,  # N2, Novo
                (90, 2): 7,  # N2, Processando (atribuído)
                (90, 3): 4,  # N2, Processando (planejado)
                (90, 4): 3,  # N2, Pendente
                (90, 5): 6,  # N2, Solucionado
                (90, 6): 9,  # N2, Fechado
                (91, 1): 8,  # N3, Novo
                (91, 2): 4,  # N3, Processando (atribuído)
                (91, 3): 2,  # N3, Processando (planejado)
                (91, 4): 1,  # N3, Pendente
                (91, 5): 5,  # N3, Solucionado
                (91, 6): 7,  # N3, Fechado
                (92, 1): 12,  # N4, Novo
                (92, 2): 6,  # N4, Processando (atribuído)
                (92, 3): 3,  # N4, Processando (planejado)
                (92, 4): 2,  # N4, Pendente
                (92, 5): 4,  # N4, Solucionado
                (92, 6): 8,  # N4, Fechado
            }
            return counts.get((group_id, status_id), 0)

        with patch.object(service, "get_ticket_count", side_effect=mock_get_ticket_count):
            # Act
            result = service._get_metrics_by_level_internal()

            # Assert
            assert isinstance(result, dict)
            assert "N1" in result
            assert "N2" in result
            assert "N3" in result
            assert "N4" in result

            # Verifica estrutura dos dados para N1
            n1_metrics = result["N1"]
            assert n1_metrics["Novo"] == 10
            assert n1_metrics["Processando (atribuído)"] == 5
            assert n1_metrics["Processando (planejado)"] == 3
            assert n1_metrics["Pendente"] == 2
            assert n1_metrics["Solucionado"] == 8
            assert n1_metrics["Fechado"] == 12

    def test_get_metrics_by_level_internal_with_date_filter(self, mock_authenticated_service):
        """Testa obtenção de métricas por nível com filtro de data"""
        # Arrange
        service = mock_authenticated_service
        service._ensure_authenticated = Mock(return_value=True)

        # Mock dos atributos necessários
        service.service_levels = {"N1": 89, "N2": 90, "N3": 91, "N4": 92}
        service.status_map = {
            "Novo": 1,
            "Processando (atribuído)": 2,
            "Processando (planejado)": 3,
            "Pendente": 4,
            "Solucionado": 5,
            "Fechado": 6,
        }

        start_date = "2024-01-01"
        end_date = "2024-01-31"

        with patch.object(service, "get_ticket_count", return_value=5) as mock_get_count:
            # Act
            result = service._get_metrics_by_level_internal(start_date, end_date)

            # Assert
            assert isinstance(result, dict)
            # Verifica se get_ticket_count foi chamado com os parâmetros de data
            mock_get_count.assert_called()
            # Verifica se foi chamado com argumentos posicionais corretos
            call_args = mock_get_count.call_args_list[0]
            assert len(call_args[0]) >= 4  # group_id, status_id, start_date, end_date
            assert call_args[0][2] == start_date  # terceiro argumento é start_date
            assert call_args[0][3] == end_date  # quarto argumento é end_date

    def test_get_metrics_by_level_internal_ticket_count_failure(self, mock_authenticated_service):
        """Testa comportamento quando get_ticket_count falha"""
        # Arrange
        service = mock_authenticated_service
        service._ensure_authenticated = Mock(return_value=True)

        # Mock dos atributos necessários
        service.service_levels = {"N1": 89, "N2": 90, "N3": 91, "N4": 92}
        service.status_map = {
            "Novo": 1,
            "Processando (atribuído)": 2,
            "Processando (planejado)": 3,
            "Pendente": 4,
            "Solucionado": 5,
            "Fechado": 6,
        }

        with patch.object(service, "get_ticket_count", return_value=None):
            # Act
            result = service._get_metrics_by_level_internal()

            # Assert
            assert isinstance(result, dict)
            # Verifica se os valores são 0 quando get_ticket_count retorna None
            for level in ["N1", "N2", "N3", "N4"]:
                for status in service.status_map.keys():
                    assert result[level][status] == 0

    def test_get_metrics_by_level_internal_partial_failure(self, mock_authenticated_service):
        """Testa comportamento com falhas parciais"""
        # Arrange
        service = mock_authenticated_service
        service._ensure_authenticated = Mock(return_value=True)

        # Mock dos atributos necessários
        service.service_levels = {"N1": 89, "N2": 90, "N3": 91, "N4": 92}
        service.status_map = {
            "Novo": 1,
            "Processando (atribuído)": 2,
            "Processando (planejado)": 3,
            "Pendente": 4,
            "Solucionado": 5,
            "Fechado": 6,
        }

        def mock_get_ticket_count(group_id, status_id, start_date=None, end_date=None, correlation_id=None):
            # Simula falha apenas para N2
            if group_id == 90:  # N2
                return None
            return 5

        with patch.object(service, "get_ticket_count", side_effect=mock_get_ticket_count):
            # Act
            result = service._get_metrics_by_level_internal()

            # Assert
            assert isinstance(result, dict)
            # N1, N3, N4 devem ter valores 5
            assert all(result["N1"][status] == 5 for status in service.status_map.keys())
            assert all(result["N3"][status] == 5 for status in service.status_map.keys())
            assert all(result["N4"][status] == 5 for status in service.status_map.keys())
            # N2 deve ter valores 0 (falha)
            assert all(result["N2"][status] == 0 for status in service.status_map.keys())


class TestGetDashboardMetricsWithDateFilter:
    """Testes para o método get_dashboard_metrics_with_date_filter"""

    def test_get_dashboard_metrics_with_date_filter_success(self, mock_authenticated_service):
        """Testa obtenção de métricas do dashboard com filtro de data - sucesso"""
        # Arrange
        service = mock_authenticated_service
        start_date = "2024-01-01"
        end_date = "2024-01-31"

        # Mock das métricas por nível
        mock_level_metrics = {
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
            "N3": {
                "Novo": 8,
                "Processando (atribuído)": 4,
                "Processando (planejado)": 2,
                "Pendente": 1,
                "Solucionado": 5,
                "Fechado": 7,
            },
            "N4": {
                "Novo": 12,
                "Processando (atribuído)": 6,
                "Processando (planejado)": 3,
                "Pendente": 2,
                "Solucionado": 4,
                "Fechado": 8,
            },
        }

        # Mock das métricas gerais
        mock_general_metrics = {
            "Novo": 50,
            "Processando (atribuído)": 25,
            "Processando (planejado)": 15,
            "Pendente": 10,
            "Solucionado": 30,
            "Fechado": 40,
        }

        with patch.object(service, "_get_metrics_by_level_internal", return_value=mock_level_metrics):
            with patch.object(
                service,
                "_get_general_metrics_internal",
                return_value=mock_general_metrics,
            ):
                with patch.object(service, "_ensure_authenticated", return_value=True):
                    with patch.object(service, "discover_field_ids", return_value=True):
                        # Act
                        result = service.get_dashboard_metrics_with_date_filter(start_date, end_date)

                        # Assert
                        assert isinstance(result, dict)
                        assert result["success"] is True
                        assert "data" in result
                        assert "niveis" in result["data"]
                        assert "filters_applied" in result["data"]
                        assert result["data"]["filters_applied"]["data_inicio"] == start_date
                        assert result["data"]["filters_applied"]["data_fim"] == end_date

                        # Verifica estrutura dos níveis
                        niveis = result["data"]["niveis"]
                        assert "geral" in niveis
                        assert "n1" in niveis
                        assert "n2" in niveis
                        assert "n3" in niveis
                        assert "n4" in niveis

    def test_get_dashboard_metrics_with_date_filter_cache_hit(self, mock_authenticated_service):
        """Testa uso do cache quando dados estão disponíveis"""
        # Arrange
        service = mock_authenticated_service
        start_date = "2024-01-01"
        end_date = "2024-01-31"
        cache_key = f"{start_date}_{end_date}"

        cached_data = {"success": True, "data": {"cached": True}}

        with patch.object(service, "_is_cache_valid", return_value=True):
            with patch.object(service, "_get_cache_data", return_value=cached_data):
                # Act
                result = service.get_dashboard_metrics_with_date_filter(start_date, end_date)

                # Assert
                assert result == cached_data

    def test_get_dashboard_metrics_with_date_filter_authentication_failure(self, mock_authenticated_service):
        """Testa falha de autenticação"""
        # Mock falha de autenticação
        mock_authenticated_service._ensure_authenticated = Mock(return_value=False)

        result = mock_authenticated_service.get_dashboard_metrics_with_date_filter("2024-01-01", "2024-01-31")

        assert result is None
        mock_authenticated_service._ensure_authenticated.assert_called_once()

    def test_get_dashboard_metrics_with_date_filter_field_ids_failure(self, glpi_service):
        """Testa falha ao descobrir field IDs"""
        # Usar glpi_service sem field_ids configurados
        service = glpi_service
        service.field_ids = {}

        with patch.object(service, "_ensure_authenticated", return_value=True):
            with patch.object(service, "discover_field_ids", return_value=False) as mock_discover:
                result = service.get_dashboard_metrics_with_date_filter("2024-01-01", "2024-01-31")

                assert result is None
                mock_discover.assert_called_once()

    def test_get_dashboard_metrics_with_date_filter_exception(self, mock_authenticated_service):
        """Testa tratamento de exceções"""
        # Mock para simular exceção durante processamento
        mock_authenticated_service._get_general_metrics_internal = Mock(side_effect=Exception("Test error"))

        result = mock_authenticated_service.get_dashboard_metrics_with_date_filter("2024-01-01", "2024-01-31")

        # O método deve retornar None em caso de exceção
        assert result is None

    def test_get_dashboard_metrics_with_date_filter_no_dates(self, mock_authenticated_service):
        """Testa comportamento sem filtros de data"""
        # Arrange
        service = mock_authenticated_service

        mock_level_metrics = {
            "N1": {
                "Novo": 5,
                "Processando (atribuído)": 3,
                "Processando (planejado)": 2,
                "Pendente": 1,
                "Solucionado": 4,
                "Fechado": 6,
            }
        }

        mock_general_metrics = {
            "Novo": 10,
            "Processando (atribuído)": 8,
            "Processando (planejado)": 5,
            "Pendente": 3,
            "Solucionado": 12,
            "Fechado": 15,
        }

        with patch.object(service, "_get_metrics_by_level_internal", return_value=mock_level_metrics):
            with patch.object(
                service,
                "_get_general_metrics_internal",
                return_value=mock_general_metrics,
            ):
                with patch.object(service, "_ensure_authenticated", return_value=True):
                    with patch.object(service, "discover_field_ids", return_value=True):
                        # Act
                        result = service.get_dashboard_metrics_with_date_filter()

                        # Assert
                        assert isinstance(result, dict)
                        assert result["success"] is True

    def test_get_dashboard_metrics_with_date_filter_cache_storage(self, mock_authenticated_service):
        """Testa armazenamento no cache"""
        # Arrange
        service = mock_authenticated_service
        start_date = "2024-01-01"
        end_date = "2024-01-31"

        mock_level_metrics = {"N1": {"Novo": 5}}
        mock_general_metrics = {"Novo": 10}

        with patch.object(service, "_is_cache_valid", return_value=False):
            with patch.object(
                service,
                "_get_metrics_by_level_internal",
                return_value=mock_level_metrics,
            ):
                with patch.object(
                    service,
                    "_get_general_metrics_internal",
                    return_value=mock_general_metrics,
                ):
                    with patch.object(service, "_ensure_authenticated", return_value=True):
                        with patch.object(service, "discover_field_ids", return_value=True):
                            with patch.object(service, "_set_cache_data") as mock_set_cache:
                                # Act
                                result = service.get_dashboard_metrics_with_date_filter(start_date, end_date)

                                # Assert
                                assert result["success"] is True
                                mock_set_cache.assert_called_once()


class TestTokenManagement:
    """Testes para gerenciamento de tokens e autenticação"""

    def test_token_expiration_check(self, glpi_service):
        """Testa verificação de expiração de token"""
        # Arrange
        service = glpi_service

        # Token expirado
        service.token_created_at = time.time() - 3700  # 1 hora e 2 minutos atrás
        assert service._is_token_expired() is True

        # Token válido
        service.token_created_at = time.time() - 1800  # 30 minutos atrás
        assert service._is_token_expired() is False

        # Sem token
        service.token_created_at = None
        assert service._is_token_expired() is True

    def test_ensure_authenticated_with_expired_token(self, glpi_service):
        """Testa re-autenticação quando token está expirado"""
        # Arrange
        service = glpi_service
        service.session_token = "old_token"
        service.token_created_at = time.time() - 3700  # Token expirado

        with patch.object(service, "_authenticate_with_retry", return_value=True) as mock_auth:
            # Act
            result = service._ensure_authenticated()

            # Assert
            assert result is True
            mock_auth.assert_called_once()

    def test_ensure_authenticated_with_valid_token(self, mock_authenticated_service):
        """Testa que não re-autentica quando token é válido"""
        # Simula token válido (não expirado)
        mock_authenticated_service.token_created_at = time.time() - 1800  # 30 minutos atrás
        mock_authenticated_service._authenticate_with_retry = Mock(return_value=True)

        result = mock_authenticated_service._ensure_authenticated()

        # Com token válido, deve retornar True sem chamar autenticação
        assert result is True
        mock_authenticated_service._authenticate_with_retry.assert_not_called()


class TestErrorHandling:
    """Testes para tratamento de erros"""

    def test_authentication_retry_mechanism(self, glpi_service):
        """Testa mecanismo de retry na autenticação"""
        # Arrange
        service = glpi_service

        with patch.object(service, "_perform_authentication", side_effect=[False, False, True]):
            with patch("time.sleep") as mock_sleep:
                # Act
                result = service._authenticate_with_retry()

                # Assert
                assert result is True
                assert mock_sleep.call_count == 2  # Duas tentativas falharam

    def test_authentication_max_retries_exceeded(self, glpi_service):
        """Testa falha após esgotar tentativas de autenticação"""
        # Arrange
        service = glpi_service

        with patch.object(service, "_perform_authentication", return_value=False):
            with patch("time.sleep"):
                with patch.object(service.logger, "error") as mock_logger:
                    # Act
                    result = service._authenticate_with_retry()

                    # Assert
                    assert result is False
                    mock_logger.assert_called()

    def test_missing_tokens_configuration(self, glpi_service):
        """Testa comportamento com tokens não configurados"""
        # Arrange
        service = glpi_service
        service.app_token = None
        service.user_token = None

        with patch.object(service.logger, "error") as mock_logger:
            # Act
            result = service._perform_authentication()

            # Assert
            assert result is False
            mock_logger.assert_called_with("GLPI_APP_TOKEN não está configurado ou é inválido")

    def test_network_timeout_handling(self, glpi_service):
        """Testa tratamento de timeout de rede"""
        # Arrange
        service = glpi_service

        with patch("requests.get", side_effect=requests.exceptions.Timeout("Request timeout")):
            with patch.object(service.logger, "error") as mock_logger:
                # Act
                result = service._perform_authentication()

                # Assert
                assert result is False
                mock_logger.assert_called()

    def test_connection_error_handling(self, glpi_service):
        """Testa tratamento de erro de conexão"""
        # Arrange
        service = glpi_service

        with patch(
            "requests.get",
            side_effect=requests.exceptions.ConnectionError("Connection failed"),
        ):
            with patch.object(service.logger, "error") as mock_logger:
                # Act
                result = service._perform_authentication()

                # Assert
                assert result is False
                mock_logger.assert_called()


class TestCacheManagement:
    """Testes para sistema de cache"""

    def test_cache_validity_check(self, glpi_service):
        """Testa verificação de validade do cache"""
        # Arrange
        service = glpi_service

        # Cache válido
        service._cache["test_key"] = {
            "data": {"test": "data"},
            "timestamp": time.time(),
            "ttl": 300,
        }
        assert service._is_cache_valid("test_key") is True

        # Cache expirado
        service._cache["expired_key"] = {
            "data": {"test": "data"},
            "timestamp": time.time() - 400,  # Mais antigo que TTL
            "ttl": 300,
        }
        assert service._is_cache_valid("expired_key") is False

        # Cache inexistente
        assert service._is_cache_valid("nonexistent_key") is False

    def test_cache_data_operations(self, glpi_service):
        """Testa operações de dados do cache"""
        # Arrange
        service = glpi_service
        test_data = {"test": "value"}

        # Set cache
        service._set_cache_data("test_key", test_data, ttl=600)

        # Get cache
        retrieved_data = service._get_cache_data("test_key")
        assert retrieved_data == test_data

        # Verify cache structure
        cache_entry = service._cache["test_key"]
        assert cache_entry["data"] == test_data
        assert cache_entry["ttl"] == 600
        assert isinstance(cache_entry["timestamp"], float)

    def test_cache_sub_key_operations(self, glpi_service):
        """Testa operações de cache com sub-chaves"""
        # Arrange
        service = glpi_service
        test_data = {"nested": "value"}

        # Set cache with sub-key
        service._set_cache_data("main_key", test_data, ttl=300, sub_key="sub_key")

        # Get cache with sub-key
        retrieved_data = service._get_cache_data("main_key", "sub_key")
        assert retrieved_data == test_data

        # Check validity with sub-key
        assert service._is_cache_valid("main_key", "sub_key") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
