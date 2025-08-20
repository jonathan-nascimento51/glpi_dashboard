#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
from datetime import datetime

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService

def test_profile_user_search(glpi_service, description, params):
    print(f"\n=== {description} ===")
    print(f"Parâmetros: {params}")
    
    response = glpi_service._make_authenticated_request(
        'GET',
        f'{glpi_service.glpi_url}/search/Profile_User',
        params=params
    )
    
    if response and response.status_code in [200, 206]:
        try:
            data = response.json()
            profile_users = data.get('data', [])
            print(f"✅ Encontrados {len(profile_users)} registros")
            
            if profile_users:
                print("\nPrimeiros 3 registros:")
                for i, record in enumerate(profile_users[:3]):
                    print(f"  Registro {i+1}: {record}")
            
            return profile_users
        except Exception as e:
            print(f"❌ Erro ao processar resposta: {e}")
            print(f"Resposta bruta: {response.text[:200]}")
    else:
        print(f"❌ Falha na busca: {response.status_code if response else 'None'}")
        if response:
            print(f"Resposta: {response.text[:200]}")
    
    return []

def main():
    print("=== Debug Simples Profile_User ===")
    
    # Configurar GLPI service
    glpi_service = GLPIService()
    
    # Autenticar
    print("\n1. Autenticando...")
    if not glpi_service.authenticate():
        print("❌ Falha na autenticação")
        return
    print("✅ Autenticação bem-sucedida")
    
    # Teste 1: Buscar todos os Profile_User (sem filtro)
    params1 = {
        "forcedisplay[0]": "2",   # ID
        "forcedisplay[1]": "3",   # entities_id
        "forcedisplay[2]": "4",   # profiles_id
        "forcedisplay[3]": "5",   # users_id
        "range": "0-10"
    }
    test_profile_user_search(glpi_service, "Todos os Profile_User (primeiros 10)", params1)
    
    # Teste 2: Buscar apenas por perfil 6 (Tecnico)
    params2 = {
        "criteria[0][field]": "4",  # profiles_id
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": "6",
        "forcedisplay[0]": "2",   # ID
        "forcedisplay[1]": "3",   # entities_id
        "forcedisplay[2]": "4",   # profiles_id
        "forcedisplay[3]": "5",   # users_id
        "range": "0-10"
    }
    test_profile_user_search(glpi_service, "Profile_User apenas com perfil 6", params2)
    
    # Teste 3: Buscar apenas por entidade 2
    params3 = {
        "criteria[0][field]": "3",  # entities_id
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": "2",
        "forcedisplay[0]": "2",   # ID
        "forcedisplay[1]": "3",   # entities_id
        "forcedisplay[2]": "4",   # profiles_id
        "forcedisplay[3]": "5",   # users_id
        "range": "0-10"
    }
    test_profile_user_search(glpi_service, "Profile_User apenas com entidade 2", params3)
    
    # Teste 4: Buscar com perfil 6 E entidade 2 (usando campo correto)
    params4 = {
        "criteria[0][field]": "4",  # profiles_id
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": "6",
        "criteria[1][field]": "3",  # entities_id
        "criteria[1][searchtype]": "equals", 
        "criteria[1][value]": "2",
        "criteria[1][link]": "AND",
        "forcedisplay[0]": "2",   # ID
        "forcedisplay[1]": "3",   # entities_id
        "forcedisplay[2]": "4",   # profiles_id
        "forcedisplay[3]": "5",   # users_id
        "range": "0-10"
    }
    test_profile_user_search(glpi_service, "Profile_User com perfil 6 E entidade 2 (campo correto)", params4)
    
    # Teste 5: Verificar quais campos estão disponíveis
    print("\n=== Verificando campos disponíveis ===")
    params5 = {
        "range": "0-1"
    }
    response = glpi_service._make_authenticated_request(
        'GET',
        f'{glpi_service.glpi_url}/search/Profile_User',
        params=params5
    )
    
    if response and response.status_code in [200, 206]:
        try:
            data = response.json()
            if 'data' in data and data['data']:
                print("Campos disponíveis no primeiro registro:")
                first_record = data['data'][0]
                for key, value in first_record.items():
                    print(f"  Campo '{key}': {value} (tipo: {type(value)})")
        except Exception as e:
            print(f"Erro: {e}")
    
    print("\n=== Fim do Debug ===")

if __name__ == "__main__":
    main()