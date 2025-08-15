#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de debug para testar o ranking de técnicos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.glpi_service import GLPIService
from app.config import get_active_config
import json

def test_technician_ranking():
    """Testa o ranking de técnicos passo a passo"""
    print("=== INICIANDO TESTE DE RANKING DE TÉCNICOS ===")
    
    # Inicializar serviço
    config = get_active_config()
    glpi_service = GLPIService()
    
    print(f"URL GLPI: {config.GLPI_URL}")
    print(f"App Token: {config.GLPI_APP_TOKEN[:10]}...")
    print(f"User Token: {config.GLPI_USER_TOKEN[:10]}...")
    
    # Teste 1: Verificar autenticação
    print("\n1. Testando autenticação...")
    auth_result = glpi_service._ensure_authenticated()
    print(f"Autenticação: {'OK' if auth_result else 'FALHOU'}")
    
    if not auth_result:
        print("ERRO: Falha na autenticação. Abortando teste.")
        return
    
    # Teste 2: Descobrir field ID do técnico
    print("\n2. Descobrindo field ID do técnico...")
    field_id = glpi_service._discover_tech_field_id()
    print(f"Field ID descoberto: {field_id}")
    
    # Teste 3: Buscar técnicos ativos
    print("\n3. Buscando técnicos ativos...")
    try:
        active_techs = glpi_service.get_active_technicians()
        print(f"Técnicos ativos encontrados: {len(active_techs)}")
        if active_techs:
            print(f"Primeiro técnico: {active_techs[0]}")
    except Exception as e:
        print(f"ERRO ao buscar técnicos ativos: {e}")
        active_techs = []
    
    # Teste 4: Buscar ranking
    print("\n4. Buscando ranking de técnicos...")
    try:
        ranking = glpi_service.get_technician_ranking(limit=5)
        print(f"Ranking obtido: {len(ranking)} técnicos")
        
        if ranking:
            print("\nTop 3 técnicos:")
            for i, tech in enumerate(ranking[:3]):
                print(f"{i+1}. {tech}")
        else:
            print("AVISO: Ranking vazio")
            
    except Exception as e:
        print(f"ERRO ao buscar ranking: {e}")
        import traceback
        print(f"Stack trace: {traceback.format_exc()}")
    
    # Teste 5: Testar método de fallback
    print("\n5. Testando método de fallback...")
    try:
        fallback_ranking = glpi_service._get_technician_ranking_fallback()
        print(f"Ranking fallback: {len(fallback_ranking)} técnicos")
        
        if fallback_ranking:
            print("\nTop 3 técnicos (fallback):")
            for i, tech in enumerate(fallback_ranking[:3]):
                print(f"{i+1}. {tech}")
                
    except Exception as e:
        print(f"ERRO no método fallback: {e}")
    
    print("\n=== TESTE CONCLUÍDO ===")

if __name__ == "__main__":
    test_technician_ranking()
