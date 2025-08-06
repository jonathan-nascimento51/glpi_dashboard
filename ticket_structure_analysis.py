#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise da estrutura real dos tickets GLPI para encontrar o campo correto de data
"""

import os
import sys
import requests
import logging
import json
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TicketStructureAnalyzer:
    def __init__(self):
        self.base_url = os.getenv('GLPI_URL')
        self.app_token = os.getenv('GLPI_APP_TOKEN')
        self.user_token = os.getenv('GLPI_USER_TOKEN')
        self.session_token = None
        
        if not all([self.base_url, self.app_token, self.user_token]):
            raise ValueError("Variáveis de ambiente GLPI não configuradas")
    
    def authenticate(self):
        """Autenticar na API GLPI"""
        headers = {
            'Content-Type': 'application/json',
            'App-Token': self.app_token,
            'Authorization': f'user_token {self.user_token}'
        }
        
        try:
            response = requests.get(f"{self.base_url}/initSession", headers=headers)
            response.raise_for_status()
            
            data = response.json()
            self.session_token = data['session_token']
            logger.info("Autenticação bem-sucedida")
            return True
            
        except Exception as e:
            logger.error(f"Erro na autenticação: {e}")
            return False
    
    def get_headers(self):
        """Obter headers para requisições autenticadas"""
        return {
            'Content-Type': 'application/json',
            'App-Token': self.app_token,
            'Session-Token': self.session_token
        }
    
    def get_search_options(self):
        """Obter opções de busca disponíveis para tickets"""
        try:
            response = requests.get(
                f"{self.base_url}/listSearchOptions/Ticket",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao obter opções de busca: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao obter opções de busca: {e}")
            return None
    
    def get_sample_tickets(self, limit=5):
        """Obter alguns tickets de exemplo para análise"""
        params = {
            'is_deleted': 0,
            'range': f'0-{limit-1}'
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/search/Ticket",
                headers=self.get_headers(),
                params=params
            )
            
            if response.status_code in [200, 206]:
                data = response.json()
                return data.get('data', [])
            else:
                logger.error(f"Erro ao obter tickets: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Erro ao obter tickets: {e}")
            return []
    
    def get_ticket_details(self, ticket_id):
        """Obter detalhes completos de um ticket específico"""
        try:
            response = requests.get(
                f"{self.base_url}/Ticket/{ticket_id}",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao obter detalhes do ticket {ticket_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao obter detalhes do ticket {ticket_id}: {e}")
            return None
    
    def analyze_date_fields(self, search_options):
        """Analisar campos relacionados a data nas opções de busca"""
        date_fields = []
        
        for field_id, field_info in search_options.items():
            if isinstance(field_info, dict):
                field_name = field_info.get('name', '').lower()
                field_table = field_info.get('table', '')
                field_field = field_info.get('field', '')
                
                # Procurar por campos que podem ser de data
                if any(keyword in field_name for keyword in ['date', 'data', 'time', 'tempo', 'criação', 'creation']):
                    date_fields.append({
                        'id': field_id,
                        'name': field_info.get('name', ''),
                        'table': field_table,
                        'field': field_field,
                        'datatype': field_info.get('datatype', '')
                    })
        
        return date_fields
    
    def test_date_field(self, field_id, field_name):
        """Testar um campo específico para ver se contém datas válidas"""
        params = {
            'is_deleted': 0,
            'range': '0-4',  # Pegar 5 tickets
            'criteria[0][field]': str(field_id),
            'criteria[0][searchtype]': 'morethan',
            'criteria[0][value]': '2020/01/01'  # Usar formato que sabemos que funciona
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/search/Ticket",
                headers=self.get_headers(),
                params=params
            )
            
            if response.status_code in [200, 206]:
                content_range = response.headers.get('Content-Range')
                if content_range:
                    total = int(content_range.split('/')[-1])
                    
                    if total > 0:
                        data = response.json()
                        tickets = data.get('data', [])
                        
                        print(f"\nCampo {field_id} ({field_name}): {total} tickets encontrados")
                        
                        # Mostrar valores do campo para os primeiros tickets
                        for i, ticket in enumerate(tickets[:3]):
                            field_value = ticket.get(str(field_id), 'N/A')
                            ticket_id = ticket.get('2', 'N/A')
                            print(f"  Ticket {ticket_id}: {field_value}")
                        
                        return total
                    else:
                        print(f"\nCampo {field_id} ({field_name}): 0 tickets encontrados")
                        return 0
                else:
                    print(f"\nCampo {field_id} ({field_name}): Erro - sem Content-Range")
                    return -1
            else:
                print(f"\nCampo {field_id} ({field_name}): Erro HTTP {response.status_code}")
                return -1
                
        except Exception as e:
            print(f"\nCampo {field_id} ({field_name}): Erro - {e}")
            return -1
    
    def logout(self):
        """Encerrar sessão"""
        if self.session_token:
            try:
                requests.get(f"{self.base_url}/killSession", headers=self.get_headers())
                logger.info("Sessão encerrada")
            except:
                pass

def main():
    print("\n" + "="*80)
    print("ANÁLISE DA ESTRUTURA DOS TICKETS GLPI")
    print("="*80)
    
    analyzer = TicketStructureAnalyzer()
    
    try:
        # Autenticar
        if not analyzer.authenticate():
            return
        
        print("\n1. OBTENDO OPÇÕES DE BUSCA DISPONÍVEIS...")
        print("-" * 50)
        
        search_options = analyzer.get_search_options()
        if not search_options:
            print("❌ Não foi possível obter as opções de busca")
            return
        
        print(f"✅ {len(search_options)} opções de busca encontradas")
        
        print("\n2. ANALISANDO CAMPOS RELACIONADOS A DATA...")
        print("-" * 50)
        
        date_fields = analyzer.analyze_date_fields(search_options)
        
        if date_fields:
            print(f"\n📅 Campos de data encontrados ({len(date_fields)}):")
            for field in date_fields:
                print(f"  ID {field['id']}: {field['name']} (tabela: {field['table']}, campo: {field['field']}, tipo: {field['datatype']})")
        else:
            print("❌ Nenhum campo de data encontrado")
        
        print("\n3. OBTENDO TICKETS DE EXEMPLO...")
        print("-" * 50)
        
        sample_tickets = analyzer.get_sample_tickets(3)
        
        if sample_tickets:
            print(f"\n📋 Estrutura dos tickets (primeiros 3):")
            for i, ticket in enumerate(sample_tickets):
                ticket_id = ticket.get('2', 'N/A')
                print(f"\n  Ticket {ticket_id}:")
                
                # Mostrar todos os campos do ticket
                for field_id, value in ticket.items():
                    if field_id in search_options:
                        field_name = search_options[field_id].get('name', f'Campo {field_id}')
                        print(f"    {field_id}: {value} ({field_name})")
                    else:
                        print(f"    {field_id}: {value}")
                
                if i == 0:  # Só mostrar detalhes do primeiro ticket
                    print(f"\n  Detalhes completos do ticket {ticket_id}:")
                    details = analyzer.get_ticket_details(ticket_id)
                    if details:
                        # Procurar por campos de data nos detalhes
                        for key, value in details.items():
                            if isinstance(value, str) and any(keyword in key.lower() for keyword in ['date', 'data', 'time']):
                                print(f"    {key}: {value}")
        
        print("\n4. TESTANDO CAMPOS DE DATA IDENTIFICADOS...")
        print("-" * 50)
        
        if date_fields:
            for field in date_fields:
                analyzer.test_date_field(field['id'], field['name'])
        
        # Testar também alguns campos comuns conhecidos
        print("\n5. TESTANDO CAMPOS COMUNS DE DATA...")
        print("-" * 50)
        
        common_date_fields = [
            ('15', 'Data de criação (comum)'),
            ('19', 'Data de modificação (comum)'),
            ('60', 'Campo 60 (que estávamos usando)'),
            ('61', 'Campo 61'),
            ('62', 'Campo 62')
        ]
        
        for field_id, description in common_date_fields:
            analyzer.test_date_field(field_id, description)
        
        print("\n" + "="*80)
        print("RESUMO DA ANÁLISE")
        print("="*80)
        print("\nEsta análise nos ajudará a identificar:")
        print("1. Qual é o campo correto para data de criação")
        print("2. Como as datas são armazenadas no GLPI")
        print("3. Por que o campo 60 retorna None")
        print("4. Quais campos de data estão disponíveis")
        
    except Exception as e:
        logger.error(f"Erro durante a análise: {e}")
    finally:
        analyzer.logout()

if __name__ == "__main__":
    main()