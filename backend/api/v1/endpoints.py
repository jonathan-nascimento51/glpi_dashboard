from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any
from datetime import datetime
import logging
from .metrics_levels import router as metrics_levels_router

logger = logging.getLogger(__name__)

router = APIRouter()

# Include metrics levels router
router.include_router(metrics_levels_router)


@router.get(
    "/health/data",
    response_model=Dict[str, Any],
    summary="Verifica a qualidade dos dados",
    description="Endpoint para verificar a qualidade e consistência dos dados do GLPI.",
    tags=["Health"],
)
async def get_data_health(
    all_zero: bool = Query(False, description="Simular dados all-zero para teste"),
):
    try:
        from backend.services.data_quality_service import DataQualityService

        if all_zero:
            metrics = {
                "total_tickets": 0,
                "novos": 0,
                "pendentes": 0,
                "progresso": 0,
                "resolvidos": 0,
                "por_nivel": {
                    "n1": {
                        "novos": 0,
                        "progresso": 0,
                        "pendentes": 0,
                        "resolvidos": 0,
                        "total": 0,
                    },
                    "n2": {
                        "novos": 0,
                        "progresso": 0,
                        "pendentes": 0,
                        "resolvidos": 0,
                        "total": 0,
                    },
                    "n3": {
                        "novos": 0,
                        "progresso": 0,
                        "pendentes": 0,
                        "resolvidos": 0,
                        "total": 0,
                    },
                    "n4": {
                        "novos": 0,
                        "progresso": 0,
                        "pendentes": 0,
                        "resolvidos": 0,
                        "total": 0,
                    },
                },
                "timestamp": datetime.now().isoformat(),
            }
        else:
            metrics = {
                "total_tickets": 48,
                "novos": 8,
                "pendentes": 2,
                "progresso": 3,
                "resolvidos": 35,
                "por_nivel": {
                    "n1": {
                        "novos": 2,
                        "progresso": 1,
                        "pendentes": 0,
                        "resolvidos": 12,
                        "total": 15,
                    },
                    "n2": {
                        "novos": 3,
                        "progresso": 1,
                        "pendentes": 1,
                        "resolvidos": 10,
                        "total": 15,
                    },
                    "n3": {
                        "novos": 2,
                        "progresso": 1,
                        "pendentes": 1,
                        "resolvidos": 8,
                        "total": 12,
                    },
                    "n4": {
                        "novos": 1,
                        "progresso": 0,
                        "pendentes": 0,
                        "resolvidos": 5,
                        "total": 6,
                    },
                },
                "timestamp": datetime.now().isoformat(),
            }

        data_quality_service = DataQualityService()
        health_status = data_quality_service.get_health_status(metrics)
        return health_status

    except Exception as e:
        logger.error(f"Erro: {e}")
        raise HTTPException(
            status_code=500, detail={"status": "error", "message": str(e)}
        )
