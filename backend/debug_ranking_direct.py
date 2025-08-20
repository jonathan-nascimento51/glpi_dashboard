#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService

def debug_ranking_direct():
    """Debug direto do ranking de técnicos usando as funções do GLPIService"""
    
    # Inicializar serviço
    glpi = GLPIService()
    
    # Autenticar
    if not glpi.authenticate():
        print("Falha na autenticação")
        return
    
    print("=== DEBUG RANKING DE TÉCNICOS ===")
    
    # Testar descoberta de campo de técnico
    tech_field = glpi._discover_tech_field_id()
    print(f"Campo de técnico descoberto: {tech_field}")
    
    # Testar busca de técnicos
    print("\n--- Buscando técnicos ---")
    try:
        tech_ids, tech_names = glpi._get_all_technician_ids_and_names()
        print(f"Total de técnicos encontrados: {len(tech_ids)}")
        
        # Mostrar alguns técnicos
        for i, tech_id in enumerate(tech_ids[:10]):
            tech_name = tech_names.get(tech_id, 'Nome não encontrado')
            print(f"  {tech_id}: {tech_name}")
        
        if len(tech_ids) > 10:
            print(f"  ... e mais {len(tech_ids) - 10} técnicos")
            
    except Exception as e:
        print(f"Erro ao buscar técnicos: {e}")
        return
    
    # Testar ranking usando a função existente
    print("\n--- Testando ranking de técnicos ---")
    try:
        # Usar a função de ranking existente
        ranking = glpi.get_technician_ranking()
        print(f"Ranking retornado: {len(ranking)} técnicos")
        
        if ranking:
            print("Top 10 técnicos no ranking:")
            for i, tech in enumerate(ranking[:10]):
                print(f"  {i+1}. {tech.get('name', 'N/A')}: {tech.get('ticket_count', 0)} tickets")
        else:
            print("Ranking vazio!")
            
    except Exception as e:
        print(f"Erro no ranking: {e}")
        import traceback
        traceback.print_exc()
    
    # Testar contagem manual para alguns técnicos
    print("\n--- Testando contagem manual ---")
    test_techs = tech_ids[:5]  # Pegar os primeiros 5 técnicos
    
    for tech_id in test_techs:
        tech_name = tech_names.get(tech_id, 'Desconhecido')
        try:
            # Usar a função interna para contar tickets
            count = glpi._count_tickets_by_technician(tech_id, tech_field)
            print(f"  {tech_name} (ID: {tech_id}): {count} tickets")
        except Exception as e:
            print(f"  {tech_name} (ID: {tech_id}): Erro - {e}")
    
    print("\n=== FIM DO DEBUG ===")

if __name__ == "__main__":
    debug_ranking_direct()