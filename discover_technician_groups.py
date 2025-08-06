#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para descobrir os grupos de atendimento dos técnicos no GLPI
e mapear para os níveis N1, N2, N3, N4
"""

import logging
from backend.services.glpi_service import GLPIService

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def discover_technician_groups():
    """Descobre os grupos de atendimento dos técnicos"""
    try:
        # Inicializar serviço GLPI
        service = GLPIService()
        
        print("=== DESCOBERTA DOS GRUPOS DE ATENDIMENTO DOS TÉCNICOS ===")
        print(f"Service levels configurados: {service.service_levels}")
        print()
        
        # 1. Primeiro, vamos listar TODOS os grupos disponíveis no GLPI
        print("1. LISTANDO TODOS OS GRUPOS DISPONÍVEIS NO GLPI:")
        print("-" * 60)
        
        try:
            response = service._make_authenticated_request(
                'GET',
                f"{service.glpi_url}/Group",
                params={
                    "range": "0-200",
                    "is_deleted": 0
                }
            )
            
            if response and response.ok:
                groups_data = response.json()
                print(f"Total de grupos encontrados: {len(groups_data)}")
                
                # Listar grupos que podem ser relacionados a níveis de atendimento
                relevant_groups = []
                for group in groups_data:
                    if isinstance(group, dict):
                        group_id = group.get('id')
                        group_name = group.get('name', '').lower()
                        
                        # Procurar por grupos que contenham palavras relacionadas a níveis
                        keywords = ['n1', 'n2', 'n3', 'n4', 'nivel', 'nível', 'atendimento', 'suporte', 'tecnico', 'técnico']
                        if any(keyword in group_name for keyword in keywords):
                            relevant_groups.append({
                                'id': group_id,
                                'name': group.get('name', ''),
                                'comment': group.get('comment', '')
                            })
                            print(f"  ID {group_id}: {group.get('name', '')} - {group.get('comment', '')}")
                
                if not relevant_groups:
                    print("  Nenhum grupo relacionado a níveis encontrado pelos keywords.")
                    print("  Listando os primeiros 20 grupos para análise manual:")
                    for i, group in enumerate(groups_data[:20]):
                        if isinstance(group, dict):
                            print(f"  ID {group.get('id')}: {group.get('name', '')} - {group.get('comment', '')}")
                
            else:
                print(f"Erro ao buscar grupos: {response.status_code if response else 'Sem resposta'}")
                
        except Exception as e:
            print(f"Erro ao listar grupos: {e}")
        
        print("\n" + "="*80 + "\n")
        
        # 2. Obter ranking de técnicos atual
        print("2. OBTENDO TÉCNICOS ATIVOS:")
        print("-" * 30)
        
        ranking = service.get_technician_ranking()
        
        if not ranking:
            print("Nenhum técnico encontrado no ranking")
            return
        
        print(f"Encontrados {len(ranking)} técnicos ativos")
        print()
        
        # 3. Para cada técnico, descobrir seus grupos
        print("3. DESCOBRINDO GRUPOS DE CADA TÉCNICO:")
        print("-" * 40)
        
        technician_groups = {}
        
        for tech in ranking:
            user_id = int(tech['id'])
            tech_name = tech['name']
            
            print(f"\nTécnico: {tech_name} (ID: {user_id})")
            
            try:
                # Buscar grupos do usuário
                response = service._make_authenticated_request(
                    'GET',
                    f"{service.glpi_url}/search/Group_User",
                    params={
                        "range": "0-99",
                        "criteria[0][field]": "4",  # Campo users_id
                        "criteria[0][searchtype]": "equals",
                        "criteria[0][value]": str(user_id),
                        "forcedisplay[0]": "3",  # groups_id
                        "forcedisplay[1]": "4"   # users_id
                    }
                )
                
                if response and response.ok:
                    group_data = response.json()
                    total_groups = group_data.get('totalcount', 0)
                    
                    if total_groups > 0 and group_data.get('data'):
                        user_groups = []
                        for group_entry in group_data['data']:
                            if isinstance(group_entry, dict) and "3" in group_entry:
                                group_id = int(group_entry["3"])
                                user_groups.append(group_id)
                        
                        technician_groups[user_id] = {
                            'name': tech_name,
                            'groups': user_groups
                        }
                        
                        print(f"  Grupos encontrados: {user_groups}")
                        
                        # Verificar se algum grupo corresponde aos service_levels
                        matched_levels = []
                        for level, level_group_id in service.service_levels.items():
                            if level_group_id in user_groups:
                                matched_levels.append(level)
                        
                        if matched_levels:
                            print(f"  ✅ MATCH! Níveis encontrados: {matched_levels}")
                        else:
                            print(f"  ❌ Nenhum grupo corresponde aos service_levels configurados")
                    else:
                        print(f"  Nenhum grupo encontrado")
                        technician_groups[user_id] = {
                            'name': tech_name,
                            'groups': []
                        }
                else:
                    print(f"  Erro na busca: {response.status_code if response else 'Sem resposta'}")
                    
            except Exception as e:
                print(f"  Erro ao buscar grupos: {e}")
        
        print("\n" + "="*80 + "\n")
        
        # 4. Análise e recomendações
        print("4. ANÁLISE E RECOMENDAÇÕES:")
        print("-" * 30)
        
        # Contar técnicos por grupo
        group_usage = {}
        for tech_data in technician_groups.values():
            for group_id in tech_data['groups']:
                group_usage[group_id] = group_usage.get(group_id, 0) + 1
        
        print("Grupos mais utilizados pelos técnicos:")
        for group_id, count in sorted(group_usage.items(), key=lambda x: x[1], reverse=True):
            print(f"  Grupo ID {group_id}: {count} técnicos")
        
        # Verificar se os service_levels estão sendo usados
        print(f"\nVerificação dos service_levels configurados:")
        for level, group_id in service.service_levels.items():
            count = group_usage.get(group_id, 0)
            print(f"  {level} (Grupo {group_id}): {count} técnicos")
        
        # Sugestões
        print("\n📋 SUGESTÕES:")
        
        if not any(group_usage.get(group_id, 0) > 0 for group_id in service.service_levels.values()):
            print("❌ Os grupos configurados nos service_levels não estão sendo utilizados!")
            print("\n🔧 OPÇÕES DE CORREÇÃO:")
            print("\n1. ATUALIZAR service_levels com grupos realmente utilizados:")
            
            # Sugerir grupos baseado no uso
            most_used_groups = sorted(group_usage.items(), key=lambda x: x[1], reverse=True)[:4]
            suggested_levels = ['N4', 'N3', 'N2', 'N1']
            
            print("   service_levels = {")
            for i, (group_id, count) in enumerate(most_used_groups):
                if i < len(suggested_levels):
                    print(f"       '{suggested_levels[i]}': {group_id},  # {count} técnicos")
            print("   }")
            
            print("\n2. OU configurar os técnicos nos grupos N1-N4 no GLPI")
            print("\n3. OU usar distribuição por performance (implementação atual)")
        else:
            print("✅ Alguns grupos dos service_levels estão sendo utilizados!")
            print("A implementação pode usar os grupos reais do GLPI.")
        
        # Salvar resultados em arquivo
        with open('technician_groups_analysis.txt', 'w', encoding='utf-8') as f:
            f.write("=== ANÁLISE DOS GRUPOS DE TÉCNICOS ===\n\n")
            f.write(f"Service levels configurados: {service.service_levels}\n\n")
            
            f.write("TÉCNICOS E SEUS GRUPOS:\n")
            for user_id, data in technician_groups.items():
                f.write(f"{data['name']} (ID: {user_id}): {data['groups']}\n")
            
            f.write("\nGRUPOS MAIS UTILIZADOS:\n")
            for group_id, count in sorted(group_usage.items(), key=lambda x: x[1], reverse=True):
                f.write(f"Grupo ID {group_id}: {count} técnicos\n")
        
        print(f"\n💾 Resultados salvos em: technician_groups_analysis.txt")
        
        service.close_session()
        
    except Exception as e:
        logger.error(f"Erro na descoberta: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    discover_technician_groups()