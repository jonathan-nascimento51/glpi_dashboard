# -*- coding: utf-8 -*-
import logging
from typing import Dict, Optional, Tuple
import requests
from backend.config.settings import active_config


class GLPIService:
    """Serviço para integração com a API do GLPI"""
    
    def __init__(self):
        self.glpi_url = active_config.GLPI_URL
        self.app_token = active_config.GLPI_APP_TOKEN
        self.user_token = active_config.GLPI_USER_TOKEN
        
        # Mapeamento de status dos tickets
        self.status_map = {
            "Novo": 1,
            "Processando (atribuído)": 2,
            "Processando (planejado)": 3,
            "Pendente": 4,
            "Solucionado": 5,
            "Fechado": 6,
        }
        
        # Níveis de atendimento (grupos técnicos)
        self.service_levels = {
            "N1": 89,
            "N2": 90,
            "N3": 91,
            "N4": 92,
        }
        
        self.field_ids = {}
        self.session_token = None
        
        # Configuração de logging
        self.logger = logging.getLogger('api')
    
    def authenticate(self) -> bool:
        """Autentica na API do GLPI e obtém o session token"""
        if not self.app_token or not self.user_token:
            self.logger.error("Tokens de autenticação do GLPI (GLPI_APP_TOKEN, GLPI_USER_TOKEN) não estão configurados.")
            return False
            
        session_headers = {
            "Content-Type": "application/json",
            "App-Token": self.app_token,
            "Authorization": f"user_token {self.user_token}",
        }
        
        try:
            self.logger.info("Autenticando na API do GLPI...")
            response = requests.get(f"{self.glpi_url}/initSession", headers=session_headers)
            response.raise_for_status()
            self.session_token = response.json()["session_token"]
            self.logger.info("Autenticação bem-sucedida!")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Falha na autenticação: {e}")
            return False
    
    def get_api_headers(self) -> Dict[str, str]:
        """Retorna os headers necessários para as requisições da API"""
        return {
            "Session-Token": self.session_token,
            "App-Token": self.app_token
        }
    
    def discover_field_ids(self) -> bool:
        """Descobre dinamicamente os IDs dos campos do GLPI"""
        if not self.session_token:
            self.logger.error("Sessão não autenticada")
            return False
            
        try:
            headers = self.get_api_headers()
            response = requests.get(
                f"{self.glpi_url}/listSearchOptions/Ticket", 
                headers=headers
            )
            response.raise_for_status()
            search_options = response.json()
            
            group_field_name = "Grupo técnico"
            status_field_name = "Status"
            
            group_id_found = False
            status_id_found = False
            
            for item_id, item_data in search_options.items():
                if isinstance(item_data, dict) and "name" in item_data:
                    field_name = item_data["name"]
                    
                    if field_name == group_field_name and not group_id_found:
                        self.field_ids["GROUP"] = item_id
                        self.logger.info(f"ID do campo '{group_field_name}' encontrado: {item_id}")
                        group_id_found = True
                    
                    if field_name == status_field_name and not status_id_found:
                        self.field_ids["STATUS"] = item_id
                        self.logger.info(f"ID do campo '{status_field_name}' encontrado: {item_id}")
                        status_id_found = True
                
                if group_id_found and status_id_found:
                    break
            
            return group_id_found and status_id_found
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro ao descobrir IDs dos campos: {e}")
            return False
    
    def get_ticket_count(self, group_id: int, status_id: int) -> Optional[int]:
        """Busca o total de tickets para um grupo e status específicos"""
        if not self.session_token or not self.field_ids:
            return None
            
        search_params = {
            "is_deleted": 0,
            "range": "0-0",
            "criteria[0][field]": self.field_ids["GROUP"],
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": group_id,
            "criteria[1][link]": "AND",
            "criteria[1][field]": self.field_ids["STATUS"],
            "criteria[1][searchtype]": "equals",
            "criteria[1][value]": status_id,
        }
        
        try:
            headers = self.get_api_headers()
            response = requests.get(
                f"{self.glpi_url}/search/Ticket",
                headers=headers,
                params=search_params
            )
            
            if "Content-Range" in response.headers:
                total = int(response.headers["Content-Range"].split("/")[-1])
                return total
            
            if 200 <= response.status_code < 300:
                return 0
                
            response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro ao buscar contagem de tickets: {e}")
            return None
        
        return None
    
    def get_metrics_by_level(self) -> Dict[str, Dict[str, int]]:
        """Retorna métricas de tickets agrupadas por nível de atendimento"""
        if not self.authenticate():
            return {}
            
        if not self.discover_field_ids():
            return {}
        
        result = self._get_metrics_by_level_internal()
        self.close_session()
        return result
    
    def _get_metrics_by_level_internal(self) -> Dict[str, Dict[str, int]]:
        """Método interno para obter métricas por nível (sem autenticação/fechamento)"""
        metrics = {}
        
        for level_name, group_id in self.service_levels.items():
            level_metrics = {}
            
            for status_name, status_id in self.status_map.items():
                count = self.get_ticket_count(group_id, status_id)
                level_metrics[status_name] = count if count is not None else 0
            
            metrics[level_name] = level_metrics
        
        return metrics
    
    def get_general_metrics(self) -> Dict[str, int]:
        """Retorna métricas gerais de todos os tickets (não apenas grupos N1-N4)"""
        if not self.authenticate():
            return {}
            
        if not self.discover_field_ids():
            return {}
        
        result = self._get_general_metrics_internal()
        self.close_session()
        return result
    
    def _get_general_metrics_internal(self) -> Dict[str, int]:
        """Método interno para obter métricas gerais (sem autenticação/fechamento)"""
        headers = self.get_api_headers()
        status_totals = {}
        
        # Buscar totais por status sem filtro de grupo
        for status_name, status_id in self.status_map.items():
            search_params = {
                "is_deleted": 0,
                "range": "0-0",
                "criteria[0][field]": self.field_ids["STATUS"],
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": status_id,
            }
            
            try:
                response = requests.get(
                    f"{self.glpi_url}/search/Ticket",
                    headers=headers,
                    params=search_params
                )
                
                if "Content-Range" in response.headers:
                    count = int(response.headers["Content-Range"].split("/")[-1])
                    status_totals[status_name] = count
                else:
                    status_totals[status_name] = 0
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Erro ao buscar contagem geral para {status_name}: {e}")
                status_totals[status_name] = 0
        
        return status_totals
    
    def get_dashboard_metrics(self) -> Dict[str, any]:
        """Retorna métricas formatadas para o dashboard React.
        
        Retorna um dicionário com as métricas ou None em caso de falha.
        """
        # Autenticar uma única vez
        if not self.authenticate():
            return None
        
        if not self.discover_field_ids():
            self.close_session()
            return None
        
        # Obter totais gerais (todos os grupos) para métricas principais
        general_totals = self._get_general_metrics_internal()
        self.logger.info(f"Totais gerais obtidos: {general_totals}")
        
        # Obter métricas por nível (grupos N1-N4)
        raw_metrics = self._get_metrics_by_level_internal()
        
        # Agregação dos totais por status (apenas para níveis)
        totals = {
            "novos": 0,
            "pendentes": 0,
            "progresso": 0,
            "resolvidos": 0
        }
        
        # Métricas por nível
        level_metrics = {
            "n1": {
                "novos": 0,
                "progresso": 0,
                "pendentes": 0,
                "resolvidos": 0
            },
            "n2": {
                "novos": 0,
                "progresso": 0,
                "pendentes": 0,
                "resolvidos": 0
            },
            "n3": {
                "novos": 0,
                "progresso": 0,
                "pendentes": 0,
                "resolvidos": 0
            },
            "n4": {
                "novos": 0,
                "progresso": 0,
                "pendentes": 0,
                "resolvidos": 0
            }
        }
        
        for level_name, level_data in raw_metrics.items():
            level_key = level_name.lower()
            
            # Novo
            level_metrics[level_key]["novos"] = level_data.get("Novo", 0)
            totals["novos"] += level_metrics[level_key]["novos"]
            
            # Progresso (soma de Processando atribuído e planejado)
            processando_atribuido = level_data.get("Processando (atribuído)", 0)
            processando_planejado = level_data.get("Processando (planejado)", 0)
            level_metrics[level_key]["progresso"] = processando_atribuido + processando_planejado
            totals["progresso"] += level_metrics[level_key]["progresso"]
            
            # Pendente
            level_metrics[level_key]["pendentes"] = level_data.get("Pendente", 0)
            totals["pendentes"] += level_metrics[level_key]["pendentes"]
            
            # Resolvidos (soma de Solucionado e Fechado)
            solucionado = level_data.get("Solucionado", 0)
            fechado = level_data.get("Fechado", 0)
            level_metrics[level_key]["resolvidos"] = solucionado + fechado
            totals["resolvidos"] += level_metrics[level_key]["resolvidos"]
        
        # Usar totais gerais para métricas principais
        general_novos = general_totals.get("Novo", 0)
        general_pendentes = general_totals.get("Pendente", 0)
        general_progresso = general_totals.get("Processando (atribuído)", 0) + general_totals.get("Processando (planejado)", 0)
        general_resolvidos = general_totals.get("Solucionado", 0) + general_totals.get("Fechado", 0)
        general_total = general_novos + general_pendentes + general_progresso + general_resolvidos
        
        self.logger.info(f"Métricas gerais calculadas: novos={general_novos}, pendentes={general_pendentes}, progresso={general_progresso}, resolvidos={general_resolvidos}, total={general_total}")
        
        result = {
            "novos": general_novos,
            "pendentes": general_pendentes,
            "progresso": general_progresso,
            "resolvidos": general_resolvidos,
            "total": general_total,
            "niveis": {
                "n1": level_metrics["n1"],
                "n2": level_metrics["n2"],
                "n3": level_metrics["n3"],
                "n4": level_metrics["n4"]
            },
            "tendencias": {
                "novos": "0",
                "pendentes": "0",
                "progresso": "0",
                "resolvidos": "0"
            },
            "detalhes": raw_metrics
        }
        
        self.logger.info(f"Métricas formatadas: {result}")
        self.close_session()
        return result
    
    def get_technician_ranking(self) -> list:
        """Retorna ranking de técnicos por total de chamados usando dados reais da API GLPI"""
        self.logger.info("Iniciando busca de ranking de técnicos...")
        
        if not self.authenticate():
            self.logger.error("Falha na autenticação")
            return []
            
        if not self.discover_field_ids():
            self.logger.error("Falha ao descobrir field IDs")
            self.close_session()
            return []
        
        # Descobrir o field ID do técnico atribuído
        tech_field_id = self._discover_tech_field_id()
        if not tech_field_id:
            self.logger.error("Falha ao descobrir field ID do técnico")
            self.close_session()
            return []
        
        self.logger.info(f"Field ID do técnico encontrado: {tech_field_id}")
        
        # Listar técnicos ativos
        active_techs = self._list_active_technicians()
        if not active_techs:
            self.logger.error("Nenhum técnico ativo encontrado")
            self.close_session()
            return []
        
        self.logger.info(f"Encontrados {len(active_techs)} técnicos ativos")
        
        # Contar tickets por técnico
        ranking = []
        for tech_id, tech_name in active_techs:
            total_tickets = self._count_tickets_by_technician(tech_id, tech_field_id)
            if total_tickets is not None:
                self.logger.info(f"Técnico {tech_name} (ID: {tech_id}): {total_tickets} tickets")
                ranking.append({
                    "id": str(tech_id),
                    "nome": tech_name,
                    "total": total_tickets
                })
            else:
                self.logger.warning(f"Não foi possível contar tickets para técnico {tech_name} (ID: {tech_id})")
        
        # Ordenar por total de tickets (decrescente)
        ranking.sort(key=lambda x: x["total"], reverse=True)
        
        self.logger.info(f"Ranking final: {len(ranking)} técnicos com dados válidos")
        
        self.close_session()
        return ranking[:10]  # Retorna top 10
    
    def _discover_tech_field_id(self) -> Optional[str]:
        """Descobre dinamicamente o field ID do técnico atribuído"""
        try:
            headers = self.get_api_headers()
            response = requests.get(
                f"{self.glpi_url}/listSearchOptions/Ticket", 
                headers=headers
            )
            response.raise_for_status()
            search_options = response.json()
            
            # Procurar por campos relacionados ao técnico atribuído
            # Baseado no debug, o campo "5" é "Técnico" e "95" é "Técnico encarregado"
            tech_field_mapping = {
                "5": "Técnico",
                "95": "Técnico encarregado"
            }
            
            # Primeiro, tentar os campos conhecidos
            for field_id, expected_name in tech_field_mapping.items():
                if field_id in search_options:
                    field_data = search_options[field_id]
                    if isinstance(field_data, dict) and "name" in field_data:
                        field_name = field_data["name"]
                        if field_name == expected_name:
                            self.logger.info(f"Campo de técnico encontrado: {field_name} (ID: {field_id})")
                            return field_id
            
            # Fallback: procurar por nomes
            tech_field_names = ["Técnico", "Atribuído", "Assigned to", "Technician", "Técnico encarregado"]
            
            for field_id, field_data in search_options.items():
                if isinstance(field_data, dict) and "name" in field_data:
                    field_name = field_data["name"]
                    if field_name in tech_field_names:
                        self.logger.info(f"Campo de técnico encontrado (fallback): {field_name} (ID: {field_id})")
                        return field_id
            
            self.logger.error("Campo de técnico atribuído não encontrado")
            return None
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro ao descobrir field ID do técnico: {e}")
            return None
    
    def _list_active_technicians(self) -> list:
        """Lista técnicos ativos do sistema"""
        try:
            headers = self.get_api_headers()
            params = {
                "range": "0-999",
                "is_deleted": 0,
                "criteria[0][field]": "is_active",
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": 1
            }
            
            response = requests.get(
                f"{self.glpi_url}/User",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            users = response.json()
            
            # Extrair ID e nome dos usuários
            technicians = []
            for user in users:
                if isinstance(user, dict) and "id" in user and "name" in user:
                    technicians.append((user["id"], user["name"]))
            
            self.logger.info(f"Encontrados {len(technicians)} técnicos ativos")
            return technicians
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro ao listar técnicos ativos: {e}")
            return []
    
    def _count_tickets_by_technician(self, tech_id: int, tech_field_id: str) -> Optional[int]:
        """Conta o total de tickets atribuídos a um técnico específico"""
        try:
            headers = self.get_api_headers()
            params = {
                "criteria[0][field]": tech_field_id,
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": tech_id,
                "is_deleted": 0,
                "range": "0-0"
            }
            
            response = requests.get(
                f"{self.glpi_url}/search/Ticket",
                headers=headers,
                params=params
            )
            
            # Extrair total do cabeçalho Content-Range
            if "Content-Range" in response.headers:
                content_range = response.headers["Content-Range"]
                total = int(content_range.split("/")[-1])
                return total
            
            return 0
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro ao contar tickets do técnico {tech_id}: {e}")
            return None
        except (ValueError, IndexError) as e:
            self.logger.error(f"Erro ao processar Content-Range para técnico {tech_id}: {e}")
            return None

    def close_session(self):
        """Encerra a sessão com a API do GLPI"""
        if self.session_token:
            try:
                headers = self.get_api_headers()
                requests.get(f"{self.glpi_url}/killSession", headers=headers)
                self.logger.info("Sessão encerrada com sucesso")
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Erro ao encerrar sessão: {e}")
            finally:
                self.session_token = None
    
    def get_system_status(self) -> Dict[str, any]:
        """Retorna status do sistema GLPI"""
        try:
            # Tenta uma requisição simples para verificar conectividade
            response = requests.get(f"{self.glpi_url}/", timeout=5)
            
            if response.status_code == 200:
                return {
                    "status": "online",
                    "message": "GLPI conectado",
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                return {
                    "status": "warning",
                    "message": f"GLPI respondeu com status {response.status_code}",
                    "response_time": response.elapsed.total_seconds()
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "status": "offline",
                "message": f"Erro de conexão: {str(e)}",
                "response_time": None
            }