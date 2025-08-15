#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from backend.services.glpi_service import GLPIService
import json

def debug_tickets_query_extended():
    """Debug estendido da consulta de tickets"""
    glpi = GLPIService()
    
    print("=== DEBUG CONSULTA DE TICKETS ESTENDIDO ===")
    
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
    
    print(f"\n--- Teste 1: Consulta específica para Gabriel Conceição ---")
    
    # Consulta específica para Gabriel Conceição
    search_params_conceicao = {
        "range": "0-999",
        "criteria[0][field]": str(tech_field_id),
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": gabriel_conceicao_id,
        "forcedisplay[0]": "2",   # ID do ticket
        "forcedisplay[1]": "12",  # Status
        "forcedisplay[2]": str(tech_field_id),  # Técnico atribuído
    }
    
    try:
        response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/search/Ticket",
            params=search_params_conceicao
        )
        
        if response and response.ok:
            result = response.json()
            if isinstance(result, dict) and 'data' in result:
                tickets = result['data']
                print(f"Gabriel Conceição: {len(tickets)} tickets encontrados")
                if tickets:
                    print("  Primeiros 5 tickets:")
                    for ticket in tickets[:5]:
                        print(f"    Ticket {ticket.get('2', 'N/A')}: Status {ticket.get('12', 'N/A')}, Técnico {ticket.get(str(tech_field_id), 'N/A')}")
            else:
                print("Gabriel Conceição: Nenhum ticket encontrado")
        else:
            print(f"❌ Falha na consulta para Gabriel Conceição: {response.status_code if response else 'No response'}")
    
    except Exception as e:
        print(f"❌ Erro na consulta para Gabriel Conceição: {e}")
    
    print(f"\n--- Teste 2: Consulta específica para Gabriel Machado ---")
    
    # Consulta específica para Gabriel Machado
    search_params_machado = {
        "range": "0-999",
        "criteria[0][field]": str(tech_field_id),
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": gabriel_machado_id,
        "forcedisplay[0]": "2",   # ID do ticket
        "forcedisplay[1]": "12",  # Status
        "forcedisplay[2]": str(tech_field_id),  # Técnico atribuído
    }
    
    try:
        response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/search/Ticket",
            params=search_params_machado
        )
        
        if response and response.ok:
            result = response.json()
            if isinstance(result, dict) and 'data' in result:
                tickets = result['data']
                print(f"Gabriel Machado: {len(tickets)} tickets encontrados")
                if tickets:
                    print("  Primeiros 5 tickets:")
                    for ticket in tickets[:5]:
                        print(f"    Ticket {ticket.get('2', 'N/A')}: Status {ticket.get('12', 'N/A')}, Técnico {ticket.get(str(tech_field_id), 'N/A')}")
            else:
                print("Gabriel Machado: Nenhum ticket encontrado")
        else:
            print(f"❌ Falha na consulta para Gabriel Machado: {response.status_code if response else 'No response'}")
    
    except Exception as e:
        print(f"❌ Erro na consulta para Gabriel Machado: {e}")
    
    print(f"\n--- Teste 3: Consulta geral com range maior ---")
    
    # Consulta geral com range maior
    search_params_geral = {
        "range": "0-99999",  # Range muito maior
        "forcedisplay[0]": "2",   # ID do ticket
        "forcedisplay[1]": "12",  # Status
        "forcedisplay[2]": str(tech_field_id),  # Técnico atribuído
    }
    
    try:
        response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/search/Ticket",
            params=search_params_geral
        )
        
        if response and response.ok:
            result = response.json()
            if isinstance(result, dict) and 'data' in result:
                tickets = result['data']
                print(f"Total de tickets encontrados: {len(tickets)}")
                
                # Contar tickets por técnico
                tech_counts = {}
                conceicao_found = False
                machado_found = False
                
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
                    
                    tech_counts[tech_id] = tech_counts.get(tech_id, 0) + 1
                    
                    if tech_id == gabriel_conceicao_id:
                        conceicao_found = True
                    elif tech_id == gabriel_machado_id:
                        machado_found = True
                
                print(f"\nResultados da consulta geral:")
                print(f"Gabriel Conceição encontrado: {conceicao_found}")
                if gabriel_conceicao_id in tech_counts:
                    print(f"Gabriel Conceição tickets: {tech_counts[gabriel_conceicao_id]}")
                
                print(f"Gabriel Machado encontrado: {machado_found}")
                if gabriel_machado_id in tech_counts:
                    print(f"Gabriel Machado tickets: {tech_counts[gabriel_machado_id]}")
                
                print(f"\nTop 10 técnicos por número de tickets:")
                sorted_techs = sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)
                for i, (tech_id, count) in enumerate(sorted_techs[:10]):
                    print(f"  {i+1}. Técnico {tech_id}: {count} tickets")
            
            else:
                print("Nenhum ticket encontrado na consulta geral")
        else:
            print(f"❌ Falha na consulta geral: {response.status_code if response else 'No response'}")
    
    except Exception as e:
        print(f"❌ Erro na consulta geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_tickets_query_extended()