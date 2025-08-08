#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.services.glpi_service import GLPIService
import json

def debug_dtic_groups():
    """Debug dos grupos DTIC e técnicos"""
    glpi = GLPIService()
    
    print("=== DEBUG DOS GRUPOS DTIC ===")
    print(f"Service levels configurados: {glpi.service_levels}")
    
    # Verificar se consegue autenticar
    if not glpi._ensure_authenticated():
        print("❌ Falha na autenticação")
        return
    
    print("✅ Autenticação OK")
    
    # Para cada grupo DTIC, verificar se há usuários
    for level, group_id in glpi.service_levels.items():
        print(f"\n--- Verificando grupo {level} (ID: {group_id}) ---")
        
        try:
            # Buscar usuários no grupo
            response = glpi._make_authenticated_request(
                'GET',
                f"{glpi.glpi_url}/search/Group_User",
                params={
                    "range": "0-99",
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
                
                print(f"Usuários encontrados no grupo {level}: {len(users_in_group)}")
                
                if users_in_group:
                    for user_entry in users_in_group[:5]:  # Mostrar apenas os primeiros 5
                        if isinstance(user_entry, dict) and "4" in user_entry:
                            user_id = user_entry["4"]
                            
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
                    print(f"  Nenhum usuário encontrado no grupo {level}")
            else:
                print(f"❌ Erro ao buscar usuários do grupo {level}: {response.status_code if response else 'No response'}")
                
        except Exception as e:
            print(f"❌ Erro ao processar grupo {level}: {e}")
    
    # Testar alguns IDs de técnicos conhecidos
    print("\n--- Testando técnicos específicos ---")
    test_user_ids = ["926", "1032", "1160", "1197", "1291"]  # IDs que apareceram nos logs
    
    for user_id in test_user_ids:
        print(f"\nTestando técnico ID {user_id}:")
        is_dtic = glpi._is_dtic_technician(user_id)
        user_name = glpi._get_user_name(user_id)
        print(f"  Nome: {user_name}")
        print(f"  É da DTIC: {is_dtic}")

if __name__ == "__main__":
    debug_dtic_groups()