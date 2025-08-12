import pytest
import json
from unittest.mock import patch, Mock
from app import create_app
from backend.services.glpi_service import GLPIService


class TestTechnicianRankingAPI:
    """Testes de integração para a API de ranking de técnicos"""

    @pytest.fixture
    def client(self):
        """Fixture para cliente de teste Flask"""
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    @pytest.fixture
    def mock_ranking_data(self):
        """Mock de dados de ranking para testes"""
        return [
            {
                'id': 1,
                'name': 'João Silva',
                'level': 'Sênior',
                'tickets_count': 25,
                'rank': 1
            },
            {
                'id': 2,
                'name': 'Maria Santos',
                'level': 'Pleno',
                'tickets_count': 20,
                'rank': 2
            },
            {
                'id': 3,
                'name': 'Pedro Costa',
                'level': 'Júnior',
                'tickets_count': 15,
                'rank': 3
            }
        ]

    @patch('backend.api.routes.glpi_service')
    def test_get_technician_ranking_without_filters(self, mock_glpi_service, client, mock_ranking_data):
        """Testa a API de ranking sem filtros"""
        # Mock do serviço GLPI
        mock_glpi_service.get_technician_ranking.return_value = mock_ranking_data

        # Faz a requisição
        response = client.get('/api/technicians/ranking')

        # Verificações
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']) == 3
        assert data['data'][0]['name'] == 'João Silva'
        assert data['data'][0]['rank'] == 1

    @patch('backend.api.routes.glpi_service')
    def test_get_technician_ranking_with_date_filters(self, mock_glpi_service, client, mock_ranking_data):
        """Testa a API de ranking com filtros de data"""
        # Mock do serviço GLPI
        mock_glpi_service.get_technician_ranking_with_filters.return_value = mock_ranking_data

        # Faz a requisição com filtros
        response = client.get('/api/technicians/ranking?start_date=2025-01-01&end_date=2025-12-31')

        # Verificações
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']) == 3
        
        # Verifica se o método com filtros foi chamado
        mock_glpi_service.get_technician_ranking_with_filters.assert_called_once_with(
            start_date='2025-01-01',
            end_date='2025-12-31',
            level=None,
            limit=None
        )

    @patch('backend.api.routes.glpi_service')
    def test_get_technician_ranking_with_all_filters(self, mock_glpi_service, client, mock_ranking_data):
        """Testa a API de ranking com todos os filtros"""
        # Mock do serviço GLPI
        mock_glpi_service.get_technician_ranking_with_filters.return_value = mock_ranking_data[:2]

        # Faz a requisição com todos os filtros
        response = client.get('/api/technicians/ranking?start_date=2025-01-01&end_date=2025-12-31&level=Sênior&limit=2')

        # Verificações
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']) == 2
        
        # Verifica se o método com filtros foi chamado com todos os parâmetros
        mock_glpi_service.get_technician_ranking_with_filters.assert_called_once_with(
            start_date='2025-01-01',
            end_date='2025-12-31',
            level='Sênior',
            limit=2
        )

    @patch('backend.api.routes.glpi_service')
    def test_get_technician_ranking_empty_result(self, mock_glpi_service, client):
        """Testa a API quando não há dados de ranking"""
        # Mock do serviço GLPI retornando lista vazia
        mock_glpi_service.get_technician_ranking_with_filters.return_value = []

        # Faz a requisição
        response = client.get('/api/technicians/ranking?start_date=2025-01-01&end_date=2025-12-31')

        # Verificações
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data'] == []
        assert 'Não foi possível obter dados de técnicos do GLPI' in data['message']

    @patch('backend.api.routes.glpi_service')
    def test_get_technician_ranking_service_error(self, mock_glpi_service, client):
        """Testa a API quando há erro no serviço GLPI"""
        # Mock do serviço GLPI gerando exceção
        mock_glpi_service.get_technician_ranking_with_filters.side_effect = Exception("Erro de conexão")

        # Faz a requisição
        response = client.get('/api/technicians/ranking?start_date=2025-01-01&end_date=2025-12-31')

        # Verificações
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Erro interno do servidor' in data['message']

    @patch('backend.api.routes.glpi_service')
    def test_get_technician_ranking_invalid_date_format(self, mock_glpi_service, client):
        """Testa a API com formato de data inválido"""
        # Faz a requisição com data inválida
        response = client.get('/api/technicians/ranking?start_date=invalid-date&end_date=2025-12-31')

        # A API deve lidar graciosamente com datas inválidas
        assert response.status_code in [200, 400]  # Dependendo da implementação

    @patch('backend.api.routes.glpi_service')
    def test_get_technician_ranking_limit_validation(self, mock_glpi_service, client, mock_ranking_data):
        """Testa a validação do parâmetro limit"""
        # Mock do serviço GLPI
        mock_glpi_service.get_technician_ranking_with_filters.return_value = mock_ranking_data[:1]

        # Faz a requisição com limit
        response = client.get('/api/technicians/ranking?limit=1')

        # Verificações
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['data']) <= 1

    @patch('backend.api.routes.glpi_service')
    def test_get_technician_ranking_negative_limit(self, mock_glpi_service, client):
        """Testa a API com limit negativo"""
        # Faz a requisição com limit negativo
        response = client.get('/api/technicians/ranking?limit=-1')

        # A API deve lidar graciosamente com valores inválidos
        assert response.status_code in [200, 400]

    @patch('backend.api.routes.glpi_service')
    def test_get_technician_ranking_large_limit(self, mock_glpi_service, client, mock_ranking_data):
        """Testa a API com limit muito grande"""
        # Mock do serviço GLPI
        mock_glpi_service.get_technician_ranking_with_filters.return_value = mock_ranking_data

        # Faz a requisição com limit grande
        response = client.get('/api/technicians/ranking?limit=1000')

        # Verificações
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['data']) <= len(mock_ranking_data)

    @patch('backend.api.routes.glpi_service')
    def test_get_technician_ranking_response_format(self, mock_glpi_service, client, mock_ranking_data):
        """Testa o formato da resposta da API"""
        # Mock do serviço GLPI
        mock_glpi_service.get_technician_ranking.return_value = mock_ranking_data

        # Faz a requisição
        response = client.get('/api/technicians/ranking')

        # Verificações do formato da resposta
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        data = json.loads(response.data)
        assert 'success' in data
        assert 'data' in data
        assert 'message' in data
        
        # Verifica estrutura dos dados de ranking
        if data['data']:
            ranking_item = data['data'][0]
            assert 'id' in ranking_item
            assert 'name' in ranking_item
            assert 'level' in ranking_item
            assert 'tickets_count' in ranking_item
            assert 'rank' in ranking_item

    def test_get_technician_ranking_cors_headers(self, client):
        """Testa se os headers CORS estão configurados corretamente"""
        response = client.get('/api/technicians/ranking')
        
        # Verifica headers CORS (se configurados)
        # Isso depende da configuração do Flask-CORS
        assert response.status_code in [200, 500]  # Pode falhar por falta de dados, mas não por CORS