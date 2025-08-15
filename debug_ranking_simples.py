#!/usr/bin/env python3
"""
Script de diagnóstico simples para o ranking de técnicos
"""

import sys
import os
import requests
import json
from datetime import datetime

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Configurações GLPI (do arquivo .env)
GLPI_URL = "http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php"
GLPI_USER_TOKEN = "TQdSxqg2e56PfF8ZJSX3iEJ1wCpHwhCkQJ2QtRnq"
GLPI_APP_TOKEN = "aY3f9F5aNHJmY8op0vTE4koguiPwpEYANp1JULid"

def test_glpi_connection():
    """Testa a conexão com GLPI"""
    print("=== TESTE DE CONEXÃO GLPI ===")
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'user_token {GLPI_USER_TOKEN}',
        'App-Token': GLPI_APP_TOKEN
    }
    
    try:
        # Iniciar sessão
        response = requests.get(f"{GLPI_URL}/initSession", headers=headers)
        print(f"Status da conexão: {response.status_code}")
        
        if response.status_code == 200:
            session_data = response.json()
            session_token = session_data.get('session_token')
            print(f"Session token obtido: {session_token[:20]}...")
            return session_token
        else:
            print(f"Erro na conexão: {response.text}")
            return None
            
    except Exception as e:
        print(f"Erro de conexão: {e}")
        return None

def get_profiles(session_token):
    """Busca perfis de usuário"""
    print("\n=== BUSCANDO PERFIS ===")
    
    headers = {
        'Content-Type': 'application/json',
        'Session-Token': session_token,
        'App-Token': GLPI_APP_TOKEN
    }
    
    try:
        response = requests.get(f"{GLPI_URL}/Profile", headers=headers)
        print(f"Status busca perfis: {response.status_code}")
        
        if response.status_code == 200:
            profiles = response.json()
            print(f"Número de perfis encontrados: {len(profiles)}")
            
            # Procurar perfis de técnico
            tech_profiles = []
            for profile in profiles:
                name = profile.get('name', '').lower()
                if any(keyword in name for keyword in ['tecnico', 'técnico', 'tech', 'suporte']):
                    tech_profiles.append(profile)
                    print(f"Perfil técnico encontrado: {profile.get('name')} (ID: {profile.get('id')})")
            
            return tech_profiles
        else:
            print(f"Erro ao buscar perfis: {response.text}")
            return []
            
    except Exception as e:
        print(f"Erro ao buscar perfis: {e}")
        return []

def get_users_by_profile(session_token, profile_id):
    """Busca usuários por perfil"""
    print(f"\n=== BUSCANDO USUÁRIOS DO PERFIL {profile_id} ===")
    
    headers = {
        'Content-Type': 'application/json',
        'Session-Token': session_token,
        'App-Token': GLPI_APP_TOKEN
    }
    
    try:
        # Buscar usuários com o perfil específico
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
        
        print(f"Status busca usuários: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            users_data = result.get('data', [])
            print(f"Usuários encontrados com perfil {profile_id}: {len(users_data)}")
            
            # Extrair IDs dos usuários
            user_ids = []
            for user_data in users_data:
                user_id = user_data.get('2')  # users_id
                if user_id:
                    user_ids.append(user_id)
            
            print(f"IDs de usuários extraídos: {user_ids[:10]}...")  # Mostrar apenas os primeiros 10
            return user_ids
        else:
            print(f"Erro ao buscar usuários: {response.text}")
            return []
            
    except Exception as e:
        print(f"Erro ao buscar usuários: {e}")
        return []

def get_user_details(session_token, user_ids):
    """Busca detalhes dos usuários"""
    print(f"\n=== BUSCANDO DETALHES DE {len(user_ids)} USUÁRIOS ===")
    
    headers = {
        'Content-Type': 'application/json',
        'Session-Token': session_token,
        'App-Token': GLPI_APP_TOKEN
    }
    
    active_users = []
    
    # Buscar em lotes para evitar URLs muito longas
    batch_size = 50
    for i in range(0, len(user_ids), batch_size):
        batch_ids = user_ids[i:i+batch_size]
        
        try:
            response = requests.get(
                f"{GLPI_URL}/User",
                headers=headers,
                params={
                    'range': f"0-{len(batch_ids)-1}",
                    'criteria[0][field]': '2',  # id
                    'criteria[0][searchtype]': 'equals',
                    'criteria[0][value]': '|'.join(map(str, batch_ids))
                }
            )
            
            if response.status_code == 200:
                users = response.json()
                for user in users:
                    if user.get('is_active', 0) == 1:
                        active_users.append({
                            'id': user.get('id'),
                            'name': user.get('name'),
                            'realname': user.get('realname'),
                            'firstname': user.get('firstname')
                        })
            
        except Exception as e:
            print(f"Erro ao buscar lote de usuários: {e}")
    
    print(f"Usuários ativos encontrados: {len(active_users)}")
    for user in active_users[:5]:  # Mostrar apenas os primeiros 5
        print(f"  - {user['name']} ({user['realname']} {user['firstname']})")
    
    return active_users

def count_tickets_for_user(session_token, user_id):
    """Conta tickets para um usuário específico"""
    headers = {
        'Content-Type': 'application/json',
        'Session-Token': session_token,
        'App-Token': GLPI_APP_TOKEN
    }
    
    try:
        # Buscar tickets onde o usuário é técnico
        response = requests.get(
            f"{GLPI_URL}/search/Ticket",
            headers=headers,
            params={
                'criteria[0][field]': '5',  # users_id_tech (campo do técnico)
                'criteria[0][searchtype]': 'equals',
                'criteria[0][value]': user_id,
                'range': '0-0'  # Só queremos o count
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('totalcount', 0)
        else:
            return 0
            
    except Exception as e:
        print(f"Erro ao contar tickets para usuário {user_id}: {e}")
        return 0

def main():
    """Função principal"""
    print(f"Iniciando diagnóstico em {datetime.now()}")
    
    # 1. Testar conexão
    session_token = test_glpi_connection()
    if not session_token:
        print("Falha na conexão. Verifique as configurações.")
        return
    
    # 2. Buscar perfis de técnico
    tech_profiles = get_profiles(session_token)
    if not tech_profiles:
        print("Nenhum perfil de técnico encontrado.")
        return
    
    # 3. Para cada perfil, buscar usuários
    all_tech_users = []
    for profile in tech_profiles:
        profile_id = profile.get('id')
        user_ids = get_users_by_profile(session_token, profile_id)
        
        if user_ids:
            users = get_user_details(session_token, user_ids)
            all_tech_users.extend(users)
    
    print(f"\n=== RESUMO ===")
    print(f"Total de técnicos ativos: {len(all_tech_users)}")
    
    # 4. Testar contagem de tickets para alguns usuários
    if all_tech_users:
        print("\n=== TESTE DE CONTAGEM DE TICKETS ===")
        for user in all_tech_users[:3]:  # Testar apenas os primeiros 3
            ticket_count = count_tickets_for_user(session_token, user['id'])
            print(f"Usuário {user['name']}: {ticket_count} tickets")
    
    print("\nDiagnóstico concluído!")

if __name__ == "__main__":
    main()