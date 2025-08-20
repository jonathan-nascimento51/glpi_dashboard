#!/usr/bin/env python3
"""
Script de depuração para investigar problemas no ranking de técnicos com filtros de data
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from datetime import datetime, timedelta

from services.glpi_service import GLPIService


def debug_ranking_with_filters():
    """Testa o ranking de técnicos com filtros de data"""
    print("=== DEPURAÇÃO DO RANKING COM FILTROS ===")

    # Inicializar serviço
    glpi_service = GLPIService()

    # Testar autenticação
    print("\n1. Testando autenticação...")
    if not glpi_service.authenticate():
        print("❌ Falha na autenticação")
        return
    print("✅ Autenticação bem-sucedida")

    # Descobrir IDs de campos
    print("\n2. Descobrindo IDs de campos...")
    if not glpi_service.discover_field_ids():
        print("❌ Falha ao descobrir IDs de campos")
        return
    print(f"✅ IDs descobertos: {glpi_service.field_ids}")

    # Definir período de teste (últimos 30 dias)
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    print(f"\n3. Testando ranking com filtros de data ({start_date} a {end_date})...")

    # Testar ranking sem filtros primeiro
    print("\n3.1. Ranking SEM filtros de data:")
    ranking_without_filters = glpi_service.get_technician_ranking_with_filters(limit=5)
    print(f"Resultado: {len(ranking_without_filters)} técnicos")
    for i, tech in enumerate(ranking_without_filters[:3]):
        print(f"  {i+1}. {tech.get('name', 'N/A')} - {tech.get('total', 0)} tickets (ID: {tech.get('id', 'N/A')})")

    # Testar ranking com filtros
    print("\n3.2. Ranking COM filtros de data:")
    ranking_with_filters = glpi_service.get_technician_ranking_with_filters(limit=5, start_date=start_date, end_date=end_date)
    print(f"Resultado: {len(ranking_with_filters)} técnicos")
    for i, tech in enumerate(ranking_with_filters[:3]):
        print(f"  {i+1}. {tech.get('name', 'N/A')} - {tech.get('total', 0)} tickets (ID: {tech.get('id', 'N/A')})")

    # Testar método de contagem individual
    print("\n4. Testando contagem individual de tickets...")
    if ranking_without_filters:
        first_tech_id = ranking_without_filters[0].get("id")
        if first_tech_id:
            print(f"\n4.1. Testando técnico ID {first_tech_id}:")

            # Testar nome do técnico
            tech_name = glpi_service._get_technician_name(first_tech_id)
            print(f"  Nome: {tech_name}")

            # Testar contagem sem filtros
            tech_field = glpi_service.field_ids.get("TECH", "5")
            count_without_filter = glpi_service._count_tickets_by_technician_optimized(int(first_tech_id), tech_field)
            print(f"  Tickets sem filtro: {count_without_filter}")

            # Testar contagem com filtros
            count_with_filter = glpi_service._count_tickets_with_date_filter(first_tech_id, start_date, end_date)
            print(f"  Tickets com filtro ({start_date} a {end_date}): {count_with_filter}")

    # Testar busca de técnicos
    print("\n5. Testando busca de técnicos...")
    try:
        # Simular parte da lógica de busca de técnicos
        profile_users_response = glpi_service._make_authenticated_request(
            "GET",
            f"{glpi_service.glpi_url}/search/Profile_User",
            params={
                "criteria[0][field]": "4",  # profiles_id
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": "6",  # ID do perfil de técnico
                "range": "0-10",  # Limitar para teste
            },
        )

        if profile_users_response and profile_users_response.ok:
            profile_data = profile_users_response.json()
            print(f"  Encontrados {len(profile_data.get('data', []))} Profile_Users")

            # Mostrar alguns exemplos
            for i, profile_user in enumerate(profile_data.get("data", [])[:3]):
                user_id = profile_user.get("2")  # users_id
                print(f"    {i+1}. Profile_User ID: {profile_user.get('id')}, User ID: {user_id}")

                if user_id:
                    # Testar busca do usuário
                    user_response = glpi_service._make_authenticated_request("GET", f"{glpi_service.glpi_url}/User/{user_id}")

                    if user_response and user_response.ok:
                        user_data = user_response.json()
                        user_name = user_data.get("completename") or user_data.get("realname") or user_data.get("name", "N/A")
                        print(f"      Nome: {user_name}")
                    else:
                        print(f"      ❌ Erro ao buscar usuário {user_id}")
        else:
            print("  ❌ Erro ao buscar Profile_Users")

    except Exception as e:
        print(f"  ❌ Erro na busca de técnicos: {e}")

    print("\n=== FIM DA DEPURAÇÃO ===")


if __name__ == "__main__":
    debug_ranking_with_filters()
