import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Literal, List, Dict, Any
from .telemetry import init_sentry, init_otel
from .flags import Flags

# Importar modelos consolidados
from models.validation import (
    TechnicianRanking, Ticket, SystemStatus, 
    LevelMetrics, MetricsData
)

init_sentry(
    dsn=os.getenv("SENTRY_DSN"),
    environment=os.getenv("ENVIRONMENT", "dev"),
    release=os.getenv("RELEASE", "local"),
)
init_otel(
    service_name=os.getenv("OTEL_SERVICE_NAME", "gadpi-api"),
    otlp_endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318"),
)

app = FastAPI(title="GADPI API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
flags = Flags()

# Modelo específico para KPIs (não duplicado)
from pydantic import BaseModel, Field

class KPI(BaseModel):
    level: Literal["N1", "N2", "N3", "N4"]
    total: int = Field(ge=0)
    open: int = Field(ge=0)
    in_progress: int = Field(ge=0)
    closed: int = Field(ge=0)

class Metrics(BaseModel):
    total_tickets: int
    resolved_tickets: int
    avg_resolution_time: str
    customer_satisfaction: float

@app.get("/v1/kpis", response_model=List[KPI], tags=["kpis"])
def get_kpis():
    return [
        {"level": "N1", "total": 20, "open": 5, "in_progress": 10, "closed": 5},
        {"level": "N2", "total": 12, "open": 2, "in_progress": 7, "closed": 3},
        {"level": "N3", "total": 7, "open": 1, "in_progress": 3, "closed": 3},
        {"level": "N4", "total": 3, "open": 0, "in_progress": 1, "closed": 2},
    ]

@app.get("/v1/system/status", response_model=SystemStatus, tags=["system"])
def get_system_status():
    return {
        "status": "operational",
        "uptime": "99.9%",
        "version": "1.1.0"
    }

@app.get("/v1/technicians/ranking", response_model=List[TechnicianRanking], tags=["technicians"])
def get_technicians_ranking():
    return [
        {"name": "João Silva", "tickets_resolved": 45, "avg_resolution_time": "2h 30m", "satisfaction_score": 4.8},
        {"name": "Maria Santos", "tickets_resolved": 38, "avg_resolution_time": "3h 15m", "satisfaction_score": 4.6},
        {"name": "Pedro Costa", "tickets_resolved": 32, "avg_resolution_time": "2h 45m", "satisfaction_score": 4.7}
    ]

@app.get("/v1/tickets", response_model=List[Ticket], tags=["tickets"])
def get_tickets():
    return [
        {"id": 1, "title": "Problema de conectividade", "status": "open", "priority": "high", "created_at": "2024-01-15T10:30:00Z", "assigned_to": "João Silva"},
        {"id": 2, "title": "Erro no sistema", "status": "in_progress", "priority": "medium", "created_at": "2024-01-15T09:15:00Z", "assigned_to": "Maria Santos"}
    ]

@app.get("/v1/metrics", response_model=Metrics, tags=["metrics"])
def get_metrics():
    return {
        "total_tickets": 150,
        "resolved_tickets": 120,
        "avg_resolution_time": "2h 45m",
        "customer_satisfaction": 4.7
    }

@app.get("/v2/kpis", response_model=List[KPI], tags=["kpis"])
def get_kpis_v2():
    if not flags.is_enabled("use_v2_kpis"):
        raise HTTPException(status_code=501, detail="v2 desabilitado por flag")
    return [
        {"level": "N1", "total": 21, "open": 6, "in_progress": 10, "closed": 5},
        {"level": "N2", "total": 13, "open": 3, "in_progress": 7, "closed": 3},
        {"level": "N3", "total": 7, "open": 1, "in_progress": 3, "closed": 3},
        {"level": "N4", "total": 3, "open": 0, "in_progress": 1, "closed": 2},
    ]
