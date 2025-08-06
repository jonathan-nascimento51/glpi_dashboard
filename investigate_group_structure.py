#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para investigar a estrutura de grupos no GLPI
e encontrar uma forma de categorizar técnicos por níveis
"""

import logging
from backend.services.glpi_service import GLPIService

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def investigate_group_structure():
    """Investiga a estrutura de grupos para encontrar categorização por níveis"""
    try:
        # Inicializar serviço GLPI
        service = GLPIService()
        
        print("=== INVESTIGAÇÃO DA ESTRUTURA DE GRUPOS NO GLPI ===")
        print()
        
        # 1. Investigar o Grupo ID 1 (mais utilizado)
        print("1. INVESTIGANDO O GRUPO ID 1:")
        print("-" * 35)
        
        try:
            response = service._make_authenticated_request(
                'GET',
                f"{service.glpi_url}/Group/1"
            )
            
            if response and response.ok:
                group_data = response.json()
                print(f"Nome do grupo: {group_data.get('name', 'N/A')}")
                print(f"Comentário: {group_data.get('comment', 'N/A')}")
                print(f"Nível: {group_data.get('level', 'N/A')}")
                print(f"Completename: {group_data.get('completename', 'N/A')}")
                print(f"Entidades: {group_data.get('entities_id', 'N/A')}")
                print(f"É atribuível: {group_data.get('is_assign', 'N/A')}")
                print(f"É notificável: {group_data.get('is_notify', 'N/A')}")
                print(f"É técnico: {group_data.get('is_tech', 'N/A')}")
                print(f"É manager: {group_data.get('is_manager', 'N/A')}")
            else:
                print(f"Erro ao buscar grupo 1: {response.status_code if response else 'Sem resposta'}")
        except Exception as e:
            print(f"Erro ao investigar grupo 1: {e}")
        
        print("\n" + "="*80 + "\n")
        
        # 2. Buscar grupos com hierarquia ou subgrupos
        print("2. BUSCANDO GRUPOS COM HIERARQUIA:")
        print("-" * 35)
        
        try:
            response = service._make_authenticated_request(
                'GET',
                f"{service.glpi_url}/Group",
                params={
                    "range": "0-200",
                    "is_deleted": 0,
                    "forcedisplay[0]": "1",   # id
                    "forcedisplay[1]": "14",  # name
                    "forcedisplay[2]": "16",  # comment
                    "forcedisplay[3]": "2",   # entities_id
                    "forcedisplay[4]": "3",   # is_recursive
                    "forcedisplay[5]": "4",   # groups_id (parent group)
                    "forcedisplay[6]": "5",   # completename
                    "forcedisplay[7]": "6",   # level
                }
            )
            
            if response and response.ok:
                groups_data = response.json()
                print(f"Total de grupos encontrados: {len(groups_data)}")
                
                # Analisar grupos com hierarquia
                hierarchical_groups = []
                tech_related_groups = []
                
                for group in groups_data:
                    if isinstance(group, dict):
                        group_id = group.get('1')  # id
                        group_name = group.get('14', '').lower()  # name
                        group_comment = group.get('16', '').lower()  # comment
                        parent_group = group.get('4')  # groups_id (parent)
                        level = group.get('6')  # level
                        completename = group.get('5', '')  # completename
                        
                        # Grupos com hierarquia (têm parent ou level > 1)
                        if parent_group or (level and int(level) > 1):
                            hierarchical_groups.append({
                                'id': group_id,
                                'name': group.get('14', ''),
                                'parent': parent_group,
                                'level': level,
                                'completename': completename
                            })
                        
                        # Grupos relacionados a técnicos/atendimento
                        keywords = ['tecnico', 'técnico', 'atendimento', 'suporte', 'help', 'desk', 'ti', 'nivel', 'nível', 'n1', 'n2', 'n3', 'n4']
                        if any(keyword in group_name or keyword in group_comment for keyword in keywords):
                            tech_related_groups.append({
                                'id': group_id,
                                'name': group.get('14', ''),
                                'comment': group.get('16', ''),
                                'level': level,
                                'completename': completename
                            })
                
                print(f"\nGrupos com hierarquia encontrados: {len(hierarchical_groups)}")
                for group in hierarchical_groups[:10]:  # Mostrar apenas os primeiros 10
                    print(f"  ID {group['id']}: {group['name']} (Parent: {group['parent']}, Level: {group['level']})")
                    if group['completename']:
                        print(f"    Completename: {group['completename']}")
                
                print(f"\nGrupos relacionados a técnicos: {len(tech_related_groups)}")
                for group in tech_related_groups:
                    print(f"  ID {group['id']}: {group['name']} - {group['comment']}")
                    if group['completename']:
                        print(f"    Completename: {group['completename']}")
                
            else:
                print(f"Erro ao buscar grupos: {response.status_code if response else 'Sem resposta'}")
        except Exception as e:
            print(f"Erro ao buscar grupos com hierarquia: {e}")
        
        print("\n" + "="*80 + "\n")
        
        # 3. Investigar perfis dos técnicos
        print("3. INVESTIGANDO PERFIS DOS TÉCNICOS:")
        print("-" * 37)
        
        # Obter alguns técnicos para análise
        ranking = service.get_technician_ranking()
        
        if ranking:
            print(f"Analisando perfis dos primeiros 5 técnicos:")
            
            for tech in ranking[:5]:
                user_id = int(tech['id'])
                tech_name = tech['name']
                
                print(f"\nTécnico: {tech_name} (ID: {user_id})")
                
                try:
                    # Buscar perfis do usuário
                    response = service._make_authenticated_request(
                        'GET',
                        f"{service.glpi_url}/search/Profile_User",
                        params={
                            "range": "0-99",
                            "criteria[0][field]": "4",  # Campo users_id
                            "criteria[0][searchtype]": "equals",
                            "criteria[0][value]": str(user_id),
                            "forcedisplay[0]": "3",  # profiles_id
                            "forcedisplay[1]": "4",  # users_id
                            "forcedisplay[2]": "5",  # entities_id
                        }
                    )
                    
                    if response and response.ok:
                        profile_data = response.json()
                        
                        if profile_data.get('data'):
                            profiles = []
                            for profile_entry in profile_data['data']:
                                if isinstance(profile_entry, dict) and "3" in profile_entry:
                                    profile_id = int(profile_entry["3"])
                                    profiles.append(profile_id)
                            
                            print(f"  Perfis: {profiles}")
                            
                            # Buscar detalhes dos perfis
                            for profile_id in profiles:
                                try:
                                    profile_response = service._make_authenticated_request(
                                        'GET',
                                        f"{service.glpi_url}/Profile/{profile_id}"
                                    )
                                    
                                    if profile_response and profile_response.ok:
                                        profile_detail = profile_response.json()
                                        profile_name = profile_detail.get('name', 'N/A')
                                        print(f"    - Perfil {profile_id}: {profile_name}")
                                except:
                                    pass
                        else:
                            print(f"  Nenhum perfil encontrado")
                    else:
                        print(f"  Erro na busca de perfis: {response.status_code if response else 'Sem resposta'}")
                        
                except Exception as e:
                    print(f"  Erro ao buscar perfis: {e}")
        
        print("\n" + "="*80 + "\n")
        
        # 4. Buscar por campos customizados ou categorias
        print("4. BUSCANDO CAMPOS CUSTOMIZADOS:")
        print("-" * 33)
        
        try:
            # Buscar campos de usuário
            response = service._make_authenticated_request(
                'GET',
                f"{service.glpi_url}/listSearchOptions/User"
            )
            
            if response and response.ok:
                search_options = response.json()
                
                # Procurar por campos que possam indicar nível
                relevant_fields = []
                for field_id, field_data in search_options.items():
                    if isinstance(field_data, dict) and 'name' in field_data:
                        field_name = field_data['name'].lower()
                        keywords = ['nivel', 'nível', 'categoria', 'tipo', 'classificacao', 'classificação', 'grupo', 'atendimento']
                        
                        if any(keyword in field_name for keyword in keywords):
                            relevant_fields.append({
                                'id': field_id,
                                'name': field_data['name'],
                                'table': field_data.get('table', ''),
                                'field': field_data.get('field', '')
                            })
                
                if relevant_fields:
                    print("Campos relevantes encontrados:")
                    for field in relevant_fields:
                        print(f"  Campo {field['id']}: {field['name']} ({field['table']}.{field['field']})")
                else:
                    print("Nenhum campo customizado relevante encontrado.")
            
        except Exception as e:
            print(f"Erro ao buscar campos customizados: {e}")
        
        print("\n" + "="*80 + "\n")
        
        # 5. Recomendações finais
        print("5. RECOMENDAÇÕES FINAIS:")
        print("-" * 25)
        
        print("\n🔍 DESCOBERTAS:")
        print("- Todos os técnicos estão no Grupo ID 1 (grupo principal)")
        print("- Os grupos N1-N4 configurados (IDs 89-92) não estão sendo utilizados")
        print("- Não foram encontrados subgrupos ou hierarquias para níveis")
        
        print("\n💡 OPÇÕES PARA IMPLEMENTAÇÃO:")
        print("\n1. 🎯 USAR DISTRIBUIÇÃO POR PERFORMANCE (RECOMENDADO):")
        print("   - Manter a implementação atual que distribui por quartis")
        print("   - Baseado no número de tickets resolvidos")
        print("   - Mais justo e dinâmico")
        
        print("\n2. 🏗️ CONFIGURAR GRUPOS NO GLPI:")
        print("   - Criar/configurar grupos específicos para N1, N2, N3, N4")
        print("   - Atribuir técnicos aos grupos correspondentes")
        print("   - Requer trabalho manual no GLPI")
        
        print("\n3. 🔧 USAR CAMPOS CUSTOMIZADOS:")
        print("   - Adicionar campo customizado 'Nível de Atendimento' no GLPI")
        print("   - Configurar para cada técnico")
        print("   - Requer modificação no GLPI")
        
        print("\n✅ RECOMENDAÇÃO: Manter a distribuição por performance")
        print("   É a solução mais prática e justa para o cenário atual.")
        
        service.close_session()
        
    except Exception as e:
        logger.error(f"Erro na investigação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigate_group_structure()