"""Configurações e fixtures compartilhadas para testes."""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from flask import Flask
from backend.config.settings import TestingConfig
from backend.services.glpi_service import GLPIService
from backend.api.routes import api_bp


@pytest.fixture(scope="session")
def app():
    """Cria uma instância da aplicação Flask para testes."""
    app = Flask(__name__)
    app.config.from_object(TestingConfig)
    
    # Registrar blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Configurar contexto da aplicação
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """Cliente de teste para requisições HTTP."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Runner para comandos CLI."""
    return app.test_cli_runner()


@pytest.fixture
def mock_glpi_service():
    """Mock do serviço GLPI para testes isolados."""
    with patch('backend.services.glpi_service.GLPIService') as mock:
        # Configurar comportamento padrão do mock
        mock_instance = Mock()
        mock.return_value = mock_instance
        
        # Dados de teste padrão
        mock_instance.get_technician_ranking.return_value = [
            {
                'id': '1',
                'name': 'Técnico Teste 1',
                'score': 100,
                'tickets_abertos': 5,
                'tickets_fechados': 15,
                'level': 'N1',
                'rank': 1
            },
            {
                'id': '2',
                'name': 'Técnico Teste 2',
                'score': 85,
                'tickets_abertos': 3,
                'tickets_fechados': 12,
                'level': 'N2',
                'rank': 2
            }
        ]
        
        mock_instance.get_dashboard_metrics.return_value = {
            'novos': 10,
            'pendentes': 5,
            'progresso': 8,
            'resolvidos': 25,
            'total': 48,
            'niveis': {
                'n1': {'novos': 3, 'pendentes': 1, 'progresso': 2, 'resolvidos': 8},
                'n2': {'novos': 2, 'pendentes': 2, 'progresso': 3, 'resolvidos': 7},
                'n3': {'novos': 3, 'pendentes': 1, 'progresso': 2, 'resolvidos': 6},
                'n4': {'novos': 2, 'pendentes': 1, 'progresso': 1, 'resolvidos': 4}
            },
            'tendencias': {
                'novos': '+5%',
                'pendentes': '-2%',
                'progresso': '+3%',
                'resolvidos': '+8%'
            }
        }
        
        mock_instance.get_system_status.return_value = {
            'status': 'online',
            'api': 'active',
            'glpi': 'connected',
            'glpi_message': 'Sistema funcionando normalmente',
            'glpi_response_time': 150,
            'last_update': '2024-01-15T10:30:00Z',
            'version': '10.0.15',
            'sistema_ativo': True,
            'ultima_atualizacao': '2024-01-15T10:30:00Z'
        }
        
        yield mock_instance


@pytest.fixture
def sample_technician_data():
    """Dados de exemplo para testes de técnicos."""
    return [
        {
            'id': '1',
            'name': 'João Silva',
            'score': 95,
            'tickets_abertos': 3,
            'tickets_fechados': 18,
            'level': 'N1',
            'rank': 1,
            'group_id': '10'
        },
        {
            'id': '2',
            'name': 'Maria Santos',
            'score': 88,
            'tickets_abertos': 5,
            'tickets_fechados': 15,
            'level': 'N2',
            'rank': 2,
            'group_id': '11'
        },
        {
            'id': '3',
            'name': 'Pedro Costa',
            'score': 82,
            'tickets_abertos': 2,
            'tickets_fechados': 12,
            'level': 'N1',
            'rank': 3,
            'group_id': '10'
        }
    ]


@pytest.fixture
def sample_metrics_data():
    """Dados de exemplo para métricas do dashboard."""
    return {
        'novos': 15,
        'pendentes': 8,
        'progresso': 12,
        'resolvidos': 45,
        'total': 80,
        'niveis': {
            'n1': {'novos': 5, 'pendentes': 2, 'progresso': 3, 'resolvidos': 15},
            'n2': {'novos': 4, 'pendentes': 3, 'progresso': 4, 'resolvidos': 12},
            'n3': {'novos': 3, 'pendentes': 2, 'progresso': 3, 'resolvidos': 10},
            'n4': {'novos': 3, 'pendentes': 1, 'progresso': 2, 'resolvidos': 8}
        },
        'tendencias': {
            'novos': '+10%',
            'pendentes': '-5%',
            'progresso': '+15%',
            'resolvidos': '+20%'
        }
    }


@pytest.fixture
def temp_cache_dir():
    """Diretório temporário para cache durante testes."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Configuração automática do ambiente de teste."""
    # Configurar variáveis de ambiente para testes
    monkeypatch.setenv('FLASK_ENV', 'test')
    monkeypatch.setenv('TESTING', 'True')
    monkeypatch.setenv('CACHE_TYPE', 'simple')
    
    # Desabilitar logs durante testes
    import logging
    logging.disable(logging.CRITICAL)
    
    yield
    
    # Reabilitar logs após testes
    logging.disable(logging.NOTSET)


@pytest.fixture
def mock_redis():
    """Mock do Redis para testes de cache."""
    with patch('redis.Redis') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        
        # Simular comportamento do Redis
        cache_store = {}
        
        def mock_get(key):
            return cache_store.get(key)
        
        def mock_set(key, value, ex=None):
            cache_store[key] = value
            return True
        
        def mock_delete(key):
            return cache_store.pop(key, None) is not None
        
        def mock_exists(key):
            return key in cache_store
        
        mock_instance.get.side_effect = mock_get
        mock_instance.set.side_effect = mock_set
        mock_instance.delete.side_effect = mock_delete
        mock_instance.exists.side_effect = mock_exists
        
        yield mock_instance


@pytest.fixture
def mock_requests():
    """Mock para requisições HTTP externas."""
    with patch('requests.Session') as mock:
        mock_session = Mock()
        mock.return_value = mock_session
        
        # Configurar respostas padrão
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True}
        mock_response.text = '{"success": true}'
        
        mock_session.get.return_value = mock_response
        mock_session.post.return_value = mock_response
        
        yield mock_session