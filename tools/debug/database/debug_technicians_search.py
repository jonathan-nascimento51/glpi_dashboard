#!/usr/bin/env python3
"""
Script de debug específico para investigar a busca de técnicos no GLPI
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService
import json

def debug_technicians_search():
    """
    Investiga detalhadamente a busca de técnicos
    """
    print("=== DEBUG: BUSCA DE TÉCNICOS NO GLPI ===")
    
    # Inicializar serviço GLPI
    try:
        glpi = GLPIService()
        if not glpi._ensure_authenticated():
            print("❌ Falha na autenticação com GLPI")
            return
        print("✅ Autenticação com GLPI bem-sucedida")
    except Exception as e:
        print(f"❌ Erro ao inicializar GLPI: {e}")
        return
    
    print("\n=== ETAPA 1: Verificar perfis disponíveis ===")
    try:
        # Buscar todos os perfis para ver quais existem
        profiles_params = {
            "range": "0-50"
        }
        
        profiles_response = glpi._make_authenticated_request(
            "GET", f"{glpi.glpi_url}/search/Profile", params=profiles_params
        )
        
        if profiles_response and profiles_response.ok:
            profiles_data = profiles_response.json()
            total_profiles = profiles_data.get("totalcount", 0)
            profiles_list = profiles_data.get("data", [])
            
            print(f"📊 Total de perfis encontrados: {total_profiles}")
            print("   Perfis disponíveis:")
            
            for profile in profiles_list[:10]:  # Mostrar apenas os primeiros 10
                profile_id = profile.get("2", "N/A")
                profile_name = profile.get("1", "N/A")
                print(f"   - ID: {profile_id} - Nome: {profile_name}")
                
            # Verificar se existe perfil com ID 6
            profile_6_exists = any(profile.get("2") == "6" for profile in profiles_list)
            if profile_6_exists:
                print("✅ Perfil ID 6 encontrado")
            else:
                print("❌ Perfil ID 6 NÃO encontrado - este pode ser o problema!")
        else:
            print(f"❌ Falha ao buscar perfis: {profiles_response.status_code if profiles_response else 'No response'}")
            
    except Exception as e:
        print(f"❌ Erro ao verificar perfis: {e}")
    
    print("\n=== ETAPA 2: Buscar Profile_User com diferentes perfis ===")
    # Testar com diferentes IDs de perfil para ver qual funciona
    test_profile_ids = ["6", "4", "2", "3", "5", "7", "8"]
    
    for profile_id in test_profile_ids:
        try:
            print(f"\n🔍 Testando perfil ID {profile_id}:")
            
            profile_params = {
                "range": "0-20",
                "criteria[0][field]": "4",  # Campo Perfil
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": profile_id,
            }
            
            profile_response = glpi._make_authenticated_request(
                "GET", f"{glpi.glpi_url}/search/Profile_User", params=profile_params
            )
            
            if profile_response and profile_response.ok:
                profile_result = profile_response.json()
                total_count = profile_result.get("totalcount", 0)
                profile_data = profile_result.get("data", [])
                
                print(f"   Total de usuários com perfil {profile_id}: {total_count}")
                
                if total_count > 0:
                    print(f"   Primeiros usuários encontrados:")
                    for i, user in enumerate(profile_data[:3]):
                        user_id = user.get("3", "N/A")  # users_id
                        profile_user_id = user.get("2", "N/A")  # ID do Profile_User
                        print(f"     - Profile_User ID: {profile_user_id}, User ID: {user_id}")
                        
                        # Verificar se conseguimos obter dados do usuário
                        if user_id != "N/A" and user_id.isdigit():
                            try:
                                user_response = glpi._make_authenticated_request(
                                    "GET", f"{glpi.glpi_url}/User/{user_id}"
                                )
                                
                                if user_response and user_response.ok:
                                    user_data = user_response.json()
                                    username = user_data.get("name", "N/A")
                                    is_active = user_data.get("is_active", 0)
                                    is_deleted = user_data.get("is_deleted", 0)
                                    firstname = user_data.get("firstname", "")
                                    realname = user_data.get("realname", "")
                                    
                                    print(f"       Nome: {username}, Ativo: {is_active}, Deletado: {is_deleted}")
                                    print(f"       Nome completo: {firstname} {realname}")
                                else:
                                    print(f"       ❌ Falha ao obter dados do usuário {user_id}")
                            except Exception as e:
                                print(f"       ❌ Erro ao verificar usuário {user_id}: {e}")
                else:
                    print(f"   Nenhum usuário encontrado com perfil {profile_id}")
            else:
                print(f"   ❌ Falha na busca: {profile_response.status_code if profile_response else 'No response'}")
                
        except Exception as e:
            print(f"   ❌ Erro ao testar perfil {profile_id}: {e}")
    
    print("\n=== ETAPA 3: Buscar todos os usuários ativos ===")
    try:
        # Buscar usuários ativos independente do perfil
        users_params = {
            "range": "0-20",
            "criteria[0][field]": "8",  # is_active
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": "1",
        }
        
        users_response = glpi._make_authenticated_request(
            "GET", f"{glpi.glpi_url}/search/User", params=users_params
        )
        
        if users_response and users_response.ok:
            users_result = users_response.json()
            total_users = users_result.get("totalcount", 0)
            users_data = users_result.get("data", [])
            
            print(f"📊 Total de usuários ativos: {total_users}")
            print("   Primeiros usuários ativos:")
            
            for i, user in enumerate(users_data[:5]):
                user_id = user.get("2", "N/A")
                username = user.get("1", "N/A")
                print(f"   {i+1}. ID: {user_id} - Nome: {username}")
                
        else:
            print(f"❌ Falha ao buscar usuários ativos: {users_response.status_code if users_response else 'No response'}")
            
    except Exception as e:
        print(f"❌ Erro ao buscar usuários ativos: {e}")
    
    print("\n=== ETAPA 4: Verificar estrutura dos campos ===")
    try:
        # Fazer uma busca simples para ver a estrutura dos campos
        simple_params = {
            "range": "0-1"
        }
        
        # Testar Profile_User
        print("\n🔍 Estrutura dos campos Profile_User:")
        profile_user_response = glpi._make_authenticated_request(
            "GET", f"{glpi.glpi_url}/search/Profile_User", params=simple_params
        )
        
        if profile_user_response and profile_user_response.ok:
            profile_user_result = profile_user_response.json()
            if "data" in profile_user_result and profile_user_result["data"]:
                sample_profile_user = profile_user_result["data"][0]
                print("   Campos disponíveis:")
                for field_id, value in sample_profile_user.items():
                    print(f"     Campo {field_id}: {value}")
        
        # Testar User
        print("\n🔍 Estrutura dos campos User:")
        user_response = glpi._make_authenticated_request(
            "GET", f"{glpi.glpi_url}/search/User", params=simple_params
        )
        
        if user_response and user_response.ok:
            user_result = user_response.json()
            if "data" in user_result and user_result["data"]:
                sample_user = user_result["data"][0]
                print("   Campos disponíveis:")
                for field_id, value in sample_user.items():
                    print(f"     Campo {field_id}: {value}")
                    
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura dos campos: {e}")
    
    print("\n=== ANÁLISE E RECOMENDAÇÕES ===")
    print("\n🔍 Possíveis problemas identificados:")
    print("1. Perfil técnico pode não ser ID 6")
    print("2. Nenhum usuário ativo com perfil técnico")
    print("3. Estrutura dos campos pode ter mudado")
    print("4. Problemas de permissão na API")
    
    print("\n💡 Próximos passos:")
    print("1. Verificar qual é o ID correto do perfil técnico")
    print("2. Criar usuários com perfil técnico se necessário")
    print("3. Verificar permissões da API")
    print("4. Testar com diferentes campos de busca")

if __name__ == "__main__":
    debug_technicians_search()