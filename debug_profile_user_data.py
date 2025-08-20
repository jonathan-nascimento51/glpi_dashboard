#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
from datetime import datetime

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService

def main():
    print("=== Debug Profile_User Data ===")
    
    # Configurar GLPI service
    glpi_service = GLPIService()
    
    # Autenticar
    print("\n1. Autenticando...")
    if not glpi_service.authenticate():
        print("❌ Falha na autenticação")
        return
    print("✅ Autenticação bem-sucedida")
    
    # Buscar Profile_User com perfil 6 (Tecnico) e entidade 2 (CENTRAL DE ATENDIMENTOS)
    print("\n2. Buscando Profile_User com perfil 6 e entidade 2...")
    
    params = {
        "criteria[0][field]": "5",  # profiles_id
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": "6",
        "criteria[1][field]": "80",  # entities_id
        "criteria[1][searchtype]": "equals", 
        "criteria[1][value]": "2",
        "criteria[1][link]": "AND",
        "forcedisplay[0]": "2",   # ID
        "forcedisplay[1]": "3",   # entities_id
        "forcedisplay[2]": "4",   # profiles_id
        "forcedisplay[3]": "5",   # users_id
        "range": "0-50"
    }
    
    response = glpi_service._make_authenticated_request(
        'GET',
        f'{glpi_service.glpi_url}/search/Profile_User',
        params=params
    )
    
    if response and response.status_code in [200, 206]:
        try:
            data = response.json()
            profile_users = data.get('data', [])
            print(f"✅ Encontrados {len(profile_users)} registros Profile_User")
            
            print("\n3. Analisando estrutura dos dados...")
            if profile_users:
                print(f"\nPrimeiro registro completo:")
                print(json.dumps(profile_users[0], indent=2, ensure_ascii=False))
                
                print("\n4. Extraindo users_id de todos os registros...")
                user_ids = []
                for i, profile_user in enumerate(profile_users):
                    print(f"\nRegistro {i+1}:")
                    print(f"  Dados completos: {profile_user}")
                    
                    # Tentar extrair users_id do campo "5"
                    users_id_field = profile_user.get("5", "")
                    print(f"  Campo '5' (users_id): {users_id_field} (tipo: {type(users_id_field)})")
                    
                    # Verificar outros campos também
                    for field_num in ["2", "3", "4", "5"]:
                        field_value = profile_user.get(field_num, "N/A")
                        print(f"  Campo '{field_num}': {field_value} (tipo: {type(field_value)})")
                    
                    # Tentar extrair ID do usuário
                    if users_id_field and str(users_id_field).strip() and str(users_id_field).strip().isdigit():
                        user_id = str(users_id_field).strip()
                        user_ids.append(user_id)
                        print(f"  ✅ ID válido extraído: {user_id}")
                    else:
                        print(f"  ❌ ID inválido ou vazio")
                
                print(f"\n5. IDs de usuários extraídos: {user_ids}")
                print(f"   Total de IDs válidos: {len(user_ids)}")
                
                # Agora testar busca de usuários
                if user_ids:
                    print("\n6. Testando busca de usuários pelos IDs...")
                    
                    # Construir parâmetros de busca
                    user_params = {
                        "forcedisplay[0]": "2",   # ID
                        "forcedisplay[1]": "1",   # name (username)
                        "forcedisplay[2]": "9",   # firstname
                        "forcedisplay[3]": "34",  # realname
                        "forcedisplay[4]": "8",   # is_active
                        "forcedisplay[5]": "3",   # is_deleted
                        "range": "0-100"
                    }
                    
                    # Adicionar critérios OR para cada ID
                    for idx, user_id in enumerate(user_ids):
                        user_params[f"criteria[{idx}][field]"] = "2"  # ID
                        user_params[f"criteria[{idx}][searchtype]"] = "equals"
                        user_params[f"criteria[{idx}][value]"] = user_id
                        if idx > 0:
                            user_params[f"criteria[{idx}][link]"] = "OR"
                    
                    print(f"Parâmetros de busca: {user_params}")
                    
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
                            
                            full_name = f"{firstname} {realname}".strip() or username
                            
                            print(f"\n  Usuário {user_id}:")
                            print(f"    Nome: {full_name}")
                            print(f"    Username: {username}")
                            print(f"    Ativo: {is_active}")
                            print(f"    Deletado: {is_deleted}")
                            
                            if is_active == "1" and (is_deleted == "0" or is_deleted == "None" or not is_deleted):
                                print(f"    ✅ Técnico válido")
                            else:
                                print(f"    ❌ Técnico inválido (inativo ou deletado)")
                    else:
                        print(f"❌ Falha na busca de usuários: {user_response.status_code if user_response else 'None'}")
                        if user_response:
                            print(f"Resposta: {user_response.text[:500]}")
                else:
                    print("❌ Nenhum ID de usuário válido encontrado")
            else:
                print("❌ Nenhum registro Profile_User encontrado")
                
        except Exception as e:
            print(f"❌ Erro ao processar resposta: {e}")
            print(f"Resposta bruta: {response.text[:500]}")
    else:
        print(f"❌ Falha na busca Profile_User: {response.status_code if response else 'None'}")
        if response:
            print(f"Resposta: {response.text[:500]}")
    
    print("\n=== Fim do Debug ===")

if __name__ == "__main__":
    main()