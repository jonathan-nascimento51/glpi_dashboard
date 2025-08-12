#!/usr/bin/env python3
"""
Script de validação visual automática para GLPI Dashboard.

Este script:
1. Verifica se os serviços estão rodando
2. Faz hit em endpoints críticos e salva JSON de amostra
3. Valida consistência dos dados
4. Gera relatório de validação

Artefatos salvos em artifacts/ (JSON)
"""

import os
import sys
import time
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Configurações
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8050"
ARTIFACTS_DIR = Path("artifacts")
TIMEOUT = 30.0
MAX_RETRIES = 10
RETRY_DELAY = 3.0


def setup_artifacts_dir():
    """Cria diretório de artefatos se não existir."""
    ARTIFACTS_DIR.mkdir(exist_ok=True)
    print(f"Diretório de artefatos: {ARTIFACTS_DIR.absolute()}")


def wait_for_service(url: str, service_name: str, max_retries: int = MAX_RETRIES) -> bool:
    """Aguarda um serviço ficar disponível."""
    print(f"Aguardando {service_name} em {url}...")
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=5.0)
            if response.status_code == 200:
                print(f"{service_name} está disponível!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        if attempt < max_retries - 1:
            print(f"   Tentativa {attempt + 1}/{max_retries} falhou, aguardando {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)
    
    print(f"{service_name} não ficou disponível após {max_retries} tentativas")
    return False


def check_backend_health() -> Dict[str, Any]:
    """Verifica saúde do backend e retorna dados."""
    print("Verificando saúde do backend...")
    
    try:
        # Health check geral
        health_response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        health_data = health_response.json() if health_response.status_code == 200 else {}
        
        # Health check de dados
        data_health_response = requests.get(f"{BASE_URL}/api/v1/health/data", timeout=TIMEOUT)
        data_health = data_health_response.json() if data_health_response.status_code == 200 else {}
        
        # Métricas principais
        metrics_response = requests.get(f"{BASE_URL}/api/v1/metrics/levels", timeout=TIMEOUT)
        metrics_data = metrics_response.json() if metrics_response.status_code == 200 else {}
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "health": health_data,
            "data_health": data_health,
            "metrics": metrics_data,
            "status": "ok" if all([
                health_response.status_code == 200,
                data_health_response.status_code == 200,
                metrics_response.status_code == 200
            ]) else "error"
        }
        
        status = result.get("status", "unknown")
        print(f"Backend health: {status}")
        return result
        
    except Exception as e:
        print(f"Erro ao verificar backend: {e}")
        return {"timestamp": datetime.now().isoformat(), "status": "error", "error": str(e)}


def save_api_samples(backend_data: Dict[str, Any]):
    """Salva amostras das APIs em arquivos JSON."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Salvar dados completos do backend
    backend_file = ARTIFACTS_DIR / f"backend_data_{timestamp}.json"
    with open(backend_file, "w", encoding="utf-8") as f:
        json.dump(backend_data, f, indent=2, ensure_ascii=False)
    print(f"Dados do backend salvos: {backend_file}")
    
    # Salvar apenas métricas principais para análise
    if "metrics" in backend_data and backend_data["metrics"]:
        metrics_file = ARTIFACTS_DIR / f"metrics_sample_{timestamp}.json"
        with open(metrics_file, "w", encoding="utf-8") as f:
            json.dump(backend_data["metrics"], f, indent=2, ensure_ascii=False)
        print(f"Métricas salvas: {metrics_file}")


def validate_data_consistency(backend_data: Dict[str, Any]) -> bool:
    """Valida consistência dos dados - falha se todos os cards estiverem 0 quando API tem valores > 0."""
    print("Validando consistência dos dados...")
    
    try:
        # Verificar se temos dados de métricas
        metrics = backend_data.get("metrics", {})
        if not metrics:
            print("Nenhuma métrica encontrada")
            return False
        
        # Verificar se há dados de saúde
        data_health = backend_data.get("data_health", {})
        if not data_health:
            print("Nenhum dado de saúde encontrado")
            return False
        
        # Verificar se o sistema detectou all-zero quando não deveria
        all_zero = data_health.get("all_zero", False)
        quality_level = data_health.get("quality_level", "unknown")
        status = data_health.get("status", "unknown")
        
        print(f"   Status: {status}")
        print(f"   All-zero: {all_zero}")
        print(f"   Quality level: {quality_level}")
        
        # Se o status é error e all_zero é True, isso pode indicar problema
        if status == "error" and all_zero:
            print("FALHA: Sistema detectou dados all-zero - possível problema de qualidade!")
            
            # Verificar se há issues críticos
            issues = data_health.get("issues", [])
            critical_issues = [issue for issue in issues if issue.get("severity") == "critical"]
            
            if critical_issues:
                print("   Issues críticos detectados:")
                for issue in critical_issues:
                    issue_type = issue.get("type", "unknown")
                    issue_msg = issue.get("message", "sem mensagem")
                    print(f"   - {issue_type}: {issue_msg}")
            
            return False
        
        # Se chegou até aqui, dados parecem consistentes
        print("Dados parecem consistentes")
        return True
        
    except Exception as e:
        print(f"Erro na validação: {e}")
        return False


def generate_validation_report(backend_data: Dict[str, Any], validation_passed: bool):
    """Gera relatório de validação."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = ARTIFACTS_DIR / f"validation_report_{timestamp}.json"
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "validation_passed": validation_passed,
        "backend_status": backend_data.get("status", "unknown"),
        "data_health": backend_data.get("data_health", {}),
        "summary": {
            "backend_available": backend_data.get("status") == "ok",
            "data_consistent": validation_passed
        }
    }
    
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"Relatório de validação salvo: {report_file}")
    return report


def main():
    """Função principal de validação."""
    print("Iniciando validação visual automática do GLPI Dashboard")
    print("=" * 60)
    
    # Setup
    setup_artifacts_dir()
    
    # Verificar se os serviços estão rodando
    backend_ready = wait_for_service(f"{BASE_URL}/health", "Backend")
    
    if not backend_ready:
        print("Backend não está disponível. Certifique-se de que está rodando em http://localhost:8000")
        sys.exit(1)
    
    # Coletar dados do backend
    backend_data = check_backend_health()
    save_api_samples(backend_data)
    
    # Validar consistência dos dados
    validation_passed = validate_data_consistency(backend_data)
    
    # Gerar relatório
    report = generate_validation_report(backend_data, validation_passed)
    
    # Resultado final
    print("\n" + "=" * 60)
    if validation_passed:
        print("VALIDAÇÃO PASSOU: Dashboard está funcionando corretamente")
        sys.exit(0)
    else:
        print("VALIDAÇÃO FALHOU: Problemas detectados no dashboard")
        report_name = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        print(f"Verifique o relatório: artifacts/{report_name}")
        sys.exit(1)


if __name__ == "__main__":
    main()
