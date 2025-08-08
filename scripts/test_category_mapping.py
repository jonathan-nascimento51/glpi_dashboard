#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar o mapeamento de categorias com tickets reais
Este script valida se o campo categoria está funcionando corretamente
"""

import requests
import json
import sys
import os
from typing import Dict, Any, Optional, List
from collections import Counter

# Adicionar o diretório backend ao path para importar as configurações
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from config.settings import active_config

class GLPICategoryTester:
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
                print(f"✓ Autenticado com sucesso")
                return True
            else:
                print(f"✗ Erro na autenticação: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Erro ao autenticar: {e}")
            return False
    
    def test_category_field_with_real_data(self, field_id: str = '7', limit: int = 50) -> List[Dict]:
        """Testa o campo categoria com dados reais de tickets"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Session-Token': self.session_token,
                'App-Token': self.app_token
            }
            
            # Buscar tickets com o campo categoria
            search_params = {
                'is_deleted': 0,
                'range': f'0-{limit}',
                'forcedisplay[0]': '2',  # ID do ticket
                'forcedisplay[1]': '1',  # Nome/título
                'forcedisplay[2]': field_id,  # Campo categoria
                'forcedisplay[3]': '15',  # Data de criação
                'forcedisplay[4]': '12',  # Status
            }
            
            response = requests.get(
                f"{self.glpi_url}/search/Ticket",
                headers=headers,
                params=search_params
            )
            
            if response.status_code == 200:
                data = response.json()
                tickets = data.get('data', [])
                
                print(f"\n=== ANÁLISE DO CAMPO {field_id} COM {len(tickets)} TICKETS ===")
                
                # Analisar os valores de categoria
                category_values = []
                valid_tickets = []
                
                for ticket in tickets:
                    ticket_id = ticket.get('2', 'N/A')
                    ticket_name = ticket.get('1', 'N/A')
                    category_value = ticket.get(field_id, '')
                    date_created = ticket.get('15', 'N/A')
                    status = ticket.get('12', 'N/A')
                    
                    if category_value and category_value != '0' and category_value != '':
                        category_values.append(category_value)
                        valid_tickets.append({
                            'id': ticket_id,
                            'name': ticket_name,
                            'category': category_value,
                            'date': date_created,
                            'status': status
                        })
                
                # Estatísticas
                total_tickets = len(tickets)
                tickets_with_category = len(valid_tickets)
                tickets_without_category = total_tickets - tickets_with_category
                
                print(f"Total de tickets analisados: {total_tickets}")
                print(f"Tickets COM categoria: {tickets_with_category} ({tickets_with_category/total_tickets*100:.1f}%)")
                print(f"Tickets SEM categoria: {tickets_without_category} ({tickets_without_category/total_tickets*100:.1f}%)")
                
                # Top categorias mais usadas
                if category_values:
                    category_counter = Counter(category_values)
                    print(f"\nTop 10 categorias mais usadas:")
                    for category, count in category_counter.most_common(10):
                        print(f"  {category}: {count} tickets")
                
                # Mostrar alguns exemplos
                print(f"\nExemplos de tickets com categoria:")
                for ticket in valid_tickets[:5]:
                    print(f"  Ticket {ticket['id']}: {ticket['name'][:40]}... | Categoria: {ticket['category']}")
                
                return valid_tickets
            else:
                print(f"✗ Erro ao buscar tickets: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"✗ Erro ao testar campo categoria: {e}")
            return []
    
    def validate_category_ids(self, tickets_with_category: List[Dict]) -> None:
        """Valida se os IDs de categoria correspondem a categorias reais"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Session-Token': self.session_token,
                'App-Token': self.app_token
            }
            
            # Obter todas as categorias
            response = requests.get(
                f"{self.glpi_url}/ITILCategory",
                headers=headers,
                params={'range': '0-1000'}  # Buscar muitas categorias
            )
            
            if response.status_code == 200:
                categories = response.json()
                category_map = {str(cat['id']): cat for cat in categories}
                
                print(f"\n=== VALIDAÇÃO DOS IDs DE CATEGORIA ===")
                print(f"Total de categorias disponíveis: {len(categories)}")
                
                # Verificar se os IDs dos tickets correspondem a categorias reais
                unique_category_ids = set(ticket['category'] for ticket in tickets_with_category)
                
                valid_categories = 0
                invalid_categories = 0
                
                print(f"\nValidando {len(unique_category_ids)} IDs únicos de categoria:")
                
                for cat_id in sorted(unique_category_ids):
                    if cat_id in category_map:
                        category = category_map[cat_id]
                        print(f"  ✓ ID {cat_id}: {category.get('name', 'N/A')} | Completo: {category.get('completename', 'N/A')}")
                        valid_categories += 1
                    else:
                        print(f"  ✗ ID {cat_id}: CATEGORIA NÃO ENCONTRADA")
                        invalid_categories += 1
                
                print(f"\nResumo da validação:")
                print(f"  Categorias válidas: {valid_categories}")
                print(f"  Categorias inválidas: {invalid_categories}")
                
                if invalid_categories == 0:
                    print(f"  ✓ Todos os IDs de categoria são válidos!")
                else:
                    print(f"  ⚠ Alguns IDs de categoria não foram encontrados")
                    
            else:
                print(f"✗ Erro ao obter categorias: {response.status_code}")
                
        except Exception as e:
            print(f"✗ Erro ao validar categorias: {e}")
    
    def test_category_search(self, category_id: str) -> None:
        """Testa busca de tickets por uma categoria específica"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Session-Token': self.session_token,
                'App-Token': self.app_token
            }
            
            # Buscar tickets de uma categoria específica
            search_params = {
                'is_deleted': 0,
                'range': '0-10',
                'criteria[0][field]': '7',  # Campo categoria
                'criteria[0][searchtype]': 'equals',
                'criteria[0][value]': category_id,
                'forcedisplay[0]': '2',  # ID
                'forcedisplay[1]': '1',  # Nome
                'forcedisplay[2]': '7',  # Categoria
            }
            
            response = requests.get(
                f"{self.glpi_url}/search/Ticket",
                headers=headers,
                params=search_params
            )
            
            if response.status_code == 200:
                data = response.json()
                total_count = data.get('totalcount', 0)
                tickets = data.get('data', [])
                
                print(f"\n=== TESTE DE BUSCA POR CATEGORIA {category_id} ===")
                print(f"Total de tickets encontrados: {total_count}")
                
                if tickets:
                    print(f"Primeiros resultados:")
                    for ticket in tickets[:5]:
                        ticket_id = ticket.get('2', 'N/A')
                        ticket_name = ticket.get('1', 'N/A')
                        category = ticket.get('7', 'N/A')
                        print(f"  Ticket {ticket_id}: {ticket_name[:40]}... | Categoria: {category}")
                else:
                    print("  Nenhum ticket encontrado para esta categoria")
                    
            else:
                print(f"✗ Erro na busca: {response.status_code}")
                
        except Exception as e:
            print(f"✗ Erro ao testar busca por categoria: {e}")
    
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
    print("=== TESTE DE MAPEAMENTO DE CATEGORIAS NO GLPI ===")
    print("Este script valida se o campo categoria está funcionando corretamente\n")
    
    tester = GLPICategoryTester()
    
    # Autenticar
    if not tester.authenticate():
        return
    
    try:
        # Testar campo categoria com dados reais
        tickets_with_category = tester.test_category_field_with_real_data(field_id='7', limit=100)
        
        if tickets_with_category:
            # Validar IDs de categoria
            tester.validate_category_ids(tickets_with_category)
            
            # Testar busca por uma categoria específica
            if tickets_with_category:
                sample_category = tickets_with_category[0]['category']
                tester.test_category_search(sample_category)
        
        print("\n=== CONCLUSÕES ===")
        print("1. O campo 7 representa a categoria escolhida pelo usuário")
        print("2. Verifique se a porcentagem de tickets com categoria está adequada")
        print("3. Confirme se os IDs de categoria são válidos")
        print("4. Teste a busca por categoria para verificar se funciona corretamente")
        
    finally:
        tester.close_session()

if __name__ == "__main__":
    main()