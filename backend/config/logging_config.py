# -*- coding: utf-8 -*-
"""
Configuração de logging estruturado para o GLPI Dashboard.
"""

import logging
import logging.config
import os
from typing import Dict, Any


def get_logging_config(log_level: str = "INFO", log_file: str = None) -> Dict[str, Any]:
    """
    Retorna configuração de logging estruturado.

    Args:
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Caminho para arquivo de log (opcional)

    Returns:
        Dicionário de configuração para logging.config.dictConfig
    """

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "utils.structured_logger.JSONFormatter",
                "include_extra_fields": True,
            },
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "json",
                "stream": "ext://sys.stdout",
            }
        },
        "loggers": {
            "glpi_service": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "api_service": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "structured_logger": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False,
            },
        },
        "root": {"level": log_level, "handlers": ["console"]},
    }

    # Adicionar handler de arquivo se especificado
    if log_file:
        # Criar diretório se não existir
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "json",
            "filename": log_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf-8",
        }

        # Adicionar handler de arquivo aos loggers
        for logger_name in config["loggers"]:
            config["loggers"][logger_name]["handlers"].append("file")
        config["root"]["handlers"].append("file")

    return config


def configure_structured_logging(log_level: str = "INFO", log_file: str = None):
    """
    Configura o sistema de logging estruturado.

    Args:
        log_level: Nível de log
        log_file: Caminho para arquivo de log (opcional)
    """
    config = get_logging_config(log_level, log_file)
    logging.config.dictConfig(config)


# Configurações específicas para diferentes ambientes
class LoggingConfig:
    """Configurações de logging para diferentes ambientes."""

    @staticmethod
    def development():
        """Configuração para ambiente de desenvolvimento."""
        return {
            "log_level": "DEBUG",
            "log_file": "logs/glpi_dashboard_dev.log",
            "console_output": True,
        }

    @staticmethod
    def production():
        """Configuração para ambiente de produção."""
        return {
            "log_level": "INFO",
            "log_file": "logs/glpi_dashboard_prod.log",
            "console_output": False,
        }

    @staticmethod
    def testing():
        """Configuração para ambiente de testes."""
        return {"log_level": "WARNING", "log_file": None, "console_output": True}


# Configurações para integração com serviços de monitoramento
class MonitoringIntegration:
    """Configurações para integração com serviços de monitoramento."""

    @staticmethod
    def elk_stack_config():
        """
        Configuração para integração com ELK Stack (Elasticsearch, Logstash, Kibana).

        Returns:
            Dicionário com configurações recomendadas
        """
        return {
            "log_format": "json",
            "fields": {
                "service": "glpi_dashboard",
                "environment": os.getenv("ENVIRONMENT", "development"),
                "version": os.getenv("APP_VERSION", "1.0.0"),
            },
            "logstash": {
                "host": os.getenv("LOGSTASH_HOST", "localhost"),
                "port": int(os.getenv("LOGSTASH_PORT", "5044")),
                "protocol": "tcp",
            },
            "index_pattern": "glpi-dashboard-*",
        }

    @staticmethod
    def grafana_loki_config():
        """
        Configuração para integração com Grafana Loki.

        Returns:
            Dicionário com configurações recomendadas
        """
        return {
            "log_format": "json",
            "labels": {
                "service": "glpi_dashboard",
                "environment": os.getenv("ENVIRONMENT", "development"),
                "level": "${level}",
                "logger": "${logger_name}",
            },
            "loki": {
                "url": os.getenv("LOKI_URL", "http://localhost:3100"),
                "push_endpoint": "/loki/api/v1/push",
            },
        }

    @staticmethod
    def prometheus_config():
        """
        Configuração para métricas do Prometheus.

        Returns:
            Dicionário com configurações de métricas
        """
        return {
            "metrics": {
                "api_calls_total": {
                    "type": "counter",
                    "description": "Total number of API calls",
                    "labels": ["method", "endpoint", "status"],
                },
                "api_call_duration_seconds": {
                    "type": "histogram",
                    "description": "API call duration in seconds",
                    "labels": ["method", "endpoint"],
                    "buckets": [0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
                },
                "errors_total": {
                    "type": "counter",
                    "description": "Total number of errors",
                    "labels": ["error_type", "service"],
                },
            },
            "prometheus": {
                "gateway_url": os.getenv(
                    "PROMETHEUS_GATEWAY_URL", "http://localhost:9091"
                ),
                "job_name": "glpi_dashboard",
            },
        }
