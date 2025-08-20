#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar diferentes parâmetros de busca de usuários ativos no GLPI
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json

from services.glpi_service import GLPIService


def test_user_search_parameters():
    """Testar diferentes combinações de parâmetros para buscar usuários ativos"""
    print("=== TESTE DE PARÂMETROS DE BUSCA DE USUÁRIOS ===")

    glpi = GLPIService()

    # Autenticar
    if not glpi.authenticate():
        print("❌ Falha na autenticação")
        return
    print("✅ Autenticação bem-sucedida")

    # Teste 1: Apenas is_active = 1 (atual)
    print("\n1. Teste atual: apenas is_active = 1")
    user_params_1 = {
        "range": "0-10",
        "criteria[0][field]": "8",  # Campo is_active
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": "1",
        "forcedisplay[0]": "2",  # ID
        "forcedisplay[1]": "1",  # Nome de usuário
        "forcedisplay[2]": "9",  # Primeiro nome (realname)
        "forcedisplay[3]": "34",  # Sobrenome (firstname)
    }

    response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/search/User", params=user_params_1)

    if response and response.status_code in [200, 206]:
        data = response.json()
        total = data.get("totalcount", 0)
        count = data.get("count", 0)
        print(f"   ✅ {total} usuários encontrados ({count} retornados)")
        if count > 0:
            print(f"   Primeiro usuário: {data['data'][0] if 'data' in data else 'N/A'}")
    else:
        print(f"   ❌ Erro: {response.status_code if response else 'Sem resposta'}")

    # Teste 2: is_active = 1 AND is_deleted = 0
    print("\n2. Teste: is_active = 1 AND is_deleted = 0")
    user_params_2 = {
        "range": "0-10",
        "criteria[0][field]": "8",  # Campo is_active
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": "1",
        "criteria[1][field]": "23",  # Campo is_deleted
        "criteria[1][searchtype]": "equals",
        "criteria[1][value]": "0",
        "criteria[1][link]": "AND",
        "forcedisplay[0]": "2",  # ID
        "forcedisplay[1]": "1",  # Nome de usuário
        "forcedisplay[2]": "9",  # Primeiro nome (realname)
        "forcedisplay[3]": "34",  # Sobrenome (firstname)
    }

    response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/search/User", params=user_params_2)

    if response and response.status_code in [200, 206]:
        data = response.json()
        total = data.get("totalcount", 0)
        count = data.get("count", 0)
        print(f"   ✅ {total} usuários encontrados ({count} retornados)")
        if count > 0:
            print(f"   Primeiro usuário: {data['data'][0] if 'data' in data else 'N/A'}")
    else:
        print(f"   ❌ Erro: {response.status_code if response else 'Sem resposta'}")

    # Teste 3: Apenas is_deleted = 0
    print("\n3. Teste: apenas is_deleted = 0")
    user_params_3 = {
        "range": "0-10",
        "criteria[0][field]": "23",  # Campo is_deleted
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": "0",
        "forcedisplay[0]": "2",  # ID
        "forcedisplay[1]": "1",  # Nome de usuário
        "forcedisplay[2]": "9",  # Primeiro nome (realname)
        "forcedisplay[3]": "34",  # Sobrenome (firstname)
    }

    response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/search/User", params=user_params_3)

    if response and response.status_code in [200, 206]:
        data = response.json()
        total = data.get("totalcount", 0)
        count = data.get("count", 0)
        print(f"   ✅ {total} usuários encontrados ({count} retornados)")
        if count > 0:
            print(f"   Primeiro usuário: {data['data'][0] if 'data' in data else 'N/A'}")
    else:
        print(f"   ❌ Erro: {response.status_code if response else 'Sem resposta'}")

    # Teste 4: Sem filtros (todos os usuários)
    print("\n4. Teste: todos os usuários (sem filtros)")
    user_params_4 = {
        "range": "0-10",
        "forcedisplay[0]": "2",  # ID
        "forcedisplay[1]": "1",  # Nome de usuário
        "forcedisplay[2]": "8",  # is_active
        "forcedisplay[3]": "23",  # is_deleted
    }

    response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/search/User", params=user_params_4)

    if response and response.status_code in [200, 206]:
        data = response.json()
        total = data.get("totalcount", 0)
        count = data.get("count", 0)
        print(f"   ✅ {total} usuários encontrados ({count} retornados)")
        if count > 0 and "data" in data:
            print("   Primeiros usuários com status:")
            for i, user in enumerate(data["data"][:5]):
                user_id = user.get("2", "N/A")
                username = user.get("1", "N/A")
                is_active = user.get("8", "N/A")
                is_deleted = user.get("23", "N/A")
                print(f"     {i+1}. ID: {user_id}, User: {username}, Active: {is_active}, Deleted: {is_deleted}")
    else:
        print(f"   ❌ Erro: {response.status_code if response else 'Sem resposta'}")

    # Teste 5: Verificar campos disponíveis
    print("\n5. Verificando campos disponíveis na tabela User")
    try:
        response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/listSearchOptions/User")

        if response and response.status_code == 200:
            search_options = response.json()
            print("   ✅ Campos relevantes encontrados:")

            relevant_fields = ["8", "23", "1", "2", "9", "34"]
            for field_id in relevant_fields:
                if field_id in search_options:
                    field_info = search_options[field_id]
                    print(
                        f"     Campo {field_id}: {field_info.get('name', 'N/A')} ({field_info.get('table', 'N/A')}.{field_info.get('field', 'N/A')})"
                    )
                else:
                    print(f"     Campo {field_id}: NÃO ENCONTRADO")
        else:
            print(f"   ❌ Erro ao buscar campos: {response.status_code if response else 'Sem resposta'}")
    except Exception as e:
        print(f"   ❌ Erro ao verificar campos: {e}")

    print("\n=== ANÁLISE FINAL ===")
    print("Compare os resultados acima para identificar:")
    print("1. Se o campo is_deleted (23) está causando problemas")
    print("2. Se os campos estão corretos")
    print("3. Qual combinação retorna mais usuários válidos")


if __name__ == "__main__":
    test_user_search_parameters()
