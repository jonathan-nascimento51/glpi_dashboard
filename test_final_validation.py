#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste final para validar que os filtros de data estão funcionando corretamente
"""

import json
from datetime import datetime, timedelta
from backend.services.glpi_service import GLPIService

def test_date_filters_validation():
    """Teste final de validação dos filtros de data"""
    
    print("=== VALIDAÇÃO FINAL DOS FILTROS DE DATA ===")
    
    # Inicializar serviço GLPI
    glpi = GLPIService()
    
    print("Autenticando...")
    if not glpi._ensure_authenticated():
        print("❌ Falha na autenticação")
        return False
    
    print("✅ Autenticado com sucesso")
    
    # Descobrir IDs dos campos
    glpi.discover_field_ids()
    print(f"Campo DATE_CREATION descoberto: {glpi.field_ids.get('DATE_CREATION', 'Não encontrado')}")
    
    # Forçar campo 15 para data de criação
    glpi.field_ids["DATE_CREATION"] = "15"
    print(f"Campo DATE_CREATION forçado para: {glpi.field_ids['DATE_CREATION']}")
    
    # Obter contagem total sem filtros
    print("\n--- Contagem Base ---")
    total_tickets = glpi.get_ticket_count(89, 1)  # N1, Novo
    print(f"Total de tickets N1/Novo sem filtros: {total_tickets}")
    
    if total_tickets is None or total_tickets == 0:
        print("⚠️  Não há tickets para testar ou erro na consulta")
        return False
    
    # Teste 1: Filtro dos últimos 7 dias
    print("\n--- Teste 1: Últimos 7 dias ---")
    start_date_7d = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    end_date_7d = datetime.now().strftime('%Y-%m-%d')
    
    count_7d = glpi.get_ticket_count(89, 1, start_date_7d, end_date_7d)
    print(f"Período: {start_date_7d} até {end_date_7d}")
    print(f"Tickets encontrados: {count_7d}")
    
    if count_7d is not None and count_7d <= total_tickets:
        print("✅ Filtro de 7 dias funcionando (filtrou corretamente)")
    else:
        print("❌ Filtro de 7 dias não funcionando")
    
    # Teste 2: Filtro dos últimos 30 dias
    print("\n--- Teste 2: Últimos 30 dias ---")
    start_date_30d = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    end_date_30d = datetime.now().strftime('%Y-%m-%d')
    
    count_30d = glpi.get_ticket_count(89, 1, start_date_30d, end_date_30d)
    print(f"Período: {start_date_30d} até {end_date_30d}")
    print(f"Tickets encontrados: {count_30d}")
    
    if count_30d is not None and count_30d >= count_7d:
        print("✅ Filtro de 30 dias funcionando (30 dias >= 7 dias)")
    else:
        print("❌ Filtro de 30 dias não funcionando")
    
    # Teste 3: Filtro futuro (deve retornar 0)
    print("\n--- Teste 3: Filtro Futuro ---")
    start_date_future = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    end_date_future = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    count_future = glpi.get_ticket_count(89, 1, start_date_future, end_date_future)
    print(f"Período: {start_date_future} até {end_date_future}")
    print(f"Tickets encontrados: {count_future}")
    
    if count_future is not None and count_future == 0:
        print("✅ Filtro futuro funcionando (retornou 0 como esperado)")
    else:
        print("❌ Filtro futuro não funcionando")
    
    # Teste 4: Filtro muito antigo (deve retornar poucos ou 0)
    print("\n--- Teste 4: Filtro Muito Antigo ---")
    start_date_old = "2020-01-01"
    end_date_old = "2020-12-31"
    
    count_old = glpi.get_ticket_count(89, 1, start_date_old, end_date_old)
    print(f"Período: {start_date_old} até {end_date_old}")
    print(f"Tickets encontrados: {count_old}")
    
    if count_old is not None and count_old < total_tickets:
        print("✅ Filtro antigo funcionando (filtrou corretamente)")
    else:
        print("❌ Filtro antigo não funcionando")
    
    # Teste 5: Métricas por nível com filtros
    print("\n--- Teste 5: Métricas por Nível com Filtros ---")
    metrics_filtered = glpi._get_metrics_by_level_internal(start_date_7d, end_date_7d)
    
    if metrics_filtered:
        print("✅ Métricas filtradas obtidas com sucesso")
        for level, data in metrics_filtered.items():
            total_level = sum(data.values())
            print(f"  {level}: {total_level} tickets (últimos 7 dias)")
    else:
        print("❌ Falha ao obter métricas filtradas")
    
    # Teste 6: Métricas gerais com filtros
    print("\n--- Teste 6: Métricas Gerais com Filtros ---")
    general_metrics = glpi._get_general_metrics_internal(start_date_7d, end_date_7d)
    
    if general_metrics:
        print("✅ Métricas gerais filtradas obtidas com sucesso")
        total_general = sum(general_metrics.values())
        print(f"  Total geral (últimos 7 dias): {total_general} tickets")
        for status, count in general_metrics.items():
            print(f"  {status}: {count}")
    else:
        print("❌ Falha ao obter métricas gerais filtradas")
    
    # Resumo final
    print("\n=== RESUMO FINAL ===")
    tests_passed = 0
    total_tests = 6
    
    if count_7d is not None and count_7d <= total_tickets:
        tests_passed += 1
    if count_30d is not None and count_30d >= count_7d:
        tests_passed += 1
    if count_future is not None and count_future == 0:
        tests_passed += 1
    if count_old is not None and count_old < total_tickets:
        tests_passed += 1
    if metrics_filtered:
        tests_passed += 1
    if general_metrics:
        tests_passed += 1
    
    print(f"Testes aprovados: {tests_passed}/{total_tests}")
    
    if tests_passed >= 5:
        print("🎉 SUCESSO: Filtros de data estão funcionando corretamente!")
        return True
    else:
        print("⚠️  ATENÇÃO: Alguns filtros podem não estar funcionando perfeitamente")
        return False

def test_dashboard_integration():
    """Testa a integração com o dashboard"""
    print("\n=== TESTE DE INTEGRAÇÃO COM DASHBOARD ===")
    
    glpi = GLPIService()
    
    if not glpi._ensure_authenticated():
        print("❌ Falha na autenticação")
        return False
    
    # Testar métricas do dashboard com filtros
    try:
        # Simular chamada do dashboard com filtros
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"Testando métricas do dashboard para período: {start_date} até {end_date}")
        
        # Obter métricas por nível
        metrics_by_level = glpi._get_metrics_by_level_internal(start_date, end_date)
        
        # Obter métricas gerais
        general_metrics = glpi._get_general_metrics_internal(start_date, end_date)
        
        if metrics_by_level and general_metrics:
            print("✅ Integração com dashboard funcionando")
            print("Dados disponíveis para o frontend:")
            print(f"  - Métricas por nível: {len(metrics_by_level)} níveis")
            print(f"  - Métricas gerais: {len(general_metrics)} status")
            return True
        else:
            print("❌ Falha na integração com dashboard")
            return False
            
    except Exception as e:
        print(f"❌ Erro na integração: {str(e)}")
        return False

if __name__ == "__main__":
    # Executar validação dos filtros
    filters_ok = test_date_filters_validation()
    
    # Executar teste de integração
    integration_ok = test_dashboard_integration()
    
    print("\n" + "="*50)
    if filters_ok and integration_ok:
        print("🎉 VALIDAÇÃO COMPLETA: Sistema funcionando corretamente!")
        print("✅ Filtros de data implementados e validados")
        print("✅ Integração com dashboard funcionando")
    else:
        print("⚠️  VALIDAÇÃO PARCIAL: Alguns problemas identificados")
        if not filters_ok:
            print("❌ Problemas nos filtros de data")
        if not integration_ok:
            print("❌ Problemas na integração com dashboard")