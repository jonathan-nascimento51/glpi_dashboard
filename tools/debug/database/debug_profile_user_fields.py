#!/usr/bin/env python3
"""
Script para debugar os campos corretos do Profile_User
"""

import json
import os
import sys

from dotenv import load_dotenv

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService


def debug_profile_user_fields(service):
    """
    Debug detalhado dos campos do Profile_User
    """
    print("=== DEBUG: Campos do Profile_User ===")

    try:
        # Buscar com todos os campos possíveis
        response = service._make_authenticated_request(
            "GET",
            f"{service.glpi_url}/search/Profile_User",
            params={
                "range": "0-5",
                "criteria[0][field]": "5",  # profiles_id
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": "14",  # N3
                # Tentar vários campos
                "forcedisplay[0]": "2",  # id
                "forcedisplay[1]": "4",  # users_id
                "forcedisplay[2]": "5",  # profiles_id
                "forcedisplay[3]": "80",  # entities_id
                "forcedisplay[4]": "1",  # name (se existir)
                "forcedisplay[5]": "3",  # outro campo
            },
        )

        if response and response.ok:
            data = response.json()
            print(f"\n📊 Resposta completa:")
            print(json.dumps(data, indent=2, ensure_ascii=False))

            if "data" in data and data["data"]:
                record = data["data"][0]
                print(f"\n🔍 Análise do primeiro registro:")
                for field_id, value in record.items():
                    print(f"   Campo {field_id}: {value} (tipo: {type(value)})")

    except Exception as e:
        print(f"❌ Erro no debug: {e}")


def test_direct_profile_user_access(service):
    """
    Testa acesso direto aos registros Profile_User
    """
    print(f"\n=== TESTE: Acesso Direto Profile_User ===")

    try:
        # Buscar Profile_User sem forcedisplay para ver estrutura natural
        response = service._make_authenticated_request(
            "GET",
            f"{service.glpi_url}/search/Profile_User",
            params={
                "range": "0-3",
                "criteria[0][field]": "5",
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": "14",  # N3
            },
        )

        if response and response.ok:
            data = response.json()
            print(f"\n📊 Estrutura natural (sem forcedisplay):")
            print(json.dumps(data, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"❌ Erro no teste direto: {e}")


def search_all_profile_users(service):
    """
    Busca todos os Profile_User para entender a estrutura
    """
    print(f"\n=== BUSCA: Todos os Profile_User ===")

    try:
        response = service._make_authenticated_request(
            "GET",
            f"{service.glpi_url}/search/Profile_User",
            params={
                "range": "0-10",
                "forcedisplay[0]": "2",  # id
                "forcedisplay[1]": "4",  # users_id
                "forcedisplay[2]": "5",  # profiles_id
            },
        )

        if response and response.ok:
            data = response.json()
            print(f"\n📊 Primeiros 10 Profile_User:")
            print(json.dumps(data, indent=2, ensure_ascii=False))

            if "data" in data and data["data"]:
                print(f"\n🔍 Análise dos registros:")
                for i, record in enumerate(data["data"][:3]):
                    print(f"   Registro {i+1}:")
                    for field_id, value in record.items():
                        print(f"      Campo {field_id}: {value}")

                    # Se campo 4 tem um valor, tentar buscar como ID
                    users_id_value = record.get("4")
                    if users_id_value and users_id_value != "SOLICITANTE":
                        print(f"      Tentando buscar usuário com ID/nome: {users_id_value}")

                        # Tentar como ID numérico
                        try:
                            user_id = int(users_id_value)
                            user_response = service._make_authenticated_request("GET", f"{service.glpi_url}/User/{user_id}")
                            if user_response and user_response.ok:
                                user_data = user_response.json()
                                print(f"         ✅ Usuário encontrado: {user_data.get('name', 'N/A')}")
                            else:
                                print(f"         ❌ Usuário ID {user_id} não encontrado")
                        except ValueError:
                            # Não é um ID numérico, tentar como nome
                            print(f"         Tentando como nome de usuário: {users_id_value}")
                            user_data = search_user_by_name(service, users_id_value)
                            if user_data:
                                print(
                                    f"         ✅ Usuário encontrado: {user_data.get('name', 'N/A')} (ID: {user_data.get('id')})"
                                )
                            else:
                                print(f"         ❌ Usuário {users_id_value} não encontrado")

    except Exception as e:
        print(f"❌ Erro na busca geral: {e}")


def search_user_by_name(service, username):
    """
    Busca usuário por nome
    """
    try:
        response = service._make_authenticated_request(
            "GET",
            f"{service.glpi_url}/search/User",
            params={
                "range": "0-1",
                "criteria[0][field]": "1",  # name
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": username,
                "forcedisplay[0]": "2",  # id
            },
        )

        if response and response.ok:
            data = response.json()
            if "data" in data and data["data"]:
                user_id = data["data"][0].get("2")
                if user_id:
                    user_response = service._make_authenticated_request("GET", f"{service.glpi_url}/User/{user_id}")
                    if user_response and user_response.ok:
                        return user_response.json()
        return None
    except:
        return None


def investigate_profile_user_schema(service):
    """
    Investiga o schema do Profile_User
    """
    print(f"\n=== INVESTIGAÇÃO: Schema Profile_User ===")

    try:
        # Tentar acessar o schema se disponível
        response = service._make_authenticated_request("GET", f"{service.glpi_url}/listSearchOptions/Profile_User")

        if response and response.ok:
            schema = response.json()
            print(f"\n📋 Schema Profile_User:")
            print(json.dumps(schema, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Schema não disponível")

    except Exception as e:
        print(f"❌ Erro ao buscar schema: {e}")


def main():
    """
    Função principal para debug completo
    """
    print("=== DEBUG COMPLETO DOS CAMPOS PROFILE_USER ===")

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

        # Debug dos campos
        debug_profile_user_fields(service)

        # Teste de acesso direto
        test_direct_profile_user_access(service)

        # Busca geral
        search_all_profile_users(service)

        # Investigar schema
        investigate_profile_user_schema(service)

    except Exception as e:
        print(f"❌ Erro geral no debug: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
