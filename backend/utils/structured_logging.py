"""Módulo de logging estruturado JSON para observabilidade.

Este módulo implementa logging estruturado em formato JSON com correlação,
contexto e integração com métricas Prometheus.
"""

import json
import logging
import time
import uuid
from contextvars import ContextVar
from datetime import datetime
from functools import wraps
from typing import Any, Dict, List, Optional, Union

from .prometheus_metrics import prometheus_metrics

# Context variables para correlação
correlation_id_var: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)
operation_context_var: ContextVar[Optional[Dict[str, Any]]] = ContextVar("operation_context", default=None)


class JSONFormatter(logging.Formatter):
    """Formatter para logs estruturados em JSON."""

    def __init__(self, include_extra: bool = True, exclude_fields: Optional[List[str]] = None):
        super().__init__()
        self.include_extra = include_extra
        self.exclude_fields = exclude_fields or []

    def format(self, record: logging.LogRecord) -> str:
        """Formata o log record em JSON estruturado."""
        # Campos base do log
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Adicionar correlation_id se disponível
        correlation_id = correlation_id_var.get()
        if correlation_id:
            log_data["correlation_id"] = correlation_id

        # Adicionar contexto da operação
        operation_context = operation_context_var.get()
        if operation_context:
            log_data["operation"] = operation_context

        # Adicionar informações de exceção
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }

        # Adicionar campos extras do record
        if self.include_extra:
            for key, value in record.__dict__.items():
                if (
                    key
                    not in {
                        "name",
                        "msg",
                        "args",
                        "levelname",
                        "levelno",
                        "pathname",
                        "filename",
                        "module",
                        "lineno",
                        "funcName",
                        "created",
                        "msecs",
                        "relativeCreated",
                        "thread",
                        "threadName",
                        "processName",
                        "process",
                        "getMessage",
                        "exc_info",
                        "exc_text",
                        "stack_info",
                    }
                    and key not in self.exclude_fields
                ):
                    try:
                        # Tentar serializar o valor
                        json.dumps(value)
                        log_data[key] = value
                    except (TypeError, ValueError):
                        # Se não conseguir serializar, converter para string
                        log_data[key] = str(value)

        # Sanitizar dados sensíveis
        log_data = self._sanitize_sensitive_data(log_data)

        return json.dumps(log_data, ensure_ascii=False, separators=(",", ":"))

    def _sanitize_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove ou anonimiza dados sensíveis dos logs."""
        sensitive_fields = {
            "password",
            "token",
            "secret",
            "key",
            "authorization",
            "cookie",
            "session",
            "csrf",
            "api_key",
            "access_token",
        }

        def sanitize_value(key: str, value: Any) -> Any:
            if isinstance(key, str) and any(field in key.lower() for field in sensitive_fields):
                if isinstance(value, str) and len(value) > 8:
                    return f"{value[:4]}***{value[-4:]}"
                return "***"

            if isinstance(value, dict):
                return {k: sanitize_value(k, v) for k, v in value.items()}
            elif isinstance(value, list):
                return [sanitize_value(f"item_{i}", item) for i, item in enumerate(value)]

            return value

        return {k: sanitize_value(k, v) for k, v in data.items()}


class StructuredLogger:
    """Logger estruturado com contexto e correlação."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._setup_formatter()

    def _setup_formatter(self):
        """Configura o formatter JSON se não estiver configurado."""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(JSONFormatter())
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def generate_correlation_id(self) -> str:
        """Gera um novo correlation ID."""
        return str(uuid.uuid4())

    def set_correlation_id(self, correlation_id: str):
        """Define o correlation ID para o contexto atual."""
        correlation_id_var.set(correlation_id)

    def get_correlation_id(self) -> Optional[str]:
        """Obtém o correlation ID atual."""
        return correlation_id_var.get()

    def set_operation_context(self, operation: str, **kwargs):
        """Define o contexto da operação atual."""
        context = {
            "name": operation,
            "start_time": datetime.utcnow().isoformat() + "Z",
            **kwargs,
        }
        operation_context_var.set(context)

    def clear_operation_context(self):
        """Limpa o contexto da operação."""
        operation_context_var.set(None)

    def log_operation_start(self, operation: str, **kwargs):
        """Registra o início de uma operação."""
        correlation_id = self.get_correlation_id() or self.generate_correlation_id()
        self.set_correlation_id(correlation_id)
        self.set_operation_context(operation, **kwargs)

        self.logger.info(
            f"Iniciando operação: {operation}",
            extra={
                "operation_phase": "start",
                "operation_name": operation,
                "parameters": kwargs,
            },
        )

    def log_operation_step(self, step: str, **kwargs):
        """Registra uma etapa da operação."""
        self.logger.info(
            f"Executando etapa: {step}",
            extra={"operation_phase": "step", "step_name": step, "step_data": kwargs},
        )

    def log_operation_end(self, operation: str, success: bool = True, **kwargs):
        """Registra o fim de uma operação."""
        operation_context = operation_context_var.get()
        duration = None

        if operation_context and "start_time" in operation_context:
            start_time = datetime.fromisoformat(operation_context["start_time"].replace("Z", "+00:00"))
            duration = (datetime.utcnow().replace(tzinfo=start_time.tzinfo) - start_time).total_seconds()

        level = logging.INFO if success else logging.ERROR
        status = "success" if success else "error"

        self.logger.log(
            level,
            f"Operação {status}: {operation}",
            extra={
                "operation_phase": "end",
                "operation_name": operation,
                "operation_status": status,
                "duration_seconds": duration,
                "result": kwargs,
            },
        )

        self.clear_operation_context()

    def log_warning_with_context(self, warning_type: str, message: str, **kwargs):
        """Registra um warning com contexto específico."""
        self.logger.warning(message, extra={"warning_type": warning_type, "warning_data": kwargs})

        # Registrar alerta no Prometheus
        prometheus_metrics.record_alert(warning_type, "warning")

    def log_error_with_context(
        self,
        error_type: str,
        message: str,
        exception: Optional[Exception] = None,
        **kwargs,
    ):
        """Registra um erro com contexto específico."""
        extra_data = {"error_type": error_type, "error_data": kwargs}

        if exception:
            extra_data["exception_type"] = type(exception).__name__
            extra_data["exception_message"] = str(exception)

        self.logger.error(message, extra=extra_data, exc_info=exception is not None)

        # Registrar erro no Prometheus
        prometheus_metrics.record_error(error_type, kwargs.get("component", "unknown"))

    def log_performance_metric(self, metric_name: str, value: float, unit: str = "seconds", **kwargs):
        """Registra uma métrica de performance."""
        self.logger.info(
            f"Métrica de performance: {metric_name} = {value} {unit}",
            extra={
                "metric_type": "performance",
                "metric_name": metric_name,
                "metric_value": value,
                "metric_unit": unit,
                "metric_context": kwargs,
            },
        )

    def log_business_metric(self, metric_name: str, value: Union[int, float], **kwargs):
        """Registra uma métrica de negócio."""
        self.logger.info(
            f"Métrica de negócio: {metric_name} = {value}",
            extra={
                "metric_type": "business",
                "metric_name": metric_name,
                "metric_value": value,
                "metric_context": kwargs,
            },
        )

    def log_audit_event(self, event_type: str, user_id: Optional[str] = None, **kwargs):
        """Registra um evento de auditoria."""
        self.logger.info(
            f"Evento de auditoria: {event_type}",
            extra={
                "event_type": "audit",
                "audit_event": event_type,
                "user_id": user_id,
                "audit_data": kwargs,
            },
        )


# Decorador para instrumentação automática
def with_structured_logging(operation_name: str, logger_name: Optional[str] = None):
    """Decorador para adicionar logging estruturado automático."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = StructuredLogger(logger_name or func.__module__)

            # Extrair parâmetros relevantes (evitar dados sensíveis)
            safe_kwargs = {
                k: v
                for k, v in kwargs.items()
                if not any(sensitive in k.lower() for sensitive in ["password", "token", "secret", "key"])
            }

            logger.log_operation_start(operation_name, **safe_kwargs)

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                logger.log_operation_end(
                    operation_name,
                    success=True,
                    duration=duration,
                    result_type=type(result).__name__,
                )

                logger.log_performance_metric(f"{operation_name}_duration", duration, "seconds")

                return result

            except Exception as e:
                duration = time.time() - start_time

                logger.log_operation_end(operation_name, success=False, duration=duration, error=str(e))

                logger.log_error_with_context(
                    f"{operation_name}_error",
                    f"Erro na operação {operation_name}: {str(e)}",
                    exception=e,
                    component=func.__module__,
                )

                raise

        return wrapper

    return decorator


# Instâncias globais para uso direto
api_logger = StructuredLogger("glpi.api")
glpi_logger = StructuredLogger("glpi.external")
metrics_logger = StructuredLogger("glpi.metrics")
system_logger = StructuredLogger("glpi.system")
audit_logger = StructuredLogger("glpi.audit")


# Funções de conveniência
def log_api_request(method: str, endpoint: str, status_code: int, duration: float, **kwargs):
    """Log estruturado para requisições da API."""
    api_logger.log_performance_metric(
        "api_request_duration",
        duration,
        "seconds",
        method=method,
        endpoint=endpoint,
        status_code=status_code,
        **kwargs,
    )

    if duration > 0.3:  # Alerta para respostas lentas
        api_logger.log_warning_with_context(
            "slow_response",
            f"Resposta lenta detectada: {method} {endpoint} - {duration:.3f}s",
            method=method,
            endpoint=endpoint,
            duration=duration,
            threshold=0.3,
        )


def log_glpi_request(endpoint: str, status_code: int, duration: float, **kwargs):
    """Log estruturado para requisições ao GLPI."""
    glpi_logger.log_performance_metric(
        "glpi_request_duration",
        duration,
        "seconds",
        endpoint=endpoint,
        status_code=status_code,
        **kwargs,
    )


def log_metrics_processing(query_type: str, duration: float, result_count: int = 0, **kwargs):
    """Log estruturado para processamento de métricas."""
    metrics_logger.log_performance_metric(
        "metrics_processing_duration",
        duration,
        "seconds",
        query_type=query_type,
        result_count=result_count,
        **kwargs,
    )

    if result_count == 0:
        metrics_logger.log_warning_with_context(
            "zero_metrics",
            f"Métricas zeradas detectadas: {query_type}",
            query_type=query_type,
            **kwargs,
        )


def log_system_health(component: str, status: str, **kwargs):
    """Log estruturado para saúde do sistema."""
    system_logger.log_business_metric(
        f"{component}_health",
        1 if status == "healthy" else 0,
        component=component,
        status=status,
        **kwargs,
    )
