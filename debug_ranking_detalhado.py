#!/usr/bin/env python3
"""
Script de diagnóstico detalhado para o ranking de técnicos
Investiga todos os perfis e usuários para encontrar técnicos
"""

import sys
import os
import requests
import json
from datetime import datetime

# Configurações GLPI (do arquivo .env)
GLPI_URL = "http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php"
GLPI_USER_TOKEN = "TQdSxqg2e56PfF8ZJSX3iEJ1wCpHwhCkQJ2QtRnq"
GLPI_APP_TOKEN = "aY3f9F5aNHJmY8op0vTE4koguiPwpEYANp1JULid"

def get_session_token():
    """Obtém token de sessão"""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'user_token {GLPI_USER_TOKEN}',
        'App-Token': GLPI_APP_TOKEN
    }
    
    try:
        response = requests.get(f"{GLPI_URL}/initSession", headers=headers)
        if response.status_code == 200:
            session_data = response.json()
            return session_data.get('session_token')
        else:
            print(f"Erro na conexão: {response.text}")
            return None
    except Exception as e:
        print(f"Erro de conexão: {e}")
        return None

def get_all_profiles(session_token):
    """Busca todos os perfis"""
    print("\n=== TODOS OS PERFIS ===")
    
    headers = {
        'Content-Type': 'application/json',
        'Session-Token': session_token,
        'App-Token': GLPI_APP_TOKEN
    }
    
    try:
        response = requests.get(f"{GLPI_URL}/Profile", headers=headers)
        if response.status_code == 200:
            profiles = response.json()
            print(f"Total de perfis: {len(profiles)}")
            
            for profile in profiles:
                print(f"  - ID: {profile.get('id')}, Nome: {profile.get('name')}")
            
            return profiles
        else:
            print(f"Erro ao buscar perfis: {response.text}")
            return []
    except Exception as e:
        print(f"Erro ao buscar perfis: {e}")
        return []

def get_profile_users_detailed(session_token, profile_id, profile_name):
    """Busca usuários de um perfil específico com mais detalhes"""
    print(f"\n=== USUÁRIOS DO PERFIL '{profile_name}' (ID: {profile_id}) ===")
    
    headers = {
        'Content-Type': 'application/json',
        'Session-Token': session_token,
        'App-Token': GLPI_APP_TOKEN
    }
    
    try:
        # Método 1: Buscar via Profile_User
        response = requests.get(
            f"{GLPI_URL}/search/Profile_User",
            headers=headers,
            params={
                'criteria[0][field]': '3',  # profiles_id
                'criteria[0][searchtype]': 'equals',
                'criteria[0][value]': profile_id,
                'range': '0-999'
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            users_data = result.get('data', [])
            print(f"  Usuários encontrados via Profile_User: {len(users_data)}")
            
            if users_data:
                print("  Primeiros 5 usuários:")
                for i, user_data in enumerate(users_data[:5]):
                    user_id = user_data.get('2')  # users_id
                    print(f"    {i+1}. User ID: {user_id}")
            
            return [user_data.get('2') for user_data in users_data if user_data.get('2')]
        else:
            print(f"  Erro ao buscar usuários: {response.text}")
            return []
            
    except Exception as e:
        print(f"  Erro ao buscar usuários: {e}")
        return []

def get_all_users_with_profiles(session_token):
    """Busca todos os usuários e seus perfis"""
    print("\n=== TODOS OS USUÁRIOS E SEUS PERFIS ===")
    
    headers = {
        'Content-Type': 'application/json',
        'Session-Token': session_token,
        'App-Token': GLPI_APP_TOKEN
    }
    
    try:
        # Buscar todos os usuários ativos
        response = requests.get(
            f"{GLPI_URL}/search/User",
            headers=headers,
            params={
                'criteria[0][field]': '8',  # is_active
                'criteria[0][searchtype]': 'equals',
                'criteria[0][value]': '1',
                'range': '0-99'  # Limitar para não sobrecarregar
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            users_data = result.get('data', [])
            print(f"  Usuários ativos encontrados: {len(users_data)}")
            
            # Para cada usuário, buscar seus perfis
            users_with_profiles = []
            for user_data in users_data[:10]:  # Limitar a 10 para teste
                user_id = user_data.get('2')  # id
                username = user_data.get('1')  # name
                realname = user_data.get('34')  # realname
                firstname = user_data.get('9')  # firstname
                
                # Buscar perfis do usuário
                profile_response = requests.get(
                    f"{GLPI_URL}/search/Profile_User",
                    headers=headers,
                    params={
                        'criteria[0][field]': '2',  # users_id
                        'criteria[0][searchtype]': 'equals',
                        'criteria[0][value]': user_id,
                        'range': '0-99'
                    }
                )
                
                profiles = []
                if profile_response.status_code == 200:
                    profile_result = profile_response.json()
                    profile_data = profile_result.get('data', [])
                    profiles = [p.get('3') for p in profile_data if p.get('3')]  # profiles_id
                
                user_info = {
                    'id': user_id,
                    'username': username,
                    'realname': realname,
                    'firstname': firstname,
                    'profiles': profiles
                }
                users_with_profiles.append(user_info)
                
                print(f"    User: {username} ({realname} {firstname}) - Perfis: {profiles}")
            
            return users_with_profiles
        else:
            print(f"  Erro ao buscar usuários: {response.text}")
            return []
            
    except Exception as e:
        print(f"  Erro ao buscar usuários: {e}")
        return []

def search_tickets_by_technician_field(session_token):
    """Busca tickets para descobrir qual campo é usado para técnicos"""
    print("\n=== INVESTIGANDO CAMPOS DE TÉCNICO EM TICKETS ===")
    
    headers = {
        'Content-Type': 'application/json',
        'Session-Token': session_token,
        'App-Token': GLPI_APP_TOKEN
    }
    
    try:
        # Buscar alguns tickets para ver a estrutura
        response = requests.get(
            f"{GLPI_URL}/search/Ticket",
            headers=headers,
            params={
                'range': '0-5',  # Apenas 5 tickets para análise
                'forcedisplay[0]': '2',   # id
                'forcedisplay[1]': '1',   # name
                'forcedisplay[2]': '5',   # users_id_tech
                'forcedisplay[3]': '6',   # groups_id_tech
                'forcedisplay[4]': '4',   # users_id_recipient
                'forcedisplay[5]': '71',  # groups_id
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            tickets_data = result.get('data', [])
            print(f"  Tickets encontrados: {len(tickets_data)}")
            
            for i, ticket in enumerate(tickets_data):
                print(f"    Ticket {i+1}:")
                print(f"      ID: {ticket.get('2')}")
                print(f"      Nome: {ticket.get('1')}")
                print(f"      Técnico (campo 5): {ticket.get('5')}")
                print(f"      Grupo Técnico (campo 6): {ticket.get('6')}")
                print(f"      Solicitante (campo 4): {ticket.get('4')}")
                print(f"      Grupo (campo 71): {ticket.get('71')}")
                print()
            
            return tickets_data
        else:
            print(f"  Erro ao buscar tickets: {response.text}")
            return []
            
    except Exception as e:
        print(f"  Erro ao buscar tickets: {e}")
        return []

def main():
    """Função principal"""
    print(f"Iniciando diagnóstico detalhado em {datetime.now()}")
    
    # 1. Obter token de sessão
    session_token = get_session_token()
    if not session_token:
        print("Falha na autenticação")
        return
    
    print(f"Conectado com sucesso! Session token: {session_token[:20]}...")
    
    # 2. Buscar todos os perfis
    profiles = get_all_profiles(session_token)
    
    # 3. Para cada perfil, buscar usuários
    all_users = []
    for profile in profiles:
        profile_id = profile.get('id')
        profile_name = profile.get('name')
        users = get_profile_users_detailed(session_token, profile_id, profile_name)
        if users:
            all_users.extend(users)
    
    # 4. Buscar usuários ativos e seus perfis
    users_with_profiles = get_all_users_with_profiles(session_token)
    
    # 5. Investigar estrutura de tickets
    tickets = search_tickets_by_technician_field(session_token)
    
    # 6. Resumo
    print("\n=== RESUMO FINAL ===")
    print(f"Total de perfis: {len(profiles)}")
    print(f"Total de usuários encontrados via perfis: {len(set(all_users))}")
    print(f"Usuários ativos analisados: {len(users_with_profiles)}")
    print(f"Tickets analisados: {len(tickets)}")
    
    # Identificar usuários com perfis que podem ser técnicos
    potential_techs = []
    for user in users_with_profiles:
        if user['profiles']:
            potential_techs.append(user)
    
    print(f"Usuários com perfis (potenciais técnicos): {len(potential_techs)}")
    
    if potential_techs:
        print("\nPrimeiros 5 usuários com perfis:")
        for user in potential_techs[:5]:
            print(f"  - {user['username']} ({user['realname']} {user['firstname']}) - Perfis: {user['profiles']}")
    
    print("\nDiagnóstico detalhado concluído!")

if __name__ == "__main__":
    main()