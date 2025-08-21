#!/usr/bin/env python3
"""
Script para testar se os grupos técnicos configurados existem no GLPI
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService


def test_groups():
    """Testa se os grupos técnicos existem no GLPI"""
    print("=== TESTE DE GRUPOS TÉCNICOS ===")

    service = GLPIService()

    # Verificar autenticação
    print("\n1. Testando autenticação...")
    if not service._ensure_authenticated():
        print("❌ Falha na autenticação")
        return
    print("✅ Autenticação bem-sucedida")

    # Verificar se os grupos configurados existem
    print("\n2. Verificando se os grupos técnicos existem...")
    print(f"Grupos configurados: {service.service_levels}")

    for level, group_id in service.service_levels.items():
        print(f"\n🔍 Verificando grupo {level} (ID: {group_id})...")

        try:
            response = service._make_authenticated_request("GET", f"{service.glpi_url}/Group/{group_id}")

            if response and response.ok:
                group_data = response.json()
                group_name = group_data.get("name", "Nome não encontrado")
                print(f"  ✅ Grupo existe: {group_name}")
            else:
                status_code = response.status_code if response else "None"
                print(f"  ❌ Grupo não encontrado (Status: {status_code})")

        except Exception as e:
            print(f"  ❌ Erro ao verificar grupo: {e}")

    # Buscar alguns grupos existentes para comparação
    print("\n3. Buscando grupos existentes no GLPI...")
    try:
        search_params = {
            "range": "0-20",
            "is_deleted": 0,
            "forcedisplay[0]": "2",  # ID
            "forcedisplay[1]": "1",  # Nome
        }

        response = service._make_authenticated_request("GET", f"{service.glpi_url}/search/Group", params=search_params)

        if response and response.ok:
            data = response.json()
            if "data" in data and data["data"]:
                print("  Grupos encontrados no GLPI:")
                for group in data["data"][:10]:  # Mostrar apenas os primeiros 10
                    group_id = group.get("2", "N/A")
                    group_name = group.get("1", "N/A")
                    print(f"    ID: {group_id} - Nome: {group_name}")
            else:
                print("  Nenhum grupo encontrado")
        else:
            print(f"  ❌ Erro ao buscar grupos (Status: {response.status_code if response else 'None'})")

    except Exception as e:
        print(f"  ❌ Erro ao buscar grupos: {e}")

    print("\n=== FIM DO TESTE ===")


if __name__ == "__main__":
    test_groups()
