# Configuração do Protocolo de Mudanças Seguras
# GLPI Dashboard - Sistema de Otimização

# Configurações Gerais
CHANGE_PROTOCOL_VERSION = "1.0.0"
BACKUP_RETENTION_DAYS = 30
MAX_CONCURRENT_CHANGES = 3
REQUIRE_APPROVAL_FOR_HIGH_RISK = True

# Diretórios
BACKUP_DIR = "backups/changes"
REPORTS_DIR = "reports/changes"
LOGS_DIR = "logs/changes"
TEST_RESULTS_DIR = "test_results"

# Configurações de Backup
BACKUP_COMPRESSION = True
BACKUP_ENCRYPTION = False  # Implementar se necessário
BACKUP_VERIFICATION = True

# Configurações de Testes
MANDATORY_TESTS = [
    "test_api_endpoints",
    "test_database_integrity",
    "test_metrics_calculation",
    "test_frontend_rendering",
    "test_data_consistency"
]

TEST_TIMEOUT_SECONDS = 300
TEST_RETRY_COUNT = 2
FAIL_FAST_ON_CRITICAL_TESTS = True

# Configurações de Validação
VALIDATION_CHECKS = [
    "database_connection",
    "api_health",
    "metrics_integrity",
    "data_consistency",
    "performance_baseline"
]

VALIDATION_TIMEOUT_SECONDS = 180
PERFORMANCE_THRESHOLD_MS = 5000

# Configurações de Rollback
AUTO_ROLLBACK_ON_FAILURE = True
ROLLBACK_TIMEOUT_SECONDS = 120
ROLLBACK_VERIFICATION = True

# Configurações de Notificação
NOTIFY_ON_SUCCESS = True
NOTIFY_ON_FAILURE = True
NOTIFY_ON_ROLLBACK = True

# Configurações de Auditoria
AUDIT_ALL_CHANGES = True
AUDIT_RETENTION_DAYS = 90
AUDIT_INCLUDE_SNAPSHOTS = True

# Configurações de Segurança
REQUIRE_DIGITAL_SIGNATURE = False  # Para implementação futura
ALLOW_EMERGENCY_BYPASS = False
REQUIRE_PEER_REVIEW = True

# Configurações de Performance
PARALLEL_VALIDATION = True
MAX_VALIDATION_WORKERS = 4
CACHE_VALIDATION_RESULTS = True
CACHE_TTL_SECONDS = 3600

# Configurações de Métricas Críticas
CRITICAL_METRICS = [
    "tickets_by_status",
    "total_open_tickets",
    "resolution_rate",
    "sla_compliance",
    "technician_workload"
]

# Configurações de Arquivos Críticos
CRITICAL_FILES = [
    "backend/app/services/metrics_service.py",
    "backend/app/models/ticket.py",
    "backend/app/core/database.py",
    "frontend/components/MetricsCard.py",
    "frontend/components/StatusMetricsCard.py"
]

# Configurações de Ambiente
ENVIRONMENT_CONFIGS = {
    "development": {
        "require_approval": False,
        "auto_rollback": True,
        "test_timeout": 120,
        "backup_retention": 7
    },
    "staging": {
        "require_approval": True,
        "auto_rollback": True,
        "test_timeout": 300,
        "backup_retention": 14
    },
    "production": {
        "require_approval": True,
        "auto_rollback": True,
        "test_timeout": 600,
        "backup_retention": 30,
        "require_peer_review": True
    }
}

# Configurações de Integração
INTEGRATIONS = {
    "knowledge_graph": {
        "enabled": True,
        "log_changes": True,
        "track_dependencies": True
    },
    "monitoring": {
        "enabled": True,
        "alert_on_failure": True,
        "metrics_collection": True
    },
    "git": {
        "auto_commit_backups": False,
        "tag_successful_changes": True,
        "branch_protection": True
    }
}

# Configurações de Relatórios
REPORT_FORMATS = ["markdown", "json", "html"]
REPORT_INCLUDE_SCREENSHOTS = True
REPORT_INCLUDE_LOGS = True
REPORT_INCLUDE_METRICS = True

# Configurações de Logs
LOG_LEVEL = "INFO"
LOG_FORMAT = "json"
LOG_ROTATION = True
LOG_MAX_SIZE_MB = 100
LOG_BACKUP_COUNT = 5

# Configurações de Monitoramento
MONITORING_INTERVAL_SECONDS = 30
HEALTH_CHECK_ENDPOINTS = [
    "/health",
    "/metrics",
    "/api/v1/tickets/summary",
    "/api/v1/status"
]

# Configurações de Alertas
ALERT_CHANNELS = {
    "email": {
        "enabled": False,
        "recipients": []
    },
    "slack": {
        "enabled": False,
        "webhook_url": ""
    },
    "teams": {
        "enabled": False,
        "webhook_url": ""
    }
}

# Configurações de Compliance
COMPLIANCE_REQUIREMENTS = {
    "change_documentation": True,
    "approval_workflow": True,
    "audit_trail": True,
    "rollback_capability": True,
    "testing_evidence": True
}
