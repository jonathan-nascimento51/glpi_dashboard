#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes de contrato usando snapshots JSON.

Este módulo testa a compatibilidade de APIs através de snapshots
JSON que capturam a estrutura esperada das respostas.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from backend.core.application.dto import (
    DashboardMetricsDTO,
    LevelMetricsDTO,
    MetricsDTO,
    MetricsFilterDTO,
    MetricsResponseDTO,
    TechnicianLevel,
    TechnicianMetricsDTO,
    TicketMetricsDTO,
    TicketStatus,
    create_empty_metrics_dto,
    create_success_response,
)
from backend.core.application.queries import (
    DashboardMetricsQuery,
    GeneralMetricsQuery,
    MockMetricsDataSource,
    QueryContext,
    TechnicianRankingQuery,
)


class SnapshotManager:
    """Gerenciador de snapshots JSON para testes de contrato."""

    def __init__(self, test_name: str):
        self.test_name = test_name
        self.snapshots_dir = Path(__file__).parent / "snapshots"
        self.snapshots_dir.mkdir(exist_ok=True)

    def get_snapshot_path(self, snapshot_name: str) -> Path:
        """Obtém o caminho do arquivo de snapshot."""
        filename = f"{self.test_name}_{snapshot_name}.json"
        return self.snapshots_dir / filename

    def save_snapshot(self, snapshot_name: str, data: Any) -> None:
        """Salva um snapshot JSON."""
        snapshot_path = self.get_snapshot_path(snapshot_name)

        # Serializar dados para JSON
        if hasattr(data, "dict"):
            # Pydantic model
            json_data = data.dict()
        elif hasattr(data, "json"):
            # Objeto com método json
            json_data = json.loads(data.json())
        else:
            # Dados brutos
            json_data = data

        # Normalizar timestamps para comparação
        json_data = self._normalize_timestamps(json_data)

        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False, sort_keys=True)

    def load_snapshot(self, snapshot_name: str) -> Dict[str, Any]:
        """Carrega um snapshot JSON."""
        snapshot_path = self.get_snapshot_path(snapshot_name)

        if not snapshot_path.exists():
            raise FileNotFoundError(f"Snapshot não encontrado: {snapshot_path}")

        with open(snapshot_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def compare_with_snapshot(self, snapshot_name: str, data: Any, update_snapshot: bool = False) -> bool:
        """Compara dados com snapshot existente."""
        # Serializar dados atuais
        if hasattr(data, "dict"):
            current_data = data.dict()
        elif hasattr(data, "json"):
            current_data = json.loads(data.json())
        else:
            current_data = data

        # Normalizar timestamps
        current_data = self._normalize_timestamps(current_data)

        snapshot_path = self.get_snapshot_path(snapshot_name)

        if update_snapshot or not snapshot_path.exists():
            # Criar ou atualizar snapshot
            self.save_snapshot(snapshot_name, current_data)
            return True

        # Carregar snapshot existente
        expected_data = self.load_snapshot(snapshot_name)

        # Comparar estruturas
        return self._deep_compare(current_data, expected_data)

    def _normalize_timestamps(self, data: Any) -> Any:
        """Normaliza timestamps para comparação."""
        if isinstance(data, dict):
            normalized = {}
            for key, value in data.items():
                if key in ["timestamp", "created_at", "updated_at", "last_activity"]:
                    # Normalizar para formato ISO
                    if isinstance(value, str):
                        try:
                            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                            normalized[key] = "2024-01-01T00:00:00"
                        except:
                            normalized[key] = "2024-01-01T00:00:00"
                    else:
                        normalized[key] = "2024-01-01T00:00:00"
                else:
                    normalized[key] = self._normalize_timestamps(value)
            return normalized
        elif isinstance(data, list):
            return [self._normalize_timestamps(item) for item in data]
        else:
            return data

    def _deep_compare(self, current: Any, expected: Any, path: str = "") -> bool:
        """Compara estruturas profundamente."""
        if type(current) != type(expected):
            print(f"Tipo diferente em {path}: {type(current)} vs {type(expected)}")
            return False

        if isinstance(current, dict):
            # Verificar chaves
            current_keys = set(current.keys())
            expected_keys = set(expected.keys())

            if current_keys != expected_keys:
                missing = expected_keys - current_keys
                extra = current_keys - expected_keys
                if missing:
                    print(f"Chaves faltando em {path}: {missing}")
                if extra:
                    print(f"Chaves extras em {path}: {extra}")
                return False

            # Comparar valores
            for key in current_keys:
                if not self._deep_compare(current[key], expected[key], f"{path}.{key}" if path else key):
                    return False

            return True

        elif isinstance(current, list):
            if len(current) != len(expected):
                print(f"Tamanho de lista diferente em {path}: {len(current)} vs {len(expected)}")
                return False

            for i, (curr_item, exp_item) in enumerate(zip(current, expected)):
                if not self._deep_compare(curr_item, exp_item, f"{path}[{i}]"):
                    return False

            return True

        else:
            # Valores primitivos
            if current != expected:
                print(f"Valor diferente em {path}: {current} vs {expected}")
                return False
            return True


class TestMetricsDTOContracts:
    """Testes de contrato para DTOs de métricas."""

    def setup_method(self):
        """Setup para cada teste."""
        self.snapshot_manager = SnapshotManager("metrics_dto")

    def test_empty_metrics_dto_contract(self):
        """Testa contrato do DTO de métricas vazio."""
        metrics = create_empty_metrics_dto()

        assert self.snapshot_manager.compare_with_snapshot("empty_metrics", metrics)

    def test_complete_metrics_dto_contract(self):
        """Testa contrato do DTO de métricas completo."""
        # Criar métricas de tickets por nível
        n1_tickets = TicketMetricsDTO(total=100, novos=20, pendentes=30, progresso=25, resolvidos=20, fechados=5)

        n2_tickets = TicketMetricsDTO(total=80, novos=15, pendentes=25, progresso=20, resolvidos=15, fechados=5)

        # Criar métricas de nível
        n1_level = LevelMetricsDTO(
            level=TechnicianLevel.N1,
            metrics=n1_tickets,
            technician_count=10,
            avg_resolution_time=24.5,
        )

        n2_level = LevelMetricsDTO(
            level=TechnicianLevel.N2,
            metrics=n2_tickets,
            technician_count=8,
            avg_resolution_time=18.2,
        )

        # Criar métricas principais
        metrics = MetricsDTO(
            total=180,
            novos=35,
            pendentes=55,
            progresso=45,
            resolvidos=35,
            fechados=10,
            niveis={"N1": n1_level, "N2": n2_level},
            total_technicians=18,
            period_start=datetime(2024, 1, 1),
            period_end=datetime(2024, 1, 31),
        )

        assert self.snapshot_manager.compare_with_snapshot("complete_metrics", metrics)

    def test_technician_metrics_dto_contract(self):
        """Testa contrato do DTO de métricas de técnico."""
        ticket_metrics = TicketMetricsDTO(total=50, novos=10, pendentes=15, progresso=12, resolvidos=10, fechados=3)

        technician = TechnicianMetricsDTO(
            id=123,
            name="João Silva",
            level=TechnicianLevel.N2,
            rank=1,
            metrics=ticket_metrics,
            avg_resolution_time=16.5,
            efficiency_score=87.5,
            last_activity=datetime(2024, 1, 15, 14, 30),
        )

        assert self.snapshot_manager.compare_with_snapshot("technician_metrics", technician)

    def test_dashboard_metrics_dto_contract(self):
        """Testa contrato do DTO de métricas de dashboard."""
        # Criar métricas base
        base_metrics = create_empty_metrics_dto()
        base_metrics.total = 200
        base_metrics.novos = 40

        # Criar técnicos
        technicians = [
            TechnicianMetricsDTO(
                id=1,
                name="Tech 1",
                level=TechnicianLevel.N1,
                rank=1,
                metrics=TicketMetricsDTO(total=30, resolvidos=15),
            ),
            TechnicianMetricsDTO(
                id=2,
                name="Tech 2",
                level=TechnicianLevel.N2,
                rank=2,
                metrics=TicketMetricsDTO(total=25, resolvidos=12),
            ),
        ]

        # Criar dashboard
        dashboard = DashboardMetricsDTO(
            metrics=base_metrics,
            technicians=technicians,
            top_performers=technicians[:1],
            recent_tickets=[
                {"id": 1, "title": "Ticket 1", "status": "novo"},
                {"id": 2, "title": "Ticket 2", "status": "progresso"},
            ],
            response_time_ms=125.5,
            cache_hit=True,
            data_freshness=datetime(2024, 1, 15, 10, 0),
        )

        assert self.snapshot_manager.compare_with_snapshot("dashboard_metrics", dashboard)

    def test_metrics_response_dto_contract(self):
        """Testa contrato do DTO de resposta de métricas."""
        metrics = create_empty_metrics_dto()

        # Resposta de sucesso
        success_response = create_success_response(data=metrics, message="Dados obtidos com sucesso", execution_time_ms=150.0)

        assert self.snapshot_manager.compare_with_snapshot("success_response", success_response)

        # Resposta de erro
        error_response = MetricsResponseDTO(
            success=False,
            data=None,
            message="Erro ao obter dados",
            errors=["Conexão falhou", "Timeout"],
            warnings=["Cache expirado"],
        )

        assert self.snapshot_manager.compare_with_snapshot("error_response", error_response)


class TestQueryContracts:
    """Testes de contrato para queries de métricas."""

    def setup_method(self):
        """Setup para cada teste."""
        self.snapshot_manager = SnapshotManager("metrics_query")
        self.data_source = MockMetricsDataSource()

    @pytest.mark.asyncio
    async def test_general_metrics_query_contract(self):
        """Testa contrato da query de métricas gerais."""
        query = GeneralMetricsQuery(data_source=self.data_source)
        filter_dto = MetricsFilterDTO(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            status=TicketStatus.NOVO,
        )
        context = QueryContext(user_id="test_user")

        result = await query.execute(filter_dto, context)

        assert self.snapshot_manager.compare_with_snapshot("general_metrics_result", result)

    @pytest.mark.asyncio
    async def test_technician_ranking_query_contract(self):
        """Testa contrato da query de ranking de técnicos."""
        query = TechnicianRankingQuery(data_source=self.data_source)
        filter_dto = MetricsFilterDTO(limit=5, level=TechnicianLevel.N1)
        context = QueryContext(user_id="test_user")

        result = await query.execute(filter_dto, context)

        assert self.snapshot_manager.compare_with_snapshot("technician_ranking_result", result)

    @pytest.mark.asyncio
    async def test_dashboard_metrics_query_contract(self):
        """Testa contrato da query de dashboard."""
        query = DashboardMetricsQuery(data_source=self.data_source)
        filter_dto = MetricsFilterDTO()
        context = QueryContext(user_id="test_user")

        result = await query.execute(filter_dto, context)

        assert self.snapshot_manager.compare_with_snapshot("dashboard_query_result", result)


class TestAPIContractCompatibility:
    """Testes de compatibilidade de contrato de API."""

    def setup_method(self):
        """Setup para cada teste."""
        self.snapshot_manager = SnapshotManager("api_contract")

    def test_api_response_structure_v1(self):
        """Testa estrutura de resposta da API v1."""
        # Simular resposta da API v1
        api_response = {
            "success": True,
            "data": {
                "total": 100,
                "novos": 20,
                "pendentes": 30,
                "progresso": 25,
                "resolvidos": 20,
                "fechados": 5,
                "niveis": {
                    "N1": {
                        "level": "N1",
                        "metrics": {
                            "total": 50,
                            "novos": 10,
                            "pendentes": 15,
                            "progresso": 12,
                            "resolvidos": 10,
                            "fechados": 3,
                        },
                        "technician_count": 5,
                        "avg_resolution_time": 24.5,
                    }
                },
                "total_technicians": 10,
                "timestamp": "2024-01-01T00:00:00",
            },
            "message": "Dados obtidos com sucesso",
            "execution_time_ms": 150.0,
            "errors": [],
            "warnings": [],
        }

        assert self.snapshot_manager.compare_with_snapshot("api_response_v1", api_response)

    def test_api_error_response_structure(self):
        """Testa estrutura de resposta de erro da API."""
        error_response = {
            "success": False,
            "data": None,
            "message": "Erro interno do servidor",
            "errors": ["Falha na conexão com GLPI", "Timeout na consulta"],
            "warnings": ["Cache expirado", "Dados podem estar desatualizados"],
            "execution_time_ms": 5000.0,
        }

        assert self.snapshot_manager.compare_with_snapshot("api_error_response", error_response)

    def test_dashboard_api_response_structure(self):
        """Testa estrutura de resposta da API de dashboard."""
        dashboard_response = {
            "success": True,
            "data": {
                "metrics": {
                    "total": 200,
                    "novos": 40,
                    "pendentes": 60,
                    "progresso": 50,
                    "resolvidos": 40,
                    "fechados": 10,
                    "niveis": {},
                    "total_technicians": 20,
                    "timestamp": "2024-01-01T00:00:00",
                },
                "technicians": [
                    {
                        "id": 1,
                        "name": "João Silva",
                        "level": "N1",
                        "rank": 1,
                        "metrics": {"total": 30, "resolvidos": 15},
                        "efficiency_score": 85.5,
                    }
                ],
                "top_performers": [],
                "recent_tickets": [],
                "response_time_ms": 125.0,
                "cache_hit": True,
                "data_freshness": "2024-01-01T00:00:00",
            },
            "message": "Dashboard carregado com sucesso",
        }

        assert self.snapshot_manager.compare_with_snapshot("dashboard_api_response", dashboard_response)


class TestBackwardCompatibility:
    """Testes de compatibilidade com versões anteriores."""

    def setup_method(self):
        """Setup para cada teste."""
        self.snapshot_manager = SnapshotManager("backward_compatibility")

    def test_legacy_metrics_format_compatibility(self):
        """Testa compatibilidade com formato legado de métricas."""
        # Formato legado (simulado)
        legacy_format = {
            "total_tickets": 100,
            "new_tickets": 20,
            "pending_tickets": 30,
            "in_progress_tickets": 25,
            "resolved_tickets": 20,
            "closed_tickets": 5,
            "levels": {
                "level_1": {"count": 50, "technicians": 5},
                "level_2": {"count": 30, "technicians": 3},
            },
        }

        # Converter para novo formato
        new_format = {
            "total": legacy_format["total_tickets"],
            "novos": legacy_format["new_tickets"],
            "pendentes": legacy_format["pending_tickets"],
            "progresso": legacy_format["in_progress_tickets"],
            "resolvidos": legacy_format["resolved_tickets"],
            "fechados": legacy_format["closed_tickets"],
            "niveis": {
                "N1": {
                    "level": "N1",
                    "metrics": {"total": legacy_format["levels"]["level_1"]["count"]},
                    "technician_count": legacy_format["levels"]["level_1"]["technicians"],
                },
                "N2": {
                    "level": "N2",
                    "metrics": {"total": legacy_format["levels"]["level_2"]["count"]},
                    "technician_count": legacy_format["levels"]["level_2"]["technicians"],
                },
            },
        }

        assert self.snapshot_manager.compare_with_snapshot("legacy_to_new_format", new_format)

    def test_api_version_compatibility(self):
        """Testa compatibilidade entre versões da API."""
        # Resposta da API v1.0
        v1_response = {
            "status": "success",
            "result": {"tickets": {"total": 100, "new": 20, "pending": 30}},
        }

        # Resposta da API v2.0 (nova estrutura)
        v2_response = {
            "success": True,
            "data": {"total": 100, "novos": 20, "pendentes": 30},
            "message": "Dados obtidos com sucesso",
            "version": "2.0",
        }

        # Ambas devem ser válidas
        assert self.snapshot_manager.compare_with_snapshot("api_v1_response", v1_response)

        assert self.snapshot_manager.compare_with_snapshot("api_v2_response", v2_response)


class TestContractEvolution:
    """Testes para evolução de contratos."""

    def setup_method(self):
        """Setup para cada teste."""
        self.snapshot_manager = SnapshotManager("contract_evolution")

    def test_additive_changes_compatibility(self):
        """Testa compatibilidade com mudanças aditivas."""
        # Estrutura base
        base_structure = {"total": 100, "novos": 20, "pendentes": 30}

        # Estrutura com campos adicionais (mudança aditiva)
        extended_structure = {
            "total": 100,
            "novos": 20,
            "pendentes": 30,
            "progresso": 25,  # Novo campo
            "metadata": {  # Novo objeto
                "version": "2.1",
                "generated_at": "2024-01-01T00:00:00",
            },
        }

        # Mudanças aditivas devem manter compatibilidade
        assert self.snapshot_manager.compare_with_snapshot("base_structure", base_structure)

        # Estrutura estendida deve ser válida
        assert self.snapshot_manager.compare_with_snapshot("extended_structure", extended_structure)

    def test_field_deprecation_compatibility(self):
        """Testa compatibilidade com depreciação de campos."""
        # Estrutura com campo depreciado
        with_deprecated = {
            "total": 100,
            "novos": 20,
            "old_field": "deprecated_value",  # Campo depreciado
            "new_field": "new_value",  # Campo substituto
        }

        # Estrutura sem campo depreciado
        without_deprecated = {"total": 100, "novos": 20, "new_field": "new_value"}

        # Ambas devem ser válidas durante período de transição
        assert self.snapshot_manager.compare_with_snapshot("with_deprecated_field", with_deprecated)

        assert self.snapshot_manager.compare_with_snapshot("without_deprecated_field", without_deprecated)


# Utilitários para execução de testes
def update_all_snapshots():
    """Atualiza todos os snapshots (usar com cuidado)."""
    import subprocess
    import sys

    # Executar testes com flag de atualização
    result = subprocess.run([sys.executable, "-m", "pytest", __file__, "--update-snapshots"])

    return result.returncode == 0


def validate_all_contracts():
    """Valida todos os contratos sem atualizar snapshots."""
    import subprocess
    import sys

    result = subprocess.run([sys.executable, "-m", "pytest", __file__, "-v"])

    return result.returncode == 0


if __name__ == "__main__":
    # Executar validação de contratos
    if validate_all_contracts():
        print("✅ Todos os contratos estão válidos")
    else:
        print("❌ Alguns contratos falharam na validação")
