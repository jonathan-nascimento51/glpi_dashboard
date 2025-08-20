#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.glpi_service import GLPIService
import logging

# Desabilitar logs para focar no debug
logging.disable(logging.CRITICAL)

def main():
    print("=== Debug Active Users ===")
    
    # Inicializar serviço GLPI
    glpi_service = GLPIService()
    
    print("\n1. Autenticando...")
    if not glpi_service.authenticate():
        print("❌ Falha na autenticação")
        return
    print("✅ Autenticação bem-sucedida")
    
    print("\n2. Buscando usuários ativos usando endpoint direto...")
    
    # Tentar busca direta sem parâmetros complexos
    try:
        response = glpi_service._make_authenticated_request(
            "GET", 
            f"{glpi_service.glpi_url}/User",
            params={"range": "0-10"}
        )
        
        if response and response.status_code == 200:
            users = response.json()
            print(f"✅ Encontrados {len(users)} usuários via endpoint direto")
            
            print("\n3. Analisando usuários encontrados...")
            for i, user in enumerate(users[:5]):
                print(f"\nUsuário {i+1}:")
                print(f"  ID: {user.get('id', 'N/A')}")
                print(f"  Name: {user.get('name', 'N/A')}")
                print(f"  Realname: {user.get('realname', 'N/A')}")
                print(f"  Firstname: {user.get('firstname', 'N/A')}")
                print(f"  Ativo: {user.get('is_active', 'N/A')}")
                print(f"  Deletado: {user.get('is_deleted', 'N/A')}")
                
                # Verificar se este usuário tem perfil de técnico
                user_id = user.get('id')
                if user_id:
                    print(f"  Verificando perfis do usuário {user_id}...")
                    
                    profile_params = {
                        "range": "0-10",
                        "criteria[0][field]": "3",  # users_id
                        "criteria[0][searchtype]": "equals",
                        "criteria[0][value]": str(user_id)
                    }
                    
                    profile_response = glpi_service._make_authenticated_request(
                        "GET", 
                        f"{glpi_service.glpi_url}/search/Profile_User",
                        params=profile_params
                    )
                    
                    if profile_response and profile_response.status_code == 200:
                        profile_data = profile_response.json()
                        profiles = profile_data.get('data', [])
                        print(f"    Perfis encontrados: {len(profiles)}")
                        for profile in profiles:
                            profile_id = profile.get('4', 'N/A')  # profiles_id
                            entity_id = profile.get('5', 'N/A')   # entities_id
                            print(f"      Profile ID: {profile_id}, Entity ID: {entity_id}")
                            if profile_id == '6':
                                print(f"      ✅ TÉCNICO ENCONTRADO!")
                    else:
                        print(f"    ❌ Erro ao buscar perfis: {profile_response.status_code if profile_response else 'None'}")
        
        elif response and response.status_code == 206:
            print("✅ Resposta parcial (206) - alguns usuários encontrados")
            try:
                users = response.json()
                print(f"Dados recebidos: {len(users) if isinstance(users, list) else 'não é lista'}")
                if isinstance(users, list) and len(users) > 0:
                    print(f"Primeiro usuário: {users[0]}")
            except Exception as e:
                print(f"Erro ao processar resposta: {e}")
        
        else:
            print(f"❌ Erro na busca direta: {response.status_code if response else 'None'}")
            if response:
                print(f"Resposta: {response.text[:500]}")
    
    except Exception as e:
        print(f"❌ Erro na busca direta: {e}")
    
    print("\n4. Testando busca por Profile_User para encontrar usuários ativos...")
    
    # Buscar Profile_User sem filtro de entidade para ver todos os técnicos
    try:
        profile_params = {
            "range": "0-20",
            "criteria[0][field]": "4",  # profiles_id
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": "6"  # Técnico
        }
        
        profile_response = glpi_service._make_authenticated_request(
            "GET", 
            f"{glpi_service.glpi_url}/search/Profile_User",
            params=profile_params
        )
        
        if profile_response and profile_response.status_code == 200:
            profile_data = profile_response.json()
            profiles = profile_data.get('data', [])
            print(f"✅ Encontrados {len(profiles)} registros Profile_User com perfil técnico")
            
            print("\n5. Verificando quais usuários ainda existem...")
            valid_users = []
            
            for i, profile in enumerate(profiles[:10]):
                user_id = profile.get('3', 'N/A')  # users_id
                username = profile.get('5', 'N/A')  # username
                entity_path = profile.get('80', 'N/A')  # entity path
                
                print(f"\nProfile {i+1}: User ID {user_id}, Username: {username}")
                print(f"  Entity: {entity_path}")
                
                # Tentar buscar este usuário específico
                try:
                    user_response = glpi_service._make_authenticated_request(
                        "GET", 
                        f"{glpi_service.glpi_url}/User/{user_id}"
                    )
                    
                    if user_response and user_response.status_code == 200:
                        user_data = user_response.json()
                        print(f"  ✅ Usuário existe! Nome: {user_data.get('name', 'N/A')}")
                        print(f"     Ativo: {user_data.get('is_active', 'N/A')}")
                        print(f"     Deletado: {user_data.get('is_deleted', 'N/A')}")
                        valid_users.append({
                            'id': user_id,
                            'username': username,
                            'name': user_data.get('name', 'N/A'),
                            'is_active': user_data.get('is_active', 0),
                            'entity_path': entity_path
                        })
                    else:
                        print(f"  ❌ Usuário não existe (404)")
                
                except Exception as e:
                    print(f"  ❌ Erro ao verificar usuário: {e}")
            
            print(f"\n6. Resumo: {len(valid_users)} usuários técnicos válidos encontrados")
            for user in valid_users:
                print(f"  - ID {user['id']}: {user['name']} ({user['username']}) - Ativo: {user['is_active']}")
        
        else:
            print(f"❌ Erro na busca Profile_User: {profile_response.status_code if profile_response else 'None'}")
    
    except Exception as e:
        print(f"❌ Erro na busca Profile_User: {e}")
    
    print("\n=== Fim do Debug ===")

if __name__ == "__main__":
    main()