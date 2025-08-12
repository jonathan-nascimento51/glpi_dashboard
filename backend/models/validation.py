from datetime import datetime
from typing import Optional, List, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.types import PositiveInt, NonNegativeInt, PositiveFloat


class TicketStatus(str, Enum):
    """Status poss?veis para tickets"""

    ABERTO = "aberto"
    EM_ANDAMENTO = "em_andamento"
    AGUARDANDO = "aguardando"
    RESOLVIDO = "resolvido"
    FECHADO = "fechado"
    CANCELADO = "cancelado"


class Priority(str, Enum):
    """Prioridades de tickets"""

    BAIXA = "baixa"
    NORMAL = "normal"
    ALTA = "alta"
    URGENTE = "urgente"
    CRITICA = "critica"


class TechnicianLevel(str, Enum):
    """N?veis de t?cnicos"""

    N1 = "N1"
    N2 = "N2"
    N3 = "N3"
    N4 = "N4"


class LevelMetrics(BaseModel):
    """M?tricas para um n?vel espec?fico"""

    total: NonNegativeInt = Field(..., description="Total de tickets")
    resolvidos: NonNegativeInt = Field(..., description="Tickets resolvidos")
    pendentes: NonNegativeInt = Field(..., description="Tickets pendentes")
    tempo_medio: PositiveFloat = Field(
        ..., description="Tempo m?dio de resolu??o em horas"
    )

    @field_validator("resolvidos")
    @classmethod
    def validate_resolvidos(cls, v, info):
        if info.data.get("total") is not None and v > info.data["total"]:
            raise ValueError("Resolvidos n?o pode ser maior que total")
        return v

    @model_validator(mode="after")
    def validate_pendentes(self):
        if self.pendentes != self.total - self.resolvidos:
            raise ValueError("Pendentes deve ser igual a total - resolvidos")
        return self


class MetricsData(BaseModel):
    """Dados de m?tricas do sistema"""

    n1: LevelMetrics = Field(..., description="M?tricas do n?vel N1")
    n2: LevelMetrics = Field(..., description="M?tricas do n?vel N2")
    n3: LevelMetrics = Field(..., description="M?tricas do n?vel N3")
    n4: LevelMetrics = Field(..., description="M?tricas do n?vel N4")
    total_geral: NonNegativeInt = Field(..., description="Total geral de tickets")
    tempo_medio_geral: PositiveFloat = Field(..., description="Tempo m?dio geral")

    @model_validator(mode="after")
    def validate_totals(self):
        calculated_total = self.n1.total + self.n2.total + self.n3.total + self.n4.total
        if self.total_geral != calculated_total:
            raise ValueError(
                f"Total geral ({self.total_geral}) deve ser igual ? soma dos n?veis ({calculated_total})"
            )
        return self


class TechnicianRanking(BaseModel):
    """Ranking de t?cnicos"""

    nome: str = Field(..., min_length=1, description="Nome do t?cnico")
    nivel: TechnicianLevel = Field(..., description="N?vel do t?cnico")
    tickets_resolvidos: NonNegativeInt = Field(..., description="Tickets resolvidos")
    tempo_medio: PositiveFloat = Field(..., description="Tempo m?dio de resolu??o")
    pontuacao: PositiveFloat = Field(..., description="Pontua??o do t?cnico")
    posicao: PositiveInt = Field(..., description="Posi??o no ranking")

    @field_validator("nome")
    @classmethod
    def validate_nome(cls, v):
        return v.strip()


class Ticket(BaseModel):
    """Modelo de ticket"""

    id: PositiveInt = Field(..., description="ID do ticket")
    titulo: str = Field(
        ..., min_length=1, max_length=255, description="T?tulo do ticket"
    )
    descricao: Optional[str] = Field(None, description="Descri??o do ticket")
    status: TicketStatus = Field(..., description="Status do ticket")
    prioridade: Priority = Field(..., description="Prioridade do ticket")
    categoria: str = Field(..., min_length=1, description="Categoria do ticket")
    tecnico: Optional[str] = Field(None, description="T?cnico respons?vel")
    solicitante: str = Field(..., min_length=1, description="Solicitante do ticket")
    data_criacao: datetime = Field(..., description="Data de cria??o")
    data_atualizacao: Optional[datetime] = Field(
        None, description="Data de atualiza??o"
    )
    data_resolucao: Optional[datetime] = Field(None, description="Data de resolu??o")
    tempo_resolucao: Optional[PositiveFloat] = Field(
        None, description="Tempo de resolu??o em horas"
    )

    @field_validator("titulo", "categoria", "solicitante")
    @classmethod
    def validate_strings(cls, v):
        return v.strip()

    @field_validator("tecnico")
    @classmethod
    def validate_tecnico(cls, v):
        return v.strip() if v else None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.data_atualizacao and self.data_atualizacao < self.data_criacao:
            raise ValueError(
                "Data de atualiza??o n?o pode ser anterior ? data de cria??o"
            )
        if self.data_resolucao and self.data_resolucao < self.data_criacao:
            raise ValueError(
                "Data de resolu??o n?o pode ser anterior ? data de cria??o"
            )
        if (
            self.status in [TicketStatus.RESOLVIDO, TicketStatus.FECHADO]
            and not self.data_resolucao
        ):
            raise ValueError(
                "Tickets resolvidos ou fechados devem ter data de resolu??o"
            )
        return self


class NewTicket(BaseModel):
    """Modelo para cria??o de novo ticket"""

    titulo: str = Field(
        ..., min_length=1, max_length=255, description="T?tulo do ticket"
    )
    descricao: Optional[str] = Field(None, description="Descri??o do ticket")
    prioridade: Priority = Field(..., description="Prioridade do ticket")
    categoria: str = Field(..., min_length=1, description="Categoria do ticket")
    solicitante: str = Field(..., min_length=1, description="Solicitante do ticket")

    @field_validator("titulo", "categoria", "solicitante")
    @classmethod
    def validate_strings(cls, v):
        return v.strip()


class SystemStatus(BaseModel):
    """Status do sistema"""

    status: str = Field(..., description="Status geral do sistema")
    uptime: PositiveFloat = Field(..., description="Tempo de atividade em horas")
    tickets_abertos: NonNegativeInt = Field(..., description="Tickets abertos")
    tickets_pendentes: NonNegativeInt = Field(..., description="Tickets pendentes")
    load_average: PositiveFloat = Field(..., description="Carga m?dia do sistema")
    memoria_uso: float = Field(..., ge=0, le=100, description="Uso de mem?ria em %")
    disco_uso: float = Field(..., ge=0, le=100, description="Uso de disco em %")
    ultima_atualizacao: datetime = Field(default_factory=datetime.now)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        valid_statuses = ["online", "offline", "manutencao", "degradado"]
        if v.lower() not in valid_statuses:
            raise ValueError(f"Status deve ser um de: {valid_statuses}")
        return v.lower()


class FilterParams(BaseModel):
    """Par?metros de filtro para consultas"""

    status: Optional[List[TicketStatus]] = Field(None, description="Filtrar por status")
    prioridade: Optional[List[Priority]] = Field(
        None, description="Filtrar por prioridade"
    )
    categoria: Optional[str] = Field(
        None, min_length=1, description="Filtrar por categoria"
    )
    tecnico: Optional[str] = Field(
        None, min_length=1, description="Filtrar por t?cnico"
    )
    data_inicio: Optional[datetime] = Field(
        None, description="Data de in?cio do per?odo"
    )
    data_fim: Optional[datetime] = Field(None, description="Data de fim do per?odo")
    limite: Optional[int] = Field(50, ge=1, le=1000, description="Limite de resultados")
    offset: Optional[int] = Field(0, ge=0, description="Offset para pagina??o")

    @field_validator("data_fim")
    @classmethod
    def validate_data_fim(cls, v, info):
        if v and info.data.get("data_inicio"):
            if v < info.data["data_inicio"]:
                raise ValueError("Data fim n?o pode ser anterior ? data in?cio")
        return v


class ApiResponse(BaseModel):
    """Resposta padr?o da API"""

    success: bool = Field(..., description="Indica se a opera??o foi bem-sucedida")
    message: str = Field(..., description="Mensagem de resposta")
    data: Optional[Any] = Field(None, description="Dados da resposta")
    errors: Optional[List[str]] = Field(None, description="Lista de erros")
    timestamp: datetime = Field(default_factory=datetime.now)

    @field_validator("message")
    @classmethod
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError("Mensagem n?o pode estar vazia")
        return v.strip()


class ErrorDetail(BaseModel):
    """Detalhes de erro"""

    field: Optional[str] = Field(None, description="Campo que causou o erro")
    message: str = Field(..., description="Mensagem de erro")
    code: Optional[str] = Field(None, description="C?digo do erro")


class ValidationError(BaseModel):
    """Erro de valida??o"""

    detail: List[ErrorDetail] = Field(..., description="Detalhes dos erros")
    message: str = Field("Erro de valida??o", description="Mensagem geral")
