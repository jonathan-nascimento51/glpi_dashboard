#!/usr/bin/env python3
"""
Script para testar a API de ranking de técnicos e verificar
quantos técnicos estão sendo retornados por nível.
"""

import requests
import json
from collections import Counter

def test_ranking_api():
    """Testa a API de ranking de técnicos"""
    
    base_url = "http://localhost:5000"
    
    print("🔍 Testando API de ranking de técnicos...")
    print("="*60)
    
    # Teste 1: Ranking sem filtros
    print("\n📊 TESTE 1: Ranking sem filtros")
    try:
        response = requests.get(f"{base_url}/api/technicians/ranking")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                technicians = data['data']
                print(f"✅ Total de técnicos retornados: {len(technicians)}")
                
                # Contar por nível
                levels = [tech.get('level', 'Sem nível') for tech in technicians]
                level_counts = Counter(levels)
                
                print("\n📈 Distribuição por nível:")
                for level, count in sorted(level_counts.items()):
                    print(f"  {level}: {count} técnicos")
                
                # Mostrar alguns exemplos
                print("\n👥 Primeiros 10 técnicos:")
                for i, tech in enumerate(technicians[:10]):
                    print(f"  {i+1}. {tech.get('name', 'N/A')} - {tech.get('level', 'N/A')} - {tech.get('total', 0)} tickets")
                    
            else:
                print(f"❌ Resposta sem dados: {data}")
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 2: Ranking com filtro de nível N1
    print("\n📊 TESTE 2: Ranking filtrado por nível N1")
    try:
        response = requests.get(f"{base_url}/api/technicians/ranking?level=N1")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                technicians = data['data']
                print(f"✅ Técnicos N1 retornados: {len(technicians)}")
                for tech in technicians:
                    print(f"  - {tech.get('name', 'N/A')} - {tech.get('total', 0)} tickets")
            else:
                print(f"❌ Resposta sem dados: {data}")
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 3: Ranking com filtro de nível N4
    print("\n📊 TESTE 3: Ranking filtrado por nível N4")
    try:
        response = requests.get(f"{base_url}/api/technicians/ranking?level=N4")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                technicians = data['data']
                print(f"✅ Técnicos N4 retornados: {len(technicians)}")
                for tech in technicians:
                    print(f"  - {tech.get('name', 'N/A')} - {tech.get('total', 0)} tickets")
            else:
                print(f"❌ Resposta sem dados: {data}")
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 4: Verificar se há filtro padrão sendo aplicado
    print("\n📊 TESTE 4: Verificando filtros padrão")
    try:
        response = requests.get(f"{base_url}/api/technicians/ranking?limit=100")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                technicians = data['data']
                print(f"✅ Total com limite 100: {len(technicians)}")
                
                # Verificar se há técnicos com 0 tickets
                zero_tickets = [tech for tech in technicians if tech.get('total', 0) == 0]
                print(f"📊 Técnicos com 0 tickets: {len(zero_tickets)}")
                
                # Verificar distribuição por nível novamente
                levels = [tech.get('level', 'Sem nível') for tech in technicians]
                level_counts = Counter(levels)
                
                print("\n📈 Distribuição por nível (limite 100):")
                for level, count in sorted(level_counts.items()):
                    print(f"  {level}: {count} técnicos")
                    
            else:
                print(f"❌ Resposta sem dados: {data}")
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    print("\n" + "="*60)
    print("🏁 Testes concluídos!")

if __name__ == "__main__":
    test_ranking_api()