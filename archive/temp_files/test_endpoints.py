#!/usr/bin/env python3
"""
Script para testar todos os endpoints principais da API
"""

import requests
import json
from datetime import datetime

def test_endpoint(url, description):
    """Testa um endpoint e retorna o resultado"""
    try:
        response = requests.get(url, timeout=10)
        status = "✅ PASS" if response.status_code == 200 else f"❌ FAIL ({response.status_code})"
        return {
            "endpoint": url,
            "description": description,
            "status_code": response.status_code,
            "status": status,
            "response_size": len(response.content) if response.content else 0
        }
    except requests.exceptions.RequestException as e:
        return {
            "endpoint": url,
            "description": description,
            "status_code": None,
            "status": f"❌ ERROR: {str(e)}",
            "response_size": 0
        }

def main():
    """Executa todos os testes de endpoints"""
    base_url = "http://localhost:5000"
    
    endpoints = [
        ("/api/metrics", "Métricas do dashboard"),
        ("/api/metrics/filtered", "Métricas filtradas"),
        ("/api/technicians/ranking", "Ranking de técnicos"),
        ("/api/tickets/new", "Tickets novos"),
        ("/api/alerts", "Alertas do sistema"),
        ("/api/performance/stats", "Estatísticas de performance"),
        ("/api/status", "Status do sistema"),
    ]
    
    print(f"🧪 Testando endpoints da API - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    results = []
    for endpoint, description in endpoints:
        url = f"{base_url}{endpoint}"
        result = test_endpoint(url, description)
        results.append(result)
        print(f"{result['status']} {description} ({endpoint})")
        if result['status_code'] == 200:
            print(f"    📊 Tamanho da resposta: {result['response_size']} bytes")
    
    print("\n" + "=" * 70)
    
    # Resumo
    passed = sum(1 for r in results if r['status_code'] == 200)
    total = len(results)
    
    print(f"📈 Resumo: {passed}/{total} endpoints funcionando")
    
    if passed == total:
        print("🎉 Todos os endpoints estão funcionando corretamente!")
    else:
        print("⚠️  Alguns endpoints apresentaram problemas.")
        failed = [r for r in results if r['status_code'] != 200]
        print("\n❌ Endpoints com problemas:")
        for result in failed:
            print(f"  - {result['endpoint']}: {result['status']}")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)