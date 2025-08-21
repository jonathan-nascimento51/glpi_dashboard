#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests

from config.settings import Config
from services.glpi_service import GLPIService


def test_tech_fields():
    """Testa diferentes campos de técnico para ver qual retorna mais resultados"""

    # Inicializar serviço
    glpi = GLPIService()

    # Autenticar
    if not glpi.authenticate():
        print("Falha na autenticação")
        return

    print("=== TESTE DE CAMPOS DE TÉCNICO ===")

    # Campos candidatos baseados na investigação anterior
    tech_field_candidates = [2, 4, 5, 12, 95]

    # Técnicos para testar (baseados nos tickets aleatórios)
    test_technicians = [5, 32, 41, 202, 442, 539]

    results = {}

    for field_id in tech_field_candidates:
        print(f"\n--- Testando Campo {field_id} ---")
        field_results = {}

        for tech_id in test_technicians:
            try:
                # Fazer busca usando o campo específico
                search_params = {
                    "criteria": [{"field": str(field_id), "searchtype": "equals", "value": str(tech_id)}],
                    "range": "0-0",  # Só queremos o count
                }

                headers = glpi.get_api_headers()
                if not headers:
                    field_results[tech_id] = 0
                    print(f"  Técnico {tech_id}: Erro - Headers não disponíveis")
                    continue

                response = requests.get(
                    f"{glpi.glpi_url}/search/Ticket",
                    headers=headers,
                    params={"criteria": str(search_params["criteria"]).replace("'", '"')},
                )

                if response.status_code == 200:
                    content_range = response.headers.get("Content-Range", "")
                    if content_range:
                        total_count = int(content_range.split("/")[-1])
                        field_results[tech_id] = total_count
                        print(f"  Técnico {tech_id}: {total_count} tickets")
                    else:
                        field_results[tech_id] = 0
                        print(f"  Técnico {tech_id}: 0 tickets (sem Content-Range)")
                else:
                    field_results[tech_id] = 0
                    print(f"  Técnico {tech_id}: Erro {response.status_code}")

            except Exception as e:
                field_results[tech_id] = 0
                print(f"  Técnico {tech_id}: Erro - {e}")

        # Calcular total para este campo
        total_tickets = sum(field_results.values())
        results[field_id] = {"details": field_results, "total": total_tickets}
        print(f"  TOTAL para campo {field_id}: {total_tickets} tickets")

    print("\n=== RESUMO DOS RESULTADOS ===")
    for field_id, data in results.items():
        print(f"Campo {field_id}: {data['total']} tickets totais")

    # Encontrar o melhor campo
    best_field = max(results.keys(), key=lambda x: results[x]["total"])
    print(f"\nMELHOR CAMPO: {best_field} com {results[best_field]['total']} tickets")

    # Verificar qual campo a função atual está usando
    current_field = glpi._discover_tech_field_id()
    print(f"CAMPO ATUAL DESCOBERTO: {current_field}")

    if str(best_field) != str(current_field):
        print(f"[PROBLEMA] Campo atual ({current_field}) não é o melhor ({best_field})")
    else:
        print(f"[OK] Campo atual está correto")

    # Testar também o campo descoberto automaticamente
    if current_field and current_field not in [str(f) for f in tech_field_candidates]:
        print(f"\n--- Testando Campo Descoberto {current_field} ---")
        field_results = {}

        for tech_id in test_technicians:
            try:
                search_params = {
                    "criteria": [{"field": str(current_field), "searchtype": "equals", "value": str(tech_id)}],
                    "range": "0-0",
                }

                headers = glpi.get_api_headers()
                if not headers:
                    field_results[tech_id] = 0
                    print(f"  Técnico {tech_id}: Erro - Headers não disponíveis")
                    continue

                response = requests.get(
                    f"{glpi.glpi_url}/search/Ticket",
                    headers=headers,
                    params={"criteria": str(search_params["criteria"]).replace("'", '"')},
                )

                if response.status_code == 200:
                    content_range = response.headers.get("Content-Range", "")
                    if content_range:
                        total_count = int(content_range.split("/")[-1])
                        field_results[tech_id] = total_count
                        print(f"  Técnico {tech_id}: {total_count} tickets")
                    else:
                        field_results[tech_id] = 0
                        print(f"  Técnico {tech_id}: 0 tickets (sem Content-Range)")
                else:
                    field_results[tech_id] = 0
                    print(f"  Técnico {tech_id}: Erro {response.status_code}")

            except Exception as e:
                field_results[tech_id] = 0
                print(f"  Técnico {tech_id}: Erro - {e}")

        total_discovered = sum(field_results.values())
        print(f"  TOTAL para campo descoberto {current_field}: {total_discovered} tickets")


if __name__ == "__main__":
    test_tech_fields()
