#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from backend.services.glpi_service import GLPIService
import json

def list_all_groups():
    """Lista todos os grupos existentes no GLPI"""
    glpi = GLPIService()
    
    print("=== LISTANDO TODOS OS GRUPOS DO GLPI ===")
    
    # Verificar se consegue autenticar
    if not glpi._ensure_authenticated():
        print("❌ Falha na autenticação")
        return
    
    print("✅ Autenticação OK")
    
    try:
        # Buscar todos os grupos
        response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/Group",
            params={
                "range": "0-999",
                "is_deleted": "0"
            }
        )
        
        if response and response.ok:
            groups = response.json()
            
            print(f"\nTotal de grupos encontrados: {len(groups)}")
            print("\n--- LISTA DE GRUPOS ---")
            
            # Ordenar grupos por ID
            if isinstance(groups, list):
                groups.sort(key=lambda x: x.get('id', 0) if isinstance(x, dict) else 0)
                
                for group in groups:
                    if isinstance(group, dict):
                        group_id = group.get('id', 'N/A')
                        group_name = group.get('name', 'Sem nome')
                        group_comment = group.get('comment', '')
                        
                        print(f"ID: {group_id:3} | Nome: {group_name}")
                        if group_comment:
                            print(f"         | Comentário: {group_comment}")
                        
                        # Destacar se é um dos grupos configurados como service_levels
                        if group_id in glpi.service_levels.values():
                            level_name = [k for k, v in glpi.service_levels.items() if v == group_id][0]
                            print(f"         | ⭐ CONFIGURADO COMO: {level_name}")
                        
                        print()
            else:
                print(f"Formato inesperado de resposta: {type(groups)}")
                
        else:
            print(f"❌ Erro ao buscar grupos: {response.status_code if response else 'No response'}")
            if response:
                print(f"Resposta: {response.text[:500]}")
                
    except Exception as e:
        print(f"❌ Erro ao listar grupos: {e}")
    
    # Também verificar se há usuários em grupos com nomes relacionados à DTIC
    print("\n--- BUSCANDO GRUPOS COM 'DTIC' NO NOME ---")
    try:
        response = glpi._make_authenticated_request(
            'GET',
            f"{glpi.glpi_url}/search/Group",
            params={
                "range": "0-999",
                "criteria[0][field]": "1",  # Campo name
                "criteria[0][searchtype]": "contains",
                "criteria[0][value]": "DTIC",
                "forcedisplay[0]": "1",  # ID
                "forcedisplay[1]": "2",  # Nome
            }
        )
        
        if response and response.ok:
            dtic_groups = response.json()
            groups_data = dtic_groups.get('data', [])
            
            if groups_data:
                print(f"Grupos com 'DTIC' encontrados: {len(groups_data)}")
                for group in groups_data:
                    if isinstance(group, dict):
                        group_id = group.get('1', 'N/A')
                        group_name = group.get('2', 'N/A')
                        print(f"  - ID: {group_id} | Nome: {group_name}")
            else:
                print("Nenhum grupo com 'DTIC' no nome encontrado")
        else:
            print(f"❌ Erro ao buscar grupos DTIC: {response.status_code if response else 'No response'}")
            
    except Exception as e:
        print(f"❌ Erro ao buscar grupos DTIC: {e}")

if __name__ == "__main__":
    list_all_groups()