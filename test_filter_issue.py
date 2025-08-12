#!/usr/bin/env python3
"""
Script para reproduzir e analisar o problema de inconsistência dos filtros de data.
Este script faz requisições diretas à API para identificar onde está o problema.
"""

import requests
import json
from datetime import datetime, timedelta
import time

API_BASE = 'http://localhost:5000/api'

def make_request(endpoint, params=None):
    """Faz uma requisição à API e retorna os dados."""
    url = f"{API_BASE}{endpoint}"
    try:
        print(f"\n🔍 Fazendo requisição para: {url}")
        if params:
            print(f"📋 Parâmetros: {params}")
        
        response = requests.get(url, params=params, timeout=30)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"❌ Erro HTTP: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def extract_metrics_summary(data):
    """Extrai um resumo das métricas dos dados retornados."""
    if not data or 'data' not in data:
        return "Dados inválidos"
    
    metrics = data['data']
    summary = {}
    
    # Extrair dados gerais
    if 'niveis' in metrics and 'geral' in metrics['niveis']:
        geral = metrics['niveis']['geral']
        summary['geral'] = {
            'total': geral.get('total', 0),
            'novos': geral.get('novos', 0),
            'pendentes': geral.get('pendentes', 0),
            'progresso': geral.get('progresso', 0),
            'resolvidos': geral.get('resolvidos', 0)
        }
    
    # Extrair dados por nível
    if 'niveis' in metrics:
        for nivel in ['n1', 'n2', 'n3', 'n4']:
            if nivel in metrics['niveis']:
                nivel_data = metrics['niveis'][nivel]
                summary[nivel] = {
                    'total': nivel_data.get('total', 0),
                    'novos': nivel_data.get('novos', 0),
                    'pendentes': nivel_data.get('pendentes', 0),
                    'progresso': nivel_data.get('progresso', 0),
                    'resolvidos': nivel_data.get('resolvidos', 0)
                }
    
    return summary

def test_without_filters():
    """Testa a API sem filtros."""
    print("\n" + "="*60)
    print("🧪 TESTE 1: SEM FILTROS")
    print("="*60)
    
    data = make_request('/metrics')
    if data:
        summary = extract_metrics_summary(data)
        print("\n📊 Resumo dos dados:")
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return summary
    return None

def test_with_date_filter(start_date, end_date):
    """Testa a API com filtros de data específicos."""
    print(f"\n" + "="*60)
    print(f"🧪 TESTE: COM FILTROS DE DATA ({start_date} a {end_date})")
    print("="*60)
    
    params = {
        'start_date': start_date,
        'end_date': end_date
    }
    
    data = make_request('/metrics', params)
    if data:
        summary = extract_metrics_summary(data)
        print("\n📊 Resumo dos dados:")
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return summary
    return None

def compare_results(result1, result2, label1, label2):
    """Compara dois resultados e identifica diferenças."""
    print(f"\n" + "="*60)
    print(f"🔍 COMPARAÇÃO: {label1} vs {label2}")
    print("="*60)
    
    if not result1 or not result2:
        print("❌ Não é possível comparar - dados ausentes")
        return
    
    # Comparar totais gerais
    if 'geral' in result1 and 'geral' in result2:
        geral1 = result1['geral']
        geral2 = result2['geral']
        
        print("\n📊 TOTAIS GERAIS:")
        for key in ['total', 'novos', 'pendentes', 'progresso', 'resolvidos']:
            val1 = geral1.get(key, 0)
            val2 = geral2.get(key, 0)
            diff = val2 - val1
            status = "✅" if val1 == val2 else "❌"
            print(f"  {key}: {val1} → {val2} (diff: {diff:+d}) {status}")
    
    # Comparar por níveis
    print("\n📊 POR NÍVEIS:")
    for nivel in ['n1', 'n2', 'n3', 'n4']:
        if nivel in result1 and nivel in result2:
            nivel1 = result1[nivel]
            nivel2 = result2[nivel]
            
            print(f"\n  {nivel.upper()}:")
            for key in ['total', 'novos', 'pendentes', 'progresso', 'resolvidos']:
                val1 = nivel1.get(key, 0)
                val2 = nivel2.get(key, 0)
                diff = val2 - val1
                status = "✅" if val1 == val2 else "❌"
                print(f"    {key}: {val1} → {val2} (diff: {diff:+d}) {status}")

def test_multiple_requests_same_filter():
    """Testa múltiplas requisições com o mesmo filtro para verificar consistência."""
    print(f"\n" + "="*60)
    print("🧪 TESTE: MÚLTIPLAS REQUISIÇÕES COM MESMO FILTRO")
    print("="*60)
    
    params = {
        'start_date': '2024-01-01',
        'end_date': '2024-01-31'
    }
    
    results = []
    for i in range(3):
        print(f"\n🔄 Requisição {i+1}/3...")
        data = make_request('/metrics', params)
        if data:
            summary = extract_metrics_summary(data)
            results.append(summary)
        time.sleep(1)  # Pequena pausa entre requisições
    
    # Comparar resultados
    if len(results) >= 2:
        for i in range(1, len(results)):
            compare_results(results[0], results[i], f"Req 1", f"Req {i+1}")
    
    return results

def main():
    """Função principal que executa todos os testes."""
    print("🚀 INICIANDO ANÁLISE DE INCONSISTÊNCIAS DOS FILTROS DE DATA")
    print("=" * 80)
    
    # Teste 1: Sem filtros
    result_no_filter = test_without_filters()
    
    # Teste 2: Com filtro de Janeiro 2024
    result_jan = test_with_date_filter('2024-01-01', '2024-01-31')
    
    # Teste 3: Com filtro de Junho 2024
    result_jun = test_with_date_filter('2024-06-01', '2024-06-30')
    
    # Teste 4: Múltiplas requisições com mesmo filtro
    multiple_results = test_multiple_requests_same_filter()
    
    # Comparações
    if result_no_filter and result_jan:
        compare_results(result_no_filter, result_jan, "Sem Filtros", "Janeiro 2024")
    
    if result_jan and result_jun:
        compare_results(result_jan, result_jun, "Janeiro 2024", "Junho 2024")
    
    print("\n" + "="*80)
    print("🏁 ANÁLISE CONCLUÍDA")
    print("="*80)
    print("\n💡 PRÓXIMOS PASSOS:")
    print("1. Verifique se há diferenças nos totais entre requisições")
    print("2. Observe se os filtros de data estão realmente afetando os resultados")
    print("3. Compare os dados retornados com o que é exibido no frontend")
    print("4. Verifique se há problemas de cache ou sincronização")

if __name__ == '__main__':
    main()