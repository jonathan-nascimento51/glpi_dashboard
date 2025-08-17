#!/usr/bin/env python3
"""
Teste específico para verificar o comportamento dos métodos com e sem parâmetros de data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService
from datetime import datetime, timedelta

def test_date_parameters():
    """Testa o comportamento dos métodos com diferentes parâmetros de data"""
    print("=== TESTE DE PARÂMETROS DE DATA ===")
    print(f"Iniciado em: {datetime.now()}")
    
    # Inicializar serviço
    glpi_service = GLPIService()
    
    try:
        # 1. Testar sem parâmetros de data
        print("\n1. Testando get_metrics_by_level SEM parâmetros de data...")
        metrics_no_date = glpi_service.get_metrics_by_level()
        total_no_date = sum(sum(status.values()) for status in metrics_no_date.values())
        print(f"✅ Resultado sem data: {total_no_date} tickets")
        print(f"Níveis: {list(metrics_no_date.keys())}")
        
        # 2. Testar com parâmetros None
        print("\n2. Testando get_metrics_by_level com parâmetros None...")
        metrics_none_date = glpi_service.get_metrics_by_level(None, None)
        total_none_date = sum(sum(status.values()) for status in metrics_none_date.values())
        print(f"✅ Resultado com None: {total_none_date} tickets")
        
        # 3. Testar com datas específicas (últimos 30 dias)
        print("\n3. Testando get_metrics_by_level com filtro de data (últimos 30 dias)...")
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        print(f"Período: {start_date} até {end_date}")
        
        metrics_with_date = glpi_service.get_metrics_by_level(start_date, end_date)
        total_with_date = sum(sum(status.values()) for status in metrics_with_date.values())
        print(f"✅ Resultado com filtro de data: {total_with_date} tickets")
        
        # 4. Testar com período mais amplo (últimos 365 dias)
        print("\n4. Testando get_metrics_by_level com período amplo (últimos 365 dias)...")
        start_date_wide = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        metrics_wide_date = glpi_service.get_metrics_by_level(start_date_wide, end_date)
        total_wide_date = sum(sum(status.values()) for status in metrics_wide_date.values())
        print(f"✅ Resultado com período amplo: {total_wide_date} tickets")
        
        # 5. Comparação dos resultados
        print("\n5. COMPARAÇÃO DOS RESULTADOS:")
        print("──────────────────────────────────────────────────")
        print(f"Sem data: {total_no_date} tickets")
        print(f"Com None: {total_none_date} tickets")
        print(f"Últimos 30 dias: {total_with_date} tickets")
        print(f"Últimos 365 dias: {total_wide_date} tickets")
        
        # Verificar se há diferenças significativas
        if total_no_date == total_none_date:
            print("✅ Sem data e None retornam o mesmo resultado")
        else:
            print("⚠️ Diferença entre sem data e None")
            
        if total_with_date == 0:
            print("⚠️ Filtro de data está retornando 0 tickets")
        else:
            print(f"✅ Filtro de data funcionando: {total_with_date} tickets")
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Fechar sessão
        try:
            glpi_service.close_session()
            print("\n🔒 Sessão GLPI fechada")
        except:
            pass
    
    print("\n🎉 TESTE DE PARÂMETROS DE DATA CONCLUÍDO!")

if __name__ == "__main__":
    test_date_parameters()