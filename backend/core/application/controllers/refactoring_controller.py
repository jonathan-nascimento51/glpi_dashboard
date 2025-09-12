# -*- coding: utf-8 -*-
"""
Refactoring Controller - Controlador para integração da refatoração progressiva.

Este controlador integra o ProgressiveRefactoringService com as rotas Flask
existentes, permitindo uma migração gradual sem quebrar a API atual.
"""

import asyncio
import logging
from datetime import datetime
from functools import wraps
from typing import Any, Dict, Optional, Tuple

from flask import g, jsonify, request
from werkzeug.exceptions import BadRequest

from ...infrastructure.external.glpi.metrics_adapter import GLPIConfig
from ..dto.metrics_dto import MetricsFilterDTO, MetricsResponseDTO, TicketStatus, create_error_response
from ..services.progressive_refactoring_service import (
    ProgressiveRefactoringService,
    RefactoringConfig,
    RefactoringPhase,
    create_progressive_refactoring_service,
)

logger = logging.getLogger(__name__)


class RefactoringController:
    """Controlador para refatoração progressiva."""

    def __init__(
        self,
        glpi_config: GLPIConfig,
        legacy_service: Any = None,
        phase: RefactoringPhase = RefactoringPhase.LEGACY_ONLY,
    ):
        self.glpi_config = glpi_config
        self.legacy_service = legacy_service
        self.phase = phase
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Cache do serviço de refatoração
        self._refactoring_service: Optional[ProgressiveRefactoringService] = None

        # Configuração padrão
        self.default_config = {
            "migration_percentage": 0.0,
            "enable_validation": False,
            "validation_sampling": 0.1,
            "enable_fallback": True,
            "log_performance_comparison": True,
            "log_data_differences": True,
        }

    def get_refactoring_service(self, **config_overrides) -> ProgressiveRefactoringService:
        """Obtém ou cria instância do serviço de refatoração."""

        if self._refactoring_service is None:
            config = {**self.default_config, **config_overrides}

            self._refactoring_service = create_progressive_refactoring_service(
                phase=self.phase,
                glpi_config=self.glpi_config,
                legacy_service=self.legacy_service,
                **config,
            )

        return self._refactoring_service

    def parse_request_filters(self) -> MetricsFilterDTO:
        """Extrai e valida filtros da requisição Flask."""

        try:
            # Obter parâmetros da query string
            start_date_str = request.args.get("start_date")
            end_date_str = request.args.get("end_date")
            status_str = request.args.get("status")
            technician_id = request.args.get("technician_id")
            category_id = request.args.get("category_id")
            priority = request.args.get("priority")

            # Converter datas
            start_date = None
            end_date = None

            if start_date_str:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()

            if end_date_str:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            # Converter status
            status = None
            if status_str:
                try:
                    status = TicketStatus(status_str.lower())
                except ValueError:
                    raise BadRequest(f"Status inválido: {status_str}")

            # Converter IDs
            technician_id_int = None
            if technician_id:
                try:
                    technician_id_int = int(technician_id)
                except ValueError:
                    raise BadRequest(f"ID de técnico inválido: {technician_id}")

            category_id_int = None
            if category_id:
                try:
                    category_id_int = int(category_id)
                except ValueError:
                    raise BadRequest(f"ID de categoria inválido: {category_id}")

            priority_int = None
            if priority:
                try:
                    priority_int = int(priority)
                except ValueError:
                    raise BadRequest(f"Prioridade inválida: {priority}")

            return MetricsFilterDTO(
                start_date=start_date,
                end_date=end_date,
                status=status,
                technician_id=technician_id_int,
                category_id=category_id_int,
                priority=priority_int,
            )

        except Exception as e:
            self.logger.error(f"Erro ao processar filtros da requisição: {str(e)}")
            raise BadRequest(f"Filtros inválidos: {str(e)}")

    def get_correlation_id(self) -> str:
        """Obtém ou gera ID de correlação para a requisição."""

        # Tentar obter do header
        correlation_id = request.headers.get("X-Correlation-ID")

        if not correlation_id:
            # Tentar obter do Flask g
            correlation_id = getattr(g, "correlation_id", None)

        if not correlation_id:
            # Gerar novo ID
            import uuid

            correlation_id = str(uuid.uuid4())
            g.correlation_id = correlation_id

        return correlation_id

    def convert_response_to_flask(self, response: MetricsResponseDTO) -> Tuple[Dict[str, Any], int]:
        """Converte resposta DTO para formato Flask."""

        if response.success:
            # Converter DTO para dicionário
            if hasattr(response.data, "dict"):
                data = response.data.dict()
            elif hasattr(response.data, "__dict__"):
                data = response.data.__dict__
            else:
                data = response.data

            flask_response = {
                "success": True,
                "data": data,
                "timestamp": response.timestamp.isoformat() if response.timestamp else None,
                "execution_time": response.execution_time,
            }

            return flask_response, 200

        else:
            flask_response = {
                "success": False,
                "error": response.error,
                "timestamp": response.timestamp.isoformat() if response.timestamp else None,
            }

            return flask_response, 500

    async def handle_dashboard_metrics(self, **config_overrides) -> Tuple[Dict[str, Any], int]:
        """Manipula requisição de métricas do dashboard."""

        try:
            # Obter serviço de refatoração
            service = self.get_refactoring_service(**config_overrides)

            # Processar filtros
            filters = self.parse_request_filters()

            # Obter ID de correlação
            correlation_id = self.get_correlation_id()

            # Executar consulta
            response = await service.get_dashboard_metrics(filters=filters, correlation_id=correlation_id)

            # Converter para formato Flask
            return self.convert_response_to_flask(response)

        except BadRequest as e:
            return {"success": False, "error": str(e)}, 400

        except Exception as e:
            self.logger.error(f"Erro no handle_dashboard_metrics: {str(e)}")
            return {"success": False, "error": "Erro interno do servidor"}, 500

    async def handle_technician_ranking(self, **config_overrides) -> Tuple[Dict[str, Any], int]:
        """Manipula requisição de ranking de técnicos."""

        try:
            service = self.get_refactoring_service(**config_overrides)
            filters = self.parse_request_filters()
            correlation_id = self.get_correlation_id()

            response = await service.get_technician_ranking(filters=filters, correlation_id=correlation_id)

            return self.convert_response_to_flask(response)

        except BadRequest as e:
            return {"success": False, "error": str(e)}, 400

        except Exception as e:
            self.logger.error(f"Erro no handle_technician_ranking: {str(e)}")
            return {"success": False, "error": "Erro interno do servidor"}, 500

    async def handle_general_metrics(self, **config_overrides) -> Tuple[Dict[str, Any], int]:
        """Manipula requisição de métricas gerais."""

        try:
            service = self.get_refactoring_service(**config_overrides)
            filters = self.parse_request_filters()
            correlation_id = self.get_correlation_id()

            response = await service.get_general_metrics(filters=filters, correlation_id=correlation_id)

            return self.convert_response_to_flask(response)

        except BadRequest as e:
            return {"success": False, "error": str(e)}, 400

        except Exception as e:
            self.logger.error(f"Erro no handle_general_metrics: {str(e)}")
            return {"success": False, "error": "Erro interno do servidor"}, 500

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de performance da refatoração."""

        if self._refactoring_service:
            return self._refactoring_service.get_performance_metrics()
        else:
            return {"message": "Serviço de refatoração não inicializado"}

    async def close(self) -> None:
        """Fecha recursos do controlador."""

        if self._refactoring_service:
            await self._refactoring_service.close()
            self._refactoring_service = None


# Decorador para executar métodos async em rotas Flask
def async_route(f):
    """Decorador para executar métodos async em rotas Flask."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        # Verificar se já estamos em um loop de eventos
        try:
            loop = asyncio.get_running_loop()
            # Se já estamos em um loop, criar uma task
            return asyncio.create_task(f(*args, **kwargs))
        except RuntimeError:
            # Não estamos em um loop, criar um novo
            return asyncio.run(f(*args, **kwargs))

    return wrapper


# Factory para criação do controlador
def create_refactoring_controller(
    glpi_base_url: str,
    glpi_app_token: str,
    glpi_user_token: str,
    legacy_service: Any = None,
    phase: RefactoringPhase = RefactoringPhase.LEGACY_ONLY,
    **glpi_config_kwargs,
) -> RefactoringController:
    """Cria instância do RefactoringController."""

    glpi_config = GLPIConfig(
        base_url=glpi_base_url,
        app_token=glpi_app_token,
        user_token=glpi_user_token,
        **glpi_config_kwargs,
    )

    return RefactoringController(glpi_config=glpi_config, legacy_service=legacy_service, phase=phase)


# Exemplo de integração com Flask Blueprint
def create_refactoring_blueprint(controller: RefactoringController, blueprint_name: str = "refactoring_api") -> "Blueprint":
    """Cria Blueprint Flask com rotas de refatoração."""

    from flask import Blueprint

    bp = Blueprint(blueprint_name, __name__)

    @bp.route("/metrics/dashboard", methods=["GET"])
    @async_route
    async def dashboard_metrics():
        """Endpoint para métricas do dashboard."""
        result, status_code = await controller.handle_dashboard_metrics()
        return jsonify(result), status_code

    @bp.route("/metrics/technicians/ranking", methods=["GET"])
    @async_route
    async def technician_ranking():
        """Endpoint para ranking de técnicos."""
        result, status_code = await controller.handle_technician_ranking()
        return jsonify(result), status_code

    @bp.route("/metrics/general", methods=["GET"])
    @async_route
    async def general_metrics():
        """Endpoint para métricas gerais."""
        result, status_code = await controller.handle_general_metrics()
        return jsonify(result), status_code

    @bp.route("/refactoring/performance", methods=["GET"])
    def performance_metrics():
        """Endpoint para métricas de performance da refatoração."""
        result = controller.get_performance_metrics()
        return jsonify(result), 200

    @bp.route("/refactoring/health", methods=["GET"])
    def health_check():
        """Endpoint para verificação de saúde da refatoração."""
        return (
            jsonify(
                {
                    "status": "healthy",
                    "phase": controller.phase.value,
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            200,
        )

    return bp


# Exemplo de uso
async def example_usage():
    """Exemplo de como usar o RefactoringController."""

    # Importar serviço refatorado (usando facade)
    from backend.services.legacy.glpi_service_facade import GLPIServiceFacade

    legacy_service = GLPIServiceFacade()

    # Criar controlador
    controller = create_refactoring_controller(
        glpi_base_url="https://glpi.example.com",
        glpi_app_token="your-app-token",
        glpi_user_token="your-user-token",
        legacy_service=legacy_service,
        phase=RefactoringPhase.STRANGLER_FIG,
    )

    try:
        # Simular requisição Flask
        with app.test_request_context("/metrics/dashboard?start_date=2024-01-01&end_date=2024-01-31"):
            result, status_code = await controller.handle_dashboard_metrics(migration_percentage=0.2, enable_validation=True)

            print(f"Status: {status_code}")
            print(f"Resultado: {result}")

        # Verificar métricas de performance
        performance = controller.get_performance_metrics()
        print(f"Performance: {performance}")

    finally:
        # Fechar recursos
        await controller.close()


if __name__ == "__main__":
    # Para teste local
    from flask import Flask

    app = Flask(__name__)

    asyncio.run(example_usage())
