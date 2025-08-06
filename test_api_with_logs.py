#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste específico para verificar se a API está recebendo os parâmetros de data
"""

import requests
import json
import time
from datetime import datetime, timedelta

def test_api_with_detailed_logs():
    """Testa a API com logs detalhados"""
    base_url = "http://localhost:5000/api"
    
    print("=== TESTE DETALHADO DA API COM LOGS ===")
    print(f"Testando em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Teste 1: Sem filtro
    print("\n1. TESTE SEM FILTRO:")
    try:
        response = requests.get(f"{base_url}/metrics")
        print(f"URL: {response.url}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            response_data = response.json()
            data = response_data.get('data', {})
            print(f"Total: {data.get('total', 'N/A')}")
            print(f"Filtro aplicado: {data.get('filtro_data', 'Nenhum')}")
        print("Aguarde 2 segundos para verificar logs no backend...")
        time.sleep(2)
    except Exception as e:
        print(f"Erro: {e}")
    
    # Teste 2: Com filtro de 7 dias
    print("\n2. TESTE COM FILTRO DE 7 DIAS:")
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    print(f"Parâmetros que serão enviados:")
    print(f"  start_date: {start_date}")
    print(f"  end_date: {end_date}")
    
    try:
        params = {
            'start_date': start_date,
            'end_date': end_date
        }
        response = requests.get(f"{base_url}/metrics", params=params)
        print(f"URL completa: {response.url}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            response_data = response.json()
            data = response_data.get('data', {})
            print(f"Total: {data.get('total', 'N/A')}")
            print(f"Filtro aplicado: {data.get('filtro_data', 'Nenhum')}")
            if 'filtro_data' in data:
                print(f"  Data início: {data['filtro_data'].get('data_inicio', 'N/A')}")
                print(f"  Data fim: {data['filtro_data'].get('data_fim', 'N/A')}")
        print("Aguarde 2 segundos para verificar logs no backend...")
        time.sleep(2)
    except Exception as e:
        print(f"Erro: {e}")
    
    # Teste 3: Com filtro de 30 dias
    print("\n3. TESTE COM FILTRO DE 30 DIAS:")
    start_date_30 = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"Parâmetros que serão enviados:")
    print(f"  start_date: {start_date_30}")
    print(f"  end_date: {end_date}")
    
    try:
        params = {
            'start_date': start_date_30,
            'end_date': end_date
        }
        response = requests.get(f"{base_url}/metrics", params=params)
        print(f"URL completa: {response.url}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            response_data = response.json()
            data = response_data.get('data', {})
            print(f"Total: {data.get('total', 'N/A')}")
            print(f"Filtro aplicado: {data.get('filtro_data', 'Nenhum')}")
            if 'filtro_data' in data:
                print(f"  Data início: {data['filtro_data'].get('data_inicio', 'N/A')}")
                print(f"  Data fim: {data['filtro_data'].get('data_fim', 'N/A')}")
        print("Aguarde 2 segundos para verificar logs no backend...")
        time.sleep(2)
    except Exception as e:
        print(f"Erro: {e}")
    
    print("\n=== CONCLUSÃO ===")
    print("Se você vê 'Filtro aplicado: {...}' nos testes 2 e 3, a API está funcionando.")
    print("Se você vê 'Filtro aplicado: Nenhum' em todos os testes, há um problema na API.")
    print("Verifique os logs do backend para mais detalhes.")
    
if __name__ == "__main__":
    test_api_with_detailed_logs()