#!/usr/bin/env python3
"""
Script para verificar os perfis corretos dos técnicos
"""

import os
import sys

from dotenv import load_dotenv

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService


def debug_correct_profiles():
    print("=== DEBUG: Verificar perfis corretos dos técnicos ===")

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

        # Perfis que podem ser técnicos
        tech_profiles = {6: "Tecnico", 10: "Perfil 10", 13: "N2", 14: "N3", 15: "N4"}

        print("\n🔍 ETAPA 1: Verificar usuários em perfis técnicos")

        all_technicians = []

        for profile_id, profile_name in tech_profiles.items():
            print(f"\n--- Verificando {profile_name} (ID {profile_id}) ---")

            response = service._make_authenticated_request(
                "GET",
                f"{service.glpi_url}/search/Profile_User",
                params={
                    "range": "0-999",
                    "criteria[0][field]": "5",  # profiles_id
                    "criteria[0][searchtype]": "equals",
                    "criteria[0][value]": str(profile_id),
                    "forcedisplay[0]": "4",  # users_id
                    "forcedisplay[1]": "5",  # profiles_id
                },
            )

            if response and response.ok:
                profile_users = response.json()
                user_count = len(profile_users.get("data", [])) if profile_users else 0
                print(f"✅ {user_count} usuários encontrados")

                if user_count > 0 and profile_users.get("data"):
                    for user_entry in profile_users["data"]:
                        if "4" in user_entry:  # users_id
                            user_id = user_entry["4"]

                            # Buscar dados do usuário
                            user_response = service._make_authenticated_request("GET", f"{service.glpi_url}/User/{user_id}")

                            if user_response and user_response.ok:
                                user_data = user_response.json()

                                # Se a resposta é uma lista, pegar o primeiro item
                                if isinstance(user_data, list) and user_data:
                                    user_data = user_data[0]

                                if isinstance(user_data, dict):
                                    # Construir nome
                                    display_name = ""
                                    if "realname" in user_data and "firstname" in user_data:
                                        display_name = f"{user_data['firstname']} {user_data['realname']}"
                                    elif "realname" in user_data:
                                        display_name = user_data["realname"]
                                    elif "name" in user_data:
                                        display_name = user_data["name"]

                                    is_active = user_data.get("is_active", 0) == 1
                                    is_deleted = user_data.get("is_deleted", 0) == 1

                                    if is_active and not is_deleted:
                                        print(f"  ✅ {display_name} (ID: {user_id}) - Ativo")

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
                                        for (
                                            level_name,
                                            group_id,
                                        ) in service.service_levels.items():
                                            if group_id in user_groups:
                                                level = level_name
                                                break

                                        groups_str = ", ".join(map(str, user_groups)) if user_groups else "Nenhum"
                                        print(f"    Grupos: [{groups_str}] - Nível: {level or 'Não identificado'}")

                                        # Contar tickets
                                        try:
                                            tech_field_id = service.field_ids.get("technician_field_id", 8)
                                            total_tickets = service._count_tickets_by_technician_optimized(
                                                int(user_id), tech_field_id
                                            )
                                            print(f"    Tickets: {total_tickets}")
                                        except Exception as e:
                                            print(f"    Erro ao contar tickets: {e}")

                                        all_technicians.append(
                                            {
                                                "id": user_id,
                                                "name": display_name,
                                                "profile": profile_name,
                                                "profile_id": profile_id,
                                                "groups": user_groups,
                                                "level": level,
                                            }
                                        )
                                    else:
                                        print(f"  ❌ {display_name} (ID: {user_id}) - Inativo ou deletado")
            else:
                print(f"❌ Erro ao buscar usuários do perfil {profile_name}")

        print(f"\n📊 RESUMO: {len(all_technicians)} técnicos ativos encontrados")

        # Agrupar por nível
        by_level = {}
        for tech in all_technicians:
            level = tech["level"] or "SEM_NIVEL"
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(tech)

        for level, techs in by_level.items():
            print(f"\n--- {level} ({len(techs)} técnicos) ---")
            for tech in techs:
                print(f"  - {tech['name']} (Perfil: {tech['profile']})")

        print("\n🔍 ETAPA 2: Verificar se precisamos atualizar o código")

        print("\nProblemas identificados:")
        print("1. O código atual busca apenas perfil ID 6 (Tecnico) que tem 0 usuários")
        print("2. Os técnicos estão nos perfis ID 13 (N2), 14 (N3), 15 (N4)")
        print("3. Não há perfil específico para N1, pode estar no perfil genérico")

        print("\nSoluções possíveis:")
        print("1. Atualizar código para buscar múltiplos perfis: [13, 14, 15]")
        print("2. Ou buscar todos os usuários e filtrar por grupos N1-N4")
        print("3. Verificar se existe um perfil N1 (pode ser ID diferente)")

        print("\n=== FIM DO DEBUG ===")

    except Exception as e:
        print(f"❌ Erro geral no debug: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    debug_correct_profiles()
