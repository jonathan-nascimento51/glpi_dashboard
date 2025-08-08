#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para descobrir o campo categoria no GLPI
Este script ajuda a identificar qual campo representa a categoria escolhida pelo usuário no chamado
"""

import requests
import json
import sys
import os
from typing import Dict, Any, Optional

# Adicionar o diretório backend ao path para importar as configurações
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from config.settings import active_config

class GLPICategoryFieldDiscovery:
    def __init__(self):
        self.glpi_url = active_config.GLPI_URL
        self.app_token = active_config.GLPI_APP_TOKEN
        self.user_token = active_config.GLPI_USER_TOKEN
        self.session_token = None
        
    def authenticate(self) -> bool:
        """Autentica no GLPI"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'user_token {self.user_token}',
                'App-Token': self.app_token
            }
            
            response = requests.get(
                f"{self.glpi_url}/initSession",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.session_token = data.get('session_token')
                print(f"✓ Autenticado com sucesso. Session token: {self.session_token[:20]}...")
                return True
            else:
                print(f"✗ Erro na autenticação: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Erro ao autenticar: {e}")
            return False
    
    def get_search_options(self) -> Optional[Dict[str, Any]]:
        """Obtém todas as opções de busca disponíveis para Ticket"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Session-Token': self.session_token,
                'App-Token': self.app_token
            }
            
            response = requests.get(
                f"{self.glpi_url}/listSearchOptions/Ticket",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"✗ Erro ao obter opções de busca: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"✗ Erro ao obter opções de busca: {e}")
            return None
    
    def find_category_fields(self, search_options: Dict[str, Any]) -> None:
        """Encontra todos os campos relacionados a categoria"""
        print("\n=== CAMPOS RELACIONADOS A CATEGORIA ===")
        category_fields = []
        
        for field_id, field_data in search_options.items():
            if isinstance(field_data, dict) and 'name' in field_data:
                field_name = field_data['name'].lower()
                
                # Procurar por palavras-chave relacionadas a categoria
                category_keywords = ['categoria', 'category', 'itilcategory', 'tipo']
                
                if any(keyword in field_name for keyword in category_keywords):
                    category_fields.append({
                        'id': field_id,
                        'name': field_data['name'],
                        'table': field_data.get('table', 'N/A'),
                        'field': field_data.get('field', 'N/A'),
                        'datatype': field_data.get('datatype', 'N/A')
                    })
        
        if category_fields:
            print(f"Encontrados {len(category_fields)} campos relacionados a categoria:")
            for field in category_fields:
                print(f"  ID: {field['id']} | Nome: {field['name']} | Tabela: {field['table']} | Campo: {field['field']} | Tipo: {field['datatype']}")
        else:
            print("Nenhum campo de categoria encontrado com as palavras-chave padrão.")
        
        return category_fields
    
    def test_category_field(self, field_id: str) -> None:
        """Testa um campo específico para ver se retorna dados de categoria"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Session-Token': self.session_token,
                'App-Token': self.app_token
            }
            
            # Buscar alguns tickets para testar o campo
            search_params = {
                'is_deleted': 0,
                'range': '0-10',  # Primeiros 10 tickets
                'forcedisplay[0]': field_id,  # Forçar exibição do campo
                'forcedisplay[1]': '2',  # ID do ticket
                'forcedisplay[2]': '1',  # Nome/título
            }
            
            response = requests.get(
                f"{self.glpi_url}/search/Ticket",
                headers=headers,
                params=search_params
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data']:
                    print(f"\n=== TESTE DO CAMPO {field_id} ===")
                    print(f"Total de tickets encontrados: {data.get('totalcount', 0)}")
                    print("Primeiros resultados:")
                    
                    for i, ticket in enumerate(data['data'][:5]):
                        ticket_id = ticket.get('2', 'N/A')
                        ticket_name = ticket.get('1', 'N/A')
                        category_value = ticket.get(field_id, 'N/A')
                        print(f"  Ticket {ticket_id}: {ticket_name[:50]}... | Categoria: {category_value}")
                else:
                    print(f"\n✗ Campo {field_id}: Nenhum dado retornado")
            else:
                print(f"\n✗ Campo {field_id}: Erro {response.status_code}")
                
        except Exception as e:
            print(f"\n✗ Erro ao testar campo {field_id}: {e}")
    
    def get_categories_list(self) -> None:
        """Obtém a lista de categorias disponíveis no GLPI"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Session-Token': self.session_token,
                'App-Token': self.app_token
            }
            
            response = requests.get(
                f"{self.glpi_url}/ITILCategory",
                headers=headers,
                params={'range': '0-50'}  # Primeiras 50 categorias
            )
            
            if response.status_code == 200:
                categories = response.json()
                print(f"\n=== CATEGORIAS DISPONÍVEIS NO GLPI ===")
                print(f"Total de categorias encontradas: {len(categories)}")
                
                for category in categories[:10]:  # Mostrar apenas as primeiras 10
                    cat_id = category.get('id', 'N/A')
                    cat_name = category.get('name', 'N/A')
                    cat_complete = category.get('completename', 'N/A')
                    print(f"  ID: {cat_id} | Nome: {cat_name} | Nome Completo: {cat_complete}")
                    
                if len(categories) > 10:
                    print(f"  ... e mais {len(categories) - 10} categorias")
            else:
                print(f"\n✗ Erro ao obter categorias: {response.status_code}")
                
        except Exception as e:
            print(f"\n✗ Erro ao obter categorias: {e}")
    
    def close_session(self) -> None:
        """Fecha a sessão no GLPI"""
        if self.session_token:
            try:
                headers = {
                    'Content-Type': 'application/json',
                    'Session-Token': self.session_token,
                    'App-Token': self.app_token
                }
                
                requests.get(f"{self.glpi_url}/killSession", headers=headers)
                print("\n✓ Sessão encerrada")
            except:
                pass

def main():
    print("=== DESCOBERTA DO CAMPO CATEGORIA NO GLPI ===")
    print("Este script ajuda a identificar qual campo representa a categoria escolhida pelo usuário\n")
    
    discovery = GLPICategoryFieldDiscovery()
    
    # Autenticar
    if not discovery.authenticate():
        return
    
    try:
        # Obter opções de busca
        print("\nObtendo opções de busca...")
        search_options = discovery.get_search_options()
        
        if not search_options:
            return
        
        print(f"✓ {len(search_options)} opções de busca encontradas")
        
        # Encontrar campos de categoria
        category_fields = discovery.find_category_fields(search_options)
        
        # Testar campos encontrados
        if category_fields:
            print("\n=== TESTANDO CAMPOS DE CATEGORIA ===")
            for field in category_fields:
                discovery.test_category_field(field['id'])
        
        # Testar campo 7 (usado no código atual)
        print("\n=== TESTANDO CAMPO 7 (USADO NO CÓDIGO ATUAL) ===")
        discovery.test_category_field('7')
        
        # Obter lista de categorias
        discovery.get_categories_list()
        
        print("\n=== RESUMO ===")
        print("1. O campo 7 é usado atualmente no código para categoria")
        print("2. Verifique se os valores retornados pelo campo 7 correspondem às categorias esperadas")
        print("3. Se necessário, use um dos outros campos encontrados")
        print("4. As categorias são armazenadas na tabela ITILCategory")
        
    finally:
        discovery.close_session()

if __name__ == "__main__":
    main()