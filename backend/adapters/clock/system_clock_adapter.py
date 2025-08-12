from datetime import datetime
from domain.interfaces.repositories import ClockInterface

class SystemClockAdapter(ClockInterface):
    """Adaptador para operações de tempo do sistema"""
    
    def now(self) -> datetime:
        """Retorna o timestamp atual"""
        return datetime.now()
    
    def format_datetime(self, dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Formata datetime para string"""
        return dt.strftime(format_str)
