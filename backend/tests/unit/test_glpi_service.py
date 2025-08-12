# -*- coding: utf-8 -*-
import pytest
from unittest.mock import patch

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from services.glpi_service import GLPIService


class TestGLPIService:
    """Testes unitarios para GLPIService"""

    @pytest.fixture
    def glpi_service(self):
        """Fixture que cria uma instancia do GLPIService para testes"""
        with patch("services.glpi_service.active_config") as mock_config:
            mock_config.GLPI_URL = "https://test-glpi.com/apirest.php"
            mock_config.GLPI_APP_TOKEN = "test_app_token"
            mock_config.GLPI_USER_TOKEN = "test_user_token"
            mock_config.LOG_LEVEL = "INFO"
            service = GLPIService()
            return service

    def test_glpi_service_initialization(self, glpi_service):
        """Testa a inicializacao do GLPIService"""
        assert glpi_service.glpi_url == "https://test-glpi.com/apirest.php"
        assert glpi_service.app_token == "test_app_token"
        assert glpi_service.user_token == "test_user_token"
        assert glpi_service.session_token is None

    def test_get_tickets(self, glpi_service):
        """Testa o metodo get_tickets"""
        result = glpi_service.get_tickets()
        assert result["success"] is True
        assert "data" in result
        assert result["message"] == "Test implementation"

    def test_get_tickets_with_filters(self, glpi_service):
        """Testa o metodo get_tickets com filtros"""
        filters = {"status": 1, "group": 89}
        result = glpi_service.get_tickets(filters)
        assert result["success"] is True
        assert "data" in result
        assert result["message"] == "Test implementation"

    def test_get_dashboard_metrics(self, glpi_service):
        """Testa o metodo get_dashboard_metrics"""
        result = glpi_service.get_dashboard_metrics()
        assert result["success"] is True
        assert "data" in result
        assert result["message"] == "Test implementation"
