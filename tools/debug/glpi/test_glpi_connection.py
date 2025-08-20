#!/usr/bin/env python3
"""
Script para testar conectividade e autenticação com GLPI
Uso: python test_glpi_connection.py [--config CONFIG_FILE]
"""

import requests
import json
import argparse
import sys
import os
from datetime import datetime
from pathlib import Path

def load_config(config_file=None):
    """Carrega configuração do GLPI"""
    if config_file and os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    
    # Tenta carregar do arquivo padrão do backend
    backend_config = Path(__file__).parent.parent.parent.parent / 'backend' / 'config.json'
    if backend_config.exists():
        with open(backend_config, 'r') as f:
            config = json.load(f)
            return config.get('glpi', {})
    
    # Configuração padrão
    return {
        'url': 'http://localhost/glpi',
        'app_token': 'your_app_token',
        'user_token': 'your_user_token'
    }

def test_glpi_connection(config):
    """Testa conexão básica com GLPI"""
    print("🔍 Testando conexão com GLPI...")
    print(f"URL: {config['url']}")
    
    try:
        # Testa se o GLPI está acessível
        response = requests.get(f"{config['url']}/apirest.php", timeout=10)
        print(f"Status da conexão: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ GLPI está acessível")
            return True
        else:
            print(f"❌ GLPI não está acessível - Status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def test_glpi_auth(config):
    """Testa autenticação com GLPI"""
    print("\n🔐 Testando autenticação...")
    
    headers = {
        'Content-Type': 'application/json',
        'App-Token': config.get('app_token', ''),
        'Authorization': f"user_token {config.get('user_token', '')}"
    }
    
    try:
        # Tenta fazer login
        response = requests.get(
            f"{config['url']}/apirest.php/initSession",
            headers=headers,
            timeout=10
        )
        
        print(f"Status da autenticação: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            session_token = data.get('session_token')
            if session_token:
                print("✅ Autenticação bem-sucedida")
                print(f"Session Token: {session_token[:20]}...")
                return session_token
            else:
                print("❌ Autenticação falhou - Token de sessão não encontrado")
                return None
        else:
            print(f"❌ Autenticação falhou - Status: {response.status_code}")
            print(f"Resposta: {response.text[:200]}...")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na autenticação: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao decodificar resposta: {e}")
        return None

def test_glpi_tickets(config, session_token):
    """Testa busca de tickets no GLPI"""
    print("\n🎫 Testando busca de tickets...")
    
    headers = {
        'Content-Type': 'application/json',
        'App-Token': config.get('app_token', ''),
        'Session-Token': session_token
    }
    
    try:
        # Busca tickets recentes
        response = requests.get(
            f"{config['url']}/apirest.php/Ticket",
            headers=headers,
            params={'range': '0-9'},  # Primeiros 10 tickets
            timeout=10
        )
        
        print(f"Status da busca: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            ticket_count = len(data) if isinstance(data, list) else 0
            print(f"✅ Busca bem-sucedida - {ticket_count} tickets encontrados")
            
            if ticket_count > 0:
                # Mostra informações do primeiro ticket
                first_ticket = data[0] if isinstance(data, list) else data
                print(f"Primeiro ticket ID: {first_ticket.get('id', 'N/A')}")
                print(f"Status: {first_ticket.get('status', 'N/A')}")
                print(f"Título: {first_ticket.get('name', 'N/A')[:50]}...")
            
            return True
        else:
            print(f"❌ Busca falhou - Status: {response.status_code}")
            print(f"Resposta: {response.text[:200]}...")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na busca: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao decodificar resposta: {e}")
        return False

def test_glpi_users(config, session_token):
    """Testa busca de usuários/técnicos no GLPI"""
    print("\n👥 Testando busca de usuários...")
    
    headers = {
        'Content-Type': 'application/json',
        'App-Token': config.get('app_token', ''),
        'Session-Token': session_token
    }
    
    try:
        # Busca usuários
        response = requests.get(
            f"{config['url']}/apirest.php/User",
            headers=headers,
            params={'range': '0-9'},  # Primeiros 10 usuários
            timeout=10
        )
        
        print(f"Status da busca: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            user_count = len(data) if isinstance(data, list) else 0
            print(f"✅ Busca bem-sucedida - {user_count} usuários encontrados")
            
            if user_count > 0:
                # Mostra informações do primeiro usuário
                first_user = data[0] if isinstance(data, list) else data
                print(f"Primeiro usuário ID: {first_user.get('id', 'N/A')}")
                print(f"Nome: {first_user.get('name', 'N/A')}")
                print(f"Nome real: {first_user.get('realname', 'N/A')}")
            
            return True
        else:
            print(f"❌ Busca falhou - Status: {response.status_code}")
            print(f"Resposta: {response.text[:200]}...")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na busca: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao decodificar resposta: {e}")
        return False

def close_glpi_session(config, session_token):
    """Fecha a sessão do GLPI"""
    print("\n🔒 Fechando sessão...")
    
    headers = {
        'Content-Type': 'application/json',
        'App-Token': config.get('app_token', ''),
        'Session-Token': session_token
    }
    
    try:
        response = requests.get(
            f"{config['url']}/apirest.php/killSession",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Sessão fechada com sucesso")
        else:
            print(f"⚠️  Erro ao fechar sessão - Status: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Erro ao fechar sessão: {e}")

def main():
    parser = argparse.ArgumentParser(description='Testa conectividade com GLPI')
    parser.add_argument('--config', help='Arquivo de configuração JSON')
    parser.add_argument('--verbose', '-v', action='store_true', help='Saída verbosa')
    
    args = parser.parse_args()
    
    print(f"🚀 Testando conectividade com GLPI")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Carrega configuração
    config = load_config(args.config)
    
    if not config.get('url'):
        print("❌ Configuração do GLPI não encontrada")
        sys.exit(1)
    
    # Executa testes
    tests_passed = 0
    total_tests = 4
    
    # Teste 1: Conexão
    if test_glpi_connection(config):
        tests_passed += 1
    
    # Teste 2: Autenticação
    session_token = test_glpi_auth(config)
    if session_token:
        tests_passed += 1
        
        # Teste 3: Busca de tickets
        if test_glpi_tickets(config, session_token):
            tests_passed += 1
        
        # Teste 4: Busca de usuários
        if test_glpi_users(config, session_token):
            tests_passed += 1
        
        # Fecha sessão
        close_glpi_session(config, session_token)
    
    # Resumo
    print("\n📊 RESUMO DOS TESTES")
    print("=" * 50)
    print(f"🎯 Resultado Final: {tests_passed}/{total_tests} testes passaram")
    
    if tests_passed == total_tests:
        print("🎉 Todos os testes passaram! GLPI está funcionando corretamente.")
        sys.exit(0)
    else:
        print("⚠️  Alguns testes falharam. Verifique a configuração do GLPI.")
        sys.exit(1)

if __name__ == "__main__":
    main()