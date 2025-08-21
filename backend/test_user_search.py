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


def test_user_search():
    """Testar busca de usuário específico pelo ID"""

    # Inicializar serviço GLPI
    glpi_service = GLPIService()

    # Testar busca por um ID específico de técnico que sabemos que existe
    test_user_id = "709"  # anderson-oliveira

    print(f"Testando busca por usuário ID: {test_user_id}")

    # Teste 1: Busca direta pelo endpoint User/{id}
    print("\n=== Teste 1: Busca direta pelo endpoint User/{id} ===")
    try:
        response = glpi_service._make_authenticated_request("GET", f"{glpi_service.glpi_url}/User/{test_user_id}")
        if response and response.status_code == 200:
            user_data = response.json()
            print(f"✓ Sucesso! Usuário encontrado:")
            print(f"  ID: {user_data.get('id')}")
            print(f"  Nome: {user_data.get('name')}")
            print(f"  Nome real: {user_data.get('firstname')} {user_data.get('realname')}")
            print(f"  Ativo: {user_data.get('is_active')}")
            print(f"  Deletado: {user_data.get('is_deleted')}")
        else:
            print(f"✗ Falha na busca direta. Status: {response.status_code if response else 'None'}")
    except Exception as e:
        print(f"✗ Erro na busca direta: {e}")

    # Teste 2: Busca via search API por ID
    print("\n=== Teste 2: Busca via search API por ID ===")
    try:
        search_params = {
            "range": "0-10",
            "forcedisplay[0]": "2",  # ID
            "forcedisplay[1]": "1",  # Username
            "forcedisplay[2]": "9",  # Firstname
            "forcedisplay[3]": "34",  # Realname
            "forcedisplay[4]": "8",  # is_active
            "forcedisplay[5]": "3",  # is_deleted
            "criteria[0][field]": "2",  # ID
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": test_user_id,
        }

        response = glpi_service._make_authenticated_request(
            "GET", f"{glpi_service.glpi_url}/search/User", params=search_params
        )

        if response:
            search_data = response.json()
            print(f"Status: {response.status_code}")
            print(f"Total count: {search_data.get('totalcount')}")
            print(f"Count: {search_data.get('count')}")
            if search_data.get("data"):
                print(f"✓ Primeiro resultado: {search_data.get('data')[0]}")
            else:
                print(f"✗ Nenhum resultado encontrado")
        else:
            print(f"✗ Falha na requisição")
    except Exception as e:
        print(f"✗ Erro na busca via search API: {e}")

    # Teste 3: Busca por nome de usuário
    print("\n=== Teste 3: Busca por nome de usuário ===")
    try:
        search_params = {
            "range": "0-10",
            "forcedisplay[0]": "2",  # ID
            "forcedisplay[1]": "1",  # Username
            "forcedisplay[2]": "9",  # Firstname
            "forcedisplay[3]": "34",  # Realname
            "forcedisplay[4]": "8",  # is_active
            "criteria[0][field]": "1",  # Username
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": "anderson-oliveira",
        }

        response = glpi_service._make_authenticated_request(
            "GET", f"{glpi_service.glpi_url}/search/User", params=search_params
        )

        if response:
            search_data = response.json()
            print(f"Status: {response.status_code}")
            print(f"Total count: {search_data.get('totalcount')}")
            if search_data.get("data"):
                print(f"✓ Primeiro resultado: {search_data.get('data')[0]}")
            else:
                print(f"✗ Nenhum resultado encontrado")
        else:
            print(f"✗ Falha na requisição")
    except Exception as e:
        print(f"✗ Erro na busca por nome: {e}")


if __name__ == "__main__":
    test_user_search()
