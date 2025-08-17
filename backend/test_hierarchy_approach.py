#!/usr/bin/env python3
"""
Script para testar a nova abordagem baseada em hierarquia (campo 8)
que deve resolver o problema de distribuição de tickets por nível.
"""

import os
import sys
from dotenv import load_dotenv

# Adicionar o diretório backend ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService

def main():
    print("=" * 80)
    print("TESTE DA NOVA ABORDAGEM BASEADA EM HIERARQUIA (CAMPO 8)")
    print("=" * 80)
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Inicializar GLPIService
    try:
        glpi = GLPIService()
        print("✅ GLPIService inicializado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao inicializar GLPIService: {e}")
        return
    
    try:
        # Testar autenticação
        print("\n1. TESTANDO AUTENTICAÇÃO...")
        if not glpi._ensure_authenticated():
            print("❌ Falha na autenticação")
            return
        print("✅ Autenticação bem-sucedida")
        
        # Descobrir field_ids
        print("\n2. DESCOBRINDO FIELD_IDS...")
        if not glpi.discover_field_ids():
            print("❌ Falha ao descobrir field_ids")
            return
        print(f"✅ Field IDs descobertos: {glpi.field_ids}")
        
        # Testar método individual get_ticket_count_by_hierarchy
        print("\n3. TESTANDO get_ticket_count_by_hierarchy...")
        test_cases = [
            ("N1", 1),  # Novo
            ("N1", 2),  # Atribuído
            ("N2", 1),  # Novo
            ("N3", 1),  # Novo
            ("N4", 1),  # Novo
        ]
        
        for level, status_id in test_cases:
            try:
                count = glpi.get_ticket_count_by_hierarchy(level, status_id)
                print(f"  {level} - Status {status_id}: {count} tickets")
            except Exception as e:
                print(f"  ❌ Erro ao buscar {level} - Status {status_id}: {e}")
        
        # Testar método completo _get_metrics_by_level_internal_hierarchy
        print("\n4. TESTANDO _get_metrics_by_level_internal_hierarchy...")
        try:
            hierarchy_metrics = glpi._get_metrics_by_level_internal_hierarchy()
            print("\n📊 MÉTRICAS POR HIERARQUIA:")
            
            total_hierarchy = 0
            for level, status_counts in hierarchy_metrics.items():
                level_total = sum(status_counts.values())
                total_hierarchy += level_total
                print(f"\n{level}:")
                for status, count in status_counts.items():
                    print(f"  {status}: {count}")
                print(f"  Total {level}: {level_total}")
            
            print(f"\n🎯 TOTAL GERAL (HIERARQUIA): {total_hierarchy}")
            
        except Exception as e:
            print(f"❌ Erro no método hierarchy: {e}")
        
        # Comparar com método antigo
        print("\n5. COMPARANDO COM MÉTODO ANTIGO...")
        try:
            old_metrics = glpi._get_metrics_by_level_internal()
            print("\n📊 MÉTRICAS ANTIGAS (GRUPOS):")
            
            total_old = 0
            for level, status_counts in old_metrics.items():
                level_total = sum(status_counts.values())
                total_old += level_total
                print(f"\n{level}:")
                for status, count in status_counts.items():
                    print(f"  {status}: {count}")
                print(f"  Total {level}: {level_total}")
            
            print(f"\n🎯 TOTAL GERAL (GRUPOS): {total_old}")
            
        except Exception as e:
            print(f"❌ Erro no método antigo: {e}")
        
        # Resumo da comparação
        print("\n" + "=" * 80)
        print("RESUMO DA COMPARAÇÃO")
        print("=" * 80)
        
        if 'total_hierarchy' in locals() and 'total_old' in locals():
            print(f"📈 Método Hierarquia (Campo 8): {total_hierarchy} tickets")
            print(f"📉 Método Antigo (Grupos): {total_old} tickets")
            
            if total_hierarchy > total_old:
                improvement = total_hierarchy - total_old
                percentage = (improvement / max(total_old, 1)) * 100
                print(f"🚀 MELHORIA: +{improvement} tickets (+{percentage:.1f}%)")
                print("✅ A nova abordagem encontra significativamente mais tickets!")
            else:
                print("⚠️  A nova abordagem não mostrou melhoria significativa")
        
        print("\n✅ Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Fechar sessão
        try:
            glpi.close_session()
            print("\n🔒 Sessão GLPI fechada")
        except Exception as e:
            print(f"⚠️  Erro ao fechar sessão: {e}")

if __name__ == "__main__":
    main()