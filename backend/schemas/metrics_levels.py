# -*- coding: utf-8 -*-
"""Schemas para métricas consolidadas por nível"""

from datetime import date
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class StatusFilter(str, Enum):
    """Filtros de status disponíveis"""

    OPEN = "open"
    CLOSED = "closed"
    PENDING = "pending"
    ALL = "all"


class ServiceLevel(str, Enum):
    """Níveis de serviço disponíveis"""

    N1 = "n1"
    N2 = "n2"
    N3 = "n3"
    N4 = "n4"
    ALL = "all"


class MetricsLevelsQueryParams(BaseModel):
    """Parâmetros de consulta para métricas por nível"""

    start_date: Optional[date] = Field(None, description="Data de início (YYYY-MM-DD)")
    end_date: Optional[date] = Field(None, description="Data de fim (YYYY-MM-DD)")
    status: StatusFilter = Field(StatusFilter.ALL, description="Filtro por status")
    levels: List[ServiceLevel] = Field(
        [ServiceLevel.ALL], description="Níveis de serviço"
    )
    include_anomalies: bool = Field(True, description="Incluir detecção de anomalias")
    zscore_threshold: float = Field(
        2.0, description="Limite para detecção de anomalias (z-score)"
    )


class MetricsByLevel(BaseModel):
    """Métricas por nível de serviço"""

    level: ServiceLevel
    total_tickets: int
    open_tickets: int
    closed_tickets: int
    pending_tickets: int
    avg_resolution_time_hours: float
    sla_compliance_rate: float
    is_anomaly: bool = False
    anomaly_score: Optional[float] = None


class AggregatedMetrics(BaseModel):
    """Métricas agregadas consolidadas"""

    total_tickets_all_levels: int
    avg_resolution_time_all_levels: float
    overall_sla_compliance: float
    anomalies_detected: int
    performance_trend: str  # "improving", "stable", "declining"


class MetricsLevelsResponse(BaseModel):
    """Resposta do endpoint de métricas por nível"""

    metrics_by_level: List[MetricsByLevel]
    aggregated_metrics: AggregatedMetrics
    metadata: dict
    period_analyzed: dict
