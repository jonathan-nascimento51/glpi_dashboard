#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService
import logging

# Desabilitar logs para focar no debug
logging.disable(logging.CRITICAL)

def main():
    print("=== Debug User Fields ===")
    
    # Inicializar serviço GLPI
    glpi_service = GLPIService()
    
    print("\n1. Autenticando...")
    if not glpi_service.authenticate():
        print("❌ Falha na autenticação")
        return
    print("✅ Autenticação bem-sucedida")
    
    print("\n2. Buscando um usuário específico para analisar campos...")
    
    # Buscar usuários sem filtro para ver a estrutura
    user_params = {
        "range": "0-5",  # Apenas os primeiros 5
        "criteria[0][field]": "8",  # is_active
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": "1"
    }
    
    response = glpi_service._make_authenticated_request(
        "GET", 
        f"{glpi_service.glpi_url}/search/User", 
        params=user_params
    )
    
    if response.status_code != 200:
        print(f"❌ Erro na busca User: {response.status_code}")
        return
    
    user_data = response.json().get("data", [])
    print(f"✅ Encontrados {len(user_data)} usuários")
    
    print("\n3. Analisando estrutura dos usuários...")
    for i, user in enumerate(user_data[:3]):
        print(f"\nUsuário {i+1}:")
        print(f"  Estrutura completa: {user}")
        if '1' in user:
            print(f"  Campo '1' (Username): {user['1']}")
        if '2' in user:
            print(f"  Campo '2' (ID): {user['2']}")
        if '9' in user:
            print(f"  Campo '9' (Nome real): {user['9']}")
        if '5' in user:
            print(f"  Campo '5' (Email): {user['5']}")
    
    print("\n4. Testando busca por diferentes campos...")
    
    # Testar busca por nome real (campo 9)
    test_name = "anderson"
    print(f"\nTestando busca por nome real contendo '{test_name}'...")
    
    name_params = {
        "range": "0-10",
        "criteria[0][field]": "9",  # Nome real
        "criteria[0][searchtype]": "contains",
        "criteria[0][value]": test_name,
        "forcedisplay[0]": "2",   # ID
        "forcedisplay[1]": "1",   # Username
        "forcedisplay[2]": "9",   # Nome real
    }
    
    name_response = glpi_service._make_authenticated_request(
        "GET", 
        f"{glpi_service.glpi_url}/search/User", 
        params=name_params
    )
    
    if name_response.status_code == 200:
        name_data = name_response.json().get("data", [])
        print(f"✅ Encontrados {len(name_data)} usuários com nome contendo '{test_name}'")
        for user in name_data[:3]:
            print(f"  {user}")
    else:
        print(f"❌ Erro na busca por nome: {name_response.status_code}")
    
    # Testar busca por email (campo 5)
    test_email = "anderson"
    print(f"\nTestando busca por email contendo '{test_email}'...")
    
    email_params = {
        "range": "0-10",
        "criteria[0][field]": "5",  # Email
        "criteria[0][searchtype]": "contains",
        "criteria[0][value]": test_email,
        "forcedisplay[0]": "2",   # ID
        "forcedisplay[1]": "1",   # Username
        "forcedisplay[2]": "9",   # Nome real
        "forcedisplay[3]": "5",   # Email
    }
    
    email_response = glpi_service._make_authenticated_request(
        "GET", 
        f"{glpi_service.glpi_url}/search/User", 
        params=email_params
    )
    
    if email_response.status_code == 200:
        email_data = email_response.json().get("data", [])
        print(f"✅ Encontrados {len(email_data)} usuários com email contendo '{test_email}'")
        for user in email_data[:3]:
            print(f"  {user}")
    else:
        print(f"❌ Erro na busca por email: {email_response.status_code}")
    
    print("\n5. Comparando com dados do Profile_User...")
    print("Valores do campo '5' do Profile_User que encontramos:")
    print("- anderson-oliveira")
    print("- wagner-mengue")
    print("- silvio-valim")
    print("- paulo-nunes")
    print("- pablo-guimaraes")
    
    print("\n=== Fim do Debug ===")

if __name__ == "__main__":
    main()