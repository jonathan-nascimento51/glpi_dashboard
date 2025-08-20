#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import logging
from datetime import datetime

# Desabilitar todos os logs
logging.disable(logging.CRITICAL)
sys.stderr = open(os.devnull, 'w')

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService

def test_entity_filter(glpi_service, description, params):
    print(f"\n=== {description} ===")
    print(f"Parâmetros: {json.dumps(params, indent=2)}")
    
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
    else:
        print(f"❌ Falha na busca: {response.status_code if response else 'None'}")
    
    return []

def main():
    print("=== Debug Filtro de Entidade ===")
    
    # Configurar GLPI service
    glpi_service = GLPIService()
    
    # Autenticar
    print("\n1. Autenticando...")
    if not glpi_service.authenticate():
        print("❌ Falha na autenticação")
        return
    print("✅ Autenticação bem-sucedida")
    
    # Teste 1: Filtrar por campo 80 com ID numérico (como está no código atual)
    params1 = {
        "criteria[0][field]": "4",  # profiles_id
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": "6",
        "criteria[1][field]": "80",  # entities_id (campo atual)
        "criteria[1][searchtype]": "equals", 
        "criteria[1][value]": "2",  # ID da entidade
        "criteria[1][link]": "AND",
        "forcedisplay[0]": "2",   # ID
        "forcedisplay[1]": "3",   # entities_id
        "forcedisplay[2]": "4",   # profiles_id
        "forcedisplay[3]": "5",   # users_id
        "forcedisplay[4]": "80",  # entities_id (campo 80)
        "range": "0-10"
    }
    test_entity_filter(glpi_service, "Filtro atual: campo 80 = ID 2", params1)
    
    # Teste 2: Filtrar por campo 80 com nome da entidade
    params2 = {
        "criteria[0][field]": "4",  # profiles_id
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": "6",
        "criteria[1][field]": "80",  # entities_id
        "criteria[1][searchtype]": "contains", 
        "criteria[1][value]": "CENTRAL DE ATENDIMENTOS",  # Nome da entidade
        "criteria[1][link]": "AND",
        "forcedisplay[0]": "2",   # ID
        "forcedisplay[1]": "3",   # entities_id
        "forcedisplay[2]": "4",   # profiles_id
        "forcedisplay[3]": "5",   # users_id
        "forcedisplay[4]": "80",  # entities_id (campo 80)
        "range": "0-10"
    }
    test_entity_filter(glpi_service, "Filtro por nome: campo 80 contains 'CENTRAL DE ATENDIMENTOS'", params2)
    
    # Teste 3: Tentar outros campos possíveis para entities_id
    for field_num in ["3", "81", "82", "83"]:
        params = {
            "criteria[0][field]": "4",  # profiles_id
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": "6",
            "criteria[1][field]": field_num,  # testar diferentes campos
            "criteria[1][searchtype]": "equals", 
            "criteria[1][value]": "2",
            "criteria[1][link]": "AND",
            "forcedisplay[0]": "2",   # ID
            "forcedisplay[1]": "3",   # entities_id
            "forcedisplay[2]": "4",   # profiles_id
            "forcedisplay[3]": "5",   # users_id
            "forcedisplay[4]": "80",  # entities_id (campo 80)
            "forcedisplay[5]": field_num,  # campo testado
            "range": "0-5"
        }
        test_entity_filter(glpi_service, f"Teste campo {field_num} = 2", params)
    
    # Teste 4: Verificar todos os campos disponíveis em um registro
    print("\n=== Verificando todos os campos disponíveis ===")
    params_all = {
        "criteria[0][field]": "4",  # profiles_id
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": "6",
        "range": "0-1"
    }
    
    response = glpi_service._make_authenticated_request(
        'GET',
        f'{glpi_service.glpi_url}/search/Profile_User',
        params=params_all
    )
    
    if response and response.status_code in [200, 206]:
        try:
            data = response.json()
            if 'data' in data and data['data']:
                print("Todos os campos disponíveis no primeiro registro:")
                first_record = data['data'][0]
                for key, value in sorted(first_record.items()):
                    print(f"  Campo '{key}': {value}")
        except Exception as e:
            print(f"Erro: {e}")
    
    print("\n=== Fim do Debug ===")

if __name__ == "__main__":
    main()