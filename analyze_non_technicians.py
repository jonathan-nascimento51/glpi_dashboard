#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para analisar os servidores que não deveriam estar no ranking de técnicos
Identifica características comuns para refinar a busca
"""

import requests
import json
from datetime import datetime
import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.glpi_service import GLPIService

def get_current_ranking():
    """Obtém o ranking atual"""
    try:
        response = requests.get('http://localhost:5000/api/technicians/ranking')
        if response.status_code == 200:
            return response.json()['data']
        else:
            print(f"Erro ao obter ranking: {response.status_code}")
            return None
    except Exception as e:
        print(f"Erro na requisição: {e}")
        return None

def analyze_user_details(service, user_id):
    """Analisa detalhes de um usuário específico"""
    try:
        # Buscar dados básicos do usuário
        user_response = service._make_authenticated_request('GET', f"{service.glpi_url}/User/{user_id}")
        if not user_response or user_response.status_code != 200:
            return None
        
        user_data = user_response.json()
        
        # Buscar grupos do usuário
        groups_response = service._make_authenticated_request(
            'GET',
            f"{service.glpi_url}/search/Group_User",
            params={
                'criteria[0][field]': 4,  # users_id
                'criteria[0][searchtype]': 'equals',
                'criteria[0][value]': user_id,
                'forcedisplay[0]': 2,  # groups_id
                'forcedisplay[1]': 4,  # users_id
            }
        )
        
        groups = []
        if groups_response and groups_response.status_code == 200:
            groups_data = groups_response.json()
            if 'data' in groups_data:
                for group_rel in groups_data['data']:
                    group_id = group_rel.get('2')  # groups_id
                    if group_id:
                        # Buscar nome do grupo
                        group_response = service._make_authenticated_request('GET', f"{service.glpi_url}/Group/{group_id}")
                        if group_response and group_response.status_code == 200:
                            group_info = group_response.json()
                            groups.append({
                                'id': group_id,
                                'name': group_info.get('name', 'N/A')
                            })
        
        # Buscar perfis do usuário
        profiles_response = service._make_authenticated_request(
            'GET',
            f"{service.glpi_url}/search/Profile_User",
            params={
                'criteria[0][field]': 4,  # users_id
                'criteria[0][searchtype]': 'equals',
                'criteria[0][value]': user_id,
                'forcedisplay[0]': 5,  # profiles_id
                'forcedisplay[1]': 4,  # users_id
            }
        )
        
        profiles = []
        if profiles_response and profiles_response.status_code == 200:
            profiles_data = profiles_response.json()
            if 'data' in profiles_data:
                for profile_rel in profiles_data['data']:
                    profile_id = profile_rel.get('5')  # profiles_id
                    if profile_id:
                        # Buscar nome do perfil
                        profile_response = service._make_authenticated_request('GET', f"{service.glpi_url}/Profile/{profile_id}")
                        if profile_response and profile_response.status_code == 200:
                            profile_info = profile_response.json()
                            profiles.append({
                                'id': profile_id,
                                'name': profile_info.get('name', 'N/A')
                            })
        
        return {
            'user_data': user_data,
            'groups': groups,
            'profiles': profiles
        }
        
    except Exception as e:
        print(f"Erro ao analisar usuário {user_id}: {e}")
        return None

def main():
    """Função principal"""
    print("🔍 ANÁLISE DOS SERVIDORES QUE NÃO DEVERIAM ESTAR NO RANKING")
    print("=" * 70)
    print(f"⏰ Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Obter ranking atual
    ranking = get_current_ranking()
    if not ranking:
        print("❌ Não foi possível obter o ranking")
        return False
    
    print(f"📊 Total de pessoas no ranking: {len(ranking)}")
    print()
    
    # Identificar os servidores problemáticos (posições 17, 19-27)
    problematic_positions = [17, 19, 20, 21, 22, 23, 24, 25, 26, 27]
    problematic_users = []
    
    print("👥 SERVIDORES IDENTIFICADOS COMO PROBLEMÁTICOS:")
    print("-" * 50)
    
    for pos in problematic_positions:
        if pos <= len(ranking):
            user = ranking[pos - 1]  # Ajustar para índice 0
            problematic_users.append(user)
            print(f"{pos:2d}. {user['name']} (ID: {user['id']}) - Score: {user['score']}")
    
    print()
    
    # Analisar detalhes dos usuários problemáticos
    service = GLPIService()
    
    print("🔍 ANÁLISE DETALHADA DOS USUÁRIOS PROBLEMÁTICOS:")
    print("=" * 70)
    
    all_groups = set()
    all_profiles = set()
    user_details = []
    
    for user in problematic_users:
        print(f"\n👤 {user['name']} (ID: {user['id']})")
        print("-" * 40)
        
        details = analyze_user_details(service, user['id'])
        if details:
            user_details.append({
                'user': user,
                'details': details
            })
            
            # Informações básicas
            user_data = details['user_data']
            print(f"   Nome real: {user_data.get('realname', 'N/A')}")
            print(f"   Primeiro nome: {user_data.get('firstname', 'N/A')}")
            print(f"   Email: {user_data.get('email', 'N/A')}")
            print(f"   Ativo: {user_data.get('is_active', 'N/A')}")
            print(f"   Deletado: {user_data.get('is_deleted', 'N/A')}")
            
            # Grupos
            print(f"   Grupos ({len(details['groups'])}):")            
            for group in details['groups']:
                print(f"      - {group['name']} (ID: {group['id']})")
                all_groups.add(group['name'])
            
            # Perfis
            print(f"   Perfis ({len(details['profiles'])}):")            
            for profile in details['profiles']:
                print(f"      - {profile['name']} (ID: {profile['id']})")
                all_profiles.add(profile['name'])
        else:
            print("   ❌ Não foi possível obter detalhes")
    
    # Análise de padrões
    print("\n\n📊 ANÁLISE DE PADRÕES COMUNS:")
    print("=" * 50)
    
    print(f"\n🏢 Grupos únicos encontrados ({len(all_groups)}):")
    for group in sorted(all_groups):
        count = sum(1 for ud in user_details 
                   if any(g['name'] == group for g in ud['details']['groups']))
        print(f"   - {group} ({count} usuários)")
    
    print(f"\n👤 Perfis únicos encontrados ({len(all_profiles)}):")
    for profile in sorted(all_profiles):
        count = sum(1 for ud in user_details 
                   if any(p['name'] == profile for p in ud['details']['profiles']))
        print(f"   - {profile} ({count} usuários)")
    
    # Comparar com técnicos legítimos (top 10)
    print("\n\n🔍 COMPARAÇÃO COM TÉCNICOS LEGÍTIMOS (TOP 10):")
    print("=" * 60)
    
    legitimate_techs = ranking[:10]
    legitimate_groups = set()
    legitimate_profiles = set()
    
    print("\n👥 Analisando técnicos legítimos...")
    for user in legitimate_techs[:5]:  # Analisar apenas os 5 primeiros para economizar tempo
        print(f"   Analisando: {user['name']}")
        details = analyze_user_details(service, user['id'])
        if details:
            for group in details['groups']:
                legitimate_groups.add(group['name'])
            for profile in details['profiles']:
                legitimate_profiles.add(profile['name'])
    
    print(f"\n🏢 Grupos dos técnicos legítimos ({len(legitimate_groups)}):")
    for group in sorted(legitimate_groups):
        print(f"   - {group}")
    
    print(f"\n👤 Perfis dos técnicos legítimos ({len(legitimate_profiles)}):")
    for profile in sorted(legitimate_profiles):
        print(f"   - {profile}")
    
    # Identificar diferenças
    print("\n\n🎯 DIFERENÇAS IDENTIFICADAS:")
    print("=" * 40)
    
    # Grupos exclusivos dos problemáticos
    problematic_only_groups = all_groups - legitimate_groups
    if problematic_only_groups:
        print(f"\n❌ Grupos APENAS dos problemáticos ({len(problematic_only_groups)}):")
        for group in sorted(problematic_only_groups):
            print(f"   - {group}")
    
    # Perfis exclusivos dos problemáticos
    problematic_only_profiles = all_profiles - legitimate_profiles
    if problematic_only_profiles:
        print(f"\n❌ Perfis APENAS dos problemáticos ({len(problematic_only_profiles)}):")
        for profile in sorted(problematic_only_profiles):
            print(f"   - {profile}")
    
    # Grupos comuns
    common_groups = all_groups & legitimate_groups
    if common_groups:
        print(f"\n✅ Grupos COMUNS ({len(common_groups)}):")
        for group in sorted(common_groups):
            print(f"   - {group}")
    
    # Perfis comuns
    common_profiles = all_profiles & legitimate_profiles
    if common_profiles:
        print(f"\n✅ Perfis COMUNS ({len(common_profiles)}):")
        for profile in sorted(common_profiles):
            print(f"   - {profile}")
    
    # Recomendações
    print("\n\n💡 RECOMENDAÇÕES PARA FILTRAR:")
    print("=" * 40)
    
    if problematic_only_groups:
        print("\n🚫 Excluir usuários dos grupos:")
        for group in sorted(problematic_only_groups):
            print(f"   - {group}")
    
    if problematic_only_profiles:
        print("\n🚫 Excluir usuários com perfis:")
        for profile in sorted(problematic_only_profiles):
            print(f"   - {profile}")
    
    if legitimate_groups - all_groups:
        print("\n✅ Incluir APENAS usuários dos grupos:")
        for group in sorted(legitimate_groups - all_groups):
            print(f"   - {group}")
    
    print("\n" + "=" * 70)
    print("✅ ANÁLISE CONCLUÍDA")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)