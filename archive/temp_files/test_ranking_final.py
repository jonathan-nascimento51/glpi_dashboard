#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar o ranking final corrigido
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService

def test_ranking_final():
    """Testa o ranking final corrigido"""
    
    print("=== TESTE DO RANKING FINAL CORRIGIDO ===")
    
    # Inicializar serviço GLPI
    glpi = GLPIService()
    
    try:
        # Buscar ranking completo
        print("Buscando ranking completo...")
        ranking = glpi.get_technician_ranking(limit=20)
        
        print(f"\nTotal de técnicos no ranking: {len(ranking)}")
        
        # Mostrar os primeiros 10 técnicos
        print("\n=== TOP 10 TÉCNICOS ===")
        for i, tech in enumerate(ranking[:10], 1):
            print(f"{i:2d}. {tech.get('nome', 'N/A')} (ID: {tech.get('id', 'N/A')})")
            print(f"     Nível: {tech.get('nivel', 'N/A')} | Tickets: {tech.get('total', 0)}")
            print()
        
        # Procurar pelos Gabriels especificamente
        print("\n=== VERIFICAÇÃO DOS GABRIELS ===")
        gabriel_conceicao_found = False
        gabriel_machado_found = False
        
        for i, tech in enumerate(ranking, 1):
            if tech.get('id') == 1404:  # Gabriel Conceição
                print(f"✅ Gabriel Conceição encontrado na posição {i}:")
                print(f"   Nome: {tech.get('nome', 'N/A')}")
                print(f"   Nível: {tech.get('nivel', 'N/A')}")
                print(f"   Total: {tech.get('total', 0)} tickets")
                gabriel_conceicao_found = True
                print()
            
            elif tech.get('id') == 1291:  # Gabriel Machado
                print(f"✅ Gabriel Machado encontrado na posição {i}:")
                print(f"   Nome: {tech.get('nome', 'N/A')}")
                print(f"   Nível: {tech.get('nivel', 'N/A')}")
                print(f"   Total: {tech.get('total', 0)} tickets")
                gabriel_machado_found = True
                print()
        
        if not gabriel_conceicao_found:
            print("❌ Gabriel Conceição (ID 1404) NÃO encontrado no ranking")
        
        if not gabriel_machado_found:
            print("❌ Gabriel Machado (ID 1291) NÃO encontrado no ranking")
        
        # Verificar distribuição de níveis
        print("\n=== DISTRIBUIÇÃO DE NÍVEIS ===")
        levels_count = {}
        for tech in ranking:
            level = tech.get('nivel', 'N/A')
            levels_count[level] = levels_count.get(level, 0) + 1
        
        for level, count in sorted(levels_count.items()):
            print(f"{level}: {count} técnicos")
        
    except Exception as e:
        print(f"❌ Erro ao testar ranking: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ranking_final()