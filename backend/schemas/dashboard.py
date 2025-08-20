from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class LevelMetrics(BaseModel):
    """Métricas de um nível específico (N1, N2, N3, N4)"""

    novos: int = Field(ge=0, description="Número de tickets novos")
    pendentes: int = Field(ge=0, description="Número de tickets pendentes")
    progresso: int = Field(ge=0, description="Número de tickets em progresso")
    resolvidos: int = Field(ge=0, description="Número de tickets resolvidos")


class NiveisMetrics(BaseModel):
    """Métricas de todos os níveis"""

    n1: LevelMetrics
    n2: LevelMetrics
    n3: LevelMetrics
    n4: LevelMetrics


class TendenciasMetrics(BaseModel):
    """Tendências das métricas"""

    novos: str = "0"
    pendentes: str = "0"
    progresso: str = "0"
    resolvidos: str = "0"


class FiltersApplied(BaseModel):
    """Filtros aplicados na consulta"""

    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    level: Optional[str] = None
    technician: Optional[str] = None
    category: Optional[str] = None


class DashboardMetrics(BaseModel):
    """Schema unificado para métricas do dashboard"""

    novos: int = Field(ge=0, description="Total de tickets novos")
    pendentes: int = Field(ge=0, description="Total de tickets pendentes")
    progresso: int = Field(ge=0, description="Total de tickets em progresso")
    resolvidos: int = Field(ge=0, description="Total de tickets resolvidos")
    total: int = Field(ge=0, description="Total geral de tickets")
    niveis: NiveisMetrics
    tendencias: TendenciasMetrics
    filters_applied: Optional[FiltersApplied] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class TechnicianRanking(BaseModel):
    """Ranking de técnico"""

    id: int
    name: str
    ticket_count: int = Field(ge=0)
    level: str
    performance_score: Optional[float] = None


class NewTicket(BaseModel):
    """Ticket novo"""

    id: str
    title: str
    description: str
    date: str
    requester: str
    priority: str
    status: str = "Novo"
    filters_applied: Optional[FiltersApplied] = None


class ApiResponse(BaseModel):
    """Schema padrão para respostas da API"""

    success: bool = True
    data: Any
    message: Optional[str] = None
    errors: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    execution_time_ms: Optional[float] = None


class ApiError(BaseModel):
    """Schema para erros da API"""

    success: bool = False
    data: None = None
    message: str
    errors: List[str]
    timestamp: datetime = Field(default_factory=datetime.now)
    error_code: Optional[str] = None
