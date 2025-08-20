#!/usr/bin/env python3
"""
Script de Migração Automatizada - GLPI Dashboard
Este script automatiza a criação da nova estrutura arquitetural proposta.

Uso:
    python migration_script.py --phase [1|2|3|4|5|6] [--dry-run]
    
Exemplos:
    python migration_script.py --phase 1 --dry-run  # Simula a criação da Fase 1
    python migration_script.py --phase 1            # Executa a criação da Fase 1
"""

import os
import sys
import argparse
import shutil
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

class MigrationScript:
    def __init__(self, project_root: str, dry_run: bool = False):
        self.project_root = Path(project_root)
        self.dry_run = dry_run
        self.created_files = []
        self.created_dirs = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix = "[DRY-RUN]" if self.dry_run else "[EXEC]"
        print(f"{timestamp} {prefix} [{level}] {message}")
    
    def create_directory(self, path: Path) -> bool:
        """Cria diretório se não existir"""
        if path.exists():
            self.log(f"Diretório já existe: {path}", "SKIP")
            return False
            
        if not self.dry_run:
            path.mkdir(parents=True, exist_ok=True)
            
        self.log(f"Criado diretório: {path}", "CREATE")
        self.created_dirs.append(str(path))
        return True
    
    def create_file(self, path: Path, content: str = "") -> bool:
        """Cria arquivo com conteúdo"""
        if path.exists():
            self.log(f"Arquivo já existe: {path}", "SKIP")
            return False
            
        # Criar diretório pai se necessário
        self.create_directory(path.parent)
        
        if not self.dry_run:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        self.log(f"Criado arquivo: {path}", "CREATE")
        self.created_files.append(str(path))
        return True
    
    def backup_current_structure(self) -> str:
        """Cria backup da estrutura atual"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.project_root / f"backup_{timestamp}"
        
        if not self.dry_run:
            # Backup dos arquivos principais
            important_files = [
                "backend/glpi_service.py",
                "frontend/src/App.tsx",
                "backend/api_service.py"
            ]
            
            backup_dir.mkdir(exist_ok=True)
            
            for file_path in important_files:
                src = self.project_root / file_path
                if src.exists():
                    dst = backup_dir / file_path
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    
        self.log(f"Backup criado em: {backup_dir}", "BACKUP")
        return str(backup_dir)
    
    def phase_1_foundation(self):
        """Fase 1: Criação da estrutura base"""
        self.log("=== INICIANDO FASE 1: FUNDAÇÃO ===", "PHASE")
        
        # Estrutura backend
        backend_dirs = [
            "backend/core/domain/entities",
            "backend/core/domain/value_objects", 
            "backend/core/domain/repositories",
            "backend/core/domain/services",
            "backend/core/application/use_cases",
            "backend/core/application/dto",
            "backend/core/application/interfaces",
            "backend/core/infrastructure/repositories",
            "backend/core/infrastructure/external/glpi",
            "backend/core/infrastructure/external/cache",
            "backend/core/infrastructure/services",
            "backend/core/infrastructure/config",
            "backend/api/controllers",
            "backend/api/middleware",
            "backend/api/schemas/request",
            "backend/api/schemas/response",
            "backend/api/routes",
            "backend/shared/exceptions",
            "backend/shared/utils",
            "backend/shared/constants",
            "backend/shared/types",
            "backend/tests/unit/domain",
            "backend/tests/unit/application",
            "backend/tests/unit/infrastructure",
            "backend/tests/integration/api",
            "backend/tests/integration/external",
            "backend/tests/e2e/scenarios"
        ]
        
        # Estrutura frontend
        frontend_dirs = [
            "frontend/src/app/store/slices",
            "frontend/src/app/store/middleware",
            "frontend/src/app/providers",
            "frontend/src/app/router",
            "frontend/src/features/dashboard/components",
            "frontend/src/features/dashboard/hooks",
            "frontend/src/features/dashboard/services",
            "frontend/src/features/dashboard/types",
            "frontend/src/features/ranking/components",
            "frontend/src/features/ranking/hooks",
            "frontend/src/features/ranking/services",
            "frontend/src/features/ranking/types",
            "frontend/src/features/filters/components",
            "frontend/src/features/filters/hooks",
            "frontend/src/features/filters/types",
            "frontend/src/features/monitoring/components",
            "frontend/src/features/monitoring/hooks",
            "frontend/src/features/monitoring/services",
            "frontend/src/features/monitoring/types",
            "frontend/src/shared/components/ui",
            "frontend/src/shared/components/layout",
            "frontend/src/shared/components/feedback",
            "frontend/src/shared/components/data-display",
            "frontend/src/shared/hooks",
            "frontend/src/shared/services",
            "frontend/src/shared/utils",
            "frontend/src/shared/types",
            "frontend/src/shared/constants",
            "frontend/src/pages",
            "frontend/tests/features/dashboard",
            "frontend/tests/features/ranking",
            "frontend/tests/features/filters",
            "frontend/tests/shared/components",
            "frontend/tests/shared/hooks",
            "frontend/tests/shared/utils",
            "frontend/tests/integration",
            "frontend/tests/e2e"
        ]
        
        # Estrutura compartilhada e documentação
        shared_dirs = [
            "shared/types",
            "shared/constants",
            "shared/utils",
            "docs/architecture/decisions",
            "docs/architecture/diagrams",
            "docs/architecture/patterns",
            "docs/api",
            "docs/development",
            "docs/user",
            "tools/scripts",
            "tools/generators",
            "tools/linters",
            "docker",
            "infrastructure/terraform",
            "infrastructure/kubernetes",
            "infrastructure/monitoring"
        ]
        
        all_dirs = backend_dirs + frontend_dirs + shared_dirs
        
        for dir_path in all_dirs:
            self.create_directory(self.project_root / dir_path)
        
        # Criar arquivos __init__.py para Python
        python_dirs = [d for d in all_dirs if d.startswith("backend/")]
        for dir_path in python_dirs:
            init_file = self.project_root / dir_path / "__init__.py"
            self.create_file(init_file, "# -*- coding: utf-8 -*-\n")
        
        # Criar arquivos index.ts para TypeScript
        ts_feature_dirs = [
            "frontend/src/features/dashboard",
            "frontend/src/features/ranking", 
            "frontend/src/features/filters",
            "frontend/src/features/monitoring"
        ]
        for dir_path in ts_feature_dirs:
            index_file = self.project_root / dir_path / "index.ts"
            self.create_file(index_file, "// Feature exports\nexport * from './types'\nexport * from './hooks'\nexport * from './components'\n")
        
        self.log("=== FASE 1 CONCLUÍDA ===", "PHASE")
    
    def phase_2_domain(self):
        """Fase 2: Implementação do domínio"""
        self.log("=== INICIANDO FASE 2: DOMÍNIO ===", "PHASE")
        
        # Entidade Ticket
        ticket_entity = '''
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from ..value_objects.ticket_status import TicketStatus
from ..value_objects.priority import Priority

@dataclass
class Ticket:
    """Entidade de domínio para Ticket"""
    id: int
    title: str
    status: TicketStatus
    priority: Priority
    created_at: datetime
    updated_at: datetime
    assigned_technician_id: Optional[int] = None
    group_id: Optional[int] = None
    
    def is_new(self) -> bool:
        """Verifica se o ticket é novo"""
        return self.status == TicketStatus.NEW
    
    def is_resolved(self) -> bool:
        """Verifica se o ticket está resolvido"""
        return self.status in [TicketStatus.SOLVED, TicketStatus.CLOSED]
    
    def is_processing(self) -> bool:
        """Verifica se o ticket está em processamento"""
        return self.status in [TicketStatus.PROCESSING_ASSIGNED, TicketStatus.PROCESSING_PLANNED]
    
    def is_pending(self) -> bool:
        """Verifica se o ticket está pendente"""
        return self.status == TicketStatus.PENDING
    
    def days_since_creation(self) -> int:
        """Calcula dias desde a criação"""
        return (datetime.now() - self.created_at).days
'''
        
        # Value Object TicketStatus
        ticket_status = '''
from enum import Enum
from typing import List

class TicketStatus(Enum):
    """Status possíveis de um ticket"""
    NEW = 1
    PROCESSING_ASSIGNED = 2
    PROCESSING_PLANNED = 3
    PENDING = 4
    SOLVED = 5
    CLOSED = 6
    
    @classmethod
    def get_processing_statuses(cls) -> List['TicketStatus']:
        """Retorna status de processamento"""
        return [cls.PROCESSING_ASSIGNED, cls.PROCESSING_PLANNED]
    
    @classmethod
    def get_resolved_statuses(cls) -> List['TicketStatus']:
        """Retorna status resolvidos"""
        return [cls.SOLVED, cls.CLOSED]
    
    @classmethod
    def get_active_statuses(cls) -> List['TicketStatus']:
        """Retorna status ativos (não resolvidos)"""
        return [cls.NEW, cls.PROCESSING_ASSIGNED, cls.PROCESSING_PLANNED, cls.PENDING]
'''
        
        # Value Object Priority
        priority = '''
from enum import Enum

class Priority(Enum):
    """Prioridades de ticket"""
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5
    MAJOR = 6
    
    def get_weight(self) -> int:
        """Retorna peso numérico da prioridade"""
        return self.value
    
    @classmethod
    def get_high_priorities(cls):
        """Retorna prioridades altas"""
        return [cls.HIGH, cls.VERY_HIGH, cls.MAJOR]
'''
        
        # Serviço de Domínio - MetricCalculator
        metric_calculator = '''
from typing import List, Dict
from ..entities.ticket import Ticket
from ..value_objects.ticket_status import TicketStatus

class MetricCalculator:
    """Serviço de domínio para cálculo de métricas"""
    
    @staticmethod
    def calculate_status_metrics(tickets: List[Ticket]) -> Dict[str, int]:
        """Calcula métricas por status"""
        metrics = {
            'new': 0,
            'pending': 0,
            'processing': 0,
            'resolved': 0
        }
        
        for ticket in tickets:
            if ticket.is_new():
                metrics['new'] += 1
            elif ticket.is_pending():
                metrics['pending'] += 1
            elif ticket.is_processing():
                metrics['processing'] += 1
            elif ticket.is_resolved():
                metrics['resolved'] += 1
                
        return metrics
    
    @staticmethod
    def calculate_trend(current_metrics: Dict[str, int], 
                       previous_metrics: Dict[str, int]) -> Dict[str, float]:
        """Calcula tendência entre períodos"""
        trends = {}
        for key in current_metrics:
            previous_value = previous_metrics.get(key, 0)
            if previous_value == 0:
                trends[key] = 0.0
            else:
                change = current_metrics[key] - previous_value
                trends[key] = (change / previous_value) * 100
        return trends
    
    @staticmethod
    def calculate_priority_distribution(tickets: List[Ticket]) -> Dict[str, int]:
        """Calcula distribuição por prioridade"""
        distribution = {}
        for ticket in tickets:
            priority_name = ticket.priority.name.lower()
            distribution[priority_name] = distribution.get(priority_name, 0) + 1
        return distribution
'''
        
        # Repository Interface
        ticket_repository = '''
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from ..entities.ticket import Ticket

class TicketRepository(ABC):
    """Interface do repositório de tickets"""
    
    @abstractmethod
    async def get_tickets_by_date_range(self, 
                                       start_date: Optional[datetime] = None,
                                       end_date: Optional[datetime] = None) -> List[Ticket]:
        """Busca tickets por intervalo de datas"""
        pass
    
    @abstractmethod
    async def get_ticket_by_id(self, ticket_id: int) -> Optional[Ticket]:
        """Busca ticket por ID"""
        pass
    
    @abstractmethod
    async def get_tickets_by_technician(self, technician_id: int) -> List[Ticket]:
        """Busca tickets por técnico"""
        pass
    
    @abstractmethod
    async def get_tickets_by_status(self, status: List[int]) -> List[Ticket]:
        """Busca tickets por status"""
        pass
    
    @abstractmethod
    async def get_tickets_by_group(self, group_id: int) -> List[Ticket]:
        """Busca tickets por grupo"""
        pass
'''
        
        # Criar arquivos
        files_to_create = [
            ("backend/core/domain/entities/ticket.py", ticket_entity),
            ("backend/core/domain/value_objects/ticket_status.py", ticket_status),
            ("backend/core/domain/value_objects/priority.py", priority),
            ("backend/core/domain/services/metric_calculator.py", metric_calculator),
            ("backend/core/domain/repositories/ticket_repository.py", ticket_repository)
        ]
        
        for file_path, content in files_to_create:
            self.create_file(self.project_root / file_path, content)
        
        self.log("=== FASE 2 CONCLUÍDA ===", "PHASE")
    
    def phase_3_application(self):
        """Fase 3: Camada de aplicação"""
        self.log("=== INICIANDO FASE 3: APLICAÇÃO ===", "PHASE")
        
        # DTO Dashboard
        dashboard_dto = '''
from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime

@dataclass
class DateRangeDTO:
    """DTO para intervalo de datas"""
    start_date: datetime
    end_date: datetime
    
    def to_dict(self) -> Dict:
        return {
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat()
        }

@dataclass
class DashboardMetricsDTO:
    """DTO para métricas do dashboard"""
    general_metrics: Dict[str, int]
    level_metrics: Dict[str, Dict[str, int]]
    trends: Dict[str, float]
    total_tickets: int
    date_range: Optional[DateRangeDTO] = None
    
    def to_dict(self) -> Dict:
        return {
            'general_metrics': self.general_metrics,
            'level_metrics': self.level_metrics,
            'trends': self.trends,
            'total_tickets': self.total_tickets,
            'date_range': self.date_range.to_dict() if self.date_range else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DashboardMetricsDTO':
        date_range = None
        if data.get('date_range'):
            date_range = DateRangeDTO(
                start_date=datetime.fromisoformat(data['date_range']['start_date']),
                end_date=datetime.fromisoformat(data['date_range']['end_date'])
            )
        
        return cls(
            general_metrics=data['general_metrics'],
            level_metrics=data['level_metrics'],
            trends=data['trends'],
            total_tickets=data['total_tickets'],
            date_range=date_range
        )
'''
        
        # Use Case GetDashboardMetrics
        get_dashboard_metrics = '''
from typing import Optional
from ..dto.dashboard_dto import DashboardMetricsDTO, DateRangeDTO
from ..interfaces.cache_service import CacheService
from ...domain.repositories.ticket_repository import TicketRepository
from ...domain.services.metric_calculator import MetricCalculator
from ...shared.exceptions.domain_exceptions import ValidationError

class GetDashboardMetrics:
    """Caso de uso para obter métricas do dashboard"""
    
    def __init__(self, 
                 ticket_repository: TicketRepository,
                 cache_service: CacheService,
                 metric_calculator: MetricCalculator):
        self.ticket_repository = ticket_repository
        self.cache_service = cache_service
        self.metric_calculator = metric_calculator
    
    async def execute(self, date_range: Optional[DateRangeDTO] = None) -> DashboardMetricsDTO:
        """Executa o caso de uso"""
        # Validar entrada
        if date_range and date_range.start_date > date_range.end_date:
            raise ValidationError("Data inicial deve ser menor que data final")
        
        # Verificar cache
        cache_key = self._generate_cache_key(date_range)
        cached_result = await self.cache_service.get(cache_key)
        
        if cached_result:
            return DashboardMetricsDTO.from_dict(cached_result)
        
        # Buscar tickets
        tickets = await self.ticket_repository.get_tickets_by_date_range(
            start_date=date_range.start_date if date_range else None,
            end_date=date_range.end_date if date_range else None
        )
        
        # Calcular métricas gerais
        general_metrics = self.metric_calculator.calculate_status_metrics(tickets)
        
        # Calcular métricas por nível (implementar lógica de classificação)
        level_metrics = self._calculate_level_metrics(tickets)
        
        # Calcular tendências
        trends = await self._calculate_trends(general_metrics, date_range)
        
        # Criar DTO de resposta
        result = DashboardMetricsDTO(
            general_metrics=general_metrics,
            level_metrics=level_metrics,
            trends=trends,
            total_tickets=len(tickets),
            date_range=date_range
        )
        
        # Salvar no cache
        await self.cache_service.set(cache_key, result.to_dict(), ttl=300)
        
        return result
    
    def _generate_cache_key(self, date_range: Optional[DateRangeDTO]) -> str:
        """Gera chave de cache"""
        if date_range:
            return f"dashboard_metrics_{date_range.start_date.date()}_{date_range.end_date.date()}"
        return "dashboard_metrics_all"
    
    def _calculate_level_metrics(self, tickets) -> Dict[str, Dict[str, int]]:
        """Calcula métricas por nível de técnico"""
        # TODO: Implementar lógica de classificação por nível
        level_metrics = {}
        for level in ['N1', 'N2', 'N3', 'N4']:
            # Filtrar tickets por nível (implementar lógica)
            level_tickets = []  # Placeholder
            level_metrics[level] = self.metric_calculator.calculate_status_metrics(level_tickets)
        return level_metrics
    
    async def _calculate_trends(self, current_metrics, date_range) -> Dict[str, float]:
        """Calcula tendências comparando com período anterior"""
        # TODO: Implementar cálculo de tendências
        return {key: 0.0 for key in current_metrics.keys()}
'''
        
        # Interface CacheService
        cache_service = '''
from abc import ABC, abstractmethod
from typing import Any, Optional

class CacheService(ABC):
    """Interface do serviço de cache"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Busca valor no cache"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
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
'''
        
        # Criar arquivos
        files_to_create = [
            ("backend/core/application/dto/dashboard_dto.py", dashboard_dto),
            ("backend/core/application/use_cases/get_dashboard_metrics.py", get_dashboard_metrics),
            ("backend/core/application/interfaces/cache_service.py", cache_service)
        ]
        
        for file_path, content in files_to_create:
            self.create_file(self.project_root / file_path, content)
        
        self.log("=== FASE 3 CONCLUÍDA ===", "PHASE")
    
    def phase_4_infrastructure(self):
        """Fase 4: Infraestrutura"""
        self.log("=== INICIANDO FASE 4: INFRAESTRUTURA ===", "PHASE")
        
        # Cliente GLPI
        glpi_client = '''
import aiohttp
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from ....shared.exceptions.infrastructure_exceptions import ExternalAPIException

class GLPIClient:
    """Cliente para comunicação com API GLPI"""
    
    def __init__(self, base_url: str, app_token: str, user_token: str):
        self.base_url = base_url.rstrip('/')
        self.app_token = app_token
        self.user_token = user_token
        self.session_token = None
        self.session_expires = None
    
    async def authenticate(self) -> str:
        """Autentica na API GLPI"""
        url = f"{self.base_url}/initSession"
        headers = {
            'App-Token': self.app_token,
            'Authorization': f'user_token {self.user_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.session_token = data['session_token']
                        return self.session_token
                    else:
                        raise ExternalAPIException(f"Authentication failed: {response.status}")
        except Exception as e:
            raise ExternalAPIException(f"Failed to authenticate: {str(e)}")
    
    async def search_tickets(self, filters: Dict) -> List[Dict]:
        """Busca tickets com filtros"""
        if not self.session_token:
            await self.authenticate()
        
        # Construir query string
        query_params = []
        for key, value in filters.items():
            query_params.append(f"{key}={value}")
        
        query_string = "&".join(query_params)
        url = f"{self.base_url}/search/Ticket?{query_string}"
        
        headers = {
            'Session-Token': self.session_token,
            'App-Token': self.app_token,
            'Content-Type': 'application/json'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('data', [])
                    else:
                        raise ExternalAPIException(f"Search failed: {response.status}")
        except Exception as e:
            raise ExternalAPIException(f"Failed to search tickets: {str(e)}")
    
    async def get_ticket(self, ticket_id: int) -> Optional[Dict]:
        """Busca ticket específico"""
        if not self.session_token:
            await self.authenticate()
        
        url = f"{self.base_url}/Ticket/{ticket_id}"
        headers = {
            'Session-Token': self.session_token,
            'App-Token': self.app_token,
            'Content-Type': 'application/json'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        return None
                    else:
                        raise ExternalAPIException(f"Get ticket failed: {response.status}")
        except Exception as e:
            raise ExternalAPIException(f"Failed to get ticket {ticket_id}: {str(e)}")
'''
        
        # Implementação do repositório GLPI
        glpi_repository = '''
from typing import List, Optional
from datetime import datetime
from ...domain.entities.ticket import Ticket
from ...domain.repositories.ticket_repository import TicketRepository
from ..external.glpi.client import GLPIClient
from ..external.glpi.response_mapper import GLPIResponseMapper

class GLPITicketRepository(TicketRepository):
    """Implementação do repositório de tickets para GLPI"""
    
    def __init__(self, glpi_client: GLPIClient, response_mapper: GLPIResponseMapper):
        self.glpi_client = glpi_client
        self.response_mapper = response_mapper
    
    async def get_tickets_by_date_range(self, 
                                       start_date: Optional[datetime] = None,
                                       end_date: Optional[datetime] = None) -> List[Ticket]:
        """Busca tickets por intervalo de datas"""
        filters = {}
        
        if start_date:
            filters['date_creation'] = f'>={start_date.strftime("%Y-%m-%d")}'
        if end_date:
            filters['date_creation'] = f'<={end_date.strftime("%Y-%m-%d")}'
        
        raw_tickets = await self.glpi_client.search_tickets(filters)
        return [self.response_mapper.map_to_ticket(raw_ticket) for raw_ticket in raw_tickets]
    
    async def get_ticket_by_id(self, ticket_id: int) -> Optional[Ticket]:
        """Busca ticket por ID"""
        raw_ticket = await self.glpi_client.get_ticket(ticket_id)
        if raw_ticket:
            return self.response_mapper.map_to_ticket(raw_ticket)
        return None
    
    async def get_tickets_by_technician(self, technician_id: int) -> List[Ticket]:
        """Busca tickets por técnico"""
        filters = {'users_id_assign': technician_id}
        raw_tickets = await self.glpi_client.search_tickets(filters)
        return [self.response_mapper.map_to_ticket(raw_ticket) for raw_ticket in raw_tickets]
    
    async def get_tickets_by_status(self, status: List[int]) -> List[Ticket]:
        """Busca tickets por status"""
        status_filter = ','.join(map(str, status))
        filters = {'status': status_filter}
        raw_tickets = await self.glpi_client.search_tickets(filters)
        return [self.response_mapper.map_to_ticket(raw_ticket) for raw_ticket in raw_tickets]
    
    async def get_tickets_by_group(self, group_id: int) -> List[Ticket]:
        """Busca tickets por grupo"""
        filters = {'groups_id_assign': group_id}
        raw_tickets = await self.glpi_client.search_tickets(filters)
        return [self.response_mapper.map_to_ticket(raw_ticket) for raw_ticket in raw_tickets]
'''
        
        # Implementação do cache Redis
        redis_cache = '''
import json
import redis.asyncio as redis
from typing import Any, Optional
from ...application.interfaces.cache_service import CacheService
from ....shared.exceptions.infrastructure_exceptions import CacheException

class RedisCacheService(CacheService):
    """Implementação do cache usando Redis"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
    
    async def _get_client(self):
        """Obtém cliente Redis"""
        if not self.redis_client:
            self.redis_client = redis.from_url(self.redis_url)
        return self.redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        """Busca valor no cache"""
        try:
            client = await self._get_client()
            value = await client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            raise CacheException(f"Failed to get cache key {key}: {str(e)}")
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Define valor no cache"""
        try:
            client = await self._get_client()
            serialized_value = json.dumps(value, default=str)
            await client.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            raise CacheException(f"Failed to set cache key {key}: {str(e)}")
    
    async def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        try:
            client = await self._get_client()
            result = await client.delete(key)
            return result > 0
        except Exception as e:
            raise CacheException(f"Failed to delete cache key {key}: {str(e)}")
    
    async def clear(self) -> bool:
        """Limpa todo o cache"""
        try:
            client = await self._get_client()
            await client.flushdb()
            return True
        except Exception as e:
            raise CacheException(f"Failed to clear cache: {str(e)}")
'''
        
        # Criar arquivos
        files_to_create = [
            ("backend/core/infrastructure/external/glpi/client.py", glpi_client),
            ("backend/core/infrastructure/repositories/glpi_ticket_repository.py", glpi_repository),
            ("backend/core/infrastructure/services/redis_cache_service.py", redis_cache)
        ]
        
        for file_path, content in files_to_create:
            self.create_file(self.project_root / file_path, content)
        
        self.log("=== FASE 4 CONCLUÍDA ===", "PHASE")
    
    def generate_migration_report(self) -> str:
        """Gera relatório da migração"""
        report = f"""
# Relatório de Migração - GLPI Dashboard

**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Modo:** {'DRY-RUN' if self.dry_run else 'EXECUÇÃO'}

## Diretórios Criados ({len(self.created_dirs)})

"""
        for directory in self.created_dirs:
            report += f"- {directory}\n"
        
        report += f"\n## Arquivos Criados ({len(self.created_files)})\n\n"
        for file in self.created_files:
            report += f"- {file}\n"
        
        report += """

## Próximos Passos

1. **Revisar arquivos criados** - Verificar se a estrutura está correta
2. **Implementar testes** - Criar testes unitários para cada componente
3. **Configurar dependências** - Instalar bibliotecas necessárias
4. **Migrar código existente** - Mover funcionalidades do código atual
5. **Validar funcionamento** - Testar integração com GLPI

## Comandos Úteis

```bash
# Instalar dependências Python
pip install fastapi uvicorn aiohttp redis pydantic

# Instalar dependências Frontend
npm install @reduxjs/toolkit react-redux @tanstack/react-query

# Executar testes
pytest backend/tests/
npm test
```
"""
        
        return report
    
    def run_phase(self, phase: int):
        """Executa fase específica"""
        phases = {
            1: self.phase_1_foundation,
            2: self.phase_2_domain,
            3: self.phase_3_application,
            4: self.phase_4_infrastructure
        }
        
        if phase in phases:
            # Criar backup antes de executar
            if not self.dry_run:
                self.backup_current_structure()
            
            phases[phase]()
            
            # Gerar relatório
            report = self.generate_migration_report()
            report_file = self.project_root / f"migration_report_phase_{phase}.md"
            
            if not self.dry_run:
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(report)
            
            self.log(f"Relatório salvo em: {report_file}", "REPORT")
            print("\n" + "="*50)
            print(report)
            
        else:
            self.log(f"Fase {phase} não encontrada. Fases disponíveis: 1, 2, 3, 4", "ERROR")

def main():
    parser = argparse.ArgumentParser(description='Script de Migração Arquitetural - GLPI Dashboard')
    parser.add_argument('--phase', type=int, choices=[1, 2, 3, 4], required=True,
                       help='Fase da migração a ser executada')
    parser.add_argument('--dry-run', action='store_true',
                       help='Simula a execução sem criar arquivos')
    parser.add_argument('--project-root', type=str, default='.',
                       help='Diretório raiz do projeto')
    
    args = parser.parse_args()
    
    # Verificar se estamos no diretório correto
    project_root = Path(args.project_root).resolve()
    if not (project_root / 'backend').exists() and not (project_root / 'frontend').exists():
        print("❌ Erro: Não foi possível encontrar as pastas 'backend' ou 'frontend'.")
        print(f"   Certifique-se de estar no diretório raiz do projeto GLPI Dashboard.")
        print(f"   Diretório atual: {project_root}")
        sys.exit(1)
    
    # Executar migração
    migration = MigrationScript(str(project_root), args.dry_run)
    
    print(f"🚀 Iniciando migração - Fase {args.phase}")
    print(f"📁 Diretório: {project_root}")
    print(f"🔍 Modo: {'DRY-RUN (simulação)' if args.dry_run else 'EXECUÇÃO'}")
    print("="*50)
    
    try:
        migration.run_phase(args.phase)
        print("\n✅ Migração concluída com sucesso!")
    except Exception as e:
        print(f"\n❌ Erro durante a migração: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()