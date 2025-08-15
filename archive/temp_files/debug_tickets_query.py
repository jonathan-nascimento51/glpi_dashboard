#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from backend.services.glpi_service import GLPIService
import json

def debug_tickets_query():
    """Debug da consulta de tickets do método get_technician_ranking"""
    glpi = GLPIService()
    
    print("=== DEBUG CONSULTA DE TICKETS ===")
    
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
    
    # Simular a mesma consulta do método get_technician_ranking
    search_params = {
        "range": "0-9999",  # Buscar todos os tickets
        "forcedisplay[0]": "2",   # ID do ticket
        "forcedisplay[1]": "12",  # Status
        "forcedisplay[2]": str(tech_field_id),  # Técnico atribuído
    }
    
    print(f"\n--- Fazendo consulta de tickets ---")
    print(f"Parâmetros: {search_params}")
    
    try:
        response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/search/Ticket",
            params=search_params
        )
        
        if not response or not response.ok:
            print(f"❌ Falha na consulta de tickets: {response.status_code if response else 'No response'}")
            return
        
        result = response.json()
        if not isinstance(result, dict) or 'data' not in result:
            print("ℹ️ Nenhum ticket encontrado")
            return
        
        tickets = result['data']
        print(f"📊 {len(tickets)} tickets encontrados")
        
        # Procurar tickets dos Gabriels
        gabriel_conceicao_id = "1404"
        gabriel_machado_id = "1291"
        
        conceicao_tickets = []
        machado_tickets = []
        
        print(f"\n--- Analisando tickets ---")
        
        for i, ticket in enumerate(tickets):
            if not isinstance(ticket, dict):
                continue
            
            tech_id = ticket.get(str(tech_field_id))
            if not tech_id or tech_id == '0':
                continue
            
            # Processar tech_id da mesma forma que o método original
            if isinstance(tech_id, list):
                if len(tech_id) == 0:
                    continue
                tech_id = str(tech_id[0])
            elif isinstance(tech_id, str):
                if tech_id.startswith('[') and tech_id.endswith(']'):
                    import re
                    numbers = re.findall(r"'(\d+)'", tech_id)
                    if not numbers:
                        numbers = re.findall(r'"(\d+)"', tech_id)
                    if not numbers:
                        numbers = re.findall(r'(\d+)', tech_id)
                    
                    if numbers:
                        tech_id = str(numbers[0])
                    else:
                        continue
                else:
                    tech_id = str(tech_id)
            else:
                tech_id = str(tech_id)
            
            # Verificar se é um dos Gabriels
            if tech_id == gabriel_conceicao_id:
                ticket_info = {
                    'id': ticket.get('2', 'N/A'),
                    'status': ticket.get('12', 'N/A'),
                    'tech_id': tech_id
                }
                conceicao_tickets.append(ticket_info)
            elif tech_id == gabriel_machado_id:
                ticket_info = {
                    'id': ticket.get('2', 'N/A'),
                    'status': ticket.get('12', 'N/A'),
                    'tech_id': tech_id
                }
                machado_tickets.append(ticket_info)
        
        print(f"\n--- Resultados ---")
        print(f"Gabriel Conceição (ID {gabriel_conceicao_id}): {len(conceicao_tickets)} tickets encontrados")
        if conceicao_tickets:
            print("  Primeiros 5 tickets:")
            for ticket in conceicao_tickets[:5]:
                print(f"    Ticket {ticket['id']}: Status {ticket['status']}")
        
        print(f"\nGabriel Machado (ID {gabriel_machado_id}): {len(machado_tickets)} tickets encontrados")
        if machado_tickets:
            print("  Primeiros 5 tickets:")
            for ticket in machado_tickets[:5]:
                print(f"    Ticket {ticket['id']}: Status {ticket['status']}")
        
        # Simular o agrupamento por técnico
        print(f"\n--- Simulando agrupamento por técnico ---")
        technician_stats = {}
        
        for ticket in tickets:
            if not isinstance(ticket, dict):
                continue
            
            tech_id = ticket.get(str(tech_field_id))
            if not tech_id or tech_id == '0':
                continue
            
            # Processar tech_id
            if isinstance(tech_id, list):
                if len(tech_id) == 0:
                    continue
                tech_id = str(tech_id[0])
            elif isinstance(tech_id, str):
                if tech_id.startswith('[') and tech_id.endswith(']'):
                    import re
                    numbers = re.findall(r"'(\d+)'", tech_id)
                    if not numbers:
                        numbers = re.findall(r'"(\d+)"', tech_id)
                    if not numbers:
                        numbers = re.findall(r'(\d+)', tech_id)
                    
                    if numbers:
                        tech_id = str(numbers[0])
                    else:
                        continue
                else:
                    tech_id = str(tech_id)
            else:
                tech_id = str(tech_id)
            
            if tech_id not in technician_stats:
                technician_stats[tech_id] = {
                    'total': 0,
                    'abertos': 0,
                    'fechados': 0,
                    'pendentes': 0
                }
            
            technician_stats[tech_id]['total'] += 1
            
            # Contar por status
            status_id = str(ticket.get('12', '0'))
            if status_id in ['1', '2']:  # Novo, Em atendimento
                technician_stats[tech_id]['abertos'] += 1
            elif status_id in ['4', '3']:  # Pendente, Planejado
                technician_stats[tech_id]['pendentes'] += 1
            elif status_id in ['5', '6']:  # Solucionado, Fechado
                technician_stats[tech_id]['fechados'] += 1
        
        print(f"\nEstatísticas dos Gabriels:")
        if gabriel_conceicao_id in technician_stats:
            stats = technician_stats[gabriel_conceicao_id]
            print(f"Gabriel Conceição: {stats}")
        else:
            print(f"Gabriel Conceição: NÃO ENCONTRADO nas estatísticas")
        
        if gabriel_machado_id in technician_stats:
            stats = technician_stats[gabriel_machado_id]
            print(f"Gabriel Machado: {stats}")
        else:
            print(f"Gabriel Machado: NÃO ENCONTRADO nas estatísticas")
        
        print(f"\nTotal de técnicos com tickets: {len(technician_stats)}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_tickets_query()