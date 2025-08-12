from fastapi import APIRouter, Query
from backend.schemas.response import ApiResponse
from backend.schemas.dashboard import KpiResponse
import logging
from enum import Enum

class BoolStr(str, Enum):
    TRUE = 'true'
    FALSE = 'false'

# Configuração do logger
logger = logging.getLogger("api.routes")

# Router principal
router = APIRouter()

@router.get("/kpis", response_model=ApiResponse[KpiResponse])
async def get_kpis(force_refresh: BoolStr = Query(BoolStr.FALSE)):
    """Endpoint para buscar KPIs do dashboard - HOTFIX: dados mock simples.

    Retorna um payload mínimo e estável, sem qualquer dependência de GLPI
    ou módulos auxiliares para evitar erros 500 por efeitos colaterais.

    Exemplo de resposta:
    {
      "success": true,
      "message": "KPIs mockados (hexagonal)",
      "data": {
        "niveis": {
          "geral": {"novos": 45, "progresso": 23, "pendentes": 12, "resolvidos": 156, "total": 236},
          "n1": {"novos": 12, "progresso": 8, "pendentes": 3, "resolvidos": 42, "total": 65}
        },
        "tendencias": {"novos": "+12.5%", "pendentes": "-8.3%"}
      }
    }
    """
    logger.info("HOTFIX: Retornando dados mock para /hexagonal/kpis")

    # Converter para bool
    force_refresh_bool = force_refresh == BoolStr.TRUE

    mock_data = {
        "niveis": {
            "geral": {"novos": 45, "progresso": 23, "pendentes": 12, "resolvidos": 156, "total": 236},
            "n1": {"novos": 12, "progresso": 8, "pendentes": 3, "resolvidos": 42, "total": 65},
            "n2": {"novos": 15, "progresso": 7, "pendentes": 4, "resolvidos": 38, "total": 64},
            "n3": {"novos": 10, "progresso": 5, "pendentes": 3, "resolvidos": 41, "total": 59},
            "n4": {"novos": 8, "progresso": 3, "pendentes": 2, "resolvidos": 35, "total": 48}
        },
        "tendencias": {"novos": "+12.5%", "pendentes": "-8.3%", "progresso": "+15.7%", "resolvidos": "+22.1%"}
    }

    return ApiResponse(success=True, message="KPIs mockados (hexagonal)", data=KpiResponse(**mock_data))
