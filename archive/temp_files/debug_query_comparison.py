#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from backend.services.glpi_service import GLPIService
import json

def debug_query_comparison():
    """Comparar diferentes tipos de consulta para entender a diferença"""
    glpi = GLPIService()
    
    print("=== DEBUG COMPARAÇÃO DE CONSULTAS ===")
    
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
    
    print(f"\n--- Consulta 1: Método original get_technician_ranking ---")
    
    # Consulta exata do método get_technician_ranking
    search_params_original = {
        "range": "0-9999",  # Buscar todos os tickets
        "forcedisplay[0]": "2",   # ID do ticket
        "forcedisplay[1]": "12",  # Status
        "forcedisplay[2]": str(tech_field_id),  # Técnico atribuído
    }
    
    try:
        response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/search/Ticket",
            params=search_params_original
        )
        
        if response and response.ok:
            result = response.json()
            total_count = result.get('totalcount', 0)
            data_count = len(result.get('data', []))
            print(f"Consulta original: totalcount={total_count}, data_length={data_count}")
            
            # Verificar se há Content-Range
            if 'Content-Range' in response.headers:
                content_range = response.headers['Content-Range']
                print(f"Content-Range: {content_range}")
            
            # Contar Gabriels
            tickets = result.get('data', [])
            conceicao_count = 0
            machado_count = 0
            
            for ticket in tickets:
                if not isinstance(ticket, dict):
                    continue
                
                tech_id = ticket.get(str(tech_field_id))
                if not tech_id:
                    continue
                
                # Processar tech_id
                if isinstance(tech_id, list):
                    if len(tech_id) > 0:
                        tech_id = str(tech_id[0])
                    else:
                        continue
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
                
                if tech_id == gabriel_conceicao_id:
                    conceicao_count += 1
                elif tech_id == gabriel_machado_id:
                    machado_count += 1
            
            print(f"Gabriel Conceição: {conceicao_count} tickets")
            print(f"Gabriel Machado: {machado_count} tickets")
        
        else:
            print(f"❌ Falha na consulta original: {response.status_code if response else 'No response'}")
    
    except Exception as e:
        print(f"❌ Erro na consulta original: {e}")
    
    print(f"\n--- Consulta 2: Sem forcedisplay ---")
    
    # Consulta sem forcedisplay
    search_params_no_display = {
        "range": "0-9999",
    }
    
    try:
        response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/search/Ticket",
            params=search_params_no_display
        )
        
        if response and response.ok:
            result = response.json()
            total_count = result.get('totalcount', 0)
            data_count = len(result.get('data', []))
            print(f"Consulta sem forcedisplay: totalcount={total_count}, data_length={data_count}")
            
            # Verificar se há Content-Range
            if 'Content-Range' in response.headers:
                content_range = response.headers['Content-Range']
                print(f"Content-Range: {content_range}")
        
        else:
            print(f"❌ Falha na consulta sem forcedisplay: {response.status_code if response else 'No response'}")
    
    except Exception as e:
        print(f"❌ Erro na consulta sem forcedisplay: {e}")
    
    print(f"\n--- Consulta 3: Range maior ---")
    
    # Consulta com range maior
    search_params_big_range = {
        "range": "0-99999",  # Range muito maior
        "forcedisplay[0]": "2",   # ID do ticket
        "forcedisplay[1]": "12",  # Status
        "forcedisplay[2]": str(tech_field_id),  # Técnico atribuído
    }
    
    try:
        response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/search/Ticket",
            params=search_params_big_range
        )
        
        if response and response.ok:
            result = response.json()
            total_count = result.get('totalcount', 0)
            data_count = len(result.get('data', []))
            print(f"Consulta range maior: totalcount={total_count}, data_length={data_count}")
            
            # Verificar se há Content-Range
            if 'Content-Range' in response.headers:
                content_range = response.headers['Content-Range']
                print(f"Content-Range: {content_range}")
            
            # Contar Gabriels
            tickets = result.get('data', [])
            conceicao_count = 0
            machado_count = 0
            
            for ticket in tickets:
                if not isinstance(ticket, dict):
                    continue
                
                tech_id = ticket.get(str(tech_field_id))
                if not tech_id:
                    continue
                
                # Processar tech_id
                if isinstance(tech_id, list):
                    if len(tech_id) > 0:
                        tech_id = str(tech_id[0])
                    else:
                        continue
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
                
                if tech_id == gabriel_conceicao_id:
                    conceicao_count += 1
                elif tech_id == gabriel_machado_id:
                    machado_count += 1
            
            print(f"Gabriel Conceição: {conceicao_count} tickets")
            print(f"Gabriel Machado: {machado_count} tickets")
        
        else:
            print(f"❌ Falha na consulta range maior: {response.status_code if response else 'No response'}")
    
    except Exception as e:
        print(f"❌ Erro na consulta range maior: {e}")
    
    print(f"\n--- Consulta 4: Paginação manual ---")
    
    # Tentar paginação manual
    total_conceicao = 0
    total_machado = 0
    page_size = 1000
    page = 0
    
    while True:
        start = page * page_size
        end = start + page_size - 1
        
        search_params_paginated = {
            "range": f"{start}-{end}",
            "forcedisplay[0]": "2",   # ID do ticket
            "forcedisplay[1]": "12",  # Status
            "forcedisplay[2]": str(tech_field_id),  # Técnico atribuído
        }
        
        try:
            response = glpi._make_authenticated_request(
                'GET',
                f"{glpi.glpi_url}/search/Ticket",
                params=search_params_paginated
            )
            
            if not response or not response.ok:
                break
            
            result = response.json()
            tickets = result.get('data', [])
            
            if not tickets:
                break
            
            page_conceicao = 0
            page_machado = 0
            
            for ticket in tickets:
                if not isinstance(ticket, dict):
                    continue
                
                tech_id = ticket.get(str(tech_field_id))
                if not tech_id:
                    continue
                
                # Processar tech_id
                if isinstance(tech_id, list):
                    if len(tech_id) > 0:
                        tech_id = str(tech_id[0])
                    else:
                        continue
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
                
                if tech_id == gabriel_conceicao_id:
                    page_conceicao += 1
                elif tech_id == gabriel_machado_id:
                    page_machado += 1
            
            total_conceicao += page_conceicao
            total_machado += page_machado
            
            print(f"Página {page}: {len(tickets)} tickets, Gabriel C: {page_conceicao}, Gabriel M: {page_machado}")
            
            page += 1
            
            # Limitar a 5 páginas para não sobrecarregar
            if page >= 5:
                break
        
        except Exception as e:
            print(f"❌ Erro na página {page}: {e}")
            break
    
    print(f"\nTotal paginação manual:")
    print(f"Gabriel Conceição: {total_conceicao} tickets")
    print(f"Gabriel Machado: {total_machado} tickets")

if __name__ == "__main__":
    debug_query_comparison()