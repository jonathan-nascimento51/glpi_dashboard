#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para analisar a estrutura dos tickets e identificar campos corretos
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json

from services.glpi_service import GLPIService


def analyze_ticket_structure():
    """Analisar estrutura dos tickets para identificar campos corretos"""
    print("=== ANÁLISE DA ESTRUTURA DOS TICKETS ===")

    glpi = GLPIService()

    # Autenticar
    if not glpi.authenticate():
        print("❌ Falha na autenticação")
        return
    print("✅ Autenticação bem-sucedida")

    # 1. Buscar alguns tickets para análise
    print("\n1. Buscando tickets para análise...")
    response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/search/Ticket", params={"range": "0-20"})

    if response and response.status_code in [200, 206]:
        data = response.json()
        tickets = data.get("data", [])
        print(f"   ✅ {len(tickets)} tickets obtidos para análise")

        # Analisar estrutura dos primeiros tickets
        for i, ticket in enumerate(tickets[:5]):
            print(f"\n   Ticket {i+1} (ID: {ticket.get('2', 'N/A')})")
            print(f"     - Título: {ticket.get('1', 'N/A')[:50]}...")
            print(f"     - Campo 4 (users_id_tech): {ticket.get('4', 'N/A')}")
            print(f"     - Campo 5 (users_id_recipient): {ticket.get('5', 'N/A')}")
            print(f"     - Campo 8 (groups): {ticket.get('8', 'N/A')}")
            print(f"     - Status (campo 12): {ticket.get('12', 'N/A')}")
            print(f"     - Data criação (campo 15): {ticket.get('15', 'N/A')}")
            print(f"     - Todos os campos: {list(ticket.keys())}")

    # 2. Buscar usuários técnicos conhecidos
    print("\n2. Identificando usuários técnicos...")
    known_users = ["5", "539", "926", "1032", "1160", "1197", "1291"]

    for user_id in known_users:
        response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/User/{user_id}")

        if response and response.status_code == 200:
            try:
                user_data = response.json()
                name = user_data.get("name", "N/A")
                firstname = user_data.get("firstname", "")
                realname = user_data.get("realname", "")
                full_name = f"{firstname} {realname}".strip() or name
                print(f"   Usuário {user_id}: {full_name}")
            except Exception as e:
                print(f"   Usuário {user_id}: Erro - {e}")
        else:
            print(f"   Usuário {user_id}: Não encontrado")

    # 3. Testar busca por diferentes campos com usuários conhecidos
    print("\n3. Testando busca por diferentes campos...")

    test_fields = {
        "4": "users_id_tech",
        "5": "users_id_recipient",
        "22": "users_id_lastupdater",
        "71": "groups_id_tech",
    }

    # Testar com usuário 539 (que apareceu no campo 4)
    test_user = "539"

    for field_id, field_name in test_fields.items():
        print(f"\n   Testando campo {field_id} ({field_name}) com usuário {test_user}...")

        search_params = {
            "criteria[0][field]": field_id,
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": test_user,
            "range": "0-5",
        }

        response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/search/Ticket", params=search_params)

        if response and response.status_code in [200, 206]:
            try:
                data = response.json()
                total = data.get("totalcount", 0)
                count = data.get("count", 0)
                print(f"     ✅ {total} tickets encontrados ({count} retornados)")

                if count > 0 and "data" in data:
                    ticket = data["data"][0]
                    print(f"     📋 Exemplo: Ticket {ticket.get('2', 'N/A')}, Campo {field_id}: {ticket.get(field_id, 'N/A')}")
            except Exception as e:
                print(f"     ❌ Erro: {e}")
        else:
            print(f"     ❌ Falha na busca: {response.status_code if response else 'No response'}")

    # 4. Testar busca por grupos (campo 8 contém arrays)
    print("\n4. Testando busca por grupos...")

    # Buscar tickets que tenham grupos atribuídos
    group_params = {
        "criteria[0][field]": "8",  # groups_id_tech
        "criteria[0][searchtype]": "contains",
        "criteria[0][value]": "N1",
        "range": "0-5",
    }

    response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/search/Ticket", params=group_params)

    if response and response.status_code in [200, 206]:
        try:
            data = response.json()
            total = data.get("totalcount", 0)
            print(f"   ✅ {total} tickets encontrados com grupo 'N1'")
        except Exception as e:
            print(f"   ❌ Erro: {e}")

    # 5. Verificar Profile_User para entender a relação usuário-perfil
    print("\n5. Analisando Profile_User...")

    profile_params = {
        "criteria[0][field]": "4",  # profiles_id
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": "6",  # Perfil técnico
        "range": "0-10",
    }

    response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/search/Profile_User", params=profile_params)

    if response and response.status_code in [200, 206]:
        try:
            data = response.json()
            total = data.get("totalcount", 0)
            count = data.get("count", 0)
            print(f"   ✅ {total} Profile_User encontrados com perfil técnico ({count} retornados)")

            if count > 0 and "data" in data:
                for i, profile in enumerate(data["data"][:3]):
                    print(f"     Profile {i+1}: {profile}")
                    # Tentar extrair user_id de diferentes campos
                    user_id = profile.get("2") or profile.get("5") or profile.get("users_id")
                    print(f"     User ID extraído: {user_id}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")

    print("\n=== FIM DA ANÁLISE ===")


if __name__ == "__main__":
    analyze_ticket_structure()
