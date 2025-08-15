#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar se há dados duplicados na API que podem causar chaves duplicadas no React
"""

import requests
import json
from collections import Counter
from datetime import datetime

def check_api_duplicates():
    """Verifica se há IDs duplicados nos dados da API"""
    base_url = "http://localhost:5000/api"
    
    print("🔍 Verificando duplicatas na API...\n")
    
    # Endpoints para verificar
    endpoints = [
        "/metrics",
        "/technicians/ranking",
        "/tickets/new"
    ]
    
    for endpoint in endpoints:
        print(f"📡 Verificando endpoint: {endpoint}")
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                check_endpoint_duplicates(endpoint, data)
            else:
                print(f"❌ Erro {response.status_code} ao acessar {endpoint}")
        except Exception as e:
            print(f"❌ Erro ao acessar {endpoint}: {e}")
        print()

def check_endpoint_duplicates(endpoint, data):
    """Verifica duplicatas em um endpoint específico"""
    
    if endpoint == "/metrics":
        check_dashboard_duplicates(data)
    elif endpoint == "/technicians/ranking":
        check_technician_ranking_duplicates(data)
    elif endpoint == "/tickets/new":
        check_new_tickets_duplicates(data)

def check_dashboard_duplicates(data):
    """Verifica duplicatas nos dados do dashboard"""
    print("   📊 Verificando dados do dashboard...")
    
    # Verificar se há níveis duplicados
    if 'niveis' in data:
        niveis = list(data['niveis'].keys())
        nivel_counts = Counter(niveis)
        duplicates = {k: v for k, v in nivel_counts.items() if v > 1}
        
        if duplicates:
            print(f"   ⚠️  Níveis duplicados encontrados: {duplicates}")
        else:
            print(f"   ✅ Níveis únicos: {len(niveis)} níveis")
    
    # Verificar estrutura das métricas
    if 'metrics' in data:
        print(f"   📈 Métricas disponíveis: {list(data['metrics'].keys())}")
    
    print(f"   📋 Estrutura completa: {list(data.keys())}")

def check_technician_ranking_duplicates(data):
    """Verifica duplicatas no ranking de técnicos"""
    print("   👥 Verificando ranking de técnicos...")
    
    # Verificar se os dados estáo no formato esperado
    if isinstance(data, dict) and 'data' in data:
        technicians = data['data']
    elif isinstance(data, list):
        technicians = data
    else:
        print(f"   ❌ Formato inesperado: {type(data)}")
        return
    
    if not isinstance(technicians, list):
        print(f"   ❌ Lista de técnicos em formato inesperado: {type(technicians)}")
        return
    
    print(f"   📊 Total de técnicos: {len(technicians)}")
    
    # Verificar IDs duplicados
    ids = [tech.get('id') for tech in technicians if tech.get('id')]
    id_counts = Counter(ids)
    duplicates = {k: v for k, v in id_counts.items() if v > 1}
    
    if duplicates:
        print(f"   ⚠️  IDs duplicados encontrados: {duplicates}")
        # Mostrar detalhes dos técnicos duplicados
        for dup_id, count in duplicates.items():
            techs_with_id = [tech for tech in technicians if tech.get('id') == dup_id]
            print(f"      ID {dup_id} ({count}x):")
            for tech in techs_with_id:
                print(f"        - {tech.get('name', 'N/A')} (Level: {tech.get('level', 'N/A')})")
    else:
        print(f"   ✅ IDs únicos: {len(ids)} técnicos")
    
    # Verificar nomes duplicados
    names = [tech.get('name') for tech in technicians if tech.get('name')]
    name_counts = Counter(names)
    name_duplicates = {k: v for k, v in name_counts.items() if v > 1}
    
    if name_duplicates:
        print(f"   ⚠️  Nomes duplicados encontrados: {name_duplicates}")
    else:
        print(f"   ✅ Nomes únicos: {len(set(names))} nomes únicos de {len(names)} técnicos")

def check_new_tickets_duplicates(data):
    """Verifica duplicatas nos tickets novos"""
    print("   🎫 Verificando tickets novos...")
    
    # Verificar se os dados estáo no formato esperado
    if isinstance(data, dict) and 'data' in data:
        tickets = data['data']
    elif isinstance(data, list):
        tickets = data
    else:
        print(f"   ❌ Formato inesperado: {type(data)}")
        return
    
    if not isinstance(tickets, list):
        print(f"   ❌ Lista de tickets em formato inesperado: {type(tickets)}")
        return
    
    print(f"   📊 Total de tickets: {len(tickets)}")
    
    # Verificar IDs duplicados
    ids = [ticket.get('id') for ticket in tickets if ticket.get('id')]
    id_counts = Counter(ids)
    duplicates = {k: v for k, v in id_counts.items() if v > 1}
    
    if duplicates:
        print(f"   ⚠️  IDs duplicados encontrados: {duplicates}")
        for dup_id, count in duplicates.items():
            tickets_with_id = [t for t in tickets if t.get('id') == dup_id]
            print(f"      ID {dup_id} ({count}x):")
            for ticket in tickets_with_id:
                print(f"        - {ticket.get('title', 'N/A')[:50]}...")
    else:
        print(f"   ✅ IDs únicos: {len(ids)} tickets")
    
    # Verificar títulos duplicados
    titles = [ticket.get('title') for ticket in tickets if ticket.get('title')]
    title_counts = Counter(titles)
    title_duplicates = {k: v for k, v in title_counts.items() if v > 1}
    
    if title_duplicates:
        print(f"   ⚠️  Títulos duplicados encontrados: {len(title_duplicates)} duplicatas")
        for title, count in list(title_duplicates.items())[:3]:  # Mostrar apenas os primeiros 3
            print(f"      '{title[:50]}...' ({count}x)")
    else:
        print(f"   ✅ Títulos únicos: {len(set(titles))} títulos únicos de {len(titles)} tickets")

def check_react_key_patterns():
    """Verifica padrões que podem causar chaves duplicadas no React"""
    print("\n🔧 Verificando padrões que podem causar chaves duplicadas no React...\n")
    
    patterns_to_check = [
        {
            'name': 'Técnicos com mesmo ID',
            'description': 'Técnicos diferentes com o mesmo ID podem causar key={technician.id} duplicadas'
        },
        {
            'name': 'Tickets com mesmo ID',
            'description': 'Tickets diferentes com o mesmo ID podem causar key={ticket.id} duplicadas'
        },
        {
            'name': 'Níveis duplicados',
            'description': 'Níveis duplicados podem causar key={level} duplicadas'
        },
        {
            'name': 'Status duplicados',
            'description': 'Status duplicados podem causar key={status} duplicadas'
        }
    ]
    
    for pattern in patterns_to_check:
        print(f"🔍 {pattern['name']}:")
        print(f"   {pattern['description']}")
        print()

def main():
    """Funçáo principal"""
    print("🚀 Iniciando verificaçáo de chaves duplicadas...")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        check_api_duplicates()
        check_react_key_patterns()
        
        print("\n📋 RESUMO:")
        print("✅ Verificaçáo concluída")
        print("💡 Se foram encontradas duplicatas, elas podem estar causando o warning do React")
        print("🔧 Soluções possíveis:")
        print("   1. Garantir IDs únicos na API")
        print("   2. Usar chaves compostas: key={`${item.id}-${index}`}")
        print("   3. Usar índices como fallback: key={item.id || index}")
        
    except Exception as e:
        print(f"❌ Erro durante a verificaçáo: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
