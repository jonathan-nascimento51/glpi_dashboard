# -*- coding: utf-8 -*-
"""Modulo de observabilidade - logging, metricas e exception handling"""

# Logger
from .logger import (
    setup_logging,
    get_logger,
    set_request_context,
    clear_request_context,
    generate_request_id,
    StructuredLogger
)

# Exceptions
from .exceptions import (
    APIError,
    BusinessError,
    ExternalServiceError,
    ValidationError,
    setup_exception_handlers,
    create_error_response
)

# Middleware
from .middleware import (
    setup_metrics_middleware,
    get_metrics,
    get_metrics_summary,
    CacheMetrics,
    ExternalAPIMetrics,
    MetricsMiddleware
)

# Modules
from . import logger
from . import exceptions
from . import middleware


def setup_observability(app, log_level: str = "INFO", enable_json_logs: bool = True):
    """Setup all observability components for the FastAPI app."""
    setup_logging(level=log_level, enable_json=enable_json_logs)
    setup_exception_handlers(app)
    setup_metrics_middleware(app)

    logger = get_logger(__name__)
    logger.info(
        "Sistema de observabilidade configurado",
        log_level=log_level,
        json_logs=enable_json_logs
    )
    return app

__all__ = [
    # Modules
    "logger",
    "exceptions",
    "middleware",
    # Logger
    "setup_logging",
    "get_logger",
    "set_request_context",
    "clear_request_context",
    "generate_request_id",
    "StructuredLogger",
    # Exceptions
    "APIError",
    "BusinessError",
    "ExternalServiceError",
    "ValidationError",
    "setup_exception_handlers",
    "create_error_response",
    # Middleware
    "setup_metrics_middleware",
    "MetricsMiddleware",
    "get_metrics",
    "get_metrics_summary",
    "CacheMetrics",
    "ExternalAPIMetrics",
    # Setup
    "setup_observability"
]
