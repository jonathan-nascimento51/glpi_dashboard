#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from backend.services.glpi_service import GLPIService
import json

def debug_tech_fields():
    """Debug dos campos de técnico nos tickets"""
    glpi = GLPIService()
    
    print("=== DEBUG CAMPOS DE TÉCNICO ===")
    
    # Verificar se consegue autenticar
    if not glpi._ensure_authenticated():
        print("❌ Falha na autenticação")
        return
    
    print("✅ Autenticação OK")
    
    gabriel_conceicao_id = "1404"
    gabriel_machado_id = "1291"
    
    # Tickets específicos do Gabriel Conceição
    conceicao_tickets = ["9034", "8793", "8400", "8698", "8366"]
    
    print(f"\n--- Analisando tickets do Gabriel Conceição ---")
    
    for ticket_id in conceicao_tickets:
        try:
            response = glpi._make_authenticated_request(
                'GET',
                f"{glpi.glpi_url}/Ticket/{ticket_id}"
            )
            
            if response and response.ok:
                ticket_data = response.json()
                
                print(f"\nTicket {ticket_id}:")
                print(f"  users_id_tech: {ticket_data.get('users_id_tech', 'N/A')}")
                print(f"  users_id_recipient: {ticket_data.get('users_id_recipient', 'N/A')}")
                print(f"  users_id_lastupdater: {ticket_data.get('users_id_lastupdater', 'N/A')}")
                print(f"  groups_id_tech: {ticket_data.get('groups_id_tech', 'N/A')}")
                print(f"  groups_id_assign: {ticket_data.get('groups_id_assign', 'N/A')}")
                print(f"  status: {ticket_data.get('status', 'N/A')}")
                print(f"  date_creation: {ticket_data.get('date_creation', 'N/A')}")
                print(f"  date_mod: {ticket_data.get('date_mod', 'N/A')}")
                
                # Verificar se há outros campos relacionados a usuários
                user_fields = [k for k in ticket_data.keys() if 'user' in k.lower()]
                if user_fields:
                    print(f"  Outros campos de usuário: {user_fields}")
                    for field in user_fields:
                        if field not in ['users_id_tech', 'users_id_recipient', 'users_id_lastupdater']:
                            print(f"    {field}: {ticket_data.get(field, 'N/A')}")
            
            else:
                print(f"❌ Falha ao buscar ticket {ticket_id}")
        
        except Exception as e:
            print(f"❌ Erro ao buscar ticket {ticket_id}: {e}")
    
    print(f"\n--- Verificando histórico de atribuições ---")
    
    # Verificar se há histórico de atribuições para um ticket específico
    ticket_id = "9034"  # Primeiro ticket do Gabriel Conceição
    
    try:
        # Buscar logs/histórico do ticket
        response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/Ticket/{ticket_id}/Log"
        )
        
        if response and response.ok:
            logs = response.json()
            print(f"\nHistórico do ticket {ticket_id}:")
            
            if isinstance(logs, list):
                for log in logs[:10]:  # Mostrar apenas os primeiros 10
                    print(f"  {log.get('date_mod', 'N/A')}: {log.get('old_value', 'N/A')} -> {log.get('new_value', 'N/A')} (campo: {log.get('itemtype_link', 'N/A')})")
            else:
                print(f"  Formato inesperado: {logs}")
        
        else:
            print(f"❌ Falha ao buscar histórico do ticket {ticket_id}: {response.status_code if response else 'No response'}")
    
    except Exception as e:
        print(f"❌ Erro ao buscar histórico: {e}")
    
    print(f"\n--- Buscando tickets por grupo DTIC ---")
    
    # Buscar tickets atribuídos ao grupo DTIC (IDs 89-92)
    dtic_groups = ["89", "90", "91", "92"]
    
    for group_id in dtic_groups:
        try:
            search_params = {
                "range": "0-100",
                "criteria[0][field]": "8",  # groups_id_assign
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": group_id,
                "forcedisplay[0]": "2",   # ID do ticket
                "forcedisplay[1]": "5",   # users_id_tech
                "forcedisplay[2]": "8",   # groups_id_assign
                "forcedisplay[3]": "15",  # Data de criação
            }
            
            response = glpi._make_authenticated_request(
                'GET',
                f"{glpi.glpi_url}/search/Ticket",
                params=search_params
            )
            
            if response and response.ok:
                result = response.json()
                tickets = result.get('data', [])
                print(f"\nGrupo {group_id}: {len(tickets)} tickets")
                
                # Contar Gabriels
                conceicao_count = 0
                machado_count = 0
                
                for ticket in tickets[:10]:  # Mostrar apenas os primeiros 10
                    tech_id = str(ticket.get('5', ''))
                    ticket_id = ticket.get('2', 'N/A')
                    group_assign = ticket.get('8', 'N/A')
                    date_creation = ticket.get('15', 'N/A')
                    
                    print(f"  Ticket {ticket_id}: Técnico {tech_id}, Grupo {group_assign}, Data {date_creation}")
                    
                    if tech_id == gabriel_conceicao_id:
                        conceicao_count += 1
                    elif tech_id == gabriel_machado_id:
                        machado_count += 1
                
                print(f"  Gabriel Conceição: {conceicao_count} tickets")
                print(f"  Gabriel Machado: {machado_count} tickets")
            
            else:
                print(f"❌ Falha na consulta do grupo {group_id}: {response.status_code if response else 'No response'}")
        
        except Exception as e:
            print(f"❌ Erro na consulta do grupo {group_id}: {e}")
    
    print(f"\n--- Verificando usuários DTIC ---")
    
    # Verificar se os Gabriels estão nos grupos DTIC
    for user_id, name in [(gabriel_conceicao_id, "Gabriel Conceição"), (gabriel_machado_id, "Gabriel Machado")]:
        try:
            response = glpi._make_authenticated_request(
                'GET',
                f"{glpi.glpi_url}/User/{user_id}/Group_User"
            )
            
            if response and response.ok:
                groups = response.json()
                print(f"\n{name} (ID {user_id}):")
                
                if isinstance(groups, list):
                    group_ids = [str(g.get('groups_id', '')) for g in groups]
                    print(f"  Grupos: {group_ids}")
                    
                    # Verificar se está em algum grupo DTIC
                    dtic_membership = [gid for gid in group_ids if gid in dtic_groups]
                    if dtic_membership:
                        print(f"  ✅ Membro dos grupos DTIC: {dtic_membership}")
                    else:
                        print(f"  ❌ Não é membro de grupos DTIC")
                else:
                    print(f"  Formato inesperado: {groups}")
            
            else:
                print(f"❌ Falha ao buscar grupos do usuário {user_id}: {response.status_code if response else 'No response'}")
        
        except Exception as e:
            print(f"❌ Erro ao buscar grupos do usuário {user_id}: {e}")

if __name__ == "__main__":
    debug_tech_fields()