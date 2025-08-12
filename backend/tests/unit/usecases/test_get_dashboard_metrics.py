"""Testes para o caso de uso GetDashboardMetricsUseCase."""

import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime, timezone

from usecases.get_dashboard_metrics import GetDashboardMetricsUseCase
from tests.factories import DashboardMetricsFactory


class TestGetDashboardMetricsUseCase:
    """Testes para GetDashboardMetricsUseCase."""

    @pytest.fixture
    def mock_glpi_repository(self):
        """Mock do repositorio GLPI."""
        return AsyncMock()

    @pytest.fixture
    def mock_cache_repository(self):
        """Mock do repositorio de cache."""
        return AsyncMock()

    @pytest.fixture
    def mock_clock(self):
        """Mock do clock."""
        clock = Mock()
        clock.now.return_value = datetime.now(timezone.utc)
        return clock

    @pytest.fixture
    def use_case(self, mock_glpi_repository, mock_cache_repository, mock_clock):
        """Instancia do caso de uso."""
        return GetDashboardMetricsUseCase(
            glpi_repository=mock_glpi_repository,
            cache_repository=mock_cache_repository,
            clock=mock_clock,
            cache_ttl=300,
        )

    @pytest.mark.asyncio
    async def test_execute_without_cache(
        self, use_case, mock_glpi_repository, mock_cache_repository
    ):
        """Testa execucao sem cache."""
        # Arrange
        expected_metrics = DashboardMetricsFactory()
        mock_cache_repository.get.return_value = None
        mock_glpi_repository.get_dashboard_metrics.return_value = expected_metrics

        # Act
        result = await use_case.execute()

        # Assert
        assert result == expected_metrics
        mock_cache_repository.get.assert_called_once_with("dashboard_metrics")
        mock_glpi_repository.get_dashboard_metrics.assert_called_once()
        mock_cache_repository.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_with_cache(
        self, use_case, mock_glpi_repository, mock_cache_repository
    ):
        """Testa execucao com cache."""
        # Arrange
        cached_metrics = DashboardMetricsFactory()
        mock_cache_repository.get.return_value = cached_metrics

        # Act
        result = await use_case.execute()

        # Assert
        assert result == cached_metrics
        mock_cache_repository.get.assert_called_once_with("dashboard_metrics")
        mock_glpi_repository.get_dashboard_metrics.assert_not_called()
        mock_cache_repository.set.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_force_refresh(
        self, use_case, mock_glpi_repository, mock_cache_repository
    ):
        """Testa execucao com refresh forcado."""
        # Arrange
        expected_metrics = DashboardMetricsFactory()
        mock_glpi_repository.get_dashboard_metrics.return_value = expected_metrics

        # Act
        result = await use_case.execute(force_refresh=True)

        # Assert
        assert result == expected_metrics
        mock_cache_repository.get.assert_not_called()
        mock_glpi_repository.get_dashboard_metrics.assert_called_once()
        mock_cache_repository.set.assert_called_once()
