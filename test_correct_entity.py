#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService

def test_correct_entity():
    print("=== TESTE COM ENTIDADE CORRETA ===")
    
    # Inicializar serviço
    glpi_service = GLPIService()
    
    # Autenticar
    if not glpi_service.authenticate():
        print("❌ Falha na autenticação")
        return
    print("✅ Autenticado")
    
    # Testar com entidade ID 2 (CENTRAL DE ATENDIMENTOS)
    print("\n1. Testando _get_all_technician_ids_and_names COM entidade ID 2:")
    tech_ids, tech_names = glpi_service._get_all_technician_ids_and_names(entity_id=2)
    print(f"✅ Encontrados {len(tech_ids)} técnicos")
    
    if tech_ids:
        print("\nTécnicos encontrados:")
        for tech_id in tech_ids:
            tech_name = tech_names.get(tech_id, 'Nome não encontrado')
            print(f"   ID: {tech_id} - Nome: {tech_name}")
    
    # Testar sem filtro de entidade
    print("\n2. Testando _get_all_technician_ids_and_names SEM filtro de entidade:")
    all_tech_ids, all_tech_names = glpi_service._get_all_technician_ids_and_names()
    print(f"✅ Encontrados {len(all_tech_ids)} técnicos")
    
    if all_tech_ids:
        print("\nPrimeiros 5 técnicos:")
        for i, tech_id in enumerate(all_tech_ids[:5]):
            tech_name = all_tech_names.get(tech_id, 'Nome não encontrado')
            print(f"   ID: {tech_id} - Nome: {tech_name}")
    
    # Testar ranking com entidade ID 2
    print("\n3. Testando ranking de técnicos COM entidade ID 2:")
    try:
        ranking = glpi_service.get_technician_ranking_with_filters(entity_id=2)
        print(f"✅ Ranking gerado com {len(ranking)} técnicos")
        
        if ranking:
            print("\nTop 3 técnicos no ranking:")
            for i, tech in enumerate(ranking[:3]):
                print(f"   {i+1}. {tech['name']} - Total: {tech['total_tickets']}, Resolvidos: {tech['resolved_tickets']}")
    except Exception as e:
        print(f"❌ Erro no ranking: {e}")
    
    print("\n=== TESTE CONCLUÍDO ===")

if __name__ == "__main__":
    test_correct_entity()