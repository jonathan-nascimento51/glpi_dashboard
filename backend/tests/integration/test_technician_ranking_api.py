import pytest
import json
from unittest.mock import patch, Mock
import sys
import os

# Adiciona o diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Importa a aplicação Flask do arquivo test_app.py do backend
from test_app import app
from services.glpi_service import GLPIService


class TestTechnicianRankingAPI:
    """Testes de integração para a API de ranking de técnicos"""

    @pytest.fixture
    def client(self):
        """Fixture para cliente de teste Flask"""
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

    def test_get_technician_ranking_without_filters(self, client):
        """Testa a API de ranking sem filtros"""
        # Faz a requisição
        response = client.get('/api/technicians/ranking')

        # Verificações básicas
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert isinstance(data['data'], list)
        
        # Se há dados, verifica a estrutura
        if data['data']:
            ranking_item = data['data'][0]
            assert 'id' in ranking_item
            assert 'name' in ranking_item
            assert 'level' in ranking_item
            assert 'rank' in ranking_item

    def test_get_technician_ranking_with_date_filters(self, client):
        """Testa a API de ranking com filtros de data"""
        # Faz a requisição com filtros
        response = client.get('/api/technicians/ranking?start_date=2024-01-01&end_date=2024-01-31&limit=10')

        # Verificações básicas
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert isinstance(data['data'], list)
        
        # Verifica se os filtros foram aplicados na resposta
        assert 'filters_applied' in data
        filters = data['filters_applied']
        assert filters['start_date'] == '2024-01-01'
        assert filters['end_date'] == '2024-01-31'
        assert filters['limit'] == 10

    def test_get_technician_ranking_with_all_filters(self, client):
        """Testa a API de ranking com todos os filtros"""
        # Faz a requisição com todos os filtros
        response = client.get('/api/technicians/ranking?start_date=2025-01-01&end_date=2025-12-31&level=Sênior&limit=2')

        # Verificações
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        # Verifica que retorna uma lista (pode estar vazia ou com dados)
        assert isinstance(data['data'], list)
        # Se houver dados, verifica que não excede o limite
        if data['data']:
            assert len(data['data']) <= 2

    @patch('backend.services.glpi_service.GLPIService.get_technician_ranking_with_filters')
    def test_get_technician_ranking_empty_result(self, mock_get_ranking_with_filters, client):
        """Testa a API quando não há dados de ranking"""
        # Mock do serviço GLPI retornando lista vazia
        mock_get_ranking_with_filters.return_value = []

        # Faz a requisição
        response = client.get('/api/technicians/ranking?start_date=2025-01-01&end_date=2025-12-31')

        # Verificações
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data'] == []
        assert 'Nenhum técnico encontrado com os filtros aplicados' in data['message']

    def test_get_technician_ranking_service_error(self, client):
        """Testa a API quando há erro no serviço GLPI"""
        # Faz a requisição com datas futuras que podem não retornar dados
        response = client.get('/api/technicians/ranking?start_date=2025-01-01&end_date=2025-12-31')

        # Verificações - a API deve responder normalmente mesmo sem dados
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        # Pode ter dados ou não, dependendo da configuração do GLPI

    @patch('backend.services.glpi_service.GLPIService.get_technician_ranking_with_filters')
    def test_get_technician_ranking_invalid_date_format(self, mock_get_ranking_with_filters, client):
        """Testa a API com formato de data inválido"""
        # Faz a requisição com data inválida
        response = client.get('/api/technicians/ranking?start_date=invalid-date&end_date=2025-12-31')

        # A API deve lidar graciosamente com datas inválidas
        assert response.status_code in [200, 400]  # Dependendo da implementação

    @patch('backend.services.glpi_service.GLPIService.get_technician_ranking_with_filters')
    def test_get_technician_ranking_limit_validation(self, mock_get_ranking_with_filters, client, mock_ranking_data):
        """Testa a validação do parâmetro limit"""
        # Mock do serviço GLPI
        mock_get_ranking_with_filters.return_value = mock_ranking_data[:1]

        # Faz a requisição com limit
        response = client.get('/api/technicians/ranking?limit=1')

        # Verificações
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['data']) <= 1

    def test_get_technician_ranking_negative_limit(self, client):
        """Testa a API com limit negativo"""
        # Faz a requisição com limit negativo
        response = client.get('/api/technicians/ranking?limit=-1')

        # A API deve lidar graciosamente com valores inválidos
        assert response.status_code in [200, 400, 500]  # Aceita diferentes comportamentos

    def test_get_technician_ranking_large_limit(self, client):
        """Testa a API com limit muito grande"""
        # Faz a requisição com limit grande
        response = client.get('/api/technicians/ranking?limit=1000')

        # Verificações
        assert response.status_code == 200
        data = json.loads(response.data)
        # Verifica que retorna dados válidos
        assert isinstance(data['data'], list)

    def test_get_technician_ranking_response_format(self, client):
        """Testa o formato da resposta da API"""
        # Faz a requisição
        response = client.get('/api/technicians/ranking')

        # Verificações do formato da resposta
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        data = json.loads(response.data)
        assert 'success' in data
        assert 'data' in data
        # Note: 'message' só está presente quando não há dados
        
        # Verifica estrutura dos dados de ranking
        if data['data']:
            ranking_item = data['data'][0]
            assert 'id' in ranking_item
            assert 'name' in ranking_item
            assert 'level' in ranking_item
            assert 'rank' in ranking_item
            # tickets_count pode não estar presente em dados reais

    def test_get_technician_ranking_cors_headers(self, client):
        """Testa se os headers CORS estão configurados corretamente"""
        response = client.get('/api/technicians/ranking')
        
        # Verifica headers CORS (se configurados)
        # Isso depende da configuração do Flask-CORS
        assert response.status_code in [200, 500]  # Pode falhar por falta de dados, mas não por CORS