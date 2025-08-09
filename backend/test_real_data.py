#!/usr/bin/env python3
"""
Script para testar se o backend está retornando dados reais
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService
from services.api_service import APIService
import json

def test_glpi_service():
    """Testa o GLPIService diretamente"""
    print("=== Testando GLPIService ===")
    try:
        glpi_service = GLPIService()
        print(f"GLPIService criado: {glpi_service}")
        
        # Testa get_dashboard_metrics
        print("\n--- Testando get_dashboard_metrics ---")
        metrics = glpi_service.get_dashboard_metrics()
        print(f"Tipo do retorno: {type(metrics)}")
        print(f"Dados retornados: {json.dumps(metrics, indent=2, ensure_ascii=False)}")
        
        return metrics
    except Exception as e:
        print(f"Erro no GLPIService: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_api_service():
    """Testa o APIService diretamente"""
    print("\n=== Testando APIService ===")
    try:
        api_service = APIService()
        print(f"APIService criado: {api_service}")
        
        # Testa get_dashboard_metrics
        print("\n--- Testando APIService.get_dashboard_metrics ---")
        metrics = api_service.get_dashboard_metrics()
        print(f"Tipo do retorno: {type(metrics)}")
        print(f"Dados retornados: {json.dumps(metrics, indent=2, ensure_ascii=False)}")
        
        return metrics
    except Exception as e:
        print(f"Erro no APIService: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_flask_app():
    """Testa a aplicação Flask diretamente"""
    print("\n=== Testando Flask App ===")
    try:
        from api.routes import app
        
        with app.test_client() as client:
            print("\n--- Testando /api/dashboard/metrics ---")
            response = client.get('/api/dashboard/metrics')
            print(f"Status Code: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"Dados JSON: {json.dumps(data, indent=2, ensure_ascii=False)}")
            else:
                print(f"Erro na resposta: {response.get_data(as_text=True)}")
                
            return response
    except Exception as e:
        print(f"Erro na Flask App: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🔍 Iniciando análise completa do backend...\n")
    
    # Teste 1: GLPIService
    glpi_result = test_glpi_service()
    
    # Teste 2: APIService
    api_result = test_api_service()
    
    # Teste 3: Flask App
    flask_result = test_flask_app()
    
    print("\n" + "="*50)
    print("📊 RESUMO DOS TESTES")
    print("="*50)
    print(f"GLPIService: {'✅ OK' if glpi_result else '❌ FALHOU'}")
    print(f"APIService: {'✅ OK' if api_result else '❌ FALHOU'}")
    print(f"Flask App: {'✅ OK' if flask_result and flask_result.status_code == 200 else '❌ FALHOU'}")
    
    if glpi_result and api_result and flask_result and flask_result.status_code == 200:
        print("\n🎉 Todos os testes passaram! O backend está funcionando.")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique os logs acima.")