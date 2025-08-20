#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debugar os dados que chegam no frontend
"""

import requests
import json

def test_api_endpoints():
    """Testa os endpoints da API para ver a estrutura dos dados"""
    base_url = "http://localhost:5000/api"
    
    print("🔍 TESTANDO ENDPOINTS DA API")
    print("=" * 50)
    
    # 1. Testar ranking de técnicos
    print("\n1. Testando /technicians/ranking")
    try:
        response = requests.get(f"{base_url}/technicians/ranking")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Tipo de resposta: {type(data)}")
            print(f"Chaves da resposta: {list(data.keys()) if isinstance(data, dict) else 'Lista'}")
            
            if isinstance(data, dict) and 'data' in data:
                ranking_data = data['data']
                print(f"Número de técnicos: {len(ranking_data)}")
                
                if ranking_data:
                    print("\nPrimeiro técnico:")
                    first_tech = ranking_data[0]
                    print(json.dumps(first_tech, indent=2, ensure_ascii=False))
                    
                    print("\nTodos os técnicos (resumo):")
                    for i, tech in enumerate(ranking_data[:10]):
                        name = tech.get('name', 'N/A')
                        total = tech.get('total', 0)
                        level = tech.get('level', 'N/A')
                        print(f"  {i+1}. {name}: {total} tickets (Nível: {level})")
            else:
                print("Dados não encontrados ou formato inesperado")
                print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"Erro: {response.text}")
    except Exception as e:
        print(f"Erro na requisição: {e}")
    
    # 2. Testar métricas do dashboard
    print("\n2. Testando /dashboard/metrics")
    try:
        response = requests.get(f"{base_url}/dashboard/metrics")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Tipo de resposta: {type(data)}")
            print(f"Chaves da resposta: {list(data.keys()) if isinstance(data, dict) else 'Lista'}")
            
            # Verificar se há dados de ranking nas métricas
            if isinstance(data, dict):
                if 'technicianRanking' in data:
                    print(f"TechnicianRanking encontrado: {len(data['technicianRanking'])} técnicos")
                    if data['technicianRanking']:
                        print("Primeiro técnico do ranking nas métricas:")
                        print(json.dumps(data['technicianRanking'][0], indent=2, ensure_ascii=False))
                else:
                    print("TechnicianRanking não encontrado nas métricas")
        else:
            print(f"Erro: {response.text}")
    except Exception as e:
        print(f"Erro na requisição: {e}")

if __name__ == "__main__":
    test_api_endpoints()