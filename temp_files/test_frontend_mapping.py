#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_frontend_mapping():
    """Testa se o mapeamento do frontend está funcionando corretamente"""
    try:
        print("=== TESTANDO MAPEAMENTO DO FRONTEND ===")
        
        # Fazer requisição para o backend
        response = requests.get('http://localhost:5000/api/technicians/ranking')
        
        if response.status_code == 200:
            data = response.json()
            technicians = data.get('data', [])
            
            print(f"✅ Backend retornou {len(technicians)} técnicos")
            print("\n=== PRIMEIROS 5 TÉCNICOS DO BACKEND ===")
            
            for i, tech in enumerate(technicians[:5], 1):
                print(f"{i}. ID: {tech.get('id')}")
                print(f"   Nome (campo 'nome'): {tech.get('nome')}")
                print(f"   Nível (campo 'nivel'): {tech.get('nivel')}")
                print(f"   Total: {tech.get('total')}")
                print(f"   Abertos: {tech.get('abertos')}")
                print(f"   Fechados: {tech.get('fechados')}")
                print(f"   Pendentes: {tech.get('pendentes')}")
                print()
            
            # Simular o mapeamento do frontend
            print("\n=== SIMULANDO MAPEAMENTO DO FRONTEND ===")
            
            mapped_data = []
            for index, tech in enumerate(technicians[:5]):
                mapped_tech = {
                    'id': tech.get('id'),
                    'name': tech.get('nome') or tech.get('name'),  # Usar 'nome' do backend, fallback para 'name'
                    'level': tech.get('nivel') or tech.get('level') or 'N1',  # Usar 'nivel' do backend
                    'total': tech.get('total') or tech.get('total_tickets') or 0,
                    'rank': index + 1,
                    'score': tech.get('score') or 0,
                    'tickets_abertos': tech.get('abertos') or tech.get('tickets_abertos') or 0,
                    'tickets_fechados': tech.get('fechados') or tech.get('tickets_fechados') or 0,
                    'tickets_pendentes': tech.get('pendentes') or tech.get('tickets_pendentes') or 0
                }
                mapped_data.append(mapped_tech)
                
                print(f"{mapped_tech['rank']}. {mapped_tech['name']} ({mapped_tech['level']}) - {mapped_tech['total']} tickets")
            
            print("\n✅ Mapeamento concluído com sucesso!")
            print(f"Todos os {len(mapped_data)} técnicos têm nomes válidos: {all(tech['name'] for tech in mapped_data)}")
            
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_frontend_mapping()