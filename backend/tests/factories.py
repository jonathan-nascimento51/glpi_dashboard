# -*- coding: utf-8 -*-
"""Factories para criação de dados de teste usando factory_boy."""

import factory
from datetime import datetime, timedelta, timezone
from factory import Faker, SubFactory, LazyAttribute
from factory.fuzzy import FuzzyChoice, FuzzyInteger, FuzzyDateTime

from domain.entities.ticket import Ticket, TicketStatus, TicketPriority
from domain.entities.dashboard_metrics import (
    LevelMetrics,
    TechnicianRanking,
    TrendData,
    DashboardMetrics,
)


class TicketFactory(factory.Factory):
    """Factory para criação de tickets de teste."""

    class Meta:
        model = Ticket

    id = FuzzyInteger(1, 10000)
    name = Faker("sentence", nb_words=4)
    status = FuzzyChoice(list(TicketStatus))
    priority = FuzzyChoice(list(TicketPriority))
    created_at = FuzzyDateTime(
        start_dt=datetime.now(timezone.utc) - timedelta(days=30),
        end_dt=datetime.now(timezone.utc),
    )
    updated_at = LazyAttribute(lambda obj: obj.created_at + timedelta(hours=2))
    assigned_group_id = FuzzyInteger(1, 50)
    assigned_user_id = FuzzyInteger(1, 100)
    resolved_at = None
    closed_at = None


class ResolvedTicketFactory(TicketFactory):
    """Factory para tickets resolvidos."""

    status = TicketStatus.SOLUCIONADO
    resolved_at = LazyAttribute(lambda obj: obj.created_at + timedelta(hours=24))


class LevelMetricsFactory(factory.Factory):
    """Factory para métricas por nível."""

    class Meta:
        model = LevelMetrics

    novos = FuzzyInteger(0, 50)
    progresso = FuzzyInteger(0, 30)
    pendentes = FuzzyInteger(0, 20)
    resolvidos = FuzzyInteger(10, 100)
    total = LazyAttribute(
        lambda obj: obj.novos + obj.progresso + obj.pendentes + obj.resolvidos
    )


class TechnicianRankingFactory(factory.Factory):
    """Factory para ranking de técnicos."""

    class Meta:
        model = TechnicianRanking

    name = Faker("name")
    resolved_tickets = FuzzyInteger(1, 50)
    avg_resolution_time = FuzzyInteger(1, 48)  # horas
    satisfaction_score = FuzzyInteger(1, 5)


class TrendDataFactory(factory.Factory):
    """Factory para dados de tendência."""

    class Meta:
        model = TrendData

    date = Faker("date_this_month")
    value = FuzzyInteger(0, 20)
    label = Faker("word")


class DashboardMetricsFactory(factory.Factory):
    """Factory para métricas do dashboard."""

    class Meta:
        model = DashboardMetrics

    niveis = factory.Dict(
        {
            "n1": SubFactory(LevelMetricsFactory),
            "n2": SubFactory(LevelMetricsFactory),
            "n3": SubFactory(LevelMetricsFactory),
            "n4": SubFactory(LevelMetricsFactory),
        }
    )
    technician_ranking = factory.List(
        [SubFactory(TechnicianRankingFactory) for _ in range(5)]
    )
    trends = factory.Dict(
        {"weekly": factory.List([SubFactory(TrendDataFactory) for _ in range(7)])}
    )
    system_status = "operational"
    last_updated = LazyAttribute(lambda obj: datetime.now(timezone.utc))
