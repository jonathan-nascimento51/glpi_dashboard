# -*- coding: utf-8 -*-
"""Fixtures para testes usando pytest."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any, List

from tests.factories import (
    TicketFactory,
    ResolvedTicketFactory,
    DashboardMetricsFactory,
)
from domain.entities.ticket import Ticket, TicketStatus
from domain.entities.dashboard_metrics import DashboardMetrics
from domain.interfaces.repositories import TicketRepository
from domain.interfaces.cache import CacheInterface


@pytest.fixture
def sample_ticket() -> Ticket:
    """Fixture para um ticket de exemplo."""
    return TicketFactory()


@pytest.fixture
def resolved_ticket() -> Ticket:
    """Fixture para um ticket resolvido."""
    return ResolvedTicketFactory()


@pytest.fixture
def ticket_list() -> List[Ticket]:
    """Fixture para uma lista de tickets."""
    return [
        TicketFactory(status=TicketStatus.NOVO),
        TicketFactory(status=TicketStatus.PROCESSANDO),
        ResolvedTicketFactory(),
        TicketFactory(status=TicketStatus.PENDENTE),
    ]


@pytest.fixture
def dashboard_metrics() -> DashboardMetrics:
    """Fixture para métricas do dashboard."""
    return DashboardMetricsFactory()


@pytest.fixture
def mock_ticket_repository() -> Mock:
    """Mock do repositório de tickets."""
    mock_repo = Mock(spec=TicketRepository)
    mock_repo.get_tickets_by_date_range = AsyncMock(return_value=[])
    mock_repo.get_dashboard_metrics = AsyncMock(return_value=DashboardMetricsFactory())
    return mock_repo


@pytest.fixture
def mock_cache() -> Mock:
    """Mock do cache."""
    mock_cache = Mock(spec=CacheInterface)
    mock_cache.get = AsyncMock(return_value=None)
    mock_cache.set = AsyncMock(return_value=None)
    mock_cache.delete = AsyncMock(return_value=None)
    return mock_cache


@pytest.fixture
def mock_glpi_response() -> Dict[str, Any]:
    """Mock de resposta da API GLPI."""
    return {
        "data": [
            {
                "id": "1",
                "name": "Ticket de teste",
                "status": "2",
                "priority": "3",
                "date_creation": "2024-01-01 10:00:00",
                "date_mod": "2024-01-01 11:00:00",
                "groups_id_assign": "1",
                "users_id_assign": "1",
            }
        ],
        "count": 1,
        "totalcount": 1,
    }


@pytest.fixture
def date_range_params() -> Dict[str, str]:
    """Fixture para parâmetros de range de data."""
    hoje = datetime.now()
    ontem = hoje - timedelta(days=1)
    return {
        "data_inicio": ontem.strftime("%Y-%m-%d"),
        "data_fim": hoje.strftime("%Y-%m-%d"),
    }
