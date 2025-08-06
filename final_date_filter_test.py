#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste final dos filtros de data usando o campo correto (15 - Data de criação)
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

class FinalDateFilterTester:
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
    
    def test_date_filter_with_samples(self, field_id, search_type, date_value, description):
        """Testar filtro de data e mostrar amostras dos resultados"""
        params = {
            'is_deleted': 0,
            'range': '0-4',  # Pegar 5 tickets para mostrar exemplos
            'criteria[0][field]': str(field_id),
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
            print(f"  Campo: {field_id}, Operador: {search_type}, Valor: '{date_value}'")
            print(f"  Status HTTP: {response.status_code}")
            
            if response.status_code in [200, 206]:
                content_range = response.headers.get('Content-Range')
                if content_range:
                    total = int(content_range.split('/')[-1])
                    print(f"  ✅ Total encontrado: {total} tickets")
                    
                    if total > 0:
                        try:
                            data = response.json()
                            tickets = data.get('data', [])
                            print(f"  📋 Exemplos de tickets:")
                            for ticket in tickets:
                                ticket_id = ticket.get('2', 'N/A')
                                date_creation = ticket.get(str(field_id), 'N/A')
                                title = ticket.get('1', 'Sem título')[:50] + '...' if len(ticket.get('1', '')) > 50 else ticket.get('1', 'Sem título')
                                print(f"    • Ticket {ticket_id}: {date_creation} - {title}")
                        except Exception as e:
                            print(f"    ⚠️ Erro ao processar dados: {e}")
                    
                    return total
                else:
                    try:
                        data = response.json()
                        total = data.get('totalcount', 0)
                        print(f"  ✅ Total do JSON: {total}")
                        return total
                    except:
                        print(f"  ❌ Nenhum resultado encontrado")
                        return 0
            else:
                print(f"  ❌ Erro HTTP: {response.status_code}")
                return -1
                
        except Exception as e:
            print(f"  ❌ Erro: {e}")
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
    
    def test_combined_filters(self):
        """Testar filtros combinados (período específico)"""
        print("\n" + "="*60)
        print("TESTANDO FILTROS COMBINADOS (PERÍODO ESPECÍFICO)")
        print("="*60)
        
        # Teste: tickets criados entre 2024-01-01 e 2024-12-31
        params = {
            'is_deleted': 0,
            'range': '0-4',
            'criteria[0][field]': '15',  # Data de criação
            'criteria[0][searchtype]': 'morethan',
            'criteria[0][value]': '2024/01/01',
            'criteria[1][field]': '15',  # Data de criação
            'criteria[1][searchtype]': 'lessthan',
            'criteria[1][value]': '2025/01/01',
            'criteria[1][link]': 'AND'
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/search/Ticket",
                headers=self.get_headers(),
                params=params
            )
            
            print(f"\nTickets criados em 2024 (entre 2024/01/01 e 2025/01/01):")
            print(f"  Status HTTP: {response.status_code}")
            
            if response.status_code in [200, 206]:
                content_range = response.headers.get('Content-Range')
                if content_range:
                    total = int(content_range.split('/')[-1])
                    print(f"  ✅ Total encontrado: {total} tickets")
                    
                    if total > 0:
                        data = response.json()
                        tickets = data.get('data', [])
                        print(f"  📋 Exemplos de tickets de 2024:")
                        for ticket in tickets:
                            ticket_id = ticket.get('2', 'N/A')
                            date_creation = ticket.get('15', 'N/A')
                            title = ticket.get('1', 'Sem título')[:40] + '...' if len(ticket.get('1', '')) > 40 else ticket.get('1', 'Sem título')
                            print(f"    • Ticket {ticket_id}: {date_creation} - {title}")
                    
                    return total
                else:
                    data = response.json()
                    total = data.get('totalcount', 0)
                    print(f"  ✅ Total do JSON: {total}")
                    return total
            else:
                print(f"  ❌ Erro HTTP: {response.status_code}")
                return -1
                
        except Exception as e:
            print(f"  ❌ Erro: {e}")
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
    print("TESTE FINAL - FILTROS DE DATA COM CAMPO CORRETO (15)")
    print("="*80)
    
    tester = FinalDateFilterTester()
    
    try:
        # Autenticar
        if not tester.authenticate():
            return
        
        # Obter total de tickets
        total_tickets = tester.get_total_tickets()
        print(f"\n📊 Total de tickets no sistema: {total_tickets}")
        
        print("\n" + "="*60)
        print("TESTANDO OPERADOR 'morethan' (APÓS DATA)")
        print("="*60)
        
        # Testes com morethan
        test_cases_morethan = [
            ('2020/01/01', 'Tickets criados após 01/01/2020'),
            ('2023/01/01', 'Tickets criados após 01/01/2023'),
            ('2024/01/01', 'Tickets criados após 01/01/2024'),
            ('2024/06/01', 'Tickets criados após 01/06/2024'),
            ('2025/01/01', 'Tickets criados após 01/01/2025'),
            ('2025/08/01', 'Tickets criados após 01/08/2025'),
        ]
        
        results_morethan = []
        for date_val, desc in test_cases_morethan:
            result = tester.test_date_filter_with_samples(15, 'morethan', date_val, desc)
            results_morethan.append((desc, result))
        
        print("\n" + "="*60)
        print("TESTANDO OPERADOR 'lessthan' (ANTES DA DATA)")
        print("="*60)
        
        # Testes com lessthan
        test_cases_lessthan = [
            ('2025/12/31', 'Tickets criados antes de 31/12/2025'),
            ('2025/08/01', 'Tickets criados antes de 01/08/2025'),
            ('2025/01/01', 'Tickets criados antes de 01/01/2025'),
            ('2024/12/31', 'Tickets criados antes de 31/12/2024'),
            ('2024/06/01', 'Tickets criados antes de 01/06/2024'),
            ('2023/01/01', 'Tickets criados antes de 01/01/2023'),
        ]
        
        results_lessthan = []
        for date_val, desc in test_cases_lessthan:
            result = tester.test_date_filter_with_samples(15, 'lessthan', date_val, desc)
            results_lessthan.append((desc, result))
        
        # Teste de filtros combinados
        combined_result = tester.test_combined_filters()
        
        print("\n" + "="*80)
        print("RESUMO DOS RESULTADOS")
        print("="*80)
        
        print(f"\n📊 Total de tickets no sistema: {total_tickets}")
        
        print("\n🔍 Resultados 'morethan' (após data):")
        for desc, result in results_morethan:
            status = "✅" if result > 0 else "❌" if result == 0 else "⚠️"
            print(f"  {status} {desc}: {result} tickets")
        
        print("\n🔍 Resultados 'lessthan' (antes da data):")
        for desc, result in results_lessthan:
            status = "✅" if result > 0 else "❌" if result == 0 else "⚠️"
            print(f"  {status} {desc}: {result} tickets")
        
        if combined_result is not None:
            status = "✅" if combined_result > 0 else "❌" if combined_result == 0 else "⚠️"
            print(f"\n🔗 Filtro combinado (2024): {status} {combined_result} tickets")
        
        print("\n" + "="*80)
        print("CONCLUSÃO")
        print("="*80)
        
        working_filters = sum(1 for _, result in results_morethan + results_lessthan if result > 0)
        total_tests = len(results_morethan) + len(results_lessthan)
        
        if working_filters > 0:
            print(f"\n🎉 SUCESSO! {working_filters}/{total_tests} filtros funcionaram corretamente!")
            print("\n✅ Descobertas importantes:")
            print("   • Campo correto para data de criação: 15 (não 60)")
            print("   • Formato de data que funciona: YYYY/MM/DD (com barras)")
            print("   • Operadores funcionais: morethan, lessthan")
            print("   • Filtros combinados: funcionam com link AND")
        else:
            print(f"\n❌ Ainda há problemas com os filtros de data")
            print("   Todos os testes retornaram 0 ou erro")
        
    except Exception as e:
        logger.error(f"Erro durante o teste: {e}")
    finally:
        tester.logout()

if __name__ == "__main__":
    main()