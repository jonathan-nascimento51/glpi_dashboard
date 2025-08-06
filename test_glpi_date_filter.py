#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Teste Isolado - Filtro de Data GLPI

Testa a aplicação de filtros de data nas consultas:
1. Total de tickets por status e nível (N1-N4)
2. Ranking de técnicos

Uso: python test_glpi_date_filter.py
"""

import os
import sys
import requests
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from pprint import pprint
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GLPITestService:
    """Serviço simplificado para teste de filtros de data no GLPI"""
    
    def __init__(self):
        # Configurações da API GLPI
        self.glpi_url = os.environ.get('GLPI_URL', 'http://10.73.0.79/glpi/apirest.php')
        self.app_token = os.environ.get('GLPI_APP_TOKEN')
        self.user_token = os.environ.get('GLPI_USER_TOKEN')
        
        if not self.app_token or not self.user_token:
            logger.error("GLPI_APP_TOKEN e GLPI_USER_TOKEN devem estar configurados no .env")
            sys.exit(1)
        
        # Mapeamentos (conforme serviço original)
        self.status_map = {
            "Novo": 1,
            "Atribuído": 2,  # Processando (atribuído)
            "Pendente": 4,
            "Resolvido": 5   # Solucionado
        }
        
        self.service_levels = {
            "N1": 89,
            "N2": 90,
            "N3": 91,
            "N4": 92
        }
        
        # Controle de sessão
        self.session_token = None
        self.field_ids = {}
    
    def authenticate(self) -> bool:
        """Autentica na API GLPI"""
        headers = {
            "Content-Type": "application/json",
            "App-Token": self.app_token,
            "Authorization": f"user_token {self.user_token}"
        }
        
        try:
            logger.info("Autenticando na API GLPI...")
            response = requests.get(f"{self.glpi_url}/initSession", headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.session_token = data["session_token"]
            logger.info("Autenticacao bem-sucedida!")
            return True
            
        except Exception as e:
            logger.error(f"Falha na autenticação: {e}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Retorna headers para requisições autenticadas"""
        return {
            "Session-Token": self.session_token,
            "App-Token": self.app_token,
            "Content-Type": "application/json"
        }
    
    def discover_field_ids(self) -> bool:
        """Descobre IDs dos campos necessários usando nomes exatos"""
        try:
            logger.info("Descobrindo IDs dos campos...")
            response = requests.get(
                f"{self.glpi_url}/listSearchOptions/Ticket",
                headers=self.get_headers(),
                timeout=10
            )
            response.raise_for_status()
            search_options = response.json()
            
            # Nomes exatos dos campos (conforme serviço original)
            target_fields = {
                "Grupo técnico": "GROUP",
                "Status": "STATUS",
                "Data de criação": "DATE_CREATION",
                "Técnico": "TECHNICIAN",
                "Atribuído para": "TECHNICIAN"  # Nome alternativo
            }
            
            # Buscar campos necessários por nome exato
            for field_id, field_data in search_options.items():
                if isinstance(field_data, dict) and "name" in field_data:
                    field_name = field_data["name"]
                    if field_name in target_fields:
                        field_key = target_fields[field_name]
                        if field_key not in self.field_ids:  # Evita sobrescrever
                            self.field_ids[field_key] = field_id
                            logger.info(f"Campo '{field_name}' encontrado: ID {field_id}")
            
            # Verificar campos obrigatórios
            required_fields = ["GROUP", "STATUS", "DATE_CREATION"]
            missing_fields = [f for f in required_fields if f not in self.field_ids]
            
            if missing_fields:
                logger.error(f"Campos obrigatórios não encontrados: {missing_fields}")
                # Debug: mostrar todos os campos disponíveis
                logger.info("Campos disponíveis:")
                for field_id, field_data in search_options.items():
                    if isinstance(field_data, dict) and "name" in field_data:
                        logger.info(f"ID {field_id}: {field_data['name']}")
                return False
            
            logger.info("Todos os campos necessários foram descobertos!")
            logger.info(f"Campos mapeados: {self.field_ids}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao descobrir campos: {e}")
            return False
    
    def parse_date_filter(self, date_filter: str) -> tuple:
        """Converte filtro de data em datas início/fim"""
        today = datetime.now()
        
        if date_filter == "today":
            start_date = today.strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
        elif date_filter == "last_7_days":
            start_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
        elif date_filter == "last_30_days":
            start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
        else:
            logger.error(f"Filtro de data inválido: {date_filter}")
            return None, None
        
        return start_date, end_date
    
    def get_ticket_count_no_filter(self, group_id: int, status_id: int) -> int:
        """Conta tickets sem filtro de data (para teste)"""
        params = {
            "is_deleted": 0,
            "range": "0-0",  # Só queremos o total
            "criteria[0][field]": self.field_ids["GROUP"],
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": group_id,
            "criteria[1][link]": "AND",
            "criteria[1][field]": self.field_ids["STATUS"],
            "criteria[1][searchtype]": "equals",
            "criteria[1][value]": status_id
        }
        
        logger.debug(f"Teste SEM filtro - Grupo: {group_id}, Status: {status_id}")
        
        try:
            response = requests.get(
                f"{self.glpi_url}/search/Ticket",
                headers=self.get_headers(),
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            if "Content-Range" in response.headers:
                content_range = response.headers["Content-Range"]
                total = int(content_range.split("/")[-1])
                logger.debug(f"SEM filtro - Total: {total}")
                return total
            
            return 0
            
        except Exception as e:
            logger.error(f"Erro ao contar tickets sem filtro: {e}")
            return 0
    
    def get_ticket_count_with_filter(self, group_id: int, status_id: int, start_date: str, end_date: str) -> int:
        """Conta tickets com filtros de grupo, status e data"""
        params = {
            "is_deleted": 0,
            "range": "0-0",  # Só queremos o total
            "criteria[0][field]": self.field_ids["GROUP"],
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": group_id,
            "criteria[1][link]": "AND",
            "criteria[1][field]": self.field_ids["STATUS"],
            "criteria[1][searchtype]": "equals",
            "criteria[1][value]": status_id,
            "criteria[2][link]": "AND",
            "criteria[2][field]": self.field_ids["DATE_CREATION"],
            "criteria[2][searchtype]": "morethan",
            "criteria[2][value]": start_date,
            "criteria[3][link]": "AND",
            "criteria[3][field]": self.field_ids["DATE_CREATION"],
            "criteria[3][searchtype]": "lessthan",
            "criteria[3][value]": end_date
        }
        
        # Debug: log dos parâmetros de busca
        logger.debug(f"Buscando tickets - Grupo: {group_id}, Status: {status_id}")
        logger.debug(f"Período: {start_date} até {end_date}")
        logger.debug(f"Parâmetros: {params}")
        
        try:
            response = requests.get(
                f"{self.glpi_url}/search/Ticket",
                headers=self.get_headers(),
                params=params,
                timeout=10
            )
            
            logger.debug(f"Status da resposta: {response.status_code}")
            logger.debug(f"Headers da resposta: {dict(response.headers)}")
            
            response.raise_for_status()
            
            # O total vem no header Content-Range
            if "Content-Range" in response.headers:
                content_range = response.headers["Content-Range"]
                total = int(content_range.split("/")[-1])
                logger.debug(f"Content-Range: {content_range}, Total: {total}")
                return total
            
            logger.debug("Header Content-Range não encontrado")
            return 0
            
        except Exception as e:
            logger.error(f"Erro ao contar tickets: {e}")
            return 0
    
    def get_technician_ranking_with_filter(self, start_date: str, end_date: str, limit: int = 10) -> List[Dict]:
        """Obtém ranking de técnicos com filtro de data"""
        if "TECHNICIAN" not in self.field_ids:
            logger.warning("Campo de técnico não encontrado, pulando ranking")
            return []
        
        params = {
            "is_deleted": 0,
            "range": f"0-{limit-1}",
            "criteria[0][field]": self.field_ids["DATE_CREATION"],
            "criteria[0][searchtype]": "morethan",
            "criteria[0][value]": start_date,
            "criteria[1][link]": "AND",
            "criteria[1][field]": self.field_ids["DATE_CREATION"],
            "criteria[1][searchtype]": "lessthan",
            "criteria[1][value]": end_date,
            "forcedisplay[0]": self.field_ids["TECHNICIAN"],
            "sort": self.field_ids["TECHNICIAN"],
            "order": "ASC"
        }
        
        try:
            response = requests.get(
                f"{self.glpi_url}/search/Ticket",
                headers=self.get_headers(),
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Processar dados para criar ranking
            technician_counts = {}
            if "data" in data:
                for ticket in data["data"]:
                    tech_field = str(self.field_ids["TECHNICIAN"])
                    if tech_field in ticket:
                        tech_name = ticket[tech_field]
                        if tech_name and tech_name != "0":
                            technician_counts[tech_name] = technician_counts.get(tech_name, 0) + 1
            
            # Converter para lista ordenada
            ranking = [
                {"nome": name, "total": count, "rank": idx + 1}
                for idx, (name, count) in enumerate(
                    sorted(technician_counts.items(), key=lambda x: x[1], reverse=True)
                )
            ]
            
            return ranking[:limit]
            
        except Exception as e:
            logger.error(f"Erro ao obter ranking de técnicos: {e}")
            return []
    
    def test_date_format(self, start_date: str, end_date: str) -> int:
        """Testa um formato específico de data"""
        params = {
            "is_deleted": 0,
            "range": "0-0",  # Só queremos o total
            "criteria[0][field]": self.field_ids["DATE_CREATION"],
            "criteria[0][searchtype]": "morethan",
            "criteria[0][value]": start_date,
            "criteria[1][link]": "AND",
            "criteria[1][field]": self.field_ids["DATE_CREATION"],
            "criteria[1][searchtype]": "lessthan",
            "criteria[1][value]": end_date
        }
        
        logger.debug(f"Testando formato - Início: {start_date}, Fim: {end_date}")
        logger.debug(f"Parâmetros: {params}")
        
        try:
            response = requests.get(
                f"{self.glpi_url}/search/Ticket",
                headers=self.get_headers(),
                params=params,
                timeout=10
            )
            
            logger.debug(f"Status da resposta: {response.status_code}")
            logger.debug(f"Headers da resposta: {dict(response.headers)}")
            
            response.raise_for_status()
            
            # O total vem no header Content-Range
            if "Content-Range" in response.headers:
                content_range = response.headers["Content-Range"]
                total = int(content_range.split("/")[-1])
                logger.debug(f"Content-Range: {content_range}, Total: {total}")
                return total
            
            logger.debug("Header Content-Range não encontrado")
            return 0
            
        except Exception as e:
            logger.error(f"Erro ao testar formato de data: {e}")
            return 0
    
    def test_single_date_criteria(self, search_type: str, date_value: str) -> int:
        """Testa um único critério de data (morethan ou lessthan)"""
        params = {
            "is_deleted": 0,
            "range": "0-0",  # Só queremos o total
            "criteria[0][field]": self.field_ids["DATE_CREATION"],
            "criteria[0][searchtype]": search_type,
            "criteria[0][value]": date_value
        }
        
        logger.debug(f"Testando critério único - Tipo: {search_type}, Valor: {date_value}")
        logger.debug(f"Parâmetros: {params}")
        
        try:
            response = requests.get(
                f"{self.glpi_url}/search/Ticket",
                headers=self.get_headers(),
                params=params,
                timeout=10
            )
            
            logger.debug(f"Status da resposta: {response.status_code}")
            logger.debug(f"Headers da resposta: {dict(response.headers)}")
            
            response.raise_for_status()
            
            # O total vem no header Content-Range
            if "Content-Range" in response.headers:
                content_range = response.headers["Content-Range"]
                total = int(content_range.split("/")[-1])
                logger.debug(f"Content-Range: {content_range}, Total: {total}")
                return total
            
            logger.debug("Header Content-Range não encontrado")
            return 0
            
        except Exception as e:
            logger.error(f"Erro ao testar critério único de data: {e}")
            return 0
    
    def test_contains_date_criteria(self, prefix: str, date_value: str) -> int:
        """Testa critério de data usando 'contains' com prefixos > ou <"""
        params = {
            "is_deleted": 0,
            "range": "0-0",  # Só queremos o total
            "criteria[0][field]": self.field_ids["DATE_CREATION"],
            "criteria[0][searchtype]": "contains",
            "criteria[0][value]": f"{prefix}{date_value}"
        }
        
        logger.debug(f"Testando critério contains - Prefixo: {prefix}, Valor: {date_value}")
        logger.debug(f"Parâmetros: {params}")
        
        try:
            response = requests.get(
                f"{self.glpi_url}/search/Ticket",
                headers=self.get_headers(),
                params=params,
                timeout=10
            )
            
            logger.debug(f"Status da resposta: {response.status_code}")
            logger.debug(f"Headers da resposta: {dict(response.headers)}")
            
            response.raise_for_status()
            
            # O total vem no header Content-Range
            if "Content-Range" in response.headers:
                content_range = response.headers["Content-Range"]
                total = int(content_range.split("/")[-1])
                logger.debug(f"Content-Range: {content_range}, Total: {total}")
                return total
            
            logger.debug("Header Content-Range não encontrado")
            return 0
            
        except Exception as e:
            logger.error(f"Erro ao testar critério contains de data: {e}")
            return 0
    
    def close_session(self):
        """Encerra sessão GLPI"""
        if self.session_token:
            try:
                requests.get(f"{self.glpi_url}/killSession", headers=self.get_headers(), timeout=5)
                logger.info("Sessão GLPI encerrada")
            except:
                pass

def main():
    """Função principal do teste"""
    print("\n" + "="*60)
    print("TESTE ISOLADO - DIFERENTES FORMATOS DE DATA GLPI")
    print("="*60)
    
    # Inicializar serviço
    service = GLPITestService()
    
    try:
        # 1. Autenticar
        if not service.authenticate():
            print("Falha na autenticação. Verifique as credenciais no .env")
            return
        
        # 2. Descobrir campos
        if not service.discover_field_ids():
            print("Falha ao descobrir campos necessários")
            return
        
        # DIAGNÓSTICO: Testar critérios de data individualmente
        print("DIAGNÓSTICO: TESTANDO CRITÉRIOS DE DATA INDIVIDUALMENTE")
        print("=" * 60)
        
        print("TESTE 1: Apenas critério 'morethan' (maior que)")
        print("-" * 50)
        count1 = service.test_single_date_criteria("morethan", "2025-01-01")
        print(f"Tickets criados após 2025-01-01: {count1}")
        print()
        
        print("TESTE 2: Apenas critério 'lessthan' (menor que)")
        print("-" * 50)
        count2 = service.test_single_date_criteria("lessthan", "2025-12-31")
        print(f"Tickets criados antes de 2025-12-31: {count2}")
        print()
        
        print("TESTE 3: Combinação morethan + lessthan (período amplo)")
        print("-" * 50)
        count3 = service.test_date_format("2025-01-01", "2025-12-31")
        print(f"Tickets no período 2025-01-01 a 2025-12-31: {count3}")
        print()
        
        print("TESTE 4: Testando com formato de data e hora")
        print("-" * 50)
        count4 = service.test_date_format("2025-01-01 00:00:00", "2025-12-31 23:59:59")
        print(f"Tickets no período com hora: {count4}")
        print()
        
        print("TESTE 5: Verificando se existem tickets recentes")
        print("-" * 50)
        count5 = service.test_single_date_criteria("morethan", "2024-01-01")
        print(f"Tickets criados após 2024-01-01: {count5}")
        print()
        
        print("TESTE 6: Verificando tickets muito antigos")
        print("-" * 50)
        count6 = service.test_single_date_criteria("lessthan", "2020-01-01")
        print(f"Tickets criados antes de 2020-01-01: {count6}")
        print()
        
        print("TESTE 7: Usando 'contains' com prefixo '>' (maior que)")
        print("-" * 50)
        count7 = service.test_contains_date_criteria(">", "2024-01-01")
        print(f"Tickets criados após 2024-01-01 (contains >): {count7}")
        print()
        
        print("TESTE 8: Usando 'contains' com prefixo '<' (menor que)")
        print("-" * 50)
        count8 = service.test_contains_date_criteria("<", "2025-12-31")
        print(f"Tickets criados antes de 2025-12-31 (contains <): {count8}")
        print()
        
        print("TESTE 9: Testando período específico com contains")
        print("-" * 50)
        count9a = service.test_contains_date_criteria(">", "2025-07-01")
        count9b = service.test_contains_date_criteria("<", "2025-08-31")
        print(f"Tickets após 2025-07-01 (contains >): {count9a}")
        print(f"Tickets antes de 2025-08-31 (contains <): {count9b}")
        print()
        
        print("RESUMO DOS TESTES DE DIAGNÓSTICO:")
        print(f"- Apenas 'morethan' 2025-01-01: {count1}")
        print(f"- Apenas 'lessthan' 2025-12-31: {count2}")
        print(f"- Período 2025 completo: {count3}")
        print(f"- Período 2025 com hora: {count4}")
        print(f"- Tickets desde 2024: {count5}")
        print(f"- Tickets antes de 2020: {count6}")
        print(f"- Contains > 2024-01-01: {count7}")
        print(f"- Contains < 2025-12-31: {count8}")
        print(f"- Contains > 2025-07-01: {count9a}")
        print(f"- Contains < 2025-08-31: {count9b}")
        print()
        
        # TESTE PRELIMINAR: Verificar se há tickets SEM filtro de data
        print("TESTE PRELIMINAR: TICKETS SEM FILTRO DE DATA")
        print("-" * 50)
        total_no_filter = 0
        for level_name, group_id in service.service_levels.items():
            level_total_no_filter = 0
            for status_name, status_id in service.status_map.items():
                count = service.get_ticket_count_no_filter(group_id, status_id)
                level_total_no_filter += count
                total_no_filter += count
            if level_total_no_filter > 0:
                print(f"{level_name} (Grupo {group_id}): {level_total_no_filter} tickets")
        
        print(f"TOTAL SEM FILTRO: {total_no_filter} tickets")
        print()
        
        # 4. TESTE 1: Métricas por Nível e Status
        print("TESTE 1: TICKETS POR STATUS E NÍVEL (COM FILTRO DE DATA)")
        print("-" * 50)
        
        total_geral = 0
        metrics_by_level = {}
        
        for level_name, group_id in service.service_levels.items():
            print(f"\n{level_name} (Grupo {group_id}):")
            level_total = 0
            level_metrics = {}
            
            for status_name, status_id in service.status_map.items():
                count = service.get_ticket_count_with_filter(group_id, status_id, start_date, end_date)
                level_metrics[status_name] = count
                level_total += count
                print(f"  • {status_name:12}: {count:4d} tickets")
            
            metrics_by_level[level_name] = level_metrics
            total_geral += level_total
            print(f"  Total {level_name:8}: {level_total:4d} tickets")
        
        print(f"\nTOTAL GERAL: {total_geral} tickets")
        
        # 5. TESTE 2: Ranking de Técnicos
        print("\n" + "="*50)
        print("TESTE 2: RANKING DE TÉCNICOS")
        print("-" * 50)
        
        ranking = service.get_technician_ranking_with_filter(start_date, end_date, limit=10)
        
        if ranking:
            print(f"\nTop {len(ranking)} técnicos no período:")
            for tech in ranking:
                print(f"  {tech['rank']:2d}. {tech['nome']:25} - {tech['total']:3d} tickets")
        else:
            print("Nenhum técnico encontrado ou campo de técnico não disponível")
        
        # 6. Resumo dos Resultados
        print("\n" + "="*60)
        print("RESUMO DOS RESULTADOS")
        print("="*60)
        print(f"Período analisado: {start_date} até {end_date}")
        print(f"Total de tickets: {total_geral}")
        print(f"Técnicos no ranking: {len(ranking)}")
        print(f"Filtro aplicado: {DATE_FILTER}")
        
        # Exibir estrutura completa dos dados
        print("\n" + "="*60)
        print("DADOS DETALHADOS (para debug)")
        print("="*60)
        print("\nMétricas por Nível:")
        pprint(metrics_by_level)
        
        if ranking:
            print("\nRanking Completo:")
            pprint(ranking)
        
        print("\nTeste concluído com sucesso!")
        
    except KeyboardInterrupt:
        print("\nTeste interrompido pelo usuário")
    except Exception as e:
        print(f"\nErro durante o teste: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Sempre encerrar a sessão
        service.close_session()
        print("\nSessão encerrada. Teste finalizado.")

if __name__ == "__main__":
    main()