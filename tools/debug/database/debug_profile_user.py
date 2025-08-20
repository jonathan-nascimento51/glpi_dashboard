#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debugar a estrutura dos dados do Profile_User
Para entender por que não conseguimos extrair os IDs dos usuários
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json

from services.glpi_service import GLPIService


def debug_profile_user_structure():
    """Debug detalhado da estrutura do Profile_User"""

    print("=== DEBUG PROFILE_USER STRUCTURE ===")

    # Inicializar serviço
    glpi_service = GLPIService()

    # Teste 1: Autenticação
    print("\n1. Testando autenticação...")
    if not glpi_service.authenticate():
        print("❌ Falha na autenticação")
        return
    print("✅ Autenticação bem-sucedida")

    # Teste 2: Buscar Profile_User com mais detalhes
    print("\n2. Analisando estrutura do Profile_User...")
    try:
        profile_params = {
            "range": "0-10",  # Limitar para análise detalhada
            "criteria[0][field]": "4",  # Campo Perfil na tabela Profile_User
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": "6",  # ID do perfil técnico
            "forcedisplay[0]": "2",  # ID do Profile_User
            "forcedisplay[1]": "5",  # Usuário (users_id)
            "forcedisplay[2]": "4",  # Perfil
            "forcedisplay[3]": "80",  # Entidade
        }

        response = glpi_service._make_authenticated_request(
            "GET", f"{glpi_service.glpi_url}/search/Profile_User", params=profile_params
        )

        if response and response.ok:
            result = response.json()
            total_count = result.get("totalcount", 0)
            print(f"✅ Profile_User encontrou {total_count} registros")

            data = result.get("data", [])
            print(f"\nAnalisando primeiros {len(data)} registros:")

            for i, record in enumerate(data):
                print(f"\n--- Registro {i+1} ---")
                print(f"Tipo: {type(record)}")
                print(f"Chaves disponíveis: {list(record.keys()) if isinstance(record, dict) else 'N/A'}")

                for key, value in record.items():
                    print(f"  Campo {key}: {repr(value)} (tipo: {type(value)})")

                # Tentar extrair user_id de diferentes formas
                print("\nTentativas de extração de user_id:")

                # Método 1: Campo "5" direto
                if "5" in record:
                    field_5 = record["5"]
                    print(f"  Campo '5' direto: {repr(field_5)} (tipo: {type(field_5)})")

                    # Se for string, tentar diferentes abordagens
                    if isinstance(field_5, str):
                        print(f"    Como string: '{field_5}'")
                        print(f"    Stripped: '{field_5.strip()}'")
                        print(f"    É dígito? {field_5.strip().isdigit()}")

                        # Tentar parse como JSON
                        try:
                            import json

                            parsed = json.loads(field_5)
                            print(f"    Parse JSON: {repr(parsed)} (tipo: {type(parsed)})")
                        except:
                            print(f"    Não é JSON válido")

                    # Se for número
                    elif isinstance(field_5, (int, float)):
                        print(f"    Como número: {field_5}")
                        print(f"    Como string: '{str(field_5)}'")

                # Método 2: Procurar por padrões de user_id
                for key, value in record.items():
                    if isinstance(value, str) and value.strip().isdigit():
                        print(f"  Campo {key} contém número: {value}")
                    elif isinstance(value, (int, float)) and value > 0:
                        print(f"  Campo {key} é número positivo: {value}")
        else:
            print(f"❌ Erro na busca Profile_User: {response.status_code if response else 'Sem resposta'}")
    except Exception as e:
        print(f"❌ Erro na análise do Profile_User: {e}")

    # Teste 3: Comparar com o que funciona no ranking
    print("\n3. Comparando com método que funciona no ranking...")
    try:
        # Usar os mesmos parâmetros do método que funciona
        ranking_params = {
            "range": "0-10",
            "criteria[0][field]": "4",
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": "6",
            "forcedisplay[0]": "2",
            "forcedisplay[1]": "5",
            "forcedisplay[2]": "80",
        }

        response = glpi_service._make_authenticated_request(
            "GET", f"{glpi_service.glpi_url}/search/Profile_User", params=ranking_params
        )

        if response and response.ok:
            result = response.json()
            data = result.get("data", [])
            print(f"✅ Método do ranking retornou {len(data)} registros")

            for i, record in enumerate(data):
                print(f"\n--- Registro {i+1} (método ranking) ---")
                for key, value in record.items():
                    print(f"  Campo {key}: {repr(value)}")
        else:
            print(f"❌ Erro no método do ranking: {response.status_code if response else 'Sem resposta'}")
    except Exception as e:
        print(f"❌ Erro no teste do método ranking: {e}")

    # Teste 4: Buscar um usuário específico que sabemos que existe
    print("\n4. Testando usuário específico conhecido...")
    try:
        # Sabemos que 'anderson-oliveira' aparece no Profile_User
        user_search_params = {
            "range": "0-10",
            "criteria[0][field]": "1",  # Campo name (username)
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": "anderson-oliveira",
            "forcedisplay[0]": "2",  # ID
            "forcedisplay[1]": "1",  # Username
            "forcedisplay[2]": "9",  # Realname
            "forcedisplay[3]": "34",  # Firstname
        }

        response = glpi_service._make_authenticated_request(
            "GET", f"{glpi_service.glpi_url}/search/User", params=user_search_params
        )

        if response and response.ok:
            result = response.json()
            data = result.get("data", [])
            print(f"✅ Usuário 'anderson-oliveira' encontrado: {len(data)} registros")

            for record in data:
                user_id = record.get("2", "N/A")
                username = record.get("1", "N/A")
                print(f"  ID: {user_id}, Username: {username}")

                # Agora verificar se este ID aparece no Profile_User
                print(f"\n  Verificando se ID {user_id} tem perfil técnico...")
                profile_check_params = {
                    "range": "0-999",
                    "criteria[0][field]": "5",  # Campo users_id
                    "criteria[0][searchtype]": "equals",
                    "criteria[0][value]": str(user_id),
                    "criteria[1][field]": "4",  # Campo profiles_id
                    "criteria[1][searchtype]": "equals",
                    "criteria[1][value]": "6",
                    "criteria[1][link]": "AND",
                    "forcedisplay[0]": "2",
                    "forcedisplay[1]": "5",
                    "forcedisplay[2]": "4",
                }

                profile_response = glpi_service._make_authenticated_request(
                    "GET",
                    f"{glpi_service.glpi_url}/search/Profile_User",
                    params=profile_check_params,
                )

                if profile_response and profile_response.ok:
                    profile_result = profile_response.json()
                    profile_count = profile_result.get("totalcount", 0)
                    print(f"    ✅ Perfil técnico para ID {user_id}: {profile_count} registros")

                    if profile_count > 0:
                        profile_data = profile_result.get("data", [])
                        for prof_record in profile_data:
                            print(f"    Registro perfil: {prof_record}")
                else:
                    print(
                        f"    ❌ Erro ao verificar perfil: {profile_response.status_code if profile_response else 'Sem resposta'}"
                    )
        else:
            print(f"❌ Usuário 'anderson-oliveira' não encontrado: {response.status_code if response else 'Sem resposta'}")
    except Exception as e:
        print(f"❌ Erro no teste de usuário específico: {e}")

    print("\n=== DEBUG CONCLUÍDO ===")


if __name__ == "__main__":
    debug_profile_user_structure()
