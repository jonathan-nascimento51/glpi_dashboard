#!/usr/bin/env python3
"""
Script de validação do dashboard GLPI - Versão corrigida
Verifica se os serviços estão funcionando e os dados fazem sentido.
"""

import json
import requests
import time
from datetime import datetime
from pathlib import Path

# Configurações
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"
ARTIFACTS_DIR = Path("artifacts")

# Endpoints críticos para validar
CRITICAL_ENDPOINTS = {
    "/api/metrics": "Métricas gerais",
    "/api/metrics/simple": "Métricas por níveis N1-N4", 
    "/api/technicians/ranking": "Ranking de técnicos",
    "/api/alerts": "Alertas do sistema"
}

def check_service_health():
    """Verifica se os serviços estão rodando"""
    backend_ok = False
    frontend_ok = False
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        backend_ok = response.status_code == 200
        print("Backend esta saudavel" if backend_ok else "Backend com problemas")
    except Exception as e:
        print(f"Backend inacessivel: {e}")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        frontend_ok = response.status_code == 200
        print("Frontend esta acessivel" if frontend_ok else "Frontend com problemas")
    except Exception as e:
        print(f"Frontend inacessivel: {e}")
    
    return backend_ok, frontend_ok

def validate_data_consistency(data):
    """Valida se os dados fazem sentido"""
    issues = []

    # Verifica se o summary tem dados
    summary = data.get("/api/metrics")
    if summary:
        total_tickets = summary.get("data", {}).get("total", 0)
        if total_tickets == 0:
            issues.append("Total de tickets é zero")
        else:
            print(f"\nTotal de tickets (geral): {total_tickets}")
    else:
        issues.append("Dados de summary nao disponiveis")

    # Verifica dados por níveis N1-N4
    by_status = data.get("/api/metrics/simple")
    if by_status and by_status.get("data"):
        simple_data = by_status.get("data", {})
        total_by_status = simple_data.get("total", 0)
        print(f"Total por níveis N1-N4: {total_by_status}")
        
        # Nota: /api/metrics (geral) e /api/metrics/simple (N1-N4) são conjuntos diferentes
        # É normal ter totais diferentes - não é inconsistência
        if total_by_status == 0:
            issues.append("Total por níveis N1-N4 é zero")
    else:
        issues.append("Dados por status nao disponiveis")

    return issues

print("Script de validação corrigido criado!")
