#!/usr/bin/env python3
"""
Script para debugar o GLPIService e identificar o problema de autenticaçáo
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório do backend ao path
project_root = Path(__file__).parent.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

try:
    from app.services.glpi_service import GLPIService
    from app.core.config import active_config
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    sys.exit(1)

def debug_glpi_service():
    """Debug detalhado do GLPIService"""
    print("🔍 DEBUG GLPIService")
    print("="*50)
    
    # Verificar configurações
    print(f"GLPI_URL: {active_config.GLPI_URL}")
    print(f"GLPI_USER_TOKEN: {'*' * 10 if active_config.GLPI_USER_TOKEN else 'NáO CONFIGURADO'}")
    print(f"GLPI_APP_TOKEN: {'*' * 10 if active_config.GLPI_APP_TOKEN else 'NáO CONFIGURADO'}")
    
    try:
        print("\n🔄 Inicializando GLPIService...")
        glpi_service = GLPIService()
        
        print(f"URL configurada: {glpi_service.glpi_url}")
        print(f"App Token configurado: {'Sim' if glpi_service.app_token else 'Náo'}")
        print(f"User Token configurado: {'Sim' if glpi_service.user_token else 'Náo'}")
        
        print("\n🔐 Testando autenticaçáo...")
        
        # Testar método público
        print("Testando método authenticate()...")
        auth_result = glpi_service.authenticate()
        print(f"Resultado authenticate(): {auth_result}")
        
        if auth_result:
            print(f"Session token: {glpi_service.session_token[:10]}...")
            print(f"Token criado em: {glpi_service.token_created_at}")
            
            # Testar obtençáo de headers
            print("\n📋 Testando obtençáo de headers...")
            headers = glpi_service.get_api_headers()
            if headers:
                print(f"Headers obtidos: {list(headers.keys())}")
            else:
                print("❌ Falha ao obter headers")
                
            # Testar uma requisiçáo simples
            print("\n🌐 Testando requisiçáo autenticada...")
            try:
                response = glpi_service._make_authenticated_request(
                    'GET',
                    f"{glpi_service.glpi_url}/getMyProfiles"
                )
                if response:
                    print(f"Requisiçáo bem-sucedida: {response.status_code}")
                else:
                    print("❌ Falha na requisiçáo autenticada")
            except Exception as e:
                print(f"❌ Erro na requisiçáo: {e}")
        else:
            print("❌ Falha na autenticaçáo")
            
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_glpi_service()
