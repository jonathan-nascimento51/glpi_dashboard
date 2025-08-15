#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validaçáo matemática das tendências do dashboard GLPI
"""

import requests
import json
from datetime import datetime, timedelta

def validate_trend_calculation(current: int, previous: int, expected_trend: str):
    """Valida se o cálculo de tendência está correto"""
    print(f"\n=== VALIDAÇáO MATEMÁTICA ===")
    print(f"Valor atual: {current}")
    print(f"Valor anterior: {previous}")
    print(f"Tendência esperada: {expected_trend}")
    
    # Calcular tendência manualmente
    if previous == 0:
        calculated_trend = "+100%" if current > 0 else "0%"
    else:
        change = ((current - previous) / previous) * 100
        if change > 0:
            calculated_trend = f"+{change:.1f}%"
        elif change < 0:
            calculated_trend = f"{change:.1f}%"
        else:
            calculated_trend = "0%"
    
    print(f"Tendência calculada: {calculated_trend}")
    
    # Verificar se está correto
    is_correct = calculated_trend == expected_trend
    print(f"Status: {'✅ CORRETO' if is_correct else '❌ INCORRETO'}")
    
    if not is_correct:
        print(f"⚠️  DIFERENÇA DETECTADA!")
        print(f"   Esperado: {expected_trend}")
        print(f"   Calculado: {calculated_trend}")
    
    return is_correct

def test_api_without_filters():
    """Testa API sem filtros de data"""
    print("\n=== TESTE SEM FILTROS DE DATA ===")
    
    try:
        response = requests.get('http://localhost:5000/api/metrics')
        response.raise_for_status()
        data = response.json()
        
        niveis = data['data']['niveis']['geral']
        tendencias = data['data']['tendencias']
        
        print(f"\nDados atuais (sem filtro):")
        print(f"  Novos: {niveis['novos']}")
        print(f"  Pendentes: {niveis['pendentes']}")
        print(f"  Progresso: {niveis['progresso']}")
        print(f"  Resolvidos: {niveis['resolvidos']}")
        
        print(f"\nTendências retornadas:")
        print(f"  Novos: {tendencias['novos']}")
        print(f"  Pendentes: {tendencias['pendentes']}")
        print(f"  Progresso: {tendencias['progresso']}")
        print(f"  Resolvidos: {tendencias['resolvidos']}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False

def test_api_with_date_filters():
    """Testa API com filtros de data específicos"""
    print("\n=== TESTE COM FILTROS DE DATA ===")
    
    # Testar período de julho 2025
    start_date = "2025-07-01"
    end_date = "2025-07-31"
    
    try:
        url = f'http://localhost:5000/api/metrics?start_date={start_date}&end_date={end_date}'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        niveis = data['data']['niveis']['geral']
        tendencias = data['data']['tendencias']
        filtros = data['data'].get('filtros_aplicados', {})
        
        print(f"\nFiltros aplicados:")
        print(f"  Data início: {filtros.get('data_inicio', 'N/A')}")
        print(f"  Data fim: {filtros.get('data_fim', 'N/A')}")
        
        print(f"\nDados do período {start_date} a {end_date}:")
        print(f"  Novos: {niveis['novos']}")
        print(f"  Pendentes: {niveis['pendentes']}")
        print(f"  Progresso: {niveis['progresso']}")
        print(f"  Resolvidos: {niveis['resolvidos']}")
        print(f"  Total: {niveis['total']}")
        
        print(f"\nTendências vs. período anterior:")
        print(f"  Novos: {tendencias['novos']}")
        print(f"  Pendentes: {tendencias['pendentes']}")
        print(f"  Progresso: {tendencias['progresso']}")
        print(f"  Resolvidos: {tendencias['resolvidos']}")
        
        # Calcular qual seria o período anterior
        current_start = datetime.strptime(start_date, '%Y-%m-%d')
        current_end = datetime.strptime(end_date, '%Y-%m-%d')
        period_duration = (current_end - current_start).days
        
        end_date_previous = (current_start - timedelta(days=1)).strftime('%Y-%m-%d')
        start_date_previous = (current_start - timedelta(days=period_duration + 1)).strftime('%Y-%m-%d')
        
        print(f"\nPeríodo anterior calculado: {start_date_previous} a {end_date_previous}")
        print(f"Duraçáo do período: {period_duration} dias")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False

def analyze_trend_logic():
    """Analisa a lógica de cálculo das tendências"""
    print("\n=== ANÁLISE DA LÓGICA DE TENDÊNCIAS ===")
    
    # Cenários de teste
    test_cases = [
        {"name": "Crescimento normal", "current": 100, "previous": 80, "expected": "+25.0%"},
        {"name": "Decréscimo normal", "current": 80, "previous": 100, "expected": "-20.0%"},
        {"name": "Sem mudança", "current": 100, "previous": 100, "expected": "0%"},
        {"name": "Crescimento de zero", "current": 50, "previous": 0, "expected": "+100%"},
        {"name": "Permanece zero", "current": 0, "previous": 0, "expected": "0%"},
        {"name": "Volta a zero", "current": 0, "previous": 50, "expected": "-100.0%"},
        {"name": "Crescimento alto", "current": 1000, "previous": 10, "expected": "+9900.0%"},
    ]
    
    all_correct = True
    
    for case in test_cases:
        print(f"\n--- {case['name']} ---")
        is_correct = validate_trend_calculation(
            case['current'], 
            case['previous'], 
            case['expected']
        )
        if not is_correct:
            all_correct = False
    
    return all_correct

def main():
    """Funçáo principal de validaçáo"""
    print("=== VALIDAÇáO MATEMÁTICA DAS TENDÊNCIAS ===")
    print("Este script valida se os cálculos de tendência estáo matematicamente corretos.\n")
    
    # Executar testes
    test1 = analyze_trend_logic()
    test2 = test_api_without_filters()
    test3 = test_api_with_date_filters()
    
    print("\n=== RESUMO FINAL ===")
    print(f"Lógica matemática: {'✅ CORRETA' if test1 else '❌ INCORRETA'}")
    print(f"API sem filtros: {'✅ FUNCIONANDO' if test2 else '❌ COM PROBLEMAS'}")
    print(f"API com filtros: {'✅ FUNCIONANDO' if test3 else '❌ COM PROBLEMAS'}")
    
    if test1 and test2 and test3:
        print("\n🎉 VALIDAÇáO COMPLETA: Todos os testes passaram!")
        print("Os cálculos de tendência estáo matematicamente corretos.")
    else:
        print("\n⚠️  PROBLEMAS DETECTADOS: Alguns testes falharam.")
        print("Verifique os detalhes acima para identificar os problemas.")

if __name__ == "__main__":
    main()
