import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal, List
from .telemetry import init_sentry, init_otel
from .flags import Flags

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
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
flags = Flags()


class KPI(BaseModel):
    level: Literal["N1", "N2", "N3", "N4"]
    total: int = Field(ge=0)
    open: int = Field(ge=0)
    in_progress: int = Field(ge=0)
    closed: int = Field(ge=0)


@app.get("/v1/kpis", response_model=List[KPI], tags=["kpis"])
def get_kpis():
    return [
        {"level": "N1", "total": 20, "open": 5, "in_progress": 10, "closed": 5},
        {"level": "N2", "total": 12, "open": 2, "in_progress": 7, "closed": 3},
        {"level": "N3", "total": 7, "open": 1, "in_progress": 3, "closed": 3},
        {"level": "N4", "total": 3, "open": 0, "in_progress": 1, "closed": 2},
    ]


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
