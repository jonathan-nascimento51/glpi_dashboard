#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debugar o problema com Profile_User no GLPI.
Investiga se o perfil de técnico (ID 6) existe e quais perfis estão disponíveis.
"""

import sys
import os

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService

def debug_profile_user():
    """Debug do problema com Profile_User"""
    print("=== DEBUG PROFILE_USER ===")
    
    # Inicializar serviço GLPI
    glpi_service = GLPIService()
    
    # Autenticar
    print("\n1. Autenticando com GLPI...")
    if not glpi_service.authenticate():
        print("❌ Falha na autenticação")
        return False
    print("✅ Autenticação bem-sucedida")
    
    # Investigar perfis disponíveis
    print("\n2. Investigando perfis disponíveis...")
    try:
        # Buscar todos os perfis
        profile_response = glpi_service._make_authenticated_request(
            "GET",
            f"{glpi_service.glpi_url}/Profile",
            params={"range": "0-50"}
        )
        
        if profile_response and profile_response.ok:
            profiles = profile_response.json()
            print(f"✅ Encontrados {len(profiles)} perfis:")
            for profile in profiles:
                print(f"   ID: {profile.get('id', 'N/A')} - Nome: {profile.get('name', 'N/A')}")
        else:
            print(f"❌ Falha ao buscar perfis: {profile_response.status_code if profile_response else 'No response'}")
    except Exception as e:
        print(f"❌ Erro ao buscar perfis: {e}")
    
    # Investigar Profile_User com diferentes perfis
    print("\n3. Investigando Profile_User...")
    
    # Testar diferentes IDs de perfil
    profile_ids_to_test = [6, 4, 2, 3, 5, 7, 8]  # Incluindo o 6 (técnico) e outros comuns
    
    for profile_id in profile_ids_to_test:
        print(f"\n   Testando perfil ID {profile_id}:")
        try:
            profile_user_params = {
                "range": "0-10",
                "criteria[0][field]": "4",  # profiles_id
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": str(profile_id),
                "forcedisplay[0]": "2",  # ID do Profile_User
                "forcedisplay[1]": "5",  # users_id
                "forcedisplay[2]": "4",  # profiles_id
                "forcedisplay[3]": "80", # entities_id
            }
            
            response = glpi_service._make_authenticated_request(
                "GET",
                f"{glpi_service.glpi_url}/search/Profile_User",
                params=profile_user_params
            )
            
            if response and response.ok:
                data = response.json()
                profile_users = data.get('data', [])
                print(f"     ✅ Perfil {profile_id}: {len(profile_users)} usuários")
                if profile_users:
                    print(f"     Amostra: {profile_users[0]}")
            else:
                print(f"     ❌ Perfil {profile_id}: Falha na requisição ({response.status_code if response else 'No response'})")
                
        except Exception as e:
            print(f"     ❌ Perfil {profile_id}: Erro - {e}")
    
    # Investigar estrutura da tabela Profile_User
    print("\n4. Investigando estrutura da tabela Profile_User...")
    try:
        # Buscar alguns registros sem filtro para ver a estrutura
        response = glpi_service._make_authenticated_request(
            "GET",
            f"{glpi_service.glpi_url}/search/Profile_User",
            params={
                "range": "0-5",
                "forcedisplay[0]": "2",  # ID
                "forcedisplay[1]": "4",  # profiles_id
                "forcedisplay[2]": "5",  # users_id
                "forcedisplay[3]": "80", # entities_id
            }
        )
        
        if response and response.ok:
            data = response.json()
            profile_users = data.get('data', [])
            print(f"✅ Estrutura Profile_User ({len(profile_users)} registros):")
            for i, pu in enumerate(profile_users[:3]):
                print(f"   Registro {i+1}: {pu}")
        else:
            print(f"❌ Falha ao buscar estrutura: {response.status_code if response else 'No response'}")
            
    except Exception as e:
        print(f"❌ Erro ao investigar estrutura: {e}")
    
    # Investigar usuários diretamente
    print("\n5. Investigando usuários diretamente...")
    try:
        # Buscar alguns usuários ativos
        user_response = glpi_service._make_authenticated_request(
            "GET",
            f"{glpi_service.glpi_url}/search/User",
            params={
                "range": "0-10",
                "criteria[0][field]": "8",  # is_active
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": "1",
                "forcedisplay[0]": "2",  # ID
                "forcedisplay[1]": "1",  # Username
                "forcedisplay[2]": "9",  # Firstname
                "forcedisplay[3]": "34", # Realname
            }
        )
        
        if user_response and user_response.ok:
            users = user_response.json().get('data', [])
            print(f"✅ Encontrados {len(users)} usuários ativos:")
            for i, user in enumerate(users[:5]):
                print(f"   Usuário {i+1}: ID={user.get('2', 'N/A')}, Nome={user.get('9', '')} {user.get('34', '')}, Username={user.get('1', 'N/A')}")
        else:
            print(f"❌ Falha ao buscar usuários: {user_response.status_code if user_response else 'No response'}")
            
    except Exception as e:
        print(f"❌ Erro ao buscar usuários: {e}")
    
    print("\n=== DEBUG CONCLUÍDO ===")
    return True

if __name__ == "__main__":
    try:
        debug_profile_user()
    except Exception as e:
        print(f"\n💥 Erro durante o debug: {e}")
        import traceback
        traceback.print_exc()