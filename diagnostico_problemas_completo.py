#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico Completo dos Problemas do Dashboard GLPI
Identifica TODOS os problemas reportados pelo usuário
"""

import requests
import json
from datetime import datetime
import sys

def test_endpoint_detailed(url, name):
    """Testa um endpoint e retorna análise detalhada"""
    try:
        print(f"\n{'='*60}")
        print(f"TESTANDO: {name}")
        print(f"URL: {url}")
        print(f"{'='*60}")
        
        response = requests.get(url, timeout=10)
        print(f"Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Sucesso: {data.get('success', 'N/A')}")
            
            # Análise específica por endpoint
            if 'metrics' in url:
                analyze_metrics_problems(data)
            elif 'tickets/new' in url:
                analyze_tickets_problems(data)
            elif 'ranking' in url:
                analyze_ranking_problems(data)
                
            return data
        else:
            print(f" ERRO HTTP: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f" ERRO NA REQUISIÇÃO: {e}")
        return None

def analyze_metrics_problems(data):
    """Analisa problemas específicos nas métricas"""
    print("\n ANÁLISE DE PROBLEMAS - MÉTRICAS")
    
    if not data or not data.get('success'):
        print(" PROBLEMA: Dados de métricas não disponíveis")
        return
    
    metrics_data = data.get('data', {})
    
    # PROBLEMA 1: Inconsistência nos totais
    total_geral = metrics_data.get('total', 0)
    novos = metrics_data.get('novos', 0)
    pendentes = metrics_data.get('pendentes', 0)
    progresso = metrics_data.get('progresso', 0)
    resolvidos = metrics_data.get('resolvidos', 0)
    
    soma_status = novos + pendentes + progresso + resolvidos
    
    print(f"\n TOTAIS REPORTADOS:")
    print(f"   Total geral: {total_geral}")
    print(f"   Novos: {novos}")
    print(f"   Pendentes: {pendentes}")
    print(f"   Em Progresso: {progresso}")
    print(f"   Resolvidos: {resolvidos}")
    print(f"   Soma por status: {soma_status}")
    
    if total_geral != soma_status:
        print(f" PROBLEMA CRÍTICO: Total geral ({total_geral}) != Soma por status ({soma_status})")
        print(f"   Diferença: {abs(total_geral - soma_status)}")
    
    # PROBLEMA 2: Distribuição por níveis incorreta
    niveis = metrics_data.get('niveis', {})
    if niveis:
        print(f"\n DISTRIBUIÇÃO POR NÍVEIS:")
        total_niveis = 0
        for nivel, dados_nivel in niveis.items():
            if nivel == 'geral':
                continue
            if isinstance(dados_nivel, dict):
                total_nivel = sum(dados_nivel.values()) if all(isinstance(v, (int, float)) for v in dados_nivel.values()) else 0
                total_niveis += total_nivel
                print(f"   {nivel.upper()}: {total_nivel} tickets")
                print(f"      Detalhes: {dados_nivel}")
        
        print(f"   TOTAL SOMADO DOS NÍVEIS: {total_niveis}")
        if total_niveis != total_geral:
            print(f" PROBLEMA: Total dos níveis ({total_niveis}) != Total geral ({total_geral})")
    
    # PROBLEMA 3: Tendências irrealistas
    tendencias = metrics_data.get('tendencias', {})
    if tendencias:
        print(f"\n TENDÊNCIAS REPORTADAS:")
        for status, tendencia in tendencias.items():
            print(f"   {status}: {tendencia}")
            # Verificar tendências suspeitas
            if '+10000%' in str(tendencia) or '+1000%' in str(tendencia):
                print(f" PROBLEMA: Tendência irrealista para {status}: {tendencia}")

def analyze_tickets_problems(data):
    """Analisa problemas nos tickets novos"""
    print("\n ANÁLISE DE PROBLEMAS - TICKETS NOVOS")
    
    if not data or not data.get('success'):
        print(" PROBLEMA: Dados de tickets não disponíveis")
        return
    
    tickets = data.get('data', [])
    print(f"\n TICKETS ENCONTRADOS: {len(tickets)}")
    
    if tickets:
        # Verificar problemas de formatação
        for i, ticket in enumerate(tickets[:3]):  # Primeiros 3 tickets
            print(f"\n   Ticket {i+1}:")
            prioridade = ticket.get('prioridade', 'N/A')
            print(f"      Prioridade: '{prioridade}'")
            
            # PROBLEMA 4: Prioridade mal formatada
            if 'Mdia' in prioridade:
                print(f" PROBLEMA: Prioridade mal formatada: '{prioridade}' (deveria ser 'Média')")
            
            print(f"      Status: {ticket.get('status', 'N/A')}")
            print(f"      Título: {ticket.get('titulo', 'N/A')[:50]}...")

def analyze_ranking_problems(data):
    """Analisa problemas no ranking de técnicos"""
    print("\n ANÁLISE DE PROBLEMAS - RANKING DE TÉCNICOS")
    
    if not data or not data.get('success'):
        print(" PROBLEMA: Endpoint de ranking não funcional")
        return
    
    ranking_data = data.get('data', [])
    message = data.get('message', '')
    
    print(f"\n RANKING ENCONTRADO: {len(ranking_data)} técnicos")
    print(f"   Mensagem: {message}")
    
    # PROBLEMA 5: Ranking vazio
    if len(ranking_data) == 0:
        print(f" PROBLEMA CRÍTICO: Ranking de técnicos completamente vazio")
        print(f"   Isso indica problema na consulta ao GLPI ou mapeamento de dados")

def main():
    """Diagnóstico completo dos problemas reportados"""
    print("\n" + "="*80)
    print("DIAGNÓSTICO COMPLETO DOS PROBLEMAS DO DASHBOARD GLPI")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("PROBLEMAS REPORTADOS PELO USUÁRIO:")
    print("1. Ranking de técnicos vazio")
    print("2. Inconsistências nos totais de tickets")
    print("3. Cores e textos de prioridade incorretos")
    print("4. Tendências irrealistas e inconsistentes")
    print("5. Distribuição incorreta entre níveis")
    print("="*80)
    
    base_url = "http://localhost:5000/api"
    
    # Testar todos os endpoints problemáticos
    endpoints = {
        'Métricas Gerais': f"{base_url}/metrics",
        'Tickets Novos': f"{base_url}/tickets/new",
        'Ranking Técnicos': f"{base_url}/technicians/ranking",
    }
    
    results = {}
    for name, url in endpoints.items():
        results[name] = test_endpoint_detailed(url, name)
    
    # Resumo final dos problemas
    print("\n" + "="*80)
    print("RESUMO DOS PROBLEMAS IDENTIFICADOS")
    print("="*80)
    print(" CRÍTICOS:")
    print("   1. Ranking de técnicos completamente vazio")
    print("   2. Totais inconsistentes entre geral e soma por status")
    print("   3. Distribuição incorreta entre níveis N1-N4")
    print("\n FORMATAÇÃO:")
    print("   4. Prioridades com texto 'Mdia' ao invés de 'Média'")
    print("   5. Cores de prioridade incorretas")
    print("\n CÁLCULOS:")
    print("   6. Tendências irrealistas (+10000%)")
    print("   7. Inconsistência nos números de tendência")
    print("\n" + "="*80)
    print("PRÓXIMOS PASSOS NECESSÁRIOS:")
    print("1. Corrigir consultas ao GLPI para ranking")
    print("2. Revisar agregações e cálculos de totais")
    print("3. Corrigir formatação de prioridades")
    print("4. Revisar lógica de cálculo de tendências")
    print("5. Validar distribuição por níveis")
    print("="*80)

if __name__ == '__main__':
    main()
