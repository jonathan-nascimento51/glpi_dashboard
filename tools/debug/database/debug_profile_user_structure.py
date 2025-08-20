#!/usr/bin/env python3
"""
Script para debugar a estrutura de dados retornada pelo endpoint Profile_User
"""

import json
import os
import sys

from dotenv import load_dotenv

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService


def debug_profile_user_structure(service):
    """
    Debug da estrutura de dados do endpoint Profile_User
    """
    print("=== DEBUG: Estrutura Profile_User ===")

    try:
        # Buscar dados do Profile_User para análise
        response = service._make_authenticated_request(
            "GET",
            f"{service.glpi_url}/search/Profile_User",
            params={
                "range": "0-5",  # Apenas 5 registros para debug
                "forcedisplay[0]": "4",  # users_id
                "forcedisplay[1]": "5",  # profiles_id
            },
        )

        if response and response.ok:
            data = response.json()

            print(f"\n📊 Resposta completa:")
            print(json.dumps(data, indent=2, ensure_ascii=False))

            if "data" in data:
                print(f"\n🔍 Analisando estrutura dos dados:")
                print(f"   Tipo de 'data': {type(data['data'])}")
                print(f"   Quantidade de registros: {len(data['data'])}")

                if data["data"]:
                    first_record = data["data"][0]
                    print(f"   Tipo do primeiro registro: {type(first_record)}")
                    print(f"   Conteúdo do primeiro registro: {first_record}")

                    if isinstance(first_record, dict):
                        print(f"   Chaves disponíveis: {list(first_record.keys())}")
                    elif isinstance(first_record, list):
                        print(f"   Tamanho da lista: {len(first_record)}")
                        print(f"   Conteúdo da lista: {first_record}")

        else:
            print(f"❌ Erro na requisição: {response.status_code if response else 'Sem resposta'}")

    except Exception as e:
        print(f"❌ Erro no debug: {e}")
        import traceback

        traceback.print_exc()


def debug_user_endpoint(service):
    """
    Debug do endpoint User para verificar estrutura
    """
    print(f"\n=== DEBUG: Estrutura User ===")

    try:
        # Buscar alguns usuários para análise
        response = service._make_authenticated_request(
            "GET",
            f"{service.glpi_url}/search/User",
            params={
                "range": "0-3",
                "forcedisplay[0]": "2",  # id
                "forcedisplay[1]": "1",  # name
                "forcedisplay[2]": "8",  # is_active
                "forcedisplay[3]": "23",  # is_deleted
            },
        )

        if response and response.ok:
            data = response.json()

            print(f"\n📊 Resposta User:")
            print(json.dumps(data, indent=2, ensure_ascii=False))

            if "data" in data and data["data"]:
                first_user = data["data"][0]
                print(f"\n🔍 Estrutura do primeiro usuário:")
                print(f"   Tipo: {type(first_user)}")
                print(f"   Conteúdo: {first_user}")

                # Tentar acessar um usuário específico
                if isinstance(first_user, dict) and "2" in first_user:
                    user_id = first_user["2"]
                    print(f"\n🎯 Testando acesso direto ao usuário {user_id}:")

                    user_response = service._make_authenticated_request("GET", f"{service.glpi_url}/User/{user_id}")

                    if user_response and user_response.ok:
                        user_data = user_response.json()
                        print(f"   ✅ Dados do usuário {user_id}:")
                        print(json.dumps(user_data, indent=2, ensure_ascii=False))
                    else:
                        print(f"   ❌ Erro ao acessar usuário {user_id}")

    except Exception as e:
        print(f"❌ Erro no debug User: {e}")


def test_specific_profiles(service):
    """
    Testa perfis específicos N2, N3, N4
    """
    print(f"\n=== TESTE: Perfis Específicos N2, N3, N4 ===")

    target_profiles = {"13": "N2", "14": "N3", "15": "N4"}

    for profile_id, profile_name in target_profiles.items():
        print(f"\n🔍 Testando perfil {profile_id} ({profile_name}):")

        try:
            response = service._make_authenticated_request(
                "GET",
                f"{service.glpi_url}/search/Profile_User",
                params={
                    "range": "0-10",
                    "criteria[0][field]": "5",  # profiles_id
                    "criteria[0][searchtype]": "equals",
                    "criteria[0][value]": profile_id,
                    "forcedisplay[0]": "4",  # users_id
                    "forcedisplay[1]": "5",  # profiles_id
                },
            )

            if response and response.ok:
                data = response.json()

                print(f"   📊 Resposta para {profile_name}:")
                print(json.dumps(data, indent=2, ensure_ascii=False))

                if "data" in data:
                    print(f"   Registros encontrados: {len(data['data'])}")

                    for i, record in enumerate(data["data"][:3]):
                        print(f"   Registro {i+1}: {record} (tipo: {type(record)})")
            else:
                print(f"   ❌ Erro na requisição para {profile_name}")

        except Exception as e:
            print(f"   ❌ Erro ao testar {profile_name}: {e}")


def main():
    """
    Função principal para debug
    """
    print("=== DEBUG COMPLETO DA ESTRUTURA DE DADOS ===")

    # Carregar variáveis de ambiente
    load_dotenv()

    try:
        # Inicializar serviço GLPI
        service = GLPIService()

        # Garantir autenticação
        if not service._ensure_authenticated():
            print("❌ Falha na autenticação com GLPI")
            return

        print("✅ Autenticado com sucesso no GLPI\n")

        # Debug da estrutura Profile_User
        debug_profile_user_structure(service)

        # Debug da estrutura User
        debug_user_endpoint(service)

        # Teste de perfis específicos
        test_specific_profiles(service)

    except Exception as e:
        print(f"❌ Erro geral no debug: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
