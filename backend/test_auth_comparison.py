#!/usr/bin/env python3
"""
Script para comparar a autenticaçáo GLPI atual vs teste manual
"""

import requests
import os
from dotenv import load_dotenv
import json

def test_manual_auth():
    """Teste manual que funcionou anteriormente"""
    load_dotenv()
    
    url = os.getenv('GLPI_URL')
    app_token = os.getenv('GLPI_APP_TOKEN')
    user_token = os.getenv('GLPI_USER_TOKEN')
    
    print("=== TESTE MANUAL (que funcionou) ===")
    print(f"URL: {url}")
    print(f"App Token: {app_token[:10]}...")
    print(f"User Token: {user_token[:10]}...")
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'user_token {user_token}',
        'App-Token': app_token
    }
    
    print("\nHeaders do teste manual:")
    for key, value in headers.items():
        if 'token' in key.lower() or 'authorization' in key.lower():
            print(f"  {key}: {value[:20]}...")
        else:
            print(f"  {key}: {value}")
    
    try:
        response = requests.get(f'{url}/initSession', headers=headers, timeout=10)
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erro: {e}")
        return False

def test_glpi_service_auth():
    """Teste usando a implementaçáo atual do GLPIService"""
    print("\n=== TESTE GLPI SERVICE (implementaçáo atual) ===")
    
    # Simular a implementaçáo atual
    load_dotenv()
    
    url = os.getenv('GLPI_URL')
    app_token = os.getenv('GLPI_APP_TOKEN')
    user_token = os.getenv('GLPI_USER_TOKEN')
    
    # Headers como implementado no GLPIService
    session_headers = {
        "Content-Type": "application/json",
        "App-Token": app_token,
        "Authorization": f"user_token {user_token}",
    }
    
    print("\nHeaders do GLPIService:")
    for key, value in session_headers.items():
        if 'token' in key.lower() or 'authorization' in key.lower():
            print(f"  {key}: {value[:20]}...")
        else:
            print(f"  {key}: {value}")
    
    try:
        response = requests.get(
            f"{url}/initSession",
            headers=session_headers,
            timeout=10
        )
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erro: {e}")
        return False

def compare_implementations():
    """Compara as duas implementações"""
    print("\n=== COMPARAÇáO ===")
    
    manual_success = test_manual_auth()
    service_success = test_glpi_service_auth()
    
    print(f"\nResultados:")
    print(f"  Teste Manual: {' SUCESSO' if manual_success else ' FALHA'}")
    print(f"  GLPIService:  {' SUCESSO' if service_success else ' FALHA'}")
    
    if manual_success and not service_success:
        print("\n DIAGNÓSTICO: Implementaçáo do GLPIService tem problema")
    elif not manual_success and not service_success:
        print("\n DIAGNÓSTICO: Problema nas credenciais ou conectividade")
    elif manual_success and service_success:
        print("\n DIAGNÓSTICO: Ambas implementações funcionam")
    else:
        print("\n DIAGNÓSTICO: Situaçáo inesperada")

if __name__ == "__main__":
    compare_implementations()

