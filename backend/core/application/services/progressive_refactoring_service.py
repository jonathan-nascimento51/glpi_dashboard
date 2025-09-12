# -*- coding: utf-8 -*-
"""
Progressive Refactoring Service - Implementação do padrão Strangler Fig.

Este serviço implementa uma refatoração progressiva que permite migrar
gradualmente do GLPIService legado para a nova arquitetura baseada em
DTOs, Queries e Adapters, sem quebrar a funcionalidade existente.
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from ...infrastructure.external.glpi.metrics_adapter import GLPIConfig, GLPIMetricsAdapter
from ..dto.metrics_dto import (
    MetricsFilterDTO,
    create_error_response,
    create_success_response,
)

# Import consolidated models from schemas
from schemas.dashboard import (
    DashboardMetrics,
    ApiResponse,
    ApiError,
)
from ..queries.metrics_query import (
    DashboardMetricsQuery,
    GeneralMetricsQuery,
    MetricsQueryFactory,
    QueryContext,
    TechnicianRankingQuery,
)

logger = logging.getLogger(__name__)


class RefactoringPhase(Enum):
    """Fases da refatoração progressiva."""

    LEGACY_ONLY = "legacy_only"  # Usar apenas código legado
    STRANGLER_FIG = "strangler_fig"  # Interceptar e redirecionar gradualmente
    NEW_ARCHITECTURE = "new_architecture"  # Usar apenas nova arquitetura
    VALIDATION = "validation"  # Executar ambos e comparar


@dataclass
class RefactoringConfig:
    """Configuração para refatoração progressiva."""

    phase: RefactoringPhase = RefactoringPhase.LEGACY_ONLY

    # Configurações de migração gradual
    migration_percentage: float = 0.0  # % de requests para nova arquitetura
    endpoints_to_migrate: List[str] = None  # Endpoints específicos para migrar

    # Configurações de validação
    enable_validation: bool = False  # Executar ambas implementações
    validation_sampling: float = 0.1  # % de requests para validação

    # Configurações de fallback
    enable_fallback: bool = True  # Fallback para legado em caso de erro
    fallback_timeout_ms: int = 5000  # Timeout para fallback

    # Configurações de observabilidade
    log_performance_comparison: bool = True
    log_data_differences: bool = True

    def __post_init__(self):
        if self.endpoints_to_migrate is None:
            self.endpoints_to_migrate = []


class ProgressiveRefactoringService:
    """Serviço para refatoração progressiva usando padrão Strangler Fig."""

    def __init__(
        self,
        config: RefactoringConfig,
        glpi_config: GLPIConfig,
        legacy_service: Any = None,
    ):
        self.config = config
        self.legacy_service = legacy_service
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Inicializar nova arquitetura  
        from core.infrastructure.external.glpi.metrics_adapter import GLPIMetricsAdapter
        self.glpi_adapter = GLPIMetricsAdapter(glpi_config)

        self.query_factory = MetricsQueryFactory(self.glpi_adapter)

        # Métricas de performance
        self.performance_metrics = {
            "legacy_calls": 0,
            "new_calls": 0,
            "validation_calls": 0,
            "fallback_calls": 0,
            "errors": 0,
        }

    async def get_dashboard_metrics(
        self,
        filters: Optional[MetricsFilterDTO] = None,
        correlation_id: Optional[str] = None,
    ) -> ApiResponse:
        """Obtém métricas do dashboard usando refatoração progressiva."""

        context = QueryContext(
            correlation_id=correlation_id,
            user_id=None,
            request_timestamp=datetime.now(),
        )

        endpoint = "dashboard_metrics"

        try:
            # Determinar qual implementação usar
            use_new_architecture = self._should_use_new_architecture(endpoint)

            if self.config.phase == RefactoringPhase.VALIDATION:
                return await self._execute_validation_mode(filters, context)

            elif use_new_architecture:
                return await self._execute_new_architecture(filters, context)

            else:
                return await self._execute_legacy_with_fallback(filters, context)

        except Exception as e:
            self.logger.error(
                f"Erro na obtenção de métricas do dashboard: {str(e)}",
                extra={"correlation_id": correlation_id},
            )
            self.performance_metrics["errors"] += 1
            return create_error_response(f"Erro interno: {str(e)}")

    async def get_technician_ranking(
        self,
        filters: Optional[MetricsFilterDTO] = None,
        correlation_id: Optional[str] = None,
    ) -> ApiResponse:
        """Obtém ranking de técnicos usando refatoração progressiva."""

        context = QueryContext(
            correlation_id=correlation_id,
            user_id=None,
            request_timestamp=datetime.now(),
        )

        endpoint = "technician_ranking"

        try:
            use_new_architecture = self._should_use_new_architecture(endpoint)

            if self.config.phase == RefactoringPhase.VALIDATION:
                return await self._execute_validation_mode_ranking(filters, context)

            elif use_new_architecture:
                return await self._execute_new_architecture_ranking(filters, context)

            else:
                return await self._execute_legacy_ranking_with_fallback(filters, context)

        except Exception as e:
            self.logger.error(
                f"Erro na obtenção de ranking de técnicos: {str(e)}",
                extra={"correlation_id": correlation_id},
            )
            self.performance_metrics["errors"] += 1
            return create_error_response(f"Erro interno: {str(e)}")

    async def get_general_metrics(
        self,
        filters: Optional[MetricsFilterDTO] = None,
        correlation_id: Optional[str] = None,
    ) -> ApiResponse:
        """Obtém métricas gerais usando refatoração progressiva."""

        context = QueryContext(
            correlation_id=correlation_id,
            user_id=None,
            request_timestamp=datetime.now(),
        )

        endpoint = "general_metrics"

        try:
            use_new_architecture = self._should_use_new_architecture(endpoint)

            if self.config.phase == RefactoringPhase.VALIDATION:
                return await self._execute_validation_mode_general(filters, context)

            elif use_new_architecture:
                return await self._execute_new_architecture_general(filters, context)

            else:
                return await self._execute_legacy_general_with_fallback(filters, context)

        except Exception as e:
            self.logger.error(
                f"Erro na obtenção de métricas gerais: {str(e)}",
                extra={"correlation_id": correlation_id},
            )
            self.performance_metrics["errors"] += 1
            return create_error_response(f"Erro interno: {str(e)}")

    def _should_use_new_architecture(self, endpoint: str) -> bool:
        """Determina se deve usar nova arquitetura baseado na configuração."""

        if self.config.phase == RefactoringPhase.LEGACY_ONLY:
            return False

        if self.config.phase == RefactoringPhase.NEW_ARCHITECTURE:
            return True

        if self.config.phase == RefactoringPhase.STRANGLER_FIG:
            # Verificar se endpoint está na lista de migração
            if endpoint in self.config.endpoints_to_migrate:
                return True

            # Usar percentual de migração
            import random

            return random.random() < self.config.migration_percentage

        return False

    async def _execute_new_architecture(
        self, filters: Optional[MetricsFilterDTO], context: QueryContext
    ) -> ApiResponse:
        """Executa usando nova arquitetura."""

        start_time = time.time()

        try:
            # Criar query para dashboard
            dashboard_query = self.query_factory.create_dashboard_query()

            # Executar query
            result = await dashboard_query.execute(filters, context)

            # Converter para DTO de resposta
            dashboard_dto = DashboardMetrics(
                general=result.get("general", {}),
                levels=result.get("levels", {}),
                trends=result.get("trends", {}),
                recent_tickets=result.get("recent_tickets", []),
                timestamp=datetime.now(),
            )

            execution_time = time.time() - start_time

            self.performance_metrics["new_calls"] += 1

            self.logger.info(
                f"Nova arquitetura executada com sucesso",
                extra={
                    "correlation_id": context.correlation_id,
                    "execution_time": execution_time,
                    "architecture": "new",
                },
            )

            return create_success_response(data=dashboard_dto, execution_time=execution_time)

        except Exception as e:
            if self.config.enable_fallback:
                self.logger.warning(
                    f"Erro na nova arquitetura, fazendo fallback: {str(e)}",
                    extra={"correlation_id": context.correlation_id},
                )
                return await self._execute_legacy_fallback(filters, context)
            else:
                raise

    async def _execute_legacy_with_fallback(
        self, filters: Optional[MetricsFilterDTO], context: QueryContext
    ) -> ApiResponse:
        """Executa usando arquitetura legada."""

        start_time = time.time()

        try:
            # Converter filtros DTO para formato legado
            legacy_params = self._convert_filters_to_legacy(filters)

            # Executar método legado
            if hasattr(self.legacy_service, "get_dashboard_metrics_with_date_filter"):
                result = self.legacy_service.get_dashboard_metrics_with_date_filter(
                    start_date=legacy_params.get("start_date"),
                    end_date=legacy_params.get("end_date"),
                )
            else:
                # Fallback para método padrão
                result = self.legacy_service.get_metrics()

            execution_time = time.time() - start_time

            self.performance_metrics["legacy_calls"] += 1

            # Converter resultado legado para DTO
            dashboard_dto = self._convert_legacy_result_to_dto(result)

            self.logger.info(
                f"Arquitetura legada executada com sucesso",
                extra={
                    "correlation_id": context.correlation_id,
                    "execution_time": execution_time,
                    "architecture": "legacy",
                },
            )

            return create_success_response(data=dashboard_dto, execution_time=execution_time)

        except Exception as e:
            self.logger.error(
                f"Erro na arquitetura legada: {str(e)}",
                extra={"correlation_id": context.correlation_id},
            )
            raise

    async def _execute_validation_mode(self, filters: Optional[MetricsFilterDTO], context: QueryContext) -> ApiResponse:
        """Executa ambas implementações e compara resultados."""

        import random

        # Verificar se deve executar validação baseado no sampling
        if random.random() > self.config.validation_sampling:
            # Executar apenas uma implementação
            return await self._execute_new_architecture(filters, context)

        self.performance_metrics["validation_calls"] += 1

        # Executar ambas implementações
        start_time = time.time()

        try:
            # Executar nova arquitetura
            new_result_task = asyncio.create_task(self._execute_new_architecture(filters, context))

            # Executar arquitetura legada
            legacy_result_task = asyncio.create_task(self._execute_legacy_with_fallback(filters, context))

            # Aguardar ambos os resultados
            new_result, legacy_result = await asyncio.gather(new_result_task, legacy_result_task, return_exceptions=True)

            execution_time = time.time() - start_time

            # Comparar resultados
            await self._compare_results(new_result, legacy_result, context, execution_time)

            # Retornar resultado da nova arquitetura se bem-sucedido
            if isinstance(new_result, ApiResponse) and new_result.success:
                return new_result
            elif isinstance(legacy_result, ApiResponse) and legacy_result.success:
                return legacy_result
            else:
                return create_error_response("Ambas implementações falharam")

        except Exception as e:
            self.logger.error(
                f"Erro no modo de validação: {str(e)}",
                extra={"correlation_id": context.correlation_id},
            )
            # Fallback para arquitetura legada
            return await self._execute_legacy_with_fallback(filters, context)

    async def _execute_legacy_fallback(self, filters: Optional[MetricsFilterDTO], context: QueryContext) -> ApiResponse:
        """Executa fallback para arquitetura legada."""

        self.performance_metrics["fallback_calls"] += 1

        self.logger.info(
            "Executando fallback para arquitetura legada",
            extra={"correlation_id": context.correlation_id},
        )

        return await self._execute_legacy_with_fallback(filters, context)

    def _convert_filters_to_legacy(self, filters: Optional[MetricsFilterDTO]) -> Dict[str, Any]:
        """Converte filtros DTO para formato legado."""

        if not filters:
            return {}

        legacy_params = {}

        if filters.start_date:
            legacy_params["start_date"] = filters.start_date.strftime("%Y-%m-%d")

        if filters.end_date:
            legacy_params["end_date"] = filters.end_date.strftime("%Y-%m-%d")

        if filters.status:
            legacy_params["status"] = filters.status.value

        if filters.technician_id:
            legacy_params["technician_id"] = filters.technician_id

        if filters.category_id:
            legacy_params["category_id"] = filters.category_id

        if filters.priority:
            legacy_params["priority"] = filters.priority

        return legacy_params

    def _convert_legacy_result_to_dto(self, legacy_result: Dict[str, Any]) -> DashboardMetrics:
        """Converte resultado legado para DTO."""

        if not legacy_result or not isinstance(legacy_result, dict):
            return DashboardMetrics(
                general={},
                levels={},
                trends={},
                recent_tickets=[],
                timestamp=datetime.now(),
            )

        # Extrair dados do resultado legado
        data = legacy_result.get("data", {})

        return DashboardMetrics(
            general=data.get("geral", {}),
            levels={
                "n1": data.get("niveis", {}).get("n1", {}),
                "n2": data.get("niveis", {}).get("n2", {}),
                "n3": data.get("niveis", {}).get("n3", {}),
                "n4": data.get("niveis", {}).get("n4", {}),
            },
            trends=data.get("tendencias", {}),
            recent_tickets=data.get("recent_tickets", []),
            timestamp=datetime.now(),
        )

    async def _compare_results(
        self,
        new_result: Any,
        legacy_result: Any,
        context: QueryContext,
        execution_time: float,
    ) -> None:
        """Compara resultados das duas implementações."""

        comparison_data = {
            "correlation_id": context.correlation_id,
            "execution_time": execution_time,
            "new_success": isinstance(new_result, ApiResponse) and new_result.success,
            "legacy_success": isinstance(legacy_result, ApiResponse) and legacy_result.success,
        }

        if self.config.log_performance_comparison:
            # Comparar performance
            new_time = getattr(new_result, "execution_time", 0) if hasattr(new_result, "execution_time") else 0
            legacy_time = getattr(legacy_result, "execution_time", 0) if hasattr(legacy_result, "execution_time") else 0

            comparison_data.update(
                {
                    "new_execution_time": new_time,
                    "legacy_execution_time": legacy_time,
                    "performance_difference": new_time - legacy_time,
                }
            )

        if self.config.log_data_differences:
            # Comparar dados (implementação simplificada)
            data_match = self._compare_data_structures(new_result, legacy_result)
            comparison_data["data_match"] = data_match

        self.logger.info("Comparação de resultados concluída", extra=comparison_data)

    def _compare_data_structures(self, new_result: Any, legacy_result: Any) -> bool:
        """Compara estruturas de dados (implementação simplificada)."""

        try:
            # Implementação básica - pode ser expandida
            if not isinstance(new_result, ApiResponse) or not isinstance(legacy_result, ApiResponse):
                return False

            if not new_result.success or not legacy_result.success:
                return False

            # Comparar campos principais
            new_data = new_result.data
            legacy_data = legacy_result.data

            if not isinstance(new_data, DashboardMetrics) or not isinstance(legacy_data, DashboardMetrics):
                return False

            # Comparação básica de totais
            new_general = new_data.general
            legacy_general = legacy_data.general

            return new_general.get("total", 0) == legacy_general.get("total", 0) and new_general.get(
                "novos", 0
            ) == legacy_general.get("novos", 0)

        except Exception as e:
            self.logger.warning(f"Erro na comparação de dados: {str(e)}")
            return False


    def get_performance_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de performance da refatoração."""

        total_calls = sum(
            [
                self.performance_metrics["legacy_calls"],
                self.performance_metrics["new_calls"],
                self.performance_metrics["validation_calls"],
            ]
        )

        return {
            **self.performance_metrics,
            "total_calls": total_calls,
            "new_architecture_percentage": (
                self.performance_metrics["new_calls"] / total_calls * 100 if total_calls > 0 else 0
            ),
            "fallback_rate": (self.performance_metrics["fallback_calls"] / total_calls * 100 if total_calls > 0 else 0),
            "error_rate": (self.performance_metrics["errors"] / total_calls * 100 if total_calls > 0 else 0),
        }

    async def close(self) -> None:
        """Fecha recursos e conexões."""
        if self.glpi_adapter:
            await self.glpi_adapter.close()


# Factory para criação do serviço
def create_progressive_refactoring_service(
    phase: RefactoringPhase,
    glpi_config: GLPIConfig,
    legacy_service: Any = None,
    **kwargs,
) -> ProgressiveRefactoringService:
    """Cria instância do ProgressiveRefactoringService."""

    config = RefactoringConfig(phase=phase, **kwargs)

    return ProgressiveRefactoringService(config=config, glpi_config=glpi_config, legacy_service=legacy_service)


# Exemplo de uso
async def example_usage():
    """Exemplo de como usar o ProgressiveRefactoringService."""

    # Configurar GLPI
    glpi_config = GLPIConfig(
        base_url="https://glpi.example.com",
        app_token="your-app-token",
        user_token="your-user-token",
    )

    # Importar serviço refatorado (usando facade)
    from backend.services.legacy.glpi_service_facade import GLPIServiceFacade

    legacy_service = GLPIServiceFacade()

    # Criar serviço de refatoração progressiva
    refactoring_service = create_progressive_refactoring_service(
        phase=RefactoringPhase.STRANGLER_FIG,
        glpi_config=glpi_config,
        legacy_service=legacy_service,
        migration_percentage=0.1,  # 10% para nova arquitetura
        enable_validation=True,
        validation_sampling=0.05,  # 5% para validação
    )

    try:
        # Obter métricas do dashboard
        filters = MetricsFilterDTO()
        result = await refactoring_service.get_dashboard_metrics(filters=filters, correlation_id="example-123")

        print(f"Sucesso: {result.success}")
        if result.success:
            print(f"Dados: {result.data}")

        # Verificar métricas de performance
        performance = refactoring_service.get_performance_metrics()
        print(f"Performance: {performance}")

    finally:
        # Fechar recursos
        await refactoring_service.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
