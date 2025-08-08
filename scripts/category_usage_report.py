#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para gerar relatório de uso de categorias no GLPI
Este script cria um relatório detalhado sobre como as categorias são utilizadas
"""

import requests
import json
import sys
import os
from typing import Dict, Any, Optional, List
from collections import Counter, defaultdict
from datetime import datetime, timedelta

# Adicionar o diretório backend ao path para importar as configurações
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from config.settings import active_config

class GLPICategoryReporter:
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
    
    def get_all_categories(self) -> Dict[str, Dict]:
        """Obtém todas as categorias disponíveis"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Session-Token': self.session_token,
                'App-Token': self.app_token
            }
            
            response = requests.get(
                f"{self.glpi_url}/ITILCategory",
                headers=headers,
                params={'range': '0-2000'}  # Buscar muitas categorias
            )
            
            if response.status_code == 200:
                categories = response.json()
                return {str(cat['id']): cat for cat in categories}
            else:
                print(f"✗ Erro ao obter categorias: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"✗ Erro ao obter categorias: {e}")
            return {}
    
    def count_tickets_by_category(self, category_id: str, days_back: int = 30) -> int:
        """Conta tickets de uma categoria nos últimos N dias"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Session-Token': self.session_token,
                'App-Token': self.app_token
            }
            
            # Data de início (N dias atrás)
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            search_params = {
                'is_deleted': 0,
                'range': '0-0',  # Apenas contagem
                'criteria[0][field]': '7',  # Campo categoria
                'criteria[0][searchtype]': 'equals',
                'criteria[0][value]': category_id,
                'criteria[1][link]': 'AND',
                'criteria[1][field]': '15',  # Data de criação
                'criteria[1][searchtype]': 'morethan',
                'criteria[1][value]': start_date,
            }
            
            response = requests.get(
                f"{self.glpi_url}/search/Ticket",
                headers=headers,
                params=search_params
            )
            
            if response.status_code == 200:
                if "Content-Range" in response.headers:
                    total = int(response.headers["Content-Range"].split("/")[-1])
                    return total
                return 0
            else:
                return 0
                
        except Exception as e:
            print(f"✗ Erro ao contar tickets da categoria {category_id}: {e}")
            return 0
    
    def get_category_hierarchy(self, categories: Dict[str, Dict]) -> Dict[str, List]:
        """Organiza categorias por hierarquia"""
        hierarchy = defaultdict(list)
        
        for cat_id, category in categories.items():
            level = category.get('level', 1)
            complete_name = category.get('completename', category.get('name', ''))
            
            if level == 1:
                hierarchy['root'].append({
                    'id': cat_id,
                    'name': category.get('name', ''),
                    'complete_name': complete_name
                })
            else:
                parent_parts = complete_name.split(' > ')[:-1]
                parent_name = ' > '.join(parent_parts) if parent_parts else 'root'
                hierarchy[parent_name].append({
                    'id': cat_id,
                    'name': category.get('name', ''),
                    'complete_name': complete_name,
                    'level': level
                })
        
        return hierarchy
    
    def generate_usage_report(self, days_back: int = 30) -> None:
        """Gera relatório completo de uso de categorias"""
        print(f"\n=== RELATÓRIO DE USO DE CATEGORIAS (ÚLTIMOS {days_back} DIAS) ===")
        
        # Obter todas as categorias
        print("Obtendo categorias...")
        categories = self.get_all_categories()
        
        if not categories:
            print("✗ Não foi possível obter as categorias")
            return
        
        print(f"✓ {len(categories)} categorias encontradas")
        
        # Contar tickets por categoria
        print("Contando tickets por categoria...")
        category_usage = []
        
        for cat_id, category in categories.items():
            ticket_count = self.count_tickets_by_category(cat_id, days_back)
            
            if ticket_count > 0:  # Apenas categorias com tickets
                category_usage.append({
                    'id': cat_id,
                    'name': category.get('name', ''),
                    'complete_name': category.get('completename', ''),
                    'level': category.get('level', 1),
                    'ticket_count': ticket_count
                })
        
        # Ordenar por uso (decrescente)
        category_usage.sort(key=lambda x: x['ticket_count'], reverse=True)
        
        print(f"\n=== CATEGORIAS MAIS UTILIZADAS ===")
        print(f"Total de categorias com tickets: {len(category_usage)}")
        print(f"Total de categorias sem tickets: {len(categories) - len(category_usage)}")
        
        # Top 20 categorias
        print(f"\nTop 20 categorias mais utilizadas:")
        total_tickets = sum(cat['ticket_count'] for cat in category_usage)
        
        for i, category in enumerate(category_usage[:20], 1):
            percentage = (category['ticket_count'] / total_tickets * 100) if total_tickets > 0 else 0
            print(f"{i:2d}. {category['complete_name'][:60]:<60} | {category['ticket_count']:4d} tickets ({percentage:5.1f}%)")
        
        # Análise por nível
        print(f"\n=== ANÁLISE POR NÍVEL DE CATEGORIA ===")
        level_stats = defaultdict(lambda: {'count': 0, 'tickets': 0})
        
        for category in category_usage:
            level = category['level']
            level_stats[level]['count'] += 1
            level_stats[level]['tickets'] += category['ticket_count']
        
        for level in sorted(level_stats.keys()):
            stats = level_stats[level]
            avg_tickets = stats['tickets'] / stats['count'] if stats['count'] > 0 else 0
            print(f"Nível {level}: {stats['count']} categorias, {stats['tickets']} tickets (média: {avg_tickets:.1f} tickets/categoria)")
        
        # Categorias sem uso
        unused_categories = [cat for cat in categories.values() if cat['id'] not in [c['id'] for c in category_usage]]
        
        if unused_categories:
            print(f"\n=== CATEGORIAS SEM USO (ÚLTIMOS {days_back} DIAS) ===")
            print(f"Total: {len(unused_categories)} categorias")
            
            # Mostrar algumas categorias sem uso
            print("Exemplos de categorias sem tickets:")
            for category in unused_categories[:10]:
                complete_name = category.get('completename', category.get('name', ''))
                print(f"  - {complete_name}")
            
            if len(unused_categories) > 10:
                print(f"  ... e mais {len(unused_categories) - 10} categorias")
        
        # Salvar relatório em arquivo
        self.save_report_to_file(category_usage, unused_categories, days_back)
    
    def save_report_to_file(self, category_usage: List[Dict], unused_categories: List[Dict], days_back: int) -> None:
        """Salva o relatório em arquivo JSON"""
        try:
            report_data = {
                'generated_at': datetime.now().isoformat(),
                'period_days': days_back,
                'summary': {
                    'total_categories': len(category_usage) + len(unused_categories),
                    'categories_with_tickets': len(category_usage),
                    'categories_without_tickets': len(unused_categories),
                    'total_tickets': sum(cat['ticket_count'] for cat in category_usage)
                },
                'categories_with_usage': category_usage,
                'categories_without_usage': [
                    {
                        'id': cat['id'],
                        'name': cat.get('name', ''),
                        'complete_name': cat.get('completename', ''),
                        'level': cat.get('level', 1)
                    } for cat in unused_categories
                ]
            }
            
            # Salvar no diretório scripts
            report_file = os.path.join(os.path.dirname(__file__), f'category_usage_report_{days_back}days.json')
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n✓ Relatório salvo em: {report_file}")
            
        except Exception as e:
            print(f"✗ Erro ao salvar relatório: {e}")
    
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
    print("=== GERADOR DE RELATÓRIO DE USO DE CATEGORIAS ===")
    print("Este script gera um relatório detalhado sobre o uso de categorias no GLPI\n")
    
    # Permitir especificar período via argumento
    days_back = 30
    if len(sys.argv) > 1:
        try:
            days_back = int(sys.argv[1])
            print(f"Período personalizado: {days_back} dias")
        except ValueError:
            print("Argumento inválido, usando 30 dias por padrão")
    
    reporter = GLPICategoryReporter()
    
    # Autenticar
    if not reporter.authenticate():
        return
    
    try:
        # Gerar relatório
        reporter.generate_usage_report(days_back)
        
        print("\n=== INSTRUÇÕES DE USO ===")
        print("1. Execute este script regularmente para monitorar o uso de categorias")
        print("2. Use o argumento para especificar período: python category_usage_report.py 7")
        print("3. Analise categorias sem uso para possível limpeza")
        print("4. Monitore as categorias mais utilizadas para otimização")
        
    finally:
        reporter.close_session()

if __name__ == "__main__":
    main()