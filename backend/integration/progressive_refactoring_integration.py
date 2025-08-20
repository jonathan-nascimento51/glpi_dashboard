# -*- coding: utf-8 -*-
"""
Progressive Refactoring Integration - Integração da refatoração progressiva com Flask.

Este script demonstra como integrar a refatoração progressiva com as rotas
Flask existentes, permitindo uma migração gradual sem quebrar a API atual.
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

from flask import Blueprint, Flask, g, jsonify, request
from werkzeug.exceptions import BadRequest

# Importar componentes da nova arquitetura
from backend.core.application.controllers import (
    RefactoringController,
    async_route,
    create_refactoring_blueprint,
    create_refactoring_controller,
)
from backend.core.application.services import RefactoringConfig, RefactoringPhase
from backend.core.infrastructure.external.glpi.metrics_adapter import GLPIConfig

# Importar serviços legados
try:
    from backend.api.routes import api_bp  # Blueprint existente
    from backend.services.glpi_service import GLPIService
except ImportError as e:
    print(f"Aviso: Não foi possível importar serviços legados: {e}")
    GLPIService = None
    api_bp = None


logger = logging.getLogger(__name__)


class ProgressiveRefactoringIntegration:
    """Classe para integração da refatoração progressiva."""

    def __init__(self, app: Flask):
        self.app = app
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Configurações
        self.glpi_config = self._load_glpi_config()
        self.refactoring_phase = self._get_refactoring_phase()

        # Serviços
        self.legacy_service = self._create_legacy_service()
        self.refactoring_controller = self._create_refactoring_controller()

        # Estado da integração
        self.is_initialized = False

    def _load_glpi_config(self) -> GLPIConfig:
        """Carrega configuração do GLPI a partir de variáveis de ambiente."""

        return GLPIConfig(
            base_url=os.getenv("GLPI_BASE_URL", "https://glpi.example.com"),
            app_token=os.getenv("GLPI_APP_TOKEN", ""),
            user_token=os.getenv("GLPI_USER_TOKEN", ""),
            timeout=int(os.getenv("GLPI_TIMEOUT", "30")),
            max_retries=int(os.getenv("GLPI_MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("GLPI_RETRY_DELAY", "1.0")),
        )

    def _get_refactoring_phase(self) -> RefactoringPhase:
        """Obtém fase da refatoração a partir de variável de ambiente."""

        phase_str = os.getenv("REFACTORING_PHASE", "legacy_only").lower()

        phase_mapping = {
            "legacy_only": RefactoringPhase.LEGACY_ONLY,
            "strangler_fig": RefactoringPhase.STRANGLER_FIG,
            "new_architecture": RefactoringPhase.NEW_ARCHITECTURE,
            "validation": RefactoringPhase.VALIDATION,
        }

        return phase_mapping.get(phase_str, RefactoringPhase.LEGACY_ONLY)

    def _create_legacy_service(self) -> Optional[Any]:
        """Cria instância do serviço legado."""

        if GLPIService is None:
            self.logger.warning("GLPIService não disponível")
            return None

        try:
            return GLPIService()
        except Exception as e:
            self.logger.error(f"Erro ao criar GLPIService: {e}")
            return None

    def _create_refactoring_controller(self) -> RefactoringController:
        """Cria controlador de refatoração."""

        return create_refactoring_controller(
            glpi_base_url=self.glpi_config.base_url,
            glpi_app_token=self.glpi_config.app_token,
            glpi_user_token=self.glpi_config.user_token,
            legacy_service=self.legacy_service,
            phase=self.refactoring_phase,
            timeout=self.glpi_config.timeout,
            max_retries=self.glpi_config.max_retries,
            retry_delay=self.glpi_config.retry_delay,
        )

    def initialize(self) -> None:
        """Inicializa a integração."""

        if self.is_initialized:
            return

        try:
            # Registrar blueprint de refatoração
            self._register_refactoring_blueprint()

            # Interceptar rotas existentes se necessário
            self._setup_route_interception()

            # Configurar middleware
            self._setup_middleware()

            # Configurar logging
            self._setup_logging()

            self.is_initialized = True

            self.logger.info(f"Refatoração progressiva inicializada - Fase: {self.refactoring_phase.value}")

        except Exception as e:
            self.logger.error(f"Erro ao inicializar refatoração progressiva: {e}")
            raise

    def _register_refactoring_blueprint(self) -> None:
        """Registra blueprint com novas rotas de refatoração."""

        # Criar blueprint com prefixo para evitar conflitos
        refactoring_bp = create_refactoring_blueprint(controller=self.refactoring_controller, blueprint_name="refactoring_v2")

        # Registrar com prefixo
        self.app.register_blueprint(refactoring_bp, url_prefix="/api/v2")

        self.logger.info("Blueprint de refatoração registrado em /api/v2")

    def _setup_route_interception(self) -> None:
        """Configura interceptação de rotas existentes."""

        if self.refactoring_phase == RefactoringPhase.LEGACY_ONLY:
            return

        # Interceptar rotas específicas baseado na fase
        routes_to_intercept = self._get_routes_to_intercept()

        for route_pattern in routes_to_intercept:
            self._intercept_route(route_pattern)

    def _get_routes_to_intercept(self) -> list:
        """Retorna lista de rotas para interceptar baseado na fase."""

        if self.refactoring_phase == RefactoringPhase.STRANGLER_FIG:
            # Interceptar gradualmente
            migration_percentage = float(os.getenv("MIGRATION_PERCENTAGE", "0.1"))

            if migration_percentage > 0:
                return ["/api/metrics", "/api/metrics/filtered"]

        elif self.refactoring_phase == RefactoringPhase.NEW_ARCHITECTURE:
            # Interceptar todas as rotas de métricas
            return ["/api/metrics", "/api/metrics/filtered", "/api/technicians/ranking"]

        elif self.refactoring_phase == RefactoringPhase.VALIDATION:
            # Interceptar para validação
            return ["/api/metrics"]

        return []

    def _intercept_route(self, route_pattern: str) -> None:
        """Intercepta uma rota específica."""

        # Esta é uma implementação conceitual
        # Na prática, seria necessário usar um middleware mais sofisticado

        @self.app.before_request
        def intercept_request():
            if request.path == route_pattern:
                # Marcar para interceptação
                g.intercept_with_refactoring = True
                g.original_route = route_pattern

    def _setup_middleware(self) -> None:
        """Configura middleware para interceptação."""

        @self.app.before_request
        def before_request():
            # Gerar ID de correlação
            correlation_id = request.headers.get("X-Correlation-ID")
            if not correlation_id:
                import uuid

                correlation_id = str(uuid.uuid4())

            g.correlation_id = correlation_id
            g.request_start_time = datetime.now()

        @self.app.after_request
        def after_request(response):
            # Log de performance
            if hasattr(g, "request_start_time"):
                duration = (datetime.now() - g.request_start_time).total_seconds()

                self.logger.info(
                    f"Request completed",
                    extra={
                        "correlation_id": getattr(g, "correlation_id", None),
                        "path": request.path,
                        "method": request.method,
                        "status_code": response.status_code,
                        "duration": duration,
                        "refactoring_phase": self.refactoring_phase.value,
                    },
                )

            # Adicionar headers de correlação
            if hasattr(g, "correlation_id"):
                response.headers["X-Correlation-ID"] = g.correlation_id

            return response

    def _setup_logging(self) -> None:
        """Configura logging estruturado."""

        # Configurar formato JSON para logs
        import json

        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno,
                }

                # Adicionar campos extras
                if hasattr(record, "correlation_id"):
                    log_entry["correlation_id"] = record.correlation_id

                if hasattr(record, "refactoring_phase"):
                    log_entry["refactoring_phase"] = record.refactoring_phase

                return json.dumps(log_entry)

        # Aplicar formatter aos handlers existentes
        json_formatter = JSONFormatter()

        for handler in logging.getLogger().handlers:
            if handler.name != "console":  # Manter console legível
                handler.setFormatter(json_formatter)

    def create_intercepted_route_handler(self, original_endpoint: str):
        """Cria handler para rota interceptada."""

        @async_route
        async def intercepted_handler():
            try:
                # Determinar qual método usar baseado no endpoint
                if "dashboard" in original_endpoint or original_endpoint == "/api/metrics":
                    (
                        result,
                        status_code,
                    ) = await self.refactoring_controller.handle_dashboard_metrics(
                        migration_percentage=float(os.getenv("MIGRATION_PERCENTAGE", "0.1")),
                        enable_validation=os.getenv("ENABLE_VALIDATION", "false").lower() == "true",
                    )

                elif "ranking" in original_endpoint:
                    (
                        result,
                        status_code,
                    ) = await self.refactoring_controller.handle_technician_ranking()

                else:
                    (
                        result,
                        status_code,
                    ) = await self.refactoring_controller.handle_general_metrics()

                return jsonify(result), status_code

            except Exception as e:
                self.logger.error(f"Erro no handler interceptado: {e}")
                return jsonify({"success": False, "error": "Erro interno"}), 500

        return intercepted_handler

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de performance da refatoração."""

        base_metrics = self.refactoring_controller.get_performance_metrics()

        return {
            **base_metrics,
            "phase": self.refactoring_phase.value,
            "initialized": self.is_initialized,
            "glpi_config": {
                "base_url": self.glpi_config.base_url,
                "timeout": self.glpi_config.timeout,
                "max_retries": self.glpi_config.max_retries,
            },
        }

    async def cleanup(self) -> None:
        """Limpa recursos da integração."""

        if self.refactoring_controller:
            await self.refactoring_controller.close()

        self.logger.info("Recursos da refatoração progressiva limpos")


# Factory function para facilitar uso
def setup_progressive_refactoring(app: Flask) -> ProgressiveRefactoringIntegration:
    """Configura refatoração progressiva em uma aplicação Flask."""

    integration = ProgressiveRefactoringIntegration(app)
    integration.initialize()

    # Adicionar rota para métricas de performance
    @app.route("/api/refactoring/metrics", methods=["GET"])
    def refactoring_metrics():
        metrics = integration.get_performance_metrics()
        return jsonify(metrics), 200

    # Adicionar rota para health check
    @app.route("/api/refactoring/health", methods=["GET"])
    def refactoring_health():
        return (
            jsonify(
                {
                    "status": "healthy",
                    "phase": integration.refactoring_phase.value,
                    "initialized": integration.is_initialized,
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            200,
        )

    return integration


# Exemplo de uso
def create_app_with_refactoring() -> Flask:
    """Cria aplicação Flask com refatoração progressiva."""

    app = Flask(__name__)

    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Registrar blueprint legado (se disponível)
    if api_bp:
        app.register_blueprint(api_bp, url_prefix="/api")

    # Configurar refatoração progressiva
    integration = setup_progressive_refactoring(app)

    # Configurar cleanup no shutdown
    import atexit

    def cleanup():
        import asyncio

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(integration.cleanup())
            else:
                asyncio.run(integration.cleanup())
        except Exception as e:
            print(f"Erro no cleanup: {e}")

    atexit.register(cleanup)

    return app


if __name__ == "__main__":
    # Para teste local
    app = create_app_with_refactoring()

    print("Aplicação Flask com refatoração progressiva criada")
    print("Rotas disponíveis:")
    print("- /api/v2/metrics/dashboard (nova arquitetura)")
    print("- /api/v2/metrics/technicians/ranking (nova arquitetura)")
    print("- /api/v2/metrics/general (nova arquitetura)")
    print("- /api/refactoring/metrics (métricas de performance)")
    print("- /api/refactoring/health (health check)")

    # Executar aplicação
    app.run(debug=True, port=5000)
