#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar o dashboard após as correções
Verifica se o backend está funcionando e se o frontend consegue conectar
"""

import requests
import json
import time
from datetime import datetime

def test_backend_health():
    """Testa se o backend está respondendo"""
    print("=== TESTE DE SAÚDE DO BACKEND ===")
    
    try:
        response = requests.get('http://localhost:5000/health', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend funcionando: {data.get('message', 'OK')}")
            return True
        else:
            print(f"❌ Backend retornou status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao backend")
        print("   Certifique-se de que o backend está rodando em http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar backend: {e}")
        return False

def test_metrics_endpoint():
    """Testa o endpoint de métricas"""
    print("\n=== TESTE DO ENDPOINT DE MÉTRICAS ===")
    
    try:
        start_time = time.time()
        response = requests.get('http://localhost:5000/api/metrics', timeout=30)
        response_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Métricas obtidas com sucesso")
            print(f"   Tempo de resposta: {response_time:.2f}ms")
            
            # Verifica estrutura básica
            if 'data' in data:
                metrics = data['data']
                print(f"   Total de tickets: {metrics.get('total', 'N/A')}")
                print(f"   Novos: {metrics.get('novos', 'N/A')}")
                print(f"   Pendentes: {metrics.get('pendentes', 'N/A')}")
                print(f"   Em progresso: {metrics.get('progresso', 'N/A')}")
                print(f"   Resolvidos: {metrics.get('resolvidos', 'N/A')}")
                
                # Verifica tendências
                if 'tendencias' in metrics:
                    tendencias = metrics['tendencias']
                    print(f"   Tendências: {json.dumps(tendencias, indent=2)}")
                
                return True
            else:
                print("❌ Estrutura de dados inválida")
                return False
        else:
            print(f"❌ Endpoint retornou status {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Erro: {error_data.get('error', 'Erro desconhecido')}")
            except:
                print(f"   Resposta: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout ao buscar métricas (>30s)")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão ao buscar métricas")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar métricas: {e}")
        return False

def test_technician_ranking():
    """Testa o endpoint de ranking de técnicos"""
    print("\n=== TESTE DO RANKING DE TÉCNICOS ===")
    
    try:
        start_time = time.time()
        response = requests.get('http://localhost:5000/api/technicians/ranking?limit=5', timeout=30)
        response_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ranking obtido com sucesso")
            print(f"   Tempo de resposta: {response_time:.2f}ms")
            
            if 'data' in data and isinstance(data['data'], list):
                ranking = data['data']
                print(f"   {len(ranking)} técnicos encontrados")
                
                for i, tech in enumerate(ranking[:3], 1):
                    name = tech.get('name', 'N/A')
                    count = tech.get('total', tech.get('ticket_count', 0))
                    print(f"   {i}º lugar: {name} - {count} tickets")
                
                return True
            else:
                print("❌ Estrutura de dados inválida")
                return False
        else:
            print(f"❌ Endpoint retornou status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar ranking: {e}")
        return False

def main():
    """Executa todos os testes"""
    print(f"🔍 TESTE DO DASHBOARD - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Testa backend
    backend_ok = test_backend_health()
    
    if not backend_ok:
        print("\n❌ Backend não está funcionando. Inicie o backend primeiro:")
        print("   python run_backend.py")
        return
    
    # Testa endpoints
    metrics_ok = test_metrics_endpoint()
    ranking_ok = test_technician_ranking()
    
    # Resumo
    print("\n=== RESUMO DOS TESTES ===")
    print(f"Backend: {'✅ OK' if backend_ok else '❌ FALHOU'}")
    print(f"Métricas: {'✅ OK' if metrics_ok else '❌ FALHOU'}")
    print(f"Ranking: {'✅ OK' if ranking_ok else '❌ FALHOU'}")
    
    if backend_ok and metrics_ok and ranking_ok:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("O dashboard está funcionando corretamente.")
        print("\nPróximos passos:")
        print("1. Inicie o frontend: cd frontend && npm start")
        print("2. Acesse http://localhost:3000")
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM")
        print("Verifique os logs acima para identificar os problemas.")

if __name__ == "__main__":
    main()