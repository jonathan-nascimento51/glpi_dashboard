#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste com limite maior para encontrar técnicos N4
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.glpi_service import GLPIService

def test_large_limit():
    """Testa com limite maior para encontrar técnicos N4"""
    print("🚀 Iniciando teste com limite maior...")
    
    service = GLPIService()
    
    print("\n📊 Testando ranking COM filtro N4 (limite 50)...")
    ranking_with_filter = service.get_technician_ranking_with_filters(limit=50, level='N4')
    
    if ranking_with_filter and 'technicians' in ranking_with_filter:
        techs = ranking_with_filter['technicians']
        print(f"✅ Encontrados {len(techs)} técnicos com filtro N4:")
        
        for tech in techs:
            print(f"  - {tech['name']}: {tech['ticket_count']} tickets, Nível: {tech.get('level', 'N/A')}")
    else:
        print("❌ Nenhum técnico N4 encontrado com filtro (limite 50)")
    
    print("\n📊 Testando ranking COM filtro N3 (limite 50)...")
    ranking_n3 = service.get_technician_ranking_with_filters(limit=50, level='N3')
    
    if ranking_n3 and 'technicians' in ranking_n3:
        techs = ranking_n3['technicians']
        print(f"✅ Encontrados {len(techs)} técnicos com filtro N3:")
        
        for tech in techs:
            print(f"  - {tech['name']}: {tech['ticket_count']} tickets, Nível: {tech.get('level', 'N/A')}")
    else:
        print("❌ Nenhum técnico N3 encontrado com filtro (limite 50)")
    
    print("\n📊 Testando ranking COM filtro N2 (limite 50)...")
    ranking_n2 = service.get_technician_ranking_with_filters(limit=50, level='N2')
    
    if ranking_n2 and 'technicians' in ranking_n2:
        techs = ranking_n2['technicians']
        print(f"✅ Encontrados {len(techs)} técnicos com filtro N2:")
        
        for tech in techs:
            print(f"  - {tech['name']}: {tech['ticket_count']} tickets, Nível: {tech.get('level', 'N/A')}")
    else:
        print("❌ Nenhum técnico N2 encontrado com filtro (limite 50)")
    
    print("\n✅ Teste com limite maior concluído!")

if __name__ == "__main__":
    test_large_limit()