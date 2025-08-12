from abc import ABC, abstractmethod
from typing import List, Any, Optional
from datetime import datetime
from domain.entities.ticket import Ticket
from domain.entities.dashboard_metrics import DashboardMetrics, TechnicianRanking

class GLPIRepositoryInterface(ABC):
    """Interface para repositório GLPI"""
    
    @abstractmethod
    async def get_tickets(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Ticket]:
        """Busca tickets do GLPI"""
        pass
    
    @abstractmethod
    async def get_dashboard_metrics(self) -> DashboardMetrics:
        """Busca métricas do dashboard"""
        pass
    
    @abstractmethod
    async def get_technician_ranking(self) -> List[TechnicianRanking]:
        """Busca ranking de técnicos"""
        pass
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Autentica com o GLPI"""
        pass

class CacheRepositoryInterface(ABC):
    """Interface para repositório de cache"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Busca valor do cache"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Define valor no cache"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Limpa todo o cache"""
        pass

class ClockInterface(ABC):
    """Interface para operações de tempo"""
    
    @abstractmethod
    def now(self) -> datetime:
        """Retorna o timestamp atual"""
        pass
    
    @abstractmethod
    def format_datetime(self, dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Formata datetime para string"""
        pass
