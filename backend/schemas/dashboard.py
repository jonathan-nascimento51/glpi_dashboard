from pydantic import BaseModel, Field
from typing import Optional

class KpiQueryParams(BaseModel):
    start_date: Optional[str] = Field(None, description="Data de início (YYYY-MM-DD) para filtrar os KPIs.")
    end_date: Optional[str] = Field(None, description="Data de fim (YYYY-MM-DD) para filtrar os KPIs.")

class TicketCounts(BaseModel):
    novos: int
    progresso: int
    pendentes: int
    resolvidos: int
    total: int

class KpiLevels(BaseModel):
    geral: TicketCounts
    n1: TicketCounts
    n2: TicketCounts
    n3: TicketCounts
    n4: TicketCounts

class KpiTrends(BaseModel):
    novos: str
    pendentes: str
    progresso: str
    resolvidos: str

class KpiResponse(BaseModel):
    niveis: KpiLevels
    tendencias: KpiTrends
