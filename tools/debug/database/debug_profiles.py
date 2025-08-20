#!/usr/bin/env python3
"""
Script para verificar todos os perfis disponíveis no GLPI
"""

import os
import sys

from dotenv import load_dotenv

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService


def debug_profiles():
    print("=== DEBUG: Verificar perfis disponíveis no GLPI ===")

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

        print("\n🔍 ETAPA 1: Listar todos os perfis")

        # Buscar todos os perfis
        response = service._make_authenticated_request("GET", f"{service.glpi_url}/Profile", params={"range": "0-99"})

        if response and response.ok:
            profiles = response.json()
            if profiles:
                print(f"✅ {len(profiles)} perfis encontrados:")
                for profile in profiles:
                    profile_id = profile.get("id", "N/A")
                    profile_name = profile.get("name", "Nome não encontrado")
                    print(f"  - ID {profile_id}: {profile_name}")
            else:
                print("❌ Nenhum perfil encontrado")
        else:
            print(f"❌ Erro ao buscar perfis: {response.status_code if response else 'Sem resposta'}")

        print("\n🔍 ETAPA 2: Verificar usuários com diferentes perfis")

        # Testar alguns IDs de perfil comuns
        test_profile_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        for profile_id in test_profile_ids:
            response = service._make_authenticated_request(
                "GET",
                f"{service.glpi_url}/search/Profile_User",
                params={
                    "range": "0-10",
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
                print(f"  - Perfil ID {profile_id}: {user_count} usuários")

                # Se encontrou usuários, mostrar alguns exemplos
                if user_count > 0 and profile_users.get("data"):
                    print(f"    Exemplos de usuários:")
                    for i, user_entry in enumerate(profile_users["data"][:3]):
                        if "4" in user_entry:  # users_id
                            user_id = user_entry["4"]

                            # Buscar nome do usuário
                            user_response = service._make_authenticated_request("GET", f"{service.glpi_url}/User/{user_id}")

                            if user_response and user_response.ok:
                                user_data = user_response.json()

                                # Se a resposta é uma lista, pegar o primeiro item
                                if isinstance(user_data, list) and user_data:
                                    user_data = user_data[0]

                                if isinstance(user_data, dict):
                                    display_name = ""
                                    if "realname" in user_data and "firstname" in user_data:
                                        display_name = f"{user_data['firstname']} {user_data['realname']}"
                                    elif "realname" in user_data:
                                        display_name = user_data["realname"]
                                    elif "name" in user_data:
                                        display_name = user_data["name"]

                                    is_active = user_data.get("is_active", 0) == 1
                                    is_deleted = user_data.get("is_deleted", 0) == 1

                                    print(
                                        f"      {i+1}. ID {user_id}: {display_name} (Ativo: {is_active}, Deletado: {is_deleted})"
                                    )
                                else:
                                    print(f"      {i+1}. ID {user_id}: Formato de dados inesperado")
            else:
                print(f"  - Perfil ID {profile_id}: Erro na consulta")

        print("\n🔍 ETAPA 3: Verificar método atual do ranking")

        # Verificar como o método atual busca técnicos
        print("\nMétodo atual usa:")
        print("- Busca Profile_User com profiles_id = 6")
        print("- Filtra usuários ativos (is_active = 1)")
        print("- Filtra usuários não deletados (is_deleted = 0)")

        # Tentar buscar com o método atual
        print("\n🔍 ETAPA 4: Testar busca atual do ranking")

        try:
            # Replicar a busca do método get_technician_ranking
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

            if response and response.ok:
                result = response.json()
                print(f"Resposta da API: {result}")
            else:
                print(f"Erro na busca: {response.status_code if response else 'Sem resposta'}")
                if response:
                    print(f"Conteúdo da resposta: {response.text}")

        except Exception as e:
            print(f"Erro na busca: {e}")

        print("\n=== FIM DO DEBUG ===")

    except Exception as e:
        print(f"❌ Erro geral no debug: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    debug_profiles()
