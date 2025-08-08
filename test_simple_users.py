#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from backend.services.glpi_service import GLPIService
import json

def test_simple_users():
    """Busca usuários de forma mais simples"""
    glpi = GLPIService()
    
    print("=== BUSCANDO USUÁRIOS DE FORMA SIMPLES ===\n")
    
    # Verificar se consegue autenticar
    if not glpi._ensure_authenticated():
        print("❌ Falha na autenticação")
        return
    
    print("✅ Autenticação OK\n")
    
    # Buscar usuários diretamente
    try:
        response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/User",
            params={
                "range": "0-50"
            }
        )
        
        if response and response.ok:
            users_data = response.json()
            print(f"Resposta da API: {json.dumps(users_data, indent=2, ensure_ascii=False)[:1000]}...")
            
        else:
            print(f"❌ Erro ao buscar usuários: {response.status_code if response else 'No response'}")
            if response:
                print(f"Resposta: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
    
    # Tentar buscar com search
    print("\n=== TENTANDO COM SEARCH ===\n")
    
    try:
        response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/search/User",
            params={
                "range": "0-20",
                "forcedisplay[0]": "2",  # ID
                "forcedisplay[1]": "1",  # Nome
            }
        )
        
        if response and response.ok:
            users_data = response.json()
            print(f"Total count: {users_data.get('totalcount', 'N/A')}")
            print(f"Count: {users_data.get('count', 'N/A')}")
            
            users = users_data.get('data', [])
            print(f"\nUsuários encontrados: {len(users)}")
            
            for i, user in enumerate(users[:10], 1):
                print(f"{i}. {user}")
            
        else:
            print(f"❌ Erro ao buscar usuários com search: {response.status_code if response else 'No response'}")
            if response:
                print(f"Resposta: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Erro com search: {e}")
    
    # Tentar buscar tickets para ver técnicos
    print("\n=== BUSCANDO TICKETS PARA ENCONTRAR TÉCNICOS ===\n")
    
    try:
        response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/search/Ticket",
            params={
                "range": "0-20",
                "forcedisplay[0]": "2",  # ID
                "forcedisplay[1]": "1",  # Nome
                "forcedisplay[2]": "5",  # users_id_tech
            }
        )
        
        if response and response.ok:
            tickets_data = response.json()
            print(f"Total tickets: {tickets_data.get('totalcount', 'N/A')}")
            
            tickets = tickets_data.get('data', [])
            print(f"\nTickets encontrados: {len(tickets)}")
            
            technicians = set()
            for ticket in tickets[:10]:
                print(f"Ticket: {ticket}")
                if isinstance(ticket, dict) and "5" in ticket:
                    tech_id = ticket["5"]
                    if tech_id and tech_id != "0":
                        technicians.add(tech_id)
            
            print(f"\nTécnicos únicos encontrados: {technicians}")
            
        else:
            print(f"❌ Erro ao buscar tickets: {response.status_code if response else 'No response'}")
            if response:
                print(f"Resposta: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Erro ao buscar tickets: {e}")

if __name__ == "__main__":
    test_simple_users()