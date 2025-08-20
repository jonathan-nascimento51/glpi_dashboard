#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar se a correção do mapeamento funcionou
"""

import requests
import json

def test_ranking_fix():
    """Testa se o endpoint de ranking está retornando dados corretos"""
    base_url = "http://localhost:5000/api"
    
    print("🔧 TESTANDO CORREÇÃO DO RANKING")
    print("=" * 50)
    
    try:
        response = requests.get(f"{base_url}/technicians/ranking")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, dict) and 'data' in data:
                ranking_data = data['data']
                print(f"✅ Número de técnicos: {len(ranking_data)}")
                
                if ranking_data:
                    print("\n📊 DADOS DOS TÉCNICOS:")
                    print("-" * 80)
                    
                    for i, tech in enumerate(ranking_data[:10]):
                        name = tech.get('name', 'N/A')
                        total_tickets = tech.get('total_tickets', 0)
                        total = tech.get('total', 0)
                        level = tech.get('level', 'N/A')
                        rank = tech.get('rank', 0)
                        
                        print(f"{i+1:2d}. {name:<35} | Tickets: {total_tickets:4d} | Total: {total:4d} | Nível: {level} | Rank: {rank}")
                    
                    # Verificar se há técnicos com tickets > 0
                    techs_with_tickets = [t for t in ranking_data if t.get('total_tickets', 0) > 0]
                    print(f"\n✅ Técnicos com tickets > 0: {len(techs_with_tickets)}")
                    
                    if techs_with_tickets:
                        print("\n🎯 TOP 3 TÉCNICOS COM MAIS TICKETS:")
                        top_3 = sorted(techs_with_tickets, key=lambda x: x.get('total_tickets', 0), reverse=True)[:3]
                        for i, tech in enumerate(top_3):
                            name = tech.get('name', 'N/A')
                            tickets = tech.get('total_tickets', 0)
                            print(f"  {i+1}. {name}: {tickets} tickets")
                    else:
                        print("❌ Nenhum técnico com tickets > 0 encontrado")
                        
                else:
                    print("❌ Nenhum dado de ranking encontrado")
            else:
                print("❌ Formato de resposta inesperado")
                print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_ranking_fix()