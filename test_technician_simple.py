#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService

def test_technician_search():
    """Teste simples da nova implementação de busca de técnicos"""
    
    print("=== Teste da Nova Implementação de Busca de Técnicos ===")
    
    # Configurar serviço
    glpi_service = GLPIService()
    
    try:
        # Testar a nova implementação
        print("\n1. Testando _get_all_technician_ids_and_names...")
        tech_ids, tech_names = glpi_service._get_all_technician_ids_and_names()
        
        print(f"\nResultado: {len(tech_ids)} técnicos encontrados")
        
        if tech_ids:
            print("\nPrimeiros 5 técnicos encontrados:")
            for i, tech_id in enumerate(tech_ids[:5]):
                tech_name = tech_names.get(tech_id, "Nome não encontrado")
                print(f"  {i+1}. ID: {tech_id}, Nome: {tech_name}")
        else:
            print("\nNenhum técnico encontrado!")
            
        # Testar também _get_all_technician_ids
        print("\n2. Testando _get_all_technician_ids...")
        tech_ids = glpi_service._get_all_technician_ids()
        print(f"IDs de técnicos: {len(tech_ids)} encontrados")
        if tech_ids:
            print(f"Primeiros 5 IDs: {list(tech_ids)[:5]}")
            
    except Exception as e:
        print(f"\nErro durante o teste: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Fim do Teste ===")

if __name__ == "__main__":
    test_technician_search()