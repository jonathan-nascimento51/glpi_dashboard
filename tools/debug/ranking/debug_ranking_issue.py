#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para depurar o problema específico do ranking
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json

from services.glpi_service import GLPIService


def debug_ranking_issue():
    """Depurar problema específico do ranking"""
    print("=== DEPURAÇÃO DO PROBLEMA DO RANKING ===")

    glpi = GLPIService()

    # Autenticar
    if not glpi.authenticate():
        print("❌ Falha na autenticação")
        return
    print("✅ Autenticação bem-sucedida")

    # 1. Testar método _count_tickets_with_date_filter diretamente
    print("\n1. Testando _count_tickets_with_date_filter diretamente...")

    tech_id = "539"  # Carla de Jesus Calero

    # Sem filtros de data
    count_direct = glpi._count_tickets_with_date_filter(tech_id)
    print(f"   Contagem direta (sem filtros): {count_direct}")

    # Com filtros de data
    count_with_filters = glpi._count_tickets_with_date_filter(tech_id, "2024-01-01", "2025-12-31")
    print(f"   Contagem direta (com filtros): {count_with_filters}")

    # 2. Testar método get_technician_ranking_with_filters
    print("\n2. Testando get_technician_ranking_with_filters...")

    # Sem filtros de data
    ranking_no_filters = glpi.get_technician_ranking_with_filters(limit=5)
    print(f"   Ranking sem filtros: {len(ranking_no_filters)} técnicos")
    if ranking_no_filters:
        for i, tech in enumerate(ranking_no_filters[:3], 1):
            print(f"     {i}º: {tech.get('name', 'N/A')} - {tech.get('total', 0)} tickets (ID: {tech.get('id', 'N/A')})")

    # Com filtros de data
    ranking_with_filters = glpi.get_technician_ranking_with_filters(limit=5, start_date="2024-01-01", end_date="2025-12-31")
    print(f"   Ranking com filtros: {len(ranking_with_filters)} técnicos")
    if ranking_with_filters:
        for i, tech in enumerate(ranking_with_filters[:3], 1):
            print(f"     {i}º: {tech.get('name', 'N/A')} - {tech.get('total', 0)} tickets (ID: {tech.get('id', 'N/A')})")

    # 3. Testar método _get_technicians
    print("\n3. Testando _get_technicians...")

    # Simular o método get_technician_ranking_with_filters manualmente
    correlation_id = "debug_test"

    # Obter lista de técnicos
    known_technicians = {
        "539": "Carla de Jesus Calero",
        "926": "Leonardo Trojan Repiso Riela",
        "1032": "Jonathan Nascimento Moletta",
        "1160": "Leonardo Trojan Repiso Riela",
        "1291": "Gabriel Silva Machado",
    }

    technician_ids = []

    # Verificar cada técnico conhecido
    for tech_id, expected_name in known_technicians.items():
        try:
            # Verificar se o usuário está ativo
            user_response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/User/{tech_id}")

            if user_response and user_response.status_code == 200:
                user_data = user_response.json()
                is_active = user_data.get("is_active", 0)

                if is_active:
                    technician_ids.append(tech_id)
                    print(f"   ✅ Técnico ativo: {tech_id} ({expected_name})")
                else:
                    print(f"   ⚠️  Técnico inativo: {tech_id} ({expected_name})")
            else:
                print(f"   ❌ Técnico não encontrado: {tech_id}")

        except Exception as e:
            print(f"   ❌ Erro ao verificar técnico {tech_id}: {e}")
            continue

    print(f"   Total de técnicos ativos: {len(technician_ids)}")

    # 4. Simular o loop do ranking manualmente
    print("\n4. Simulando loop do ranking manualmente...")

    ranking = []

    for tech_id in technician_ids:
        try:
            print(f"\n   Processando técnico {tech_id}...")

            # Obter nome do técnico
            tech_name = glpi._get_technician_name(tech_id)
            print(f"     Nome: {tech_name}")

            # Contar tickets sem filtros
            ticket_count_no_filter = glpi._count_tickets_with_date_filter(tech_id)
            print(f"     Tickets (sem filtros): {ticket_count_no_filter}")

            # Contar tickets com filtros
            ticket_count_with_filter = glpi._count_tickets_with_date_filter(tech_id, "2024-01-01", "2025-12-31")
            print(f"     Tickets (com filtros): {ticket_count_with_filter}")

            ranking.append(
                {
                    "id": tech_id,
                    "name": tech_name,
                    "total_no_filter": ticket_count_no_filter,
                    "total_with_filter": ticket_count_with_filter,
                }
            )

        except Exception as e:
            print(f"     ❌ Erro ao processar técnico {tech_id}: {e}")
            import traceback

            print(f"     Traceback: {traceback.format_exc()}")
            continue

    # 5. Mostrar resultados finais
    print("\n5. Resultados finais:")

    if ranking:
        print("   Ranking sem filtros:")
        ranking_no_filter = sorted(ranking, key=lambda x: x["total_no_filter"], reverse=True)
        for i, tech in enumerate(ranking_no_filter, 1):
            print(f"     {i}º: {tech['name']} - {tech['total_no_filter']} tickets (ID: {tech['id']})")

        print("\n   Ranking com filtros:")
        ranking_with_filter = sorted(ranking, key=lambda x: x["total_with_filter"], reverse=True)
        for i, tech in enumerate(ranking_with_filter, 1):
            print(f"     {i}º: {tech['name']} - {tech['total_with_filter']} tickets (ID: {tech['id']})")
    else:
        print("   ❌ Nenhum resultado obtido")

    print("\n=== FIM DA DEPURAÇÃO DO RANKING ===")


if __name__ == "__main__":
    debug_ranking_issue()
