#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from backend.services.glpi_service import GLPIService
import json

def test_all_technicians():
    """Testa para encontrar todos os técnicos ativos no sistema"""
    glpi = GLPIService()
    
    print("=== BUSCANDO TODOS OS TÉCNICOS ATIVOS ===\n")
    
    # Verificar se consegue autenticar
    if not glpi._ensure_authenticated():
        print("❌ Falha na autenticação")
        return
    
    print("✅ Autenticação OK\n")
    
    # Buscar todos os usuários ativos
    try:
        response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/search/User",
            params={
                "range": "0-999",
                "criteria[0][field]": "8",  # Campo is_active
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": "1",
                "criteria[1][field]": "23",  # Campo is_deleted
                "criteria[1][searchtype]": "equals",
                "criteria[1][value]": "0",
                "forcedisplay[0]": "2",  # ID
                "forcedisplay[1]": "1",  # Nome
                "forcedisplay[2]": "34", # firstname
                "forcedisplay[3]": "9",  # realname
            }
        )
        
        if response and response.ok:
            users_data = response.json()
            users = users_data.get('data', [])
            
            print(f"Total de usuários ativos encontrados: {len(users)}\n")
            
            # Filtrar apenas usuários que parecem ser técnicos (têm nome e sobrenome)
            potential_technicians = []
            
            for user in users:
                if isinstance(user, dict):
                    user_id = user.get('2', '')
                    username = user.get('1', '')
                    firstname = user.get('34', '')
                    realname = user.get('9', '')
                    
                    # Filtrar usuários que parecem ser técnicos
                    if username and ('-' in username or '.' in username) and len(username) > 5:
                        potential_technicians.append({
                            'id': user_id,
                            'username': username,
                            'firstname': firstname,
                            'realname': realname
                        })
            
            print(f"Potenciais técnicos encontrados: {len(potential_technicians)}\n")
            
            # Mostrar os primeiros 20 técnicos
            print("=== PRIMEIROS 20 TÉCNICOS ENCONTRADOS ===\n")
            for i, tech in enumerate(potential_technicians[:20], 1):
                print(f"{i:2d}. {tech['username']} (ID: {tech['id']})")
                if tech['firstname'] or tech['realname']:
                    print(f"     Nome: {tech['firstname']} {tech['realname']}")
                print()
            
            # Verificar grupos de alguns técnicos
            print("\n=== VERIFICANDO GRUPOS DOS PRIMEIROS 10 TÉCNICOS ===\n")
            
            for tech in potential_technicians[:10]:
                user_id = tech['id']
                username = tech['username']
                
                print(f"Técnico: {username} (ID: {user_id})")
                
                # Buscar grupos do usuário
                try:
                    group_response = glpi._make_authenticated_request(
                        'GET',
                        f"{glpi.glpi_url}/search/Group_User",
                        params={
                            "range": "0-99",
                            "criteria[0][field]": "4",  # Campo users_id
                            "criteria[0][searchtype]": "equals",
                            "criteria[0][value]": str(user_id),
                            "forcedisplay[0]": "3",  # groups_id
                            "forcedisplay[1]": "4",  # users_id
                        }
                    )
                    
                    if group_response and group_response.ok:
                        user_groups = group_response.json()
                        groups_data = user_groups.get('data', [])
                        
                        if groups_data:
                            print(f"  Grupos:")
                            for group_entry in groups_data:
                                if isinstance(group_entry, dict) and "3" in group_entry:
                                    group_id = group_entry["3"]
                                    
                                    # Buscar nome do grupo
                                    group_detail_response = glpi._make_authenticated_request(
                                        'GET',
                                        f"{glpi.glpi_url}/Group/{group_id}"
                                    )
                                    
                                    if group_detail_response and group_detail_response.ok:
                                        group_data = group_detail_response.json()
                                        group_name = group_data.get('name', f'ID:{group_id}')
                                        print(f"    - {group_name} (ID: {group_id})")
                        else:
                            print(f"  Não está em nenhum grupo")
                    else:
                        print(f"  ❌ Erro ao buscar grupos")
                        
                except Exception as e:
                    print(f"  ❌ Erro ao verificar grupos: {e}")
                
                print()
            
            # Buscar técnicos que têm tickets atribuídos
            print("\n=== BUSCANDO TÉCNICOS COM TICKETS ATRIBUÍDOS ===\n")
            
            # Descobrir o ID do campo técnico
            tech_field_id = None
            try:
                # Buscar campo "Técnico" ou "Assigned to"
                search_response = glpi._make_authenticated_request(
                    'GET',
                    f"{glpi.glpi_url}/search/Ticket",
                    params={
                        "range": "0-50",
                        "criteria[0][field]": "5",  # Campo users_id_tech (técnico)
                        "criteria[0][searchtype": "contains",
                        "criteria[0][value]": "1",
                        "forcedisplay[0]": "5",  # users_id_tech
                    }
                )
                
                if search_response and search_response.ok:
                    tickets_data = search_response.json()
                    tickets = tickets_data.get('data', [])
                    
                    technicians_with_tickets = set()
                    
                    for ticket in tickets:
                        if isinstance(ticket, dict) and "5" in ticket:
                            tech_id = ticket["5"]
                            if tech_id and tech_id != "0":
                                technicians_with_tickets.add(str(tech_id))
                    
                    print(f"Técnicos únicos com tickets atribuídos: {len(technicians_with_tickets)}")
                    
                    # Buscar nomes dos técnicos
                    print("\nTécnicos com tickets:")
                    for tech_id in sorted(technicians_with_tickets, key=int)[:15]:
                        user_response = glpi._make_authenticated_request(
                            'GET',
                            f"{glpi.glpi_url}/User/{tech_id}"
                        )
                        
                        if user_response and user_response.ok:
                            user_data = user_response.json()
                            username = user_data.get('name', f'ID:{tech_id}')
                            is_active = user_data.get('is_active', 0)
                            is_deleted = user_data.get('is_deleted', 1)
                            
                            status = "✅ Ativo" if (is_active == 1 and is_deleted == 0) else "❌ Inativo/Deletado"
                            print(f"  - {username} (ID: {tech_id}) - {status}")
                
            except Exception as e:
                print(f"❌ Erro ao buscar técnicos com tickets: {e}")
            
        else:
            print(f"❌ Erro ao buscar usuários: {response.status_code if response else 'No response'}")
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    test_all_technicians()