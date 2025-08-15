import sys
import os
import asyncio
from datetime import datetime, timedelta

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.glpi_service import GLPIService
from app.core.config import active_config

async def test_glpi_connection():
    print("=== DIAGNÓSTICO GLPI ===")
    print(f"URL GLPI: {active_config.GLPI_URL}")
    print(f"User Token: {active_config.GLPI_USER_TOKEN[:10]}...")
    print(f"App Token: {active_config.GLPI_APP_TOKEN[:10]}...")
    print()
    
    glpi_service = GLPIService()
    
    try:
        # 1. Teste de autenticaçáo
        print("1. Testando autenticaçáo...")
        auth_result = await glpi_service.authenticate()
        print(f"   Autenticaçáo: {'OK' if auth_result else 'FALHOU'}")
        
        if not auth_result:
            print("   Erro: Náo foi possível autenticar no GLPI")
            return
        
        # 2. Descobrir IDs dos campos
        print("\n2. Descobrindo IDs dos campos...")
        field_ids = await glpi_service.discover_field_ids()
        print(f"   Field IDs: {field_ids}")
        
        # 3. Teste do método get_ticket_count
        print("\n3. Testando get_ticket_count...")
        
        # Testar para N1 (grupo 8) com status Novo (1)
        count_n1_novo = await glpi_service.get_ticket_count(
            group_id=8,
            status_id=1
        )
        print(f"   N1 - Tickets Novos: {count_n1_novo}")
        
        # Testar sem filtro de data
        count_total = await glpi_service.get_ticket_count(
            group_id=8,
            status_id=1,
            start_date=None,
            end_date=None
        )
        print(f"   N1 - Tickets Novos (sem filtro data): {count_total}")
        
        # 4. Teste do método get_general_metrics
        print("\n4. Testando get_general_metrics...")
        
        general_metrics = await glpi_service.get_general_metrics()
        print(f"   Métricas gerais (sem filtro): {general_metrics}")
        
        # 5. Teste com filtro de data dos últimos 30 dias
        print("\n5. Testando com filtro de 30 dias...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        general_metrics_30d = await glpi_service.get_general_metrics(
            start_date=start_date,
            end_date=end_date
        )
        print(f"   Métricas gerais (30 dias): {general_metrics_30d}")
        
    except Exception as e:
        print(f"\nErro durante o diagnóstico: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        try:
            await glpi_service.logout()
            print("\nLogout realizado")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_glpi_connection())

