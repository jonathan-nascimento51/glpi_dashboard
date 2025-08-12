from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class TicketStatus(Enum):
    NOVO = 1
    PROCESSANDO_ATRIBUIDO = 2
    PROCESSANDO_PLANEJADO = 3
    PENDENTE = 4
    SOLUCIONADO = 5
    FECHADO = 6


class TicketPriority(Enum):
    MUITO_BAIXA = 1
    BAIXA = 2
    MEDIA = 3
    ALTA = 4
    MUITO_ALTA = 5
    CRITICA = 6


@dataclass
class Ticket:
    """Entidade de domínio representando um ticket do GLPI"""

    id: int
    name: str
    status: TicketStatus
    priority: TicketPriority
    created_at: datetime
    updated_at: datetime
    assigned_group_id: Optional[int] = None
    assigned_user_id: Optional[int] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    def is_resolved(self) -> bool:
        return self.status in [TicketStatus.SOLUCIONADO, TicketStatus.FECHADO]

    def is_pending(self) -> bool:
        return self.status == TicketStatus.PENDENTE

    def is_in_progress(self) -> bool:
        return self.status in [
            TicketStatus.PROCESSANDO_ATRIBUIDO,
            TicketStatus.PROCESSANDO_PLANEJADO,
        ]
