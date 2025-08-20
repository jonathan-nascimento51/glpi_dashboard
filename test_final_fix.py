#!/usr/bin/env python3
"""
Teste final para verificar se a correção do mapeamento de campos resolveu
o problema de exibição dos tickets no frontend.
"""

import requests
import json
from datetime import datetime, timedelta

def test_ranking_endpoints():
    """Testa ambos os endpoints de ranking para verificar os campos retornados."""
    base_url = "http://localhost:5000/api"
    
    print("🔍 Testando endpoints de ranking após correção...\n")
    
    # Teste 1: Ranking sem filtros (deve retornar total_tickets)
    print("1. Testando ranking SEM filtros:")
    try:
        response = requests.get(f"{base_url}/technicians/ranking", timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                ranking = data['data']
                print(f"   ✅ Status: {response.status_code}")
                print(f"   📊 Técnicos retornados: {len(ranking)}")
                if ranking:
                    first_tech = ranking[0]
                    print(f"   👤 Primeiro técnico: {first_tech.get('name', 'N/A')}")
                    print(f"   🎯 Campo 'total': {'✅ PRESENTE' if 'total' in first_tech else '❌ AUSENTE'}")
                    print(f"   🎯 Campo 'total_tickets': {'✅ PRESENTE' if 'total_tickets' in first_tech else '❌ AUSENTE'}")
                    if 'total' in first_tech:
                        print(f"   📈 Valor 'total': {first_tech['total']}")
                    if 'total_tickets' in first_tech:
                        print(f"   📈 Valor 'total_tickets': {first_tech['total_tickets']}")
            else:
                print(f"   ❌ Resposta sem dados válidos")
        else:
            print(f"   ❌ Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Teste 2: Ranking com filtros (deve retornar total)
    print("2. Testando ranking COM filtros de data:")
    try:
        # Filtro dos últimos 30 dias
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        params = {
            'start_date': start_date,
            'end_date': end_date
        }
        
        response = requests.get(f"{base_url}/technicians/ranking", params=params, timeout=60)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                ranking = data['data']
                print(f"   ✅ Status: {response.status_code}")
                print(f"   📊 Técnicos retornados: {len(ranking)}")
                print(f"   📅 Período: {start_date} a {end_date}")
                if ranking:
                    first_tech = ranking[0]
                    print(f"   👤 Primeiro técnico: {first_tech.get('name', 'N/A')}")
                    print(f"   🎯 Campo 'total': {'✅ PRESENTE' if 'total' in first_tech else '❌ AUSENTE'}")
                    print(f"   🎯 Campo 'total_tickets': {'✅ PRESENTE' if 'total_tickets' in first_tech else '❌ AUSENTE'}")
                    if 'total' in first_tech:
                        print(f"   📈 Valor 'total': {first_tech['total']}")
                    if 'total_tickets' in first_tech:
                        print(f"   📈 Valor 'total_tickets': {first_tech['total_tickets']}")
            else:
                print(f"   ❌ Resposta sem dados válidos")
        else:
            print(f"   ❌ Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Teste 3: Verificar se o frontend pode processar ambos os casos
    print("3. Resumo da correção aplicada:")
    print("   🔧 ModernDashboard.tsx: Alterado para 'tech.total || tech.total_tickets || 0'")
    print("   🔧 ProfessionalDashboard.tsx: Alterado para 'tech.total || tech.total_tickets || 0'")
    print("   ✅ Agora o frontend prioriza 'total' (com filtros) e usa 'total_tickets' como fallback (sem filtros)")
    print("   🎯 Isso deve resolver o problema de exibição de '0' nos tickets")

if __name__ == "__main__":
    test_ranking_endpoints()