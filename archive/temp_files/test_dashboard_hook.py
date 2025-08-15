#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar o comportamento do hook useDashboard
"""

import requests
import json
from datetime import datetime, timedelta
import time

def test_api_endpoints():
    """Testa todos os endpoints usados pelo hook useDashboard"""
    print("🔍 Testando endpoints da API...")
    
    base_url = 'http://localhost:5000'
    endpoints = {
        'metrics': '/api/metrics',
        'system_status': '/api/status',
        'technician_ranking': '/api/technicians/ranking'
    }
    
    results = {}
    
    for name, endpoint in endpoints.items():
        try:
            print(f"\n📡 Testando {name}: {endpoint}")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results[name] = {
                    'status': 'success',
                    'data': data,
                    'response_time': response.elapsed.total_seconds()
                }
                print(f"✅ {name}: OK ({response.elapsed.total_seconds():.2f}s)")
                
                # Verificar estrutura específica
                if name == 'metrics':
                    if 'data' in data and 'niveis' in data['data']:
                        print(f"   📊 Níveis encontrados: {list(data['data']['niveis'].keys())}")
                    else:
                        print(f"   ⚠️ Estrutura inesperada: {list(data.keys())}")
                        
                elif name == 'system_status':
                    if 'data' in data:
                        status_data = data['data']
                        print(f"   🔧 Status: {status_data.get('status', 'unknown')}")
                        print(f"   🔗 GLPI: {status_data.get('glpi', 'unknown')}")
                    else:
                        print(f"   ⚠️ Estrutura inesperada: {list(data.keys())}")
                        
                elif name == 'technician_ranking':
                    if 'data' in data and isinstance(data['data'], list):
                        print(f"   👥 Técnicos encontrados: {len(data['data'])}")
                    else:
                        print(f"   ⚠️ Estrutura inesperada: {type(data.get('data', 'missing'))}")
                        
            else:
                results[name] = {
                    'status': 'error',
                    'error': f"HTTP {response.status_code}",
                    'response': response.text[:200]
                }
                print(f"❌ {name}: HTTP {response.status_code}")
                
        except Exception as e:
            results[name] = {
                'status': 'error',
                'error': str(e)
            }
            print(f"❌ {name}: {e}")
    
    return results

def test_parallel_requests():
    """Testa requisições paralelas como faz o hook useDashboard"""
    print("\n🔄 Testando requisições paralelas...")
    
    import concurrent.futures
    import threading
    
    base_url = 'http://localhost:5000'
    endpoints = [
        '/api/metrics',
        '/api/status', 
        '/api/technicians/ranking'
    ]
    
    def fetch_endpoint(endpoint):
        try:
            start_time = time.time()
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            end_time = time.time()
            
            return {
                'endpoint': endpoint,
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response_time': end_time - start_time,
                'data': response.json() if response.status_code == 200 else None,
                'error': None
            }
        except Exception as e:
            return {
                'endpoint': endpoint,
                'status_code': None,
                'success': False,
                'response_time': None,
                'data': None,
                'error': str(e)
            }
    
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(fetch_endpoint, endpoint) for endpoint in endpoints]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"⏱️ Tempo total das requisições paralelas: {total_time:.2f}s")
    
    for result in results:
        endpoint = result['endpoint']
        if result['success']:
            print(f"✅ {endpoint}: OK ({result['response_time']:.2f}s)")
        else:
            print(f"❌ {endpoint}: {result['error'] or f'HTTP {result['status_code']}'}")
    
    return results

def test_with_date_filters():
    """Testa endpoints com filtros de data"""
    print("\n📅 Testando com filtros de data...")
    
    base_url = 'http://localhost:5000'
    
    # Testar diferentes ranges de data
    date_ranges = [
        {
            'name': 'Últimos 7 dias',
            'start_date': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            'end_date': datetime.now().strftime('%Y-%m-%d')
        },
        {
            'name': 'Último mês',
            'start_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'end_date': datetime.now().strftime('%Y-%m-%d')
        },
        {
            'name': 'Este ano',
            'start_date': f"{datetime.now().year}-01-01",
            'end_date': datetime.now().strftime('%Y-%m-%d')
        }
    ]
    
    for date_range in date_ranges:
        print(f"\n📊 Testando: {date_range['name']}")
        print(f"   📅 De: {date_range['start_date']} até {date_range['end_date']}")
        
        params = {
            'start_date': date_range['start_date'],
            'end_date': date_range['end_date']
        }
        
        try:
            response = requests.get(f"{base_url}/api/metrics", params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'niveis' in data['data']:
                    niveis = data['data']['niveis']
                    total_tickets = sum(
                        nivel.get('novos', 0) + nivel.get('pendentes', 0) + 
                        nivel.get('progresso', 0) + nivel.get('resolvidos', 0)
                        for nivel in niveis.values()
                    )
                    print(f"   ✅ Total de tickets: {total_tickets}")
                    print(f"   📈 Tendências: {list(data['data'].get('tendencias', {}).keys())}")
                else:
                    print(f"   ⚠️ Estrutura inesperada")
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")

def simulate_dashboard_hook_behavior():
    """Simula o comportamento completo do hook useDashboard"""
    print("\n🎯 Simulando comportamento do hook useDashboard...")
    
    # Simular estado inicial
    print("📋 Estado inicial:")
    print("   - isLoading: true")
    print("   - data: null")
    print("   - error: null")
    
    # Simular carregamento inicial
    print("\n🔄 Carregamento inicial (sem filtros)...")
    initial_results = test_parallel_requests()
    
    all_success = all(result['success'] for result in initial_results)
    
    if all_success:
        print("\n✅ Carregamento inicial: SUCESSO")
        print("   - isLoading: false")
        print("   - data: populated")
        print("   - error: null")
        
        # Simular atualização de filtros
        print("\n🔄 Simulando atualização de filtros...")
        test_with_date_filters()
        
        print("\n✅ Hook useDashboard deveria funcionar corretamente")
        
    else:
        print("\n❌ Carregamento inicial: FALHA")
        print("   - isLoading: false")
        print("   - data: null")
        print("   - error: 'Falha ao carregar dados do dashboard'")
        
        failed_endpoints = [r['endpoint'] for r in initial_results if not r['success']]
        print(f"   - Endpoints com falha: {failed_endpoints}")
        
        print("\n❌ Hook useDashboard teria problemas")
    
    return all_success

def main():
    """Função principal"""
    print("=== TESTE DO HOOK useDashboard ===")
    print(f"Timestamp: {datetime.now()}\n")
    
    # Teste 1: Endpoints individuais
    print("\n" + "="*50)
    print("TESTE 1: Endpoints Individuais")
    print("="*50)
    api_results = test_api_endpoints()
    
    # Teste 2: Requisições paralelas
    print("\n" + "="*50)
    print("TESTE 2: Requisições Paralelas")
    print("="*50)
    parallel_results = test_parallel_requests()
    
    # Teste 3: Filtros de data
    print("\n" + "="*50)
    print("TESTE 3: Filtros de Data")
    print("="*50)
    test_with_date_filters()
    
    # Teste 4: Simulação completa
    print("\n" + "="*50)
    print("TESTE 4: Simulação Completa do Hook")
    print("="*50)
    hook_success = simulate_dashboard_hook_behavior()
    
    # Resumo final
    print("\n" + "="*50)
    print("RESUMO FINAL")
    print("="*50)
    
    endpoints_ok = all(result.get('status') == 'success' for result in api_results.values())
    parallel_ok = all(result['success'] for result in parallel_results)
    
    print(f"✅ Endpoints individuais: {'OK' if endpoints_ok else 'FALHA'}")
    print(f"✅ Requisições paralelas: {'OK' if parallel_ok else 'FALHA'}")
    print(f"✅ Simulação do hook: {'OK' if hook_success else 'FALHA'}")
    
    if endpoints_ok and parallel_ok and hook_success:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("O hook useDashboard deveria funcionar corretamente.")
        print("Se ainda há problemas, eles podem estar na renderização do React.")
    else:
        print("\n❌ ALGUNS TESTES FALHARAM!")
        print("Há problemas na API que precisam ser corrigidos.")
    
    print("\n=== FIM DOS TESTES ===")

if __name__ == "__main__":
    main()