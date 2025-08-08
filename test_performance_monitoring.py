#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste de performance e monitoramento do ranking de técnicos
Testa tempos de resposta, cache e estabilidade do sistema
"""

import requests
import time
import json
from datetime import datetime
import statistics
import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_response_time(num_requests=5):
    """Testa o tempo de resposta do endpoint"""
    print(f"\n=== TESTE DE PERFORMANCE - {num_requests} requisições ===")
    
    times = []
    successful_requests = 0
    
    for i in range(num_requests):
        try:
            start_time = time.time()
            response = requests.get('http://localhost:5000/api/technicians/ranking')
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # em ms
            times.append(response_time)
            
            if response.status_code == 200:
                successful_requests += 1
                data = response.json()
                print(f"   Requisição {i+1}: {response_time:.0f}ms - {len(data['data'])} técnicos")
            else:
                print(f"   Requisição {i+1}: ERRO {response.status_code} - {response_time:.0f}ms")
                
        except Exception as e:
            print(f"   Requisição {i+1}: FALHA - {e}")
    
    if times:
        print(f"\n📊 Estatísticas de Performance:")
        print(f"   - Tempo médio: {statistics.mean(times):.0f}ms")
        print(f"   - Tempo mínimo: {min(times):.0f}ms")
        print(f"   - Tempo máximo: {max(times):.0f}ms")
        print(f"   - Desvio padrão: {statistics.stdev(times) if len(times) > 1 else 0:.0f}ms")
        print(f"   - Taxa de sucesso: {successful_requests}/{num_requests} ({successful_requests/num_requests*100:.1f}%)")
        
        # Avaliar performance
        avg_time = statistics.mean(times)
        if avg_time < 1000:
            print("   ✅ Performance EXCELENTE (< 1s)")
        elif avg_time < 3000:
            print("   ✅ Performance BOA (< 3s)")
        elif avg_time < 5000:
            print("   ⚠️ Performance ACEITÁVEL (< 5s)")
        else:
            print("   ❌ Performance RUIM (> 5s)")
    
    return times, successful_requests

def test_cache_behavior():
    """Testa o comportamento do cache"""
    print("\n=== TESTE DE CACHE ===")
    
    # Primeira requisição (cache miss)
    print("   Primeira requisição (cache miss):")
    start_time = time.time()
    response1 = requests.get('http://localhost:5000/api/technicians/ranking')
    time1 = (time.time() - start_time) * 1000
    
    if response1.status_code == 200:
        data1 = response1.json()
        print(f"   ✅ {time1:.0f}ms - {len(data1['data'])} técnicos")
    else:
        print(f"   ❌ Erro {response1.status_code}")
        return False
    
    # Segunda requisição imediata (cache hit)
    print("   Segunda requisição (cache hit):")
    start_time = time.time()
    response2 = requests.get('http://localhost:5000/api/technicians/ranking')
    time2 = (time.time() - start_time) * 1000
    
    if response2.status_code == 200:
        data2 = response2.json()
        print(f"   ✅ {time2:.0f}ms - {len(data2['data'])} técnicos")
        
        # Comparar dados
        if data1 == data2:
            print("   ✅ Dados consistentes entre requisições")
        else:
            print("   ❌ Dados inconsistentes entre requisições")
        
        # Avaliar melhoria do cache
        if time2 < time1 * 0.8:  # 20% mais rápido
            improvement = ((time1 - time2) / time1) * 100
            print(f"   ✅ Cache efetivo - {improvement:.1f}% mais rápido")
        else:
            print("   ⚠️ Cache pode não estar funcionando adequadamente")
        
        return True
    else:
        print(f"   ❌ Erro {response2.status_code}")
        return False

def test_data_stability(num_tests=3, interval=2):
    """Testa a estabilidade dos dados ao longo do tempo"""
    print(f"\n=== TESTE DE ESTABILIDADE - {num_tests} testes com {interval}s de intervalo ===")
    
    previous_data = None
    stable_count = 0
    
    for i in range(num_tests):
        try:
            response = requests.get('http://localhost:5000/api/technicians/ranking')
            if response.status_code == 200:
                current_data = response.json()['data']
                
                if previous_data is not None:
                    # Comparar IDs e scores dos top 10
                    prev_top10 = [(t['id'], t['score']) for t in previous_data[:10]]
                    curr_top10 = [(t['id'], t['score']) for t in current_data[:10]]
                    
                    if prev_top10 == curr_top10:
                        stable_count += 1
                        print(f"   Teste {i+1}: ✅ Dados estáveis (top 10 inalterado)")
                    else:
                        print(f"   Teste {i+1}: ⚠️ Dados alterados no top 10")
                        # Mostrar diferenças
                        for j, (prev, curr) in enumerate(zip(prev_top10, curr_top10)):
                            if prev != curr:
                                print(f"      Posição {j+1}: {prev} → {curr}")
                else:
                    print(f"   Teste {i+1}: ✅ Dados coletados ({len(current_data)} técnicos)")
                
                previous_data = current_data
                
            else:
                print(f"   Teste {i+1}: ❌ Erro {response.status_code}")
        
        except Exception as e:
            print(f"   Teste {i+1}: ❌ Falha - {e}")
        
        if i < num_tests - 1:  # Não esperar após o último teste
            time.sleep(interval)
    
    if num_tests > 1:
        stability_rate = (stable_count / (num_tests - 1)) * 100
        print(f"\n   📊 Taxa de estabilidade: {stability_rate:.1f}%")
        
        if stability_rate >= 90:
            print("   ✅ Sistema MUITO ESTÁVEL")
        elif stability_rate >= 70:
            print("   ✅ Sistema ESTÁVEL")
        elif stability_rate >= 50:
            print("   ⚠️ Sistema MODERADAMENTE ESTÁVEL")
        else:
            print("   ❌ Sistema INSTÁVEL")
    
    return stable_count

def test_concurrent_requests(num_concurrent=5):
    """Testa requisições concorrentes"""
    print(f"\n=== TESTE DE CONCORRÊNCIA - {num_concurrent} requisições simultâneas ===")
    
    import threading
    import queue
    
    results = queue.Queue()
    
    def make_request(request_id):
        try:
            start_time = time.time()
            response = requests.get('http://localhost:5000/api/technicians/ranking')
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                results.put((request_id, 'SUCCESS', response_time, len(data['data'])))
            else:
                results.put((request_id, 'ERROR', response_time, response.status_code))
                
        except Exception as e:
            results.put((request_id, 'FAILURE', 0, str(e)))
    
    # Criar e iniciar threads
    threads = []
    start_time = time.time()
    
    for i in range(num_concurrent):
        thread = threading.Thread(target=make_request, args=(i+1,))
        threads.append(thread)
        thread.start()
    
    # Aguardar conclusão
    for thread in threads:
        thread.join()
    
    total_time = (time.time() - start_time) * 1000
    
    # Coletar resultados
    successful = 0
    times = []
    
    while not results.empty():
        req_id, status, resp_time, extra = results.get()
        
        if status == 'SUCCESS':
            successful += 1
            times.append(resp_time)
            print(f"   Requisição {req_id}: ✅ {resp_time:.0f}ms - {extra} técnicos")
        elif status == 'ERROR':
            print(f"   Requisição {req_id}: ❌ Erro {extra} - {resp_time:.0f}ms")
        else:
            print(f"   Requisição {req_id}: ❌ Falha - {extra}")
    
    print(f"\n   📊 Resultados da concorrência:")
    print(f"   - Tempo total: {total_time:.0f}ms")
    print(f"   - Taxa de sucesso: {successful}/{num_concurrent} ({successful/num_concurrent*100:.1f}%)")
    
    if times:
        print(f"   - Tempo médio por requisição: {statistics.mean(times):.0f}ms")
        print(f"   - Tempo máximo: {max(times):.0f}ms")
        print(f"   - Tempo mínimo: {min(times):.0f}ms")
    
    if successful == num_concurrent:
        print("   ✅ Sistema suporta bem requisições concorrentes")
    elif successful >= num_concurrent * 0.8:
        print("   ⚠️ Sistema suporta parcialmente requisições concorrentes")
    else:
        print("   ❌ Sistema tem problemas com requisições concorrentes")
    
    return successful

def main():
    """Função principal"""
    print("🚀 INICIANDO TESTES DE PERFORMANCE E MONITORAMENTO")
    print(f"⏰ Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Executar testes
    times, success_rate = test_response_time(5)
    cache_ok = test_cache_behavior()
    stability = test_data_stability(3, 2)
    concurrent_success = test_concurrent_requests(5)
    
    # Resultado final
    print("\n=== RESULTADO FINAL DOS TESTES DE PERFORMANCE ===")
    
    performance_ok = times and statistics.mean(times) < 5000 and success_rate >= 4
    concurrency_ok = concurrent_success >= 4
    
    all_tests_passed = performance_ok and cache_ok and concurrency_ok
    
    if all_tests_passed:
        print("✅ TODOS OS TESTES DE PERFORMANCE PASSARAM!")
    else:
        print("❌ ALGUNS TESTES DE PERFORMANCE FALHARAM")
    
    print(f"\n📋 Resumo:")
    print(f"   - Performance: {'✅' if performance_ok else '❌'}")
    print(f"   - Cache: {'✅' if cache_ok else '❌'}")
    print(f"   - Concorrência: {'✅' if concurrency_ok else '❌'}")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)