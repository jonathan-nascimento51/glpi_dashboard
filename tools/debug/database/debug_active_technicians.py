#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para encontrar técnicos ativos no GLPI
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json

from services.glpi_service import GLPIService


def debug_active_technicians():
    """Encontrar técnicos ativos no GLPI"""
    print("=== BUSCA DE TÉCNICOS ATIVOS ===")

    glpi = GLPIService()

    # Autenticar
    if not glpi.authenticate():
        print("❌ Falha na autenticação")
        return
    print("✅ Autenticação bem-sucedida")

    # 1. Buscar todos os usuários ativos
    print("\n1. Buscando usuários ativos...")

    user_params = {
        "criteria[0][field]": "8",  # is_active
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": "1",  # ativo
        "forcedisplay[0]": "1",  # id
        "forcedisplay[1]": "5",  # username
        "forcedisplay[2]": "9",  # realname
        "forcedisplay[3]": "6",  # firstname
        "range": "0-20",
    }

    response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/search/User", params=user_params)

    active_users = []
    if response and response.status_code in [200, 206]:
        try:
            data = response.json()
            total = data.get("totalcount", 0)
            count = data.get("count", 0)
            print(f"   ✅ {total} usuários ativos ({count} retornados)")

            if count > 0 and "data" in data:
                print("   Primeiros usuários ativos:")

                for i, user in enumerate(data["data"]):
                    user_id = user.get("1", "N/A")
                    username = user.get("5", "N/A")
                    firstname = user.get("6", "")
                    realname = user.get("9", "")
                    full_name = f"{firstname} {realname}".strip() or username

                    print(f"     {i+1}. ID: {user_id}, Nome: {full_name}, Username: {username}")
                    active_users.append({"id": user_id, "username": username, "full_name": full_name})
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    else:
        print(f"   ❌ Falha na busca: {response.status_code if response else 'No response'}")

    # 2. Para cada usuário ativo, verificar se tem perfil de técnico
    print("\n2. Verificando perfis de técnico para usuários ativos...")

    technicians_found = []

    for user in active_users[:10]:  # Testar apenas os primeiros 10
        user_id = user["id"]
        print(f"\n   Verificando usuário {user_id} ({user['full_name']})...")

        # Buscar Profile_User para este usuário
        profile_params = {
            "criteria[0][field]": "2",  # users_id
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": str(user_id),
            "forcedisplay[0]": "2",  # users_id
            "forcedisplay[1]": "4",  # profiles_id
            "forcedisplay[2]": "80",  # entities_id
            "range": "0-10",
        }

        profile_response = glpi._make_authenticated_request(
            "GET", f"{glpi.glpi_url}/search/Profile_User", params=profile_params
        )

        if profile_response and profile_response.status_code in [200, 206]:
            try:
                profile_data = profile_response.json()
                profile_count = profile_data.get("count", 0)

                if profile_count > 0 and "data" in profile_data:
                    print(f"     Perfis encontrados: {profile_count}")

                    for profile in profile_data["data"]:
                        profile_id = profile.get("4", "N/A")
                        entity = profile.get("80", "N/A")

                        print(f"       Perfil: {profile_id}, Entidade: {entity}")

                        # Verificar se é perfil de técnico (ID 6)
                        if str(profile_id) == "6" or profile_id == "Tecnico":
                            print(f"       ✅ TÉCNICO ENCONTRADO!")
                            technicians_found.append(
                                {
                                    "user_id": user_id,
                                    "username": user["username"],
                                    "full_name": user["full_name"],
                                    "profile_id": profile_id,
                                    "entity": entity,
                                }
                            )
                else:
                    print(f"     Nenhum perfil encontrado")
            except Exception as e:
                print(f"     ❌ Erro ao verificar perfis: {e}")
        else:
            print(f"     ❌ Falha na busca de perfis: {profile_response.status_code if profile_response else 'No response'}")

    # 3. Resumo dos técnicos encontrados
    print(f"\n3. RESUMO - Técnicos ativos encontrados: {len(technicians_found)}")

    if technicians_found:
        print("   Lista de técnicos ativos:")
        for i, tech in enumerate(technicians_found):
            print(f"     {i+1}. {tech['full_name']} (ID: {tech['user_id']}, Username: {tech['username']})")
            print(f"        Perfil: {tech['profile_id']}, Entidade: {tech['entity']}")

            # Testar contagem de tickets
            ticket_params = {
                "criteria[0][field]": "4",  # users_id_tech
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": str(tech["user_id"]),
                "range": "0-0",  # Apenas contagem
            }

            ticket_response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/search/Ticket", params=ticket_params)

            if ticket_response and ticket_response.status_code in [200, 206]:
                try:
                    ticket_data = ticket_response.json()
                    total_tickets = ticket_data.get("totalcount", 0)
                    print(f"        Tickets: {total_tickets}")
                except Exception as e:
                    print(f"        Tickets: Erro - {e}")
            else:
                print(f"        Tickets: Falha na busca")
    else:
        print("   ❌ Nenhum técnico ativo encontrado!")
        print("   \n   POSSÍVEIS CAUSAS:")
        print("   - Perfil de técnico não é ID 6")
        print("   - Técnicos estão em perfis diferentes (13, 14, 15)")
        print("   - Técnicos estão desativados")
        print("   - Problema na estrutura de dados do GLPI")

    # 4. Verificar outros perfis possíveis
    print("\n4. Verificando outros perfis possíveis (13, 14, 15)...")

    for profile_id in ["13", "14", "15"]:
        print(f"\n   Verificando perfil {profile_id}...")

        profile_params = {
            "criteria[0][field]": "4",  # profiles_id
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": profile_id,
            "forcedisplay[0]": "2",  # users_id
            "forcedisplay[1]": "4",  # profiles_id
            "forcedisplay[2]": "5",  # username
            "range": "0-5",
        }

        response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/search/Profile_User", params=profile_params)

        if response and response.status_code in [200, 206]:
            try:
                data = response.json()
                total = data.get("totalcount", 0)
                count = data.get("count", 0)
                print(f"     {total} usuários com perfil {profile_id} ({count} retornados)")

                if count > 0 and "data" in data:
                    for i, profile in enumerate(data["data"]):
                        user_id = profile.get("2", "N/A")
                        username = profile.get("5", "N/A")
                        print(f"       {i+1}. User ID: {user_id}, Username: {username}")

                        # Verificar se o usuário está ativo
                        if str(user_id).isdigit():
                            user_response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/User/{user_id}")

                            if user_response and user_response.status_code == 200:
                                try:
                                    user_data = user_response.json()
                                    is_active = user_data.get("is_active", 0)
                                    firstname = user_data.get("firstname", "")
                                    realname = user_data.get("realname", "")
                                    name = user_data.get("name", username)
                                    full_name = f"{firstname} {realname}".strip() or name

                                    if is_active:
                                        print(f"         ✅ ATIVO: {full_name}")
                                    else:
                                        print(f"         ❌ Inativo: {full_name}")
                                except Exception as e:
                                    print(f"         ❌ Erro ao verificar usuário: {e}")
                            else:
                                print(f"         ❌ Usuário {user_id} não encontrado")
            except Exception as e:
                print(f"     ❌ Erro: {e}")
        else:
            print(f"     ❌ Falha na busca: {response.status_code if response else 'No response'}")

    print("\n=== FIM DA BUSCA ===")


if __name__ == "__main__":
    debug_active_technicians()
