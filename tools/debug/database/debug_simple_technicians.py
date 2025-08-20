#!/usr/bin/env python3
"""
Script de debug simples para verificar técnicos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService
import logging

# Desabilitar logs detalhados
logging.getLogger().setLevel(logging.ERROR)

def debug_simple():
    print("=== DEBUG SIMPLES: TÉCNICOS ===")
    
    glpi = GLPIService()
    if not glpi._ensure_authenticated():
        print("❌ Falha na autenticação")
        return
    
    print("✅ Autenticado com sucesso")
    
    # Testar perfil 6 (técnico)
    print("\n🔍 Testando perfil ID 6:")
    profile_params = {
        "range": "0-5",
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
        
        print(f"Total usuários com perfil 6: {total}")
        
        if items:
            print("Estrutura dos dados:")
            for i, item in enumerate(items[:3]):
                print(f"  Item {i+1}: {item}")
                
                # Tentar diferentes campos para user_id
                user_id = None
                for field in ["3", "users_id", "2"]:
                    if field in item and item[field]:
                        user_id = str(item[field])
                        print(f"    User ID encontrado no campo {field}: {user_id}")
                        break
                
                if user_id and user_id.isdigit():
                    # Verificar dados do usuário
                    user_response = glpi._make_authenticated_request(
                        "GET", f"{glpi.glpi_url}/User/{user_id}"
                    )
                    
                    if user_response and user_response.ok:
                        user_data = user_response.json()
                        name = user_data.get("name", "N/A")
                        active = user_data.get("is_active", 0)
                        deleted = user_data.get("is_deleted", 0)
                        
                        print(f"    Nome: {name}, Ativo: {active}, Deletado: {deleted}")
                        
                        if active and not deleted:
                            print(f"    ✅ Técnico válido encontrado!")
                        else:
                            print(f"    ❌ Técnico inativo ou deletado")
    else:
        print(f"❌ Falha na busca: {response.status_code if response else 'No response'}")
    
    # Testar método direto
    print("\n🔍 Testando método _get_all_technician_ids_and_names():")
    tech_ids, tech_names = glpi._get_all_technician_ids_and_names()
    print(f"Resultado: {len(tech_ids)} técnicos encontrados")
    
    if tech_ids:
        print("Técnicos encontrados:")
        for tech_id in tech_ids[:5]:
            name = tech_names.get(tech_id, f"Técnico {tech_id}")
            print(f"  - ID: {tech_id}, Nome: {name}")
    else:
        print("❌ Nenhum técnico encontrado pelo método direto")

if __name__ == "__main__":
    debug_simple()