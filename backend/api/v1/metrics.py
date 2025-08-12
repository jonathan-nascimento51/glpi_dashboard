# -*- coding: utf-8 -*-
"""Endpoints para métricas e monitoramento"""

from fastapi import APIRouter, Response, HTTPException
from typing import Dict, Any, Optional, List
import logging

from utils.metrics import get_metrics, CONTENT_TYPE_LATEST
from schemas.response import ApiResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/prometheus", response_class=Response)
async def get_prometheus_metrics():
    """Endpoint para métricas Prometheus

    Retorna métricas no formato Prometheus para scraping.
    """
    try:
        metrics = get_metrics()
        prometheus_data = metrics.get_prometheus_metrics()

        return Response(content=prometheus_data, media_type=CONTENT_TYPE_LATEST)
    except Exception as e:
        logger.error(f"Erro ao obter métricas Prometheus: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao obter métricas")


@router.get("/structured", response_model=ApiResponse[List[Dict[str, Any]]])
async def get_structured_logs(limit: Optional[int] = 100):
    """Endpoint para logs estruturados

    Args:
        limit: Número máximo de logs a retornar (padrão: 100)

    Returns:
        Lista de eventos de log estruturados
    """
    try:
        if limit and (limit < 1 or limit > 1000):
            raise HTTPException(
                status_code=400, detail="Limite deve estar entre 1 e 1000"
            )

        metrics = get_metrics()
        logs = metrics.get_structured_logs(limit)

        return ApiResponse(
            success=True, data=logs, message=f"Retornados {len(logs)} eventos de log"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter logs estruturados: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao obter logs")


@router.get("/summary", response_model=ApiResponse[Dict[str, Any]])
async def get_metrics_summary():
    """Endpoint para resumo de métricas

    Returns:
        Estatísticas resumidas das métricas coletadas
    """
    try:
        metrics = get_metrics()
        summary = metrics.get_summary_stats()

        return ApiResponse(
            success=True, data=summary, message="Resumo de métricas obtido com sucesso"
        )
    except Exception as e:
        logger.error(f"Erro ao obter resumo de métricas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao obter resumo")


@router.get("/health", response_model=ApiResponse[Dict[str, Any]])
async def get_metrics_health():
    """Endpoint para verificar saúde do sistema de métricas

    Returns:
        Status de saúde do sistema de métricas
    """
    try:
        metrics = get_metrics()

        # Verificar se o sistema está funcionando
        summary = metrics.get_summary_stats()

        health_data = {
            "metrics_enabled": True,
            "prometheus_enabled": summary.get("prometheus_enabled", False),
            "total_events_recorded": summary.get("total_events", 0),
            "structured_logs_count": len(metrics.get_structured_logs()),
            "status": "healthy",
        }

        return ApiResponse(
            success=True,
            data=health_data,
            message="Sistema de métricas funcionando corretamente",
        )
    except Exception as e:
        logger.error(f"Erro ao verificar saúde das métricas: {e}")

        # Retornar status não saudável mas não falhar
        health_data = {
            "metrics_enabled": False,
            "prometheus_enabled": False,
            "total_events_recorded": 0,
            "structured_logs_count": 0,
            "status": "unhealthy",
            "error": str(e),
        }

        return ApiResponse(
            success=False, data=health_data, message="Sistema de métricas com problemas"
        )


@router.post("/reset", response_model=ApiResponse[Dict[str, str]])
async def reset_metrics():
    """Endpoint para resetar métricas (apenas logs estruturados)

    ATENÇÃO: Este endpoint limpa os logs estruturados.
    As métricas Prometheus não são afetadas.

    Returns:
        Confirmação do reset
    """
    try:
        metrics = get_metrics()

        # Limpar apenas logs estruturados
        old_count = len(metrics.structured_logs)
        metrics.structured_logs.clear()

        logger.info(f"Métricas resetadas. {old_count} logs removidos.")

        return ApiResponse(
            success=True,
            data={"status": "reset", "logs_removed": str(old_count)},
            message=f"Logs estruturados resetados. {old_count} eventos removidos.",
        )
    except Exception as e:
        logger.error(f"Erro ao resetar métricas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao resetar métricas")
