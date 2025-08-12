"""Testes E2E anti-zero para validação de qualidade de dados.

Este módulo implementa testes end-to-end que verificam:
- Falha quando all-zero=true
- Comportamento correto com dados válidos
- Integração completa do sistema de qualidade de dados
"""

import requests
import pytest
from typing import Dict, Any


# Configuração base
BASE_URL = "http://localhost:8000"
TIMEOUT = 30.0


def test_health_data_endpoint_exists():
    """Testa se o endpoint /api/v1/health/data existe e responde."""
    response = requests.get(f"{BASE_URL}/api/v1/health/data", timeout=TIMEOUT)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "quality_level" in data
    assert "timestamp" in data


def test_health_data_with_valid_data():
    """Testa endpoint com dados válidos (all_zero=false)."""
    response = requests.get(f"{BASE_URL}/api/v1/health/data?all_zero=false", timeout=TIMEOUT)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "ok"
    assert data["all_zero"] is False
    assert data["quality_level"] in ["excellent", "good", "warning"]
    assert isinstance(data["metrics"], dict)
    
    # Verificar estrutura real das métricas
    metrics = data["metrics"]
    assert "numeric_fields" in metrics
    assert "total_fields" in metrics
    assert "numeric_summary" in metrics
    assert metrics["numeric_fields"] > 0


def test_health_data_fails_with_all_zero():
    """Testa que o endpoint falha quando all_zero=true.
    
    Este é o teste crítico que deve falhar quando todos os dados são zero,
    indicando um problema de qualidade de dados.
    """
    response = requests.get(f"{BASE_URL}/api/v1/health/data?all_zero=true", timeout=TIMEOUT)
    assert response.status_code == 200
    
    data = response.json()
    # O status deve ser "error" quando todos os dados são zero
    assert data["status"] == "error"
    assert data["all_zero"] is True
    assert data["quality_level"] in ["critical", "failed"]
    assert data["critical_issues"] is True
    assert data["issues_count"] > 0
    
    # Verificar que as métricas indicam dados zerados
    metrics = data["metrics"]
    numeric_summary = metrics["numeric_summary"]
    assert numeric_summary["min"] == 0.0
    assert numeric_summary["max"] == 0.0
    assert numeric_summary["mean"] == 0.0
    assert metrics["critical_issues"] > 0


def test_health_data_detects_anomalies():
    """Testa detecção de anomalias nos dados."""
    response = requests.get(f"{BASE_URL}/api/v1/health/data", timeout=TIMEOUT)
    assert response.status_code == 200
    
    data = response.json()
    assert "anomalies" in data
    assert isinstance(data["anomalies"], bool)


def test_health_data_response_structure():
    """Testa estrutura completa da resposta do endpoint."""
    response = requests.get(f"{BASE_URL}/api/v1/health/data", timeout=TIMEOUT)
    assert response.status_code == 200
    
    data = response.json()
    required_fields = [
        "status",
        "quality_level",
        "all_zero",
        "anomalies",
        "issues_count",
        "critical_issues",
        "timestamp",
        "metrics",
        "issues"
    ]
    
    for field in required_fields:
        assert field in data, f"Campo obrigatório '{field}' não encontrado na resposta"
    
    # Verificar estrutura das métricas
    metrics = data["metrics"]
    metrics_required_fields = [
        "total_fields",
        "numeric_fields",
        "total_issues",
        "critical_issues",
        "warning_issues",
        "data_completeness",
        "numeric_summary"
    ]
    
    for field in metrics_required_fields:
        assert field in metrics, f"Campo obrigatório '{field}' não encontrado em metrics"


def test_integration_with_metrics_endpoint():
    """Testa integração com endpoint de métricas principais."""
    # Primeiro, buscar métricas normais
    metrics_response = requests.get(f"{BASE_URL}/api/v1/metrics/levels", timeout=TIMEOUT)
    assert metrics_response.status_code == 200
    
    # Depois, verificar health dos dados
    health_response = requests.get(f"{BASE_URL}/api/v1/health/data", timeout=TIMEOUT)
    assert health_response.status_code == 200
    
    health_data = health_response.json()
    # Se as métricas estão funcionando, a qualidade deve ser boa
    assert health_data["status"] == "ok"


def test_error_handling():
    """Testa tratamento de erros no endpoint."""
    # Testar com parâmetro inválido
    response = requests.get(f"{BASE_URL}/api/v1/health/data?all_zero=invalid", timeout=TIMEOUT)
    # FastAPI deve converter automaticamente ou retornar erro de validação
    assert response.status_code in [200, 422]


def test_anti_zero_validation_critical():
    """Teste crítico: validação anti-zero deve falhar com dados all-zero.
    
    Este teste é o coração da validação E2E anti-zero.
    Deve falhar quando o sistema retorna todos os dados como zero.
    """
    # Forçar cenário all-zero
    response = requests.get(f"{BASE_URL}/api/v1/health/data?all_zero=true", timeout=TIMEOUT)
    assert response.status_code == 200
    
    data = response.json()
    
    # Validações críticas para anti-zero
    assert data["status"] == "error", "Sistema deve reportar erro quando todos os dados são zero"
    assert data["all_zero"] is True, "Flag all_zero deve ser True"
    assert data["quality_level"] in ["critical", "failed"], "Qualidade deve ser crítica/falha"
    assert data["critical_issues"] is True, "Deve haver issues críticos"
    assert data["issues_count"] > 0, "Deve haver pelo menos um issue reportado"
    
    # Verificar que o sistema detectou o problema all-zero
    issues = data.get("issues", [])
    all_zero_detected = any(
        issue.get("type") == "all_zero" and issue.get("severity") == "critical"
        for issue in issues
    )
    assert all_zero_detected, "Sistema deve detectar e reportar problema all-zero como crítico"
    
    # Verificar que as métricas numéricas estão todas zeradas
    metrics = data["metrics"]
    numeric_summary = metrics["numeric_summary"]
    assert numeric_summary["min"] == 0.0, "Valor mínimo deve ser 0"
    assert numeric_summary["max"] == 0.0, "Valor máximo deve ser 0"
    assert numeric_summary["mean"] == 0.0, "Média deve ser 0"


def test_quality_levels_progression():
    """Testa progressão dos níveis de qualidade entre cenários."""
    # Cenário com dados válidos
    valid_response = requests.get(f"{BASE_URL}/api/v1/health/data?all_zero=false", timeout=TIMEOUT)
    assert valid_response.status_code == 200
    valid_data = valid_response.json()
    
    # Cenário com dados zerados
    zero_response = requests.get(f"{BASE_URL}/api/v1/health/data?all_zero=true", timeout=TIMEOUT)
    assert zero_response.status_code == 200
    zero_data = zero_response.json()
    
    # Comparar qualidade
    valid_quality = valid_data["quality_level"]
    zero_quality = zero_data["quality_level"]
    
    # Qualidade com dados válidos deve ser melhor que com dados zerados
    quality_hierarchy = ["failed", "critical", "warning", "good", "excellent"]
    valid_index = quality_hierarchy.index(valid_quality)
    zero_index = quality_hierarchy.index(zero_quality)
    
    assert valid_index > zero_index, f"Qualidade com dados válidos ({valid_quality}) deve ser melhor que com dados zerados ({zero_quality})"


if __name__ == "__main__":
    # Executar testes diretamente
    pytest.main(["-v", __file__])
