#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste final do ranking de técnicos com filtro de entidade
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService
from datetime import datetime, timedelta

def test_technician_ranking():
    """Testa o ranking de técnicos com filtro de entidade"""
    try:
        print("=== Teste do Ranking de Técnicos ===")
        
        # Inicializar serviço GLPI
        glpi_service = GLPIService()
        
        # Testar busca de técnicos sem filtro de entidade
        print("\n1. Testando busca de técnicos (sem filtro de entidade):")
        tech_ids, tech_names = glpi_service._get_all_technician_ids_and_names()
        print(f"   Técnicos encontrados: {len(tech_ids)}")
        if tech_ids:
            print(f"   Primeiros 3 técnicos: {list(tech_names.items())[:3]}")
        
        # Testar busca de técnicos com filtro de entidade (CAU)
        print("\n2. Testando busca de técnicos (com filtro entidade CAU - ID: 1):")
        tech_ids_cau, tech_names_cau = glpi_service._get_all_technician_ids_and_names(entity_id=1)
        print(f"   Técnicos da entidade CAU: {len(tech_ids_cau)}")
        if tech_ids_cau:
            print(f"   Primeiros 3 técnicos CAU: {list(tech_names_cau.items())[:3]}")
        
        # Testar ranking de técnicos
        print("\n3. Testando ranking de técnicos (últimos 30 dias):")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        ranking = glpi_service.get_technician_ranking_with_filters(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            entity_id=None  # Sem filtro de entidade
        )
        
        print(f"   Técnicos no ranking: {len(ranking)}")
        if ranking:
            print("   Top 3 técnicos:")
            for i, tech in enumerate(ranking[:3], 1):
                print(f"   {i}. {tech['name']} - Total: {tech['total']}, Nível: {tech['level']}")
        
        # Testar ranking com filtro de entidade
        print("\n4. Testando ranking de técnicos com filtro de entidade CAU:")
        ranking_cau = glpi_service.get_technician_ranking_with_filters(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            entity_id=1  # Filtro para entidade CAU
        )
        
        print(f"   Técnicos no ranking CAU: {len(ranking_cau)}")
        if ranking_cau:
            print("   Top 3 técnicos CAU:")
            for i, tech in enumerate(ranking_cau[:3], 1):
                print(f"   {i}. {tech['name']} - Total: {tech['total']}, Nível: {tech['level']}")
        
        print("\n=== Teste Concluído com Sucesso ===")
        
    except Exception as e:
        print(f"Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_technician_ranking()