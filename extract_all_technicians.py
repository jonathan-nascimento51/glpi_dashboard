#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from backend.services.glpi_service import GLPIService
import json
from collections import defaultdict

def extract_all_technicians():
    """Extrai todos os técnicos únicos dos tickets"""
    glpi = GLPIService()
    
    print("=== EXTRAINDO TODOS OS TÉCNICOS DOS TICKETS ===\n")
    
    # Verificar se consegue autenticar
    if not glpi._ensure_authenticated():
        print("❌ Falha na autenticação")
        return
    
    print("✅ Autenticação OK\n")
    
    all_technicians = set()
    technician_tickets = defaultdict(int)
    
    # Buscar tickets em lotes
    batch_size = 100
    total_processed = 0
    
    try:
        # Primeiro, descobrir quantos tickets existem
        response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/search/Ticket",
            params={
                "range": "0-0",
                "forcedisplay[0]": "2",  # ID
            }
        )
        
        if response and response.ok:
            tickets_data = response.json()
            total_tickets = tickets_data.get('totalcount', 0)
            print(f"Total de tickets no sistema: {total_tickets}\n")
            
            # Processar em lotes
            for start in range(0, min(total_tickets, 1000), batch_size):  # Limitar a 1000 para teste
                end = start + batch_size - 1
                print(f"Processando tickets {start}-{end}...")
                
                response = glpi._make_authenticated_request(
                    'GET',
                    f"{glpi.glpi_url}/search/Ticket",
                    params={
                        "range": f"{start}-{end}",
                        "forcedisplay[0]": "2",  # ID
                        "forcedisplay[1]": "5",  # users_id_tech
                    }
                )
                
                if response and response.ok:
                    batch_data = response.json()
                    tickets = batch_data.get('data', [])
                    
                    for ticket in tickets:
                        if isinstance(ticket, dict) and "5" in ticket:
                            tech_field = ticket["5"]
                            
                            # Técnicos podem vir como lista ou string
                            if isinstance(tech_field, list):
                                for tech_id in tech_field:
                                    if tech_id and str(tech_id) != "0":
                                        all_technicians.add(str(tech_id))
                                        technician_tickets[str(tech_id)] += 1
                            elif tech_field and str(tech_field) != "0":
                                all_technicians.add(str(tech_field))
                                technician_tickets[str(tech_field)] += 1
                    
                    total_processed += len(tickets)
                    
                else:
                    print(f"❌ Erro no lote {start}-{end}: {response.status_code if response else 'No response'}")
                    break
            
            print(f"\nTotal de tickets processados: {total_processed}")
            print(f"Técnicos únicos encontrados: {len(all_technicians)}\n")
            
            # Buscar informações dos técnicos
            print("=== INFORMAÇÕES DOS TÉCNICOS ===\n")
            
            technician_info = []
            
            for tech_id in sorted(all_technicians, key=lambda x: technician_tickets[x], reverse=True):
                try:
                    user_response = glpi._make_authenticated_request(
                        'GET',
                        f"{glpi.glpi_url}/User/{tech_id}"
                    )
                    
                    if user_response and user_response.ok:
                        user_data = user_response.json()
                        username = user_data.get('name', f'ID:{tech_id}')
                        firstname = user_data.get('firstname', '')
                        realname = user_data.get('realname', '')
                        is_active = user_data.get('is_active', 0)
                        is_deleted = user_data.get('is_deleted', 1)
                        
                        full_name = f"{firstname} {realname}".strip()
                        if not full_name:
                            full_name = username
                        
                        status = "✅ Ativo" if (is_active == 1 and is_deleted == 0) else "❌ Inativo/Deletado"
                        ticket_count = technician_tickets[tech_id]
                        
                        technician_info.append({
                            'id': tech_id,
                            'username': username,
                            'full_name': full_name,
                            'is_active': is_active == 1 and is_deleted == 0,
                            'ticket_count': ticket_count
                        })
                        
                        print(f"{len(technician_info):2d}. {full_name} ({username}) - ID: {tech_id}")
                        print(f"     Status: {status} | Tickets: {ticket_count}")
                        
                        # Verificar grupos do técnico
                        try:
                            group_response = glpi._make_authenticated_request(
                                'GET',
                                f"{glpi.glpi_url}/search/Group_User",
                                params={
                                    "range": "0-20",
                                    "criteria[0][field]": "4",  # Campo users_id
                                    "criteria[0][searchtype]": "equals",
                                    "criteria[0][value]": str(tech_id),
                                    "forcedisplay[0]": "3",  # groups_id
                                }
                            )
                            
                            if group_response and group_response.ok:
                                user_groups = group_response.json()
                                groups_data = user_groups.get('data', [])
                                
                                if groups_data:
                                    group_names = []
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
                                                group_names.append(f"{group_name} ({group_id})")
                                    
                                    if group_names:
                                        print(f"     Grupos: {', '.join(group_names)}")
                                    else:
                                        print(f"     Grupos: Nenhum")
                                else:
                                    print(f"     Grupos: Nenhum")
                        except Exception as e:
                            print(f"     Grupos: Erro ao verificar ({e})")
                        
                        print()
                        
                except Exception as e:
                    print(f"❌ Erro ao buscar técnico {tech_id}: {e}")
            
            # Resumo
            print("\n=== RESUMO ===\n")
            active_technicians = [t for t in technician_info if t['is_active']]
            inactive_technicians = [t for t in technician_info if not t['is_active']]
            
            print(f"Total de técnicos encontrados: {len(technician_info)}")
            print(f"Técnicos ativos: {len(active_technicians)}")
            print(f"Técnicos inativos/deletados: {len(inactive_technicians)}")
            
            print(f"\nTop 10 técnicos ativos por número de tickets:")
            active_sorted = sorted(active_technicians, key=lambda x: x['ticket_count'], reverse=True)
            for i, tech in enumerate(active_sorted[:10], 1):
                print(f"{i:2d}. {tech['full_name']} - {tech['ticket_count']} tickets")
            
        else:
            print(f"❌ Erro ao buscar tickets: {response.status_code if response else 'No response'}")
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    extract_all_technicians()