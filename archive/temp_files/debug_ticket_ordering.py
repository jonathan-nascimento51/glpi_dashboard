#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from backend.services.glpi_service import GLPIService
import json

def debug_ticket_ordering():
    """Debug da ordenação e filtros de tickets"""
    glpi = GLPIService()
    
    print("=== DEBUG ORDENAÇÃO DE TICKETS ===")
    
    # Verificar se consegue autenticar
    if not glpi._ensure_authenticated():
        print("❌ Falha na autenticação")
        return
    
    print("✅ Autenticação OK")
    
    # Descobrir field ID do técnico
    tech_field_id = glpi._discover_tech_field_id()
    if not tech_field_id:
        print("❌ Não foi possível descobrir field ID do técnico")
        return
    
    print(f"✅ Field ID do técnico: {tech_field_id}")
    
    gabriel_conceicao_id = "1404"
    gabriel_machado_id = "1291"
    
    print(f"\n--- Teste 1: Consulta com ordenação por ID (crescente) ---")
    
    # Consulta com ordenação por ID crescente
    search_params_asc = {
        "range": "0-9999",
        "forcedisplay[0]": "2",   # ID do ticket
        "forcedisplay[1]": "12",  # Status
        "forcedisplay[2]": str(tech_field_id),  # Técnico atribuído
        "forcedisplay[3]": "15",  # Data de criação
        "sort": "2",  # Ordenar por ID
        "order": "ASC"  # Ordem crescente
    }
    
    try:
        response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/search/Ticket",
            params=search_params_asc
        )
        
        if response and response.ok:
            result = response.json()
            tickets = result.get('data', [])
            print(f"Consulta ASC: {len(tickets)} tickets")
            
            # Verificar primeiros e últimos tickets
            if tickets:
                first_ticket = tickets[0]
                last_ticket = tickets[-1]
                print(f"Primeiro ticket: ID {first_ticket.get('2', 'N/A')}, Data {first_ticket.get('15', 'N/A')}")
                print(f"Último ticket: ID {last_ticket.get('2', 'N/A')}, Data {last_ticket.get('15', 'N/A')}")
            
            # Contar Gabriels
            conceicao_count = 0
            machado_count = 0
            
            for ticket in tickets:
                tech_id = str(ticket.get(str(tech_field_id), ''))
                if tech_id == gabriel_conceicao_id:
                    conceicao_count += 1
                elif tech_id == gabriel_machado_id:
                    machado_count += 1
            
            print(f"Gabriel Conceição: {conceicao_count} tickets")
            print(f"Gabriel Machado: {machado_count} tickets")
        
        else:
            print(f"❌ Falha na consulta ASC: {response.status_code if response else 'No response'}")
    
    except Exception as e:
        print(f"❌ Erro na consulta ASC: {e}")
    
    print(f"\n--- Teste 2: Consulta com ordenação por ID (decrescente) ---")
    
    # Consulta com ordenação por ID decrescente
    search_params_desc = {
        "range": "0-9999",
        "forcedisplay[0]": "2",   # ID do ticket
        "forcedisplay[1]": "12",  # Status
        "forcedisplay[2]": str(tech_field_id),  # Técnico atribuído
        "forcedisplay[3]": "15",  # Data de criação
        "sort": "2",  # Ordenar por ID
        "order": "DESC"  # Ordem decrescente
    }
    
    try:
        response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/search/Ticket",
            params=search_params_desc
        )
        
        if response and response.ok:
            result = response.json()
            tickets = result.get('data', [])
            print(f"Consulta DESC: {len(tickets)} tickets")
            
            # Verificar primeiros e últimos tickets
            if tickets:
                first_ticket = tickets[0]
                last_ticket = tickets[-1]
                print(f"Primeiro ticket: ID {first_ticket.get('2', 'N/A')}, Data {first_ticket.get('15', 'N/A')}")
                print(f"Último ticket: ID {last_ticket.get('2', 'N/A')}, Data {last_ticket.get('15', 'N/A')}")
            
            # Contar Gabriels
            conceicao_count = 0
            machado_count = 0
            
            for ticket in tickets:
                tech_id = str(ticket.get(str(tech_field_id), ''))
                if tech_id == gabriel_conceicao_id:
                    conceicao_count += 1
                elif tech_id == gabriel_machado_id:
                    machado_count += 1
            
            print(f"Gabriel Conceição: {conceicao_count} tickets")
            print(f"Gabriel Machado: {machado_count} tickets")
        
        else:
            print(f"❌ Falha na consulta DESC: {response.status_code if response else 'No response'}")
    
    except Exception as e:
        print(f"❌ Erro na consulta DESC: {e}")
    
    print(f"\n--- Teste 3: Consulta sem ordenação específica ---")
    
    # Consulta sem ordenação específica (padrão do GLPI)
    search_params_default = {
        "range": "0-9999",
        "forcedisplay[0]": "2",   # ID do ticket
        "forcedisplay[1]": "12",  # Status
        "forcedisplay[2]": str(tech_field_id),  # Técnico atribuído
        "forcedisplay[3]": "15",  # Data de criação
    }
    
    try:
        response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/search/Ticket",
            params=search_params_default
        )
        
        if response and response.ok:
            result = response.json()
            tickets = result.get('data', [])
            print(f"Consulta padrão: {len(tickets)} tickets")
            
            # Verificar primeiros e últimos tickets
            if tickets:
                first_ticket = tickets[0]
                last_ticket = tickets[-1]
                print(f"Primeiro ticket: ID {first_ticket.get('2', 'N/A')}, Data {first_ticket.get('15', 'N/A')}")
                print(f"Último ticket: ID {last_ticket.get('2', 'N/A')}, Data {last_ticket.get('15', 'N/A')}")
            
            # Contar Gabriels
            conceicao_count = 0
            machado_count = 0
            
            for ticket in tickets:
                tech_id = str(ticket.get(str(tech_field_id), ''))
                if tech_id == gabriel_conceicao_id:
                    conceicao_count += 1
                elif tech_id == gabriel_machado_id:
                    machado_count += 1
            
            print(f"Gabriel Conceição: {conceicao_count} tickets")
            print(f"Gabriel Machado: {machado_count} tickets")
        
        else:
            print(f"❌ Falha na consulta padrão: {response.status_code if response else 'No response'}")
    
    except Exception as e:
        print(f"❌ Erro na consulta padrão: {e}")
    
    print(f"\n--- Teste 4: Verificar total real de tickets ---")
    
    # Consulta para verificar o total real de tickets
    search_params_count = {
        "range": "0-0",  # Só queremos a contagem
    }
    
    try:
        response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/search/Ticket",
            params=search_params_count
        )
        
        if response and response.ok:
            result = response.json()
            total_count = result.get('totalcount', 0)
            print(f"Total real de tickets no sistema: {total_count}")
            
            # Verificar Content-Range
            if 'Content-Range' in response.headers:
                content_range = response.headers['Content-Range']
                print(f"Content-Range: {content_range}")
        
        else:
            print(f"❌ Falha na consulta de contagem: {response.status_code if response else 'No response'}")
    
    except Exception as e:
        print(f"❌ Erro na consulta de contagem: {e}")
    
    print(f"\n--- Teste 5: Buscar tickets específicos dos Gabriels por ID ---")
    
    # Buscar alguns tickets específicos dos Gabriels
    conceicao_tickets = ["9034", "8793", "8400", "8698", "8366"]  # IDs dos primeiros tickets do Gabriel Conceição
    
    for ticket_id in conceicao_tickets:
        try:
            response = glpi._make_authenticated_request(
                'GET',
                f"{glpi.glpi_url}/Ticket/{ticket_id}"
            )
            
            if response and response.ok:
                ticket_data = response.json()
                tech_id = ticket_data.get('users_id_tech', 'N/A')
                date_creation = ticket_data.get('date_creation', 'N/A')
                status = ticket_data.get('status', 'N/A')
                print(f"Ticket {ticket_id}: Técnico {tech_id}, Data {date_creation}, Status {status}")
            else:
                print(f"❌ Falha ao buscar ticket {ticket_id}")
        
        except Exception as e:
            print(f"❌ Erro ao buscar ticket {ticket_id}: {e}")

if __name__ == "__main__":
    debug_ticket_ordering()