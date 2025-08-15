#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste específico para técnicos conhecidos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.glpi_service import GLPIService

def test_specific_technicians():
    """Testa técnicos específicos que sabemos que existem"""
    print("🚀 Iniciando teste de técnicos específicos...")
    
    service = GLPIService()
    
    # Técnicos que sabemos que são N4
    known_n4_techs = ['anderson-oliveira', 'wagner-mengue', 'silvio-valim']
    
    print("\n📊 Testando determinação de nível para técnicos conhecidos...")
    for tech_id in known_n4_techs:
        tech_name = f"Técnico {tech_id}"
        level = service._get_technician_level_by_name(tech_name)
        print(f"  {tech_name}: {level}")
    
    print("\n📊 Testando ranking sem filtro (limite 10)...")
    ranking_no_filter = service.get_technician_ranking_with_filters(limit=10)
    
    if ranking_no_filter and 'technicians' in ranking_no_filter:
        techs = ranking_no_filter['technicians']
        print(f"✅ Encontrados {len(techs)} técnicos sem filtro:")
        
        n4_found = []
        for tech in techs:
            if tech.get('level') == 'N4':
                n4_found.append(tech['name'])
            print(f"  - {tech['name']}: {tech['ticket_count']} tickets, Nível: {tech.get('level', 'N/A')}")
        
        print(f"\n📈 Técnicos N4 encontrados sem filtro: {len(n4_found)}")
        for tech_name in n4_found:
            print(f"  - {tech_name}")
    
    print("\n📊 Testando ranking COM filtro N4 (limite 10)...")
    ranking_with_filter = service.get_technician_ranking_with_filters(limit=10, level='N4')
    
    if ranking_with_filter and 'technicians' in ranking_with_filter:
        techs = ranking_with_filter['technicians']
        print(f"✅ Encontrados {len(techs)} técnicos com filtro N4:")
        
        for tech in techs:
            print(f"  - {tech['name']}: {tech['ticket_count']} tickets, Nível: {tech.get('level', 'N/A')}")
    else:
        print("❌ Nenhum técnico N4 encontrado com filtro")
    
    print("\n✅ Teste de técnicos específicos concluído!")

if __name__ == "__main__":
    test_specific_technicians()