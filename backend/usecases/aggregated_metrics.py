# -*- coding: utf-8 -*-
"""Use cases para métricas agregadas por nível de serviço e período"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

from adapters.glpi.pagination import (
    TicketFilters, ServiceLevel, TicketStatus, DateRange,
    PaginationParams, GLPIQueryBuilder
)
from adapters.glpi.resilient_client import GLPIResilientClient

logger = logging.getLogger(__name__)


class MetricPeriod(Enum):
    """Períodos para agregação de métricas"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class MetricType(Enum):
    """Tipos de métricas disponíveis"""
    COUNT = "count"
    RESOLUTION_TIME = "resolution_time"
    RESPONSE_TIME = "response_time"
    SLA_COMPLIANCE = "sla_compliance"
    BACKLOG = "backlog"


@dataclass
class ServiceLevelMetric:
    """Métrica por nível de serviço"""
    service_level: ServiceLevel
    period_start: date
    period_end: date
    total_tickets: int
    new_tickets: int
    in_progress_tickets: int
    resolved_tickets: int
    closed_tickets: int
    pending_tickets: int
    avg_resolution_time_hours: Optional[float] = None
    avg_response_time_hours: Optional[float] = None
    sla_compliance_rate: Optional[float] = None
    backlog_count: int = 0
    
    @property
    def service_level_name(self) -> str:
        """Nome do nível de serviço"""
        return self.service_level.name
    
    @property
    def resolution_rate(self) -> float:
        """Taxa de resolução (resolvidos/total)"""
        if self.total_tickets == 0:
            return 0.0
        return (self.resolved_tickets + self.closed_tickets) / self.total_tickets
    
    @property
    def pending_rate(self) -> float:
        """Taxa de tickets pendentes"""
        if self.total_tickets == 0:
            return 0.0
        return self.pending_tickets / self.total_tickets


@dataclass
class AggregatedMetrics:
    """Métricas agregadas por período"""
    period: MetricPeriod
    period_start: date
    period_end: date
    metrics_by_level: Dict[ServiceLevel, ServiceLevelMetric]
    total_metrics: ServiceLevelMetric
    generated_at: datetime
    
    def get_level_metric(self, level: ServiceLevel) -> Optional[ServiceLevelMetric]:
        """Obtém métrica para um nível específico"""
        return self.metrics_by_level.get(level)
    
    def get_all_levels_summary(self) -> Dict[str, Any]:
        """Resumo de todos os níveis"""
        return {
            "period": {
                "type": self.period.value,
                "start": self.period_start.isoformat(),
                "end": self.period_end.isoformat()
            },
            "total": {
                "tickets": self.total_metrics.total_tickets,
                "new": self.total_metrics.new_tickets,
                "resolved": self.total_metrics.resolved_tickets,
                "pending": self.total_metrics.pending_tickets,
                "resolution_rate": self.total_metrics.resolution_rate,
                "avg_resolution_time_hours": self.total_metrics.avg_resolution_time_hours
            },
            "by_level": {
                level.name: {
                    "tickets": metric.total_tickets,
                    "new": metric.new_tickets,
                    "resolved": metric.resolved_tickets,
                    "pending": metric.pending_tickets,
                    "resolution_rate": metric.resolution_rate,
                    "avg_resolution_time_hours": metric.avg_resolution_time_hours
                }
                for level, metric in self.metrics_by_level.items()
            },
            "generated_at": self.generated_at.isoformat()
        }


class AggregatedMetricsUseCase:
    """Use case para obtenção de métricas agregadas"""
    
    def __init__(self, glpi_client: GLPIResilientClient):
        self.glpi_client = glpi_client
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def get_metrics_by_period(
        self,
        period: MetricPeriod,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        service_levels: Optional[List[ServiceLevel]] = None
    ) -> AggregatedMetrics:
        """Obtém métricas agregadas por período"""
        
        # Determinar período se não especificado
        if not start_date or not end_date:
            start_date, end_date = self._calculate_period_dates(period, start_date, end_date)
        
        # Níveis de serviço padrão se não especificado
        if not service_levels:
            service_levels = list(ServiceLevel)
        
        self.logger.info(
            f"Obtendo métricas agregadas para período {period.value} "
            f"de {start_date} a {end_date} para níveis {[sl.name for sl in service_levels]}"
        )
        
        # Obter métricas por nível
        metrics_by_level = {}
        total_counts = {
            'total': 0, 'new': 0, 'in_progress': 0,
            'resolved': 0, 'closed': 0, 'pending': 0
        }
        
        for level in service_levels:
            try:
                metric = await self._get_service_level_metrics(
                    level, start_date, end_date
                )
                metrics_by_level[level] = metric
                
                # Acumular totais
                total_counts['total'] += metric.total_tickets
                total_counts['new'] += metric.new_tickets
                total_counts['in_progress'] += metric.in_progress_tickets
                total_counts['resolved'] += metric.resolved_tickets
                total_counts['closed'] += metric.closed_tickets
                total_counts['pending'] += metric.pending_tickets
                
            except Exception as e:
                self.logger.error(f"Erro ao obter métricas para nível {level.name}: {e}")
                # Criar métrica vazia em caso de erro
                metrics_by_level[level] = ServiceLevelMetric(
                    service_level=level,
                    period_start=start_date,
                    period_end=end_date,
                    total_tickets=0,
                    new_tickets=0,
                    in_progress_tickets=0,
                    resolved_tickets=0,
                    closed_tickets=0,
                    pending_tickets=0
                )
        
        # Criar métrica total
        total_metrics = ServiceLevelMetric(
            service_level=ServiceLevel.N1,  # Placeholder
            period_start=start_date,
            period_end=end_date,
            **total_counts
        )
        
        return AggregatedMetrics(
            period=period,
            period_start=start_date,
            period_end=end_date,
            metrics_by_level=metrics_by_level,
            total_metrics=total_metrics,
            generated_at=datetime.now()
        )
    
    async def get_daily_metrics(
        self,
        target_date: Optional[date] = None,
        service_levels: Optional[List[ServiceLevel]] = None
    ) -> AggregatedMetrics:
        """Obtém métricas do dia"""
        if not target_date:
            target_date = date.today()
        
        return await self.get_metrics_by_period(
            MetricPeriod.DAILY,
            target_date,
            target_date,
            service_levels
        )
    
    async def get_weekly_metrics(
        self,
        week_start: Optional[date] = None,
        service_levels: Optional[List[ServiceLevel]] = None
    ) -> AggregatedMetrics:
        """Obtém métricas da semana"""
        if not week_start:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
        
        week_end = week_start + timedelta(days=6)
        
        return await self.get_metrics_by_period(
            MetricPeriod.WEEKLY,
            week_start,
            week_end,
            service_levels
        )
    
    async def get_monthly_metrics(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None,
        service_levels: Optional[List[ServiceLevel]] = None
    ) -> AggregatedMetrics:
        """Obtém métricas do mês"""
        if not year or not month:
            today = date.today()
            year = year or today.year
            month = month or today.month
        
        month_start = date(year, month, 1)
        if month == 12:
            month_end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(year, month + 1, 1) - timedelta(days=1)
        
        return await self.get_metrics_by_period(
            MetricPeriod.MONTHLY,
            month_start,
            month_end,
            service_levels
        )
    
    async def get_comparative_metrics(
        self,
        current_period: MetricPeriod,
        periods_back: int = 1,
        service_levels: Optional[List[ServiceLevel]] = None
    ) -> Dict[str, AggregatedMetrics]:
        """Obtém métricas comparativas entre períodos"""
        
        periods = {}
        
        for i in range(periods_back + 1):
            if current_period == MetricPeriod.DAILY:
                target_date = date.today() - timedelta(days=i)
                metrics = await self.get_daily_metrics(target_date, service_levels)
                period_key = f"day_{i}" if i > 0 else "current"
            
            elif current_period == MetricPeriod.WEEKLY:
                today = date.today()
                week_start = today - timedelta(days=today.weekday() + (7 * i))
                metrics = await self.get_weekly_metrics(week_start, service_levels)
                period_key = f"week_{i}" if i > 0 else "current"
            
            elif current_period == MetricPeriod.MONTHLY:
                today = date.today()
                target_month = today.month - i
                target_year = today.year
                
                while target_month <= 0:
                    target_month += 12
                    target_year -= 1
                
                metrics = await self.get_monthly_metrics(target_year, target_month, service_levels)
                period_key = f"month_{i}" if i > 0 else "current"
            
            else:
                raise ValueError(f"Período {current_period} não suportado para comparação")
            
            periods[period_key] = metrics
        
        return periods
    
    async def _get_service_level_metrics(
        self,
        service_level: ServiceLevel,
        start_date: date,
        end_date: date
    ) -> ServiceLevelMetric:
        """Obtém métricas para um nível de serviço específico"""
        
        date_range = DateRange(start_date=start_date, end_date=end_date)
        
        # Contadores por status
        status_counts = {}
        total_tickets = 0
        
        # Obter contagem para cada status
        for status in TicketStatus:
            try:
                filters = TicketFilters(
                    service_level=[service_level],
                    status=[status],
                    date_range=date_range
                )
                
                count = await self._count_tickets_with_filters(filters)
                status_counts[status] = count
                total_tickets += count
                
            except Exception as e:
                self.logger.warning(
                    f"Erro ao obter contagem para {service_level.name}/{status.name}: {e}"
                )
                status_counts[status] = 0
        
        # Obter backlog (tickets não resolvidos de períodos anteriores)
        backlog_count = await self._get_backlog_count(service_level, start_date)
        
        return ServiceLevelMetric(
            service_level=service_level,
            period_start=start_date,
            period_end=end_date,
            total_tickets=total_tickets,
            new_tickets=status_counts.get(TicketStatus.NOVO, 0),
            in_progress_tickets=(
                status_counts.get(TicketStatus.PROCESSANDO_ATRIBUIDO, 0) +
                status_counts.get(TicketStatus.PROCESSANDO_PLANEJADO, 0)
            ),
            resolved_tickets=status_counts.get(TicketStatus.SOLUCIONADO, 0),
            closed_tickets=status_counts.get(TicketStatus.FECHADO, 0),
            pending_tickets=status_counts.get(TicketStatus.PENDENTE, 0),
            backlog_count=backlog_count
        )
    
    async def _count_tickets_with_filters(self, filters: TicketFilters) -> int:
        """Conta tickets com filtros específicos"""
        try:
            # Usar paginação mínima apenas para obter contagem
            pagination = PaginationParams(page=1, page_size=1)
            
            query_builder = GLPIQueryBuilder()
            query_params = (
                query_builder
                .add_filters(filters)
                .add_pagination(pagination)
                .build()
            )
            
            response = await self.glpi_client.search_tickets(query_params)
            
            # Extrair contagem total do Content-Range
            if 'content_range' in response:
                content_range = response['content_range']
                try:
                    total_str = content_range.split('/')[-1]
                    return int(total_str)
                except (ValueError, IndexError):
                    pass
            
            # Fallback: contar itens retornados
            return len(response.get('data', []))
            
        except Exception as e:
            self.logger.error(f"Erro ao contar tickets: {e}")
            return 0
    
    async def _get_backlog_count(
        self,
        service_level: ServiceLevel,
        period_start: date
    ) -> int:
        """Obtém contagem de backlog (tickets não resolvidos de períodos anteriores)"""
        try:
            # Tickets criados antes do período e ainda não resolvidos
            filters = TicketFilters(
                service_level=[service_level],
                status=[
                    TicketStatus.NOVO,
                    TicketStatus.PROCESSANDO_ATRIBUIDO,
                    TicketStatus.PROCESSANDO_PLANEJADO,
                    TicketStatus.PENDENTE
                ],
                date_range=DateRange(
                    start_date=None,
                    end_date=period_start - timedelta(days=1)
                )
            )
            
            return await self._count_tickets_with_filters(filters)
            
        except Exception as e:
            self.logger.warning(f"Erro ao obter backlog para {service_level.name}: {e}")
            return 0
    
    def _calculate_period_dates(
        self,
        period: MetricPeriod,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> tuple[date, date]:
        """Calcula datas de início e fim para um período"""
        today = date.today()
        
        if period == MetricPeriod.DAILY:
            return start_date or today, end_date or today
        
        elif period == MetricPeriod.WEEKLY:
            if not start_date:
                start_date = today - timedelta(days=today.weekday())
            if not end_date:
                end_date = start_date + timedelta(days=6)
            return start_date, end_date
        
        elif period == MetricPeriod.MONTHLY:
            if not start_date:
                start_date = date(today.year, today.month, 1)
            if not end_date:
                if today.month == 12:
                    end_date = date(today.year + 1, 1, 1) - timedelta(days=1)
                else:
                    end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)
            return start_date, end_date
        
        elif period == MetricPeriod.QUARTERLY:
            if not start_date:
                quarter = (today.month - 1) // 3 + 1
                start_date = date(today.year, (quarter - 1) * 3 + 1, 1)
            if not end_date:
                quarter = (start_date.month - 1) // 3 + 1
                if quarter == 4:
                    end_date = date(start_date.year + 1, 1, 1) - timedelta(days=1)
                else:
                    end_date = date(start_date.year, quarter * 3 + 1, 1) - timedelta(days=1)
            return start_date, end_date
        
        elif period == MetricPeriod.YEARLY:
            if not start_date:
                start_date = date(today.year, 1, 1)
            if not end_date:
                end_date = date(start_date.year, 12, 31)
            return start_date, end_date
        
        else:
            # CUSTOM - usar datas fornecidas ou padrão para hoje
            return start_date or today, end_date or today


# Factory functions
def create_aggregated_metrics_use_case(glpi_client: GLPIResilientClient) -> AggregatedMetricsUseCase:
    """Cria instância do use case de métricas agregadas"""
    return AggregatedMetricsUseCase(glpi_client)


# Funções utilitárias para análise
def calculate_trend(
    current_metrics: AggregatedMetrics,
    previous_metrics: AggregatedMetrics,
    metric_name: str = "total_tickets"
) -> Dict[str, float]:
    """Calcula tendência entre dois períodos"""
    trends = {}
    
    for level in current_metrics.metrics_by_level.keys():
        current_value = getattr(current_metrics.metrics_by_level[level], metric_name, 0)
        previous_value = getattr(previous_metrics.metrics_by_level.get(level), metric_name, 0) if previous_metrics.metrics_by_level.get(level) else 0
        
        if previous_value > 0:
            trend = ((current_value - previous_value) / previous_value) * 100
        else:
            trend = 100.0 if current_value > 0 else 0.0
        
        trends[level.name] = trend
    
    return trends


def get_performance_summary(metrics: AggregatedMetrics) -> Dict[str, Any]:
    """Gera resumo de performance"""
    total = metrics.total_metrics
    
    return {
        "period": {
            "type": metrics.period.value,
            "start": metrics.period_start.isoformat(),
            "end": metrics.period_end.isoformat()
        },
        "summary": {
            "total_tickets": total.total_tickets,
            "resolution_rate": round(total.resolution_rate * 100, 2),
            "pending_rate": round(total.pending_rate * 100, 2),
            "avg_resolution_time_hours": total.avg_resolution_time_hours
        },
        "by_level": {
            level.name: {
                "tickets": metric.total_tickets,
                "resolution_rate": round(metric.resolution_rate * 100, 2),
                "pending_rate": round(metric.pending_rate * 100, 2)
            }
            for level, metric in metrics.metrics_by_level.items()
        },
        "generated_at": metrics.generated_at.isoformat()
    }