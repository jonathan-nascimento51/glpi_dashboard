#!/usr/bin/env python3

import sys

sys.path.append(".")
import json

from dotenv import load_dotenv

from services.glpi_service import GLPIService


def debug_general_vs_hierarchy():
    """Compara as funções _get_general_metrics_internal e get_ticket_count_by_hierarchy"""

    load_dotenv()
    glpi = GLPIService()

    if not glpi._ensure_authenticated():
        print("Erro na autenticação")
        return

    if not glpi.discover_field_ids():
        print("Erro na descoberta de field_ids")
        return

    print("=== DEBUG: GERAL vs HIERARQUIA ===")
    print(f"Status map: {glpi.status_map}")
    print(f"Field IDs: {glpi.field_ids}")
    print()

    # 1. Testar função geral
    print("1. TESTANDO _get_general_metrics_internal...")
    try:
        general_metrics = glpi._get_general_metrics_internal()
        print(f"Resultado geral: {general_metrics}")

        # Verificar se há logs de erro
        print("\nTestando status individual na função geral:")
        for status_name, status_id in glpi.status_map.items():
            print(f"  Status {status_name} (ID {status_id}): testando...")

            # Fazer requisição manual similar à função geral
            search_params = {
                "is_deleted": 0,
                "range": "0-0",
                "criteria[0][field]": glpi.field_ids["STATUS"],
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": int(status_id),
            }

            try:
                response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/search/Ticket", params=search_params)

                if response and response.status_code in [200, 206]:
                    content_range = response.headers.get("Content-Range")
                    if content_range:
                        total = content_range.split("/")[-1]
                        print(f"    Content-Range: {content_range}, Total: {total}")
                    else:
                        print(f"    Sem Content-Range. Status: {response.status_code}")
                        # Tentar extrair do JSON
                        try:
                            data = response.json()
                            print(f'    JSON keys: {list(data.keys()) if isinstance(data, dict) else "not dict"}')
                            if isinstance(data, dict) and "totalcount" in data:
                                print(f'    totalcount: {data["totalcount"]}')
                        except:
                            print("    Erro ao decodificar JSON")
                else:
                    print(f'    Erro: Status {response.status_code if response else "None"}')
                    if response:
                        print(f"    Response text: {response.text[:200]}")
            except Exception as e:
                print(f"    Erro na requisição: {e}")

    except Exception as e:
        print(f"Erro na função geral: {e}")

    print("\n" + "=" * 50)

    # 2. Testar função por hierarquia
    print("2. TESTANDO get_ticket_count_by_hierarchy...")
    try:
        hierarchy_totals = {"novos": 0, "pendentes": 0, "progresso": 0, "resolvidos": 0}

        for level in ["N1", "N2", "N3", "N4"]:
            print(f"\n--- Nível {level} ---")

            # Novo (status 1)
            count = glpi.get_ticket_count_by_hierarchy(level, 1)
            hierarchy_totals["novos"] += count or 0
            print(f"Novos: {count}")

            # Pendente (status 4)
            count = glpi.get_ticket_count_by_hierarchy(level, 4)
            hierarchy_totals["pendentes"] += count or 0
            print(f"Pendentes: {count}")

            # Progresso (status 2 + 3)
            count2 = glpi.get_ticket_count_by_hierarchy(level, 2) or 0
            count3 = glpi.get_ticket_count_by_hierarchy(level, 3) or 0
            hierarchy_totals["progresso"] += count2 + count3
            print(f"Progresso: {count2} + {count3} = {count2 + count3}")

            # Resolvidos (status 5 + 6)
            count5 = glpi.get_ticket_count_by_hierarchy(level, 5) or 0
            count6 = glpi.get_ticket_count_by_hierarchy(level, 6) or 0
            hierarchy_totals["resolvidos"] += count5 + count6
            print(f"Resolvidos: {count5} + {count6} = {count5 + count6}")

        print(f"\nTotais por hierarquia: {hierarchy_totals}")

    except Exception as e:
        print(f"Erro na função hierarquia: {e}")

    print("\n" + "=" * 50)

    # 3. Testar requisição manual sem filtro de hierarquia
    print("3. TESTANDO requisição manual SEM filtro de hierarquia...")
    try:
        for status_name, status_id in list(glpi.status_map.items())[:2]:  # Testar apenas 2 status
            print(f"\nTestando {status_name} (ID {status_id}):")

            search_params = {
                "is_deleted": 0,
                "range": "0-0",
                "criteria[0][field]": glpi.field_ids["STATUS"],
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": int(status_id),
            }

            print(f"  Parâmetros: {search_params}")

            response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/search/Ticket", params=search_params)

            if response:
                print(f"  Status code: {response.status_code}")
                print(f"  Headers: {dict(response.headers)}")

                if response.status_code in [200, 206]:
                    content_range = response.headers.get("Content-Range")
                    if content_range:
                        print(f"  Content-Range: {content_range}")
                        total = content_range.split("/")[-1]
                        print(f"  Total extraído: {total}")

                    try:
                        data = response.json()
                        if isinstance(data, dict):
                            print(f"  JSON keys: {list(data.keys())}")
                            if "totalcount" in data:
                                print(f'  totalcount: {data["totalcount"]}')
                            if "data" in data:
                                print(f'  data length: {len(data["data"]) if isinstance(data["data"], list) else "not list"}')
                    except Exception as json_error:
                        print(f"  Erro JSON: {json_error}")
                        print(f"  Response text: {response.text[:500]}")
                else:
                    print(f"  Erro response: {response.text[:200]}")
            else:
                print("  Response é None")

    except Exception as e:
        print(f"Erro no teste manual: {e}")


if __name__ == "__main__":
    debug_general_vs_hierarchy()
