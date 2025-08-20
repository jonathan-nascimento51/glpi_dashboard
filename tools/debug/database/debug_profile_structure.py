#!/usr/bin/env python3
"""
Script para investigar a estrutura correta dos dados Profile_User
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService
import logging
import json

# Desabilitar logs detalhados
logging.getLogger().setLevel(logging.ERROR)

def debug_profile_structure():
    print("=== DEBUG: ESTRUTURA PROFILE_USER ===")
    
    glpi = GLPIService()
    if not glpi._ensure_authenticated():
        print("❌ Falha na autenticação")
        return
    
    print("✅ Autenticado com sucesso")
    
    # Buscar Profile_User com perfil técnico
    print("\n🔍 Buscando Profile_User com perfil 6:")
    profile_params = {
        "range": "0-10",
        "criteria[0][field]": "4",
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": "6",
    }
    
    response = glpi._make_authenticated_request(
        "GET", f"{glpi.glpi_url}/search/Profile_User", params=profile_params
    )
    
    if response and response.ok:
        data = response.json()
        total = data.get("totalcount", 0)
        items = data.get("data", [])
        
        print(f"Total: {total}")
        print(f"Itens retornados: {len(items)}")
        
        if items:
            print("\nEstrutura completa dos primeiros itens:")
            for i, item in enumerate(items[:3]):
                print(f"\nItem {i+1}:")
                print(json.dumps(item, indent=2, ensure_ascii=False))
                
                # Tentar obter o Profile_User diretamente pelo ID
                # Vamos tentar usar o campo "2" como ID do Profile_User
                if "2" in item:
                    profile_user_id = item["2"]
                    print(f"\nTentando buscar Profile_User ID {profile_user_id}:")
                    
                    detail_response = glpi._make_authenticated_request(
                        "GET", f"{glpi.glpi_url}/Profile_User/{profile_user_id}"
                    )
                    
                    if detail_response and detail_response.ok:
                        detail_data = detail_response.json()
                        print("Dados detalhados do Profile_User:")
                        print(json.dumps(detail_data, indent=2, ensure_ascii=False))
                        
                        # Verificar se tem users_id
                        if "users_id" in detail_data:
                            user_id = detail_data["users_id"]
                            print(f"\n✅ User ID encontrado: {user_id}")
                            
                            # Buscar dados do usuário
                            user_response = glpi._make_authenticated_request(
                                "GET", f"{glpi.glpi_url}/User/{user_id}"
                            )
                            
                            if user_response and user_response.ok:
                                user_data = user_response.json()
                                name = user_data.get("name", "N/A")
                                active = user_data.get("is_active", 0)
                                deleted = user_data.get("is_deleted", 0)
                                firstname = user_data.get("firstname", "")
                                realname = user_data.get("realname", "")
                                
                                print(f"Nome: {name}")
                                print(f"Nome completo: {firstname} {realname}")
                                print(f"Ativo: {active}, Deletado: {deleted}")
                                
                                if active and not deleted:
                                    print("✅ Este é um técnico válido!")
                                else:
                                    print("❌ Técnico inativo ou deletado")
                            else:
                                print(f"❌ Falha ao buscar usuário {user_id}")
                        else:
                            print("❌ Campo users_id não encontrado nos dados detalhados")
                    else:
                        print(f"❌ Falha ao buscar detalhes do Profile_User {profile_user_id}")
    else:
        print(f"❌ Falha na busca: {response.status_code if response else 'No response'}")
    
    # Testar busca sem filtros para ver a estrutura geral
    print("\n\n🔍 Buscando Profile_User sem filtros (para ver estrutura):")
    simple_params = {
        "range": "0-3"
    }
    
    response2 = glpi._make_authenticated_request(
        "GET", f"{glpi.glpi_url}/search/Profile_User", params=simple_params
    )
    
    if response2 and response2.ok:
        data2 = response2.json()
        items2 = data2.get("data", [])
        
        if items2:
            print("\nEstrutura geral dos Profile_User:")
            for i, item in enumerate(items2[:2]):
                print(f"\nItem {i+1}:")
                print(json.dumps(item, indent=2, ensure_ascii=False))
    
    print("\n=== ANÁLISE ===")
    print("\nO problema parece estar na estrutura dos dados retornados pela busca.")
    print("A busca Profile_User não está retornando o campo users_id diretamente.")
    print("É necessário buscar os detalhes completos de cada Profile_User para obter o users_id.")

if __name__ == "__main__":
    debug_profile_structure()