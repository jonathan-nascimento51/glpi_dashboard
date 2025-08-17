#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de integração do dashboard principal com a nova abordagem baseada em hierarquia.
Verifica se os métodos modificados funcionam corretamente.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService
import json
from datetime import datetime, timedelta

def test_dashboard_integration():
    """Testa a integração do dashboard com os novos métodos baseados em hierarquia."""
    
    print("=== TESTE DE INTEGRAÇÃO DO DASHBOARD ===")
    print(f"Iniciado em: {datetime.now()}")
    print()
    
    # Inicializar serviço GLPI
    glpi_service = GLPIService()
    
    try:
        # 1. Testar autenticação
        print("1. Testando autenticação...")
        if not glpi_service.authenticate():
            print("❌ Falha na autenticação")
            return False
        print("✅ Autenticação bem-sucedida")
        print()
        
        # 2. Testar get_metrics_by_level (método principal usado no dashboard)
        print("2. Testando get_metrics_by_level...")
        metrics_by_level = glpi_service.get_metrics_by_level()
        
        if not metrics_by_level:
            print("❌ Falha ao obter métricas por nível")
            return False
            
        print("✅ Métricas por nível obtidas com sucesso")
        print(f"Estrutura: {type(metrics_by_level)}")
        
        if isinstance(metrics_by_level, dict):
            print(f"Níveis encontrados: {list(metrics_by_level.keys())}")
            total_tickets = sum(level_data.get('total', 0) for level_data in metrics_by_level.values() if isinstance(level_data, dict))
            print(f"Total de tickets encontrados: {total_tickets}")
        print()
        
        # 3. Testar get_general_metrics (método usado na página principal)
        print("3. Testando get_general_metrics...")
        general_metrics = glpi_service.get_general_metrics()
        
        if not general_metrics:
            print("❌ Falha ao obter métricas gerais")
            return False
            
        print("✅ Métricas gerais obtidas com sucesso")
        print(f"Estrutura: {type(general_metrics)}")
        
        # Verificar se contém dados esperados
        if isinstance(general_metrics, dict):
            if 'data' in general_metrics:
                data = general_metrics['data']
                if 'metrics_by_level' in data:
                    level_metrics = data['metrics_by_level']
                    total_from_general = sum(level.get('total', 0) for level in level_metrics.values() if isinstance(level, dict))
                    print(f"Total de tickets nas métricas gerais: {total_from_general}")
        print()
        
        # 4. Testar get_dashboard_metrics_with_date_filter (método usado com filtros de data)
        print("4. Testando get_dashboard_metrics_with_date_filter...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)  # Últimos 30 dias
        
        filtered_metrics = glpi_service.get_dashboard_metrics_with_date_filter(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        if not filtered_metrics:
            print("❌ Falha ao obter métricas com filtro de data")
            return False
            
        print("✅ Métricas com filtro de data obtidas com sucesso")
        print(f"Estrutura: {type(filtered_metrics)}")
        
        if isinstance(filtered_metrics, dict) and 'metrics_by_level' in filtered_metrics:
            level_metrics = filtered_metrics['metrics_by_level']
            total_filtered = sum(level.get('total', 0) for level in level_metrics.values() if isinstance(level, dict))
            print(f"Total de tickets com filtro de data: {total_filtered}")
        print()
        
        # 5. Comparação de resultados
        print("5. Resumo dos resultados:")
        print("─" * 50)
        
        if isinstance(metrics_by_level, dict):
            total_direct = sum(sum(status_data.values()) for level_data in metrics_by_level.values() if isinstance(level_data, dict) for status_data in [level_data] if isinstance(status_data, dict))
            print(f"get_metrics_by_level: {total_direct} tickets")
        
        if isinstance(general_metrics, dict) and 'data' in general_metrics and 'metrics_by_level' in general_metrics['data']:
            level_metrics = general_metrics['data']['metrics_by_level']
            total_general = sum(level.get('total', 0) for level in level_metrics.values() if isinstance(level, dict))
            print(f"get_general_metrics: {total_general} tickets")
        
        if isinstance(filtered_metrics, dict) and 'metrics_by_level' in filtered_metrics:
            level_metrics = filtered_metrics['metrics_by_level']
            total_filtered = sum(level.get('total', 0) for level in level_metrics.values() if isinstance(level, dict))
            print(f"get_dashboard_metrics_with_date_filter: {total_filtered} tickets")
        
        print()
        print("✅ Todos os testes passaram com sucesso!")
        print("✅ A integração da nova abordagem baseada em hierarquia está funcionando")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Fechar sessão GLPI
        try:
            glpi_service.close_session()
            print("\n🔒 Sessão GLPI fechada")
        except:
            pass

if __name__ == "__main__":
    success = test_dashboard_integration()
    if success:
        print("\n🎉 TESTE DE INTEGRAÇÃO CONCLUÍDO COM SUCESSO!")
        sys.exit(0)
    else:
        print("\n💥 TESTE DE INTEGRAÇÃO FALHOU!")
        sys.exit(1)