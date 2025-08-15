#!/usr/bin/env python3`n# -*- coding: utf-8 -*-
"""
Configuração do Sistema de AI Context

Este arquivo contém as configurações para o sistema de treinamento e otimização
do AI Context, incluindo MCPs especializados e parâmetros de monitoramento.

Autor: GLPI Dashboard Team
Versão: 1.0.0
Data: 2024
"""

from datetime import timedelta
from pathlib import Path

# =============================================================================
# CONFIGURAÇÕES GERAIS
# =============================================================================

# Diretório raiz do projeto
PROJECT_ROOT = Path.cwd()

# Diretório de armazenamento do contexto
CONTEXT_STORAGE_DIR = PROJECT_ROOT / "ai_context_storage"

# Intervalo de monitoramento (segundos)
MONITORING_INTERVAL = 30

# Intervalo de atualização periódica (segundos)
UPDATE_INTERVAL = 300

# Retenção de contexto (dias)
CONTEXT_RETENTION_DAYS = 30

# Tamanho máximo de conteúdo por item (caracteres)
MAX_CONTENT_SIZE = 5000

# =============================================================================
# CONFIGURAÇÕES DE MCPs ESPECIALIZADOS
# =============================================================================

MCP_CONFIGS = [
    {
        "name": "filesystem",
        "type": "core",
        "description": "Acesso ao sistema de arquivos para monitoramento de mudanças",
        "config_path": "mcp/filesystem.json",
        "enabled": True,
        "auto_update": True,
        "update_interval": 3600,  # 1 hora
        "dependencies": []
    },
    {
        "name": "git",
        "type": "version_control",
        "description": "Integração com Git para rastreamento de mudanças",
        "config_path": "mcp/git.json",
        "enabled": True,
        "auto_update": True,
        "update_interval": 1800,  # 30 minutos
        "dependencies": ["filesystem"]
    },
    {
        "name": "knowledge_graph",
        "type": "knowledge",
        "description": "Grafo de conhecimento persistente para contexto semântico",
        "config_path": "mcp/knowledge_graph.json",
        "enabled": True,
        "auto_update": True,
        "update_interval": 7200,  # 2 horas
        "dependencies": ["filesystem", "git"]
    },
    {
        "name": "code_analysis",
        "type": "analysis",
        "description": "Análise de código para extração de padrões e métricas",
        "config_path": "mcp/code_analysis.json",
        "enabled": True,
        "auto_update": True,
        "update_interval": 3600,  # 1 hora
        "dependencies": ["filesystem"]
    },
    {
        "name": "documentation",
        "type": "documentation",
        "description": "Processamento de documentação e geração de contexto",
        "config_path": "mcp/documentation.json",
        "enabled": True,
        "auto_update": True,
        "update_interval": 7200,  # 2 horas
        "dependencies": ["filesystem"]
    },
    {
        "name": "metrics_collector",
        "type": "monitoring",
        "description": "Coleta de métricas de performance e sistema",
        "config_path": "mcp/metrics.json",
        "enabled": True,
        "auto_update": True,
        "update_interval": 900,  # 15 minutos
        "dependencies": []
    },
    {
        "name": "api_monitor",
        "type": "monitoring",
        "description": "Monitoramento de APIs e endpoints",
        "config_path": "mcp/api_monitor.json",
        "enabled": True,
        "auto_update": True,
        "update_interval": 600,  # 10 minutos
        "dependencies": ["metrics_collector"]
    }
]

# =============================================================================
# CONFIGURAÇÕES DE ANÁLISE DE ARQUIVOS
# =============================================================================

# Padrões de arquivos para monitoramento
FILE_PATTERNS = {
    "code": [
        "*.py", "*.js", "*.ts", "*.tsx", "*.jsx", "*.html", "*.css", "*.scss",
        "*.sql", "*.sh", "*.bat", "*.ps1", "*.yaml", "*.yml", "*.json", "*.toml"
    ],
    "documentation": [
        "*.md", "*.rst", "*.txt", "*.doc", "*.docx", "*.pdf"
    ],
    "configuration": [
        "*.env", "*.ini", "*.conf", "*.config", "Dockerfile", "docker-compose.yml",
        "requirements.txt", "package.json", "pyproject.toml", "setup.py"
    ],
    "architecture": [
        "ARCHITECTURE.md", "DESIGN.md", "*.arch", "*.design"
    ]
}

# Diretórios a ignorar
IGNORE_DIRECTORIES = {
    ".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
    ".mypy_cache", "dist", "build", ".tox", ".coverage", "htmlcov",
    "ai_context_storage", "artifacts", "logs", "temp", "tmp"
}

# Extensões de arquivo a ignorar
IGNORE_EXTENSIONS = {
    ".pyc", ".pyo", ".pyd", ".so", ".dll", ".exe", ".bin", ".obj",
    ".log", ".tmp", ".temp", ".cache", ".lock", ".pid"
}

# =============================================================================
# CONFIGURAÇÕES DE PRIORIDADE
# =============================================================================

# Mapeamento de prioridades por tipo de arquivo
PRIORITY_MAPPING = {
    "ARCHITECTURE.md": "critical",
    "README.md": "high",
    "CHANGELOG.md": "high",
    "requirements.txt": "high",
    "package.json": "high",
    "pyproject.toml": "high",
    "docker-compose.yml": "high",
    "Dockerfile": "high",
    ".env": "critical",
    "config.py": "high",
    "settings.py": "high"
}

# Prioridade por diretório
DIRECTORY_PRIORITY = {
    "src": "high",
    "app": "high",
    "api": "high",
    "core": "high",
    "models": "high",
    "services": "high",
    "utils": "medium",
    "tests": "medium",
    "docs": "medium",
    "scripts": "low",
    "examples": "low"
}

# =============================================================================
# CONFIGURAÇÕES DE TAGS AUTOMÁTICAS
# =============================================================================

# Tags baseadas em conteúdo
CONTENT_TAGS = {
    "async": ["async def", "await ", "asyncio"],
    "database": ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE TABLE"],
    "api": ["@app.route", "@router", "FastAPI", "flask", "endpoint"],
    "testing": ["def test_", "pytest", "unittest", "assert"],
    "security": ["password", "token", "auth", "permission", "security"],
    "performance": ["cache", "optimize", "performance", "benchmark"],
    "monitoring": ["logging", "metric", "monitor", "alert"],
    "frontend": ["react", "vue", "angular", "html", "css", "javascript"],
    "backend": ["fastapi", "flask", "django", "sqlalchemy", "pydantic"],
    "devops": ["docker", "kubernetes", "ci/cd", "deployment", "pipeline"]
}

# Tags baseadas em nome de arquivo
FILE_TAGS = {
    "model": ["model", "models", "schema", "schemas"],
    "service": ["service", "services", "business"],
    "repository": ["repository", "repo", "dao", "data"],
    "controller": ["controller", "handler", "view", "endpoint"],
    "utility": ["util", "utils", "helper", "helpers"],
    "configuration": ["config", "settings", "env", "constants"],
    "migration": ["migration", "migrate", "alembic"],
    "test": ["test", "spec", "e2e", "integration"]
}

# =============================================================================
# CONFIGURAÇÕES DE EXTRAÇÃO DE DEPENDÊNCIAS
# =============================================================================

# Padrões para extração de imports Python
PYTHON_IMPORT_PATTERNS = [
    r"^import\s+([\w\.]+)",
    r"^from\s+([\w\.]+)\s+import",
    r"^from\s+\.([\w\.]+)\s+import"
]

# Padrões para extração de imports JavaScript/TypeScript
JS_IMPORT_PATTERNS = [
    r"^import\s+.*?from\s+['\"]([^'\"]+)['\"]",
    r"^const\s+.*?=\s+require\(['\"]([^'\"]+)['\"]\)",
    r"^import\s+['\"]([^'\"]+)['\"]"
]

# =============================================================================
# CONFIGURAÇÕES DE MÉTRICAS
# =============================================================================

# Métricas a coletar
METRICS_CONFIG = {
    "context_items": {
        "enabled": True,
        "interval": 300,  # 5 minutos
        "retention": 7  # dias
    },
    "file_changes": {
        "enabled": True,
        "interval": 60,  # 1 minuto
        "retention": 30  # dias
    },
    "mcp_status": {
        "enabled": True,
        "interval": 600,  # 10 minutos
        "retention": 7  # dias
    },
    "storage_usage": {
        "enabled": True,
        "interval": 3600,  # 1 hora
        "retention": 30  # dias
    },
    "processing_time": {
        "enabled": True,
        "interval": 300,  # 5 minutos
        "retention": 7  # dias
    }
}

# =============================================================================
# CONFIGURAÇÕES DE OTIMIZAÇÃO
# =============================================================================

# Configurações de performance
PERFORMANCE_CONFIG = {
    "max_concurrent_files": 10,
    "max_file_size": 1024 * 1024,  # 1MB
    "batch_size": 50,
    "cache_ttl": 3600,  # 1 hora
    "compression_enabled": True,
    "deduplication_enabled": True
}

# Configurações de limpeza automática
CLEANUP_CONFIG = {
    "enabled": True,
    "interval": 86400,  # 24 horas
    "max_items": 10000,
    "max_storage_size": 100 * 1024 * 1024,  # 100MB
    "remove_duplicates": True,
    "remove_old_items": True
}

# =============================================================================
# CONFIGURAÇÕES DE LOGGING
# =============================================================================

LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "ai_context.log",
    "max_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5,
    "structured_logging": True
}

# =============================================================================
# CONFIGURAÇÕES DE SEGURANÇA
# =============================================================================

SECURITY_CONFIG = {
    "sanitize_content": True,
    "exclude_secrets": True,
    "secret_patterns": [
        r"password\s*=\s*['\"][^'\"]+['\"]",
        r"token\s*=\s*['\"][^'\"]+['\"]",
        r"key\s*=\s*['\"][^'\"]+['\"]",
        r"secret\s*=\s*['\"][^'\"]+['\"]",
        r"api_key\s*=\s*['\"][^'\"]+['\"]"
    ],
    "max_content_preview": 500,
    "hash_sensitive_data": True
}

# =============================================================================
# CONFIGURAÇÕES DE INTEGRAÇÃO
# =============================================================================

# Integração com Knowledge Graph
KNOWLEDGE_GRAPH_CONFIG = {
    "enabled": True,
    "endpoint": "http://localhost:8001/knowledge",
    "auto_sync": True,
    "sync_interval": 3600,  # 1 hora
    "batch_size": 100
}

# Integração com Git
GIT_CONFIG = {
    "enabled": True,
    "track_commits": True,
    "track_branches": True,
    "track_tags": True,
    "ignore_merge_commits": False,
    "max_commit_history": 1000
}

# Integração com Prometheus
PROMETHEUS_CONFIG = {
    "enabled": False,
    "endpoint": "http://localhost:9090",
    "metrics_prefix": "ai_context_",
    "push_interval": 60  # segundos
}

# =============================================================================
# CONFIGURAÇÕES POR AMBIENTE
# =============================================================================

ENVIRONMENT_CONFIGS = {
    "development": {
        "monitoring_interval": 10,
        "update_interval": 60,
        "logging_level": "DEBUG",
        "performance_monitoring": True,
        "detailed_metrics": True
    },
    "staging": {
        "monitoring_interval": 30,
        "update_interval": 300,
        "logging_level": "INFO",
        "performance_monitoring": True,
        "detailed_metrics": False
    },
    "production": {
        "monitoring_interval": 60,
        "update_interval": 600,
        "logging_level": "WARNING",
        "performance_monitoring": False,
        "detailed_metrics": False
    }
}

# =============================================================================
# CONFIGURAÇÕES DE VALIDAÇÃO
# =============================================================================

VALIDATION_CONFIG = {
    "validate_json": True,
    "validate_yaml": True,
    "validate_python_syntax": True,
    "validate_imports": True,
    "check_file_encoding": True,
    "max_validation_time": 30  # segundos
}

# =============================================================================
# CONFIGURAÇÕES DE EXPORTAÇÃO
# =============================================================================

EXPORT_CONFIG = {
    "formats": ["json", "yaml", "markdown"],
    "include_metadata": True,
    "include_metrics": True,
    "compress_exports": True,
    "export_directory": "exports",
    "auto_export_interval": 86400  # 24 horas
}

