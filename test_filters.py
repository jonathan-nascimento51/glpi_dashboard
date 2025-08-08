#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime, timedelta

def test_ranking_api():
    """Testa a API de ranking de técnicos com diferentes filtros"""
    base_url = "http://localhost:5000/api/technicians/ranking"
    
    print("=== Teste da API de Ranking de Técnicos ===")
    print()
    
    # Teste 1: Ranking sem filtros
    print("1. Testando ranking sem filtros (limit=3)...")
    try:
        response = requests.get(f"{base_url}?limit=3")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Sucesso: {len(data.get('data', []))} técnicos retornados")
            print(f"   ✓ Tempo de resposta: {data.get('response_time_ms', 0):.2f}ms")
            if data.get('data'):
                top_tech = data['data'][0]
                print(f"   ✓ Top técnico: {top_tech.get('name')} ({top_tech.get('total')} tickets)")
        else:
            print(f"   ✗ Erro: Status {response.status_code}")
    except Exception as e:
        print(f"   ✗ Erro: {e}")
    print()
    
    # Teste 2: Ranking com filtros de data
    print("2. Testando ranking com filtros de data (últimos 30 dias)...")
    try:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        response = requests.get(f"{base_url}?start_date={start_date}&end_date={end_date}&limit=3")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Sucesso: {len(data.get('data', []))} técnicos retornados")
            print(f"   ✓ Período: {start_date} até {end_date}")
            print(f"   ✓ Tempo de resposta: {data.get('response_time_ms', 0):.2f}ms")
            if data.get('data'):
                top_tech = data['data'][0]
                print(f"   ✓ Top técnico no período: {top_tech.get('name')} ({top_tech.get('ticket_count')} tickets)")
        else:
            print(f"   ✗ Erro: Status {response.status_code}")
    except Exception as e:
        print(f"   ✗ Erro: {e}")
    print()
    
    # Teste 3: Ranking com período específico (julho 2025)
    print("3. Testando ranking para julho de 2025...")
    try:
        response = requests.get(f"{base_url}?start_date=2025-07-01&end_date=2025-07-31&limit=3")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Sucesso: {len(data.get('data', []))} técnicos retornados")
            print(f"   ✓ Período: julho de 2025")
            print(f"   ✓ Tempo de resposta: {data.get('response_time_ms', 0):.2f}ms")
            if data.get('data'):
                for i, tech in enumerate(data['data'], 1):
                    print(f"   ✓ {i}º lugar: {tech.get('name')} ({tech.get('ticket_count')} tickets)")
        else:
            print(f"   ✗ Erro: Status {response.status_code}")
    except Exception as e:
        print(f"   ✗ Erro: {e}")
    print()
    
    print("=== Teste Concluído ===")

if __name__ == "__main__":
    test_ranking_api()