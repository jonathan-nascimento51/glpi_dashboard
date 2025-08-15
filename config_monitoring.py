#!/usr/bin/env python3
"""
Configuração do Sistema de Monitoramento Proativo - GLPI Dashboard

Este arquivo contém todas as configurações para o sistema de monitoramento,
incluindo limites, alertas, notificações e integrações.

Autor: Sistema de Otimização GLPI Dashboard
Data: 2025-01-14
"""

from datetime import timedelta
from typing import Dict, Any, List

# =============================================================================
# CONFIGURAÇÕES PRINCIPAIS
# =============================================================================

MONITORING_CONFIG = {
    # Intervalo de monitoramento (segundos)
    "monitoring_interval": 30,
    
    # URLs dos serviços
    "api_base_url": "http://localhost:8000",
    "frontend_url": "http://localhost:8050",
    "database_url": "postgresql://localhost:5432/glpi",
    
    # Retenção de dados
    "retention_days": 30,
    "max_history_size": 1000,
    
    # Timeouts
    "api_timeout": 10,  # segundos
    "database_timeout": 5,  # segundos
    
    # Canais de alerta
    "alert_channels": {
        "file": True,
        "email": False,
        "slack": False,
        "webhook": False
    },
    
    # Configurações de notificação
    "notification_config": {
        "email": {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "",
            "password": "",
            "recipients": []
        },
        "slack": {
            "webhook_url": "",
            "channel": "#alerts",
            "username": "GLPI Monitor"
        },
        "webhook": {
            "url": "",
            "headers": {},
            "timeout": 5
        }
    },
    
    # Configurações de relatórios
    "reporting": {
        "auto_generate": True,
        "interval_hours": 6,
        "formats": ["json", "html"],
        "include_charts": True
    }
}

# =============================================================================
# LIMITES E THRESHOLDS
# =============================================================================

METRIC_THRESHOLDS = {
    # Métricas de Tickets
    "tickets_by_status": {
        "min_value": 0,
        "max_value": None,
        "zero_tolerance": True,
        "change_threshold": 0.3,  # 30%
        "consecutive_failures": 3,
        "alert_levels": {
            "zero_data": "CRITICAL",
            "sudden_change": "WARNING"
        }
    },
    
    "total_open_tickets": {
        "min_value": 0,
        "max_value": 10000,
        "zero_tolerance": True,
        "change_threshold": 0.25,
        "consecutive_failures": 2,
        "alert_levels": {
            "zero_data": "CRITICAL",
            "high_volume": "WARNING"
        }
    },
    
    "resolution_rate": {
        "min_value": 0.0,
        "max_value": 1.0,
        "expected_range": (0.1, 0.9),
        "change_threshold": 0.2,
        "consecutive_failures": 3,
        "alert_levels": {
            "low_rate": "WARNING",
            "zero_rate": "CRITICAL"
        }
    },
    
    # Métricas de Performance
    "api_response_time": {
        "min_value": 0,
        "max_value": 5000,  # 5 segundos
        "warning_threshold": 2000,  # 2 segundos
        "change_threshold": 0.5,
        "consecutive_failures": 3,
        "alert_levels": {
            "slow_response": "WARNING",
            "very_slow": "CRITICAL"
        }
    },
    
    "database_response_time": {
        "min_value": 0,
        "max_value": 3000,  # 3 segundos
        "warning_threshold": 1000,  # 1 segundo
        "change_threshold": 0.4,
        "consecutive_failures": 2,
        "alert_levels": {
            "slow_query": "WARNING",
            "timeout": "CRITICAL"
        }
    },
    
    # Métricas de Sistema
    "cpu_usage": {
        "min_value": 0.0,
        "max_value": 0.80,  # 80%
        "warning_threshold": 0.70,  # 70%
        "change_threshold": 0.3,
        "consecutive_failures": 3,
        "alert_levels": {
            "high_cpu": "WARNING",
            "critical_cpu": "CRITICAL"
        }
    },
    
    "memory_usage": {
        "min_value": 0.0,
        "max_value": 0.85,  # 85%
        "warning_threshold": 0.75,  # 75%
        "change_threshold": 0.2,
        "consecutive_failures": 3,
        "alert_levels": {
            "high_memory": "WARNING",
            "critical_memory": "CRITICAL"
        }
    },
    
    "disk_usage": {
        "min_value": 0.0,
        "max_value": 0.90,  # 90%
        "warning_threshold": 0.80,  # 80%
        "change_threshold": 0.1,
        "consecutive_failures": 2,
        "alert_levels": {
            "high_disk": "WARNING",
            "critical_disk": "CRITICAL"
        }
    },
    
    # Métricas de Conectividade
    "database_connections": {
        "min_value": 0,
        "max_value": 100,
        "warning_threshold": 80,
        "change_threshold": 0.4,
        "consecutive_failures": 3,
        "alert_levels": {
            "high_connections": "WARNING",
            "connection_limit": "CRITICAL"
        }
    },
    
    "api_error_rate": {
        "min_value": 0.0,
        "max_value": 0.05,  # 5%
        "warning_threshold": 0.02,  # 2%
        "change_threshold": 0.5,
        "consecutive_failures": 2,
        "alert_levels": {
            "high_errors": "WARNING",
            "critical_errors": "CRITICAL"
        }
    }
}

# =============================================================================
# CONFIGURAÇÕES DE ALERTAS
# =============================================================================

ALERT_CONFIG = {
    # Configurações gerais
    "spam_prevention": {
        "min_interval_seconds": 300,  # 5 minutos
        "max_alerts_per_hour": 20,
        "escalation_threshold": 5
    },
    
    # Configurações por nível
    "level_config": {
        "INFO": {
            "enabled": True,
            "notification_channels": ["file"],
            "auto_resolve_minutes": 60
        },
        "WARNING": {
            "enabled": True,
            "notification_channels": ["file", "slack"],
            "auto_resolve_minutes": 30,
            "escalate_after_minutes": 60
        },
        "CRITICAL": {
            "enabled": True,
            "notification_channels": ["file", "email", "slack", "webhook"],
            "auto_resolve_minutes": 15,
            "escalate_after_minutes": 30,
            "require_acknowledgment": True
        },
        "EMERGENCY": {
            "enabled": True,
            "notification_channels": ["file", "email", "slack", "webhook"],
            "auto_resolve_minutes": 5,
            "immediate_notification": True,
            "require_acknowledgment": True,
            "escalate_immediately": True
        }
    },
    
    # Configurações de escalação
    "escalation": {
        "enabled": True,
        "levels": [
            {
                "name": "Level 1 - Operations",
                "contacts": ["ops@company.com"],
                "delay_minutes": 0
            },
            {
                "name": "Level 2 - Engineering",
                "contacts": ["eng@company.com"],
                "delay_minutes": 30
            },
            {
                "name": "Level 3 - Management",
                "contacts": ["mgmt@company.com"],
                "delay_minutes": 60
            }
        ]
    }
}

# =============================================================================
# ENDPOINTS CRÍTICOS PARA MONITORAMENTO
# =============================================================================

CRITICAL_ENDPOINTS = [
    {
        "name": "API Health",
        "url": "/health",
        "method": "GET",
        "expected_status": 200,
        "timeout": 5,
        "critical": True,
        "check_interval": 30
    },
    {
        "name": "Tickets Summary",
        "url": "/api/v1/tickets/summary",
        "method": "GET",
        "expected_status": 200,
        "timeout": 10,
        "critical": True,
        "check_interval": 60,
        "validate_response": True
    },
    {
        "name": "Tickets by Status",
        "url": "/api/v1/tickets/by-status",
        "method": "GET",
        "expected_status": 200,
        "timeout": 10,
        "critical": True,
        "check_interval": 60,
        "validate_response": True
    },
    {
        "name": "Metrics",
        "url": "/metrics",
        "method": "GET",
        "expected_status": 200,
        "timeout": 5,
        "critical": False,
        "check_interval": 120
    },
    {
        "name": "OpenAPI Docs",
        "url": "/docs",
        "method": "GET",
        "expected_status": 200,
        "timeout": 5,
        "critical": False,
        "check_interval": 300
    }
]

# =============================================================================
# CONFIGURAÇÕES DE VALIDAÇÃO DE DADOS
# =============================================================================

DATA_VALIDATION = {
    "tickets_summary": {
        "required_fields": ["tickets_by_status", "total_tickets", "open_tickets"],
        "validation_rules": {
            "total_tickets": {
                "type": "integer",
                "min_value": 0,
                "max_value": 100000
            },
            "tickets_by_status": {
                "type": "dict",
                "required_keys": ["new", "assigned", "planned", "pending", "solved", "closed"],
                "value_type": "integer",
                "min_sum": 0
            }
        }
    },
    
    "system_metrics": {
        "required_fields": ["cpu_percent", "memory_percent", "disk_percent"],
        "validation_rules": {
            "cpu_percent": {
                "type": "float",
                "min_value": 0.0,
                "max_value": 100.0
            },
            "memory_percent": {
                "type": "float",
                "min_value": 0.0,
                "max_value": 100.0
            },
            "disk_percent": {
                "type": "float",
                "min_value": 0.0,
                "max_value": 100.0
            }
        }
    }
}

# =============================================================================
# CONFIGURAÇÕES DE INTEGRAÇÃO
# =============================================================================

INTEGRATION_CONFIG = {
    # Knowledge Graph
    "knowledge_graph": {
        "enabled": True,
        "store_alerts": True,
        "store_metrics": True,
        "entity_types": {
            "alert": "MonitoringAlert",
            "metric": "SystemMetric",
            "incident": "SystemIncident"
        }
    },
    
    # Git Integration
    "git": {
        "enabled": True,
        "auto_commit_reports": False,
        "branch_for_reports": "monitoring-reports",
        "commit_message_template": "chore: monitoring report {timestamp}"
    },
    
    # External Monitoring
    "external_monitoring": {
        "prometheus": {
            "enabled": False,
            "push_gateway_url": "",
            "job_name": "glpi-dashboard"
        },
        "grafana": {
            "enabled": False,
            "dashboard_url": "",
            "api_key": ""
        }
    }
}

# =============================================================================
# CONFIGURAÇÕES DE AMBIENTE
# =============================================================================

ENVIRONMENT_CONFIG = {
    "development": {
        "monitoring_interval": 60,  # Menos frequente
        "alert_channels": {"file": True},
        "log_level": "DEBUG",
        "retention_days": 7
    },
    
    "staging": {
        "monitoring_interval": 45,
        "alert_channels": {"file": True, "slack": True},
        "log_level": "INFO",
        "retention_days": 14
    },
    
    "production": {
        "monitoring_interval": 30,
        "alert_channels": {"file": True, "email": True, "slack": True, "webhook": True},
        "log_level": "WARNING",
        "retention_days": 30,
        "high_availability": True,
        "backup_monitoring": True
    }
}

# =============================================================================
# CONFIGURAÇÕES DE SEGURANÇA
# =============================================================================

SECURITY_CONFIG = {
    "authentication": {
        "required": False,  # Para desenvolvimento
        "api_key_header": "X-Monitoring-Key",
        "allowed_ips": [],  # Vazio = todos permitidos
        "rate_limiting": {
            "enabled": True,
            "requests_per_minute": 60
        }
    },
    
    "data_protection": {
        "encrypt_sensitive_data": True,
        "mask_credentials_in_logs": True,
        "sanitize_error_messages": True
    },
    
    "audit": {
        "log_all_actions": True,
        "include_user_info": True,
        "retention_days": 90
    }
}

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def get_config_for_environment(env: str = "development") -> Dict[str, Any]:
    """Obter configuração para ambiente específico"""
    base_config = MONITORING_CONFIG.copy()
    env_config = ENVIRONMENT_CONFIG.get(env, ENVIRONMENT_CONFIG["development"])
    
    # Mesclar configurações
    base_config.update(env_config)
    
    return base_config

def get_threshold_for_metric(metric_name: str) -> Dict[str, Any]:
    """Obter threshold para métrica específica"""
    return METRIC_THRESHOLDS.get(metric_name, {})

def get_alert_config_for_level(level: str) -> Dict[str, Any]:
    """Obter configuração de alerta para nível específico"""
    return ALERT_CONFIG["level_config"].get(level, {})

def validate_config() -> List[str]:
    """Validar configurações e retornar lista de erros"""
    errors = []
    
    # Validar URLs
    required_urls = ["api_base_url", "frontend_url"]
    for url_key in required_urls:
        if not MONITORING_CONFIG.get(url_key):
            errors.append(f"URL obrigatória não configurada: {url_key}")
    
    # Validar thresholds
    for metric_name, threshold in METRIC_THRESHOLDS.items():
        if threshold.get("min_value") is not None and threshold.get("max_value") is not None:
            if threshold["min_value"] >= threshold["max_value"]:
                errors.append(f"Threshold inválido para {metric_name}: min >= max")
    
    # Validar canais de alerta
    enabled_channels = [k for k, v in MONITORING_CONFIG["alert_channels"].items() if v]
    if not enabled_channels:
        errors.append("Nenhum canal de alerta habilitado")
    
    return errors

# Validar configurações na importação
if __name__ == "__main__":
    validation_errors = validate_config()
    if validation_errors:
        print(" Erros de configuração encontrados:")
        for error in validation_errors:
            print(f"  - {error}")
    else:
        print(" Configurações válidas")
