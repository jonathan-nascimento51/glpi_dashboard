#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar especificamente o campo 5 (Técnico) no GLPI
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def test_field_5():
    """Testa especificamente o campo 5 (Técnico)"""
    
    # Configurações do GLPI
    glpi_url = os.getenv('GLPI_URL')
    user_token = os.getenv('GLPI_USER_TOKEN')
    app_token = os.getenv('GLPI_APP_TOKEN')
    
    if not all([glpi_url, user_token, app_token]):
        print(" Tokens não configurados")
        return False
    
    print(f" Conectando ao GLPI: {glpi_url}")
    
    # Headers para autenticação
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'user_token {user_token}',
        'App-Token': app_token
    }
    
    try:
        # 1. Iniciar sessão
        print("\n1 Iniciando sessão...")
        init_response = requests.get(
            f"{glpi_url}/initSession",
            headers=headers,
            timeout=30
        )
        
        if init_response.status_code != 200:
            print(f" Falha na autenticação: {init_response.status_code}")
            return False
        
        session_data = init_response.json()
        session_token = session_data.get('session_token')
        headers['Session-Token'] = session_token
        
        print(f" Sessão iniciada")
        
        # 2. Testar busca com campo 5 (Técnico)
        print("\n2 Testando busca com campo 5 (Técnico)...")
        
        # Buscar tickets com técnico atribuído (campo 5)
        search_url = f"{glpi_url}/search/Ticket"
        search_params = {
            'criteria[0][field]': '5',
            'criteria[0][searchtype]': 'contains',
            'criteria[0][value]': '',
            'range': '0-9'
        }
        
        print(f"URL: {search_url}")
        print(f"Parâmetros: {search_params}")
        
        tickets_response = requests.get(
            search_url,
            headers=headers,
            params=search_params,
            timeout=30
        )
        
        print(f"Status da resposta: {tickets_response.status_code}")
        
        if tickets_response.status_code == 200:
            try:
                tickets_data = tickets_response.json()
                total_count = tickets_data.get('totalcount', 0)
                print(f" Busca bem-sucedida: {total_count} tickets encontrados")
                
                if 'data' in tickets_data and tickets_data['data']:
                    print("\n Primeiros tickets encontrados:")
                    for i, ticket in enumerate(tickets_data['data'][:5]):
                        ticket_id = ticket.get('2', 'N/A')  # Campo 2 é o ID
                        tech_field = ticket.get('5', 'N/A')  # Campo 5 é o técnico
                        print(f"   Ticket {ticket_id}: Técnico = '{tech_field}'")
                else:
                    print(" Nenhum ticket encontrado com técnico atribuído")
                    
            except json.JSONDecodeError as e:
                print(f" Erro ao decodificar JSON: {e}")
                print(f"Resposta bruta: {tickets_response.text[:500]}...")
        else:
            print(f" Falha na busca: {tickets_response.status_code}")
            print(f"Resposta: {tickets_response.text[:500]}...")
        
        # 3. Testar busca de usuários ativos com perfil 6
        print("\n3 Testando busca de usuários ativos (perfil 6)...")
        
        users_url = f"{glpi_url}/search/User"
        users_params = {
            'criteria[0][field]': '20',  # Campo 20 é profiles_id
            'criteria[0][searchtype]': 'equals',
            'criteria[0][value]': '6',
            'criteria[1][field]': '8',   # Campo 8 é is_active
            'criteria[1][searchtype]': 'equals',
            'criteria[1][value]': '1',
            'criteria[1][link]': 'AND',
            'range': '0-9'
        }
        
        users_response = requests.get(
            users_url,
            headers=headers,
            params=users_params,
            timeout=30
        )
        
        if users_response.status_code == 200:
            try:
                users_data = users_response.json()
                total_users = users_data.get('totalcount', 0)
                print(f" Encontrados {total_users} usuários ativos com perfil 6")
                
                if 'data' in users_data and users_data['data']:
                    print("\n Primeiros técnicos encontrados:")
                    for i, user in enumerate(users_data['data'][:5]):
                        user_id = user.get('2', 'N/A')  # Campo 2 é o ID
                        user_name = user.get('1', 'N/A')  # Campo 1 é o nome
                        print(f"   ID {user_id}: {user_name}")
                        
            except json.JSONDecodeError as e:
                print(f" Erro ao decodificar JSON de usuários: {e}")
        else:
            print(f" Falha na busca de usuários: {users_response.status_code}")
        
        # 4. Encerrar sessão
        print("\n4 Encerrando sessão...")
        kill_response = requests.get(
            f"{glpi_url}/killSession",
            headers=headers,
            timeout=30
        )
        
        if kill_response.status_code == 200:
            print(" Sessão encerrada")
        
        return True
        
    except Exception as e:
        print(f" Erro: {e}")
        import traceback
        print(f"Stack trace: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print(" Teste Específico do Campo 5 (Técnico) - GLPI")
    print("=" * 50)
    
    success = test_field_5()
    
    print("\n" + "=" * 50)
    if success:
        print(" Teste concluído!")
    else:
        print(" Teste falhou!")
