#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from backend.services.glpi_service import GLPIService
import json

def debug_ranking_inclusion():
    """Debug para verificar por que Gabriel Conceição não aparece no ranking"""
    glpi = GLPIService()
    
    print("=== DEBUG INCLUSÃO NO RANKING - GABRIEL CONCEIÇÃO ===")
    
    # Verificar se consegue autenticar
    if not glpi._ensure_authenticated():
        print("❌ Falha na autenticação")
        return
    
    print("✅ Autenticação OK")
    
    # IDs dos Gabriels
    gabriel_conceicao_id = 1404
    gabriel_machado_id = 1291
    
    print(f"\n--- Testando processo completo do ranking ---")
    
    try:
        # Simular o processo do get_technician_ranking
        print("\n1. Buscando todos os tickets para extrair técnicos...")
        
        # Buscar uma amostra de tickets para ver se Gabriel Conceição aparece
        response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/search/Ticket",
            params={
                "range": "0-100",
                "criteria[0][field]": "5",  # Campo users_id_tech
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": str(gabriel_conceicao_id),
                "forcedisplay[0]": "2",  # ID do ticket
                "forcedisplay[1]": "5",  # users_id_tech
                "forcedisplay[2]": "12", # status
            }
        )
        
        if response and response.ok:
            tickets_data = response.json()
            tickets = tickets_data.get('data', [])
            total_count = tickets_data.get('totalcount', 0)
            
            print(f"Gabriel Conceição (ID {gabriel_conceicao_id}):")
            print(f"  Total de tickets encontrados: {total_count}")
            print(f"  Primeiros {len(tickets)} tickets:")
            
            for ticket in tickets[:5]:
                ticket_id = ticket.get('2', 'N/A')
                tech_id = ticket.get('5', 'N/A')
                status = ticket.get('12', 'N/A')
                print(f"    Ticket {ticket_id}: Técnico {tech_id}, Status {status}")
        
        # Fazer o mesmo para Gabriel Machado
        response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/search/Ticket",
            params={
                "range": "0-100",
                "criteria[0][field]": "5",  # Campo users_id_tech
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": str(gabriel_machado_id),
                "forcedisplay[0]": "2",  # ID do ticket
                "forcedisplay[1]": "5",  # users_id_tech
                "forcedisplay[2]": "12", # status
            }
        )
        
        if response and response.ok:
            tickets_data = response.json()
            tickets = tickets_data.get('data', [])
            total_count = tickets_data.get('totalcount', 0)
            
            print(f"\nGabriel Machado (ID {gabriel_machado_id}):")
            print(f"  Total de tickets encontrados: {total_count}")
            print(f"  Primeiros {len(tickets)} tickets:")
            
            for ticket in tickets[:5]:
                ticket_id = ticket.get('2', 'N/A')
                tech_id = ticket.get('5', 'N/A')
                status = ticket.get('12', 'N/A')
                print(f"    Ticket {ticket_id}: Técnico {tech_id}, Status {status}")
        
        print(f"\n2. Verificando se são considerados técnicos DTIC...")
        
        is_dtic_conceicao = glpi._is_dtic_technician(str(gabriel_conceicao_id))
        is_dtic_machado = glpi._is_dtic_technician(str(gabriel_machado_id))
        
        print(f"Gabriel Conceição é DTIC: {is_dtic_conceicao}")
        print(f"Gabriel Machado é DTIC: {is_dtic_machado}")
        
        print(f"\n3. Verificando níveis determinados...")
        
        level_conceicao = glpi._get_technician_level(gabriel_conceicao_id, 48)
        level_machado = glpi._get_technician_level(gabriel_machado_id, 217)
        
        print(f"Gabriel Conceição nível: {level_conceicao}")
        print(f"Gabriel Machado nível: {level_machado}")
        
        print(f"\n4. Testando o ranking completo...")
        
        # Chamar o método de ranking
        ranking_data = glpi.get_technician_ranking(limit=50)
        
        print(f"Total de técnicos no ranking: {len(ranking_data)}")
        
        # Procurar pelos Gabriels
        conceicao_found = False
        machado_found = False
        
        for i, tech in enumerate(ranking_data):
            tech_id = tech.get('id')
            tech_name = tech.get('name', '')
            tech_level = tech.get('level', 'N/A')
            tech_tickets = tech.get('total_tickets', 0)
            
            if tech_id == gabriel_conceicao_id:
                conceicao_found = True
                print(f"\n✅ Gabriel Conceição encontrado no ranking:")
                print(f"   Posição: {i+1}")
                print(f"   Nome: {tech_name}")
                print(f"   Nível: {tech_level}")
                print(f"   Tickets: {tech_tickets}")
            
            elif tech_id == gabriel_machado_id:
                machado_found = True
                print(f"\n✅ Gabriel Machado encontrado no ranking:")
                print(f"   Posição: {i+1}")
                print(f"   Nome: {tech_name}")
                print(f"   Nível: {tech_level}")
                print(f"   Tickets: {tech_tickets}")
        
        if not conceicao_found:
            print(f"\n❌ Gabriel Conceição NÃO encontrado no ranking")
        
        if not machado_found:
            print(f"\n❌ Gabriel Machado NÃO encontrado no ranking")
        
        print(f"\n5. Listando todos os técnicos N1 no ranking...")
        
        n1_techs = [tech for tech in ranking_data if tech.get('level') == 'N1']
        print(f"Técnicos N1 encontrados: {len(n1_techs)}")
        
        for tech in n1_techs:
            print(f"  ID: {tech.get('id')}, Nome: {tech.get('name')}, Tickets: {tech.get('total_tickets')}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_ranking_inclusion()