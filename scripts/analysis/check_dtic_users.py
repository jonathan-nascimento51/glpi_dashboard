#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.services.glpi_service import GLPIService
import json

def check_dtic_users():
    """Verifica usuários nos grupos da DTIC"""
    glpi = GLPIService()
    
    print("=== VERIFICANDO USUÁRIOS NOS GRUPOS DTIC ===")
    
    # Verificar se consegue autenticar
    if not glpi._ensure_authenticated():
        print("❌ Falha na autenticação")
        return
    
    print("✅ Autenticação OK")
    
    # Grupos DTIC identificados
    dtic_groups = {
        "CC-SE-SUBADM-DTIC": 17,
        "CC-DTIC-RESTRITO": 18,
        "N1": 89,
        "N2": 90,
        "N3": 91,
        "N4": 92,
        "Inventário": 98
    }
    
    all_dtic_users = set()
    
    # Para cada grupo DTIC, verificar se há usuários
    for group_name, group_id in dtic_groups.items():
        print(f"\n--- Verificando grupo {group_name} (ID: {group_id}) ---")
        
        try:
            # Buscar usuários no grupo
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
                
                if users_in_group:
                    for user_entry in users_in_group:
                        if isinstance(user_entry, dict) and "4" in user_entry:
                            user_id = user_entry["4"]
                            all_dtic_users.add(str(user_id))
                            
                            # Buscar nome do usuário
                            user_response = glpi._make_authenticated_request(
                                'GET',
                                f"{glpi.glpi_url}/User/{user_id}"
                            )
                            
                            if user_response and user_response.ok:
                                user_data = user_response.json()
                                user_name = user_data.get('name', f'ID:{user_id}')
                                is_active = user_data.get('is_active', 0)
                                is_deleted = user_data.get('is_deleted', 1)
                                
                                status = "✅ Ativo" if (is_active == 1 and is_deleted == 0) else "❌ Inativo/Deletado"
                                print(f"  - {user_name} (ID: {user_id}) - {status}")
                else:
                    print(f"  Nenhum usuário encontrado no grupo {group_name}")
            else:
                print(f"❌ Erro ao buscar usuários do grupo {group_name}: {response.status_code if response else 'No response'}")
                
        except Exception as e:
            print(f"❌ Erro ao processar grupo {group_name}: {e}")
    
    print(f"\n=== RESUMO ===")
    print(f"Total de usuários únicos encontrados nos grupos DTIC: {len(all_dtic_users)}")
    
    if all_dtic_users:
        print("\nIDs dos usuários DTIC:")
        for user_id in sorted(all_dtic_users, key=int):
            print(f"  - {user_id}")
    
    # Testar alguns técnicos conhecidos contra os grupos principais
    print("\n--- Testando técnicos específicos nos grupos principais ---")
    test_user_ids = ["926", "1032", "1160", "1197", "1291"]
    
    for user_id in test_user_ids:
        print(f"\nTestando técnico ID {user_id}:")
        user_name = glpi._get_user_name(user_id)
        print(f"  Nome: {user_name}")
        
        # Verificar se está em algum grupo DTIC
        is_in_dtic = str(user_id) in all_dtic_users
        print(f"  Está nos grupos DTIC: {is_in_dtic}")
        
        # Verificar grupos do usuário
        try:
            response = glpi._make_authenticated_request(
                'GET',
                f"{glpi.glpi_url}/search/Group_User",
                params={
                    "range": "0-999",
                    "criteria[0][field]": "4",  # Campo users_id
                    "criteria[0][searchtype]": "equals",
                    "criteria[0][value]": str(user_id),
                    "forcedisplay[0]": "3",  # groups_id
                    "forcedisplay[1]": "4",  # users_id
                }
            )
            
            if response and response.ok:
                user_groups = response.json()
                groups_data = user_groups.get('data', [])
                
                if groups_data:
                    print(f"  Grupos do usuário:")
                    for group_entry in groups_data:
                        if isinstance(group_entry, dict) and "3" in group_entry:
                            group_id = group_entry["3"]
                            
                            # Buscar nome do grupo
                            group_response = glpi._make_authenticated_request(
                                'GET',
                                f"{glpi.glpi_url}/Group/{group_id}"
                            )
                            
                            if group_response and group_response.ok:
                                group_data = group_response.json()
                                group_name = group_data.get('name', f'ID:{group_id}')
                                print(f"    - {group_name} (ID: {group_id})")
                else:
                    print(f"  Usuário não está em nenhum grupo")
                    
        except Exception as e:
            print(f"  ❌ Erro ao verificar grupos do usuário: {e}")

if __name__ == "__main__":
    check_dtic_users()