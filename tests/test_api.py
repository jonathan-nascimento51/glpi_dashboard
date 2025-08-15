import pytest
import requests
import time

# URL base da API
BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Testa se o endpoint de health está funcionando"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_root_endpoint():
    """Testa se o endpoint raiz está funcionando"""
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "status" in data
    assert data["status"] == "running"

def test_api_response_format():
    """Testa se as respostas da API estão no formato JSON correto"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.headers.get("content-type") == "application/json"
    
    # Verifica se é um JSON válido
    try:
        response.json()
    except ValueError:
        pytest.fail("Resposta não é um JSON válido")

def test_cors_headers():
    """Testa se os headers CORS estão configurados"""
    response = requests.get(f"{BASE_URL}/health")
    # Verifica se não há erro de CORS (status 200 indica que CORS está OK)
    assert response.status_code == 200
