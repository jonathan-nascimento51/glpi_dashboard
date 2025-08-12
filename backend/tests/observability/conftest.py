# -*- coding: utf-8 -*-
"""Configuracao para testes de observabilidade"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from prometheus_client import CollectorRegistry

@pytest.fixture
def mock_registry():
    """Mock do registry do Prometheus"""
    registry = Mock(spec=CollectorRegistry)
    registry._names_to_collectors = {}
    yield registry

@pytest.fixture
def test_client():
    """Cliente de teste para a aplicacao"""
    from fastapi import FastAPI
    from observability import setup_observability
    
    app = FastAPI()
    setup_observability(app)
    return TestClient(app)

@pytest.fixture
def sample_kpi_data():
    """Dados de exemplo para KPIs"""
    return [
        {"level": "N1", "total": 150, "open": 45, "in_progress": 30, "closed": 75},
        {"level": "N2", "total": 89, "open": 23, "in_progress": 18, "closed": 48},
        {"level": "N3", "total": 67, "open": 12, "in_progress": 15, "closed": 40},
        {"level": "N4", "total": 34, "open": 8, "in_progress": 6, "closed": 20}
    ]

@pytest.fixture
def sample_metrics_data():
    """Dados de exemplo para metricas"""
    return {
        "total_tickets": 340,
        "resolved_tickets": 183,
        "avg_resolution_time": 4.2,
        "customer_satisfaction": 4.1
    }
