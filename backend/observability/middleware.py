# -*- coding: utf-8 -*-
"""Middleware para métricas de performance, latência e observabilidade"""

import time
from typing import Callable, Dict, Any, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from prometheus_client import Counter, Histogram, Gauge, generate_latest

from .logger import (
    get_logger,
    set_request_context,
    generate_request_id,
    clear_request_context,
)

logger = get_logger(__name__)

# Métricas Prometheus
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status_code"]
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint", "status_code"],
)

REQUEST_SIZE = Histogram(
    "http_request_size_bytes", "HTTP request size in bytes", ["method", "endpoint"]
)

RESPONSE_SIZE = Histogram(
    "http_response_size_bytes",
    "HTTP response size in bytes",
    ["method", "endpoint", "status_code"],
)

ACTIVE_REQUESTS = Gauge("http_requests_active", "Number of active HTTP requests")

CACHE_HITS = Counter(
    "cache_hits_total", "Total cache hits", ["cache_type", "key_pattern"]
)

CACHE_MISSES = Counter(
    "cache_misses_total", "Total cache misses", ["cache_type", "key_pattern"]
)

EXTERNAL_API_CALLS = Counter(
    "external_api_calls_total",
    "Total external API calls",
    ["service", "endpoint", "status_code"],
)

EXTERNAL_API_DURATION = Histogram(
    "external_api_duration_seconds",
    "External API call duration in seconds",
    ["service", "endpoint"],
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware para coleta de métricas de performance"""

    def __init__(self, app: ASGIApp, exclude_paths: Optional[list] = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/metrics",
            "/health",
            "/docs",
            "/openapi.json",
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Processa request e coleta métricas"""

        # Gerar request ID e configurar contexto
        request_id = generate_request_id()
        set_request_context(request_id)

        # Adicionar request_id aos headers da response
        start_time = time.time()
        path = request.url.path
        method = request.method

        # Incrementar requests ativos
        ACTIVE_REQUESTS.inc()

        # Calcular tamanho da request
        request_size = 0
        if hasattr(request, "body"):
            try:
                body = await request.body()
                request_size = len(body)
            except:
                pass

        # Log da request
        if path not in self.exclude_paths:
            logger.api_request(
                request,
                request_size=request_size,
                user_agent=request.headers.get("user-agent", "unknown"),
            )

        try:
            # Processar request
            response = await call_next(request)

            # Calcular métricas
            duration = time.time() - start_time
            status_code = str(response.status_code)

            # Calcular tamanho da response
            response_size = 0
            if hasattr(response, "body"):
                try:
                    response_size = len(response.body)
                except:
                    pass

            # Registrar métricas (exceto para paths excluídos)
            if path not in self.exclude_paths:
                endpoint = self._normalize_path(path)

                REQUEST_COUNT.labels(
                    method=method, endpoint=endpoint, status_code=status_code
                ).inc()

                REQUEST_DURATION.labels(
                    method=method, endpoint=endpoint, status_code=status_code
                ).observe(duration)

                REQUEST_SIZE.labels(method=method, endpoint=endpoint).observe(
                    request_size
                )

                RESPONSE_SIZE.labels(
                    method=method, endpoint=endpoint, status_code=status_code
                ).observe(response_size)

                # Log da response
                logger.api_response(
                    request,
                    status_code=response.status_code,
                    duration_ms=duration * 1000,
                    response_size=response_size,
                )

            # Adicionar headers de observabilidade
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration:.3f}s"

            return response

        except Exception as e:
            # Registrar erro
            duration = time.time() - start_time

            if path not in self.exclude_paths:
                endpoint = self._normalize_path(path)

                REQUEST_COUNT.labels(
                    method=method, endpoint=endpoint, status_code="500"
                ).inc()

                REQUEST_DURATION.labels(
                    method=method, endpoint=endpoint, status_code="500"
                ).observe(duration)

                logger.error(
                    f"Request failed: {str(e)}",
                    path=path,
                    method=method,
                    duration=duration * 1000,
                    exc_info=True,
                )

            raise

        finally:
            # Decrementar requests ativos
            ACTIVE_REQUESTS.dec()

            # Limpar contexto
            clear_request_context()

    def _normalize_path(self, path: str) -> str:
        """Normaliza path para métricas (remove IDs dinâmicos)"""
        # Substituir IDs numéricos por placeholder
        import re

        normalized = re.sub(r"/\d+", "/{id}", path)
        normalized = re.sub(r"/[a-f0-9-]{36}", "/{uuid}", normalized)  # UUIDs
        return normalized


class CacheMetrics:
    """Classe para registrar métricas de cache"""

    @staticmethod
    def record_hit(cache_type: str, key_pattern: str = "default"):
        """Registra cache hit"""
        CACHE_HITS.labels(cache_type=cache_type, key_pattern=key_pattern).inc()
        logger.debug(
            f"Cache hit: {cache_type}", cache_type=cache_type, key_pattern=key_pattern
        )

    @staticmethod
    def record_miss(cache_type: str, key_pattern: str = "default"):
        """Registra cache miss"""
        CACHE_MISSES.labels(cache_type=cache_type, key_pattern=key_pattern).inc()
        logger.debug(
            f"Cache miss: {cache_type}", cache_type=cache_type, key_pattern=key_pattern
        )


class ExternalAPIMetrics:
    """Classe para registrar métricas de APIs externas"""

    @staticmethod
    def record_call(
        service: str, endpoint: str, status_code: int, duration: float, **kwargs
    ):
        """Registra chamada para API externa"""
        EXTERNAL_API_CALLS.labels(
            service=service, endpoint=endpoint, status_code=str(status_code)
        ).inc()

        EXTERNAL_API_DURATION.labels(service=service, endpoint=endpoint).observe(
            duration
        )

        logger.info(
            f"External API call: {service} {endpoint}",
            service=service,
            endpoint=endpoint,
            status_code=status_code,
            duration=duration * 1000,
            **kwargs,
        )


def get_metrics() -> str:
    """Retorna métricas no formato Prometheus"""
    return generate_latest()


def get_metrics_summary() -> Dict[str, Any]:
    """Retorna resumo das métricas em formato JSON"""
    from prometheus_client import REGISTRY

    metrics_data = {}

    for collector in REGISTRY._collector_to_names:
        for metric in collector.collect():
            metric_name = metric.name
            metric_data = {
                "help": metric.documentation,
                "type": metric.type,
                "samples": [],
            }

            for sample in metric.samples:
                metric_data["samples"].append(
                    {
                        "name": sample.name,
                        "labels": sample.labels,
                        "value": sample.value,
                    }
                )

            metrics_data[metric_name] = metric_data

    return metrics_data


def setup_metrics_middleware(app, exclude_paths: Optional[list] = None):
    """Configura middleware de métricas na aplicação"""
    app.add_middleware(MetricsMiddleware, exclude_paths=exclude_paths)
    logger.info("Metrics middleware configurado")
