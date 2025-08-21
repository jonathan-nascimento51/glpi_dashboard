#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Desabilitar todos os logs antes de importar
import logging

logging.disable(logging.CRITICAL)

import json

from services.glpi_service import GLPIService


def test_glpi_connection():
    """Testar conectividade básica com GLPI"""

    # Inicializar serviço GLPI
    glpi_service = GLPIService()

    print(f"URL do GLPI: {glpi_service.glpi_url}")
    print(f"App Token configurado: {'Sim' if glpi_service.app_token else 'Não'}")
    print(f"User Token configurado: {'Sim' if glpi_service.user_token else 'Não'}")

    # Teste 1: Verificar se consegue fazer uma busca básica de usuários
    print("\n=== Teste 1: Busca básica de usuários (primeiros 5) ===")
    try:
        search_params = {
            "range": "0-4",
            "forcedisplay[0]": "2",  # ID
            "forcedisplay[1]": "1",  # Username
            "forcedisplay[2]": "9",  # Firstname
            "forcedisplay[3]": "34",  # Realname
        }

        response = glpi_service._make_authenticated_request(
            "GET", f"{glpi_service.glpi_url}/search/User", params=search_params
        )

        if response:
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                search_data = response.json()
                print(f"Total count: {search_data.get('totalcount')}")
                print(f"Count: {search_data.get('count')}")
                if search_data.get("data"):
                    print(f"✓ Primeiros usuários encontrados:")
                    for i, user in enumerate(search_data.get("data", [])[:3]):
                        print(
                            f"  {i+1}. ID: {user.get('2')}, Username: {user.get('1')}, Nome: {user.get('9')} {user.get('34')}"
                        )
                else:
                    print(f"✗ Nenhum usuário encontrado")
            else:
                print(f"✗ Erro HTTP: {response.status_code}")
                print(f"Resposta: {response.text[:500]}")
        else:
            print(f"✗ Falha na requisição - resposta None")
    except Exception as e:
        print(f"✗ Erro na busca básica: {e}")

    # Teste 2: Verificar se consegue buscar Profile_User
    print("\n=== Teste 2: Busca de Profile_User (técnicos) ===")
    try:
        search_params = {
            "range": "0-9",
            "forcedisplay[0]": "2",  # ID
            "forcedisplay[1]": "3",  # users_id
            "forcedisplay[2]": "4",  # profiles_id
            "forcedisplay[3]": "5",  # entities_id
            "criteria[0][field]": "4",  # profiles_id
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": "6",  # Técnico
        }

        response = glpi_service._make_authenticated_request(
            "GET", f"{glpi_service.glpi_url}/search/Profile_User", params=search_params
        )

        if response:
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                search_data = response.json()
                print(f"Total count: {search_data.get('totalcount')}")
                print(f"Count: {search_data.get('count')}")
                if search_data.get("data"):
                    print(f"✓ Primeiros Profile_User encontrados:")
                    for i, profile in enumerate(search_data.get("data", [])[:3]):
                        print(
                            f"  {i+1}. ID: {profile.get('2')}, User ID: {profile.get('3')}, Profile ID: {profile.get('4')}, Entity ID: {profile.get('5')}"
                        )
                else:
                    print(f"✗ Nenhum Profile_User encontrado")
            else:
                print(f"✗ Erro HTTP: {response.status_code}")
                print(f"Resposta: {response.text[:500]}")
        else:
            print(f"✗ Falha na requisição - resposta None")
    except Exception as e:
        print(f"✗ Erro na busca de Profile_User: {e}")

    # Teste 3: Tentar buscar um usuário específico que sabemos que existe
    print("\n=== Teste 3: Busca de usuário específico por username ===")
    try:
        # Primeiro vamos pegar um username real dos resultados anteriores
        search_params = {
            "range": "0-0",  # Apenas 1 resultado
            "forcedisplay[0]": "2",  # ID
            "forcedisplay[1]": "1",  # Username
            "forcedisplay[2]": "8",  # is_active
            "criteria[0][field]": "8",  # is_active
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": "1",  # Ativo
        }

        response = glpi_service._make_authenticated_request(
            "GET", f"{glpi_service.glpi_url}/search/User", params=search_params
        )

        if response and response.status_code == 200:
            search_data = response.json()
            if search_data.get("data"):
                first_user = search_data.get("data")[0]
                user_id = first_user.get("2")
                username = first_user.get("1")
                print(f"✓ Primeiro usuário ativo encontrado: ID {user_id}, Username: {username}")

                # Agora tentar buscar este usuário específico por ID
                print(f"\n--- Testando busca por ID {user_id} ---")
                search_params_by_id = {
                    "range": "0-0",
                    "forcedisplay[0]": "2",  # ID
                    "forcedisplay[1]": "1",  # Username
                    "criteria[0][field]": "2",  # ID
                    "criteria[0][searchtype]": "equals",
                    "criteria[0][value]": str(user_id),
                }

                response_by_id = glpi_service._make_authenticated_request(
                    "GET", f"{glpi_service.glpi_url}/search/User", params=search_params_by_id
                )

                if response_by_id and response_by_id.status_code == 200:
                    search_data_by_id = response_by_id.json()
                    print(f"Busca por ID - Total count: {search_data_by_id.get('totalcount')}")
                    if search_data_by_id.get("data"):
                        print(f"✓ Usuário encontrado por ID: {search_data_by_id.get('data')[0]}")
                    else:
                        print(f"✗ Usuário NÃO encontrado por ID")
                else:
                    print(f"✗ Falha na busca por ID")
            else:
                print(f"✗ Nenhum usuário ativo encontrado")
        else:
            print(f"✗ Falha na busca inicial de usuários ativos")
    except Exception as e:
        print(f"✗ Erro no teste de usuário específico: {e}")


if __name__ == "__main__":
    test_glpi_connection()
