#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService
import logging

# Configurar logging para mostrar apenas resultados
logging.basicConfig(level=logging.WARNING)

def test_technician_ranking():
    print("=== Teste Final do Ranking de Técnicos ===")
    
    try:
        # Inicializar serviço GLPI
        glpi_service = GLPIService()
        
        # Testar busca de técnicos sem filtro
        print("\n1. Testando busca de técnicos (sem filtro):")
        tech_ids, tech_names = glpi_service._get_all_technician_ids_and_names()
        print(f"   Técnicos encontrados: {len(tech_ids)}")
        
        # Testar busca de técnicos com filtro de entidade CAU
        print("\n2. Testando busca de técnicos (filtro CAU - ID: 1):")
        tech_ids_cau, tech_names_cau = glpi_service._get_all_technician_ids_and_names(entity_id=1)
        print(f"   Técnicos CAU encontrados: {len(tech_ids_cau)}")
        
        # Testar ranking sem filtro
        print("\n3. Testando ranking de técnicos (sem filtro):")
        ranking = glpi_service.get_technician_ranking_with_filters()
        if ranking:
            print(f"   Técnicos no ranking: {len(ranking)}")
            print("   Top 3 técnicos:")
            for i, tech in enumerate(ranking[:3], 1):
                print(f"   {i}. {tech['name']} - Total: {tech['total']}, Nível: {tech['level']}")
        
        # Testar ranking com filtro de entidade
        print("\n4. Testando ranking de técnicos (filtro CAU):")
        ranking_cau = glpi_service.get_technician_ranking_with_filters(entity_id=1)
        if ranking_cau:
            print(f"   Técnicos no ranking CAU: {len(ranking_cau)}")
            print("   Top 3 técnicos CAU:")
            for i, tech in enumerate(ranking_cau[:3], 1):
                print(f"   {i}. {tech['name']} - Total: {tech['total']}, Nível: {tech['level']}")
        
        print("\n=== Teste Concluído com Sucesso ===")
        
    except Exception as e:
        print(f"Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_technician_ranking()
    sys.exit(0 if success else 1)