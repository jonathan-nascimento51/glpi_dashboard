from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/kpis")
async def get_kpis() -> Dict[str, Any]:
    """Endpoint para obter KPIs do dashboard"""
    try:
        # Mock data para teste - substitua pela l�gica real
        kpis_data = {
            "total_tickets": 150,
            "open_tickets": 45,
            "resolved_tickets": 105,
            "avg_resolution_time": 2.5,
            "satisfaction_rate": 85.2,
            "technician_efficiency": 78.9
        }
        
        return {
            "success": True,
            "data": kpis_data
        }
    except Exception as e:
        logger.error(f"Erro ao obter KPIs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@router.get("/system/status")
async def get_system_status() -> Dict[str, Any]:
    """Endpoint para verificar status do sistema"""
    try:
        status_data = {
            "api": "online",
            "glpi": "online",
            "database": "online",
            "last_update": "2024-01-15 10:30:00",
            "version": "1.0.0"
        }
        
        return {
            "success": True,
            "data": status_data
        }
    except Exception as e:
        logger.error(f"Erro ao verificar status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@router.get("/technicians/ranking")
async def get_technician_ranking() -> Dict[str, Any]:
    """Endpoint para obter ranking de t�cnicos"""
    try:
        ranking_data = [
            {"id": 1, "name": "Jo�o Silva", "tickets_resolved": 25, "avg_time": 2.1, "satisfaction": 92.5},
            {"id": 2, "name": "Maria Santos", "tickets_resolved": 22, "avg_time": 1.8, "satisfaction": 89.3},
            {"id": 3, "name": "Pedro Costa", "tickets_resolved": 20, "avg_time": 2.3, "satisfaction": 87.1}
        ]
        
        return {
            "success": True,
            "data": ranking_data
        }
    except Exception as e:
        logger.error(f"Erro ao obter ranking: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@router.get("/tickets/new")
async def get_new_tickets(limit: int = 6) -> Dict[str, Any]:
    """Endpoint para obter novos tickets"""
    try:
        tickets_data = [
            {"id": 1, "title": "Problema de rede", "priority": "Alta", "status": "Aberto", "created_at": "2024-01-15T10:30:00Z"},
            {"id": 2, "title": "Instala��o de software", "priority": "M�dia", "status": "Em andamento", "created_at": "2024-01-15T09:15:00Z"},
            {"id": 3, "title": "Manuten��o preventiva", "priority": "Baixa", "status": "Pendente", "created_at": "2024-01-15T08:45:00Z"},
            {"id": 4, "title": "Suporte t�cnico", "priority": "Alta", "status": "Aberto", "created_at": "2024-01-15T08:00:00Z"},
            {"id": 5, "title": "Configura��o de email", "priority": "M�dia", "status": "Em andamento", "created_at": "2024-01-15T07:30:00Z"},
            {"id": 6, "title": "Backup de dados", "priority": "Baixa", "status": "Conclu�do", "created_at": "2024-01-15T07:00:00Z"}
        ][:limit]
        
        return {
            "success": True,
            "data": tickets_data
        }
    except Exception as e:
        logger.error(f"Erro ao obter tickets: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")
