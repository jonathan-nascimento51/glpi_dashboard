# -*- coding: utf-8 -*-
"""Sistema de métricas Prometheus para monitoramento do cliente GLPI"""

import time
import functools
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import logging
from contextlib import contextmanager

try:
    from prometheus_client import (
        Counter, Histogram, Gauge, Info, CollectorRegistry,
        generate_latest, CONTENT_TYPE_LATEST
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # Fallback classes para quando prometheus_client não estiver disponível
    class Counter:
        def __init__(self, *args, **kwargs):
            self._value = 0
        def inc(self, amount=1):
            self._value += amount
        def labels(self, **kwargs):
            return self
    
    class Histogram:
        def __init__(self, *args, **kwargs):
            self._observations = []
        def observe(self, amount):
            self._observations.append(amount)
        def labels(self, **kwargs):
            return self
        def time(self):
            return _HistogramTimer(self)
    
    class Gauge:
        def __init__(self, *args, **kwargs):
            self._value = 0
        def set(self, value):
            self._value = value
        def inc(self, amount=1):
            self._value += amount
        def dec(self, amount=1):
            self._value -= amount
        def labels(self, **kwargs):
            return self
    
    class Info:
        def __init__(self, *args, **kwargs):
            self._info = {}
        def info(self, data):
            self._info = data
        def labels(self, **kwargs):
            return self
    
    class CollectorRegistry:
        def __init__(self):
            pass
    
    def generate_latest(registry):
        return b"# Prometheus metrics not available\n"
    
    CONTENT_TYPE_LATEST = "text/plain"
    
    class _HistogramTimer:
        def __init__(self, histogram):
            self.histogram = histogram
            self.start_time = None
        
        def __enter__(self):
            self.start_time = time.time()
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.start_time:
                duration = time.time() - self.start_time
                self.histogram.observe(duration)


logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Tipos de métricas"""
    COUNTER = "counter"
    HISTOGRAM = "histogram"
    GAUGE = "gauge"
    INFO = "info"


class OperationType(Enum):
    """Tipos de operações monitoradas"""
    AUTHENTICATION = "authentication"
    SEARCH_TICKETS = "search_tickets"
    GET_TICKET = "get_ticket"
    SESSION_RENEWAL = "session_renewal"
    CIRCUIT_BREAKER = "circuit_breaker"
    RETRY = "retry"
    AGGREGATED_METRICS = "aggregated_metrics"


@dataclass
class MetricEvent:
    """Evento de métrica"""
    operation: OperationType
    status: str  # success, error, timeout, etc.
    duration_seconds: Optional[float] = None
    error_type: Optional[str] = None
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class GLPIMetrics:
    """Coletor de métricas para o cliente GLPI"""
    
    def __init__(self, registry: Optional[CollectorRegistry] = None, enable_prometheus: bool = True):
        self.registry = registry or CollectorRegistry()
        self.enable_prometheus = enable_prometheus and PROMETHEUS_AVAILABLE
        self.structured_logs: List[Dict[str, Any]] = []
        
        # Inicializar métricas Prometheus se disponível
        if self.enable_prometheus:
            self._init_prometheus_metrics()
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def _init_prometheus_metrics(self):
        """Inicializa métricas Prometheus"""
        # Contador de requisições
        self.requests_total = Counter(
            'glpi_requests_total',
            'Total number of GLPI API requests',
            ['operation', 'status', 'error_type'],
            registry=self.registry
        )
        
        # Histograma de latência
        self.request_duration = Histogram(
            'glpi_request_duration_seconds',
            'Duration of GLPI API requests in seconds',
            ['operation', 'status'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 25.0, 50.0, 100.0],
            registry=self.registry
        )
        
        # Gauge para sessões ativas
        self.active_sessions = Gauge(
            'glpi_active_sessions',
            'Number of active GLPI sessions',
            registry=self.registry
        )
        
        # Gauge para estado do circuit breaker
        self.circuit_breaker_state = Gauge(
            'glpi_circuit_breaker_state',
            'Circuit breaker state (0=closed, 1=open, 2=half_open)',
            ['operation'],
            registry=self.registry
        )
        
        # Contador de falhas do circuit breaker
        self.circuit_breaker_failures = Counter(
            'glpi_circuit_breaker_failures_total',
            'Total number of circuit breaker failures',
            ['operation'],
            registry=self.registry
        )
        
        # Contador de retries
        self.retries_total = Counter(
            'glpi_retries_total',
            'Total number of retry attempts',
            ['operation', 'retry_reason'],
            registry=self.registry
        )
        
        # Histograma de tempo de retry
        self.retry_delay = Histogram(
            'glpi_retry_delay_seconds',
            'Delay between retry attempts in seconds',
            ['operation'],
            buckets=[0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
            registry=self.registry
        )
        
        # Gauge para métricas de negócio
        self.business_metrics = Gauge(
            'glpi_business_metrics',
            'Business metrics from GLPI',
            ['metric_type', 'service_level', 'status'],
            registry=self.registry
        )
        
        # Info sobre versão e configuração
        self.info = Info(
            'glpi_client_info',
            'Information about GLPI client',
            registry=self.registry
        )
    
    def record_request(self, event: MetricEvent):
        """Registra uma requisição"""
        if self.enable_prometheus:
            # Incrementar contador de requisições
            self.requests_total.labels(
                operation=event.operation.value,
                status=event.status,
                error_type=event.error_type or 'none'
            ).inc()
            
            # Registrar duração se disponível
            if event.duration_seconds is not None:
                self.request_duration.labels(
                    operation=event.operation.value,
                    status=event.status
                ).observe(event.duration_seconds)
        
        # Log estruturado
        self._log_structured_event(event)
    
    def record_circuit_breaker_state(self, operation: OperationType, state: str):
        """Registra estado do circuit breaker"""
        if self.enable_prometheus:
            state_value = {
                'closed': 0,
                'open': 1,
                'half_open': 2
            }.get(state, 0)
            
            self.circuit_breaker_state.labels(
                operation=operation.value
            ).set(state_value)
    
    def record_circuit_breaker_failure(self, operation: OperationType):
        """Registra falha do circuit breaker"""
        if self.enable_prometheus:
            self.circuit_breaker_failures.labels(
                operation=operation.value
            ).inc()
    
    def record_retry(self, operation: OperationType, reason: str, delay_seconds: float):
        """Registra tentativa de retry"""
        if self.enable_prometheus:
            self.retries_total.labels(
                operation=operation.value,
                retry_reason=reason
            ).inc()
            
            self.retry_delay.labels(
                operation=operation.value
            ).observe(delay_seconds)
    
    def set_active_sessions(self, count: int):
        """Define número de sessões ativas"""
        if self.enable_prometheus:
            self.active_sessions.set(count)
    
    def record_business_metric(
        self,
        metric_type: str,
        value: float,
        service_level: Optional[str] = None,
        status: Optional[str] = None
    ):
        """Registra métrica de negócio"""
        if self.enable_prometheus:
            self.business_metrics.labels(
                metric_type=metric_type,
                service_level=service_level or 'all',
                status=status or 'all'
            ).set(value)
    
    def set_client_info(self, info: Dict[str, str]):
        """Define informações do cliente"""
        if self.enable_prometheus:
            self.info.info(info)
    
    def _log_structured_event(self, event: MetricEvent):
        """Registra evento em log estruturado"""
        log_data = {
            'timestamp': event.timestamp.isoformat(),
            'operation': event.operation.value,
            'status': event.status,
            'duration_seconds': event.duration_seconds,
            'error_type': event.error_type,
            'labels': event.labels
        }
        
        # Adicionar à lista de logs estruturados
        self.structured_logs.append(log_data)
        
        # Manter apenas os últimos 1000 eventos
        if len(self.structured_logs) > 1000:
            self.structured_logs = self.structured_logs[-1000:]
        
        # Log usando logger padrão
        if event.status == 'error':
            self.logger.error("GLPI operation failed", extra=log_data)
        elif event.status == 'timeout':
            self.logger.warning("GLPI operation timeout", extra=log_data)
        else:
            self.logger.info("GLPI operation completed", extra=log_data)
    
    def get_prometheus_metrics(self) -> bytes:
        """Retorna métricas no formato Prometheus"""
        if self.enable_prometheus:
            return generate_latest(self.registry)
        else:
            return b"# Prometheus metrics not available\n"
    
    def get_structured_logs(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retorna logs estruturados"""
        if limit:
            return self.structured_logs[-limit:]
        return self.structured_logs.copy()
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas resumidas"""
        if not self.structured_logs:
            return {}
        
        # Contar por operação e status
        operation_stats = {}
        status_stats = {}
        error_stats = {}
        durations = []
        
        for log in self.structured_logs:
            operation = log['operation']
            status = log['status']
            error_type = log.get('error_type')
            duration = log.get('duration_seconds')
            
            # Estatísticas por operação
            if operation not in operation_stats:
                operation_stats[operation] = {'total': 0, 'success': 0, 'error': 0}
            operation_stats[operation]['total'] += 1
            if status == 'success':
                operation_stats[operation]['success'] += 1
            elif status == 'error':
                operation_stats[operation]['error'] += 1
            
            # Estatísticas por status
            status_stats[status] = status_stats.get(status, 0) + 1
            
            # Estatísticas por tipo de erro
            if error_type:
                error_stats[error_type] = error_stats.get(error_type, 0) + 1
            
            # Durações
            if duration is not None:
                durations.append(duration)
        
        # Calcular estatísticas de duração
        duration_stats = {}
        if durations:
            durations.sort()
            duration_stats = {
                'min': min(durations),
                'max': max(durations),
                'avg': sum(durations) / len(durations),
                'p50': durations[len(durations) // 2],
                'p95': durations[int(len(durations) * 0.95)],
                'p99': durations[int(len(durations) * 0.99)]
            }
        
        return {
            'total_events': len(self.structured_logs),
            'operation_stats': operation_stats,
            'status_stats': status_stats,
            'error_stats': error_stats,
            'duration_stats': duration_stats,
            'prometheus_enabled': self.enable_prometheus
        }


# Instância global de métricas
_global_metrics: Optional[GLPIMetrics] = None


def get_metrics() -> GLPIMetrics:
    """Obtém instância global de métricas"""
    global _global_metrics
    if _global_metrics is None:
        _global_metrics = GLPIMetrics()
    return _global_metrics


def init_metrics(registry: Optional[CollectorRegistry] = None, enable_prometheus: bool = True) -> GLPIMetrics:
    """Inicializa sistema de métricas"""
    global _global_metrics
    _global_metrics = GLPIMetrics(registry, enable_prometheus)
    return _global_metrics


# Decoradores para instrumentação automática
def monitor_operation(operation: OperationType, include_args: bool = False):
    """Decorator para monitorar operações"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            metrics = get_metrics()
            start_time = time.time()
            
            labels = {}
            if include_args and args:
                labels['args_count'] = str(len(args))
            if include_args and kwargs:
                labels['kwargs_count'] = str(len(kwargs))
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                event = MetricEvent(
                    operation=operation,
                    status='success',
                    duration_seconds=duration,
                    labels=labels
                )
                metrics.record_request(event)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                error_type = type(e).__name__
                
                event = MetricEvent(
                    operation=operation,
                    status='error',
                    duration_seconds=duration,
                    error_type=error_type,
                    labels=labels
                )
                metrics.record_request(event)
                
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            metrics = get_metrics()
            start_time = time.time()
            
            labels = {}
            if include_args and args:
                labels['args_count'] = str(len(args))
            if include_args and kwargs:
                labels['kwargs_count'] = str(len(kwargs))
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                event = MetricEvent(
                    operation=operation,
                    status='success',
                    duration_seconds=duration,
                    labels=labels
                )
                metrics.record_request(event)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                error_type = type(e).__name__
                
                event = MetricEvent(
                    operation=operation,
                    status='error',
                    duration_seconds=duration,
                    error_type=error_type,
                    labels=labels
                )
                metrics.record_request(event)
                
                raise
        
        # Retornar wrapper apropriado baseado na função
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


@contextmanager
def measure_operation(operation: OperationType, labels: Optional[Dict[str, str]] = None):
    """Context manager para medir operações"""
    metrics = get_metrics()
    start_time = time.time()
    labels = labels or {}
    
    try:
        yield
        duration = time.time() - start_time
        
        event = MetricEvent(
            operation=operation,
            status='success',
            duration_seconds=duration,
            labels=labels
        )
        metrics.record_request(event)
        
    except Exception as e:
        duration = time.time() - start_time
        error_type = type(e).__name__
        
        event = MetricEvent(
            operation=operation,
            status='error',
            duration_seconds=duration,
            error_type=error_type,
            labels=labels
        )
        metrics.record_request(event)
        
        raise


# Funções utilitárias
def record_business_metrics_from_aggregated(aggregated_metrics):
    """Registra métricas de negócio a partir de métricas agregadas"""
    metrics = get_metrics()
    
    # Métricas totais
    total = aggregated_metrics.total_metrics
    metrics.record_business_metric('total_tickets', total.total_tickets)
    metrics.record_business_metric('new_tickets', total.new_tickets)
    metrics.record_business_metric('resolved_tickets', total.resolved_tickets)
    metrics.record_business_metric('pending_tickets', total.pending_tickets)
    metrics.record_business_metric('resolution_rate', total.resolution_rate)
    
    # Métricas por nível
    for level, level_metrics in aggregated_metrics.metrics_by_level.items():
        level_name = level.name
        
        metrics.record_business_metric(
            'level_total_tickets', level_metrics.total_tickets, level_name
        )
        metrics.record_business_metric(
            'level_new_tickets', level_metrics.new_tickets, level_name
        )
        metrics.record_business_metric(
            'level_resolved_tickets', level_metrics.resolved_tickets, level_name
        )
        metrics.record_business_metric(
            'level_pending_tickets', level_metrics.pending_tickets, level_name
        )
        metrics.record_business_metric(
            'level_resolution_rate', level_metrics.resolution_rate, level_name
        )


# Importar asyncio no final para evitar problemas de importação circular
import asyncio