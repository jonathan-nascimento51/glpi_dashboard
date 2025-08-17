#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug específico para entender por que o dashboard não está retornando tickets
com a nova abordagem baseada em hierarquia.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService
import json
from datetime import datetime

def debug_dashboard_hierarchy():
    """Debug específico do dashboard com hierarquia."""
    
    print("=== DEBUG DASHBOARD HIERARQUIA ===")
    print(f"Iniciado em: {datetime.now()}")
    print()
    
    # Inicializar serviço GLPI
    glpi_service = GLPIService()
    
    try:
        # 1. Autenticação
        print("1. Autenticando...")
        if not glpi_service.authenticate():
            print("❌ Falha na autenticação")
            return False
        print("✅ Autenticação bem-sucedida")
        print()
        
        # 2. Verificar field_ids
        print("2. Verificando field_ids...")
        if not glpi_service.discover_field_ids():
            print("❌ Falha ao descobrir field_ids")
            return False
        print(f"✅ Field IDs: {glpi_service.field_ids}")
        print()
        
        # 3. Verificar status_map
        print("3. Verificando status_map...")
        print(f"Status map: {glpi_service.status_map}")
        print()
        
        # 4. Testar get_ticket_count_by_hierarchy diretamente
        print("4. Testando get_ticket_count_by_hierarchy diretamente...")
        test_cases = [
            ("N1", 1),  # Novo
            ("N1", 2),  # Atribuído
            ("N2", 1),  # Novo
        ]
        
        for level, status_id in test_cases:
            count = glpi_service.get_ticket_count_by_hierarchy(level, status_id)
            print(f"  {level} - Status {status_id}: {count} tickets")
        print()
        
        # 5. Testar _get_metrics_by_level_internal_hierarchy diretamente
        print("5. Testando _get_metrics_by_level_internal_hierarchy diretamente...")
        hierarchy_metrics = glpi_service._get_metrics_by_level_internal_hierarchy()
        
        print(f"Tipo retornado: {type(hierarchy_metrics)}")
        print(f"Conteúdo: {hierarchy_metrics}")
        
        if isinstance(hierarchy_metrics, dict):
            total_hierarchy = 0
            for level, status_counts in hierarchy_metrics.items():
                if isinstance(status_counts, dict):
                    level_total = sum(status_counts.values())
                    total_hierarchy += level_total
                    print(f"  {level}: {level_total} tickets")
            print(f"  TOTAL: {total_hierarchy} tickets")
        print()
        
        # 6. Testar get_metrics_by_level (método usado no dashboard)
        print("6. Testando get_metrics_by_level (método do dashboard)...")
        dashboard_metrics = glpi_service.get_metrics_by_level()
        
        print(f"Tipo retornado: {type(dashboard_metrics)}")
        print(f"Conteúdo: {dashboard_metrics}")
        
        if isinstance(dashboard_metrics, dict):
            total_dashboard = 0
            for level, status_counts in dashboard_metrics.items():
                if isinstance(status_counts, dict):
                    level_total = sum(status_counts.values())
                    total_dashboard += level_total
                    print(f"  {level}: {level_total} tickets")
            print(f"  TOTAL: {total_dashboard} tickets")
        print()
        
        # 7. Comparação
        print("7. COMPARAÇÃO:")
        print("─" * 50)
        
        if 'total_hierarchy' in locals():
            print(f"_get_metrics_by_level_internal_hierarchy: {total_hierarchy} tickets")
        
        if 'total_dashboard' in locals():
            print(f"get_metrics_by_level (dashboard): {total_dashboard} tickets")
        
        if 'total_hierarchy' in locals() and 'total_dashboard' in locals():
            if total_hierarchy != total_dashboard:
                print(f"⚠️  DIFERENÇA DETECTADA: {total_hierarchy} vs {total_dashboard}")
            else:
                print("✅ Ambos os métodos retornam o mesmo resultado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o debug: {e}")
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
    success = debug_dashboard_hierarchy()
    if success:
        print("\n🎉 DEBUG CONCLUÍDO COM SUCESSO!")
        sys.exit(0)
    else:
        print("\n💥 DEBUG FALHOU!")
        sys.exit(1)