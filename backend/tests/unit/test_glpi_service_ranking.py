import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from backend.services.glpi_service import GLPIService
from backend.config.settings import Config


class TestGLPIServiceRanking:
    """Testes para funcionalidades de ranking de técnicos do GLPIService"""

    @pytest.fixture
    def glpi_service(self):
        """Fixture para criar instância do GLPIService"""
        with patch('backend.services.glpi_service.GLPIService._authenticate_with_retry'):
            service = GLPIService()
            service.session_token = 'mock_token'
            return service

    @pytest.fixture
    def mock_technicians_response(self):
        """Mock da resposta da API do GLPI para busca de técnicos"""
        return {
            'data': [
                {
                    'id': '1',
                    'users_id': '10',
                    'User': {
                        'id': '10',
                        'name': 'João Silva',
                        'realname': 'João',
                        'firstname': 'Silva'
                    }
                },
                {
                    'id': '2',
                    'users_id': '20',
                    'User': {
                        'id': '20',
                        'name': 'Maria Santos',
                        'realname': 'Maria',
                        'firstname': 'Santos'
                    }
                },
                {
                    'id': '3',
                    'users_id': '30',
                    'User': {
                        'id': '30',
                        'name': 'Pedro Costa',
                        'realname': 'Pedro',
                        'firstname': 'Costa'
                    }
                }
            ]
        }

    @pytest.fixture
    def mock_tickets_response(self):
        """Mock da resposta da API do GLPI para contagem de tickets"""
        return {
            'data': [
                {'id': '1', 'users_id_recipient': '10'},
                {'id': '2', 'users_id_recipient': '10'},
                {'id': '3', 'users_id_recipient': '20'},
                {'id': '4', 'users_id_recipient': '30'},
                {'id': '5', 'users_id_recipient': '30'},
                {'id': '6', 'users_id_recipient': '30'}
            ]
        }

    @patch('backend.services.glpi_service.GLPIService._authenticate_with_retry')
    @patch('backend.services.glpi_service.requests.get')
    def test_get_technician_ranking_with_filters_success(self, mock_get, mock_auth, glpi_service, mock_technicians_response, mock_tickets_response):
        """Testa o ranking de técnicos com filtros aplicados com sucesso"""
        # Mock da autenticação
        mock_auth.return_value = True
        
        # Mock das respostas da API
        mock_get.side_effect = [
            Mock(status_code=200, json=lambda: mock_technicians_response),  # Busca de técnicos
            Mock(status_code=200, json=lambda: mock_tickets_response),      # Tickets do João
            Mock(status_code=200, json=lambda: {'data': [mock_tickets_response['data'][2]]}),  # Tickets da Maria
            Mock(status_code=200, json=lambda: {'data': mock_tickets_response['data'][3:6]})   # Tickets do Pedro
        ]

        # Mock do token de sessão
        glpi_service.session_token = 'mock_token'

        # Executa o método
        result = glpi_service.get_technician_ranking_with_filters(
            start_date='2025-01-01',
            end_date='2025-12-31',
            level=None,
            limit=10
        )

        # Verificações
        assert result is not None
        assert len(result) == 3
        
        # Verifica ordenação por número de tickets (decrescente)
        assert result[0]['name'] == 'Pedro Costa'
        assert result[0]['tickets_count'] == 3
        assert result[0]['rank'] == 1
        
        assert result[1]['name'] == 'João Silva'
        assert result[1]['tickets_count'] == 2
        assert result[1]['rank'] == 2
        
        assert result[2]['name'] == 'Maria Santos'
        assert result[2]['tickets_count'] == 1
        assert result[2]['rank'] == 3

    @patch('backend.services.glpi_service.GLPIService._authenticate_with_retry')
    @patch('backend.services.glpi_service.requests.get')
    def test_get_technician_ranking_with_filters_no_technicians(self, mock_get, mock_auth, glpi_service):
        """Testa o ranking quando não há técnicos encontrados"""
        # Mock da autenticação
        mock_auth.return_value = True
        
        # Mock de resposta vazia
        mock_get.return_value = Mock(status_code=200, json=lambda: {'data': []})
        glpi_service.session_token = 'mock_token'

        result = glpi_service.get_technician_ranking_with_filters(
            start_date='2025-01-01',
            end_date='2025-12-31'
        )

        assert result == []

    @patch('backend.services.glpi_service.GLPIService._authenticate_with_retry')
    @patch('backend.services.glpi_service.requests.get')
    def test_get_technician_ranking_with_filters_api_error(self, mock_get, mock_auth, glpi_service):
        """Testa o ranking quando há erro na API"""
        # Mock da autenticação
        mock_auth.return_value = True
        
        # Mock de erro na API
        mock_get.return_value = Mock(status_code=500)
        glpi_service.session_token = 'mock_token'

        result = glpi_service.get_technician_ranking_with_filters(
            start_date='2025-01-01',
            end_date='2025-12-31'
        )

        assert result == []

    @patch('backend.services.glpi_service.GLPIService._authenticate_with_retry')
    @patch('backend.services.glpi_service.requests.get')
    def test_get_technician_ranking_with_filters_with_level_filter(self, mock_get, mock_auth, glpi_service, mock_technicians_response, mock_tickets_response):
        """Testa o ranking com filtro de nível aplicado"""
        # Mock da autenticação
        mock_auth.return_value = True
        
        # Mock das respostas da API
        mock_get.side_effect = [
            Mock(status_code=200, json=lambda: mock_technicians_response),
            Mock(status_code=200, json=lambda: mock_tickets_response),
            Mock(status_code=200, json=lambda: {'data': [mock_tickets_response['data'][2]]}),
            Mock(status_code=200, json=lambda: {'data': mock_tickets_response['data'][3:6]})
        ]

        glpi_service.session_token = 'mock_token'

        result = glpi_service.get_technician_ranking_with_filters(
            start_date='2025-01-01',
            end_date='2025-12-31',
            level='Sênior',
            limit=5
        )

        # Verifica se o resultado foi obtido
        assert isinstance(result, list)
        # O filtro de nível é aplicado no frontend, então aqui retorna todos
        assert len(result) <= 5  # Respeitando o limite

    @patch('backend.services.glpi_service.GLPIService._authenticate_with_retry')
    @patch('backend.services.glpi_service.requests.get')
    def test_get_technician_ranking_with_filters_with_limit(self, mock_get, mock_auth, glpi_service, mock_technicians_response, mock_tickets_response):
        """Testa o ranking com limite aplicado"""
        # Mock da autenticação
        mock_auth.return_value = True
        
        # Mock das respostas da API
        mock_get.side_effect = [
            Mock(status_code=200, json=lambda: mock_technicians_response),
            Mock(status_code=200, json=lambda: mock_tickets_response),
            Mock(status_code=200, json=lambda: {'data': [mock_tickets_response['data'][2]]}),
            Mock(status_code=200, json=lambda: {'data': mock_tickets_response['data'][3:6]})
        ]

        glpi_service.session_token = 'mock_token'

        result = glpi_service.get_technician_ranking_with_filters(
            start_date='2025-01-01',
            end_date='2025-12-31',
            limit=2
        )

        # Verifica se o limite foi respeitado
        assert len(result) <= 2

    def test_get_technician_ranking_with_filters_no_session_token(self, glpi_service):
        """Testa o ranking sem token de sessão"""
        glpi_service.session_token = None

        result = glpi_service.get_technician_ranking_with_filters(
            start_date='2025-01-01',
            end_date='2025-12-31'
        )

        assert result == []

    @patch('backend.services.glpi_service.GLPIService._authenticate_with_retry')
    @patch('backend.services.glpi_service.requests.get')
    def test_get_technician_ranking_with_filters_invalid_dates(self, mock_get, mock_auth, glpi_service):
        """Testa o ranking com datas inválidas"""
        # Mock da autenticação
        mock_auth.return_value = True
        
        glpi_service.session_token = 'mock_token'

        # Testa com data de início posterior à data de fim
        result = glpi_service.get_technician_ranking_with_filters(
            start_date='2025-12-31',
            end_date='2025-01-01'
        )

        # O método deve lidar com datas inválidas graciosamente
        assert isinstance(result, list)

    @patch('backend.services.glpi_service.GLPIService._authenticate_with_retry')
    @patch('backend.services.glpi_service.requests.get')
    def test_get_technician_ranking_with_filters_exception_handling(self, mock_get, mock_auth, glpi_service):
        """Testa o tratamento de exceções no ranking"""
        # Mock da autenticação
        mock_auth.return_value = True
        
        # Mock que gera exceção
        mock_get.side_effect = Exception("Erro de conexão")
        glpi_service.session_token = 'mock_token'

        result = glpi_service.get_technician_ranking_with_filters(
            start_date='2025-01-01',
            end_date='2025-12-31'
        )

        # Deve retornar lista vazia em caso de exceção
        assert result == []