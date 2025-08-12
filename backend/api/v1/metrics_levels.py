# -*- coding: utf-8 -*-
"""Endpoint para m?tricas consolidadas por n?vel"""

from datetime import date, datetime
from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse

from schemas.metrics_levels import (
    MetricsLevelsQueryParams,
    MetricsLevelsResponse,
    StatusFilter,
    ServiceLevel,
)
from schemas.response import ApiResponse
from usecases.metrics_levels_usecase import MetricsLevelsUseCase
from utils.structured_logger import create_glpi_logger

router = APIRouter(prefix="/metrics", tags=["metrics-levels"])
logger = create_glpi_logger()


@router.get(
    "/levels",
    response_model=ApiResponse[MetricsLevelsResponse],
    summary="M?tricas consolidadas por n?vel",
    description="""Retorna m?tricas consolidadas de tickets agrupadas por n?vel de servi?o (N1-N4).
    
    Funcionalidades:
    - Filtros por per?odo, status e n?veis espec?ficos
    - M?tricas agregadas e por n?vel individual
    - Detec??o de anomalias com z-score (opcional)
    - Suporte a timezone
    - Metadados de execu??o
    
    Exemplo de uso:
    - `/metrics/levels` - Todas as m?tricas dos ?ltimos 30 dias
    - `/metrics/levels?status=resolvidos&levels=n1,n2` - Apenas tickets resolvidos N1 e N2
    - `/metrics/levels?include_zscore=true&zscore_threshold=2.0` - Com detec??o de anomalias
    """,
)
async def get_metrics_by_levels(
    start_date: Optional[date] = Query(
        None, description="Data de in?cio (YYYY-MM-DD). Padr?o: 30 dias atr?s"
    ),
    end_date: Optional[date] = Query(
        None, description="Data de fim (YYYY-MM-DD). Padr?o: hoje"
    ),
    status: StatusFilter = Query(
        StatusFilter.ALL, description="Filtro por status dos tickets"
    ),
    levels: Optional[str] = Query(
        None, description="N?veis espec?ficos separados por v?rgula (ex: n1,n2,n3)"
    ),
    timezone: str = Query(
        "America/Sao_Paulo", description="Timezone para c?lculos de data"
    ),
    include_zscore: bool = Query(
        False, description="Incluir detec??o de anomalias com z-score"
    ),
    zscore_threshold: float = Query(
        2.0,
        ge=0.5,
        le=5.0,
        description="Threshold para detec??o de anomalias (padr?o: 2.0)",
    ),
) -> ApiResponse[MetricsLevelsResponse]:
    """Endpoint para obter m?tricas consolidadas por n?vel"""

    try:
        logger.info(
            f"Solicita??o de m?tricas por n?vel: status={status}, levels={levels}"
        )

        # Processar n?veis se fornecidos
        parsed_levels = None
        if levels:
            try:
                level_list = [level.strip().lower() for level in levels.split(",")]
                parsed_levels = [
                    ServiceLevel(level)
                    for level in level_list
                    if level in ["n1", "n2", "n3", "n4"]
                ]
                if not parsed_levels:
                    raise ValueError("Nenhum n?vel v?lido fornecido")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"N?veis inv?lidos: {levels}. Use: n1, n2, n3, n4",
                )

        # Criar par?metros da consulta
        query_params = MetricsLevelsQueryParams(
            start_date=start_date,
            end_date=end_date,
            status=status,
            levels=parsed_levels or [ServiceLevel.ALL],
            timezone=timezone,
            include_zscore=include_zscore,
            zscore_threshold=zscore_threshold,
        )

        # Executar use case
        use_case = MetricsLevelsUseCase()
        result = await use_case.get_metrics_by_level(query_params)

        if not result:
            logger.error("Erro no use case: resultado vazio")
            raise HTTPException(
                status_code=500, detail="Erro no processamento das m?tricas"
            )

        logger.info(
            f"M?tricas obtidas com sucesso: {result.aggregated_metrics.total_tickets_all_levels} tickets processados"
        )
        return ApiResponse(
            success=True, message="Métricas por nível obtidas com sucesso", data=result
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao obter m?tricas por n?vel: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )


@router.get(
    "/levels/summary",
    summary="Resumo r?pido das m?tricas por n?vel",
    description="Retorna apenas os totais agregados sem detalhamento por n?vel",
)
async def get_metrics_summary(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    status: StatusFilter = Query(StatusFilter.ALL),
) -> JSONResponse:
    """Endpoint simplificado para resumo das m?tricas"""

    try:
        query_params = MetricsLevelsQueryParams(
            start_date=start_date, end_date=end_date, status=status
        )

        use_case = MetricsLevelsUseCase()
        result = await use_case.get_metrics_by_level(query_params)

        if not result:
            raise HTTPException(
                status_code=500, detail="Erro no processamento das m?tricas"
            )

        # Retornar apenas dados agregados
        summary = {
            "total_tickets": result.aggregated_metrics.total_tickets_all_levels,
            "avg_resolution_time_hours": result.aggregated_metrics.avg_resolution_time_all_levels,
            "overall_sla_compliance_rate": result.aggregated_metrics.overall_sla_compliance,
            "timestamp": datetime.now().isoformat(),
        }

        return JSONResponse(content=summary)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter resumo das m?tricas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get(
    "/levels/health",
    summary="Health check do endpoint de m?tricas",
    description="Verifica se o endpoint est? funcionando corretamente",
)
async def metrics_levels_health() -> JSONResponse:
    """Health check espec?fico para m?tricas por n?vel"""

    try:
        # Teste r?pido com dados mock
        query_params = MetricsLevelsQueryParams()
        use_case = MetricsLevelsUseCase()
        result = await use_case.get_metrics_by_level(query_params)

        is_healthy = (
            result is not None
            and hasattr(result, "aggregated_metrics")
            and result.aggregated_metrics is not None
        )

        status = "healthy" if is_healthy else "unhealthy"

        return JSONResponse(
            content={
                "status": status,
                "service": "metrics-levels",
                "timestamp": datetime.now().isoformat(),
                "test_result": {
                    "success": is_healthy,
                    "has_data": result is not None,
                    "has_aggregated_metrics": hasattr(result, "aggregated_metrics") and result.aggregated_metrics is not None,
                },
            },
            status_code=200 if is_healthy else 503,
        )

    except Exception as e:
        logger.error(f"Health check falhou: {e}")
        return JSONResponse(
            content={
                "status": "unhealthy",
                "service": "metrics-levels",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
            },
            status_code=503,
        )
