#!/usr/bin/env python3
"""
Script de teste simplificado para diagnosticar o ranking de técnicos
"""

import os
import sys
import requests
import json
from datetime import datetime

# Configurações diretas (sem importar app.config)
GLPI_URL = os.environ.get('GLPI_URL', 'http://10.73.0.79/glpi/apirest.php')
GLPI_USER_TOKEN = os.environ.get('GLPI_USER_TOKEN')
GLPI_APP_TOKEN = os.environ.get('GLPI_APP_TOKEN')

class GLPITester:
    def __init__(self):
        self.base_url = GLPI_URL
        self.user_token = GLPI_USER_TOKEN
        self.app_token = GLPI_APP_TOKEN
        self.session_token = None
        
    def authenticate(self):
        """Testa autenticação com GLPI"""
        print("\n=== TESTE DE AUTENTICAÇÃO ===")
        print(f"URL: {self.base_url}")
        print(f"User Token: {'***' if self.user_token else 'NÃO DEFINIDO'}")
        print(f"App Token: {'***' if self.app_token else 'NÃO DEFINIDO'}")
        
        if not self.user_token or not self.app_token:
            print(" ERRO: Tokens não configurados")
            return False
            
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'user_token {self.user_token}',
            'App-Token': self.app_token
        }
        
        try:
            response = requests.get(f"{self.base_url}/initSession", headers=headers, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.session_token = data.get('session_token')
                print(f" Autenticação bem-sucedida")
                print(f"Session Token: {self.session_token[:20]}...")
                return True
            else:
                print(f" Falha na autenticação: {response.text}")
                return False
                
        except Exception as e:
            print(f" Erro na autenticação: {e}")
            return False
    
    def test_search_options(self):
        """Testa as opções de pesquisa para tickets"""
        print("\n=== TESTE DE OPÇÕES DE PESQUISA ===")
        
        if not self.session_token:
            print(" Sem token de sessão")
            return
            
        headers = {
            'Content-Type': 'application/json',
            'Session-Token': self.session_token,
            'App-Token': self.app_token
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/listSearchOptions/Ticket",
                headers=headers,
                timeout=10
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f" Opções de pesquisa obtidas: {len(data)} campos")
                
                # Procurar campos relacionados a técnico
                tech_fields = {}
                for field_id, field_info in data.items():
                    field_name = field_info.get('name', '').lower()
                    if any(term in field_name for term in ['técnico', 'tecnico', 'assigned', 'atribuído']):
                        tech_fields[field_id] = field_info
                        print(f"  Campo {field_id}: {field_info.get('name')} - {field_info.get('table')}.{field_info.get('field')}")
                
                if not tech_fields:
                    print(" Nenhum campo de técnico encontrado")
                else:
                    print(f" Encontrados {len(tech_fields)} campos de técnico")
                    
                return tech_fields
            else:
                print(f" Erro ao obter opções: {response.text}")
                return {}
                
        except Exception as e:
            print(f" Erro ao testar opções: {e}")
            return {}
    
    def cleanup(self):
        """Limpa a sessão"""
        if self.session_token:
            headers = {
                'Session-Token': self.session_token,
                'App-Token': self.app_token
            }
            try:
                requests.get(f"{self.base_url}/killSession", headers=headers, timeout=5)
                print("\n Sessão encerrada")
            except:
                pass

def main():
    print(" DIAGNÓSTICO DO RANKING DE TÉCNICOS")
    print("=" * 50)
    
    tester = GLPITester()
    
    try:
        # 1. Teste de autenticação
        if not tester.authenticate():
            print("\n FALHA CRÍTICA: Não foi possível autenticar")
            return
        
        # 2. Teste de opções de pesquisa
        tech_fields = tester.test_search_options()
        
        # Resumo
        print("\n" + "=" * 50)
        print(" RESUMO DO DIAGNÓSTICO")
        print(f" Autenticação: {'OK' if tester.session_token else 'FALHOU'}")
        print(f" Campos de técnico: {len(tech_fields)} encontrados")
        
        if not tech_fields:
            print("\n  PROBLEMA IDENTIFICADO:")
            print("   Nenhum campo de técnico foi encontrado nas opções de pesquisa.")
            print("   Isso explica por que o ranking não funciona.")
        
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()
