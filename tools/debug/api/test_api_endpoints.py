#!/usr/bin/env python3
"""
Script para testar endpoints da API do GLPI Dashboard
Uso: python test_api_endpoints.py [--host HOST] [--port PORT]
"""

import requests
import json
import argparse
import sys
from datetime import datetime, timedelta

def test_endpoint(url, description, expected_status=200):
    """Testa um endpoint específico"""
    print(f"\n🔍 Testando: {description}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == expected_status:
            print("✅ Sucesso")
            if response.headers.get('content-type', '').startswith('application/json'):
                data = response.json()
                print(f"Dados retornados: {len(str(data))} caracteres")
                if isinstance(data, dict):
                    print(f"Chaves principais: {list(data.keys())[:5]}")
            return True
        else:
            print(f"❌ Falha - Status esperado: {expected_status}")
            print(f"Resposta: {response.text[:200]}...")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao decodificar JSON: {e}")
        return False

def test_api_health(base_url):
    """Testa a saúde geral da API"""
    endpoints = [
        ("/api/health", "Health Check"),
        ("/api/dashboard/metrics", "Dashboard Metrics"),
        ("/api/technicians/ranking", "Technician Ranking"),
        ("/api/system/status", "System Status"),
        ("/api/tickets/new", "New Tickets")
    ]
    
    results = []
    for endpoint, description in endpoints:
        url = f"{base_url}{endpoint}"
        success = test_endpoint(url, description)
        results.append((endpoint, success))
    
    return results

def test_ranking_with_filters(base_url):
    """Testa o endpoint de ranking com diferentes filtros"""
    print("\n🎯 Testando Ranking com Filtros")
    
    # Data de hoje e 30 dias atrás
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    test_cases = [
        (f"/api/technicians/ranking?limit=10", "Ranking com limite"),
        (f"/api/technicians/ranking?level=N1", "Ranking nível N1"),
        (f"/api/technicians/ranking?start_date={start_date}&end_date={end_date}", "Ranking com filtro de data"),
        (f"/api/technicians/ranking?start_date={start_date}&end_date={end_date}&level=N2&limit=5", "Ranking completo")
    ]
    
    results = []
    for endpoint, description in test_cases:
        url = f"{base_url}{endpoint}"
        success = test_endpoint(url, description)
        results.append((endpoint, success))
    
    return results

def test_cors_headers(base_url):
    """Testa se os headers CORS estão configurados corretamente"""
    print("\n🌐 Testando Headers CORS")
    
    url = f"{base_url}/api/technicians/ranking"
    headers = {
        'Origin': 'http://localhost:3002',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        
        print("Headers CORS encontrados:")
        for header, value in cors_headers.items():
            status = "✅" if value else "❌"
            print(f"  {status} {header}: {value}")
        
        return all(cors_headers.values())
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao testar CORS: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Testa endpoints da API do GLPI Dashboard')
    parser.add_argument('--host', default='localhost', help='Host da API (default: localhost)')
    parser.add_argument('--port', default='5000', help='Porta da API (default: 5000)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Saída verbosa')
    
    args = parser.parse_args()
    base_url = f"http://{args.host}:{args.port}"
    
    print(f"🚀 Testando API em: {base_url}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Testa endpoints básicos
    basic_results = test_api_health(base_url)
    
    # Testa ranking com filtros
    ranking_results = test_ranking_with_filters(base_url)
    
    # Testa CORS
    cors_ok = test_cors_headers(base_url)
    
    # Resumo dos resultados
    print("\n📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    print("\nEndpoints Básicos:")
    for endpoint, success in basic_results:
        status = "✅" if success else "❌"
        print(f"  {status} {endpoint}")
    
    print("\nRanking com Filtros:")
    for endpoint, success in ranking_results:
        status = "✅" if success else "❌"
        print(f"  {status} {endpoint}")
    
    print(f"\nCORS: {'✅' if cors_ok else '❌'}")
    
    # Estatísticas finais
    total_tests = len(basic_results) + len(ranking_results) + 1
    passed_tests = sum(1 for _, success in basic_results + ranking_results if success) + (1 if cors_ok else 0)
    
    print(f"\n🎯 Resultado Final: {passed_tests}/{total_tests} testes passaram")
    
    if passed_tests == total_tests:
        print("🎉 Todos os testes passaram! API está funcionando corretamente.")
        sys.exit(0)
    else:
        print("⚠️  Alguns testes falharam. Verifique os logs acima.")
        sys.exit(1)

if __name__ == "__main__":
    main()