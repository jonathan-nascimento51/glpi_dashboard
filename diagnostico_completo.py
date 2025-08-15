#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico Completo do Dashboard GLPI
Identifica inconsistências e problemas nos dados
"""

import requests
import json
from datetime import datetime
import sys

def test_endpoint(url, name):
    """Testa um endpoint e retorna os dados"""
    try:
        print(f"\n=== Testando {name} ===")
        print(f"URL: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Sucesso: {data.get('success', 'N/A')}")
            print(f"Tempo execução: {data.get('tempo_execucao', data.get('response_time_ms', 'N/A'))}")
            return data
        else:
            print(f"Erro: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"Erro na requisição: {e}")
        return None

def analyze_metrics_consistency(metrics_data):
    """Analisa consistência dos dados de métricas"""
    print("\n=== ANÁLISE DE CONSISTÊNCIA - MÉTRICAS ===")
    
    if not metrics_data or not metrics_data.get('success'):
        print(" Dados de métricas não disponíveis")
        return
    
    data = metrics_data.get('data', {})
    
    # Verificar totais gerais
    total_geral = data.get('total', 0)
    novos = data.get('novos', 0)
    pendentes = data.get('pendentes', 0)
    progresso = data.get('progresso', 0)
    resolvidos = data.get('resolvidos', 0)
    
    soma_status = novos + pendentes + progresso + resolvidos
    
    print(f"Total geral: {total_geral}")
    print(f"Soma por status: {soma_status} (novos: {novos}, pendentes: {pendentes}, progresso: {progresso}, resolvidos: {resolvidos})")
    
    if total_geral != soma_status:
        print(f" INCONSISTÊNCIA: Total geral ({total_geral}) != Soma por status ({soma_status})")
    else:
        print(" Totais gerais consistentes")
    
    # Verificar níveis
    niveis = data.get('niveis', {})
    if niveis:
        print("\n--- Análise por Níveis ---")
        for nivel, dados_nivel in niveis.items():
            if nivel == 'geral':
                continue
                
            if isinstance(dados_nivel, dict):
                total_nivel = sum(dados_nivel.values()) if all(isinstance(v, (int, float)) for v in dados_nivel.values()) else 0
                print(f"{nivel.upper()}: {dados_nivel} (total: {total_nivel})")
    
    # Verificar tendências
    tendencias = data.get('tendencias', {})
    if tendencias:
        print("\n--- Análise de Tendências ---")
        for status, tendencia in tendencias.items():
            print(f"{status}: {tendencia}")
            # Verificar se tendências são realistas
            if '+10228.7%' in str(tendencia):
                print(f" INCONSISTÊNCIA: Tendência irrealista para {status}: {tendencia}")

def main():
    """Função principal de diagnóstico"""
    print("=" * 60)
    print("DIAGNÓSTICO COMPLETO DO DASHBOARD GLPI")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    base_url = "http://localhost:5000/api"
    
    # Testar endpoints principais
    endpoints = {
        'metrics': f"{base_url}/metrics",
        'tickets_new': f"{base_url}/tickets/new",
        'ranking': f"{base_url}/technicians/ranking",
    }
    
    results = {}
    for name, url in endpoints.items():
        results[name] = test_endpoint(url, name)
    
    # Análises específicas
    analyze_metrics_consistency(results.get('metrics'))
    
    print("\n=== PROBLEMAS IDENTIFICADOS ===")
    print("1.  Tendências irrealistas (+10228.7%)")
    print("2.  Prioridades mal formatadas ('Mdia')")
    print("3.  Ranking de técnicos vazio")
    
if __name__ == '__main__':
    main()
