#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para depurar campos de tickets e identificar o problema na contagem
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datetime import datetime, timedelta

from services.glpi_service import GLPIService


def test_ticket_fields():
    """Teste de diferentes campos de tickets"""
    print("=== TESTE DE CAMPOS DE TICKETS ===")

    glpi = GLPIService()

    # Autenticar
    if not glpi.authenticate():
        print("❌ Falha na autenticação")
        return
    print("✅ Autenticação bem-sucedida")

    # Descobrir field_ids
    glpi.discover_field_ids()
    print(f"Field IDs descobertos: {glpi.field_ids}")

    # Testar busca básica de tickets sem filtros
    print("\n1. Testando busca básica de tickets...")
    basic_params = {"is_deleted": 0, "range": "0-10"}

    response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/search/Ticket", params=basic_params)

    if response and response.status_code == 200:
        data = response.json()
        print(f"✅ Busca básica bem-sucedida")
        print(f"   - Total count: {data.get('totalcount', 'N/A')}")
        print(f"   - Count: {data.get('count', 'N/A')}")
        print(f"   - Content-Range header: {response.headers.get('Content-Range', 'N/A')}")

        # Mostrar alguns tickets para análise
        if "data" in data and len(data["data"]) > 0:
            print(f"   - Primeiro ticket: {data['data'][0]}")
    else:
        print(f"❌ Falha na busca básica: {response.status_code if response else 'No response'}")

    # Testar diferentes campos de técnico
    print("\n2. Testando diferentes campos de técnico...")
    tech_fields = {
        "ASSIGN": glpi.field_ids.get("ASSIGN", "5"),
        "TECH": glpi.field_ids.get("TECH", "8"),
        "Campo 4": "4",  # users_id_tech
        "Campo 5": "5",  # users_id_recipient
        "Campo 8": "8",  # users_id_lastupdater
    }

    # Usar um ID de técnico que sabemos que existe
    tech_id = "5"  # Anderson da Silva Morim de Oliveira

    for field_name, field_id in tech_fields.items():
        print(f"\n   Testando campo {field_name} (ID: {field_id})...")

        search_params = {
            "is_deleted": 0,
            "range": "0-5",
            "criteria[0][field]": field_id,
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": tech_id,
        }

        response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/search/Ticket", params=search_params)

        if response and response.status_code == 200:
            data = response.json()
            total = data.get("totalcount", 0)
            count = data.get("count", 0)
            print(f"     ✅ Campo {field_name}: {total} tickets totais, {count} retornados")

            # Se encontrou tickets, mostrar detalhes
            if total > 0 and "data" in data and len(data["data"]) > 0:
                ticket = data["data"][0]
                print(f"     📋 Exemplo de ticket: ID {ticket.get('2', 'N/A')}, Status {ticket.get('12', 'N/A')}")
        else:
            print(f"     ❌ Falha no campo {field_name}: {response.status_code if response else 'No response'}")

    # Testar busca com filtro de data
    print("\n3. Testando busca com filtro de data...")

    # Usar período de uma semana atrás até hoje
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    # Usar o campo que funcionou melhor
    best_field = "5"  # Campo ASSIGN

    date_params = {
        "is_deleted": 0,
        "range": "0-5",
        "criteria[0][field]": best_field,
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": tech_id,
        "criteria[1][link]": "AND",
        "criteria[1][field]": "15",  # Data de criação
        "criteria[1][searchtype]": "morethan",
        "criteria[1][value]": f"{start_date} 00:00:00",
        "criteria[2][link]": "AND",
        "criteria[2][field]": "15",  # Data de criação
        "criteria[2][searchtype]": "lessthan",
        "criteria[2][value]": f"{end_date} 23:59:59",
    }

    response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/search/Ticket", params=date_params)

    if response and response.status_code == 200:
        data = response.json()
        total = data.get("totalcount", 0)
        count = data.get("count", 0)
        print(f"✅ Busca com filtro de data: {total} tickets totais, {count} retornados")
        print(f"   - Período: {start_date} até {end_date}")
        print(f"   - Técnico ID: {tech_id}")

        if total > 0 and "data" in data and len(data["data"]) > 0:
            for i, ticket in enumerate(data["data"][:3]):
                print(f"   - Ticket {i+1}: ID {ticket.get('2', 'N/A')}, Data {ticket.get('15', 'N/A')}")
    else:
        print(f"❌ Falha na busca com filtro de data: {response.status_code if response else 'No response'}")

    print("\n=== FIM DO TESTE DE CAMPOS ===")


if __name__ == "__main__":
    test_ticket_fields()
