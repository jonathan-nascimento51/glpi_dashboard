#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from backend.services.glpi_service import GLPIService
import json

def debug_all_gabriels():
    """Buscar todos os usuários com Gabriel no nome, incluindo inativos"""
    glpi = GLPIService()
    
    print("=== DEBUG TODOS OS GABRIELS ===")
    
    # Verificar se consegue autenticar
    if not glpi._ensure_authenticated():
        print("❌ Falha na autenticação")
        return
    
    print("✅ Autenticação OK")
    
    # Buscar por Gabriel no firstname (incluindo inativos)
    print(f"\n--- Buscando todos os usuários com 'Gabriel' no firstname (incluindo inativos) ---")
    try:
        response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/search/User",
            params={
                "range": "0-999",
                "criteria[0][field]": "3",  # Campo firstname
                "criteria[0][searchtype]": "contains",
                "criteria[0][value]": "Gabriel",
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
            
            print(f"Encontrados {len(users)} usuários com 'Gabriel' no firstname:")
            
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
            print(f"❌ Erro ao buscar usuários: {response.status_code if response else 'No response'}")
            
    except Exception as e:
        print(f"❌ Erro na busca: {e}")
    
    # Buscar por Gabriel no realname (incluindo inativos)
    print(f"\n--- Buscando todos os usuários com 'Gabriel' no realname (incluindo inativos) ---")
    try:
        response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/search/User",
            params={
                "range": "0-999",
                "criteria[0][field]": "9",  # Campo realname
                "criteria[0][searchtype]": "contains",
                "criteria[0][value]": "Gabriel",
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
            
            print(f"Encontrados {len(users)} usuários com 'Gabriel' no realname:")
            
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
            print(f"❌ Erro ao buscar usuários: {response.status_code if response else 'No response'}")
            
    except Exception as e:
        print(f"❌ Erro na busca: {e}")

if __name__ == "__main__":
    debug_all_gabriels()