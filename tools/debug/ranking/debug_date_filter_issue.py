#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debugar e corrigir o problema dos filtros de data
que estão zerando os valores das métricas.
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

def test_api_directly():
    """Testa a API diretamente para identificar o problema."""
    print("\n" + "="*80)
    print("🔍 ANÁLISE DIRETA DO PROBLEMA DOS FILTROS DE DATA")
    print("="*80)
    
    # Teste 1: Sem filtros
    print("\n1️⃣ TESTE SEM FILTROS:")
    response = requests.get(f"{API_BASE}/metrics")
    if response.status_code == 200:
        data = response.json()
        if data.get('success') and 'data' in data:
            geral = data['data']['niveis']['geral']
            print(f"   ✅ Total: {geral['total']}")
            print(f"   ✅ Novos: {geral['novos']}")
            print(f"   ✅ Pendentes: {geral['pendentes']}")
            print(f"   ✅ Progresso: {geral['progresso']}")
            print(f"   ✅ Resolvidos: {geral['resolvidos']}")
        else:
            print(f"   ❌ Resposta inválida: {data}")
    else:
        print(f"   ❌ Erro HTTP: {response.status_code}")
    
    # Teste 2: Com filtros de data (Janeiro 2024)
    print("\n2️⃣ TESTE COM FILTROS (Janeiro 2024):")
    params = {'start_date': '2024-01-01', 'end_date': '2024-01-31'}
    response = requests.get(f"{API_BASE}/metrics", params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get('success') and 'data' in data:
            geral = data['data']['niveis']['geral']
            filtros = data['data'].get('filtros_aplicados', {})
            print(f"   📅 Filtros aplicados: {filtros}")
            print(f"   ✅ Total: {geral['total']}")
            print(f"   ✅ Novos: {geral['novos']}")
            print(f"   ✅ Pendentes: {geral['pendentes']}")
            print(f"   ✅ Progresso: {geral['progresso']}")
            print(f"   ✅ Resolvidos: {geral['resolvidos']}")
            
            # Verificar se os valores estão zerados
            total_filtrado = geral['total']
            if total_filtrado == 0:
                print("   ⚠️ PROBLEMA IDENTIFICADO: Filtros estão zerando os valores!")
            else:
                print(f"   ✅ Filtros funcionando: {total_filtrado} tickets encontrados")
        else:
            print(f"   ❌ Resposta inválida: {data}")
    else:
        print(f"   ❌ Erro HTTP: {response.status_code}")

def test_glpi_service_directly():
    """Testa o GLPIService diretamente para identificar onde está o problema."""
    print("\n" + "="*80)
    print("🔧 TESTE DIRETO DO GLPI SERVICE")
    print("="*80)
    
    try:
        glpi_service = GLPIService()
        
        # Teste 1: Métricas sem filtro
        print("\n1️⃣ MÉTRICAS SEM FILTRO:")
        metrics_no_filter = glpi_service.get_dashboard_metrics()
        if metrics_no_filter and metrics_no_filter.get('success'):
            geral = metrics_no_filter['data']['niveis']['geral']
            print(f"   ✅ Total sem filtro: {geral['total']}")
        else:
            print(f"   ❌ Erro ao obter métricas sem filtro: {metrics_no_filter}")
        
        # Teste 2: Métricas com filtro de data
        print("\n2️⃣ MÉTRICAS COM FILTRO DE DATA:")
        metrics_with_filter = glpi_service.get_dashboard_metrics_with_date_filter(
            start_date='2024-01-01',
            end_date='2024-01-31'
        )
        if metrics_with_filter and metrics_with_filter.get('success'):
            geral = metrics_with_filter['data']['niveis']['geral']
            print(f"   ✅ Total com filtro: {geral['total']}")
            print(f"   📅 Filtros aplicados: {metrics_with_filter['data'].get('filtros_aplicados')}")
            
            # Comparar resultados
            total_sem_filtro = metrics_no_filter['data']['niveis']['geral']['total']
            total_com_filtro = geral['total']
            
            if total_com_filtro == 0 and total_sem_filtro > 0:
                print("   🚨 PROBLEMA CONFIRMADO: Filtros estão zerando os valores!")
                return True
            elif total_com_filtro > 0:
                print(f"   ✅ Filtros funcionando: {total_com_filtro}/{total_sem_filtro} tickets")
                return False
        else:
            print(f"   ❌ Erro ao obter métricas com filtro: {metrics_with_filter}")
            
    except Exception as e:
        print(f"   ❌ Erro no teste do GLPI Service: {e}")
        return None
    
    return None

def analyze_filter_logic():
    """Analisa a lógica de filtros para identificar o problema específico."""
    print("\n" + "="*80)
    print("🔍 ANÁLISE DA LÓGICA DE FILTROS")
    print("="*80)
    
    try:
        glpi_service = GLPIService()
        
        # Verificar se a autenticação está funcionando
        print("\n1️⃣ VERIFICANDO AUTENTICAÇÃO:")
        if glpi_service._ensure_authenticated():
            print("   ✅ Autenticação bem-sucedida")
        else:
            print("   ❌ Falha na autenticação")
            return
        
        # Verificar descoberta de field_ids
        print("\n2️⃣ VERIFICANDO DESCOBERTA DE FIELD_IDS:")
        if glpi_service.discover_field_ids():
            print(f"   ✅ Field IDs descobertos: {glpi_service.field_ids}")
        else:
            print("   ❌ Falha na descoberta de field_ids")
            return
        
        # Testar contagem de tickets com filtro específico
        print("\n3️⃣ TESTANDO CONTAGEM DE TICKETS COM FILTRO:")
        
        # Testar para status "Novo" (ID 1) sem filtro de data
        count_no_filter = glpi_service.get_ticket_count(group_id=None, status_id=1)
        print(f"   📊 Tickets 'Novo' sem filtro: {count_no_filter}")
        
        # Testar para status "Novo" (ID 1) com filtro de data
        count_with_filter = glpi_service.get_ticket_count(
            group_id=None, 
            status_id=1, 
            start_date='2024-01-01', 
            end_date='2024-01-31'
        )
        print(f"   📊 Tickets 'Novo' com filtro Jan/2024: {count_with_filter}")
        
        if count_with_filter == 0 and count_no_filter > 0:
            print("   🚨 PROBLEMA IDENTIFICADO: Filtro de data está zerando a contagem!")
            print("   🔧 Possíveis causas:")
            print("      - Formato de data incorreto na query GLPI")
            print("      - Campo de data incorreto (field_id)")
            print("      - Operadores de comparação incorretos (morethan/lessthan)")
            print("      - Dados não existem no período especificado")
            
            # Testar com período mais amplo
            print("\n4️⃣ TESTANDO COM PERÍODO MAIS AMPLO (2023-2025):")
            count_wide_range = glpi_service.get_ticket_count(
                group_id=None, 
                status_id=1, 
                start_date='2023-01-01', 
                end_date='2025-12-31'
            )
            print(f"   📊 Tickets 'Novo' com filtro amplo: {count_wide_range}")
            
            if count_wide_range > 0:
                print("   💡 DIAGNÓSTICO: Dados existem, problema é no período específico")
            else:
                print("   💡 DIAGNÓSTICO: Problema na lógica de filtro de data")
        
    except Exception as e:
        print(f"   ❌ Erro na análise: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Função principal para executar todos os testes."""
    print("🚀 INICIANDO DIAGNÓSTICO DO PROBLEMA DOS FILTROS DE DATA")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Teste 1: API diretamente
    test_api_directly()
    
    # Teste 2: GLPI Service diretamente
    problem_confirmed = test_glpi_service_directly()
    
    # Teste 3: Análise detalhada se problema confirmado
    if problem_confirmed:
        analyze_filter_logic()
    
    print("\n" + "="*80)
    print("✅ DIAGNÓSTICO CONCLUÍDO")
    print("="*80)
    print("\n📋 PRÓXIMOS PASSOS:")
    print("   1. Verificar logs do backend para erros específicos")
    print("   2. Validar formato de data na query GLPI")
    print("   3. Confirmar field_id correto para data de criação")
    print("   4. Testar query GLPI manualmente")
    print("   5. Implementar correção baseada nos achados")

if __name__ == "__main__":
    main()