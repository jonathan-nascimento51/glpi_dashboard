#!/usr/bin/env python3
"""
Script para investigar por que técnicos N1 e N4 não aparecem no ranking
"""

import os
import sys

from dotenv import load_dotenv

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService


def debug_n1_n4_missing():
    print("=== DEBUG: Por que N1 e N4 não aparecem no ranking? ===")

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

        # Verificar grupos N1 e N4 especificamente
        print("\n🔍 ETAPA 1: Verificar usuários nos grupos N1 e N4")

        for level in ["N1", "N4"]:
            group_id = service.service_levels[level]
            print(f"\n--- Verificando {level} (Grupo ID: {group_id}) ---")

            try:
                # Buscar usuários no grupo
                response = service._make_authenticated_request(
                    "GET",
                    f"{service.glpi_url}/search/Group_User",
                    params={
                        "range": "0-99",
                        "criteria[0][field]": "3",  # Campo groups_id
                        "criteria[0][searchtype]": "equals",
                        "criteria[0][value]": str(group_id),
                        "forcedisplay[0]": "3",  # groups_id
                        "forcedisplay[1]": "4",  # users_id
                    },
                )

                if response and response.ok:
                    group_users = response.json()
                    if group_users and group_users.get("data"):
                        print(f"   ✅ {len(group_users['data'])} usuários encontrados no grupo {level}:")

                        for user_entry in group_users["data"]:
                            if "4" in user_entry:  # users_id
                                user_id = user_entry["4"]

                                # Buscar dados do usuário
                                user_response = service._make_authenticated_request(
                                    "GET", f"{service.glpi_url}/User/{user_id}"
                                )

                                if user_response and user_response.ok:
                                    user_data = user_response.json()

                                    # Construir nome
                                    display_name = ""
                                    if "realname" in user_data and "firstname" in user_data:
                                        display_name = f"{user_data['firstname']} {user_data['realname']}"
                                    elif "realname" in user_data:
                                        display_name = user_data["realname"]
                                    elif "name" in user_data:
                                        display_name = user_data["name"]

                                    # Verificar se é ativo
                                    is_active = user_data.get("is_active", 0) == 1
                                    is_deleted = user_data.get("is_deleted", 0) == 1

                                    print(f"     - ID {user_id}: {display_name} (Ativo: {is_active}, Deletado: {is_deleted})")

                                    # Verificar se tem perfil de técnico (ID 6)
                                    profile_response = service._make_authenticated_request(
                                        "GET",
                                        f"{service.glpi_url}/search/Profile_User",
                                        params={
                                            "range": "0-99",
                                            "criteria[0][field]": "4",  # users_id
                                            "criteria[0][searchtype]": "equals",
                                            "criteria[0][value]": str(user_id),
                                            "criteria[1][field]": "5",  # profiles_id
                                            "criteria[1][searchtype]": "equals",
                                            "criteria[1][value]": "6",  # Perfil técnico
                                            "criteria[1][link]": "AND",
                                            "forcedisplay[0]": "4",  # users_id
                                            "forcedisplay[1]": "5",  # profiles_id
                                        },
                                    )

                                    has_tech_profile = False
                                    if profile_response and profile_response.ok:
                                        profile_data = profile_response.json()
                                        has_tech_profile = profile_data and profile_data.get("data")

                                    print(f"       Perfil Técnico (ID 6): {has_tech_profile}")

                                    # Se atende todos os critérios, verificar por que não aparece no ranking
                                    if is_active and not is_deleted and has_tech_profile:
                                        print(f"       ⚠️  DEVERIA APARECER NO RANKING!")

                                        # Verificar contagem de tickets
                                        tech_field_id = service.field_ids.get("technician_field_id", 8)
                                        try:
                                            total_tickets = service._count_tickets_by_technician_optimized(
                                                int(user_id), tech_field_id
                                            )
                                            print(f"       Tickets: {total_tickets}")
                                        except Exception as e:
                                            print(f"       Erro ao contar tickets: {e}")
                                    else:
                                        print(f"       ❌ Não atende critérios para ranking")
                                else:
                                    print(f"     - ID {user_id}: Erro ao buscar dados do usuário")
                    else:
                        print(f"   ❌ Nenhum usuário encontrado no grupo {level}")
                else:
                    print(
                        f"   ❌ Erro ao buscar usuários do grupo {level}: {response.status_code if response else 'Sem resposta'}"
                    )

            except Exception as e:
                print(f"   ❌ Erro ao verificar grupo {level}: {e}")

        print("\n🔍 ETAPA 2: Verificar critérios de filtragem no método get_technician_ranking")

        # Verificar se o método está filtrando corretamente
        print("\nCritérios usados no ranking:")
        print("- Perfil ID 6 (técnico)")
        print("- is_active = 1")
        print("- is_deleted = 0")
        print("- Deve ter pelo menos 1 ticket")

        print("\n=== FIM DO DEBUG ===")

    except Exception as e:
        print(f"❌ Erro geral no debug: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    debug_n1_n4_missing()
