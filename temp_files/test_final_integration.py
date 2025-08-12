#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste final de integração após correções
"""

import requests
import json
from datetime import datetime
import time

def test_all_endpoints():
    """Testa todos os endpoints principais"""
    print("🔍 Teste Final de Integração")
    print("=" * 50)
    
    base_url = 'http://localhost:5000'
    endpoints = {
        'Métricas': '/api/metrics',
        'Status do Sistema': '/api/status',
        'Ranking de Técnicos': '/api/technicians/ranking'
    }
    
    all_success = True
    
    for name, endpoint in endpoints.items():
        try:
            print(f"\n📡 Testando {name}: {endpoint}")
            start_time = time.time()
            response = requests.get(f"{base_url}{endpoint}", timeout=15)
            response_time = (time.time() - start_time) * 1000
            
            print(f"⏱️  Tempo de resposta: {response_time:.2f}ms")
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {name}: OK")
                
                # Verificar estrutura específica
                if 'success' in data and data['success']:
                    print(f"   ✅ Campo 'success' = True")
                else:
                    print(f"   ⚠️  Campo 'success' não encontrado ou False")
                
                if 'data' in data:
                    print(f"   ✅ Campo 'data' presente")
                    
                    # Verificações específicas
                    if endpoint == '/api/metrics':
                        metrics = data['data']
                        if 'niveis' in metrics:
                            print(f"   📊 Níveis encontrados: {list(metrics['niveis'].keys())}")
                        if 'tendencias' in metrics:
                            print(f"   📈 Tendências disponíveis")
                            
                    elif endpoint == '/api/status':
                        status = data['data']
                        if 'api' in status and 'glpi' in status:
                            print(f"   🟢 API: {status['api']}, GLPI: {status['glpi']}")
                            
                    elif endpoint == '/api/technicians/ranking':
                        ranking = data['data']
                        print(f"   👥 Técnicos retornados: {len(ranking)}")
                        
                else:
                    print(f"   ⚠️  Campo 'data' não encontrado")
                    
            else:
                print(f"❌ {name}: FALHA - Status {response.status_code}")
                print(f"   Resposta: {response.text[:200]}...")
                all_success = False
                
        except requests.exceptions.Timeout:
            print(f"❌ {name}: TIMEOUT")
            all_success = False
        except Exception as e:
            print(f"❌ {name}: ERRO - {str(e)}")
            all_success = False
    
    print("\n" + "=" * 50)
    if all_success:
        print("🎉 TODOS OS ENDPOINTS FUNCIONANDO!")
        print("✅ A integração frontend-backend está OK")
    else:
        print("❌ ALGUNS ENDPOINTS COM PROBLEMAS")
        print("⚠️  Verifique os logs acima")
    
    return all_success

def test_frontend_integration():
    """Testa se o frontend consegue processar os dados"""
    print("\n🌐 Testando integração com frontend...")
    
    try:
        # Simular chamada do frontend
        response = requests.get('http://localhost:5000/api/metrics', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success') and 'data' in data:
                metrics = data['data']
                
                # Simular processamento do frontend
                if 'niveis' in metrics:
                    # Calcular totais gerais (como faz o transformLegacyData)
                    geral = {
                        'novos': sum(nivel.get('novos', 0) for nivel in metrics['niveis'].values()),
                        'pendentes': sum(nivel.get('pendentes', 0) for nivel in metrics['niveis'].values()),
                        'progresso': sum(nivel.get('progresso', 0) for nivel in metrics['niveis'].values()),
                        'resolvidos': sum(nivel.get('resolvidos', 0) for nivel in metrics['niveis'].values())
                    }
                    
                    print(f"   ✅ Processamento frontend simulado:")
                    print(f"      📊 Total geral: {sum(geral.values())} tickets")
                    print(f"      🆕 Novos: {geral['novos']}")
                    print(f"      ⏳ Pendentes: {geral['pendentes']}")
                    print(f"      🔄 Em progresso: {geral['progresso']}")
                    print(f"      ✅ Resolvidos: {geral['resolvidos']}")
                    
                    return True
                else:
                    print("   ❌ Estrutura de níveis não encontrada")
                    return False
            else:
                print("   ❌ Resposta da API inválida")
                return False
        else:
            print(f"   ❌ Erro na API: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro na integração: {str(e)}")
        return False

if __name__ == "__main__":
    print(f"🚀 Iniciando teste final - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Teste 1: Endpoints
    endpoints_ok = test_all_endpoints()
    
    # Teste 2: Integração frontend
    frontend_ok = test_frontend_integration()
    
    print("\n" + "=" * 50)
    print("📋 RESUMO FINAL:")
    print(f"   🔗 Endpoints: {'✅ OK' if endpoints_ok else '❌ FALHA'}")
    print(f"   🌐 Frontend: {'✅ OK' if frontend_ok else '❌ FALHA'}")
    
    if endpoints_ok and frontend_ok:
        print("\n🎉 INTEGRAÇÃO COMPLETA FUNCIONANDO!")
        print("✅ O dashboard deve estar carregando corretamente")
    else:
        print("\n⚠️  AINDA HÁ PROBLEMAS A RESOLVER")
    
    print("\n=== FIM DO TESTE ===")