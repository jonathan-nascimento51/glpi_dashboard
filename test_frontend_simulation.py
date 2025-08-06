#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulação das chamadas que o frontend deveria estar fazendo
"""

import requests
import json
import time
from datetime import datetime, timedelta

def simulate_frontend_calls():
    """Simula as chamadas que o frontend deveria estar fazendo"""
    base_url = "http://localhost:5000/api"
    
    print("=== SIMULANDO CHAMADAS DO FRONTEND ===")
    
    # Simular carregamento inicial (sem filtro)
    print("\n1. Carregamento inicial (sem filtro):")
    try:
        response = requests.get(f"{base_url}/metrics")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total de tickets: {data.get('total', 'N/A')}")
            print(f"Filtro aplicado: {data.get('filtro_data', 'Nenhum')}")
    except Exception as e:
        print(f"Erro: {e}")
    
    time.sleep(1)
    
    # Simular clique no filtro "Últimos 7 dias"
    print("\n2. Simulando clique em 'Últimos 7 dias':")
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    try:
        params = {
            'start_date': start_date,
            'end_date': end_date
        }
        response = requests.get(f"{base_url}/metrics", params=params)
        print(f"URL completa: {response.url}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total de tickets (7 dias): {data.get('total', 'N/A')}")
            print(f"Filtro aplicado: {data.get('filtro_data', 'Nenhum')}")
    except Exception as e:
        print(f"Erro: {e}")
    
    time.sleep(1)
    
    # Simular clique no filtro "Últimos 30 dias"
    print("\n3. Simulando clique em 'Últimos 30 dias':")
    start_date_30 = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    try:
        params = {
            'start_date': start_date_30,
            'end_date': end_date
        }
        response = requests.get(f"{base_url}/metrics", params=params)
        print(f"URL completa: {response.url}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total de tickets (30 dias): {data.get('total', 'N/A')}")
            print(f"Filtro aplicado: {data.get('filtro_data', 'Nenhum')}")
    except Exception as e:
        print(f"Erro: {e}")
    
    time.sleep(1)
    
    # Simular filtro personalizado
    print("\n4. Simulando filtro personalizado (últimos 14 dias):")
    start_date_custom = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
    
    try:
        params = {
            'start_date': start_date_custom,
            'end_date': end_date
        }
        response = requests.get(f"{base_url}/metrics", params=params)
        print(f"URL completa: {response.url}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total de tickets (14 dias): {data.get('total', 'N/A')}")
            print(f"Filtro aplicado: {data.get('filtro_data', 'Nenhum')}")
    except Exception as e:
        print(f"Erro: {e}")
    
    print("\n=== INSTRUÇÕES PARA TESTE NO NAVEGADOR ===")
    print("1. Abra o DevTools (F12)")
    print("2. Vá para a aba Network")
    print("3. Clique em um filtro de data no dashboard")
    print("4. Verifique se aparece uma chamada para /api/metrics")
    print("5. Clique na chamada e verifique se tem start_date e end_date nos Query String Parameters")
    print("6. Se não aparecer, o problema está no frontend não enviando os parâmetros")
    
if __name__ == "__main__":
    simulate_frontend_calls()