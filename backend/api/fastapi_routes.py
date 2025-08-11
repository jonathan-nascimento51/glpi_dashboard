# -*- coding: utf-8 -*-
import os
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from services.glpi_service import GLPIService
from services.api_service import APIService
from utils.response_formatter import ResponseFormatter
import logging

logger = logging.getLogger("fastapi_routes")
glpi_service = GLPIService()
api_service = APIService()
USE_REAL_GLPI_DATA = os.getenv("FLAG_USE_REAL_GLPI_DATA", "false").lower() == "true"
router = APIRouter()

@router.get("/kpis")
async def get_kpis(start_date: Optional[str] = Query(None), end_date: Optional[str] = Query(None)):
    try:
        if USE_REAL_GLPI_DATA:
            metrics = glpi_service.get_dashboard_metrics()
            return ResponseFormatter.format_success_response(data=metrics, message="KPIs obtidos do GLPI")
        else:
            mock_data = {
                "niveis": {
                    "geral": {
                        "novos": 45,
                        "progresso": 23,
                        "pendentes": 12,
                        "resolvidos": 156,
                        "total": 236
                    },
                    "n1": {
                        "novos": 12,
                        "progresso": 8,
                        "pendentes": 3,
                        "resolvidos": 42,
                        "total": 65
                    },
                    "n2": {
                        "novos": 15,
                        "progresso": 7,
                        "pendentes": 4,
                        "resolvidos": 38,
                        "total": 64
                    },
                    "n3": {
                        "novos": 10,
                        "progresso": 5,
                        "pendentes": 3,
                        "resolvidos": 41,
                        "total": 59
                    },
                    "n4": {
                        "novos": 8,
                        "progresso": 3,
                        "pendentes": 2,
                        "resolvidos": 35,
                        "total": 48
                    }
                },
                "tendencias": {
                    "novos": "+12.5%",
                    "pendentes": "-8.3%",
                    "progresso": "+15.7%",
                    "resolvidos": "+22.1%"
                }
            }
            return ResponseFormatter.format_success_response(data=mock_data, message="KPIs mockados")
    except Exception as e:
        logger.error(f"Erro ao buscar KPIs: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/system/status")
async def get_system_status():
    try:
        if USE_REAL_GLPI_DATA:
            try:
                if glpi_service._ensure_authenticated():
                    
                    glpi_status = "online"
                else:
                    glpi_status = "offline"
            except:
                glpi_status = "offline"
            status_data = {
                "api": "online",
                "glpi": glpi_status,
                "database": "online",
                "last_update": "2024-01-15T10:30:00Z",
                "version": "1.0.0"
            }
        else:
            status_data = {
                "api": "online",
                "glpi": "online",
                "database": "online",
                "last_update": "2024-01-15T10:30:00Z",
                "version": "1.0.0"
            }
        return ResponseFormatter.format_success_response(data=status_data, message="Status do sistema")
    except Exception as e:
        logger.error(f"Erro ao buscar status: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/technicians/ranking")
async def get_technician_ranking(limit: Optional[int] = Query(10)):
    try:
        if USE_REAL_GLPI_DATA:
            ranking_data = glpi_service.get_technician_ranking(limit=limit)
            return ResponseFormatter.format_success_response(data=ranking_data, message="Ranking de tecnicos do GLPI")
        else:
            ranking_data = [
                {"name": "Joao Silva", "tickets_resolved": 25, "avg_time": 2.1, "satisfaction": 4.8},
                {"name": "Maria Santos", "tickets_resolved": 22, "avg_time": 2.3, "satisfaction": 4.7}
            ]
            return ResponseFormatter.format_success_response(data=ranking_data[:limit], message="Ranking de tecnicos")
    except Exception as e:
        logger.error(f"Erro ao buscar ranking: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/tickets/new")
async def get_new_tickets(limit: Optional[int] = Query(10)):
    try:
        if USE_REAL_GLPI_DATA:
            tickets_data = glpi_service.get_new_tickets(limit=limit)
            return ResponseFormatter.format_success_response(data=tickets_data, message="Novos tickets do GLPI")
        else:
            mock_tickets = [
                {"id": 1, "title": "Problema de rede", "priority": "Alta", "status": "Aberto", "created_at": "2024-01-15T10:00:00Z"},
                {"id": 2, "title": "Instalacao de software", "priority": "Media", "status": "Em andamento", "created_at": "2024-01-15T09:30:00Z"}
            ]
            return ResponseFormatter.format_success_response(data=mock_tickets[:limit], message="Novos tickets mockados")
    except Exception as e:
        logger.error(f"Erro ao buscar tickets: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

