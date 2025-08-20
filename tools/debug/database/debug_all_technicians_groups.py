#!/usr/bin/env python3
"""
Script para verificar todos os técnicos e seus grupos
"""

import os
import sys

from dotenv import load_dotenv

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService


def debug_all_technicians_groups():
    print("=== DEBUG: Verificar todos os técnicos e seus grupos ===")

    # Carregar variáveis de ambiente
    load_dotenv()

    try:
        # Inicializar serviço GLPI
        service = GLPIService()

        # Garantir autenticação
        if not service._ensure_authenticated():
            print("❌ Falha na autenticação com GLPI")
            return

        print("✅ Autenticado com sucesso no GLPI")

        print("\n🔍 ETAPA 1: Buscar todos os usuários com perfil técnico (ID 6)")

        # Buscar todos os usuários com perfil técnico
        response = service._make_authenticated_request(
            "GET",
            f"{service.glpi_url}/search/Profile_User",
            params={
                "range": "0-999",
                "criteria[0][field]": "5",  # profiles_id
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": "6",  # Perfil técnico
                "forcedisplay[0]": "4",  # users_id
                "forcedisplay[1]": "5",  # profiles_id
            },
        )

        if not response or not response.ok:
            print("❌ Erro ao buscar usuários com perfil técnico")
            return

        profile_users = response.json()
        if not profile_users or not profile_users.get("data"):
            print("❌ Nenhum usuário com perfil técnico encontrado")
            return

        print(f"✅ {len(profile_users['data'])} usuários com perfil técnico encontrados")

        # Extrair IDs dos usuários
        user_ids = []
        for entry in profile_users["data"]:
            if "4" in entry:  # users_id
                user_ids.append(entry["4"])

        print(f"\n🔍 ETAPA 2: Verificar dados e grupos de cada técnico")

        technicians_by_group = {
            "N1": [],
            "N2": [],
            "N3": [],
            "N4": [],
            "SEM_GRUPO": [],
            "OUTROS_GRUPOS": [],
        }

        for user_id in user_ids:
            try:
                # Buscar dados do usuário
                user_response = service._make_authenticated_request("GET", f"{service.glpi_url}/User/{user_id}")

                if not user_response or not user_response.ok:
                    continue

                user_data = user_response.json()

                # Verificar se é ativo e não deletado
                is_active = user_data.get("is_active", 0) == 1
                is_deleted = user_data.get("is_deleted", 0) == 1

                if not is_active or is_deleted:
                    continue

                # Construir nome
                display_name = ""
                if "realname" in user_data and "firstname" in user_data:
                    display_name = f"{user_data['firstname']} {user_data['realname']}"
                elif "realname" in user_data:
                    display_name = user_data["realname"]
                elif "name" in user_data:
                    display_name = user_data["name"]

                # Buscar grupos do usuário
                groups_response = service._make_authenticated_request(
                    "GET",
                    f"{service.glpi_url}/search/Group_User",
                    params={
                        "range": "0-99",
                        "criteria[0][field]": "4",  # users_id
                        "criteria[0][searchtype]": "equals",
                        "criteria[0][value]": str(user_id),
                        "forcedisplay[0]": "3",  # groups_id
                        "forcedisplay[1]": "4",  # users_id
                    },
                )

                user_groups = []
                if groups_response and groups_response.ok:
                    groups_data = groups_response.json()
                    if groups_data and groups_data.get("data"):
                        for group_entry in groups_data["data"]:
                            if "3" in group_entry:  # groups_id
                                user_groups.append(int(group_entry["3"]))

                # Determinar nível baseado nos grupos
                level = None
                for level_name, group_id in service.service_levels.items():
                    if group_id in user_groups:
                        level = level_name
                        break

                # Categorizar técnico
                tech_info = {"id": user_id, "name": display_name, "groups": user_groups}

                if level:
                    technicians_by_group[level].append(tech_info)
                elif not user_groups:
                    technicians_by_group["SEM_GRUPO"].append(tech_info)
                else:
                    technicians_by_group["OUTROS_GRUPOS"].append(tech_info)

            except Exception as e:
                print(f"❌ Erro ao processar usuário {user_id}: {e}")

        print("\n📊 RESULTADO: Técnicos por categoria")

        for category, techs in technicians_by_group.items():
            print(f"\n--- {category} ({len(techs)} técnicos) ---")
            for tech in techs:
                groups_str = ", ".join(map(str, tech["groups"])) if tech["groups"] else "Nenhum"
                print(f"  - {tech['name']} (ID: {tech['id']}) - Grupos: [{groups_str}]")

        print("\n🔍 ETAPA 3: Verificar se grupos N1 e N4 existem no GLPI")

        for level_name, group_id in service.service_levels.items():
            group_response = service._make_authenticated_request("GET", f"{service.glpi_url}/Group/{group_id}")

            if group_response and group_response.ok:
                group_data = group_response.json()
                group_name = group_data.get("name", "Nome não encontrado")
                print(f"✅ {level_name} (ID {group_id}): {group_name}")
            else:
                print(f"❌ {level_name} (ID {group_id}): Grupo não encontrado")

        print("\n=== FIM DO DEBUG ===")

    except Exception as e:
        print(f"❌ Erro geral no debug: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    debug_all_technicians_groups()
