#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug da resposta da API para entender o que está sendo retornado
"""

import requests
import json
from datetime import datetime, timedelta

def debug_api_response():
    """Debug detalhado da resposta da API"""
    base_url = "http://localhost:5000/api"
    
    print("=== DEBUG DA RESPOSTA DA API ===")
    
    # Teste com filtro de 7 dias
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    print(f"\nTestando com filtro:")
    print(f"start_date: {start_date}")
    print(f"end_date: {end_date}")
    
    try:
        params = {
            'start_date': start_date,
            'end_date': end_date
        }
        response = requests.get(f"{base_url}/metrics", params=params)
        print(f"\nURL: {response.url}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nResposta completa:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Verificar campos específicos
            print(f"\n=== CAMPOS ESPECÍFICOS ===")
            print(f"total_tickets: {data.get('total_tickets')}")
            print(f"tickets_by_status: {data.get('tickets_by_status')}")
            print(f"tickets_by_priority: {data.get('tickets_by_priority')}")
            print(f"tickets_by_category: {data.get('tickets_by_category')}")
            print(f"average_resolution_time: {data.get('average_resolution_time')}")
            
        else:
            print(f"Erro: {response.text}")
            
    except Exception as e:
        print(f"Erro na requisição: {e}")
    
    # Teste sem filtro para comparação
    print(f"\n\n=== TESTE SEM FILTRO PARA COMPARAÇÃO ===")
    try:
        response = requests.get(f"{base_url}/metrics")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nResposta sem filtro:")
            print(f"total_tickets: {data.get('total_tickets')}")
            print(f"tickets_by_status: {data.get('tickets_by_status')}")
            
        else:
            print(f"Erro: {response.text}")
            
    except Exception as e:
        print(f"Erro na requisição: {e}")

if __name__ == "__main__":
    debug_api_response()