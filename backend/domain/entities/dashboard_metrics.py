from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime


@dataclass
class LevelMetrics:
    """Métricas por nível de atendimento"""

    novos: int
    progresso: int
    pendentes: int
    resolvidos: int
    total: int


@dataclass
class TechnicianRanking:
    """Ranking de técnicos"""

    name: str
    resolved_tickets: int
    avg_resolution_time: float
    satisfaction_score: float


@dataclass
class TrendData:
    """Dados de tendência temporal"""

    date: datetime
    value: int
    label: str


@dataclass
class DashboardMetrics:
    """Entidade agregada representando todas as métricas do dashboard"""

    niveis: Dict[str, LevelMetrics]
    technician_ranking: List[TechnicianRanking]
    trends: Dict[str, List[TrendData]]
    system_status: str
    last_updated: datetime

    def get_total_tickets(self) -> int:
        """Retorna o total de tickets em todos os níveis"""
        return sum(nivel.total for nivel in self.niveis.values())

    def get_resolution_rate(self) -> float:
        """Calcula a taxa de resolução geral"""
        total = self.get_total_tickets()
        resolved = sum(nivel.resolvidos for nivel in self.niveis.values())
        return (resolved / total * 100) if total > 0 else 0.0
