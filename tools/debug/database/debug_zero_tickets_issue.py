#!/usr/bin/env python3
"""
Script de debug para investigar o problema de tickets zerados no ranking de técnicos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService
from datetime import datetime, timedelta
import json

def debug_zero_tickets_issue():
    """
    Investiga o problema de tickets zerados no ranking
    """
    print("=== DEBUG: PROBLEMA DE TICKETS ZERADOS ===")
    print(f"Timestamp: {datetime.now()}")
    
    # Inicializar serviço GLPI
    try:
        glpi = GLPIService()
        if not glpi._ensure_authenticated():
            print("❌ Falha na autenticação com GLPI")
            return
        print("✅ Autenticação com GLPI bem-sucedida")
    except Exception as e:
        print(f"❌ Erro ao inicializar GLPI: {e}")
        return
    
    print("\n=== ETAPA 1: Verificar obtenção de técnicos ===")
    try:
        tech_ids, tech_names = glpi._get_all_technician_ids_and_names()
        print(f"📊 Técnicos encontrados: {len(tech_ids)}")
        
        if not tech_ids:
            print("❌ PROBLEMA IDENTIFICADO: Nenhum técnico encontrado!")
            print("   Possíveis causas:")
            print("   - Nenhum usuário com perfil técnico (ID 6) ativo")
            print("   - Problemas na busca Profile_User")
            print("   - Usuários inativos ou deletados")
            return
        
        print(f"✅ Técnicos válidos encontrados: {len(tech_ids)}")
        print("   Primeiros 5 técnicos:")
        for i, tech_id in enumerate(tech_ids[:5]):
            name = tech_names.get(tech_id, f"Técnico {tech_id}")
            print(f"   {i+1}. ID: {tech_id} - Nome: {name}")
            
    except Exception as e:
        print(f"❌ Erro ao obter técnicos: {e}")
        return
    
    print("\n=== ETAPA 2: Testar contagem individual de tickets ===")
    # Testar os primeiros 3 técnicos
    test_tech_ids = tech_ids[:3]
    
    for tech_id in test_tech_ids:
        tech_name = tech_names.get(tech_id, f"Técnico {tech_id}")
        print(f"\n🔍 Testando técnico: {tech_name} (ID: {tech_id})")
        
        try:
            # Teste 1: Método otimizado sem filtro
            count_optimized = glpi._count_tickets_by_technician_optimized(int(tech_id), "4")
            print(f"   Método otimizado: {count_optimized} tickets")
            
            # Teste 2: Método com filtro de data (últimos 30 dias)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            count_with_filter = glpi._count_tickets_with_date_filter(
                tech_id, 
                start_date.strftime("%Y-%m-%d"), 
                end_date.strftime("%Y-%m-%d")
            )
            print(f"   Com filtro (30 dias): {count_with_filter} tickets")
            
            # Teste 3: Verificar se há tickets no GLPI para este técnico
            # Busca direta na API
            search_params = {
                "is_deleted": 0,
                "criteria[0][field]": "4",  # users_id_tech
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": str(tech_id),
                "range": "0-4"  # Buscar apenas os primeiros 5 tickets
            }
            
            response = glpi._make_authenticated_request(
                "GET", 
                f"{glpi.glpi_url}/search/Ticket", 
                params=search_params
            )
            
            if response and response.ok:
                data = response.json()
                total_count = data.get("totalcount", 0)
                tickets_data = data.get("data", [])
                print(f"   Busca direta API: {total_count} tickets totais")
                
                if tickets_data:
                    print(f"   Primeiros tickets encontrados:")
                    for i, ticket in enumerate(tickets_data[:3]):
                        ticket_id = ticket.get("2", "N/A")
                        ticket_title = ticket.get("1", "N/A")
                        print(f"     - Ticket #{ticket_id}: {ticket_title}")
                else:
                    print(f"   ⚠️  Nenhum ticket encontrado na busca direta")
            else:
                print(f"   ❌ Falha na busca direta: {response.status_code if response else 'No response'}")
                
        except Exception as e:
            print(f"   ❌ Erro ao testar técnico {tech_id}: {e}")
    
    print("\n=== ETAPA 3: Testar métodos em lote ===")
    try:
        # Teste sem filtro de data
        print("\n📊 Testando método em lote SEM filtro de data:")
        batch_counts_no_filter = glpi._get_tickets_batch_without_date_filter(test_tech_ids)
        total_no_filter = sum(batch_counts_no_filter.values())
        print(f"   Total de tickets encontrados: {total_no_filter}")
        
        for tech_id in test_tech_ids:
            tech_name = tech_names.get(tech_id, f"Técnico {tech_id}")
            count = batch_counts_no_filter.get(tech_id, 0)
            print(f"   - {tech_name}: {count} tickets")
        
        # Teste com filtro de data
        print("\n📊 Testando método em lote COM filtro de data (30 dias):")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        batch_counts_with_filter = glpi._get_tickets_batch_with_date_filter(
            test_tech_ids,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        total_with_filter = sum(batch_counts_with_filter.values())
        print(f"   Total de tickets encontrados (30 dias): {total_with_filter}")
        
        for tech_id in test_tech_ids:
            tech_name = tech_names.get(tech_id, f"Técnico {tech_id}")
            count = batch_counts_with_filter.get(tech_id, 0)
            print(f"   - {tech_name}: {count} tickets")
            
    except Exception as e:
        print(f"❌ Erro ao testar métodos em lote: {e}")
    
    print("\n=== ETAPA 4: Testar ranking completo ===")
    try:
        # Teste ranking sem filtros
        print("\n🏆 Testando get_technician_ranking():")
        ranking_no_filter = glpi.get_technician_ranking()
        print(f"   Ranking retornado: {len(ranking_no_filter)} técnicos")
        
        if ranking_no_filter:
            total_tickets_ranking = sum(tech.get("total", 0) for tech in ranking_no_filter)
            print(f"   Total de tickets no ranking: {total_tickets_ranking}")
            
            print("   Top 5 técnicos:")
            for i, tech in enumerate(ranking_no_filter[:5]):
                name = tech.get("name", "N/A")
                total = tech.get("total", 0)
                level = tech.get("level", "N/A")
                print(f"     {i+1}. {name} - {total} tickets (Nível: {level})")
        else:
            print("   ❌ Ranking vazio retornado")
        
        # Teste ranking com filtros
        print("\n🏆 Testando get_technician_ranking_with_filters():")
        ranking_with_filter = glpi.get_technician_ranking_with_filters()
        print(f"   Ranking filtrado retornado: {len(ranking_with_filter)} técnicos")
        
        if ranking_with_filter:
            total_tickets_filtered = sum(tech.get("total", 0) for tech in ranking_with_filter)
            print(f"   Total de tickets no ranking filtrado: {total_tickets_filtered}")
            
            print("   Top 5 técnicos (filtrado):")
            for i, tech in enumerate(ranking_with_filter[:5]):
                name = tech.get("name", "N/A")
                total = tech.get("total", 0)
                level = tech.get("level", "N/A")
                print(f"     {i+1}. {name} - {total} tickets (Nível: {level})")
        else:
            print("   ❌ Ranking filtrado vazio retornado")
            
    except Exception as e:
        print(f"❌ Erro ao testar ranking: {e}")
    
    print("\n=== ANÁLISE FINAL ===")
    print("\n🔍 Possíveis causas do problema:")
    print("1. Campo users_id_tech (campo 4) não está sendo usado corretamente")
    print("2. Técnicos não têm tickets atribuídos no GLPI")
    print("3. Problemas na query de busca de tickets")
    print("4. Filtros de data muito restritivos")
    print("5. Problemas de autenticação ou permissões")
    print("6. Configuração incorreta dos field_ids")
    
    print("\n💡 Próximos passos recomendados:")
    print("1. Verificar se existem tickets no GLPI com técnicos atribuídos")
    print("2. Testar queries diretamente no GLPI")
    print("3. Verificar configuração dos campos (field_ids)")
    print("4. Analisar logs detalhados do backend")
    print("5. Verificar se o perfil técnico (ID 6) está correto")

if __name__ == "__main__":
    debug_zero_tickets_issue()