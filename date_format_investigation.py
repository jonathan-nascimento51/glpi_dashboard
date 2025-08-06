#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Investigação específica dos formatos de data que funcionam na API GLPI
"""

import os
import sys
import requests
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DateFormatInvestigator:
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
    
    def test_date_filter_detailed(self, search_type, date_value, description):
        """Testar filtro de data com detalhes"""
        params = {
            'is_deleted': 0,
            'range': '0-2',  # Pegar alguns tickets para ver os dados
            'criteria[0][field]': '60',  # Campo data de criação
            'criteria[0][searchtype]': search_type,
            'criteria[0][value]': date_value
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/search/Ticket",
                headers=self.get_headers(),
                params=params
            )
            
            print(f"\n{description}:")
            print(f"  Parâmetro: {search_type} '{date_value}'")
            print(f"  Status HTTP: {response.status_code}")
            
            if response.status_code in [200, 206]:
                content_range = response.headers.get('Content-Range')
                if content_range:
                    total = int(content_range.split('/')[-1])
                    print(f"  Total encontrado: {total}")
                    
                    # Se encontrou tickets, mostrar alguns exemplos
                    if total > 0:
                        try:
                            data = response.json()
                            tickets = data.get('data', [])
                            print(f"  Exemplos de tickets encontrados:")
                            for i, ticket in enumerate(tickets[:3]):
                                ticket_id = ticket.get('2', 'N/A')
                                date_creation = ticket.get('60', 'N/A')
                                print(f"    Ticket {ticket_id}: {date_creation}")
                        except:
                            pass
                    
                    return total
                else:
                    try:
                        data = response.json()
                        total = data.get('totalcount', 0)
                        print(f"  Total do JSON: {total}")
                        return total
                    except:
                        print(f"  Nenhum resultado encontrado")
                        return 0
            else:
                print(f"  Erro HTTP: {response.status_code}")
                return -1
                
        except Exception as e:
            print(f"  Erro: {e}")
            return -1
    
    def get_total_tickets(self):
        """Obter total de tickets no sistema"""
        params = {'is_deleted': 0, 'range': '0-0'}
        
        try:
            response = requests.get(
                f"{self.base_url}/search/Ticket",
                headers=self.get_headers(),
                params=params
            )
            
            if response.status_code in [200, 206]:
                content_range = response.headers.get('Content-Range')
                if content_range:
                    return int(content_range.split('/')[-1])
                else:
                    data = response.json()
                    return data.get('totalcount', 0)
            return 0
        except:
            return 0
    
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
    print("INVESTIGAÇÃO DETALHADA - FORMATOS DE DATA QUE FUNCIONAM")
    print("="*80)
    
    investigator = DateFormatInvestigator()
    
    try:
        # Autenticar
        if not investigator.authenticate():
            return
        
        # Obter total de tickets
        total_tickets = investigator.get_total_tickets()
        print(f"\nTotal de tickets no sistema: {total_tickets}")
        
        print("\n" + "="*80)
        print("TESTANDO DIFERENTES FORMATOS E OPERADORES")
        print("="*80)
        
        # Teste 1: Formato que funcionou (com barras)
        print("\n1. FORMATO COM BARRAS (que funcionou):")
        print("-" * 50)
        
        # Testar diferentes datas com barras
        dates_with_slashes = [
            ('2020/01/01', 'Início de 2020'),
            ('2023/01/01', 'Início de 2023'),
            ('2024/01/01', 'Início de 2024'),
            ('2025/01/01', 'Início de 2025'),
            ('2025/08/01', 'Início de agosto 2025'),
            ('2025/08/05', 'Hoje (05/08/2025)'),
            ('2025/08/06', 'Amanhã (06/08/2025)')
        ]
        
        for date_val, desc in dates_with_slashes:
            investigator.test_date_filter_detailed('morethan', date_val, f"Tickets após {desc}")
        
        print("\n2. TESTANDO OPERADOR 'lessthan' COM BARRAS:")
        print("-" * 50)
        
        for date_val, desc in dates_with_slashes:
            investigator.test_date_filter_detailed('lessthan', date_val, f"Tickets antes de {desc}")
        
        print("\n3. TESTANDO OPERADOR 'equals' COM BARRAS:")
        print("-" * 50)
        
        # Testar equals com algumas datas específicas
        test_dates = ['2025/08/05', '2025/08/04', '2025/08/03', '2024/12/31']
        for date_val in test_dates:
            investigator.test_date_filter_detailed('equals', date_val, f"Tickets criados em {date_val}")
        
        print("\n4. COMPARANDO FORMATOS (mesmo operador, formatos diferentes):")
        print("-" * 50)
        
        # Comparar o mesmo filtro com formatos diferentes
        test_date = '2024-01-01'  # Data de referência
        formats_to_compare = [
            ('2024-01-01', 'Formato ISO (YYYY-MM-DD)'),
            ('2024/01/01', 'Formato com barras (YYYY/MM/DD)'),
            ('01/01/2024', 'Formato americano (MM/DD/YYYY)'),
            ('2024-1-1', 'Formato sem zeros'),
            ('2024-01-01 00:00:00', 'Formato com hora')
        ]
        
        for date_format, description in formats_to_compare:
            investigator.test_date_filter_detailed('morethan', date_format, f"morethan {description}")
        
        print("\n" + "="*80)
        print("CONCLUSÕES")
        print("="*80)
        print("\nBaseado nos testes acima, podemos identificar:")
        print("1. Quais formatos de data funcionam")
        print("2. Quais operadores funcionam")
        print("3. Como a API interpreta as datas")
        print("4. Por que alguns filtros retornam 0 e outros não")
        
    except Exception as e:
        logger.error(f"Erro durante a investigação: {e}")
    finally:
        investigator.logout()

if __name__ == "__main__":
    main()