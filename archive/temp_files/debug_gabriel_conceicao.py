#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from backend.services.glpi_service import GLPIService
import json

def debug_gabriel_conceicao():
    """Debug específico para encontrar Gabriel Conceição"""
    glpi = GLPIService()
    
    print("=== DEBUG GABRIEL CONCEIÇÃO ===")
    
    # Verificar se consegue autenticar
    if not glpi._ensure_authenticated():
        print("❌ Falha na autenticação")
        return
    
    print("✅ Autenticação OK")
    
    # Verificar usuários nos grupos DTIC principais
    dtic_groups = {
        "CC-SE-SUBADM-DTIC": 17,
        "CC-DTIC-RESTRITO": 18
    }
    
    all_dtic_users = []
    
    for group_name, group_id in dtic_groups.items():
        print(f"\n--- Verificando grupo {group_name} (ID: {group_id}) ---")
        try:
            response = glpi._make_authenticated_request(
                'GET',
                f"{glpi.glpi_url}/search/Group_User",
                params={
                    "range": "0-999",
                    "criteria[0][field]": "3",  # Campo groups_id
                    "criteria[0][searchtype]": "equals",
                    "criteria[0][value]": str(group_id),
                    "forcedisplay[0]": "3",  # groups_id
                    "forcedisplay[1]": "4",  # users_id
                }
            )
            
            if response and response.ok:
                group_data = response.json()
                users_in_group = group_data.get('data', [])
                
                print(f"Usuários encontrados no grupo {group_name}: {len(users_in_group)}")
                
                for user_group in users_in_group:
                    user_id = user_group.get('4')
                    if user_id:
                        all_dtic_users.append(user_id)
                        user_name = glpi._get_user_name(str(user_id))
                        print(f"  ID: {user_id} - Nome: {user_name}")
                        
                        # Buscar dados completos do usuário
                        user_response = glpi._make_authenticated_request(
                            'GET',
                            f"{glpi.glpi_url}/User/{user_id}"
                        )
                        
                        if user_response and user_response.ok:
                            user_data = user_response.json()
                            name = user_data.get('name', 'N/A')
                            realname = user_data.get('realname', 'N/A')
                            firstname = user_data.get('firstname', 'N/A')
                            is_active = user_data.get('is_active', 'N/A')
                            is_deleted = user_data.get('is_deleted', 'N/A')
                            
                            print(f"    Name: {name}")
                            print(f"    Real Name: {realname}")
                            print(f"    First Name: {firstname}")
                            print(f"    Ativo: {is_active}")
                            print(f"    Deletado: {is_deleted}")
                            
                            # Verificar se contém "gabriel" e "conceição"
                            full_name = f"{firstname} {realname}".lower()
                            if 'gabriel' in full_name and ('conceicao' in full_name or 'conceição' in full_name):
                                print(f"    🎯 ENCONTRADO GABRIEL CONCEIÇÃO!")
                            
                            # Verificar se é DTIC
                            is_dtic = glpi._is_dtic_technician(str(user_id))
                            print(f"    É DTIC: {is_dtic}")
                            
                            # Contar tickets
                            try:
                                tickets_response = glpi._make_authenticated_request(
                                    'GET',
                                    f"{glpi.glpi_url}/search/Ticket",
                                    params={
                                        "range": "0-1",
                                        "criteria[0][field]": "5",  # Campo users_id_tech
                                        "criteria[0][searchtype]": "equals",
                                        "criteria[0][value]": str(user_id),
                                        "forcedisplay[0]": "2",  # ID do ticket
                                    }
                                )
                                
                                if tickets_response and tickets_response.ok:
                                    tickets_data = tickets_response.json()
                                    total_tickets = tickets_data.get('totalcount', 0)
                                    print(f"    Total de tickets: {total_tickets}")
                            except Exception as e:
                                print(f"    Erro ao contar tickets: {e}")
                            
                            print()
            
            else:
                print(f"❌ Erro ao buscar usuários do grupo {group_name}: {response.status_code if response else 'No response'}")
                
        except Exception as e:
            print(f"❌ Erro ao verificar grupo {group_name}: {e}")
    
    print(f"\n=== RESUMO ===")
    print(f"Total de usuários únicos encontrados nos grupos DTIC principais: {len(set(all_dtic_users))}")
    
    # Buscar especificamente por Gabriel nos nomes
    print(f"\n--- Buscando todos os Gabriels ativos ---")
    try:
        response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/search/User",
            params={
                "range": "0-999",
                "criteria[0][field]": "3",  # Campo firstname
                "criteria[0][searchtype]": "contains",
                "criteria[0][value]": "Gabriel",
                "criteria[1][link]": "AND",
                "criteria[1][field]": "8",  # Campo is_active
                "criteria[1][searchtype]": "equals",
                "criteria[1][value]": "1",
                "forcedisplay[0]": "2",  # ID
                "forcedisplay[1]": "1",  # name
                "forcedisplay[2]": "9",  # realname
                "forcedisplay[3]": "3",  # firstname
                "forcedisplay[4]": "8",  # is_active
                "forcedisplay[5]": "23", # is_deleted
            }
        )
        
        if response and response.ok:
            users_data = response.json()
            users = users_data.get('data', [])
            
            print(f"Encontrados {len(users)} Gabriels ativos:")
            
            for user in users:
                user_id = user.get('2', 'N/A')  # ID
                name = user.get('1', 'N/A')     # name
                realname = user.get('9', 'N/A') # realname
                firstname = user.get('3', 'N/A') # firstname
                is_active = user.get('8', 'N/A') # is_active
                is_deleted = user.get('23', 'N/A') # is_deleted
                
                print(f"\n  ID: {user_id}")
                print(f"  Name: {name}")
                print(f"  Real Name: {realname}")
                print(f"  First Name: {firstname}")
                print(f"  Ativo: {is_active}")
                print(f"  Deletado: {is_deleted}")
                
                # Verificar se contém "conceição"
                full_name = f"{firstname} {realname}".lower()
                if 'conceicao' in full_name or 'conceição' in full_name:
                    print(f"  🎯 ESTE É O GABRIEL CONCEIÇÃO!")
                
                if user_id != 'N/A':
                    is_dtic = glpi._is_dtic_technician(str(user_id))
                    print(f"  É DTIC: {is_dtic}")
                    
                    # Contar tickets
                    try:
                        tickets_response = glpi._make_authenticated_request(
                            'GET',
                            f"{glpi.glpi_url}/search/Ticket",
                            params={
                                "range": "0-1",
                                "criteria[0][field]": "5",  # Campo users_id_tech
                                "criteria[0][searchtype]": "equals",
                                "criteria[0][value]": str(user_id),
                                "forcedisplay[0]": "2",  # ID do ticket
                            }
                        )
                        
                        if tickets_response and tickets_response.ok:
                            tickets_data = tickets_response.json()
                            total_tickets = tickets_data.get('totalcount', 0)
                            print(f"  Total de tickets: {total_tickets}")
                    except Exception as e:
                        print(f"  Erro ao contar tickets: {e}")
        
        else:
            print(f"❌ Erro ao buscar Gabriels: {response.status_code if response else 'No response'}")
            
    except Exception as e:
        print(f"❌ Erro na busca de Gabriels: {e}")

if __name__ == "__main__":
    debug_gabriel_conceicao()