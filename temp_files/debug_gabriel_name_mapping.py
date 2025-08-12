#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from backend.services.glpi_service import GLPIService
import json

def debug_gabriel_name_mapping():
    """Debug específico para verificar como o nome do Gabriel Conceição está sendo construído"""
    glpi = GLPIService()
    
    print("=== DEBUG MAPEAMENTO DE NOME - GABRIEL CONCEIÇÃO ===")
    
    # Verificar se consegue autenticar
    if not glpi._ensure_authenticated():
        print("❌ Falha na autenticação")
        return
    
    print("✅ Autenticação OK")
    
    # ID do Gabriel Conceição que encontramos
    gabriel_id = 1404
    
    print(f"\n--- Verificando usuário ID {gabriel_id} (Gabriel Conceição) ---")
    
    try:
        # Buscar dados completos do usuário
        user_response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/User/{gabriel_id}"
        )
        
        if user_response and user_response.ok:
            user_data = user_response.json()
            
            print("\n=== DADOS COMPLETOS DO USUÁRIO ===")
            for key, value in user_data.items():
                print(f"{key}: {value}")
            
            print("\n=== CONSTRUÇÃO DO NOME (como no código) ===")
            
            # Replicar a lógica do código
            display_name = ""
            if "realname" in user_data and "firstname" in user_data:
                display_name = f"{user_data['firstname']} {user_data['realname']}"
                print(f"Usando firstname + realname: '{display_name}'")
            elif "realname" in user_data:
                display_name = user_data["realname"]
                print(f"Usando apenas realname: '{display_name}'")
            elif "name" in user_data:
                display_name = user_data["name"]
                print(f"Usando name: '{display_name}'")
            elif "1" in user_data:
                display_name = user_data["1"]
                print(f"Usando campo '1': '{display_name}'")
            
            user_name = display_name.lower().strip()
            print(f"Nome final (lowercase + strip): '{user_name}'")
            
            # Verificar mapeamentos
            n1_names = ['gabriel andrade da conceicao', 'nicolas fernando muniz nunez']
            n2_names = ['alessandro carbonera vieira', 'jonathan nascimento moletta', 'thales vinicius paz leite', 'leonardo trojan repiso riela', 'edson joel dos santos silva', 'luciano marcelino da silva']
            n3_names = ['anderson da silva morim de oliveira', 'silvio godinho valim', 'jorge antonio vicente júnior', 'pablo hebling guimaraes', 'miguelangelo ferreira']
            n4_names = ['gabriel silva machado', 'luciano de araujo silva', 'wagner mengue', 'paulo césar pedó nunes', 'alexandre rovinski almoarqueg']
            
            print(f"\n=== VERIFICAÇÃO DE MAPEAMENTO ===")
            print(f"Nome esperado para N1: 'gabriel andrade da conceicao'")
            print(f"Nome atual: '{user_name}'")
            print(f"Match N1: {user_name in n1_names}")
            print(f"Match N2: {user_name in n2_names}")
            print(f"Match N3: {user_name in n3_names}")
            print(f"Match N4: {user_name in n4_names}")
            
            # Verificar se é DTIC
            is_dtic = glpi._is_dtic_technician(str(gabriel_id))
            print(f"\nÉ DTIC: {is_dtic}")
            
            # Verificar nível atual
            tech_level = glpi._get_technician_level(gabriel_id, 48)
            print(f"Nível determinado: {tech_level}")
            
            # Verificar grupos
            print(f"\n=== GRUPOS DO USUÁRIO ===")
            group_response = glpi._make_authenticated_request(
                'GET',
                f"{glpi.glpi_url}/search/Group_User",
                params={
                    "range": "0-99",
                    "criteria[0][field]": "4",  # Campo users_id
                    "criteria[0][searchtype]": "equals",
                    "criteria[0][value]": str(gabriel_id),
                    "forcedisplay[0]": "3",  # groups_id
                    "forcedisplay[1]": "4",  # users_id
                }
            )
            
            if group_response and group_response.ok:
                group_data = group_response.json()
                groups = group_data.get('data', [])
                
                print(f"Grupos encontrados: {len(groups)}")
                for group_entry in groups:
                    if isinstance(group_entry, dict) and "3" in group_entry:
                        group_id = group_entry["3"]
                        print(f"  Grupo ID: {group_id}")
                        
                        # Verificar se é um dos grupos de nível
                        service_levels = {"N1": 89, "N2": 90, "N3": 91, "N4": 92}
                        for level, level_group_id in service_levels.items():
                            if int(group_id) == level_group_id:
                                print(f"    -> Este é o grupo {level}!")
            else:
                print("Erro ao buscar grupos")
        
        else:
            print(f"❌ Erro ao buscar usuário: {user_response.status_code if user_response else 'No response'}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Verificar também o Gabriel Machado para comparação
    print(f"\n\n--- Verificando Gabriel Machado (ID 1291) para comparação ---")
    
    try:
        user_response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/User/1291"
        )
        
        if user_response and user_response.ok:
            user_data = user_response.json()
            
            print(f"Name: {user_data.get('name', 'N/A')}")
            print(f"Real Name: {user_data.get('realname', 'N/A')}")
            print(f"First Name: {user_data.get('firstname', 'N/A')}")
            
            # Construir nome
            display_name = ""
            if "realname" in user_data and "firstname" in user_data:
                display_name = f"{user_data['firstname']} {user_data['realname']}"
            elif "realname" in user_data:
                display_name = user_data["realname"]
            elif "name" in user_data:
                display_name = user_data["name"]
            
            user_name = display_name.lower().strip()
            print(f"Nome construído: '{user_name}'")
            
            # Verificar nível
            tech_level = glpi._get_technician_level(1291, 217)
            print(f"Nível determinado: {tech_level}")
        
    except Exception as e:
        print(f"❌ Erro ao verificar Gabriel Machado: {e}")

if __name__ == "__main__":
    debug_gabriel_name_mapping()