#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste simples e direto para investigar filtros de data na API GLPI
"""

import os
import sys
import requests
import logging
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

class SimpleGLPITester:
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
    
    def get_sample_tickets(self, limit=5):
        """Obter amostra de tickets para ver as datas reais"""
        params = {
            'is_deleted': 0,
            'range': f'0-{limit-1}',
            'sort': 60,  # Campo data de criação
            'order': 'DESC'  # Mais recentes primeiro
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/search/Ticket",
                headers=self.get_headers(),
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            tickets = data.get('data', [])
            
            print(f"\nAMOSTRA DE {len(tickets)} TICKETS MAIS RECENTES:")
            print("-" * 50)
            
            for ticket in tickets:
                ticket_id = ticket.get('2', 'N/A')  # ID do ticket
                date_creation = ticket.get('60', 'N/A')  # Data de criação
                status = ticket.get('12', 'N/A')  # Status
                print(f"Ticket {ticket_id}: {date_creation} (Status: {status})")
            
            return tickets
            
        except Exception as e:
            logger.error(f"Erro ao obter amostra de tickets: {e}")
            return []
    
    def test_date_filter(self, search_type, date_value):
        """Testar filtro de data específico"""
        params = {
            'is_deleted': 0,
            'range': '0-0',  # Só queremos o total
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
            
            logger.info(f"Teste {search_type} {date_value}: Status {response.status_code}")
            
            if response.status_code in [200, 206]:  # 206 = Partial Content
                content_range = response.headers.get('Content-Range')
                if content_range:
                    total = int(content_range.split('/')[-1])
                    logger.info(f"Content-Range: {content_range}, Total: {total}")
                    return total
                else:
                    # Tentar obter do JSON se não há Content-Range
                    try:
                        data = response.json()
                        total = data.get('totalcount', 0)
                        logger.info(f"Total do JSON: {total}")
                        return total
                    except:
                        # Se não há Content-Range nem totalcount, pode ser que não há resultados
                        return 0
            else:
                logger.error(f"Erro HTTP {response.status_code}: {response.text[:200]}")
                return -1
                
        except Exception as e:
            logger.error(f"Erro ao testar filtro {search_type} {date_value}: {e}")
            return -1
    
    def count_all_tickets(self):
        """Contar todos os tickets (sem filtro de data)"""
        params = {
            'is_deleted': 0,
            'range': '0-0'
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/search/Ticket",
                headers=self.get_headers(),
                params=params
            )
            
            logger.info(f"Count all tickets - Status: {response.status_code}")
            logger.info(f"Headers: {dict(response.headers)}")
            
            if response.status_code in [200, 206]:  # 206 = Partial Content
                content_range = response.headers.get('Content-Range')
                if content_range:
                    total = int(content_range.split('/')[-1])
                    logger.info(f"Content-Range: {content_range}, Total: {total}")
                    return total
                else:
                    # Tentar obter do JSON se não há Content-Range
                    try:
                        data = response.json()
                        total = data.get('totalcount', 0)
                        logger.info(f"Total do JSON: {total}")
                        return total
                    except:
                        pass
            return 0
            
        except Exception as e:
            logger.error(f"Erro ao contar todos os tickets: {e}")
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
    print("\n" + "="*70)
    print("TESTE SIMPLES E DIRETO - FILTROS DE DATA GLPI")
    print("="*70)
    
    tester = SimpleGLPITester()
    
    try:
        # 1. Autenticar
        if not tester.authenticate():
            return
        
        # 2. Contar todos os tickets primeiro
        print("\n1. CONTAGEM TOTAL (SEM FILTROS)")
        print("-" * 40)
        total_all = tester.count_all_tickets()
        print(f"Total de tickets no sistema: {total_all}")
        
        # 3. Obter amostra de tickets para ver datas reais
        print("\n2. AMOSTRA DE TICKETS RECENTES")
        print("-" * 40)
        sample_tickets = tester.get_sample_tickets(10)
        
        # 4. Testar filtros de data com diferentes abordagens
        print("\n3. TESTES DE FILTROS DE DATA")
        print("-" * 40)
        
        # Teste com datas muito amplas
        print("\nTeste 1: Datas muito amplas")
        result1 = tester.test_date_filter('morethan', '1990-01-01')
        print(f"Tickets após 1990-01-01: {result1}")
        
        result2 = tester.test_date_filter('lessthan', '2030-12-31')
        print(f"Tickets antes de 2030-12-31: {result2}")
        
        # Teste com ano atual
        current_year = datetime.now().year
        print(f"\nTeste 2: Ano atual ({current_year})")
        result3 = tester.test_date_filter('morethan', f'{current_year}-01-01')
        print(f"Tickets após {current_year}-01-01: {result3}")
        
        result4 = tester.test_date_filter('lessthan', f'{current_year}-12-31')
        print(f"Tickets antes de {current_year}-12-31: {result4}")
        
        # Teste com data de hoje
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"\nTeste 3: Data de hoje ({today})")
        result5 = tester.test_date_filter('equals', today)
        print(f"Tickets criados hoje: {result5}")
        
        # Teste com diferentes formatos
        print("\nTeste 4: Diferentes formatos de data")
        formats_to_test = [
            ('2024-01-01', 'YYYY-MM-DD'),
            ('2024/01/01', 'YYYY/MM/DD'),
            ('01/01/2024', 'DD/MM/YYYY'),
            ('2024-1-1', 'YYYY-M-D'),
            ('2024-01-01 00:00:00', 'YYYY-MM-DD HH:MM:SS')
        ]
        
        for date_format, description in formats_to_test:
            result = tester.test_date_filter('morethan', date_format)
            print(f"Formato {description} ({date_format}): {result} tickets")
        
        # Resumo
        print("\n" + "="*70)
        print("RESUMO DOS RESULTADOS")
        print("="*70)
        print(f"Total de tickets no sistema: {total_all}")
        print(f"Tickets após 1990-01-01: {result1}")
        print(f"Tickets antes de 2030-12-31: {result2}")
        print(f"Tickets após {current_year}-01-01: {result3}")
        print(f"Tickets antes de {current_year}-12-31: {result4}")
        print(f"Tickets criados hoje: {result5}")
        
        # Análise
        print("\nANÁLISE:")
        if result1 == 0 and result2 == 0 and total_all > 0:
            print("❌ PROBLEMA: Filtros de data não estão funcionando!")
            print("   Todos os filtros retornam 0, mas existem tickets no sistema.")
        elif result1 > 0 or result2 > 0:
            print("✅ SUCESSO: Pelo menos alguns filtros de data funcionam!")
        else:
            print("⚠️  INCONCLUSIVO: Não há tickets suficientes para testar.")
        
    except Exception as e:
        logger.error(f"Erro durante o teste: {e}")
    finally:
        tester.logout()

if __name__ == "__main__":
    main()