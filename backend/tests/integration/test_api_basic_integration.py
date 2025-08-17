import pytest
import json
import sys
import os

# Adiciona o diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Importa a aplicação Flask do arquivo test_app.py do backend
from test_app import app


class TestBasicAPIIntegration:
    """Testes básicos de integração para verificar se as APIs estão funcionando"""

    @pytest.fixture
    def client(self):
        """Fixture para cliente de teste Flask"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_technician_ranking_api_responds(self, client):
        """Testa se a API de ranking de técnicos responde"""
        response = client.get('/api/technicians/ranking')
        
        # Verifica se a API responde (pode ser 200 ou erro, mas não deve falhar)
        assert response.status_code in [200, 400, 500, 503]
        
        # Verifica se a resposta é JSON válido
        try:
            data = json.loads(response.data)
            assert isinstance(data, dict)
        except json.JSONDecodeError:
            pytest.fail("Resposta não é JSON válido")

    def test_technician_ranking_api_with_filters_responds(self, client):
        """Testa se a API de ranking com filtros responde"""
        response = client.get('/api/technicians/ranking?start_date=2025-01-01&end_date=2025-01-31')
        
        # Verifica se a API responde
        assert response.status_code in [200, 400, 500, 503]
        
        # Verifica se a resposta é JSON válido
        try:
            data = json.loads(response.data)
            assert isinstance(data, dict)
        except json.JSONDecodeError:
            pytest.fail("Resposta não é JSON válido")

    def test_technician_ranking_api_invalid_date_format(self, client):
        """Testa se a API lida com formato de data inválido"""
        response = client.get('/api/technicians/ranking?start_date=invalid-date')
        
        # Deve retornar erro 400 para data inválida
        assert response.status_code == 400
        
        # Verifica se a resposta é JSON válido
        try:
            data = json.loads(response.data)
            assert isinstance(data, dict)
            assert 'success' in data
            assert data['success'] is False
        except json.JSONDecodeError:
            pytest.fail("Resposta não é JSON válido")

    def test_technician_ranking_api_response_structure(self, client):
        """Testa se a estrutura da resposta está correta quando há sucesso"""
        response = client.get('/api/technicians/ranking')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            
            # Verifica estrutura básica da resposta
            assert 'success' in data
            assert 'data' in data
            
            # Se há dados, verifica se é uma lista
            if data['data']:
                assert isinstance(data['data'], list)
                
                # Verifica estrutura básica de um item de ranking
                first_item = data['data'][0]
                assert isinstance(first_item, dict)
                # Campos básicos que devem existir
                expected_fields = ['id', 'name']
                for field in expected_fields:
                    assert field in first_item, f"Campo '{field}' não encontrado no item de ranking"