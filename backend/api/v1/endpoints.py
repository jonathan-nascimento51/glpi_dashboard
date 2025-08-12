# -*- coding: utf-8 -*-
from fastapi import APIRouter, Query, HTTPException
from backend.schemas.response import ApiResponse, ErrorDetail
from backend.schemas.dashboard import KpiResponse, KpiQueryParams
from backend.services.glpi_service import GLPIService
from backend.app.flags import Flags
from .metrics import router as metrics_router
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
flags = Flags()
glpi_service = GLPIService()

# Include metrics routes
router.include_router(metrics_router)

@router.get(
    "/kpis",
    response_model=ApiResponse[KpiResponse],
    summary="Obtém os principais indicadores de desempenho (KPIs)",
    description="Retorna uma visão geral dos KPIs de tickets, divididos por nível e com tendências.",
    tags=["Dashboard"],
)
async def get_kpis(params: KpiQueryParams = Query(...)):
    """
    Endpoint para obter os principais indicadores de desempenho (KPIs) do sistema.

    - **Comportamento:**
      - Se a flag `USE_REAL_GLPI_DATA` estiver ativa, busca dados reais do GLPI.
      - Caso contrário, retorna dados mockados para desenvolvimento e testes.

    - **Parâmetros de Query:**
      - `start_date`: Data de início para filtrar os KPIs (formato: YYYY-MM-DD).
      - `end_date`: Data de fim para filtrar os KPIs (formato: YYYY-MM-DD).

    - **Respostas:**
      - `200 OK`: Retorna os dados dos KPIs no formato `KpiResponse`.
      - `500 Internal Server Error`: Se ocorrer um erro inesperado no servidor.
    """
    try:
        if flags.is_enabled("USE_REAL_GLPI_DATA"):
            # Lógica para buscar dados reais do GLPI
            metrics = glpi_service.get_dashboard_metrics(
                start_date=params.start_date, end_date=params.end_date
            )
            return ApiResponse[KpiResponse](
                success=True,
                message="KPIs obtidos do GLPI com sucesso.",
                data=KpiResponse(**metrics),
            )
        else:
            # Lógica para retornar dados mockados
            mock_data = {
                "niveis": {
                    "geral": {"novos": 45, "progresso": 23, "pendentes": 12, "resolvidos": 156, "total": 236},
                    "n1": {"novos": 12, "progresso": 8, "pendentes": 3, "resolvidos": 42, "total": 65},
                    "n2": {"novos": 15, "progresso": 7, "pendentes": 4, "resolvidos": 38, "total": 64},
                    "n3": {"novos": 10, "progresso": 5, "pendentes": 3, "resolvidos": 41, "total": 59},
                    "n4": {"novos": 8, "progresso": 3, "pendentes": 2, "resolvidos": 35, "total": 48},
                },
                "tendencias": {
                    "novos": "+12.5%",
                    "pendentes": "-8.3%",
                    "progresso": "+15.7%",
                    "resolvidos": "+22.1%",
                },
            }
            return ApiResponse[KpiResponse](
                success=True,
                message="KPIs mockados retornados com sucesso.",
                data=KpiResponse(**mock_data),
            )
    except Exception as e:
        logger.error(f"Erro ao buscar KPIs: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=ApiResponse[None](
                success=False,
                message="Erro interno ao processar a solicitação de KPIs.",
                errors=[ErrorDetail(message=str(e), code="KPI_FETCH_ERROR")],
            ),
        )