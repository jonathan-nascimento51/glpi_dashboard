#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import logging
from datetime import datetime

# Desabilitar todos os logs
logging.disable(logging.CRITICAL)
sys.stderr = open(os.devnull, 'w')

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService

def main():
    print("=== Teste Final da Função de Técnicos ===")
    
    # Configurar GLPI service
    glpi_service = GLPIService()
    
    # Autenticar
    print("\n1. Autenticando...")
    if not glpi_service.authenticate():
        print("❌ Falha na autenticação")
        return
    print("✅ Autenticação bem-sucedida")
    
    # Teste 1: Buscar técnicos sem filtro de entidade
    print("\n2. Testando _get_all_technician_ids_and_names sem filtro de entidade...")
    tech_ids_all, tech_names_all = glpi_service._get_all_technician_ids_and_names()
    print(f"✅ Encontrados {len(tech_ids_all)} técnicos sem filtro")
    print(f"   IDs: {tech_ids_all[:5]}..." if len(tech_ids_all) > 5 else f"   IDs: {tech_ids_all}")
    print(f"   Nomes (primeiros 3): {list(tech_names_all.items())[:3]}")
    
    # Teste 2: Buscar técnicos com filtro de entidade ID 2
    print("\n3. Testando _get_all_technician_ids_and_names com entidade ID 2...")
    tech_ids_filtered, tech_names_filtered = glpi_service._get_all_technician_ids_and_names(entity_id=2)
    print(f"✅ Encontrados {len(tech_ids_filtered)} técnicos com filtro entidade 2")
    print(f"   IDs: {tech_ids_filtered[:5]}..." if len(tech_ids_filtered) > 5 else f"   IDs: {tech_ids_filtered}")
    print(f"   Nomes (primeiros 3): {list(tech_names_filtered.items())[:3]}")
    
    # Teste 3: Comparar resultados
    print("\n4. Comparando resultados...")
    if len(tech_ids_filtered) > 0:
        print(f"✅ Filtro de entidade funcionou! {len(tech_ids_filtered)} técnicos encontrados")
        
        # Verificar se os técnicos filtrados são um subconjunto dos técnicos totais
        filtered_set = set(tech_ids_filtered)
        all_set = set(tech_ids_all)
        
        if filtered_set.issubset(all_set):
            print("✅ Técnicos filtrados são um subconjunto válido dos técnicos totais")
        else:
            print("⚠️ Alguns técnicos filtrados não estão na lista total")
            
        # Mostrar alguns nomes
        print("\nTécnicos encontrados com filtro de entidade:")
        for tech_id in tech_ids_filtered[:5]:
            name = tech_names_filtered.get(tech_id, 'Nome não encontrado')
            print(f"  - {tech_id}: {name}")
    else:
        print("❌ Filtro de entidade não funcionou - nenhum técnico encontrado")
    
    # Teste 4: Testar ranking com filtro de entidade
    print("\n5. Testando ranking de técnicos com filtro de entidade...")
    try:
        # Simular uma data de início e fim
        start_date = "2024-01-01"
        end_date = "2024-12-31"
        
        ranking = glpi_service.get_technician_ranking_with_filters(
            start_date=start_date,
            end_date=end_date,
            entity_id=2
        )
        
        print(f"✅ Ranking gerado com {len(ranking)} técnicos")
        
        if ranking:
            print("\nTop 3 técnicos no ranking:")
            for i, tech in enumerate(ranking[:3]):
                print(f"  {i+1}. {tech.get('name', 'N/A')} - Total: {tech.get('total_tickets', 0)}, Resolvidos: {tech.get('resolved_tickets', 0)}")
        else:
            print("❌ Ranking vazio")
            
    except Exception as e:
        print(f"❌ Erro ao gerar ranking: {e}")
    
    print("\n=== Fim do Teste ===")

if __name__ == "__main__":
    main()