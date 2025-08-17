#!/usr/bin/env python3
"""
Script para investigar o problema do ranking de técnicos
Por que apenas técnicos N2 e N3 aparecem no ranking?
"""

import os
import sys
import json
from dotenv import load_dotenv

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.glpi_service import GLPIService

def debug_technician_ranking():
    print("=== DEBUG: INVESTIGAÇÃO DO RANKING DE TÉCNICOS ===")
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    try:
        # Inicializar serviço GLPI
        service = GLPIService()
        
        # Garantir autenticação
        if not service._ensure_authenticated():
            print("❌ Falha na autenticação com GLPI")
            return
            
        print("✅ Autenticado com sucesso no GLPI")
        print(f"URL: {service.glpi_url}")
        print(f"Session Token: {service.session_token[:20]}...")
        
        print("\n📋 CONFIGURAÇÃO DOS GRUPOS (service_levels):")
        for level, group_id in service.service_levels.items():
            print(f"  - {level}: Grupo {group_id}")
        
        print("\n🔍 ETAPA 1: Buscar usuários com perfil de técnico (ID 6)")
        
        # Buscar usuários com perfil de técnico
        profile_params = {
            "range": "0-999",
            "criteria[0][field]": "4",  # Campo Perfil na tabela Profile_User
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
        
        if not response:
            print("❌ Falha ao buscar usuários com perfil de técnico")
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
        
        print(f"✅ Encontrados {len(technician_ids)} técnicos com perfil ID 6")
        print(f"IDs dos técnicos: {technician_ids}")
        
        print("\n🔍 ETAPA 2: Analisar cada técnico individualmente")
        
        technicians_by_level = {
            "N1": [],
            "N2": [],
            "N3": [],
            "N4": [],
            "Sem_Nivel": []
        }
        
        for tech_id in technician_ids:
            print(f"\n--- Analisando técnico ID: {tech_id} ---")
            
            # Obter nome do técnico
            tech_name = service._get_technician_name(tech_id)
            print(f"Nome: {tech_name}")
            
            # Determinar nível usando o método atual
            try:
                tech_id_int = int(tech_id)
                tech_level = service._get_technician_level(tech_id_int, 0)
                print(f"Nível determinado: {tech_level}")
                
                # Verificar grupos do técnico
                group_response = service._make_authenticated_request(
                    'GET',
                    f"{service.glpi_url}/search/Group_User",
                    params={
                        "range": "0-99",
                        "criteria[0][field]": "4",  # Campo users_id
                        "criteria[0][searchtype]": "equals",
                        "criteria[0][value]": str(tech_id),
                        "forcedisplay[0]": "3",  # groups_id
                        "forcedisplay[1]": "4",  # users_id
                    }
                )
                
                if group_response and group_response.ok:
                    group_data = group_response.json()
                    if group_data and group_data.get('data'):
                        groups = []
                        for group_entry in group_data['data']:
                            if "3" in group_entry:
                                groups.append(group_entry["3"])
                        print(f"Grupos do técnico: {groups}")
                        
                        # Verificar se está nos grupos N1-N4
                        n_groups = []
                        for level, group_id in service.service_levels.items():
                            if str(group_id) in groups or group_id in groups:
                                n_groups.append(level)
                        print(f"Grupos N1-N4 encontrados: {n_groups}")
                    else:
                        print("Nenhum grupo encontrado para este técnico")
                else:
                    print(f"Erro ao buscar grupos: {group_response.status_code if group_response else 'Sem resposta'}")
                
                # Contar tickets do técnico
                ticket_count = service._count_tickets_with_date_filter(tech_id, None, None)
                print(f"Total de tickets: {ticket_count}")
                
                # Adicionar à lista por nível
                technicians_by_level[tech_level].append({
                    'id': tech_id,
                    'name': tech_name,
                    'level': tech_level,
                    'tickets': ticket_count
                })
                
            except Exception as e:
                print(f"❌ Erro ao processar técnico {tech_id}: {e}")
                technicians_by_level["Sem_Nivel"].append({
                    'id': tech_id,
                    'name': tech_name,
                    'level': 'ERRO',
                    'tickets': 0
                })
        
        print("\n📊 RESUMO POR NÍVEL:")
        for level, techs in technicians_by_level.items():
            print(f"\n{level}: {len(techs)} técnicos")
            for tech in techs:
                print(f"  - {tech['name']} (ID: {tech['id']}) - {tech['tickets']} tickets")
        
        print("\n🔍 ETAPA 3: Testar método get_technician_ranking atual")
        
        try:
            ranking = service.get_technician_ranking()
            print(f"\n📈 RANKING ATUAL: {len(ranking)} técnicos")
            for i, tech in enumerate(ranking[:10]):  # Mostrar top 10
                print(f"  {i+1}. {tech.get('name', 'N/A')} - Nível: {tech.get('level', 'N/A')} - Tickets: {tech.get('total', 0)}")
        except Exception as e:
            print(f"❌ Erro ao obter ranking: {e}")
        
        print("\n🔍 ETAPA 4: Verificar se grupos N1-N4 existem no GLPI")
        
        for level, group_id in service.service_levels.items():
            try:
                group_response = service._make_authenticated_request(
                    'GET',
                    f"{service.glpi_url}/Group/{group_id}"
                )
                
                if group_response and group_response.ok:
                    group_info = group_response.json()
                    print(f"✅ {level} (ID {group_id}): {group_info.get('name', 'N/A')}")
                else:
                    print(f"❌ {level} (ID {group_id}): Grupo não encontrado ou erro {group_response.status_code if group_response else 'Sem resposta'}")
            except Exception as e:
                print(f"❌ {level} (ID {group_id}): Erro ao verificar - {e}")
        
        print("\n=== FIM DO DEBUG ===")
        
    except Exception as e:
        print(f"❌ Erro geral no debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_technician_ranking()