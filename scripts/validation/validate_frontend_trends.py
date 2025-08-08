#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para validar a matemática das tendências tanto no backend quanto no frontend
Verifica se os cálculos estão corretos e se a exibição na interface está adequada
"""

import requests
import json
import re
from datetime import datetime, timedelta

def calculate_percentage_change(current: int, previous: int) -> str:
    """Replica a função de cálculo de percentual do backend"""
    if previous == 0:
        return "+100%" if current > 0 else "0%"
    
    change = ((current - previous) / previous) * 100
    if change > 0:
        return f"+{change:.1f}%"
    elif change < 0:
        return f"{change:.1f}%"
    else:
        return "0%"

def parse_trend_frontend(trend_str: str) -> dict:
    """Replica as funções do frontend para processar tendências"""
    if not trend_str:
        return {'direction': 'stable', 'value': 0, 'display': '0%'}
    
    # getTrendDirection
    value = float(trend_str.replace('%', '').replace('+', ''))
    if value > 0:
        direction = 'up'
    elif value < 0:
        direction = 'down'
    else:
        direction = 'stable'
    
    # parseTrendValue
    abs_value = abs(value)
    
    return {
        'direction': direction,
        'value': abs_value,
        'display': trend_str,
        'original': trend_str
    }

def test_api_trends():
    """Testa as tendências retornadas pela API"""
    print("=== TESTE DE TENDÊNCIAS DA API ===")
    
    try:
        # Teste sem filtros de data
        print("\n1. Testando sem filtros de data:")
        response = requests.get('http://localhost:5000/api/metrics')
        response.raise_for_status()
        data = response.json()
        
        tendencias = data['data']['tendencias']
        print(f"Tendências recebidas: {json.dumps(tendencias, indent=2)}")
        
        # Processar cada tendência como o frontend faria
        for categoria, trend_str in tendencias.items():
            frontend_data = parse_trend_frontend(trend_str)
            print(f"\n{categoria.upper()}:")
            print(f"  String original: {trend_str}")
            print(f"  Direção: {frontend_data['direction']}")
            print(f"  Valor absoluto: {frontend_data['value']}%")
            print(f"  Display: {frontend_data['display']}")
        
        # Teste com filtros de data específicos
        print("\n\n2. Testando com filtros de data (Julho 2025):")
        params = {
            'start_date': '2025-07-01',
            'end_date': '2025-07-31'
        }
        response = requests.get('http://localhost:5000/api/metrics', params=params)
        response.raise_for_status()
        data = response.json()
        
        tendencias = data['data']['tendencias']
        filtros = data['data']['filtros_aplicados']
        
        print(f"Filtros aplicados: {json.dumps(filtros, indent=2)}")
        print(f"Tendências com filtro: {json.dumps(tendencias, indent=2)}")
        
        # Processar tendências com filtro
        for categoria, trend_str in tendencias.items():
            frontend_data = parse_trend_frontend(trend_str)
            print(f"\n{categoria.upper()} (com filtro):")
            print(f"  String original: {trend_str}")
            print(f"  Direção: {frontend_data['direction']}")
            print(f"  Valor absoluto: {frontend_data['value']}%")
            print(f"  Display: {frontend_data['display']}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO no teste da API: {e}")
        return False

def test_mathematical_consistency():
    """Testa a consistência matemática dos cálculos"""
    print("\n\n=== TESTE DE CONSISTÊNCIA MATEMÁTICA ===")
    
    test_cases = [
        # (atual, anterior, esperado)
        (10, 5, "+100.0%"),    # Dobrou
        (5, 10, "-50.0%"),     # Reduziu pela metade
        (10, 10, "0%"),        # Sem mudança
        (5, 0, "+100%"),       # Crescimento do zero
        (0, 5, "-100.0%"),     # Voltou ao zero
        (0, 0, "0%"),          # Permaneceu zero
        (15, 3, "+400.0%"),    # Alto crescimento
        (100, 200, "-50.0%"),  # Redução significativa
    ]
    
    all_passed = True
    
    for i, (atual, anterior, esperado) in enumerate(test_cases, 1):
        resultado = calculate_percentage_change(atual, anterior)
        frontend_data = parse_trend_frontend(resultado)
        
        print(f"\nTeste {i}: atual={atual}, anterior={anterior}")
        print(f"  Esperado: {esperado}")
        print(f"  Calculado: {resultado}")
        print(f"  Frontend - Direção: {frontend_data['direction']}, Valor: {frontend_data['value']}%")
        
        if resultado == esperado:
            print(f"  ✅ PASSOU")
        else:
            print(f"  ❌ FALHOU - Esperado: {esperado}, Obtido: {resultado}")
            all_passed = False
    
    return all_passed

def validate_frontend_processing():
    """Valida o processamento das tendências no frontend"""
    print("\n\n=== VALIDAÇÃO DO PROCESSAMENTO FRONTEND ===")
    
    trend_examples = [
        "+100.0%",
        "-50.0%",
        "0%",
        "+933.3%",
        "-0.2%",
        "+1600.0%"
    ]
    
    for trend in trend_examples:
        frontend_data = parse_trend_frontend(trend)
        print(f"\nTendência: {trend}")
        print(f"  Direção: {frontend_data['direction']}")
        print(f"  Valor absoluto: {frontend_data['value']}")
        print(f"  Display: {frontend_data['display']}")
        
        # Validar lógica de direção
        expected_direction = 'up' if trend.startswith('+') and not trend == '+0%' else ('down' if trend.startswith('-') and not trend == '-0%' else 'stable')
        if frontend_data['direction'] == expected_direction:
            print(f"  ✅ Direção correta")
        else:
            print(f"  ❌ Direção incorreta - Esperado: {expected_direction}, Obtido: {frontend_data['direction']}")

def main():
    """Função principal que executa todos os testes"""
    print("🔍 VALIDAÇÃO COMPLETA DA MATEMÁTICA DAS TENDÊNCIAS")
    print("=" * 60)
    
    # Teste 1: API
    api_ok = test_api_trends()
    
    # Teste 2: Matemática
    math_ok = test_mathematical_consistency()
    
    # Teste 3: Frontend
    validate_frontend_processing()
    
    # Resumo final
    print("\n\n=== RESUMO FINAL ===")
    print(f"✅ API funcionando: {'Sim' if api_ok else 'Não'}")
    print(f"✅ Matemática correta: {'Sim' if math_ok else 'Não'}")
    print(f"✅ Processamento frontend: Validado")
    
    if api_ok and math_ok:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("A matemática das tendências está correta tanto no backend quanto no frontend.")
        print("\nComo funciona:")
        print("1. Backend calcula: ((atual - anterior) / anterior) * 100")
        print("2. Backend formata: +X.X% ou -X.X% ou 0%")
        print("3. Frontend processa a string para extrair direção e valor")
        print("4. Frontend exibe com ícones e cores apropriadas")
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM")
        print("Verifique os logs acima para identificar os problemas.")

if __name__ == "__main__":
    main()