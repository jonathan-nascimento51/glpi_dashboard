# -*- coding: utf-8 -*-
"""Configurações compartilhadas para todos os testes"""
import logging
import os
import sys
from unittest.mock import Mock, patch

import pytest

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.glpi_service import GLPIService


@pytest.fixture(autouse=True)
def setup_logging():
    """Configura logging para testes"""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Silencia logs durante testes para não poluir a saída
    logging.getLogger("glpi_service").setLevel(logging.CRITICAL)
    logging.getLogger("requests").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)


@pytest.fixture
def mock_glpi_config():
    """Mock das configurações do GLPI"""
    config = Mock()
    config.GLPI_URL = "https://test-glpi.com/apirest.php"
    config.GLPI_APP_TOKEN = "test_app_token"
    config.GLPI_USER_TOKEN = "test_user_token"
    return config


@pytest.fixture
def mock_requests_session():
    """Mock de uma sessão de requests"""
    session = Mock()
    response = Mock()
    response.ok = True
    response.status_code = 200
    response.json.return_value = {"session_token": "test_session_token"}
    session.get.return_value = response
    session.post.return_value = response
    return session


@pytest.fixture
def sample_ticket_data():
    """Dados de exemplo de tickets para testes"""
    return {
        "totalcount": 3,
        "data": [
            {
                "2": "1",  # ID
                "1": "Ticket 1",  # Nome
                "12": "1",  # Status (Novo)
                "8": "89",  # Grupo (N1)
                "15": "2024-01-15 10:30:00",  # Data de criação
                "21": "Descrição do ticket 1",  # Conteúdo
            },
            {
                "2": "2",
                "1": "Ticket 2",
                "12": "2",  # Status (Processando)
                "8": "90",  # Grupo (N2)
                "15": "2024-01-16 14:20:00",
                "21": "Descrição do ticket 2",
            },
            {
                "2": "3",
                "1": "Ticket 3",
                "12": "5",  # Status (Solucionado)
                "8": "91",  # Grupo (N3)
                "15": "2024-01-17 09:15:00",
                "21": "Descrição do ticket 3",
            },
        ],
    }


@pytest.fixture
def sample_user_data():
    """Dados de exemplo de usuários para testes"""
    return {
        "totalcount": 2,
        "data": [
            {
                "2": "1",  # ID
                "1": "user1",  # Username
                "name": "user1",
                "realname": "Silva",
                "firstname": "João",
                "is_active": 1,
                "is_deleted": 0,
            },
            {
                "2": "2",
                "1": "user2",
                "name": "user2",
                "realname": "Santos",
                "firstname": "Maria",
                "is_active": 1,
                "is_deleted": 0,
            },
        ],
    }


@pytest.fixture
def sample_field_ids():
    """IDs de campos de exemplo para testes"""
    return {
        "STATUS": "12",
        "GROUP": "8",
        "TECHNICIAN": "5",
        "DATE": "15",
        "PRIORITY": "3",
        "CATEGORY": "7",
    }


@pytest.fixture
def sample_metrics_data():
    """Dados de métricas de exemplo para testes"""
    return {
        "level_metrics": {
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
        },
        "general_metrics": {
            "Novo": 50,
            "Processando (atribuído)": 25,
            "Processando (planejado)": 15,
            "Pendente": 10,
            "Solucionado": 30,
            "Fechado": 40,
        },
    }


@pytest.fixture
def glpi_service(mock_glpi_config):
    """Fixture para instanciar GLPIService com configuração mockada"""
    with patch("services.glpi_service.active_config", mock_glpi_config):
        service = GLPIService()
        return service


@pytest.fixture
def mock_http_response():
    """Mock de resposta HTTP"""
    response = Mock()
    response.ok = True
    response.status_code = 200
    response.json.return_value = {"session_token": "test_token"}
    response.raise_for_status.return_value = None
    return response


@pytest.fixture
def mock_authenticated_service(glpi_service, mock_http_response):
    """Fixture para GLPIService autenticado"""
    glpi_service.session_token = "test_session_token"
    glpi_service.token_created_at = 1640995200  # Data fixa para testes
    glpi_service.token_expires_at = 1640998800
    return glpi_service
