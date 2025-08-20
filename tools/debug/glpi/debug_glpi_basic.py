#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para depuração básica da API GLPI
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datetime import datetime, timedelta

from services.glpi_service import GLPIService


def debug_glpi_basic():
    """Depuração básica da API GLPI"""
    print("=== DEPURAÇÃO BÁSICA DA API GLPI ===")

    glpi = GLPIService()

    # Autenticar
    if not glpi.authenticate():
        print("❌ Falha na autenticação")
        return
    print("✅ Autenticação bem-sucedida")

    # 1. Testar endpoint básico de tickets sem parâmetros
    print("\n1. Testando endpoint básico de tickets...")
    response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/search/Ticket")

    if response:
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")

        if response.status_code in [200, 206]:  # 206 = Partial Content
            try:
                data = response.json()
                print(f"   Total count: {data.get('totalcount', 'N/A')}")
                print(f"   Count: {data.get('count', 'N/A')}")
                print(f"   Keys: {list(data.keys())}")

                if "data" in data and len(data["data"]) > 0:
                    print(f"   Primeiro ticket: {data['data'][0]}")
                    print(f"   Campos disponíveis no ticket: {list(data['data'][0].keys())}")
            except Exception as e:
                print(f"   Erro ao processar JSON: {e}")
                print(f"   Conteúdo: {response.text[:500]}")
    else:
        print("   ❌ Nenhuma resposta")

    # 2. Testar com range específico
    print("\n2. Testando com range específico...")
    response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/search/Ticket", params={"range": "0-10"})

    if response and response.status_code in [200, 206]:
        try:
            data = response.json()
            print(f"   ✅ Total count: {data.get('totalcount', 'N/A')}")
            print(f"   Count: {data.get('count', 'N/A')}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")

    # 3. Testar busca de usuários
    print("\n3. Testando busca de usuários...")
    response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/search/User", params={"range": "0-10"})

    if response and response.status_code in [200, 206]:
        try:
            data = response.json()
            print(f"   ✅ Total usuários: {data.get('totalcount', 'N/A')}")
            print(f"   Count: {data.get('count', 'N/A')}")

            if "data" in data and len(data["data"]) > 0:
                for i, user in enumerate(data["data"][:3]):
                    user_id = user.get("2", "N/A")
                    user_name = user.get("1", "N/A")
                    print(f"   Usuário {i+1}: ID {user_id}, Nome: {user_name}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")

    # 4. Testar busca específica por usuário conhecido
    print("\n4. Testando busca por usuário específico (ID 5)...")
    response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/User/5")

    if response and response.status_code == 200:
        try:
            user_data = response.json()
            print(f"   ✅ Usuário encontrado: {user_data.get('name', 'N/A')}")
            print(f"   ID: {user_data.get('id', 'N/A')}")
            print(f"   Ativo: {user_data.get('is_active', 'N/A')}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    else:
        print(f"   ❌ Usuário não encontrado: {response.status_code if response else 'No response'}")

    # 5. Testar busca de tickets por usuário específico usando diferentes métodos
    print("\n5. Testando diferentes métodos de busca de tickets...")

    # Método 1: Busca direta por ID
    print("   Método 1: Busca direta por tickets do usuário 5...")
    response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/User/5/Ticket")

    if response and response.status_code == 200:
        try:
            tickets = response.json()
            print(f"     ✅ Tickets encontrados: {len(tickets) if isinstance(tickets, list) else 'N/A'}")
            if isinstance(tickets, list) and len(tickets) > 0:
                print(f"     Primeiro ticket: {tickets[0]}")
        except Exception as e:
            print(f"     ❌ Erro: {e}")
    else:
        print(f"     ❌ Falha: {response.status_code if response else 'No response'}")

    # Método 2: Busca com critério mais simples
    print("   Método 2: Busca com critério simples...")
    simple_params = {
        "criteria[0][field]": "4",  # users_id_tech
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": "5",
    }

    response = glpi._make_authenticated_request("GET", f"{glpi.glpi_url}/search/Ticket", params=simple_params)

    if response and response.status_code in [200, 206]:
        try:
            data = response.json()
            print(f"     ✅ Total: {data.get('totalcount', 'N/A')}")
        except Exception as e:
            print(f"     ❌ Erro: {e}")

    # 6. Verificar se há tickets no sistema
    print("\n6. Verificando total de tickets no sistema...")
    response = glpi._make_authenticated_request(
        "GET",
        f"{glpi.glpi_url}/search/Ticket",
        params={"range": "0-0"},  # Apenas contagem
    )

    if response and response.status_code in [200, 206]:
        try:
            data = response.json()
            total_tickets = data.get("totalcount", 0)
            print(f"   ✅ Total de tickets no sistema: {total_tickets}")

            if total_tickets == 0:
                print("   ⚠️  ATENÇÃO: Não há tickets no sistema GLPI!")
            else:
                print(f"   ✅ Sistema tem {total_tickets} tickets")
        except Exception as e:
            print(f"   ❌ Erro: {e}")

    print("\n=== FIM DA DEPURAÇÃO BÁSICA ===")


if __name__ == "__main__":
    debug_glpi_basic()
