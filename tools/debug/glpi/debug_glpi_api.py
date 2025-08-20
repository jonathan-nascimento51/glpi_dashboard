#!/usr/bin/env python3
"""
Script para debugar as requisições à API do GLPI e identificar o problema
com Content-Range que está causando inconsistências nos dados.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json

from services.glpi_service import GLPIService


def debug_glpi_requests():
    """Debug detalhado das requisições GLPI"""
    print("=== DEBUG GLPI API REQUESTS ===")

    service = GLPIService()

    # Verificar autenticação
    print("\n1. Testando autenticação...")
    if not service._ensure_authenticated():
        print("❌ Falha na autenticação")
        return
    print("✅ Autenticação bem-sucedida")

    # Verificar field_ids
    print("\n2. Verificando field_ids...")
    if not service.discover_field_ids():
        print("❌ Falha ao descobrir field_ids")
        return
    print(f"✅ Field IDs descobertos: {service.field_ids}")

    # Testar requisição geral (sem filtro de grupo)
    print("\n3. Testando requisição geral (todos os tickets)...")
    general_params = {
        "is_deleted": 0,
        "range": "0-0",
        "criteria[0][field]": service.field_ids["STATUS"],
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": 1,  # Status "Novo"
    }

    try:
        response = service._make_authenticated_request("GET", f"{service.glpi_url}/search/Ticket", params=general_params)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        if "Content-Range" in response.headers:
            print(f"✅ Content-Range encontrado: {response.headers['Content-Range']}")
        else:
            print("❌ Content-Range não encontrado")
            print(f"Response text (primeiros 500 chars): {response.text[:500]}")
    except Exception as e:
        print(f"❌ Erro na requisição geral: {e}")

    # Testar requisições específicas por grupo
    print("\n4. Testando requisições por grupo específico...")
    for level, group_id in service.service_levels.items():
        print(f"\n--- Testando {level} (Grupo {group_id}) ---")

        group_params = {
            "is_deleted": 0,
            "range": "0-0",
            "criteria[0][field]": service.field_ids["GROUP"],
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": group_id,
            "criteria[1][link]": "AND",
            "criteria[1][field]": service.field_ids["STATUS"],
            "criteria[1][searchtype]": "equals",
            "criteria[1][value]": 1,  # Status "Novo"
        }

        try:
            response = service._make_authenticated_request("GET", f"{service.glpi_url}/search/Ticket", params=group_params)
            print(f"  Status Code: {response.status_code}")
            if "Content-Range" in response.headers:
                content_range = response.headers["Content-Range"]
                total = content_range.split("/")[-1] if "/" in content_range else "?"
                print(f"  ✅ Content-Range: {content_range} (Total: {total})")
            else:
                print(f"  ❌ Content-Range não encontrado")
                print(f"  Response text (primeiros 200 chars): {response.text[:200]}")

        except Exception as e:
            print(f"  ❌ Erro na requisição para {level}: {e}")

    # Testar se os grupos existem
    print("\n5. Verificando se os grupos existem no GLPI...")
    for level, group_id in service.service_levels.items():
        try:
            response = service._make_authenticated_request("GET", f"{service.glpi_url}/Group/{group_id}")
            if response.status_code == 200:
                group_data = response.json()
                print(f"  ✅ {level} (ID {group_id}): {group_data.get('name', 'Nome não encontrado')}")
            else:
                print(f"  ❌ {level} (ID {group_id}): Grupo não encontrado (Status: {response.status_code})")
        except Exception as e:
            print(f"  ❌ Erro ao verificar grupo {level}: {e}")

    print("\n=== FIM DO DEBUG ===")


if __name__ == "__main__":
    debug_glpi_requests()
