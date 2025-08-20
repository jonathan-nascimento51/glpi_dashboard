#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para verificar se os filtros de data estão funcionando corretamente
no ranking de técnicos do GLPI Dashboard.
"""

import sys
import os
from datetime import datetime, timedelta

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService

def test_date_filters():
    """Testa os filtros de data no ranking de técnicos"""
    print("=== TESTE DE FILTROS DE DATA NO RANKING DE TÉCNICOS ===")
    
    # Inicializar serviço GLPI
    glpi_service = GLPIService()
    
    # Autenticar
    print("\n1. Autenticando com GLPI...")
    if not glpi_service.authenticate():
        print("❌ Falha na autenticação")
        return False
    print("✅ Autenticação bem-sucedida")
    
    # Descobrir field ID do técnico
    print("\n2. Descobrindo field ID do técnico...")
    tech_field_id = glpi_service._discover_tech_field_id()
    if not tech_field_id:
        print("❌ Falha ao descobrir field ID do técnico")
        return False
    print(f"✅ Field ID do técnico: {tech_field_id}")
    
    # Definir períodos de teste
    today = datetime.now()
    
    # Teste 1: Últimos 30 dias
    start_date_30d = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    end_date_30d = today.strftime('%Y-%m-%d')
    
    # Teste 2: Últimos 7 dias
    start_date_7d = (today - timedelta(days=7)).strftime('%Y-%m-%d')
    end_date_7d = today.strftime('%Y-%m-%d')
    
    # Teste 3: Mês passado
    first_day_last_month = today.replace(day=1) - timedelta(days=1)
    start_date_last_month = first_day_last_month.replace(day=1).strftime('%Y-%m-%d')
    end_date_last_month = first_day_last_month.strftime('%Y-%m-%d')
    
    print("\n3. Testando ranking SEM filtros de data...")
    ranking_no_filter = glpi_service.get_technician_ranking(limit=5)
    print(f"✅ Ranking sem filtros: {len(ranking_no_filter)} técnicos")
    if ranking_no_filter:
        print("   Top 3:")
        for i, tech in enumerate(ranking_no_filter[:3]):
            print(f"   {i+1}. {tech.get('name', 'N/A')} - {tech.get('total', 0)} tickets")
    
    print(f"\n4. Testando ranking COM filtros de data (últimos 30 dias: {start_date_30d} a {end_date_30d})...")
    ranking_30d = glpi_service.get_technician_ranking_with_filters(
        start_date=start_date_30d,
        end_date=end_date_30d,
        limit=5
    )
    print(f"✅ Ranking 30 dias: {len(ranking_30d)} técnicos")
    if ranking_30d:
        print("   Top 3:")
        for i, tech in enumerate(ranking_30d[:3]):
            print(f"   {i+1}. {tech.get('name', 'N/A')} - {tech.get('total', 0)} tickets")
    
    print(f"\n5. Testando ranking COM filtros de data (últimos 7 dias: {start_date_7d} a {end_date_7d})...")
    ranking_7d = glpi_service.get_technician_ranking_with_filters(
        start_date=start_date_7d,
        end_date=end_date_7d,
        limit=5
    )
    print(f"✅ Ranking 7 dias: {len(ranking_7d)} técnicos")
    if ranking_7d:
        print("   Top 3:")
        for i, tech in enumerate(ranking_7d[:3]):
            print(f"   {i+1}. {tech.get('name', 'N/A')} - {tech.get('total', 0)} tickets")
    
    print(f"\n6. Testando ranking COM filtros de data (mês passado: {start_date_last_month} a {end_date_last_month})...")
    ranking_last_month = glpi_service.get_technician_ranking_with_filters(
        start_date=start_date_last_month,
        end_date=end_date_last_month,
        limit=5
    )
    print(f"✅ Ranking mês passado: {len(ranking_last_month)} técnicos")
    if ranking_last_month:
        print("   Top 3:")
        for i, tech in enumerate(ranking_last_month[:3]):
            print(f"   {i+1}. {tech.get('name', 'N/A')} - {tech.get('total', 0)} tickets")
    
    # Análise dos resultados
    print("\n=== ANÁLISE DOS RESULTADOS ===")
    
    # Verificar se os números fazem sentido (período menor deve ter menos tickets)
    if ranking_no_filter and ranking_30d and ranking_7d:
        total_no_filter = sum(tech.get('total', 0) for tech in ranking_no_filter)
        total_30d = sum(tech.get('total', 0) for tech in ranking_30d)
        total_7d = sum(tech.get('total', 0) for tech in ranking_7d)
        
        print(f"Total de tickets (sem filtro): {total_no_filter}")
        print(f"Total de tickets (30 dias): {total_30d}")
        print(f"Total de tickets (7 dias): {total_7d}")
        
        # Verificações lógicas
        if total_7d <= total_30d:
            print("✅ Lógica correta: 7 dias <= 30 dias")
        else:
            print("❌ Problema: 7 dias > 30 dias (não deveria acontecer)")
        
        if total_30d <= total_no_filter:
            print("✅ Lógica correta: 30 dias <= sem filtro")
        else:
            print("❌ Problema: 30 dias > sem filtro (pode indicar problema)")
    
    # Teste com filtro de entidade
    print("\n7. Testando ranking com filtro de entidade (entity_id=1)...")
    ranking_entity = glpi_service.get_technician_ranking_with_filters(
        start_date=start_date_30d,
        end_date=end_date_30d,
        entity_id="1",
        limit=5
    )
    print(f"✅ Ranking com entidade: {len(ranking_entity)} técnicos")
    if ranking_entity:
        print("   Top 3:")
        for i, tech in enumerate(ranking_entity[:3]):
            print(f"   {i+1}. {tech.get('name', 'N/A')} - {tech.get('total', 0)} tickets")
    
    print("\n=== TESTE CONCLUÍDO ===")
    return True

if __name__ == "__main__":
    try:
        success = test_date_filters()
        if success:
            print("\n🎉 Todos os testes foram executados com sucesso!")
        else:
            print("\n❌ Alguns testes falharam.")
    except Exception as e:
        print(f"\n💥 Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()