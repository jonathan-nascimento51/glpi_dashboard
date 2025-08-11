#!/usr/bin/env python3
"""
Script de teste para validar a integração entre frontend e backend
Testa todos os endpoints da API e verifica se os dados estão sendo retornados corretamente
"""

import requests
import json
import time
from datetime import datetime

API_BASE_URL = 'http://localhost:5000/api'

def test_endpoint(endpoint, description):
    """Testa um endpoint específico"""
    print(f"\n🔍 Testando {description}...")
    print(f"📍 Endpoint: {endpoint}")
    
    try:
        start_time = time.time()
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=30)
        response_time = (time.time() - start_time) * 1000
        
        print(f"⏱️  Tempo de resposta: {response_time:.2f}ms")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso! Dados recebidos.")
            
            # Verificar estrutura básica
            if 'success' in data and data['success']:
                print(f"✅ Campo 'success' = True")
            else:
                print(f"⚠️  Campo 'success' não encontrado ou False")
            
            if 'data' in data:
                print(f"✅ Campo 'data' presente")
                
                # Verificações específicas por endpoint
                if endpoint == '/metrics':
                    validate_metrics_data(data['data'])
                elif endpoint == '/technicians/ranking':
                    validate_technician_ranking_data(data['data'])
                elif endpoint == '/status':
                    validate_status_data(data['data'])
                    
            else:
                print(f"⚠️  Campo 'data' não encontrado")
                
            return True, data
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"📄 Resposta: {response.text[:200]}...")
            return False, None
            
    except requests.exceptions.Timeout:
        print(f"⏰ Timeout na requisição")
        return False, None
    except requests.exceptions.ConnectionError:
        print(f"🔌 Erro de conexão")
        return False, None
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False, None

def validate_metrics_data(data):
    """Valida a estrutura dos dados de métricas"""
    print(f"  🔍 Validando estrutura de métricas...")
    
    # Verificar campos obrigatórios
    required_fields = ['niveis', 'tendencias']
    for field in required_fields:
        if field in data:
            print(f"  ✅ Campo '{field}' presente")
        else:
            print(f"  ❌ Campo '{field}' ausente")
    
    # Verificar estrutura dos níveis
    if 'niveis' in data:
        niveis = data['niveis']
        expected_levels = ['n1', 'n2', 'n3', 'n4']
        
        for level in expected_levels:
            if level in niveis:
                level_data = niveis[level]
                metrics = ['novos', 'pendentes', 'progresso', 'resolvidos']
                
                print(f"  📊 Nível {level}:")
                for metric in metrics:
                    if metric in level_data:
                        value = level_data[metric]
                        print(f"    ✅ {metric}: {value}")
                    else:
                        print(f"    ❌ {metric}: ausente")
            else:
                print(f"  ❌ Nível '{level}' ausente")
    
    # Verificar tendências
    if 'tendencias' in data:
        tendencias = data['tendencias']
        print(f"  📈 Tendências: {tendencias}")

def validate_technician_ranking_data(data):
    """Valida a estrutura dos dados de ranking de técnicos"""
    print(f"  🔍 Validando ranking de técnicos...")
    
    if isinstance(data, list):
        print(f"  ✅ Dados em formato de lista")
        print(f"  📊 Total de técnicos: {len(data)}")
        
        if len(data) > 0:
            first_tech = data[0]
            required_fields = ['id', 'name', 'score', 'total_tickets']
            
            print(f"  🔍 Validando primeiro técnico:")
            for field in required_fields:
                if field in first_tech:
                    print(f"    ✅ {field}: {first_tech[field]}")
                else:
                    print(f"    ❌ {field}: ausente")
    else:
        print(f"  ❌ Dados não estão em formato de lista")

def validate_status_data(data):
    """Valida a estrutura dos dados de status"""
    print(f"  🔍 Validando status do sistema...")
    
    required_fields = ['api', 'glpi', 'glpi_message', 'version']
    for field in required_fields:
        if field in data:
            print(f"  ✅ {field}: {data[field]}")
        else:
            print(f"  ❌ {field}: ausente")

def test_metrics_with_filters():
    """Testa métricas com filtros de data"""
    print(f"\n🔍 Testando métricas com filtros de data...")
    
    # Teste com filtro de data
    params = {
        'start_date': '2024-01-01',
        'end_date': '2024-12-31'
    }
    
    try:
        response = requests.get(f"{API_BASE_URL}/metrics", params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Métricas com filtro de data funcionando")
            return True, data
        else:
            print(f"❌ Erro ao testar métricas com filtros: {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ Erro ao testar métricas com filtros: {e}")
        return False, None

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes de integração Frontend-Backend")
    print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 API Base URL: {API_BASE_URL}")
    
    # Lista de endpoints para testar
    endpoints = [
        ('/metrics', 'Métricas do Dashboard'),
        ('/status', 'Status do Sistema'),
        ('/technicians/ranking', 'Ranking de Técnicos'),
        ('/test', 'Endpoint de Teste')
    ]
    
    results = []
    
    # Testar cada endpoint
    for endpoint, description in endpoints:
        success, data = test_endpoint(endpoint, description)
        results.append((endpoint, success, data))
    
    # Testar métricas com filtros
    success, data = test_metrics_with_filters()
    results.append(('/metrics (com filtros)', success, data))
    
    # Resumo dos resultados
    print("\n" + "="*60)
    print("📋 RESUMO DOS TESTES")
    print("="*60)
    
    successful_tests = 0
    total_tests = len(results)
    
    for endpoint, success, data in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{status} - {endpoint}")
        if success:
            successful_tests += 1
    
    print(f"\n📊 Resultado Final: {successful_tests}/{total_tests} testes passaram")
    
    if successful_tests == total_tests:
        print("🎉 Todos os testes passaram! Backend está funcionando corretamente.")
        print("💡 Se o frontend ainda não está mostrando dados, o problema está na integração frontend.")
    else:
        print("⚠️  Alguns testes falharam. Verifique os endpoints com problemas.")
    
    # Salvar resultados em arquivo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'test_results_{timestamp}.json'
    
    test_results = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': total_tests,
        'successful_tests': successful_tests,
        'results': [
            {
                'endpoint': endpoint,
                'success': success,
                'data_sample': str(data)[:500] if data else None
            }
            for endpoint, success, data in results
        ]
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em: {filename}")

if __name__ == '__main__':
    main()