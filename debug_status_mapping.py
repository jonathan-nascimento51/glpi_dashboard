#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debugar o mapeamento de status que está causando
valores zerados em novos, pendentes e progresso.
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

API_BASE = "http://localhost:5000/api"

def analyze_status_distribution():
    """Analisa a distribuição de status para identificar o problema."""
    print("\n" + "="*80)
    print("🔍 ANÁLISE DA DISTRIBUIÇÃO DE STATUS")
    print("="*80)
    
    try:
        glpi_service = GLPIService()
        
        # Verificar autenticação e field_ids
        if not glpi_service._ensure_authenticated():
            print("❌ Falha na autenticação")
            return
        
        if not glpi_service.discover_field_ids():
            print("❌ Falha na descoberta de field_ids")
            return
        
        print(f"✅ Status map: {glpi_service.status_map}")
        print(f"✅ Service levels: {glpi_service.service_levels}")
        
        # Testar contagem por status SEM filtro de data
        print("\n1️⃣ CONTAGEM POR STATUS SEM FILTRO:")
        status_counts_no_filter = {}
        for status_name, status_id in glpi_service.status_map.items():
            count = glpi_service.get_ticket_count(group_id=None, status_id=status_id)
            status_counts_no_filter[status_name] = count
            print(f"   📊 {status_name} (ID {status_id}): {count} tickets")
        
        total_no_filter = sum(status_counts_no_filter.values())
        print(f"   📊 TOTAL SEM FILTRO: {total_no_filter}")
        
        # Testar contagem por status COM filtro de data (Janeiro 2024)
        print("\n2️⃣ CONTAGEM POR STATUS COM FILTRO (Janeiro 2024):")
        status_counts_with_filter = {}
        for status_name, status_id in glpi_service.status_map.items():
            count = glpi_service.get_ticket_count(
                group_id=None, 
                status_id=status_id,
                start_date='2024-01-01',
                end_date='2024-01-31'
            )
            status_counts_with_filter[status_name] = count
            print(f"   📊 {status_name} (ID {status_id}): {count} tickets")
        
        total_with_filter = sum(status_counts_with_filter.values())
        print(f"   📊 TOTAL COM FILTRO: {total_with_filter}")
        
        # Comparar distribuições
        print("\n3️⃣ COMPARAÇÃO DE DISTRIBUIÇÕES:")
        for status_name in glpi_service.status_map.keys():
            no_filter = status_counts_no_filter.get(status_name, 0)
            with_filter = status_counts_with_filter.get(status_name, 0)
            
            if no_filter > 0:
                percentage = (with_filter / no_filter) * 100
                print(f"   📈 {status_name}: {with_filter}/{no_filter} ({percentage:.1f}%)")
            else:
                print(f"   📈 {status_name}: {with_filter}/{no_filter} (N/A)")
        
        # Verificar se há tickets em Janeiro 2024 com outros status
        print("\n4️⃣ VERIFICANDO TICKETS EM JANEIRO 2024 (todos os status):")
        
        # Fazer uma busca geral com filtro de data para ver todos os status
        search_params = {
            "is_deleted": 0,
            "range": "0-0",
            "criteria[0][field]": "15",  # Data de criação
            "criteria[0][searchtype]": "morethan",
            "criteria[0][value]": "2024-01-01",
            "criteria[1][link]": "AND",
            "criteria[1][field]": "15",
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
                total_january = int(response.headers["Content-Range"].split("/")[-1])
                print(f"   📊 Total de tickets em Janeiro 2024: {total_january}")
                
                if total_january != total_with_filter:
                    print(f"   ⚠️ DISCREPÂNCIA: Soma por status ({total_with_filter}) != Total geral ({total_january})")
                    print(f"   💡 Isso pode indicar que alguns status não estão sendo mapeados corretamente")
            else:
                print("   ❌ Não foi possível obter total geral")
        else:
            print(f"   ❌ Erro na busca geral: {response.status_code if response else 'None'}")
        
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        import traceback
        traceback.print_exc()

def test_raw_glpi_queries():
    """Testa queries GLPI diretas para entender melhor o comportamento."""
    print("\n" + "="*80)
    print("🔧 TESTE DE QUERIES GLPI DIRETAS")
    print("="*80)
    
    try:
        glpi_service = GLPIService()
        
        if not glpi_service._ensure_authenticated():
            print("❌ Falha na autenticação")
            return
        
        if not glpi_service.discover_field_ids():
            print("❌ Falha na descoberta de field_ids")
            return
        
        # Teste 1: Buscar tickets de Janeiro 2024 com detalhes
        print("\n1️⃣ BUSCANDO TICKETS DE JANEIRO 2024 COM DETALHES:")
        
        search_params = {
            "is_deleted": 0,
            "range": "0-9",  # Primeiros 10 tickets
            "criteria[0][field]": "15",  # Data de criação
            "criteria[0][searchtype]": "morethan",
            "criteria[0][value]": "2024-01-01",
            "criteria[1][link]": "AND",
            "criteria[1][field]": "15",
            "criteria[1][searchtype]": "lessthan",
            "criteria[1][value]": "2024-01-31",
            "forcedisplay[0]": "2",   # ID
            "forcedisplay[1]": "12",  # Status
            "forcedisplay[2]": "15",  # Data de criação
            "forcedisplay[3]": "1",   # Nome
        }
        
        response = glpi_service._make_authenticated_request(
            'GET',
            f"{glpi_service.glpi_url}/search/Ticket",
            params=search_params
        )
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                if 'data' in data:
                    print(f"   📊 Encontrados {len(data['data'])} tickets (amostra):")
                    for ticket in data['data'][:5]:  # Mostrar apenas os primeiros 5
                        ticket_id = ticket.get('2', 'N/A')
                        status = ticket.get('12', 'N/A')
                        date_created = ticket.get('15', 'N/A')
                        name = ticket.get('1', 'N/A')
                        print(f"      🎫 ID: {ticket_id}, Status: {status}, Data: {date_created}")
                        print(f"         Nome: {name[:50]}..." if len(str(name)) > 50 else f"         Nome: {name}")
                else:
                    print("   ❌ Nenhum ticket encontrado ou estrutura de dados inesperada")
            except json.JSONDecodeError:
                print(f"   ❌ Erro ao decodificar JSON: {response.text[:200]}...")
        else:
            print(f"   ❌ Erro na busca: {response.status_code if response else 'None'}")
            if response:
                print(f"   📄 Resposta: {response.text[:200]}...")
        
        # Teste 2: Verificar se existem tickets com status específicos em Janeiro
        print("\n2️⃣ VERIFICANDO STATUS ESPECÍFICOS EM JANEIRO 2024:")
        
        # Testar especificamente status "Novo" (ID 1)
        search_params_novo = {
            "is_deleted": 0,
            "range": "0-0",
            "criteria[0][field]": "12",  # Status
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": "1",   # Novo
            "criteria[1][link]": "AND",
            "criteria[1][field]": "15",  # Data de criação
            "criteria[1][searchtype]": "morethan",
            "criteria[1][value]": "2024-01-01",
            "criteria[2][link]": "AND",
            "criteria[2][field]": "15",
            "criteria[2][searchtype]": "lessthan",
            "criteria[2][value]": "2024-01-31"
        }
        
        response = glpi_service._make_authenticated_request(
            'GET',
            f"{glpi_service.glpi_url}/search/Ticket",
            params=search_params_novo
        )
        
        if response and "Content-Range" in response.headers:
            count_novo = int(response.headers["Content-Range"].split("/")[-1])
            print(f"   📊 Tickets 'Novo' em Janeiro 2024: {count_novo}")
        else:
            print("   ❌ Erro ao buscar tickets 'Novo'")
        
    except Exception as e:
        print(f"❌ Erro nos testes de query: {e}")
        import traceback
        traceback.print_exc()

def analyze_aggregation_logic():
    """Analisa a lógica de agregação das métricas."""
    print("\n" + "="*80)
    print("🧮 ANÁLISE DA LÓGICA DE AGREGAÇÃO")
    print("="*80)
    
    try:
        glpi_service = GLPIService()
        
        # Obter métricas brutas por nível com filtro
        print("\n1️⃣ MÉTRICAS BRUTAS POR NÍVEL (Janeiro 2024):")
        raw_metrics = glpi_service._get_metrics_by_level_internal(
            start_date='2024-01-01',
            end_date='2024-01-31'
        )
        
        print("   📊 Métricas brutas por nível:")
        for level_name, level_data in raw_metrics.items():
            print(f"      🏷️ {level_name}: {level_data}")
        
        # Obter métricas gerais com filtro
        print("\n2️⃣ MÉTRICAS GERAIS (Janeiro 2024):")
        general_metrics = glpi_service._get_general_metrics_internal(
            start_date='2024-01-01',
            end_date='2024-01-31'
        )
        
        print("   📊 Métricas gerais:")
        for status_name, count in general_metrics.items():
            print(f"      🏷️ {status_name}: {count}")
        
        # Simular a agregação manual
        print("\n3️⃣ SIMULAÇÃO DA AGREGAÇÃO:")
        
        # Agregação dos totais por status (apenas para níveis)
        totals = {
            "novos": 0,
            "pendentes": 0,
            "progresso": 0,
            "resolvidos": 0
        }
        
        for level_name, level_data in raw_metrics.items():
            # Novo
            novos = level_data.get("Novo", 0)
            totals["novos"] += novos
            print(f"      📈 {level_name} - Novos: {novos}")
            
            # Progresso (soma de Processando atribuído e planejado)
            processando_atribuido = level_data.get("Processando (atribuído)", 0)
            processando_planejado = level_data.get("Processando (planejado)", 0)
            progresso = processando_atribuido + processando_planejado
            totals["progresso"] += progresso
            print(f"      📈 {level_name} - Progresso: {progresso} (atrib: {processando_atribuido}, plan: {processando_planejado})")
            
            # Pendente
            pendentes = level_data.get("Pendente", 0)
            totals["pendentes"] += pendentes
            print(f"      📈 {level_name} - Pendentes: {pendentes}")
            
            # Resolvidos (soma de Solucionado e Fechado)
            solucionado = level_data.get("Solucionado", 0)
            fechado = level_data.get("Fechado", 0)
            resolvidos = solucionado + fechado
            totals["resolvidos"] += resolvidos
            print(f"      📈 {level_name} - Resolvidos: {resolvidos} (soluc: {solucionado}, fech: {fechado})")
        
        print(f"\n   📊 TOTAIS AGREGADOS DOS NÍVEIS: {totals}")
        
        # Comparar com métricas gerais
        general_novos = general_metrics.get("Novo", 0)
        general_pendentes = general_metrics.get("Pendente", 0)
        general_progresso = general_metrics.get("Processando (atribuído)", 0) + general_metrics.get("Processando (planejado)", 0)
        general_resolvidos = general_metrics.get("Solucionado", 0) + general_metrics.get("Fechado", 0)
        
        print(f"\n   📊 MÉTRICAS GERAIS CALCULADAS:")
        print(f"      🏷️ Novos: {general_novos}")
        print(f"      🏷️ Pendentes: {general_pendentes}")
        print(f"      🏷️ Progresso: {general_progresso}")
        print(f"      🏷️ Resolvidos: {general_resolvidos}")
        
        # Identificar discrepâncias
        print(f"\n4️⃣ IDENTIFICAÇÃO DE DISCREPÂNCIAS:")
        if totals["novos"] != general_novos:
            print(f"   ⚠️ DISCREPÂNCIA em Novos: Níveis={totals['novos']}, Geral={general_novos}")
        if totals["pendentes"] != general_pendentes:
            print(f"   ⚠️ DISCREPÂNCIA em Pendentes: Níveis={totals['pendentes']}, Geral={general_pendentes}")
        if totals["progresso"] != general_progresso:
            print(f"   ⚠️ DISCREPÂNCIA em Progresso: Níveis={totals['progresso']}, Geral={general_progresso}")
        if totals["resolvidos"] != general_resolvidos:
            print(f"   ⚠️ DISCREPÂNCIA em Resolvidos: Níveis={totals['resolvidos']}, Geral={general_resolvidos}")
        
        if all([
            totals["novos"] == general_novos,
            totals["pendentes"] == general_pendentes,
            totals["progresso"] == general_progresso,
            totals["resolvidos"] == general_resolvidos
        ]):
            print("   ✅ Nenhuma discrepância encontrada na agregação")
        
    except Exception as e:
        print(f"❌ Erro na análise de agregação: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Função principal para executar todos os testes."""
    print("🚀 INICIANDO ANÁLISE DETALHADA DO MAPEAMENTO DE STATUS")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Análise 1: Distribuição de status
    analyze_status_distribution()
    
    # Análise 2: Queries GLPI diretas
    test_raw_glpi_queries()
    
    # Análise 3: Lógica de agregação
    analyze_aggregation_logic()
    
    print("\n" + "="*80)
    print("✅ ANÁLISE DETALHADA CONCLUÍDA")
    print("="*80)
    print("\n📋 CONCLUSÕES ESPERADAS:")
    print("   1. Identificar se tickets existem em Janeiro 2024 com status diferentes de 'resolvido'")
    print("   2. Verificar se o mapeamento de status está correto")
    print("   3. Confirmar se a agregação está funcionando corretamente")
    print("   4. Identificar se o problema é nos dados ou na lógica")

if __name__ == "__main__":
    main()