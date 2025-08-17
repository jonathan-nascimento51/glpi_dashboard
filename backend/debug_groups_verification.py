#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar se os grupos N1-N4 estão configurados corretamente no GLPI
e se os técnicos estão associados aos grupos corretos.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from services.glpi_service import GLPIService

def debug_groups_verification():
    print("🔍 VERIFICAÇÃO DOS GRUPOS N1-N4 NO GLPI")
    print("=" * 60)
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    try:
        # Inicializar serviço
        service = GLPIService()
        
        if not service._ensure_authenticated():
            print("❌ Falha na autenticação")
            return
        
        print("✅ Autenticado com sucesso")
        
        print("\n📋 ETAPA 1: Verificar se os grupos N1-N4 existem no GLPI")
        
        groups_status = {}
        for level, group_id in service.service_levels.items():
            try:
                response = service._make_authenticated_request(
                    'GET',
                    f"{service.glpi_url}/Group/{group_id}"
                )
                
                if response and response.ok:
                    group_data = response.json()
                    group_name = group_data.get('name', 'N/A')
                    groups_status[level] = {
                        'exists': True,
                        'name': group_name,
                        'id': group_id
                    }
                    print(f"  ✅ {level} (ID {group_id}): {group_name}")
                else:
                    groups_status[level] = {
                        'exists': False,
                        'name': None,
                        'id': group_id
                    }
                    status_code = response.status_code if response else 'Sem resposta'
                    print(f"  ❌ {level} (ID {group_id}): Grupo não encontrado (Status: {status_code})")
                    
            except Exception as e:
                groups_status[level] = {
                    'exists': False,
                    'name': None,
                    'id': group_id
                }
                print(f"  ❌ {level} (ID {group_id}): Erro - {e}")
        
        print("\n📋 ETAPA 2: Buscar técnicos com perfil ID 6")
        
        # Buscar usuários com perfil de técnico
        profile_params = {
            "range": "0-999",
            "criteria[0][field]": "4",  # Campo Perfil
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": "6",  # ID do perfil técnico
            "forcedisplay[0]": "2",  # ID do Profile_User
            "forcedisplay[1]": "5",  # Usuário (users_id)
            "forcedisplay[2]": "4",  # Perfil
            "forcedisplay[3]": "80"  # Entidade
        }
        
        response = service._make_authenticated_request(
            'GET',
            f"{service.glpi_url}/search/Profile_User",
            params=profile_params
        )
        
        if not response or not response.ok:
            print("❌ Falha ao buscar técnicos")
            return
        
        profile_result = response.json()
        
        if 'data' not in profile_result or not profile_result['data']:
            print("❌ Nenhum técnico encontrado")
            return
        
        # Extrair IDs dos técnicos
        technician_ids = []
        for item in profile_result['data']:
            if '5' in item:  # Campo users_id
                technician_ids.append(item['5'])
        
        print(f"✅ Encontrados {len(technician_ids)} técnicos")
        
        print("\n📋 ETAPA 3: Verificar grupos de cada técnico")
        
        technicians_by_group = {
            'N1': [],
            'N2': [],
            'N3': [],
            'N4': [],
            'SEM_GRUPO_N': [],
            'ERRO': []
        }
        
        for tech_id in technician_ids:
            try:
                # Obter nome do técnico
                user_response = service._make_authenticated_request(
                    'GET',
                    f"{service.glpi_url}/User/{tech_id}"
                )
                
                tech_name = "Desconhecido"
                if user_response and user_response.ok:
                    user_data = user_response.json()
                    if "realname" in user_data and "firstname" in user_data:
                        tech_name = f"{user_data['firstname']} {user_data['realname']}"
                    elif "realname" in user_data:
                        tech_name = user_data["realname"]
                    elif "name" in user_data:
                        tech_name = user_data["name"]
                
                # Buscar grupos do técnico
                groups_response = service._make_authenticated_request(
                    'GET',
                    f"{service.glpi_url}/search/Group_User",
                    params={
                        "range": "0-99",
                        "criteria[0][field]": "4",  # users_id
                        "criteria[0][searchtype]": "equals",
                        "criteria[0][value]": str(tech_id),
                        "forcedisplay[0]": "3",  # groups_id
                        "forcedisplay[1]": "4",  # users_id
                    }
                )
                
                tech_groups = []
                if groups_response and groups_response.ok:
                    groups_data = groups_response.json()
                    if groups_data and groups_data.get('data'):
                        for group_entry in groups_data['data']:
                            if "3" in group_entry:
                                tech_groups.append(int(group_entry["3"]))
                
                # Verificar se está em algum grupo N1-N4
                found_level = None
                for level, group_id in service.service_levels.items():
                    if group_id in tech_groups:
                        found_level = level
                        break
                
                tech_info = {
                    'id': tech_id,
                    'name': tech_name,
                    'groups': tech_groups
                }
                
                if found_level:
                    technicians_by_group[found_level].append(tech_info)
                    print(f"  ✅ {tech_name} (ID: {tech_id}) -> {found_level} (Grupos: {tech_groups})")
                else:
                    technicians_by_group['SEM_GRUPO_N'].append(tech_info)
                    print(f"  ⚠️  {tech_name} (ID: {tech_id}) -> SEM GRUPO N (Grupos: {tech_groups})")
                    
            except Exception as e:
                technicians_by_group['ERRO'].append({
                    'id': tech_id,
                    'name': 'Erro ao obter dados',
                    'groups': [],
                    'error': str(e)
                })
                print(f"  ❌ Erro ao processar técnico {tech_id}: {e}")
        
        print("\n📊 RESUMO POR GRUPO:")
        for level in ['N1', 'N2', 'N3', 'N4']:
            count = len(technicians_by_group[level])
            print(f"  {level}: {count} técnicos")
            for tech in technicians_by_group[level]:
                print(f"    - {tech['name']} (ID: {tech['id']})")
        
        sem_grupo_count = len(technicians_by_group['SEM_GRUPO_N'])
        print(f"  SEM GRUPO N: {sem_grupo_count} técnicos")
        for tech in technicians_by_group['SEM_GRUPO_N']:
            print(f"    - {tech['name']} (ID: {tech['id']}) - Grupos: {tech['groups']}")
        
        erro_count = len(technicians_by_group['ERRO'])
        if erro_count > 0:
            print(f"  ERRO: {erro_count} técnicos")
            for tech in technicians_by_group['ERRO']:
                print(f"    - ID: {tech['id']} - Erro: {tech['error']}")
        
        print("\n🎯 CONCLUSÕES:")
        
        # Verificar se todos os grupos existem
        missing_groups = [level for level, status in groups_status.items() if not status['exists']]
        if missing_groups:
            print(f"  ❌ Grupos não encontrados no GLPI: {', '.join(missing_groups)}")
        else:
            print("  ✅ Todos os grupos N1-N4 existem no GLPI")
        
        # Verificar distribuição
        total_with_groups = sum(len(technicians_by_group[level]) for level in ['N1', 'N2', 'N3', 'N4'])
        total_technicians = len(technician_ids)
        
        print(f"  📈 {total_with_groups}/{total_technicians} técnicos estão em grupos N1-N4")
        print(f"  📈 {sem_grupo_count} técnicos não estão em grupos N1-N4")
        
        if sem_grupo_count > 0:
            print("  ⚠️  Técnicos sem grupo N serão classificados pelo mapeamento hardcoded")
        
        print("\n=" * 60)
        print("✅ VERIFICAÇÃO CONCLUÍDA")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_groups_verification()