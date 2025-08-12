from typing import List, Optional
from datetime import datetime
import logging
import requests
import time
from domain.entities.ticket import Ticket
from domain.entities.dashboard_metrics import DashboardMetrics, LevelMetrics, TechnicianRanking, TrendData
from domain.interfaces.repositories import GLPIRepositoryInterface
from config.settings import active_config

class GLPIAdapter(GLPIRepositoryInterface):
    """Adaptador para integração com a API do GLPI"""
    
    def __init__(self):
        self.glpi_url = active_config.GLPI_URL
        self.app_token = active_config.GLPI_APP_TOKEN
        self.user_token = active_config.GLPI_USER_TOKEN
        self.logger = logging.getLogger("glpi_adapter")
        
        # Mapeamento de status dos tickets
        self.status_map = {
            "Novo": 1,
            "Processando (atribuído)": 2,
            "Processando (planejado)": 3,
            "Pendente": 4,
            "Solucionado": 5,
            "Fechado": 6,
        }
        
        # Níveis de atendimento (grupos técnicos)
        self.service_levels = {
            "N1": 89,
            "N2": 90,
            "N3": 91,
            "N4": 92,
        }
        
        self.session_token = None
        self.token_created_at = None
        self.max_retries = 3
        self.retry_delay_base = 2
        self.session_timeout = 3600
    
    async def authenticate(self) -> bool:
        """Autentica com o GLPI"""
        try:
            if self._is_token_valid():
                return True
            
            headers = {
                "Content-Type": "application/json",
                "App-Token": self.app_token,
                "Authorization": f"user_token {self.user_token}",
            }
            
            response = requests.get(
                f"{self.glpi_url}/initSession",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.session_token = data.get("session_token")
                self.token_created_at = time.time()
                self.logger.info("Autenticação GLPI realizada com sucesso")
                return True
            else:
                self.logger.error(f"Erro na autenticação GLPI: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro na autenticação GLPI: {e}")
            return False
    
    def _is_token_valid(self) -> bool:
        """Verifica se o token ainda é válido"""
        if not self.session_token or not self.token_created_at:
            return False
        
        current_time = time.time()
        return (current_time - self.token_created_at) < self.session_timeout
    
    async def get_tickets(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Ticket]:
        """Busca tickets do GLPI"""
        if not await self.authenticate():
            raise Exception("Falha na autenticação GLPI")
        
        # Por enquanto retorna lista vazia - implementação completa seria feita aqui
        return []
    
    async def get_dashboard_metrics(self) -> DashboardMetrics:
        """Busca métricas do dashboard"""
        if not await self.authenticate():
            raise Exception("Falha na autenticação GLPI")
        
        # Implementação mock baseada no serviço existente
        niveis = {
            "N1": LevelMetrics(novos=5, progresso=12, pendentes=3, resolvidos=45, total=65),
            "N2": LevelMetrics(novos=8, progresso=15, pendentes=5, resolvidos=32, total=60),
            "N3": LevelMetrics(novos=2, progresso=8, pendentes=1, resolvidos=18, total=29),
            "N4": LevelMetrics(novos=1, progresso=3, pendentes=0, resolvidos=8, total=12),
        }
        
        technician_ranking = await self.get_technician_ranking()
        
        trends = {
            "tickets_created": [
                TrendData(date=datetime.now(), value=15, label="Hoje"),
                TrendData(date=datetime.now(), value=23, label="Ontem"),
            ],
            "tickets_resolved": [
                TrendData(date=datetime.now(), value=18, label="Hoje"),
                TrendData(date=datetime.now(), value=20, label="Ontem"),
            ],
        }
        
        return DashboardMetrics(
            niveis=niveis,
            technician_ranking=technician_ranking,
            trends=trends,
            system_status="online",
            last_updated=datetime.now()
        )
    
    async def get_technician_ranking(self) -> List[TechnicianRanking]:
        """Busca ranking de técnicos"""
        if not await self.authenticate():
            raise Exception("Falha na autenticação GLPI")
        
        # Implementação mock
        return [
            TechnicianRanking(
                name="João Silva",
                resolved_tickets=25,
                avg_resolution_time=2.5,
                satisfaction_score=4.8
            ),
            TechnicianRanking(
                name="Maria Santos",
                resolved_tickets=22,
                avg_resolution_time=3.1,
                satisfaction_score=4.6
            ),
            TechnicianRanking(
                name="Pedro Costa",
                resolved_tickets=18,
                avg_resolution_time=2.8,
                satisfaction_score=4.7
            ),
        ]
