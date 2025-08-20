#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import logging
from datetime import datetime

# Desabilitar todos os logs
logging.disable(logging.CRITICAL)
sys.stderr = open(os.devnull, 'w')

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService

def main():
    print("=== Debug Extração de IDs de Usuário ===")
    
    # Configurar GLPI service
    glpi_service = GLPIService()
    
    # Autenticar
    print("\n1. Autenticando...")
    if not glpi_service.authenticate():
        print("❌ Falha na autenticação")
        return
    print("✅ Autenticação bem-sucedida")
    
    # Buscar Profile_User com filtro de entidade
    print("\n2. Buscando Profile_User com entidade ID 2...")
    
    profile_params = {
        "range": "0-999",
        "criteria[0][field]": "4",  # profiles_id
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": "6",  # ID do perfil técnico
        "criteria[1][field]": "80",  # entities_id
        "criteria[1][searchtype]": "equals",
        "criteria[1][value]": "2",  # ID da entidade
        "criteria[1][link]": "AND",
        "forcedisplay[0]": "2",  # ID do Profile_User
        "forcedisplay[1]": "3",  # entities_id
        "forcedisplay[2]": "4",  # profiles_id
        "forcedisplay[3]": "5",  # users_id
        "forcedisplay[4]": "80", # entities_id (caminho completo)
    }
    
    print(f"Parâmetros: {json.dumps(profile_params, indent=2)}")
    
    response = glpi_service._make_authenticated_request(
        'GET', 
        f'{glpi_service.glpi_url}/search/Profile_User',
        params=profile_params
    )
    
    if not response or not response.ok:
        print(f"❌ Falha na busca: {response.status_code if response else 'None'}")
        return
    
    profile_result = response.json()
    profile_data = profile_result.get('data', [])
    
    print(f"✅ Encontrados {len(profile_data)} registros Profile_User")
    
    if not profile_data:
        print("❌ Nenhum registro encontrado")
        return
    
    print("\n3. Analisando estrutura dos dados...")
    
    # Mostrar estrutura completa dos primeiros registros
    for i, record in enumerate(profile_data[:3]):
        print(f"\nRegistro {i+1}:")
        print(f"  Estrutura completa: {record}")
        
        # Verificar campos específicos
        print(f"  Campo '2' (ID Profile_User): {record.get('2', 'AUSENTE')}")
        print(f"  Campo '3' (entities_id): {record.get('3', 'AUSENTE')}")
        print(f"  Campo '4' (profiles_id): {record.get('4', 'AUSENTE')}")
        print(f"  Campo '5' (users_id): {record.get('5', 'AUSENTE')}")
        print(f"  Campo '80' (entities_path): {record.get('80', 'AUSENTE')}")
    
    print("\n4. Extraindo IDs de usuário...")
    
    user_ids = set()
    problematic_records = []
    
    for i, profile_user in enumerate(profile_data):
        print(f"\nProcessando registro {i+1}:")
        print(f"  Dados: {profile_user}")
        
        if isinstance(profile_user, dict) and "5" in profile_user:
            user_id_raw = profile_user["5"]
            print(f"  Campo '5' encontrado: {user_id_raw} (tipo: {type(user_id_raw)})")
            
            user_id = str(user_id_raw).strip()
            print(f"  Após conversão para string: '{user_id}'")
            
            if user_id and user_id.isdigit():
                user_ids.add(user_id)
                print(f"  ✅ ID válido adicionado: {user_id}")
            else:
                print(f"  ❌ ID inválido: '{user_id}' (vazio ou não numérico)")
                problematic_records.append({
                    'record': profile_user,
                    'user_id_raw': user_id_raw,
                    'user_id_processed': user_id
                })
        else:
            print(f"  ❌ Campo '5' não encontrado ou registro inválido")
            problematic_records.append({
                'record': profile_user,
                'reason': 'Campo 5 ausente'
            })
    
    print(f"\n5. Resultados da extração:")
    print(f"  IDs válidos extraídos: {len(user_ids)}")
    print(f"  IDs: {sorted(list(user_ids))}")
    print(f"  Registros problemáticos: {len(problematic_records)}")
    
    if problematic_records:
        print("\n6. Registros problemáticos:")
        for i, prob in enumerate(problematic_records):
            print(f"  Problema {i+1}: {prob}")
    
    # Testar busca de usuários com os IDs extraídos
    if user_ids:
        print("\n7. Testando busca de usuários com IDs extraídos...")
        
        user_ids_list = list(user_ids)
        user_params = {
            "range": "0-999",
            "forcedisplay[0]": "2",  # ID
            "forcedisplay[1]": "1",  # Username
            "forcedisplay[2]": "9",  # Firstname
            "forcedisplay[3]": "34", # Realname
            "forcedisplay[4]": "8",  # is_active
            "forcedisplay[5]": "3",  # is_deleted
        }
        
        # Adicionar critérios OR para cada usuário
        for idx, user_id in enumerate(user_ids_list[:5]):  # Testar apenas os primeiros 5
            user_params[f"criteria[{idx}][field]"] = "2"  # ID
            user_params[f"criteria[{idx}][searchtype]"] = "equals"
            user_params[f"criteria[{idx}][value]"] = user_id
            if idx > 0:
                user_params[f"criteria[{idx}][link]"] = "OR"
        
        print(f"Parâmetros de busca de usuários: {json.dumps(user_params, indent=2)}")
        
        user_response = glpi_service._make_authenticated_request(
            'GET', 
            f'{glpi_service.glpi_url}/search/User',
            params=user_params
        )
        
        if user_response and user_response.status_code in [200, 206]:
            user_data = user_response.json().get('data', [])
            print(f"✅ Encontrados {len(user_data)} usuários")
            
            for user in user_data:
                user_id = str(user.get("2", "")).strip()
                username = str(user.get("1", "")).strip()
                firstname = str(user.get("9", "")).strip()
                realname = str(user.get("34", "")).strip()
                is_active = str(user.get("8", "0")).strip()
                is_deleted = str(user.get("3", "0")).strip()
                
                print(f"  Usuário {user_id}: {username} ({firstname} {realname}) - Ativo: {is_active}, Deletado: {is_deleted}")
        else:
            print(f"❌ Falha na busca de usuários: {user_response.status_code if user_response else 'None'}")
    
    print("\n=== Fim do Debug ===")

if __name__ == "__main__":
    main()