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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GLPITestService:
    """Serviço simplificado para teste de filtros de data no GLPI"""
    
    def __init__(self):
        # Configurações da API GLPI
        self.glpi_url = os.environ.get('GLPI_URL', 'http://10.73.0.79/glpi/apirest.php')
        self.app_token = os.environ.get('GLPI_APP_TOKEN')
        self.user_token = os.environ.get('GLPI_USER_TOKEN')
        
        if not self.app_token or not self.user_token:
            logger.error("❌ GLPI_APP_TOKEN e GLPI_USER_TOKEN devem estar configurados no .env")
            sys.exit(1)
        
        # Mapeamentos
        self.status_map = {
            "Novo": 1,
            "Atribuído": 2,
            "Pendente": 4,
            "Resolvido": 5
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
            logger.info("🔐 Autenticando na API GLPI...")
            response = requests.get(f"{self.glpi_url}/initSession", headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.session_token = data["session_token"]
            logger.info("✅ Autenticação bem-sucedida!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Falha na autenticação: {e}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Retorna headers para requisições autenticadas"""
        return {
            "Session-Token": self.session_token,
            "App-Token": self.app_token,
            "Content-Type": "application/json"
        }
    
    def discover_field_ids(self) -> bool:
        """Descobre IDs dos campos necessários"""
        try:
            logger.info("🔍 Descobrindo IDs dos campos...")
            response = requests.get(
                f"{self.glpi_url}/listSearchOptions/Ticket",
                headers=self.get_headers(),
                timeout=10
            )
            response.raise_for_status()
            
            search_options = response.json()
            
            # Buscar campos necessários
            for field_id, field_data in search_options.items():
                if isinstance(field_data, dict) and "name" in field_data:
                    field_name = field_data["name"].lower()
                    
                    if "grupo" in field_name or "group" in field_name:
                        self.field_ids["GROUP"] = field_id
                        logger.info(f"📋 Campo Grupo encontrado: ID {field_id}")
                    elif "status" in field_name:
                        self.field_ids["STATUS"] = field_id
                        logger.info(f"📊 Campo Status encontrado: ID {field_id}")
                    elif "data de abertura" in field_name or "date" in field_name:
                        self.field_ids["DATE_CREATION"] = field_id
                        logger.info(f"📅 Campo Data encontrado: ID {field_id}")
                    elif "técnico" in field_name or "assigned" in field_name:
                        self.field_ids["TECHNICIAN"] = field_id
                        logger.info(f"👤 Campo Técnico encontrado: ID {field_id}")
            
            required_fields = ["GROUP", "STATUS", "DATE_CREATION"]
            missing_fields = [f for f in required_fields if f not in self.field_ids]
            
            if missing_fields:
                logger.error(f"❌ Campos obrigatórios não encontrados: {missing_fields}")
                return False
            
            logger.info("✅ Todos os campos necessários foram descobertos!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao descobrir campos: {e}")
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
            logger.error(f"❌ Filtro de data inválido: {date_filter}")
            return None, None
        
        return start_date, end_date
    
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
            "criteria[2][value]": f"{start_date} 00:00:00",
            "criteria[3][link]": "AND",
            "criteria[3][field]": self.field_ids["DATE_CREATION"],
            "criteria[3][searchtype]": "lessthan",
            "criteria[3][value]": f"{end_date} 23:59:59"
        }
        
        try:
            response = requests.get(
                f"{self.glpi_url}/search/Ticket",
                headers=self.get_headers(),
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            # O total vem no header Content-Range
            if "Content-Range" in response.headers:
                total = int(response.headers["Content-Range"].split("/")[-1])
                return total
            
            return 0
            
        except Exception as e:
            logger.error(f"❌ Erro ao contar tickets: {e}")
            return 0
    
    def get_technician_ranking_with_filter(self, start_date: str, end_date: str, limit: int = 10) -> List[Dict]:
        """Obtém ranking de técnicos com filtro de data"""
        if "TECHNICIAN" not in self.field_ids:
            logger.warning("⚠️ Campo de técnico não encontrado, pulando ranking")
            return []
        
        params = {
            "is_deleted": 0,
            "range": f"0-{limit-1}",
            "criteria[0][field]": self.field_ids["DATE_CREATION"],
            "criteria[0][searchtype]": "morethan",
            "criteria[0][value]": f"{start_date} 00:00:00",
            "criteria[1][link]": "AND",
            "criteria[1][field]": self.field_ids["DATE_CREATION"],
            "criteria[1][searchtype]": "lessthan",
            "criteria[1][value]": f"{end_date} 23:59:59",
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
            logger.error(f"❌ Erro ao obter ranking de técnicos: {e}")
            return []
    
    def close_session(self):
        """Encerra sessão GLPI"""
        if self.session_token:
            try:
                requests.get(f"{self.glpi_url}/killSession", headers=self.get_headers(), timeout=5)
                logger.info("🔒 Sessão GLPI encerrada")
            except:
                pass

def main():
    """Função principal do teste"""
    print("\n" + "="*60)
    print("🧪 TESTE ISOLADO - FILTRO DE DATA GLPI")
    print("="*60)
    
    # Configurar filtro de data (modificar aqui para testar diferentes períodos)
    DATE_FILTER = "last_7_days"  # Opções: "today", "last_7_days", "last_30_days"
    
    print(f"📅 Filtro de data configurado: {DATE_FILTER}")
    print()
    
    # Inicializar serviço
    service = GLPITestService()
    
    try:
        # 1. Autenticar
        if not service.authenticate():
            print("❌ Falha na autenticação. Verifique as credenciais no .env")
            return
        
        # 2. Descobrir campos
        if not service.discover_field_ids():
            print("❌ Falha ao descobrir campos necessários")
            return
        
        # 3. Converter filtro de data
        start_date, end_date = service.parse_date_filter(DATE_FILTER)
        if not start_date or not end_date:
            print("❌ Falha ao processar filtro de data")
            return
        
        print(f"📊 Período de análise: {start_date} até {end_date}")
        print()
        
        # 4. TESTE 1: Métricas por Nível e Status
        print("🎯 TESTE 1: TICKETS POR STATUS E NÍVEL")
        print("-" * 50)
        
        total_geral = 0
        metrics_by_level = {}
        
        for level_name, group_id in service.service_levels.items():
            print(f"\n📋 {level_name} (Grupo {group_id}):")
            level_total = 0
            level_metrics = {}
            
            for status_name, status_id in service.status_map.items():
                count = service.get_ticket_count_with_filter(group_id, status_id, start_date, end_date)
                level_metrics[status_name] = count
                level_total += count
                print(f"  • {status_name:12}: {count:4d} tickets")
            
            metrics_by_level[level_name] = level_metrics
            total_geral += level_total
            print(f"  📊 Total {level_name:8}: {level_total:4d} tickets")
        
        print(f"\n🎯 TOTAL GERAL: {total_geral} tickets")
        
        # 5. TESTE 2: Ranking de Técnicos
        print("\n" + "="*50)
        print("👥 TESTE 2: RANKING DE TÉCNICOS")
        print("-" * 50)
        
        ranking = service.get_technician_ranking_with_filter(start_date, end_date, limit=10)
        
        if ranking:
            print(f"\n🏆 Top {len(ranking)} técnicos no período:")
            for tech in ranking:
                print(f"  {tech['rank']:2d}. {tech['nome']:25} - {tech['total']:3d} tickets")
        else:
            print("⚠️ Nenhum técnico encontrado ou campo de técnico não disponível")
        
        # 6. Resumo dos Resultados
        print("\n" + "="*60)
        print("📋 RESUMO DOS RESULTADOS")
        print("="*60)
        
        print(f"📅 Período analisado: {start_date} até {end_date}")
        print(f"🎯 Total de tickets: {total_geral}")
        print(f"👥 Técnicos no ranking: {len(ranking)}")
        print(f"🔧 Filtro aplicado: {DATE_FILTER}")
        
        # Exibir estrutura completa dos dados
        print("\n" + "="*60)
        print("🔍 DADOS DETALHADOS (para debug)")
        print("="*60)
        
        print("\n📊 Métricas por Nível:")
        pprint(metrics_by_level)
        
        if ranking:
            print("\n👥 Ranking Completo:")
            pprint(ranking)
        
        print("\n✅ Teste concluído com sucesso!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Sempre encerrar a sessão
        service.close_session()
        print("\n🔒 Sessão encerrada. Teste finalizado.")

if __name__ == "__main__":
    main()