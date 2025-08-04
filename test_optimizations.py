#!/usr/bin/env python3
"""
Script de teste para verificar as otimizações implementadas no sistema de consultas
Verifica se o cache está funcionando e se as consultas repetitivas foram reduzidas
"""

import requests
import time
import json
from datetime import datetime

# Configurações
BASE_URL = "http://127.0.0.1:5000"
TEST_DURATION = 300  # 5 minutos de teste
REQUEST_INTERVAL = 10  # Fazer uma requisição a cada 10 segundos

def test_endpoint(endpoint, description):
    """Testa um endpoint específico e mede o tempo de resposta"""
    try:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=30)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # em ms
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'response_time': response_time,
                'status_code': response.status_code,
                'data_size': len(json.dumps(data)) if data else 0,
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'success': False,
                'response_time': response_time,
                'status_code': response.status_code,
                'error': f"HTTP {response.status_code}",
                'timestamp': datetime.now().isoformat()
            }
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'response_time': 30000,  # timeout
            'error': 'Timeout (30s)',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'success': False,
            'response_time': 0,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def run_optimization_test():
    """Executa o teste de otimização"""
    print("🚀 Iniciando teste de otimizações...")
    print(f"⏱️  Duração do teste: {TEST_DURATION} segundos")
    print(f"🔄 Intervalo entre requisições: {REQUEST_INTERVAL} segundos")
    print("="*60)
    
    endpoints = [
        ('/api/metrics', 'Métricas Gerais'),
        ('/api/technicians/ranking', 'Ranking de Técnicos'),
        ('/api/status', 'Status do Sistema')
    ]
    
    results = {endpoint[0]: [] for endpoint in endpoints}
    start_test_time = time.time()
    
    while time.time() - start_test_time < TEST_DURATION:
        print(f"\n📊 Testando endpoints - {datetime.now().strftime('%H:%M:%S')}")
        
        for endpoint, description in endpoints:
            print(f"  🔍 Testando {description}...")
            result = test_endpoint(endpoint, description)
            results[endpoint].append(result)
            
            if result['success']:
                print(f"    ✅ Sucesso - {result['response_time']:.0f}ms")
            else:
                print(f"    ❌ Erro - {result['error']}")
        
        print(f"  ⏳ Aguardando {REQUEST_INTERVAL} segundos...")
        time.sleep(REQUEST_INTERVAL)
    
    print("\n" + "="*60)
    print("📈 RELATÓRIO DE OTIMIZAÇÃO")
    print("="*60)
    
    for endpoint, description in endpoints:
        endpoint_results = results[endpoint]
        successful_requests = [r for r in endpoint_results if r['success']]
        failed_requests = [r for r in endpoint_results if not r['success']]
        
        print(f"\n🎯 {description} ({endpoint})")
        print(f"   Total de requisições: {len(endpoint_results)}")
        print(f"   Sucessos: {len(successful_requests)}")
        print(f"   Falhas: {len(failed_requests)}")
        
        if successful_requests:
            response_times = [r['response_time'] for r in successful_requests]
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            print(f"   Tempo médio de resposta: {avg_response_time:.0f}ms")
            print(f"   Tempo mínimo: {min_response_time:.0f}ms")
            print(f"   Tempo máximo: {max_response_time:.0f}ms")
            
            # Verificar se há evidência de cache (tempos de resposta consistentemente baixos)
            fast_responses = [t for t in response_times if t < 100]  # < 100ms
            if len(fast_responses) > len(response_times) * 0.5:  # Mais de 50% rápidas
                print(f"   🚀 Cache funcionando! {len(fast_responses)} respostas rápidas (<100ms)")
            else:
                print(f"   ⚠️  Cache pode não estar funcionando adequadamente")
        
        if failed_requests:
            print(f"   ❌ Erros encontrados:")
            error_counts = {}
            for req in failed_requests:
                error = req.get('error', 'Erro desconhecido')
                error_counts[error] = error_counts.get(error, 0) + 1
            
            for error, count in error_counts.items():
                print(f"      - {error}: {count} ocorrências")
    
    print("\n" + "="*60)
    print("🎯 CONCLUSÕES E RECOMENDAÇÕES")
    print("="*60)
    
    # Análise geral
    all_successful = sum(len([r for r in results[ep] if r['success']]) for ep in results)
    all_total = sum(len(results[ep]) for ep in results)
    success_rate = (all_successful / all_total) * 100 if all_total > 0 else 0
    
    print(f"Taxa de sucesso geral: {success_rate:.1f}%")
    
    if success_rate >= 95:
        print("✅ Sistema funcionando de forma excelente!")
    elif success_rate >= 80:
        print("⚠️  Sistema funcionando bem, mas há margem para melhorias")
    else:
        print("❌ Sistema apresentando problemas significativos")
    
    # Verificar se o ranking de técnicos está funcionando
    ranking_results = results.get('/api/technicians/ranking', [])
    ranking_successful = [r for r in ranking_results if r['success']]
    
    if ranking_successful:
        avg_ranking_time = sum(r['response_time'] for r in ranking_successful) / len(ranking_successful)
        if avg_ranking_time < 5000:  # Menos de 5 segundos
            print("✅ Consultas de técnicos otimizadas com sucesso!")
        else:
            print("⚠️  Consultas de técnicos ainda podem ser otimizadas")
    else:
        print("❌ Endpoint de ranking de técnicos não está funcionando")
    
    print("\n🔧 Próximos passos recomendados:")
    if success_rate < 95:
        print("   1. Verificar logs do backend para identificar erros")
        print("   2. Ajustar configurações de timeout")
        print("   3. Implementar retry logic")
    
    if any(len([r for r in results[ep] if r['success'] and r['response_time'] > 2000]) > 0 for ep in results):
        print("   4. Otimizar consultas lentas (>2s)")
        print("   5. Aumentar TTL do cache se necessário")
    
    print("   6. Monitorar sistema em produção")
    print("   7. Configurar alertas para falhas")

if __name__ == "__main__":
    try:
        run_optimization_test()
    except KeyboardInterrupt:
        print("\n\n⏹️  Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro durante o teste: {e}")
    
    print("\n🏁 Teste finalizado!")