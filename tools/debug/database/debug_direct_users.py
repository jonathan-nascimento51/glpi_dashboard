#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para buscar técnicos diretamente pela API de usuários
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json

from services.glpi_service import GLPIService


def debug_direct_users():
    """Buscar técnicos diretamente"""
    print("=== BUSCA DIRETA DE TÉCNICOS ===")

    glpi = GLPIService()

    # Autenticar
    if not glpi.authenticate():
        print("❌ Falha na autenticação")
        return
    print("✅ Autenticação bem-sucedida")

    # 1. Buscar todos os usuários ativos
    print("\n1. Buscando usuários ativos...")

    user_params = {
        "criteria[0][field]": "8",  # is_active
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": "1",
        "range": "0-50",
    }

    response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/search/User", params=user_params)

    if response and response.status_code in [200, 206]:
        try:
            data = response.json()
            users = data.get("data", [])
            print(f"   ✅ {len(users)} usuários ativos encontrados")

            # Analisar estrutura dos usuários
            if users:
                print("   Estrutura do primeiro usuário:")
                print(f"     {users[0]}")
                print(f"     Campos: {list(users[0].keys())}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")

    # 2. Usar os IDs de técnicos que sabemos que existem (do debug anterior)
    print("\n2. Testando técnicos conhecidos...")

    known_technicians = {
        "539": "Carla de Jesus Calero",
        "926": "Leonardo Trojan Repiso Riela",
        "1032": "Jonathan Nascimento Moletta",
        "1160": "Leonardo Trojan Repiso Riela",
        "1197": "Jose Guilherme Souza Barros",
        "1291": "Gabriel Silva Machado",
    }

    technician_results = []

    for tech_id, expected_name in known_technicians.items():
        print(f"\n   Técnico {tech_id} ({expected_name}):")

        # Verificar se o usuário existe
        user_response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/User/{tech_id}")

        if user_response and user_response.status_code == 200:
            try:
                user_data = user_response.json()
                firstname = user_data.get("firstname", "")
                realname = user_data.get("realname", "")
                name = user_data.get("name", "N/A")
                is_active = user_data.get("is_active", 0)
                full_name = f"{firstname} {realname}".strip() or name

                print(f"     ✅ Usuário: {full_name} (Ativo: {is_active})")

                if is_active:
                    # Contar tickets como técnico responsável
                    ticket_params = {
                        "criteria[0][field]": "4",  # users_id_tech
                        "criteria[0][searchtype]": "equals",
                        "criteria[0][value]": tech_id,
                        "range": "0-0",  # Apenas contagem
                    }

                    ticket_response = glpi._make_authenticated_request(
                        "GET", f"{glpi.glpi_url}/search/Ticket", params=ticket_params
                    )

                    if ticket_response and ticket_response.status_code in [200, 206]:
                        try:
                            ticket_data = ticket_response.json()
                            total_tickets = ticket_data.get("totalcount", 0)
                            print(f"     📋 Tickets como técnico: {total_tickets}")

                            technician_results.append(
                                {
                                    "id": tech_id,
                                    "name": full_name,
                                    "tickets": total_tickets,
                                }
                            )
                        except Exception as e:
                            print(f"     ❌ Erro ao contar tickets: {e}")
                    else:
                        print(f"     ❌ Falha na busca de tickets")
                else:
                    print(f"     ⚠️  Usuário inativo")
            except Exception as e:
                print(f"     ❌ Erro ao processar usuário: {e}")
        else:
            print(f"     ❌ Usuário não encontrado")

    # 3. Mostrar ranking dos técnicos
    print("\n3. Ranking dos técnicos encontrados:")

    if technician_results:
        # Ordenar por número de tickets (decrescente)
        technician_results.sort(key=lambda x: x["tickets"], reverse=True)

        for i, tech in enumerate(technician_results, 1):
            print(f"   {i}º: {tech['name']} - {tech['tickets']} tickets (ID: {tech['id']})")
    else:
        print("   ❌ Nenhum técnico encontrado")

    # 4. Testar método _count_tickets_with_date_filter com técnico válido
    if technician_results:
        print("\n4. Testando método _count_tickets_with_date_filter...")

        # Usar o técnico com mais tickets
        best_tech = technician_results[0]
        tech_id = best_tech["id"]

        print(f"   Testando com técnico {tech_id} ({best_tech['name']})...")

        # Testar sem filtro de data
        count_no_filter = glpi._count_tickets_with_date_filter(tech_id)
        print(f"   Sem filtro de data: {count_no_filter} tickets")

        # Testar com filtro de data amplo
        from datetime import datetime, timedelta

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")  # 1 ano atrás

        count_with_filter = glpi._count_tickets_with_date_filter(tech_id, start_date, end_date)
        print(f"   Com filtro de data ({start_date} a {end_date}): {count_with_filter} tickets")

    print("\n=== FIM DA BUSCA DIRETA ===")


if __name__ == "__main__":
    debug_direct_users()
