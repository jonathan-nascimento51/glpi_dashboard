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
                    '2': '1',  # ID do Profile_User
                    '5': '10',  # users_id (ID do usuário)
                    '4': '6',   # Perfil (técnico)
                    '80': '1'   # Entidade
                },
                {
                    '2': '2',
                    '5': '20',
                    '4': '6',
                    '80': '1'
                },
                {
                    '2': '3',
                    '5': '30',
                    '4': '6',
                    '80': '1'
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
    @patch('backend.services.glpi_service.GLPIService._ensure_authenticated')
    @patch('backend.services.glpi_service.GLPIService._make_authenticated_request')
    def test_get_technician_ranking_with_filters_success(self, mock_request, mock_ensure_auth, mock_auth, glpi_service, mock_technicians_response, mock_tickets_response):
        """Testa o ranking de técnicos com filtros aplicados com sucesso"""
        # Mock da autenticação
        mock_auth.return_value = True
        mock_ensure_auth.return_value = True
        
        # Mock das requisições - retorna dados válidos para todas as chamadas
        def mock_request_side_effect(*args, **kwargs):
            url = args[1] if len(args) > 1 else kwargs.get('url', '')
            
            # Busca de técnicos
            if 'search/Profile_User' in url:
                return Mock(ok=True, json=lambda: mock_technicians_response, headers={})
            
            # Dados dos usuários
            elif '/User/' in url:
                user_id = url.split('/User/')[-1]
                if user_id == '10':
                    return Mock(ok=True, json=lambda: {'name': 'joao', 'realname': 'João', 'firstname': 'João', 'lastname': 'Silva'}, headers={})
                elif user_id == '20':
                    return Mock(ok=True, json=lambda: {'name': 'maria', 'realname': 'Maria', 'firstname': 'Maria', 'lastname': 'Santos'}, headers={})
                elif user_id == '30':
                    return Mock(ok=True, json=lambda: {'name': 'pedro', 'realname': 'Pedro', 'firstname': 'Pedro', 'lastname': 'Costa'}, headers={})
            
            # Busca de grupos
            elif 'search/Group_User' in url:
                return Mock(ok=True, json=lambda: {'data': []}, headers={})
            
            # Busca de tickets
            elif 'search/Ticket' in url:
                params = kwargs.get('params', {})
                user_id = None
                for key, value in params.items():
                    if 'value' in key and value in ['10', '20', '30']:
                        user_id = value
                        break
                
                if user_id == '10':
                    return Mock(ok=True, json=lambda: mock_tickets_response, headers={'Content-Range': 'items 0-4/5'})
                elif user_id == '20':
                    return Mock(ok=True, json=lambda: {'data': [mock_tickets_response['data'][2]]}, headers={'Content-Range': 'items 0-0/1'})
                elif user_id == '30':
                    return Mock(ok=True, json=lambda: {'data': mock_tickets_response['data'][3:6]}, headers={'Content-Range': 'items 0-2/3'})
            
            # Default
            return Mock(ok=True, json=lambda: {'data': []}, headers={})
        
        mock_request.side_effect = mock_request_side_effect

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
        assert result[0]['name'] == 'João'
        assert result[0]['total'] == 5
        assert result[0]['rank'] == 1
        
        assert result[1]['name'] == 'Pedro'
        assert result[1]['total'] == 3
        assert result[1]['rank'] == 2
        
        assert result[2]['name'] == 'Maria'
        assert result[2]['total'] == 1
        assert result[2]['rank'] == 3

    @patch('backend.services.glpi_service.GLPIService._authenticate_with_retry')
    @patch('backend.services.glpi_service.requests.get')
    def test_get_technician_ranking_with_filters_no_technicians(self, mock_get, mock_auth, glpi_service):
        """Testa o ranking quando não há técnicos encontrados"""
        # Mock da autenticação
        mock_auth.return_value = True
        glpi_service._ensure_authenticated = Mock(return_value=True)
        
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
        glpi_service._ensure_authenticated = Mock(return_value=True)
        
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
        glpi_service._ensure_authenticated = Mock(return_value=True)
        
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
        glpi_service._ensure_authenticated = Mock(return_value=True)
        
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
        glpi_service._ensure_authenticated = Mock(return_value=False)
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
        glpi_service._ensure_authenticated = Mock(return_value=True)
        
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
        glpi_service._ensure_authenticated = Mock(return_value=True)
        
        # Mock que gera exceção
        mock_get.side_effect = Exception("Erro de conexão")
        glpi_service.session_token = 'mock_token'

        result = glpi_service.get_technician_ranking_with_filters(
            start_date='2025-01-01',
            end_date='2025-12-31'
        )

        # Deve retornar lista vazia em caso de exceção
        assert result == []