#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar a conexão e autenticação com o GLPI
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.glpi_service import GLPIService
from backend.config.settings import active_config
import logging
import json
import requests

# Configurar logging para info apenas
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_glpi')

def test_glpi_direct():
    """Testa a conexão direta com o GLPI"""
    print("=== TESTE DIRETO DE CONEXÃO COM GLPI ===")
    print(f"URL do GLPI: {active_config.GLPI_URL}")
    print(f"App Token: {active_config.GLPI_APP_TOKEN[:10]}...")
    print(f"User Token: {active_config.GLPI_USER_TOKEN[:10]}...")
    print()
    
    # Teste direto de autenticação
    session_headers = {
        "Content-Type": "application/json",
        "App-Token": active_config.GLPI_APP_TOKEN,
        "Authorization": f"user_token {active_config.GLPI_USER_TOKEN}",
    }
    
    try:
        print("1. Testando autenticação direta...")
        response = requests.get(
            f"{active_config.GLPI_URL}/initSession", 
            headers=session_headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Autenticação bem-sucedida!")
            print(f"Session Token: {data.get('session_token', 'N/A')[:20]}...")
            
            # Teste de busca simples
            session_token = data.get('session_token')
            if session_token:
                print("\n2. Testando busca de tickets...")
                search_headers = {
                    "Session-Token": session_token,
                    "App-Token": active_config.GLPI_APP_TOKEN
                }
                
                search_url = f"{active_config.GLPI_URL}/search/Ticket"
                search_params = {
                    "criteria[0][field]": "12",  # Status
                    "criteria[0][searchtype]": "equals",
                    "criteria[0][value]": "1",  # Novo
                    "range": "0-0"  # Só queremos o count
                }
                
                search_response = requests.get(
                    search_url,
                    headers=search_headers,
                    params=search_params,
                    timeout=10
                )
                
                print(f"Search Status Code: {search_response.status_code}")
                if search_response.status_code == 200:
                    content_range = search_response.headers.get('Content-Range', '')
                    print(f"Content-Range: {content_range}")
                    if content_range:
                        total = content_range.split('/')[-1]
                        print(f"✅ Total de tickets novos: {total}")
                    else:
                        print("❌ Não foi possível obter o total")
                else:
                    print(f"❌ Erro na busca: {search_response.text}")
                    
        else:
            print(f"❌ Falha na autenticação: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False
    
    return True

def test_glpi_service():
    """Testa usando o GLPIService"""
    print("\n=== TESTE USANDO GLPI SERVICE ===")
    
    try:
        glpi_service = GLPIService()
        
        # Teste de autenticação
        print("1. Testando autenticação via service...")
        auth_result = glpi_service._perform_authentication()
        if auth_result:
            print("✅ Autenticação bem-sucedida!")
            print(f"Session Token: {glpi_service.session_token[:20]}...")
            
            # Teste de métricas gerais simples
            print("\n2. Testando métricas gerais...")
            general_metrics = glpi_service._get_general_metrics_internal()
            print(f"Métricas gerais: {general_metrics}")
            
        else:
            print("❌ Falha na autenticação via service!")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste do service: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    try:
        success1 = test_glpi_direct()
        success2 = test_glpi_service()
        
        if success1 and success2:
            print("\n🎉 Todos os testes passaram!")
        else:
            print("\n💥 Alguns testes falharam!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)