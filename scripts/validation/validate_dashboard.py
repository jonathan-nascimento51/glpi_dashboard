#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de validacao do Dashboard GLPI
Verifica se os servicos estao funcionando e os dados estao sendo renderizados corretamente.
"""

import requests
import json
import time
import os
from datetime import datetime
from pathlib import Path

# Configuracoes
BACKEND_URL = "http://localhost:5000"
FRONTEND_URL = "http://localhost:5173"
ARTIFACTS_DIR = Path("artifacts")

def setup_artifacts_dir():
    """Cria o diretorio de artefatos se nao existir"""
    ARTIFACTS_DIR.mkdir(exist_ok=True)
    print(f"Diretorio de artefatos: {ARTIFACTS_DIR.absolute()}")

def check_backend_health():
    """Verifica se o backend esta respondendo"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print("Backend esta saudavel")
            return True
        else:
            print(f"Backend respondeu com status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Backend nao esta respondendo: {e}")
        return False

def check_frontend_health():
    """Verifica se o frontend esta respondendo"""
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("Frontend esta acessivel")
            return True
        else:
            print(f"Frontend respondeu com status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Frontend nao esta respondendo: {e}")
        return False

def fetch_critical_data():
    """Busca dados criticos da API"""
    endpoints = [
        "/api/metrics",
        "/api/metrics/simple",
        "/api/technicians/ranking",
        "/api/alerts"
    ]
    
    data = {}
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=10)
            if response.status_code == 200:
                data[endpoint] = response.json()
                print(f"Dados obtidos de {endpoint}")
            else:
                print(f"Erro ao buscar {endpoint}: status {response.status_code}")
                data[endpoint] = None
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar {endpoint}: {e}")
            data[endpoint] = None
    
    return data

def save_data_artifacts(data):
    """Salva os dados em arquivos JSON"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for endpoint, endpoint_data in data.items():
        if endpoint_data is not None:
            filename = f"data_{endpoint.replace('/', '_').replace('-', '_')}_{timestamp}.json"
            filepath = ARTIFACTS_DIR / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(endpoint_data, f, indent=2, ensure_ascii=False)
            
            print(f"Dados salvos em {filepath}")

def validate_data_consistency(data):
    """Valida se os dados fazem sentido"""
    issues = []
    
    # Verifica se o summary tem dados
    summary = data.get("/api/metrics")
    if summary:
        total_tickets = summary.get("data", {}).get("total", 0)
        if total_tickets == 0:
            issues.append("Total de tickets e zero")
        else:
            print(f"Total de tickets: {total_tickets}")
    else:
        issues.append("Dados de summary nao disponiveis")
    
    # Verifica dados por status
    by_status = data.get("/api/metrics/simple")
    if by_status and by_status.get("data"):
        simple_data = by_status.get("data", {}); total_by_status = simple_data.get("total", 0)
        print(f"Total por status (simple): {total_by_status}")
        
        if summary and total_tickets != total_by_status:
            issues.append(f"Inconsistencia: summary={total_tickets}, por_status={total_by_status}")
    else:
        issues.append("Dados por status nao disponiveis")
    
    return issues

def generate_validation_report(backend_ok, frontend_ok, data, issues):
    """Gera relatorio final de validacao"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = {
        "timestamp": timestamp,
        "services": {
            "backend": backend_ok,
            "frontend": frontend_ok
        },
        "data_availability": {
            endpoint: data is not None 
            for endpoint, data in data.items()
        },
        "issues": issues,
        "status": "PASS" if backend_ok and frontend_ok and not issues else "FAIL"
    }
    
    # Salva relatorio
    report_file = ARTIFACTS_DIR / f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"Relatorio salvo em {report_file}")
    
    # Exibe resumo
    print("\n" + "="*50)
    print("RESUMO DA VALIDACAO")
    print("="*50)
    print(f"Timestamp: {timestamp}")
    print(f"Backend: {'OK' if backend_ok else 'FALHA'}")
    print(f"Frontend: {'OK' if frontend_ok else 'FALHA'}")
    
    if issues:
        print("\nPROBLEMAS ENCONTRADOS:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\nNenhum problema encontrado")
    
    print(f"\nStatus Final: {report['status']}")
    print("="*50)
    
    return report

def main():
    """Funcao principal"""
    print("Iniciando validacao do dashboard GLPI...\n")
    
    # Setup
    setup_artifacts_dir()
    
    # Verificacoes de saude
    print("Verificando saude dos servicos...")
    backend_ok = check_backend_health()
    frontend_ok = check_frontend_health()
    
    # Se backend nao estiver OK, nao continua
    if not backend_ok:
        print("\nBackend nao esta funcionando. Abortando validacao.")
        return
    
    # Busca dados
    print("\nBuscando dados criticos...")
    data = fetch_critical_data()
    
    # Salva artefatos
    print("\nSalvando artefatos...")
    save_data_artifacts(data)
    
    # Valida consistencia
    print("\nValidando consistencia dos dados...")
    issues = validate_data_consistency(data)
    
    # Gera relatorio
    report = generate_validation_report(backend_ok, frontend_ok, data, issues)
    
    # Retorna codigo de saida apropriado
    exit_code = 0 if report["status"] == "PASS" else 1
    exit(exit_code)

if __name__ == "__main__":
    main()
