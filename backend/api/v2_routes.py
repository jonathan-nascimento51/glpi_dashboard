from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
import os

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/kpis")
async def get_v2_kpis() -> Dict[str, Any]:
    """Endpoint v2 para obter KPIs do dashboard com melhorias"""
    try:
        # Verifica se o feature flag está habilitado
        if not os.getenv("FLAG_USE_V2_KPIS", "false").lower() == "true":
            raise HTTPException(status_code=404, detail="Endpoint não disponível")
        
        # Mock data v2 com estrutura melhorada
        kpis_data = {
            "total_tickets": {
                "value": 150,
                "trend": "+5%",
                "previous_period": 143
            },
            "open_tickets": {
                "value": 45,
                "trend": "-2%",
                "previous_period": 46
            },
            "resolved_tickets": {
                "value": 105,
                "trend": "+8%",
                "previous_period": 97
            },
            "avg_resolution_time": {
                "value": 2.5,
                "unit": "hours",
                "trend": "-10%",
                "previous_period": 2.8
            },
            "satisfaction_rate": {
                "value": 85.2,
                "unit": "%",
                "trend": "+3%",
                "previous_period": 82.7
            },
            "technician_efficiency": {
                "value": 78.9,
                "unit": "%",
                "trend": "+1%",
                "previous_period": 78.1
            }
        }

        return {
            "success": True,
            "version": "v2",
            "data": kpis_data,
            "metadata": {
                "last_updated": "2024-01-15T10:30:00Z",
                "cache_ttl": 300
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter KPIs v2: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")
