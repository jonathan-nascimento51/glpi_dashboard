# -*- coding: utf-8 -*-
"""FastAPI application com sistema de observabilidade integrado"""

import os
from typing import List, Literal
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

# Importar sistema de observabilidade
from observability import (
    setup_observability,
    get_logger,
    get_metrics,
    get_metrics_summary,
    APIError,
    BusinessError,
    ExternalServiceError
)

# Configurar telemetria (mantendo compatibilidade)
try:
    from utils.telemetry import setup_telemetry
    setup_telemetry(
        service_name="gadpi-api",
        service_version="1.1.0",
        otlp_endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318"),
    )
except ImportError:
    pass

# Importar flags (mantendo compatibilidade)
try:
    from utils.flags import Flags
    flags = Flags()
except ImportError:
    class MockFlags:
        def is_enabled(self, flag: str) -> bool:
            return os.getenv(f"FLAG_{flag.upper()}", "false").lower() == "true"
    flags = MockFlags()

# Criar aplicação FastAPI
app = FastAPI(
    title="GADPI API",
    version="1.1.0",
    description="API para dashboard GLPI com observabilidade integrada"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar sistema de observabilidade
setup_observability(
    app,
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    enable_json_logs=os.getenv("JSON_LOGS", "true").lower() == "true"
)

# Obter logger
logger = get_logger(__name__)

# Modelos Pydantic
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

class HealthCheck(BaseModel):
    status: str
    version: str
    timestamp: str
    request_id: str

# Endpoints de saúde e métricas
@app.get("/health", response_model=HealthCheck, tags=["health"])
def health_check():
    """Endpoint de health check"""
    from datetime import datetime
    from observability.logger import request_id_var
    
    logger.info("Health check requested")
    
    return {
        "status": "healthy",
        "version": "1.1.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "request_id": request_id_var.get() or "unknown"
    }

@app.get("/metrics", response_class=PlainTextResponse, tags=["metrics"])
def prometheus_metrics():
    """Endpoint para métricas Prometheus"""
    return get_metrics()

@app.get("/metrics/summary", tags=["metrics"])
def metrics_summary():
    """Endpoint para resumo das métricas em JSON"""
    return get_metrics_summary()

# Endpoints de negócio
@app.get("/v1/kpis", response_model=List[KPI], tags=["kpis"])
def get_kpis():
    """Obtém KPIs por nível (v1)"""
    logger.business_event(
        "kpis_requested",
        version="v1",
        endpoint="/v1/kpis"
    )
    
    try:
        # Simular dados (em produção, viria do GLPI)
        kpis = [
            {"level": "N1", "total": 25, "open": 8, "in_progress": 12, "closed": 5},
            {"level": "N2", "total": 15, "open": 4, "in_progress": 8, "closed": 3},
            {"level": "N3", "total": 8, "open": 2, "in_progress": 4, "closed": 2},
            {"level": "N4", "total": 4, "open": 1, "in_progress": 2, "closed": 1},
        ]
        
        logger.info(
            "KPIs retrieved successfully",
            total_levels=len(kpis),
            total_tickets=sum(kpi["total"] for kpi in kpis)
        )
        
        return kpis
        
    except Exception as e:
        logger.error(f"Failed to retrieve KPIs: {str(e)}", exc_info=True)
        raise APIError(
            message="Failed to retrieve KPIs",
            status_code=500,
            error_code="KPI_RETRIEVAL_ERROR",
            details={"error": str(e)}
        )

@app.get("/v1/metrics", response_model=Metrics, tags=["metrics"])
def get_business_metrics():
    """Obtém métricas de negócio"""
    logger.business_event(
        "business_metrics_requested",
        endpoint="/v1/metrics"
    )
    
    try:
        # Simular dados (em produção, viria do GLPI)
        metrics = {
            "total_tickets": 150,
            "resolved_tickets": 120,
            "avg_resolution_time": "2h 45m",
            "customer_satisfaction": 4.7
        }
        
        logger.info(
            "Business metrics retrieved successfully",
            **metrics
        )
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to retrieve business metrics: {str(e)}", exc_info=True)
        raise APIError(
            message="Failed to retrieve business metrics",
            status_code=500,
            error_code="METRICS_RETRIEVAL_ERROR",
            details={"error": str(e)}
        )

@app.get("/v2/kpis", response_model=List[KPI], tags=["kpis"])
def get_kpis_v2():
    """Obtém KPIs por nível (v2) - controlado por feature flag"""
    logger.business_event(
        "kpis_requested",
        version="v2",
        endpoint="/v2/kpis"
    )
    
    # Verificar feature flag
    if not flags.is_enabled("use_v2_kpis"):
        logger.warning(
            "v2 KPIs endpoint disabled by feature flag",
            flag="use_v2_kpis"
        )
        raise BusinessError(
            message="v2 KPIs endpoint is currently disabled",
            details={"flag": "use_v2_kpis", "enabled": False}
        )
    
    try:
        # Simular dados v2 (em produção, viria do GLPI)
        kpis = [
            {"level": "N1", "total": 21, "open": 6, "in_progress": 10, "closed": 5},
            {"level": "N2", "total": 13, "open": 3, "in_progress": 7, "closed": 3},
            {"level": "N3", "total": 7, "open": 1, "in_progress": 3, "closed": 3},
            {"level": "N4", "total": 3, "open": 0, "in_progress": 1, "closed": 2},
        ]
        
        logger.info(
            "v2 KPIs retrieved successfully",
            total_levels=len(kpis),
            total_tickets=sum(kpi["total"] for kpi in kpis)
        )
        
        return kpis
        
    except Exception as e:
        logger.error(f"Failed to retrieve v2 KPIs: {str(e)}", exc_info=True)
        raise APIError(
            message="Failed to retrieve v2 KPIs",
            status_code=500,
            error_code="KPI_V2_RETRIEVAL_ERROR",
            details={"error": str(e)}
        )

# Endpoint raiz
@app.get("/", tags=["root"])
def read_root():
    """Endpoint raiz da API"""
    logger.info("Root endpoint accessed")
    return {
        "message": "GADPI API",
        "version": "1.1.0",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }

# Exemplo de endpoint que simula erro de serviço externo
@app.get("/test/external-error", tags=["test"])
def test_external_error():
    """Endpoint para testar erro de serviço externo"""
    logger.warning("Testing external service error")
    raise ExternalServiceError(
        service="GLPI",
        message="Connection timeout",
        status_code=502,
        details={"timeout": "30s", "endpoint": "/apirest.php"}
    )

# Exemplo de endpoint que simula erro de validação
@app.get("/test/validation-error", tags=["test"])
def test_validation_error():
    """Endpoint para testar erro de validação"""
    logger.warning("Testing validation error")
    from observability.exceptions import ValidationError
    raise ValidationError(
        field="level",
        message="deve ser um dos valores: N1, N2, N3, N4",
        value="N5"
    )

if __name__ == "__main__":
    import uvicorn
    
    logger.info(
        "Starting GADPI API server",
        host="0.0.0.0",
        port=8000,
        log_level=os.getenv("LOG_LEVEL", "INFO").lower()
    )
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level=os.getenv("LOG_LEVEL", "INFO").lower(),
        reload=os.getenv("RELOAD", "false").lower() == "true"
    )
