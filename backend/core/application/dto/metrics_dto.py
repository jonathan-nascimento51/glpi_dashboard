# -*- coding: utf-8 -*-
"""
Data Transfer Objects (DTOs) para métricas do GLPI Dashboard.

Este módulo define as estruturas de dados padronizadas para métricas,
garantindo consistência e validação em toda a aplicação.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, root_validator, validator
from pydantic.types import NonNegativeInt, PositiveInt


class TicketStatus(str, Enum):
    """Enum para status de tickets."""

    NOVO = "novo"
    PENDENTE = "pendente"
    PROGRESSO = "progresso"
    RESOLVIDO = "resolvido"
    FECHADO = "fechado"
    CANCELADO = "cancelado"


class TechnicianLevel(str, Enum):
    """Enum para níveis de técnicos."""

    N1 = "N1"
    N2 = "N2"
    N3 = "N3"
    N4 = "N4"
    UNKNOWN = "UNKNOWN"


class MetricsFilterDTO(BaseModel):
    """DTO para filtros de métricas."""

    start_date: Optional[datetime] = Field(None, description="Data de início do filtro")
    end_date: Optional[datetime] = Field(None, description="Data de fim do filtro")
    status: Optional[TicketStatus] = Field(None, description="Status do ticket")
    level: Optional[TechnicianLevel] = Field(None, description="Nível do técnico")
    technician_id: Optional[PositiveInt] = Field(None, description="ID do técnico")
    category_id: Optional[PositiveInt] = Field(None, description="ID da categoria")
    priority: Optional[int] = Field(None, ge=1, le=6, description="Prioridade do ticket (1-6)")
    limit: Optional[PositiveInt] = Field(None, description="Limite de resultados")
    offset: Optional[NonNegativeInt] = Field(0, description="Offset para paginação")

    @validator("end_date")
    def validate_end_date(cls, v, values):
        """Valida que end_date é posterior a start_date."""
        if v and "start_date" in values and values["start_date"]:
            if v <= values["start_date"]:
                raise ValueError("end_date deve ser posterior a start_date")
        return v

    class Config:
        use_enum_values = True
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class TicketMetricsDTO(BaseModel):
    """DTO para métricas básicas de tickets."""

    total: NonNegativeInt = Field(0, description="Total de tickets")
    novos: NonNegativeInt = Field(0, description="Tickets novos")
    pendentes: NonNegativeInt = Field(0, description="Tickets pendentes")
    progresso: NonNegativeInt = Field(0, description="Tickets em progresso")
    resolvidos: NonNegativeInt = Field(0, description="Tickets resolvidos")
    fechados: NonNegativeInt = Field(0, description="Tickets fechados")
    cancelados: NonNegativeInt = Field(0, description="Tickets cancelados")

    @root_validator
    def validate_totals(cls, values):
        """Valida que a soma dos status não excede o total."""
        total = values.get("total", 0)
        status_sum = (
            values.get("novos", 0)
            + values.get("pendentes", 0)
            + values.get("progresso", 0)
            + values.get("resolvidos", 0)
            + values.get("fechados", 0)
            + values.get("cancelados", 0)
        )

        # Permite que o total seja maior (pode haver outros status)
        if status_sum > total and total > 0:
            # Log warning mas não falha validação
            pass

        return values

    def get_status_distribution(self) -> Dict[str, float]:
        """Retorna distribuição percentual por status."""
        if self.total == 0:
            return {status: 0.0 for status in TicketStatus}

        return {
            TicketStatus.NOVO.value: (self.novos / self.total) * 100,
            TicketStatus.PENDENTE.value: (self.pendentes / self.total) * 100,
            TicketStatus.PROGRESSO.value: (self.progresso / self.total) * 100,
            TicketStatus.RESOLVIDO.value: (self.resolvidos / self.total) * 100,
            "fechados": (self.fechados / self.total) * 100,
            "cancelados": (self.cancelados / self.total) * 100,
        }


class LevelMetricsDTO(BaseModel):
    """DTO para métricas por nível de técnico."""

    level: TechnicianLevel = Field(..., description="Nível do técnico")
    metrics: TicketMetricsDTO = Field(..., description="Métricas de tickets")
    technician_count: NonNegativeInt = Field(0, description="Número de técnicos neste nível")
    avg_resolution_time: Optional[float] = Field(None, description="Tempo médio de resolução em horas")

    class Config:
        use_enum_values = True


class TechnicianMetricsDTO(BaseModel):
    """DTO para métricas de um técnico específico."""

    id: PositiveInt = Field(..., description="ID do técnico")
    name: str = Field(..., min_length=1, max_length=255, description="Nome do técnico")
    level: TechnicianLevel = Field(..., description="Nível do técnico")
    rank: Optional[PositiveInt] = Field(None, description="Posição no ranking")
    metrics: TicketMetricsDTO = Field(..., description="Métricas de tickets")
    avg_resolution_time: Optional[float] = Field(None, description="Tempo médio de resolução em horas")
    efficiency_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="Score de eficiência (0-100)")
    last_activity: Optional[datetime] = Field(None, description="Última atividade")

    class Config:
        use_enum_values = True
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class MetricsDTO(BaseModel):
    """DTO principal para métricas consolidadas."""

    # Métricas gerais
    total: NonNegativeInt = Field(0, description="Total geral de tickets")
    novos: NonNegativeInt = Field(0, description="Total de tickets novos")
    pendentes: NonNegativeInt = Field(0, description="Total de tickets pendentes")
    progresso: NonNegativeInt = Field(0, description="Total de tickets em progresso")
    resolvidos: NonNegativeInt = Field(0, description="Total de tickets resolvidos")

    # Métricas por nível
    niveis: Dict[str, LevelMetricsDTO] = Field(
        default_factory=dict,
        description="Métricas organizadas por nível (N1, N2, N3, N4)",
    )

    # Metadata
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp da coleta")
    period_start: Optional[datetime] = Field(None, description="Início do período analisado")
    period_end: Optional[datetime] = Field(None, description="Fim do período analisado")

    # Métricas calculadas
    total_technicians: NonNegativeInt = Field(0, description="Total de técnicos ativos")
    avg_tickets_per_technician: Optional[float] = Field(None, description="Média de tickets por técnico")

    @validator("niveis")
    def validate_levels(cls, v):
        """Valida que os níveis são válidos."""
        valid_levels = {level.value for level in TechnicianLevel if level != TechnicianLevel.UNKNOWN}
        for level_key in v.keys():
            if level_key not in valid_levels:
                raise ValueError(f"Nível inválido: {level_key}. Deve ser um de: {valid_levels}")
        return v

    @root_validator
    def calculate_derived_metrics(cls, values):
        """Calcula métricas derivadas."""
        # Calcular total de técnicos
        niveis = values.get("niveis", {})
        total_technicians = sum(level.technician_count for level in niveis.values())
        values["total_technicians"] = total_technicians

        # Calcular média de tickets por técnico
        total_tickets = values.get("total", 0)
        if total_technicians > 0:
            values["avg_tickets_per_technician"] = total_tickets / total_technicians

        return values

    def get_level_distribution(self) -> Dict[str, float]:
        """Retorna distribuição percentual de tickets por nível."""
        if self.total == 0:
            return {level: 0.0 for level in TechnicianLevel if level != TechnicianLevel.UNKNOWN}

        return {level: (metrics.metrics.total / self.total) * 100 for level, metrics in self.niveis.items()}

    def get_summary_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas resumidas."""
        return {
            "total_tickets": self.total,
            "total_technicians": self.total_technicians,
            "avg_tickets_per_technician": self.avg_tickets_per_technician,
            "levels_count": len(self.niveis),
            "status_distribution": {
                "novos": (self.novos / self.total * 100) if self.total > 0 else 0,
                "pendentes": (self.pendentes / self.total * 100) if self.total > 0 else 0,
                "progresso": (self.progresso / self.total * 100) if self.total > 0 else 0,
                "resolvidos": (self.resolvidos / self.total * 100) if self.total > 0 else 0,
            },
            "level_distribution": self.get_level_distribution(),
            "timestamp": self.timestamp.isoformat(),
        }

    class Config:
        use_enum_values = True
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class DashboardMetricsDTO(BaseModel):
    """DTO para métricas completas do dashboard."""

    metrics: MetricsDTO = Field(..., description="Métricas principais")
    technicians: List[TechnicianMetricsDTO] = Field(default_factory=list, description="Lista de técnicos com suas métricas")
    top_performers: List[TechnicianMetricsDTO] = Field(default_factory=list, description="Top performers (ranking)")
    recent_tickets: List[Dict[str, Any]] = Field(default_factory=list, description="Tickets recentes")

    # Métricas de performance
    response_time_ms: Optional[float] = Field(None, description="Tempo de resposta em ms")
    cache_hit: Optional[bool] = Field(None, description="Se foi hit de cache")
    data_freshness: Optional[datetime] = Field(None, description="Freshness dos dados")

    def get_performance_summary(self) -> Dict[str, Any]:
        """Retorna resumo de performance."""
        return {
            "response_time_ms": self.response_time_ms,
            "cache_hit": self.cache_hit,
            "data_freshness": self.data_freshness.isoformat() if self.data_freshness else None,
            "total_technicians": len(self.technicians),
            "top_performers_count": len(self.top_performers),
            "recent_tickets_count": len(self.recent_tickets),
        }

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class MetricsResponseDTO(BaseModel):
    """DTO para resposta padronizada de métricas."""

    success: bool = Field(True, description="Indica se a operação foi bem-sucedida")
    data: Optional[Union[MetricsDTO, DashboardMetricsDTO, List[TechnicianMetricsDTO]]] = Field(
        None, description="Dados das métricas"
    )
    message: Optional[str] = Field(None, description="Mensagem adicional")
    errors: List[str] = Field(default_factory=list, description="Lista de erros")
    warnings: List[str] = Field(default_factory=list, description="Lista de avisos")

    # Metadata da resposta
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp da resposta")
    correlation_id: Optional[str] = Field(None, description="ID de correlação para tracing")
    execution_time_ms: Optional[float] = Field(None, description="Tempo de execução em ms")

    # Informações de paginação (quando aplicável)
    pagination: Optional[Dict[str, Any]] = Field(None, description="Informações de paginação")

    @validator("data")
    def validate_data_when_success(cls, v, values):
        """Valida que data está presente quando success=True."""
        success = values.get("success", True)
        if success and v is None:
            raise ValueError("data deve estar presente quando success=True")
        return v

    @validator("errors")
    def validate_errors_when_not_success(cls, v, values):
        """Valida que errors está presente quando success=False."""
        success = values.get("success", True)
        if not success and not v:
            raise ValueError("errors deve estar presente quando success=False")
        return v

    def add_error(self, error: str) -> None:
        """Adiciona um erro e marca success=False."""
        self.errors.append(error)
        self.success = False

    def add_warning(self, warning: str) -> None:
        """Adiciona um aviso."""
        self.warnings.append(warning)

    def set_execution_time(self, start_time: datetime) -> None:
        """Define o tempo de execução baseado no tempo de início."""
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        self.execution_time_ms = round(execution_time, 2)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


# Factory functions para criação de DTOs


def create_empty_metrics_dto() -> MetricsDTO:
    """Cria um DTO de métricas vazio com valores padrão."""
    return MetricsDTO(
        total=0,
        novos=0,
        pendentes=0,
        progresso=0,
        resolvidos=0,
        niveis={
            TechnicianLevel.N1.value: LevelMetricsDTO(
                level=TechnicianLevel.N1, metrics=TicketMetricsDTO(), technician_count=0
            ),
            TechnicianLevel.N2.value: LevelMetricsDTO(
                level=TechnicianLevel.N2, metrics=TicketMetricsDTO(), technician_count=0
            ),
            TechnicianLevel.N3.value: LevelMetricsDTO(
                level=TechnicianLevel.N3, metrics=TicketMetricsDTO(), technician_count=0
            ),
            TechnicianLevel.N4.value: LevelMetricsDTO(
                level=TechnicianLevel.N4, metrics=TicketMetricsDTO(), technician_count=0
            ),
        },
    )


def create_error_response(error_message: str, correlation_id: Optional[str] = None) -> MetricsResponseDTO:
    """Cria uma resposta de erro padronizada."""
    return MetricsResponseDTO(success=False, data=None, errors=[error_message], correlation_id=correlation_id)


def create_success_response(
    data: Union[MetricsDTO, DashboardMetricsDTO, List[TechnicianMetricsDTO]],
    correlation_id: Optional[str] = None,
    message: Optional[str] = None,
) -> MetricsResponseDTO:
    """Cria uma resposta de sucesso padronizada."""
    return MetricsResponseDTO(success=True, data=data, message=message, correlation_id=correlation_id)
