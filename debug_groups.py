#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_groups():
    """Debug dos grupos disponíveis no GLPI"""
    try:
        # Inicializar serviço GLPI
        service = GLPIService()
        
        print("=== DEBUG DOS GRUPOS DISPONÍVEIS ===")
        
        # Buscar todos os grupos
        response = service._make_authenticated_request(
            'GET',
            f"{service.glpi_url}/Group",
            params={
                "range": "0-100",
                "is_deleted": 0
            }
        )
        
        if response and response.ok:
            groups_data = response.json()
            print(f"Encontrados {len(groups_data)} grupos:")
            print("-" * 80)
            
            for group in groups_data:
                if isinstance(group, dict):
                    group_id = group.get('id', 'N/A')
                    group_name = group.get('name', 'Sem nome')
                    print(f"ID: {group_id:3} | Nome: {group_name}")
        else:
            print(f"Erro ao buscar grupos: {response.status_code if response else 'Sem resposta'}")
        
        print("\n=== GRUPOS CONFIGURADOS PARA NÍVEIS ===")
        for level, group_id in service.service_levels.items():
            print(f"{level}: Grupo ID {group_id}")
        
        # Verificar se os grupos N1-N4 existem
        print("\n=== VERIFICAÇÃO DOS GRUPOS N1-N4 ===")
        for level, group_id in service.service_levels.items():
            response = service._make_authenticated_request(
                'GET',
                f"{service.glpi_url}/Group/{group_id}"
            )
            
            if response and response.ok:
                group_data = response.json()
                group_name = group_data.get('name', 'Sem nome')
                print(f"{level} (ID {group_id}): {group_name} - EXISTE")
            else:
                print(f"{level} (ID {group_id}): NÃO EXISTE ou ERRO")
        
        # Buscar usuários em cada grupo N1-N4
        print("\n=== USUÁRIOS NOS GRUPOS N1-N4 ===")
        for level, group_id in service.service_levels.items():
            response = service._make_authenticated_request(
                'GET',
                f"{service.glpi_url}/search/Group_User",
                params={
                    "range": "0-50",
                    "criteria[0][field]": "3",  # Campo groups_id
                    "criteria[0][searchtype]": "equals",
                    "criteria[0][value]": str(group_id),
                    "forcedisplay[0]": "3",  # groups_id
                    "forcedisplay[1]": "4"   # users_id
                }
            )
            
            if response and response.ok:
                users_data = response.json()
                user_count = users_data.get('totalcount', 0)
                print(f"{level} (Grupo {group_id}): {user_count} usuários")
                
                if user_count > 0 and users_data.get('data'):
                    print(f"  Primeiros usuários:")
                    for user_entry in users_data['data'][:5]:  # Mostrar apenas os 5 primeiros
                        if isinstance(user_entry, dict) and "4" in user_entry:
                            user_id = user_entry["4"]
                            print(f"    - Usuário ID: {user_id}")
            else:
                print(f"{level} (Grupo {group_id}): ERRO na busca")
        
        service.close_session()
        
    except Exception as e:
        logger.error(f"Erro no debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_groups()