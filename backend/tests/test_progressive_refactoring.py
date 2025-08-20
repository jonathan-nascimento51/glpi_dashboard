#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes para Refatoração Progressiva.

Este módulo contém testes unitários e de integração para validar
a implementação da refatoração progressiva.
"""

import asyncio
import json
import sys
import unittest
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.application.dto import MetricsDTO
from core.application.queries import BaseMetricsQuery, DashboardMetricsQuery, GeneralMetricsQuery, TechnicianRankingQuery
from core.application.services import ProgressiveRefactoringService, RefactoringConfig, RefactoringPhase


class MockLegacyService:
    """Mock do serviço legado para testes."""

    def __init__(self, should_fail: bool = False, delay: float = 0.0):
        self.should_fail = should_fail
        self.delay = delay
        self.call_count = 0

    async def get_metrics(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Mock de obtenção de métricas."""

        self.call_count += 1

        if self.delay > 0:
            await asyncio.sleep(self.delay)

        if self.should_fail:
            raise Exception("Legacy service error")

        return {
            "total_tickets": 100,
            "new_tickets": 20,
            "pending_tickets": 30,
            "in_progress_tickets": 25,
            "resolved_tickets": 25,
            "levels": {"n1": 40, "n2": 30, "n3": 20, "n4": 10},
            "timestamp": "2024-01-15T10:00:00Z",
            "source": "legacy",
        }

    async def get_technician_ranking(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Mock de ranking de técnicos."""

        self.call_count += 1

        if self.delay > 0:
            await asyncio.sleep(self.delay)

        if self.should_fail:
            raise Exception("Legacy service error")

        return {
            "technicians": [
                {"name": "João", "resolved_tickets": 30, "avg_resolution_time": 2.5},
                {"name": "Maria", "resolved_tickets": 25, "avg_resolution_time": 3.0},
            ],
            "source": "legacy",
        }


class MockNewArchitectureQuery(BaseMetricsQuery):
    """Mock da nova arquitetura para testes."""

    def __init__(self, should_fail: bool = False, delay: float = 0.0):
        self.should_fail = should_fail
        self.delay = delay
        self.call_count = 0

    async def execute(self, filters: Dict[str, Any]) -> MetricsDTO:
        """Mock de execução da query."""

        self.call_count += 1

        if self.delay > 0:
            await asyncio.sleep(self.delay)

        if self.should_fail:
            raise Exception("New architecture error")

        return MetricsDTO(
            total_tickets=105,  # Ligeiramente diferente para testar comparação
            new_tickets=22,
            pending_tickets=28,
            in_progress_tickets=25,
            resolved_tickets=30,
            levels={"n1": 42, "n2": 28, "n3": 22, "n4": 13},
            timestamp=datetime.fromisoformat("2024-01-15T10:00:00Z"),
            metadata={"source": "new_architecture"},
        )


class TestRefactoringPhases(unittest.TestCase):
    """Testes para fases da refatoração."""

    def setUp(self):
        """Configuração inicial dos testes."""

        self.legacy_service = MockLegacyService()
        self.new_query = MockNewArchitectureQuery()

        self.config = RefactoringConfig(
            phase=RefactoringPhase.LEGACY_ONLY,
            migration_percentage=0.0,
            enable_validation=False,
            enable_fallback=True,
            fallback_timeout_ms=1000,
        )

        self.service = ProgressiveRefactoringService(
            config=self.config,
            legacy_service=self.legacy_service,
            general_query=self.new_query,
            technician_query=self.new_query,
            dashboard_query=self.new_query,
        )

    def test_legacy_only_phase(self):
        """Testa fase legacy_only."""

        # Configurar para usar apenas sistema legado
        self.config.phase = RefactoringPhase.LEGACY_ONLY

        # Executar
        result = asyncio.run(self.service.get_dashboard_metrics({}))

        # Verificar
        self.assertEqual(result["source"], "legacy")
        self.assertEqual(self.legacy_service.call_count, 1)
        self.assertEqual(self.new_query.call_count, 0)

    def test_new_architecture_phase(self):
        """Testa fase new_architecture."""

        # Configurar para usar nova arquitetura
        self.config.phase = RefactoringPhase.NEW_ARCHITECTURE

        # Executar
        result = asyncio.run(self.service.get_dashboard_metrics({}))

        # Verificar
        self.assertEqual(result["metadata"]["source"], "new_architecture")
        self.assertEqual(self.legacy_service.call_count, 0)
        self.assertEqual(self.new_query.call_count, 1)

    def test_strangler_fig_phase_migration(self):
        """Testa migração gradual na fase strangler_fig."""

        # Configurar para migração de 50%
        self.config.phase = RefactoringPhase.STRANGLER_FIG
        self.config.migration_percentage = 0.5

        # Executar múltiplas vezes para testar distribuição
        legacy_count = 0
        new_count = 0

        for _ in range(100):
            result = asyncio.run(self.service.get_dashboard_metrics({}))

            if "source" in result and result["source"] == "legacy":
                legacy_count += 1
            else:
                new_count += 1

        # Verificar distribuição aproximada (com tolerância)
        total = legacy_count + new_count
        legacy_percentage = legacy_count / total
        new_percentage = new_count / total

        # Tolerância de 20% para variação estatística
        self.assertAlmostEqual(legacy_percentage, 0.5, delta=0.2)
        self.assertAlmostEqual(new_percentage, 0.5, delta=0.2)

    def test_validation_phase(self):
        """Testa fase de validação."""

        # Configurar para validação
        self.config.phase = RefactoringPhase.VALIDATION
        self.config.validation_sampling = 1.0  # 100% para garantir execução

        # Executar
        result = asyncio.run(self.service.get_dashboard_metrics({}))

        # Verificar que ambos os sistemas foram chamados
        self.assertEqual(self.legacy_service.call_count, 1)
        self.assertEqual(self.new_query.call_count, 1)

        # Resultado deve vir do sistema legado
        self.assertEqual(result["source"], "legacy")


class TestFallbackMechanism(unittest.TestCase):
    """Testes para mecanismo de fallback."""

    def setUp(self):
        """Configuração inicial dos testes."""

        self.legacy_service = MockLegacyService()
        self.new_query = MockNewArchitectureQuery()

        self.config = RefactoringConfig(
            phase=RefactoringPhase.NEW_ARCHITECTURE,
            enable_fallback=True,
            fallback_timeout_ms=1000,
        )

        self.service = ProgressiveRefactoringService(
            config=self.config,
            legacy_service=self.legacy_service,
            general_query=self.new_query,
            technician_query=self.new_query,
            dashboard_query=self.new_query,
        )

    def test_fallback_on_new_architecture_error(self):
        """Testa fallback quando nova arquitetura falha."""

        # Configurar nova arquitetura para falhar
        self.new_query.should_fail = True

        # Executar
        result = asyncio.run(self.service.get_dashboard_metrics({}))

        # Verificar que fallback foi usado
        self.assertEqual(result["source"], "legacy")
        self.assertEqual(self.legacy_service.call_count, 1)
        self.assertEqual(self.new_query.call_count, 1)

    def test_fallback_on_timeout(self):
        """Testa fallback quando nova arquitetura demora muito."""

        # Configurar nova arquitetura para demorar mais que o timeout
        self.new_query.delay = 2.0  # 2 segundos
        self.config.fallback_timeout_ms = 500  # 500ms timeout

        # Executar
        start_time = datetime.now()
        result = asyncio.run(self.service.get_dashboard_metrics({}))
        end_time = datetime.now()

        # Verificar que fallback foi usado rapidamente
        execution_time = (end_time - start_time).total_seconds()
        self.assertLess(execution_time, 1.0)  # Deve ser rápido devido ao fallback
        self.assertEqual(result["source"], "legacy")

    def test_no_fallback_when_disabled(self):
        """Testa que fallback não é usado quando desabilitado."""

        # Desabilitar fallback
        self.config.enable_fallback = False
        self.new_query.should_fail = True

        # Executar e esperar erro
        with self.assertRaises(Exception):
            asyncio.run(self.service.get_dashboard_metrics({}))


class TestDataComparison(unittest.TestCase):
    """Testes para comparação de dados."""

    def setUp(self):
        """Configuração inicial dos testes."""

        self.legacy_service = MockLegacyService()
        self.new_query = MockNewArchitectureQuery()

        self.config = RefactoringConfig(
            phase=RefactoringPhase.VALIDATION,
            validation_sampling=1.0,
            log_data_differences=True,
        )

        self.service = ProgressiveRefactoringService(
            config=self.config,
            legacy_service=self.legacy_service,
            general_query=self.new_query,
            technician_query=self.new_query,
            dashboard_query=self.new_query,
        )

    @patch("core.application.services.progressive_refactoring_service.logger")
    def test_data_comparison_logging(self, mock_logger):
        """Testa logging de comparação de dados."""

        # Executar
        result = asyncio.run(self.service.get_dashboard_metrics({}))

        # Verificar que comparação foi logada
        mock_logger.info.assert_called()

        # Verificar que diferenças foram detectadas
        log_calls = [call.args[0] for call in mock_logger.info.call_args_list]
        comparison_logs = [log for log in log_calls if "comparison" in log.lower()]

        self.assertTrue(len(comparison_logs) > 0)

    def test_identical_data_comparison(self):
        """Testa comparação quando dados são idênticos."""

        # Configurar nova arquitetura para retornar dados idênticos
        async def mock_execute(filters):
            legacy_result = await self.legacy_service.get_metrics(filters)
            return MetricsDTO(
                total_tickets=legacy_result["total_tickets"],
                new_tickets=legacy_result["new_tickets"],
                pending_tickets=legacy_result["pending_tickets"],
                in_progress_tickets=legacy_result["in_progress_tickets"],
                resolved_tickets=legacy_result["resolved_tickets"],
                levels=legacy_result["levels"],
                timestamp=datetime.fromisoformat(legacy_result["timestamp"]),
                metadata={"source": "new_architecture"},
            )

        self.new_query.execute = mock_execute

        # Executar
        with patch("core.application.services.progressive_refactoring_service.logger") as mock_logger:
            result = asyncio.run(self.service.get_dashboard_metrics({}))

            # Verificar que não há logs de diferença
            log_calls = [call.args[0] for call in mock_logger.warning.call_args_list]
            difference_logs = [log for log in log_calls if "difference" in log.lower()]

            self.assertEqual(len(difference_logs), 0)


class TestPerformanceMonitoring(unittest.TestCase):
    """Testes para monitoramento de performance."""

    def setUp(self):
        """Configuração inicial dos testes."""

        self.legacy_service = MockLegacyService(delay=0.1)  # 100ms
        self.new_query = MockNewArchitectureQuery(delay=0.05)  # 50ms

        self.config = RefactoringConfig(
            phase=RefactoringPhase.VALIDATION,
            validation_sampling=1.0,
            log_performance_comparison=True,
        )

        self.service = ProgressiveRefactoringService(
            config=self.config,
            legacy_service=self.legacy_service,
            general_query=self.new_query,
            technician_query=self.new_query,
            dashboard_query=self.new_query,
        )

    @patch("core.application.services.progressive_refactoring_service.logger")
    def test_performance_comparison_logging(self, mock_logger):
        """Testa logging de comparação de performance."""

        # Executar
        result = asyncio.run(self.service.get_dashboard_metrics({}))

        # Verificar que performance foi logada
        log_calls = [call.args[0] for call in mock_logger.info.call_args_list]
        performance_logs = [log for log in log_calls if "performance" in log.lower()]

        self.assertTrue(len(performance_logs) > 0)


class TestEndpointSpecificMigration(unittest.TestCase):
    """Testes para migração específica por endpoint."""

    def setUp(self):
        """Configuração inicial dos testes."""

        self.legacy_service = MockLegacyService()
        self.new_query = MockNewArchitectureQuery()

        self.config = RefactoringConfig(
            phase=RefactoringPhase.STRANGLER_FIG,
            migration_percentage=0.0,  # 0% global
            endpoints_to_migrate=["/api/metrics"],  # Apenas este endpoint
        )

        self.service = ProgressiveRefactoringService(
            config=self.config,
            legacy_service=self.legacy_service,
            general_query=self.new_query,
            technician_query=self.new_query,
            dashboard_query=self.new_query,
        )

    def test_endpoint_specific_migration(self):
        """Testa migração específica por endpoint."""

        # Simular requisição para endpoint migrado
        with patch("flask.request") as mock_request:
            mock_request.path = "/api/metrics"

            # Executar
            result = asyncio.run(self.service.get_dashboard_metrics({}))

            # Verificar que nova arquitetura foi usada
            self.assertEqual(result["metadata"]["source"], "new_architecture")

    def test_non_migrated_endpoint_uses_legacy(self):
        """Testa que endpoints não migrados usam sistema legado."""

        # Simular requisição para endpoint não migrado
        with patch("flask.request") as mock_request:
            mock_request.path = "/api/other"

            # Executar
            result = asyncio.run(self.service.get_dashboard_metrics({}))

            # Verificar que sistema legado foi usado
            self.assertEqual(result["source"], "legacy")


class TestConfigurationValidation(unittest.TestCase):
    """Testes para validação de configuração."""

    def test_invalid_migration_percentage(self):
        """Testa validação de percentual de migração inválido."""

        with self.assertRaises(ValueError):
            RefactoringConfig(
                phase=RefactoringPhase.STRANGLER_FIG,
                migration_percentage=1.5,  # Inválido
            )

        with self.assertRaises(ValueError):
            RefactoringConfig(
                phase=RefactoringPhase.STRANGLER_FIG,
                migration_percentage=-0.1,  # Inválido
            )

    def test_invalid_validation_sampling(self):
        """Testa validação de sampling inválido."""

        with self.assertRaises(ValueError):
            RefactoringConfig(phase=RefactoringPhase.VALIDATION, validation_sampling=2.0)  # Inválido

    def test_invalid_timeout(self):
        """Testa validação de timeout inválido."""

        with self.assertRaises(ValueError):
            RefactoringConfig(
                phase=RefactoringPhase.NEW_ARCHITECTURE,
                fallback_timeout_ms=-100,  # Inválido
            )


if __name__ == "__main__":
    # Configurar logging para testes
    import logging

    logging.basicConfig(level=logging.DEBUG)

    # Executar testes
    unittest.main(verbosity=2)
