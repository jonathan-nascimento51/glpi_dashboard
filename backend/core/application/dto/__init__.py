# -*- coding: utf-8 -*-
"""
Data Transfer Objects (DTOs) para a aplicação.

Este módulo centraliza todos os DTOs utilizados na aplicação,
fornecendo estruturas de dados padronizadas e validadas.
"""

from .metrics_dto import (
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

__all__ = [
    # Enums
    "TicketStatus",
    "TechnicianLevel",
    # DTOs principais
    "MetricsDTO",
    "LevelMetricsDTO",
    "TechnicianMetricsDTO",
    "TicketMetricsDTO",
    "DashboardMetricsDTO",
    "MetricsFilterDTO",
    "MetricsResponseDTO",
    # Factory functions
    "create_empty_metrics_dto",
    "create_error_response",
    "create_success_response",
]
