#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes unitários para DTOs de métricas.

Este módulo testa validação, serialização, factory functions e
comportamentos dos DTOs de métricas.
"""

import json
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict

import pytest
from pydantic import ValidationError

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
    create_error_response,
    create_success_response,
)


class TestTicketStatus:
    """Testes para enum TicketStatus."""

    def test_ticket_status_values(self):
        """Testa valores do enum TicketStatus."""
        assert TicketStatus.NOVO == "novo"
        assert TicketStatus.PENDENTE == "pendente"
        assert TicketStatus.PROGRESSO == "progresso"
        assert TicketStatus.RESOLVIDO == "resolvido"
        assert TicketStatus.FECHADO == "fechado"
        assert TicketStatus.CANCELADO == "cancelado"

    def test_ticket_status_iteration(self):
        """Testa iteração sobre valores do enum."""
        statuses = list(TicketStatus)
        assert len(statuses) == 6
        assert TicketStatus.NOVO in statuses


class TestTechnicianLevel:
    """Testes para enum TechnicianLevel."""

    def test_technician_level_values(self):
        """Testa valores do enum TechnicianLevel."""
        assert TechnicianLevel.N1 == "N1"
        assert TechnicianLevel.N2 == "N2"
        assert TechnicianLevel.N3 == "N3"
        assert TechnicianLevel.N4 == "N4"
        assert TechnicianLevel.UNKNOWN == "UNKNOWN"

    def test_technician_level_iteration(self):
        """Testa iteração sobre valores do enum."""
        levels = list(TechnicianLevel)
        assert len(levels) == 5
        assert TechnicianLevel.N1 in levels


class TestMetricsFilterDTO:
    """Testes para MetricsFilterDTO."""

    def test_empty_filter_creation(self):
        """Testa criação de filtro vazio."""
        filter_dto = MetricsFilterDTO()
        assert filter_dto.start_date is None
        assert filter_dto.end_date is None
        assert filter_dto.status is None
        assert filter_dto.level is None
        assert filter_dto.offset == 0

    def test_filter_with_valid_dates(self):
        """Testa filtro com datas válidas."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)

        filter_dto = MetricsFilterDTO(start_date=start_date, end_date=end_date)

        assert filter_dto.start_date == start_date
        assert filter_dto.end_date == end_date

    def test_filter_with_invalid_dates(self):
        """Testa filtro com datas inválidas."""
        start_date = datetime(2024, 1, 31)
        end_date = datetime(2024, 1, 1)  # Anterior ao start_date

        with pytest.raises(ValidationError) as exc_info:
            MetricsFilterDTO(start_date=start_date, end_date=end_date)

        assert "end_date deve ser posterior a start_date" in str(exc_info.value)

    def test_filter_with_enum_values(self):
        """Testa filtro com valores de enum."""
        filter_dto = MetricsFilterDTO(status=TicketStatus.NOVO, level=TechnicianLevel.N1)

        assert filter_dto.status == TicketStatus.NOVO
        assert filter_dto.level == TechnicianLevel.N1

    def test_filter_priority_validation(self):
        """Testa validação de prioridade."""
        # Prioridade válida
        filter_dto = MetricsFilterDTO(priority=3)
        assert filter_dto.priority == 3

        # Prioridade inválida (muito baixa)
        with pytest.raises(ValidationError):
            MetricsFilterDTO(priority=0)

        # Prioridade inválida (muito alta)
        with pytest.raises(ValidationError):
            MetricsFilterDTO(priority=7)

    def test_filter_json_serialization(self):
        """Testa serialização JSON do filtro."""
        start_date = datetime(2024, 1, 1, 10, 30, 0)
        filter_dto = MetricsFilterDTO(
            start_date=start_date,
            status=TicketStatus.NOVO,
            level=TechnicianLevel.N1,
            priority=2,
        )

        json_data = filter_dto.json()
        parsed_data = json.loads(json_data)

        assert parsed_data["start_date"] == start_date.isoformat()
        assert parsed_data["status"] == "novo"
        assert parsed_data["level"] == "N1"
        assert parsed_data["priority"] == 2


class TestTicketMetricsDTO:
    """Testes para TicketMetricsDTO."""

    def test_empty_ticket_metrics(self):
        """Testa criação de métricas vazias."""
        metrics = TicketMetricsDTO()
        assert metrics.total == 0
        assert metrics.novos == 0
        assert metrics.pendentes == 0
        assert metrics.progresso == 0
        assert metrics.resolvidos == 0
        assert metrics.fechados == 0
        assert metrics.cancelados == 0

    def test_ticket_metrics_with_values(self):
        """Testa criação de métricas com valores."""
        metrics = TicketMetricsDTO(total=100, novos=20, pendentes=30, progresso=25, resolvidos=20, fechados=5)

        assert metrics.total == 100
        assert metrics.novos == 20
        assert metrics.pendentes == 30
        assert metrics.progresso == 25
        assert metrics.resolvidos == 20
        assert metrics.fechados == 5
        assert metrics.cancelados == 0  # Valor padrão

    def test_negative_values_validation(self):
        """Testa validação de valores negativos."""
        with pytest.raises(ValidationError):
            TicketMetricsDTO(total=-1)

        with pytest.raises(ValidationError):
            TicketMetricsDTO(novos=-5)

    def test_ticket_metrics_calculations(self):
        """Testa cálculos de métricas."""
        metrics = TicketMetricsDTO(total=100, novos=20, pendentes=30, progresso=25, resolvidos=20, fechados=5)

        # Testa método de cálculo de percentual
        assert metrics.get_resolution_rate() == 20.0  # 20/100 * 100
        assert metrics.get_pending_rate() == 30.0  # 30/100 * 100

        # Testa método de status ativo
        assert metrics.get_active_tickets() == 75  # novos + pendentes + progresso

    def test_zero_total_calculations(self):
        """Testa cálculos com total zero."""
        metrics = TicketMetricsDTO(total=0)

        # Deve retornar 0.0 para evitar divisão por zero
        assert metrics.get_resolution_rate() == 0.0
        assert metrics.get_pending_rate() == 0.0
        assert metrics.get_active_tickets() == 0


class TestLevelMetricsDTO:
    """Testes para LevelMetricsDTO."""

    def test_level_metrics_creation(self):
        """Testa criação de métricas de nível."""
        ticket_metrics = TicketMetricsDTO(total=50, novos=10, resolvidos=15)

        level_metrics = LevelMetricsDTO(
            level=TechnicianLevel.N1,
            metrics=ticket_metrics,
            technician_count=5,
            avg_resolution_time=24.5,
        )

        assert level_metrics.level == TechnicianLevel.N1
        assert level_metrics.metrics.total == 50
        assert level_metrics.technician_count == 5
        assert level_metrics.avg_resolution_time == 24.5

    def test_level_metrics_json_serialization(self):
        """Testa serialização JSON de métricas de nível."""
        ticket_metrics = TicketMetricsDTO(total=30)
        level_metrics = LevelMetricsDTO(level=TechnicianLevel.N2, metrics=ticket_metrics, technician_count=3)

        json_data = level_metrics.json()
        parsed_data = json.loads(json_data)

        assert parsed_data["level"] == "N2"
        assert parsed_data["metrics"]["total"] == 30
        assert parsed_data["technician_count"] == 3


class TestTechnicianMetricsDTO:
    """Testes para TechnicianMetricsDTO."""

    def test_technician_metrics_creation(self):
        """Testa criação de métricas de técnico."""
        ticket_metrics = TicketMetricsDTO(total=25, resolvidos=20)
        last_activity = datetime.now()

        tech_metrics = TechnicianMetricsDTO(
            id=123,
            name="João Silva",
            level=TechnicianLevel.N2,
            rank=1,
            metrics=ticket_metrics,
            avg_resolution_time=18.5,
            efficiency_score=85.5,
            last_activity=last_activity,
        )

        assert tech_metrics.id == 123
        assert tech_metrics.name == "João Silva"
        assert tech_metrics.level == TechnicianLevel.N2
        assert tech_metrics.rank == 1
        assert tech_metrics.efficiency_score == 85.5
        assert tech_metrics.last_activity == last_activity

    def test_technician_name_validation(self):
        """Testa validação do nome do técnico."""
        ticket_metrics = TicketMetricsDTO()

        # Nome vazio
        with pytest.raises(ValidationError):
            TechnicianMetricsDTO(id=1, name="", level=TechnicianLevel.N1, metrics=ticket_metrics)

        # Nome muito longo
        long_name = "a" * 256
        with pytest.raises(ValidationError):
            TechnicianMetricsDTO(id=1, name=long_name, level=TechnicianLevel.N1, metrics=ticket_metrics)

    def test_efficiency_score_validation(self):
        """Testa validação do score de eficiência."""
        ticket_metrics = TicketMetricsDTO()

        # Score válido
        tech_metrics = TechnicianMetricsDTO(
            id=1,
            name="Teste",
            level=TechnicianLevel.N1,
            metrics=ticket_metrics,
            efficiency_score=75.5,
        )
        assert tech_metrics.efficiency_score == 75.5

        # Score inválido (negativo)
        with pytest.raises(ValidationError):
            TechnicianMetricsDTO(
                id=1,
                name="Teste",
                level=TechnicianLevel.N1,
                metrics=ticket_metrics,
                efficiency_score=-1.0,
            )

        # Score inválido (maior que 100)
        with pytest.raises(ValidationError):
            TechnicianMetricsDTO(
                id=1,
                name="Teste",
                level=TechnicianLevel.N1,
                metrics=ticket_metrics,
                efficiency_score=101.0,
            )


class TestMetricsDTO:
    """Testes para MetricsDTO principal."""

    def test_empty_metrics_creation(self):
        """Testa criação de métricas vazias."""
        metrics = MetricsDTO()

        assert metrics.total == 0
        assert metrics.novos == 0
        assert metrics.pendentes == 0
        assert metrics.progresso == 0
        assert metrics.resolvidos == 0
        assert len(metrics.niveis) == 0
        assert metrics.total_technicians == 0
        assert isinstance(metrics.timestamp, datetime)

    def test_metrics_with_levels(self):
        """Testa métricas com níveis."""
        # Criar métricas de nível
        n1_metrics = LevelMetricsDTO(
            level=TechnicianLevel.N1,
            metrics=TicketMetricsDTO(total=30, novos=5, resolvidos=10),
            technician_count=3,
        )

        n2_metrics = LevelMetricsDTO(
            level=TechnicianLevel.N2,
            metrics=TicketMetricsDTO(total=20, novos=3, resolvidos=8),
            technician_count=2,
        )

        # Criar métricas principais
        metrics = MetricsDTO(
            total=50,
            novos=8,
            resolvidos=18,
            niveis={"N1": n1_metrics, "N2": n2_metrics},
            total_technicians=5,
        )

        assert metrics.total == 50
        assert metrics.novos == 8
        assert metrics.resolvidos == 18
        assert len(metrics.niveis) == 2
        assert "N1" in metrics.niveis
        assert "N2" in metrics.niveis
        assert metrics.total_technicians == 5

    def test_metrics_calculations(self):
        """Testa cálculos de métricas."""
        metrics = MetricsDTO(total=100, total_technicians=10)

        # Testa cálculo de média
        metrics.calculate_averages()
        assert metrics.avg_tickets_per_technician == 10.0

    def test_metrics_period_setting(self):
        """Testa definição de período."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)

        metrics = MetricsDTO(period_start=start_date, period_end=end_date)

        assert metrics.period_start == start_date
        assert metrics.period_end == end_date


class TestDashboardMetricsDTO:
    """Testes para DashboardMetricsDTO."""

    def test_dashboard_metrics_creation(self):
        """Testa criação de métricas de dashboard."""
        # Criar métricas base
        base_metrics = MetricsDTO(total=100, novos=20)

        # Criar técnicos
        tech1 = TechnicianMetricsDTO(
            id=1,
            name="Tech 1",
            level=TechnicianLevel.N1,
            metrics=TicketMetricsDTO(total=30),
        )

        tech2 = TechnicianMetricsDTO(
            id=2,
            name="Tech 2",
            level=TechnicianLevel.N2,
            metrics=TicketMetricsDTO(total=25),
        )

        # Criar dashboard
        dashboard = DashboardMetricsDTO(
            metrics=base_metrics,
            technicians=[tech1, tech2],
            top_performers=[tech1],
            recent_tickets=[{"id": 1, "title": "Ticket 1"}],
            response_time_ms=150.5,
            cache_hit=True,
        )

        assert dashboard.metrics.total == 100
        assert len(dashboard.technicians) == 2
        assert len(dashboard.top_performers) == 1
        assert len(dashboard.recent_tickets) == 1
        assert dashboard.response_time_ms == 150.5
        assert dashboard.cache_hit is True

    def test_performance_summary(self):
        """Testa resumo de performance."""
        base_metrics = MetricsDTO()
        data_freshness = datetime.now()

        dashboard = DashboardMetricsDTO(
            metrics=base_metrics,
            response_time_ms=200.0,
            cache_hit=False,
            data_freshness=data_freshness,
        )

        summary = dashboard.get_performance_summary()

        assert summary["response_time_ms"] == 200.0
        assert summary["cache_hit"] is False
        assert summary["data_freshness"] == data_freshness.isoformat()
        assert summary["total_technicians"] == 0
        assert summary["top_performers_count"] == 0
        assert summary["recent_tickets_count"] == 0


class TestMetricsResponseDTO:
    """Testes para MetricsResponseDTO."""

    def test_success_response(self):
        """Testa resposta de sucesso."""
        metrics = MetricsDTO(total=50)

        response = MetricsResponseDTO(
            success=True,
            data=metrics,
            message="Dados obtidos com sucesso",
            execution_time_ms=125.5,
        )

        assert response.success is True
        assert response.data.total == 50
        assert response.message == "Dados obtidos com sucesso"
        assert response.execution_time_ms == 125.5
        assert len(response.errors) == 0
        assert len(response.warnings) == 0

    def test_error_response(self):
        """Testa resposta de erro."""
        response = MetricsResponseDTO(
            success=False,
            data=None,
            message="Erro ao obter dados",
            errors=["Conexão com GLPI falhou", "Timeout na consulta"],
            warnings=["Cache expirado"],
        )

        assert response.success is False
        assert response.data is None
        assert response.message == "Erro ao obter dados"
        assert len(response.errors) == 2
        assert len(response.warnings) == 1
        assert "Conexão com GLPI falhou" in response.errors

    def test_response_with_pagination(self):
        """Testa resposta com paginação."""
        pagination_info = {"page": 1, "per_page": 10, "total": 100, "pages": 10}

        response = MetricsResponseDTO(success=True, data=[], pagination=pagination_info)

        assert response.pagination["page"] == 1
        assert response.pagination["total"] == 100


class TestFactoryFunctions:
    """Testes para factory functions."""

    def test_create_empty_metrics_dto(self):
        """Testa criação de DTO vazio."""
        metrics = create_empty_metrics_dto()

        assert isinstance(metrics, MetricsDTO)
        assert metrics.total == 0
        assert metrics.novos == 0
        assert len(metrics.niveis) == 4  # N1, N2, N3, N4

        # Verifica se todos os níveis foram criados
        for level in ["N1", "N2", "N3", "N4"]:
            assert level in metrics.niveis
            assert metrics.niveis[level].technician_count == 0
            assert metrics.niveis[level].metrics.total == 0

    def test_create_error_response(self):
        """Testa criação de resposta de erro."""
        error_msg = "Erro de conexão"
        errors = ["Timeout", "Network error"]

        response = create_error_response(error_msg, errors)

        assert isinstance(response, MetricsResponseDTO)
        assert response.success is False
        assert response.message == error_msg
        assert response.errors == errors
        assert response.data is None

    def test_create_success_response(self):
        """Testa criação de resposta de sucesso."""
        metrics = MetricsDTO(total=100)
        message = "Dados obtidos"
        execution_time = 150.0

        response = create_success_response(data=metrics, message=message, execution_time_ms=execution_time)

        assert isinstance(response, MetricsResponseDTO)
        assert response.success is True
        assert response.data == metrics
        assert response.message == message
        assert response.execution_time_ms == execution_time
        assert len(response.errors) == 0


class TestDTOIntegration:
    """Testes de integração entre DTOs."""

    def test_complete_metrics_flow(self):
        """Testa fluxo completo de criação de métricas."""
        # 1. Criar métricas de tickets por nível
        n1_tickets = TicketMetricsDTO(total=50, novos=10, resolvidos=20)
        n2_tickets = TicketMetricsDTO(total=30, novos=5, resolvidos=15)

        # 2. Criar métricas de nível
        n1_level = LevelMetricsDTO(level=TechnicianLevel.N1, metrics=n1_tickets, technician_count=5)

        n2_level = LevelMetricsDTO(level=TechnicianLevel.N2, metrics=n2_tickets, technician_count=3)

        # 3. Criar métricas principais
        main_metrics = MetricsDTO(
            total=80,
            novos=15,
            resolvidos=35,
            niveis={"N1": n1_level, "N2": n2_level},
            total_technicians=8,
        )

        # 4. Criar técnicos
        technicians = [
            TechnicianMetricsDTO(
                id=1,
                name="Tech 1",
                level=TechnicianLevel.N1,
                metrics=TicketMetricsDTO(total=25, resolvidos=12),
            ),
            TechnicianMetricsDTO(
                id=2,
                name="Tech 2",
                level=TechnicianLevel.N2,
                metrics=TicketMetricsDTO(total=20, resolvidos=10),
            ),
        ]

        # 5. Criar dashboard
        dashboard = DashboardMetricsDTO(
            metrics=main_metrics,
            technicians=technicians,
            top_performers=technicians[:1],
        )

        # 6. Criar resposta final
        response = create_success_response(data=dashboard, message="Dashboard criado com sucesso")

        # Verificações
        assert response.success is True
        assert isinstance(response.data, DashboardMetricsDTO)
        assert response.data.metrics.total == 80
        assert len(response.data.technicians) == 2
        assert len(response.data.top_performers) == 1

    def test_json_serialization_roundtrip(self):
        """Testa serialização e deserialização JSON completa."""
        # Criar estrutura completa
        metrics = create_empty_metrics_dto()
        metrics.total = 100
        metrics.novos = 20

        # Serializar para JSON
        json_str = metrics.json()

        # Deserializar de volta
        json_data = json.loads(json_str)
        reconstructed = MetricsDTO(**json_data)

        # Verificar se os dados são iguais
        assert reconstructed.total == metrics.total
        assert reconstructed.novos == metrics.novos
        assert len(reconstructed.niveis) == len(metrics.niveis)

    def test_dto_validation_chain(self):
        """Testa cadeia de validação entre DTOs."""
        # Dados inválidos devem falhar em qualquer nível

        # 1. Ticket metrics inválido
        with pytest.raises(ValidationError):
            TicketMetricsDTO(total=-1)

        # 2. Level metrics com ticket inválido
        with pytest.raises(ValidationError):
            LevelMetricsDTO(
                level=TechnicianLevel.N1,
                metrics=TicketMetricsDTO(total=-1),
                technician_count=1,
            )

        # 3. Technician metrics com dados inválidos
        with pytest.raises(ValidationError):
            TechnicianMetricsDTO(
                id=0,  # ID inválido
                name="Test",
                level=TechnicianLevel.N1,
                metrics=TicketMetricsDTO(),
            )
