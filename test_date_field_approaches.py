#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar diferentes abordagens de filtro de data
e entender qual campo usar para obter resultados mais úteis.
"""

import requests
import json
from datetime import datetime, timedelta
import sys
import os

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.glpi_service import GLPIService
from backend.config.settings import active_config

def test_different_date_fields():
    """Testa diferentes campos de data para entender qual usar."""
    print("\n" + "="*80)
    print("📅 TESTE DE DIFERENTES CAMPOS DE DATA")
    print("="*80)
    
    try:
        glpi_service = GLPIService()
        
        if not glpi_service._ensure_authenticated():
            print("❌ Falha na autenticação")
            return
        
        if not glpi_service.discover_field_ids():
            print("❌ Falha na descoberta de field_ids")
            return
        
        # Campos de data comuns no GLPI
        date_fields = {
            "15": "Data de criação (date)",
            "19": "Data de modificação (date_mod)",
            "18": "Data de solução (solvedate)",
            "17": "Data de fechamento (closedate)",
            "16": "Data de vencimento (time_to_resolve)"
        }
        
        print("\n1️⃣ TESTANDO DIFERENTES CAMPOS DE DATA:")
        
        for field_id, field_name in date_fields.items():
            print(f"\n   📊 Testando {field_name} (campo {field_id}):")
            
            # Buscar tickets com este campo de data em Janeiro 2024
            search_params = {
                "is_deleted": 0,
                "range": "0-0",
                "criteria[0][field]": field_id,
                "criteria[0][searchtype]": "morethan",
                "criteria[0][value]": "2024-01-01",
                "criteria[1][link]": "AND",
                "criteria[1][field]": field_id,
                "criteria[1][searchtype]": "lessthan",
                "criteria[1][value]": "2024-01-31"
            }
            
            response = glpi_service._make_authenticated_request(
                'GET',
                f"{glpi_service.glpi_url}/search/Ticket",
                params=search_params
            )
            
            if response and response.status_code in [200, 206]:
                if "Content-Range" in response.headers:
                    total = int(response.headers["Content-Range"].split("/")[-1])
                    print(f"      ✅ Total de tickets: {total}")
                    
                    # Se encontrou tickets, buscar distribuição por status
                    if total > 0:
                        print(f"      📈 Distribuição por status:")
                        for status_name, status_id in glpi_service.status_map.items():
                            status_params = search_params.copy()
                            status_params["criteria[2][link]"] = "AND"
                            status_params["criteria[2][field]"] = "12"  # Status
                            status_params["criteria[2][searchtype]"] = "equals"
                            status_params["criteria[2][value]"] = str(status_id)
                            
                            status_response = glpi_service._make_authenticated_request(
                                'GET',
                                f"{glpi_service.glpi_url}/search/Ticket",
                                params=status_params
                            )
                            
                            if status_response and "Content-Range" in status_response.headers:
                                status_count = int(status_response.headers["Content-Range"].split("/")[-1])
                                if status_count > 0:
                                    print(f"         🏷️ {status_name}: {status_count}")
                else:
                    print(f"      ❌ Sem Content-Range no cabeçalho")
            else:
                print(f"      ❌ Erro na busca: {response.status_code if response else 'None'}")
        
    except Exception as e:
        print(f"❌ Erro no teste de campos de data: {e}")
        import traceback
        traceback.print_exc()

def test_current_vs_historical_approach():
    """Compara abordagem atual (data de criação) vs histórica (data de modificação)."""
    print("\n" + "="*80)
    print("🔄 COMPARAÇÃO: ATUAL vs HISTÓRICO")
    print("="*80)
    
    try:
        glpi_service = GLPIService()
        
        if not glpi_service._ensure_authenticated():
            print("❌ Falha na autenticação")
            return
        
        if not glpi_service.discover_field_ids():
            print("❌ Falha na descoberta de field_ids")
            return
        
        print("\n1️⃣ ABORDAGEM ATUAL (Data de Criação - Campo 15):")
        print("   📝 Mostra tickets criados no período, independente do status atual")
        
        # Buscar por data de criação
        creation_totals = {}
        for status_name, status_id in glpi_service.status_map.items():
            count = glpi_service.get_ticket_count(
                group_id=None,
                status_id=status_id,
                start_date='2024-01-01',
                end_date='2024-01-31'
            )
            if count > 0:
                creation_totals[status_name] = count
                print(f"      🏷️ {status_name}: {count}")
        
        creation_total = sum(creation_totals.values())
        print(f"   📊 Total por data de criação: {creation_total}")
        
        print("\n2️⃣ ABORDAGEM ALTERNATIVA (Data de Modificação - Campo 19):")
        print("   📝 Mostra tickets modificados no período (pode incluir mudanças de status)")
        
        # Buscar por data de modificação
        modification_totals = {}
        for status_name, status_id in glpi_service.status_map.items():
            search_params = {
                "is_deleted": 0,
                "range": "0-0",
                "criteria[0][field]": "12",  # Status
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": str(status_id),
                "criteria[1][link]": "AND",
                "criteria[1][field]": "19",  # Data de modificação
                "criteria[1][searchtype]": "morethan",
                "criteria[1][value]": "2024-01-01",
                "criteria[2][link]": "AND",
                "criteria[2][field]": "19",
                "criteria[2][searchtype]": "lessthan",
                "criteria[2][value]": "2024-01-31"
            }
            
            response = glpi_service._make_authenticated_request(
                'GET',
                f"{glpi_service.glpi_url}/search/Ticket",
                params=search_params
            )
            
            if response and "Content-Range" in response.headers:
                count = int(response.headers["Content-Range"].split("/")[-1])
                if count > 0:
                    modification_totals[status_name] = count
                    print(f"      🏷️ {status_name}: {count}")
        
        modification_total = sum(modification_totals.values())
        print(f"   📊 Total por data de modificação: {modification_total}")
        
        print("\n3️⃣ ABORDAGEM SNAPSHOT (Status Atual sem Filtro de Data):")
        print("   📝 Mostra o estado atual de todos os tickets")
        
        # Buscar status atual sem filtro de data
        current_totals = {}
        for status_name, status_id in glpi_service.status_map.items():
            count = glpi_service.get_ticket_count(group_id=None, status_id=status_id)
            if count > 0:
                current_totals[status_name] = count
                print(f"      🏷️ {status_name}: {count}")
        
        current_total = sum(current_totals.values())
        print(f"   📊 Total atual: {current_total}")
        
        print("\n4️⃣ ANÁLISE COMPARATIVA:")
        print(f"   📊 Criação: {creation_total} tickets")
        print(f"   📊 Modificação: {modification_total} tickets")
        print(f"   📊 Atual: {current_total} tickets")
        
        if creation_total == modification_total == current_total:
            print("   ✅ Todos os totais são iguais")
        else:
            print("   ⚠️ Totais diferentes - isso é esperado e normal")
        
        print("\n5️⃣ RECOMENDAÇÃO:")
        if len(creation_totals) == 1 and 'Fechado' in creation_totals:
            print("   💡 PROBLEMA IDENTIFICADO: Filtro por data de criação mostra apenas tickets fechados")
            print("   💡 SOLUÇÃO: Considerar usar data de modificação ou status atual")
            print("   💡 ALTERNATIVA: Usar período mais recente ou remover filtro de data")
        else:
            print("   ✅ Filtro por data de criação parece estar funcionando corretamente")
        
    except Exception as e:
        print(f"❌ Erro na comparação: {e}")
        import traceback
        traceback.print_exc()

def test_recent_period():
    """Testa um período mais recente para ver se há mais diversidade de status."""
    print("\n" + "="*80)
    print("🕐 TESTE COM PERÍODO MAIS RECENTE")
    print("="*80)
    
    try:
        glpi_service = GLPIService()
        
        if not glpi_service._ensure_authenticated():
            print("❌ Falha na autenticação")
            return
        
        if not glpi_service.discover_field_ids():
            print("❌ Falha na descoberta de field_ids")
            return
        
        # Testar últimos 30 dias
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        print(f"\n1️⃣ PERÍODO: {start_str} a {end_str} (últimos 30 dias)")
        
        recent_totals = {}
        for status_name, status_id in glpi_service.status_map.items():
            count = glpi_service.get_ticket_count(
                group_id=None,
                status_id=status_id,
                start_date=start_str,
                end_date=end_str
            )
            if count > 0:
                recent_totals[status_name] = count
                print(f"   🏷️ {status_name}: {count}")
        
        recent_total = sum(recent_totals.values())
        print(f"\n   📊 Total nos últimos 30 dias: {recent_total}")
        
        # Testar últimos 7 dias
        start_date_week = end_date - timedelta(days=7)
        start_str_week = start_date_week.strftime('%Y-%m-%d')
        
        print(f"\n2️⃣ PERÍODO: {start_str_week} a {end_str} (últimos 7 dias)")
        
        week_totals = {}
        for status_name, status_id in glpi_service.status_map.items():
            count = glpi_service.get_ticket_count(
                group_id=None,
                status_id=status_id,
                start_date=start_str_week,
                end_date=end_str
            )
            if count > 0:
                week_totals[status_name] = count
                print(f"   🏷️ {status_name}: {count}")
        
        week_total = sum(week_totals.values())
        print(f"\n   📊 Total nos últimos 7 dias: {week_total}")
        
        print("\n3️⃣ ANÁLISE:")
        if len(recent_totals) > 1:
            print("   ✅ Período recente mostra diversidade de status")
            print("   💡 O problema pode ser específico do período de Janeiro 2024")
        else:
            print("   ⚠️ Mesmo em período recente, poucos status aparecem")
            print("   💡 Pode indicar que a maioria dos tickets é fechada rapidamente")
        
    except Exception as e:
        print(f"❌ Erro no teste de período recente: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Função principal para executar todos os testes."""
    print("🚀 INICIANDO TESTE DE ABORDAGENS DE FILTRO DE DATA")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Teste 1: Diferentes campos de data
    test_different_date_fields()
    
    # Teste 2: Comparação de abordagens
    test_current_vs_historical_approach()
    
    # Teste 3: Período mais recente
    test_recent_period()
    
    print("\n" + "="*80)
    print("✅ TESTE DE ABORDAGENS CONCLUÍDO")
    print("="*80)
    print("\n📋 CONCLUSÕES ESPERADAS:")
    print("   1. Identificar qual campo de data é mais apropriado")
    print("   2. Entender se o problema é específico do período de Janeiro 2024")
    print("   3. Determinar se devemos mudar a abordagem de filtro")
    print("   4. Verificar se períodos mais recentes têm mais diversidade")

if __name__ == "__main__":
    main()