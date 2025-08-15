#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de debug para investigar inconsistência entre métricas gerais e por nível
"""

import sys
import os

# Adicionar o diretório pai ao path para imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(backend_dir)
sys.path.insert(0, project_dir)
sys.path.insert(0, backend_dir)

from services.glpi_service import GLPIService
import json
from datetime import datetime, timedelta

def debug_metrics_inconsistency():
    """Debug da inconsistência entre totais gerais e por nível"""
    print("=== DEBUG: INCONSISTÊNCIA MÉTRICAS ===")
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Inicializar serviço GLPI
    glpi = GLPIService()
    
    # Autenticar e descobrir field IDs
    print("Autenticando e descobrindo field IDs...")
    if not glpi._ensure_authenticated():
        print("❌ Falha na autenticaçáo!")
        return
    
    if not glpi.discover_field_ids():
        print("❌ Falha ao descobrir field IDs!")
        return
    
    print(f"✅ Field IDs descobertos: {glpi.field_ids}")
    print()
    
    # Testar sem filtros de data primeiro
    print("1. TESTANDO SEM FILTROS DE DATA")
    print("-" * 50)
    
    # Obter métricas gerais (todos os tickets)
    print("Obtendo métricas gerais (todos os tickets)...")
    general_metrics = glpi._get_general_metrics_internal()
    print(f"Métricas gerais: {json.dumps(general_metrics, indent=2)}")
    
    # Calcular totais das métricas gerais
    general_resolvidos = general_metrics.get('Solucionado', 0) + general_metrics.get('Fechado', 0)
    general_total = sum(general_metrics.values())
    print(f"Total geral resolvidos: {general_resolvidos}")
    print(f"Total geral de tickets: {general_total}")
    print()
    
    # Obter métricas por nível (apenas N1-N4)
    print("Obtendo métricas por nível (N1-N4)...")
    level_metrics = glpi._get_metrics_by_level_internal()
    print(f"Métricas por nível: {json.dumps(level_metrics, indent=2)}")
    
    # Calcular totais das métricas por nível
    level_totals = {
        'Novo': 0,
        'Pendente': 0,
        'Processando (atribuído)': 0,
        'Processando (planejado)': 0,
        'Solucionado': 0,
        'Fechado': 0
    }
    
    for level_name, level_data in level_metrics.items():
        print(f"\nNível {level_name}:")
        level_total = 0
        for status, count in level_data.items():
            level_totals[status] += count
            level_total += count
            print(f"  {status}: {count}")
        print(f"  Total do nível: {level_total}")
    
    print("\nTOTAIS AGREGADOS POR NÍVEL:")
    level_resolvidos = level_totals['Solucionado'] + level_totals['Fechado']
    level_total_all = sum(level_totals.values())
    
    for status, total in level_totals.items():
        print(f"  {status}: {total}")
    print(f"  Resolvidos (Solucionado + Fechado): {level_resolvidos}")
    print(f"  Total de todos os níveis: {level_total_all}")
    
    print("\n" + "=" * 60)
    print("COMPARAÇáO:")
    print(f"Resolvidos - Geral: {general_resolvidos}")
    print(f"Resolvidos - Níveis: {level_resolvidos}")
    print(f"Diferença: {general_resolvidos - level_resolvidos}")
    print(f"Total - Geral: {general_total}")
    print(f"Total - Níveis: {level_total_all}")
    print(f"Diferença: {general_total - level_total_all}")
    
    # Verificar se há tickets fora dos grupos N1-N4
    if general_total > level_total_all:
        print(f"\n⚠️  PROBLEMA IDENTIFICADO:")
        print(f"Existem {general_total - level_total_all} tickets que náo estáo nos grupos N1-N4")
        print("Isso explica a inconsistência nos dados!")
        
        # Investigar quais grupos existem
        print("\nInvestigando grupos existentes...")
        investigate_groups(glpi)
    
    print("\n" + "=" * 60)
    
    # Testar com filtros de data
    print("\n2. TESTANDO COM FILTROS DE DATA (últimos 30 dias)")
    print("-" * 50)
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"Período: {start_date} até {end_date}")
    
    # Métricas gerais com filtro
    general_filtered = glpi._get_general_metrics_internal(start_date, end_date)
    print(f"\nMétricas gerais (filtradas): {json.dumps(general_filtered, indent=2)}")
    
    # Métricas por nível com filtro
    level_filtered = glpi._get_metrics_by_level_internal(start_date, end_date)
    print(f"\nMétricas por nível (filtradas): {json.dumps(level_filtered, indent=2)}")
    
    # Comparar novamente
    general_resolvidos_f = general_filtered.get('Solucionado', 0) + general_filtered.get('Fechado', 0)
    level_resolvidos_f = sum(
        level_data.get('Solucionado', 0) + level_data.get('Fechado', 0)
        for level_data in level_filtered.values()
    )
    
    print(f"\nCOMPARAÇáO COM FILTROS:")
    print(f"Resolvidos - Geral: {general_resolvidos_f}")
    print(f"Resolvidos - Níveis: {level_resolvidos_f}")
    print(f"Diferença: {general_resolvidos_f - level_resolvidos_f}")

def investigate_groups(glpi):
    """Investiga quais grupos existem no GLPI"""
    try:
        print("\nBuscando todos os grupos no GLPI...")
        
        # Fazer uma busca por todos os tickets agrupados por grupo
        search_params = {
            "is_deleted": 0,
            "range": "0-50",  # Buscar alguns tickets para ver os grupos
            "forcedisplay[0]": glpi.field_ids["GROUP"],  # Campo grupo
            "forcedisplay[1]": "1",  # ID do ticket
        }
        
        response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/search/Ticket",
            params=search_params
        )
        
        if response and response.status_code == 200:
            data = response.json()
            if 'data' in data:
                groups_found = set()
                for ticket in data['data']:
                    if len(ticket) > 1:  # Tem dados do grupo
                        group_info = ticket[1]  # Campo grupo
                        if isinstance(group_info, dict) and 'name' in group_info:
                            groups_found.add(f"{group_info.get('id', 'N/A')} - {group_info['name']}")
                        elif isinstance(group_info, str):
                            groups_found.add(group_info)
                
                print(f"Grupos encontrados nos tickets:")
                for group in sorted(groups_found):
                    print(f"  - {group}")
                    
                print(f"\nGrupos configurados no sistema (N1-N4):")
                for level, group_id in glpi.service_levels.items():
                    print(f"  - {level}: {group_id}")
        
    except Exception as e:
        print(f"Erro ao investigar grupos: {e}")

if __name__ == "__main__":
    debug_metrics_inconsistency()
