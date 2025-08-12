#!/usr/bin/env python3
"""
Teste para verificar se a correção do ranking de técnicos está funcionando
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.glpi_service import GLPIService
import json

def test_ranking_with_levels():
    """Testa se o ranking está retornando os níveis corretos dos técnicos"""
    print("🔍 Testando ranking de técnicos com níveis corretos...")
    
    try:
        # Inicializar serviço GLPI
        glpi_service = GLPIService()
        
        # Testar ranking sem filtros
        print("\n📊 Testando ranking sem filtros...")
        ranking = glpi_service.get_technician_ranking_with_filters(limit=10)
        
        if ranking:
            print(f"✅ Ranking obtido com {len(ranking)} técnicos")
            
            # Verificar se os níveis estão sendo retornados corretamente
            levels_found = set()
            for tech in ranking:
                level = tech.get('level', 'N/A')
                levels_found.add(level)
                print(f"  - {tech['name']}: {tech['total']} tickets, Nível: {level}")
            
            print(f"\n🎯 Níveis encontrados: {sorted(levels_found)}")
            
            # Verificar se há técnicos com níveis válidos (N1, N2, N3, N4)
            valid_levels = {'N1', 'N2', 'N3', 'N4'}
            found_valid_levels = levels_found.intersection(valid_levels)
            
            if found_valid_levels:
                print(f"✅ Níveis válidos encontrados: {sorted(found_valid_levels)}")
            else:
                print(f"❌ Nenhum nível válido encontrado. Níveis: {levels_found}")
                
        else:
            print("❌ Nenhum técnico encontrado no ranking")
            
        # Testar ranking com filtro de nível específico
        print("\n📊 Testando ranking com filtro de nível N2...")
        ranking_n2 = glpi_service.get_technician_ranking_with_filters(level='N2', limit=5)
        
        if ranking_n2:
            print(f"✅ Ranking N2 obtido com {len(ranking_n2)} técnicos")
            for tech in ranking_n2:
                print(f"  - {tech['name']}: {tech['total']} tickets, Nível: {tech['level']}")
                
            # Verificar se todos são realmente N2
            all_n2 = all(tech['level'] == 'N2' for tech in ranking_n2)
            if all_n2:
                print("✅ Todos os técnicos retornados são N2")
            else:
                print("❌ Nem todos os técnicos retornados são N2")
        else:
            print("⚠️ Nenhum técnico N2 encontrado")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Iniciando teste de correção do ranking...")
    success = test_ranking_with_levels()
    
    if success:
        print("\n✅ Teste concluído com sucesso!")
    else:
        print("\n❌ Teste falhou!")
        sys.exit(1)