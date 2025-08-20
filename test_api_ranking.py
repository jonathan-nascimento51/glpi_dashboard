#!/usr/bin/env python3
"""
Teste da API de Ranking de Técnicos
Testa os endpoints HTTP do sistema de ranking
"""

import requests
import json
from datetime import datetime, timedelta

def test_api_endpoints():
    """Testa todos os endpoints da API de ranking"""
    base_url = "http://localhost:5000/api"
    
    print("=== TESTE DA API DE RANKING DE TÉCNICOS ===")
    print(f"Base URL: {base_url}")
    print()
    
    # 1. Teste do endpoint de técnicos
    print("1. Testando endpoint /technicians")
    try:
        response = requests.get(f"{base_url}/technicians")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Técnicos encontrados: {len(data)}")
            if data:
                print(f"   Primeiro técnico: {data[0]['name']} (ID: {data[0]['id']})")
        else:
            print(f"   Erro: {response.text}")
    except Exception as e:
        print(f"   Erro na requisição: {e}")
    print()
    
    # 2. Teste do endpoint de técnicos com filtro de entidade
    print("2. Testando endpoint /technicians com filtro CAU (entity_id=1)")
    try:
        response = requests.get(f"{base_url}/technicians", params={"entity_id": 1})
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Técnicos CAU encontrados: {len(data)}")
            for tech in data[:3]:  # Mostra os 3 primeiros
                print(f"   - {tech['name']} (ID: {tech['id']})")
        else:
            print(f"   Erro: {response.text}")
    except Exception as e:
        print(f"   Erro na requisição: {e}")
    print()
    
    # 3. Teste do endpoint de ranking
    print("3. Testando endpoint /technicians/ranking")
    try:
        response = requests.get(f"{base_url}/technicians/ranking")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            response_data = response.json()
            if isinstance(response_data, dict) and 'data' in response_data:
                data = response_data['data']
                print(f"   Técnicos no ranking: {len(data)}")
                print("   Top 3 técnicos:")
                for i, tech in enumerate(data[:3], 1):
                    print(f"   {i}. {tech.get('name', 'N/A')} - Total: {tech.get('total', 0)}, Nível: {tech.get('level', 'N/A')}")
                print(f"   Tempo de resposta: {response_data.get('response_time_ms', 0):.2f}ms")
            else:
                print(f"   Formato inesperado da resposta: {type(response_data)}")
                print(f"   Dados: {response_data}")
        else:
            print(f"   Erro: {response.text}")
    except Exception as e:
        print(f"   Erro na requisição: {e}")
    print()
    
    # 4. Teste do endpoint de ranking com filtro de entidade
    print("4. Testando endpoint /technicians/ranking com filtro CAU (entity_id=1)")
    try:
        response = requests.get(f"{base_url}/technicians/ranking", params={"entity_id": 1})
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            response_data = response.json()
            if isinstance(response_data, dict) and 'data' in response_data:
                data = response_data['data']
                print(f"   Técnicos CAU no ranking: {len(data)}")
                print("   Top técnicos CAU:")
                for i, tech in enumerate(data, 1):
                    print(f"   {i}. {tech.get('name', 'N/A')} - Total: {tech.get('total', 0)}, Nível: {tech.get('level', 'N/A')}")
                print(f"   Tempo de resposta: {response_data.get('response_time_ms', 0):.2f}ms")
            else:
                print(f"   Formato inesperado da resposta: {type(response_data)}")
                print(f"   Dados: {response_data}")
        else:
            print(f"   Erro: {response.text}")
    except Exception as e:
        print(f"   Erro na requisição: {e}")
    print()
    
    # 5. Teste do endpoint de ranking com filtro de data
    print("5. Testando endpoint /technicians/ranking com filtro de data (últimos 30 dias)")
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        params = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        
        response = requests.get(f"{base_url}/technicians/ranking", params=params)
        print(f"   Status: {response.status_code}")
        print(f"   Período: {params['start_date']} a {params['end_date']}")
        
        if response.status_code == 200:
            data = response.json()
            response_data = response.json()
            if isinstance(response_data, dict) and 'data' in response_data:
                data = response_data['data']
                print(f"   Técnicos no ranking (30 dias): {len(data)}")
                print("   Top 3 técnicos (30 dias):")
                for i, tech in enumerate(data[:3], 1):
                    print(f"   {i}. {tech.get('name', 'N/A')} - Total: {tech.get('total', 0)}, Nível: {tech.get('level', 'N/A')}")
                print(f"   Tempo de resposta: {response_data.get('response_time_ms', 0):.2f}ms")
            else:
                print(f"   Formato inesperado da resposta: {type(response_data)}")
                print(f"   Dados: {response_data}")
        else:
            print(f"   Erro: {response.text}")
    except Exception as e:
        print(f"   Erro na requisição: {e}")
    print()
    
    # 6. Teste do endpoint de ranking com filtros combinados
    print("6. Testando endpoint /technicians/ranking com filtros combinados (CAU + 30 dias)")
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        params = {
            "entity_id": 1,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        
        response = requests.get(f"{base_url}/technicians/ranking", params=params)
        print(f"   Status: {response.status_code}")
        print(f"   Filtros: CAU (entity_id=1) + Período: {params['start_date']} a {params['end_date']}")
        
        if response.status_code == 200:
            data = response.json()
            response_data = response.json()
            if isinstance(response_data, dict) and 'data' in response_data:
                data = response_data['data']
                print(f"   Técnicos CAU no ranking (30 dias): {len(data)}")
                print("   Técnicos CAU (30 dias):")
                for i, tech in enumerate(data, 1):
                    print(f"   {i}. {tech.get('name', 'N/A')} - Total: {tech.get('total', 0)}, Nível: {tech.get('level', 'N/A')}")
                print(f"   Tempo de resposta: {response_data.get('response_time_ms', 0):.2f}ms")
            else:
                print(f"   Formato inesperado da resposta: {type(response_data)}")
                print(f"   Dados: {response_data}")
        else:
            print(f"   Erro: {response.text}")
    except Exception as e:
        print(f"   Erro na requisição: {e}")
    print()
    
    print("=== TESTE DA API CONCLUÍDO ===")

if __name__ == "__main__":
    test_api_endpoints()