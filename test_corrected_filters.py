#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para verificar se as correções nos filtros de data do GLPI estão funcionando.
Este script testa os filtros de data corrigidos no serviço GLPI.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.glpi_service import GLPIService
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_corrected_date_filters():
    """Testa os filtros de data corrigidos"""
    print("=== TESTE DOS FILTROS DE DATA CORRIGIDOS ===")
    
    # Inicializar serviço GLPI
    glpi_service = GLPIService()
    
    # Testar autenticação
    if not glpi_service._ensure_authenticated():
        print("❌ Falha na autenticação")
        return False
    
    print("✅ Autenticação bem-sucedida")
    
    # Descobrir field IDs
    if not glpi_service.discover_field_ids():
        print("❌ Falha ao descobrir field IDs")
        return False
    
    print("✅ Field IDs descobertos")
    
    # Testar contagem sem filtros de data
    print("\n--- Teste sem filtros de data ---")
    total_sem_filtro = glpi_service.get_ticket_count(89, 1)  # N1, Novo
    print(f"Total de tickets N1/Novo sem filtro: {total_sem_filtro}")
    
    # Testar filtros de data
    print("\n--- Teste com filtros de data ---")
    
    # Teste 1: Filtro de data de início (últimos 30 dias)
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    total_30_dias = glpi_service.get_ticket_count(89, 1, start_date=start_date)
    print(f"Tickets N1/Novo dos últimos 30 dias: {total_30_dias}")
    
    # Teste 2: Filtro de data de fim (até ontem)
    end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    total_ate_ontem = glpi_service.get_ticket_count(89, 1, end_date=end_date)
    print(f"Tickets N1/Novo até ontem: {total_ate_ontem}")
    
    # Teste 3: Filtro de intervalo (últimos 7 dias)
    start_date_7d = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    end_date_hoje = datetime.now().strftime('%Y-%m-%d')
    total_7_dias = glpi_service.get_ticket_count(89, 1, start_date=start_date_7d, end_date=end_date_hoje)
    print(f"Tickets N1/Novo dos últimos 7 dias: {total_7_dias}")
    
    # Teste 4: Filtro muito antigo (deve retornar todos ou quase todos)
    start_date_antigo = "2020-01-01"
    total_desde_2020 = glpi_service.get_ticket_count(89, 1, start_date=start_date_antigo)
    print(f"Tickets N1/Novo desde 2020: {total_desde_2020}")
    
    # Teste 5: Filtro futuro (deve retornar 0)
    start_date_futuro = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    total_futuro = glpi_service.get_ticket_count(89, 1, start_date=start_date_futuro)
    print(f"Tickets N1/Novo do futuro: {total_futuro}")
    
    print("\n--- Análise dos resultados ---")
    
    # Verificar se os filtros estão funcionando
    filtros_funcionando = True
    
    if total_sem_filtro is None:
        print("❌ Erro: Não foi possível obter total sem filtro")
        filtros_funcionando = False
    
    if total_desde_2020 is None or total_desde_2020 == 0:
        print("❌ Erro: Filtro desde 2020 não funcionou")
        filtros_funcionando = False
    elif total_desde_2020 != total_sem_filtro:
        print(f"✅ Filtro desde 2020 funcionou: {total_desde_2020} != {total_sem_filtro}")
    else:
        print(f"⚠️  Filtro desde 2020 pode não estar funcionando: {total_desde_2020} == {total_sem_filtro}")
    
    if total_futuro is None:
        print("❌ Erro: Filtro futuro retornou None")
        filtros_funcionando = False
    elif total_futuro == 0:
        print("✅ Filtro futuro funcionou: retornou 0 como esperado")
    else:
        print(f"⚠️  Filtro futuro pode não estar funcionando: retornou {total_futuro}")
    
    if total_7_dias is not None and total_30_dias is not None:
        if total_7_dias <= total_30_dias:
            print(f"✅ Lógica de filtros consistente: 7 dias ({total_7_dias}) <= 30 dias ({total_30_dias})")
        else:
            print(f"⚠️  Lógica de filtros inconsistente: 7 dias ({total_7_dias}) > 30 dias ({total_30_dias})")
    
    print("\n--- Teste de métricas por nível com filtros ---")
    
    # Testar métricas por nível com filtros de data
    start_date_metrics = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    end_date_metrics = datetime.now().strftime('%Y-%m-%d')
    
    # Usar método interno para testar com filtros
    metrics_filtered = glpi_service._get_metrics_by_level_internal(start_date_metrics, end_date_metrics)
    print(f"Métricas filtradas (últimos 7 dias): {metrics_filtered}")
    
    if filtros_funcionando:
        print("\n🎉 TESTE CONCLUÍDO: Filtros de data parecem estar funcionando!")
        return True
    else:
        print("\n❌ TESTE FALHOU: Problemas detectados nos filtros de data")
        return False

if __name__ == "__main__":
    try:
        success = test_corrected_date_filters()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Erro durante o teste: {e}")
        sys.exit(1)