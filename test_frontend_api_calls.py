#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para verificar se o frontend está enviando parâmetros de data para a API
"""

import requests
import json
from datetime import datetime, timedelta

def test_api_calls():
    """Testa as chamadas da API com diferentes parâmetros de data"""
    base_url = "http://localhost:5000/api"
    
    print("=== TESTANDO CHAMADAS DA API ===")
    
    # Teste 1: Chamada sem parâmetros de data
    print("\n1. Testando chamada sem parâmetros de data:")
    try:
        response = requests.get(f"{base_url}/metrics")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total de tickets: {data.get('total_tickets', 'N/A')}")
        else:
            print(f"Erro: {response.text}")
    except Exception as e:
        print(f"Erro na requisição: {e}")
    
    # Teste 2: Chamada com parâmetros de data (últimos 7 dias)
    print("\n2. Testando chamada com filtro de 7 dias:")
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    try:
        params = {
            'start_date': start_date,
            'end_date': end_date
        }
        response = requests.get(f"{base_url}/metrics", params=params)
        print(f"URL: {response.url}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total de tickets (7 dias): {data.get('total_tickets', 'N/A')}")
        else:
            print(f"Erro: {response.text}")
    except Exception as e:
        print(f"Erro na requisição: {e}")
    
    # Teste 3: Chamada com parâmetros de data (últimos 30 dias)
    print("\n3. Testando chamada com filtro de 30 dias:")
    start_date_30 = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    try:
        params = {
            'start_date': start_date_30,
            'end_date': end_date
        }
        response = requests.get(f"{base_url}/metrics", params=params)
        print(f"URL: {response.url}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total de tickets (30 dias): {data.get('total_tickets', 'N/A')}")
        else:
            print(f"Erro: {response.text}")
    except Exception as e:
        print(f"Erro na requisição: {e}")
    
    # Teste 4: Verificar se o frontend está fazendo chamadas corretas
    print("\n4. Instruções para testar no navegador:")
    print("- Abra o DevTools (F12)")
    print("- Vá para a aba Network")
    print("- Clique em um filtro de data no dashboard")
    print("- Verifique se aparece uma chamada para /api/metrics com start_date e end_date")
    print("- Se não aparecer, o problema está no frontend")
    
if __name__ == "__main__":
    test_api_calls()