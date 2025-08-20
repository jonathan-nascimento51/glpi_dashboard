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
    print("=== Debug Username Search ===")
    
    # Inicializar serviço GLPI
    glpi_service = GLPIService()
    
    print("\n1. Autenticando...")
    if not glpi_service.authenticate():
        print("❌ Falha na autenticação")
        return
    print("✅ Autenticação bem-sucedida")
    
    print("\n2. Buscando Profile_User com filtro de entidade...")
    
    # Buscar Profile_User com filtro de entidade
    params = {
        "range": "0-999",
        "criteria[0][field]": "4",  # profiles_id
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": "6",  # Técnico
        "criteria[1][field]": "80",  # entities_id
        "criteria[1][searchtype]": "equals",
        "criteria[1][value]": "2",  # ID da entidade
        "criteria[1][link]": "AND",
        "forcedisplay[0]": "2",
        "forcedisplay[1]": "5",
        "forcedisplay[2]": "4",
        "forcedisplay[3]": "80"
    }
    
    response = glpi_service._make_authenticated_request("GET", f"{glpi_service.glpi_url}/search/Profile_User", params=params)
    
    if response.status_code != 200:
        print(f"❌ Erro na busca Profile_User: {response.status_code}")
        return
    
    profile_data = response.json().get("data", [])
    print(f"✅ Encontrados {len(profile_data)} registros Profile_User")
    
    print("\n3. Extraindo usernames...")
    usernames = set()
    for i, profile_user in enumerate(profile_data[:5]):  # Mostrar apenas os primeiros 5
        if isinstance(profile_user, dict) and "5" in profile_user:
            username = str(profile_user["5"]).strip()
            if username:
                usernames.add(username)
                print(f"  Registro {i+1}: username = '{username}'")
    
    print(f"\n✅ Total de usernames únicos extraídos: {len(usernames)}")
    print(f"Usernames: {list(usernames)[:10]}")
    
    if not usernames:
        print("❌ Nenhum username encontrado")
        return
    
    print("\n4. Testando busca de usuários por username...")
    
    # Testar com apenas os primeiros 3 usernames
    test_usernames = list(usernames)[:3]
    print(f"Testando com: {test_usernames}")
    
    # Construir parâmetros de busca por username
    user_params = {
        "range": "0-999",
        "forcedisplay[0]": "2",  # ID
        "forcedisplay[1]": "1",  # Username
        "forcedisplay[2]": "9",  # Nome real
        "forcedisplay[3]": "5",  # Email
    }
    
    # Adicionar critérios OR para cada username
    for idx, username in enumerate(test_usernames):
        user_params[f"criteria[{idx}][field]"] = "1"  # Username
        user_params[f"criteria[{idx}][searchtype]"] = "equals"
        user_params[f"criteria[{idx}][value]"] = username
        if idx > 0:
            user_params[f"criteria[{idx}][link]"] = "OR"
    
    print(f"\nParâmetros de busca User:")
    for key, value in user_params.items():
        print(f"  {key}: {value}")
    
    # Fazer busca de usuários
    user_response = glpi_service._make_authenticated_request("GET", f"{glpi_service.glpi_url}/search/User", params=user_params)
    
    print(f"\nStatus da resposta User: {user_response.status_code}")
    
    if user_response.status_code != 200:
        print(f"❌ Erro na busca User: {user_response.text}")
        return
    
    user_data = user_response.json().get("data", [])
    print(f"✅ Encontrados {len(user_data)} usuários")
    
    if user_data:
        print("\nPrimeiros usuários encontrados:")
        for i, user in enumerate(user_data[:3]):
            print(f"  Usuário {i+1}: {user}")
    else:
        print("❌ Nenhum usuário encontrado")
        
        # Testar busca individual
        print("\n5. Testando busca individual...")
        for username in test_usernames[:2]:
            individual_params = {
                "range": "0-999",
                "criteria[0][field]": "1",  # Username
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": username,
                "forcedisplay[0]": "2",  # ID
                "forcedisplay[1]": "1",  # Username
                "forcedisplay[2]": "9",  # Nome real
            }
            
            individual_response = glpi_service._make_authenticated_request("GET", f"{glpi_service.glpi_url}/search/User", params=individual_params)
            individual_data = individual_response.json().get("data", [])
            print(f"  Username '{username}': {len(individual_data)} resultados")
            if individual_data:
                print(f"    Primeiro resultado: {individual_data[0]}")
    
    print("\n=== Fim do Debug ===")

if __name__ == "__main__":
    main()