#!/usr/bin/env python3
"""
Script para testar a autenticaçáo GLPI e diagnosticar o problema
"""

import os
import requests
import json
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def test_glpi_authentication():
    """Testa a autenticaçáo GLPI e mostra a resposta detalhada"""
    
    # Obter configurações
    glpi_url = os.getenv('GLPI_URL')
    app_token = os.getenv('GLPI_APP_TOKEN')
    user_token = os.getenv('GLPI_USER_TOKEN')
    
    print(f"GLPI URL: {glpi_url}")
    print(f"App Token: {'*' * 10 if app_token else 'NáO CONFIGURADO'}")
    print(f"User Token: {'*' * 10 if user_token else 'NáO CONFIGURADO'}")
    print("\n" + "="*50)
    
    if not all([glpi_url, app_token, user_token]):
        print("❌ Configurações GLPI incompletas!")
        return False
    
    # Headers para autenticaçáo
    session_headers = {
        "Content-Type": "application/json",
        "App-Token": app_token,
        "Authorization": f"user_token {user_token}",
    }
    
    try:
        print("🔄 Testando conectividade com GLPI...")
        
        # Testar conectividade básica
        response = requests.get(f"{glpi_url}/status", timeout=10)
        print(f"Status endpoint: {response.status_code}")
        
        # Testar autenticaçáo
        print("\n🔐 Testando autenticaçáo...")
        auth_url = f"{glpi_url}/initSession"
        print(f"URL de autenticaçáo: {auth_url}")
        
        response = requests.get(auth_url, headers=session_headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers de resposta: {dict(response.headers)}")
        
        # Verificar se a resposta tem conteúdo
        if response.content:
            print(f"Conteúdo da resposta (raw): {response.content}")
            
            try:
                response_data = response.json()
                print(f"Resposta JSON: {json.dumps(response_data, indent=2)}")
                
                # Verificar se tem session_token
                if isinstance(response_data, dict) and "session_token" in response_data:
                    print(f"✅ Session token encontrado: {response_data['session_token'][:10]}...")
                    return True
                else:
                    print(f"❌ Session token náo encontrado na resposta")
                    print(f"Chaves disponíveis: {list(response_data.keys()) if isinstance(response_data, dict) else 'Resposta náo é um dict'}")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao decodificar JSON: {e}")
                print(f"Conteúdo náo é JSON válido: {response.text}")
                return False
        else:
            print("❌ Resposta vazia")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Erro de conexáo: {e}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"❌ Timeout: {e}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisiçáo: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Teste de Autenticaçáo GLPI")
    print("="*50)
    
    success = test_glpi_authentication()
    
    print("\n" + "="*50)
    if success:
        print("✅ Autenticaçáo GLPI funcionando corretamente!")
    else:
        print("❌ Problemas na autenticaçáo GLPI detectados.")
        print("\nVerifique:")
        print("1. Se o GLPI está rodando e acessível")
        print("2. Se os tokens estáo corretos")
        print("3. Se a URL está correta")
        print("4. Se a API do GLPI está habilitada")
