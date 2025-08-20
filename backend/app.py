#!/usr/bin/env python3
"""
Ponto de entrada principal da aplicação Flask GLPI Dashboard
"""

import logging
import os
import sys

import redis
from flask import Flask
from flask_caching import Cache
from flask_cors import CORS

# Adiciona o diretório pai ao path para importar módulos
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from api.routes import api_bp
from config.settings import active_config
from utils.alerting_system import alert_manager
from utils.observability_middleware import setup_observability
from utils.prometheus_metrics import prometheus_metrics
from utils.structured_logging import system_logger

# Instância global do cache
cache = Cache()


def create_app(config=None):
    """Cria e configura a aplicação Flask com observabilidade completa"""
    app = Flask(__name__)

    # Carrega configurações
    if config is None:
        app.config.from_object(active_config)
    else:
        app.config.from_object(config)

    # Configurar observabilidade ANTES de outros componentes
    observability_config = {
        "structured_logging": True,
        "prometheus_gateway_url": app.config.get("PROMETHEUS_GATEWAY_URL"),
    }
    observability_middleware = setup_observability(app, observability_config)

    # Log início da configuração
    system_logger.log_operation_start(
        "app_initialization",
        environment=app.config.get("ENV", "development"),
        debug=app.config.get("DEBUG", False),
    )

    # Configura cache com Redis e fallback
    try:
        # Tenta conectar ao Redis
        redis_client = redis.from_url(app.config.get("REDIS_URL", "redis://localhost:6379/0"))
        redis_client.ping()  # Testa conexão

        cache_config = {
            "CACHE_TYPE": "RedisCache",
            "CACHE_REDIS_URL": app.config.get("CACHE_REDIS_URL", "redis://localhost:6379/0"),
            "CACHE_DEFAULT_TIMEOUT": app.config.get("CACHE_DEFAULT_TIMEOUT", 300),
            "CACHE_KEY_PREFIX": app.config.get("CACHE_KEY_PREFIX", "glpi_dashboard:"),
        }

        system_logger.log_operation_end(
            "redis_connection",
            success=True,
            redis_url=app.config.get("REDIS_URL", "redis://localhost:6379/0"),
        )

    except Exception as e:
        # Fallback para cache simples em caso de erro no Redis
        cache_config = {
            "CACHE_TYPE": "SimpleCache",
            "CACHE_DEFAULT_TIMEOUT": app.config.get("CACHE_DEFAULT_TIMEOUT", 300),
        }

        system_logger.log_operation_end(
            "redis_connection_failed",
            success=False,
            error=str(e),
            fallback="SimpleCache",
        )

    # Inicializa cache
    cache.init_app(app, config=cache_config)

    # Configura CORS
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
            }
        },
    )

    # Registra blueprints
    app.register_blueprint(api_bp, url_prefix="/api")

    # Configura logging
    if not app.debug:
        logging.basicConfig(level=logging.INFO)

    # Log configuração completa
    system_logger.log_operation_end(
        "app_initialization_complete",
        success=True,
        cache_type=cache_config["CACHE_TYPE"],
        cors_enabled=True,
        blueprints_registered=["api"],
    )

    return app


# Cria a aplicação
app = create_app(active_config)

if __name__ == "__main__":
    # Configuração para execução direta
    logger = logging.getLogger("app")

    config_obj = active_config()
    port = config_obj.PORT
    host = config_obj.HOST
    debug = config_obj.DEBUG

    logger.info(f"Iniciando servidor Flask em {host}:{port} (Debug: {debug})")

    app.run(host=host, port=port, debug=debug)
