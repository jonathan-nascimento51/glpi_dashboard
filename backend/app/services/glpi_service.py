# -*- coding: utf-8 -*-
import logging
from typing import Dict, Optional, Tuple, List
import requests
import time
from datetime import datetime, timedelta
from ..core.config import active_config
from ..utils.response_formatter import ResponseFormatter
from ..utils.structured_logger import create_glpi_logger, log_api_call


class GLPIService:
    """Servio para integrao com a API do GLPI com autenticao robusta"""
    
    def __init__(self):
        self.glpi_url = active_config.GLPI_URL
        self.app_token = active_config.GLPI_APP_TOKEN
        self.user_token = active_config.GLPI_USER_TOKEN
        self.structured_logger = create_glpi_logger(active_config.LOG_LEVEL)
        self.logger = logging.getLogger("glpi_service")
        
        # Mapeamento de status dos tickets
        self.status_map = {
            "Novo": 1,
            "Processando (atribudo)": 2,
            "Processando (planejado)": 3,
            "Pendente": 4,
            "Solucionado": 5,
            "Fechado": 6,
        }
        
        # Nveis de atendimento (grupos t�cnicos)
        self.service_levels = {
            "N1": 89,
            "N2": 90,
            "N3": 91,
            "N4": 92,
        }
        self.field_ids = {}
        self.session_token = None
        self.token_created_at = None
        self.token_expires_at = None
        self.retry_delay_base = 2  # Base para backoff exponencial
        self.max_retries = 3  # Nmero mximo de tentativas
        self.session_timeout = 3600  # 1 hora em segundos
        
        # Sistema de cache para evitar consultas repetitivas
        self._cache = {
            'technician_ranking': {'data': None, 'timestamp': None, 'ttl': 300},  # 5 minutos
            'active_technicians': {'data': None, 'timestamp': None, 'ttl': 600},  # 10 minutos
            'field_ids': {'data': None, 'timestamp': None, 'ttl': 1800},  # 30 minutos
            'dashboard_metrics': {'data': None, 'timestamp': None, 'ttl': 180},  # 3 minutos
            'dashboard_metrics_filtered': {},  # Cache dinmico para filtros de data
            'priority_names': {}  # Cache para nomes de prioridade
        }
    
    def _is_cache_valid(self, cache_key: str, sub_key: str = None) -> bool:
        """Verifica se o cache  vlido"""
        try:
            if sub_key:
                cache_data = self._cache.get(cache_key, {}).get(sub_key)
            else:
                cache_data = self._cache.get(cache_key)
            
            if not cache_data or cache_data.get('timestamp') is None:
                return False
            
            current_time = time.time()
            cache_time = cache_data['timestamp']
            ttl = cache_data.get('ttl', 300)  # Default 5 minutos
            
            return (current_time - cache_time) < ttl
        except Exception as e:
            self.logger.error(f"Erro ao verificar cache: {e}")
            return False
    
    def _get_cache_data(self, cache_key: str, sub_key: str = None):
        """Obtm dados do cache"""
        try:
            if sub_key:
                return self._cache.get(cache_key, {}).get(sub_key, {}).get('data')
            else:
                return self._cache.get(cache_key, {}).get('data')
        except Exception as e:
            self.logger.error(f"Erro ao obter dados do cache: {e}")
            return None
    
    def _set_cache_data(self, cache_key: str, data, ttl: int = 300, sub_key: str = None):
        """Define dados no cache"""
        try:
            cache_entry = {
                'data': data,
                'timestamp': time.time(),
                'ttl': ttl
            }
            
            if sub_key:
                if cache_key not in self._cache:
                    self._cache[cache_key] = {}
                self._cache[cache_key][sub_key] = cache_entry
            else:
                self._cache[cache_key] = cache_entry
        except Exception as e:
            self.logger.error(f"Erro ao definir dados do cache: {e}")
    
    def _is_token_expired(self) -> bool:
        """Verifica se o token de sesso est expirado"""
        if not self.token_created_at:
            return True
        
        current_time = time.time()
        token_age = current_time - self.token_created_at
        
        # Token expira em 1 hora ou se passou do tempo definido
        return token_age >= self.session_timeout
    
    def _ensure_authenticated(self) -> bool:
        """Garante que temos um token vlido, re-autenticando se necessrio"""
        if not self.session_token or self._is_token_expired():
            self.logger.info("Token expirado ou inexistente, re-autenticando...")
            return self._authenticate_with_retry()
        return True
    
    def _authenticate_with_retry(self) -> bool:
        """Autentica com retry automtico e backoff exponencial"""
        for attempt in range(self.max_retries):
            try:
                if self._perform_authentication():
                    return True
                    
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay_base ** attempt
                    self.logger.warning(f"Tentativa {attempt + 1} falhou, aguardando {delay}s antes da prxima tentativa...")
                    time.sleep(delay)
                    
            except Exception as e:
                self.logger.error(f"Erro na tentativa {attempt + 1} de autenticao: {e}")
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay_base ** attempt
                    time.sleep(delay)
        
        self.logger.error(f"Falha na autenticao aps {self.max_retries} tentativas")
        return False
    
    def _perform_authentication(self) -> bool:
        """Executa o processo de autentica??o"""
        if not self.app_token or not self.user_token:
            self.logger.error("Tokens de autentica??o do GLPI (GLPI_APP_TOKEN, GLPI_USER_TOKEN) n?o esto configurados.")
            return False
            
        session_headers = {
            "Content-Type": "application/json",
            "App-Token": self.app_token,
            "Authorization": f"user_token {self.user_token}",
        }
        
        try:
            self.logger.info("Autenticando na API do GLPI...")
            response = requests.get(
                f"{self.glpi_url}/initSession", 
                headers=session_headers,
                timeout=10
            )
            response.raise_for_status()
            
            # Verificar se a resposta tem contedo
            if not response.content:
                self.logger.error("Resposta vazia da API do GLPI")
                return False
            
            try:
                response_data = response.json()
            except ValueError as e:
                self.logger.error(f"Erro ao decodificar JSON da resposta: {e}")
                self.logger.error(f"Contedo da resposta: {response.text}")
                return False
            
            # Verificar se response_data  um dict e contm session_token
            if not isinstance(response_data, dict):
                self.logger.error(f"Resposta n?o  um objeto JSON vlido: {type(response_data)}")
                return False
                
            if "session_token" not in response_data:
                self.logger.error(f"Session token n?o encontrado na resposta. Chaves disponveis: {list(response_data.keys())}")
                self.logger.error(f"Resposta completa: {response_data}")
                return False
            
            session_token = response_data["session_token"]
            if not session_token:
                self.logger.error("Session token est vazio")
                return False
                
            self.session_token = session_token
            self.token_created_at = time.time()
            self.token_expires_at = self.token_created_at + self.session_timeout
            
            self.logger.info(f"autentica??o bem-sucedida! Token: {session_token[:10]}...")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Falha na autentica??o (RequestException): {e}")
            return False
        except Exception as e:
            self.logger.error(f"Erro inesperado na autentica??o: {e}")
            self.logger.error(f"Tipo do erro: {type(e)}")
            return False
    
    def authenticate(self) -> bool:
        """Mtodo pblico para autenticao (mantido para compatibilidade)"""
        return self._authenticate_with_retry()
    
    def get_api_headers(self) -> Optional[Dict[str, str]]:
        """Retorna os headers necessrios para as requisies da API"""
        if not self._ensure_authenticated():
            self.logger.error("no foi possvel obter headers - falha na autenticao")
            return None
            
        return {
            "Session-Token": self.session_token,
            "App-Token": self.app_token
        }
    
    def _make_authenticated_request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """Faz uma requisio autenticada com retry automtico em caso de falha de autenticao"""
        for attempt in range(self.max_retries):
            headers = self.get_api_headers()
            if not headers:
                return None
            
            # Adicionar headers customizados se fornecidos
            if 'headers' in kwargs:
                headers.update(kwargs['headers'])
            kwargs['headers'] = headers
            
            try:
                response = requests.request(method, url, timeout=10, **kwargs)
                
                # Se recebemos 401 ou 403, token pode estar expirado
                if response.status_code in [401, 403]:
                    self.logger.warning(f"Recebido status {response.status_code}, token pode estar expirado")
                    self.session_token = None  # Forar re-autenticao
                    self.token_created_at = None
                    
                    if attempt < self.max_retries - 1:
                        self.logger.info("Tentando re-autenticar...")
                        continue
                
                return response
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Erro na requisio (tentativa {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay_base ** attempt)
                    continue
    def discover_field_ids(self) -> bool:
        """Configura IDs fixos dos campos do GLPI baseado no mapeamento conhecido"""
        try:
            # Usar IDs fixos baseados no diagnstico realizado
            # Estes IDs foram validados contra o endpoint listSearchOptions/Ticket
            self.field_ids = {
                "GROUP": "8",        # Grupo t�cnico
                "STATUS": "12",      # Status
                "DATE_CREATION": "15" # Data de cria??o
            }
            return True
        except Exception as e:
            logger.error(f"Erro ao configurar field_ids: {e}")
            return False

    def get_ticket_count(self, group_id: int, status_id: int, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Optional[int]:
        """Busca o total de tickets para um grupo e status especficos, com filtro de data opcional"""
        import datetime
        
        if not self.field_ids:
            if not self.discover_field_ids():
                timestamp = datetime.datetime.now().isoformat()
                self.logger.error(
                    f"[{timestamp}] Falha ao descobrir field_ids - "
                    f"group_id: {group_id}, status_id: {status_id}, "
                    f"start_date: {start_date}, end_date: {end_date}"
                )
                return 0
            
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
        
        # Adicionar filtros de data se fornecidos (formato ISO funciona melhor)
        criteria_index = 2
        if start_date:
            # Usar formato ISO (YYYY-MM-DD) que funciona corretamente
            search_params[f"criteria[{criteria_index}][link]"] = "AND"
            search_params[f"criteria[{criteria_index}][field]"] = "15"  # Campo 15  o correto para data de criao
            search_params[f"criteria[{criteria_index}][searchtype]"] = "morethan"
            search_params[f"criteria[{criteria_index}][value]"] = start_date
            criteria_index += 1
            
        if end_date:
            # Usar formato ISO (YYYY-MM-DD) que funciona corretamente
            search_params[f"criteria[{criteria_index}][link]"] = "AND"
            search_params[f"criteria[{criteria_index}][field]"] = "15"  # Campo 15  o correto para data de criao
            search_params[f"criteria[{criteria_index}][searchtype]"] = "lessthan"
            search_params[f"criteria[{criteria_index}][value]"] = end_date
        
        try:
            response = self._make_authenticated_request(
                'GET',
                f"{self.glpi_url}/search/Ticket",
                params=search_params
            )
            
            if not response:
                timestamp = datetime.datetime.now().isoformat()
                self.logger.error(
                    f"[{timestamp}] Resposta vazia da API GLPI - "
                    f"group_id: {group_id}, status_id: {status_id}, "
                    f"start_date: {start_date}, end_date: {end_date}"
                )
                return 0
            
            # Verificar se o status code  diferente de 200
            if response.status_code != 200:
                timestamp = datetime.datetime.now().isoformat()
                self.logger.error(
                    f"[{timestamp}] API GLPI retornou status {response.status_code} - "
                    f"group_id: {group_id}, status_id: {status_id}, "
                    f"start_date: {start_date}, end_date: {end_date}"
                )
                return 0
            
            if "Content-Range" in response.headers:
                total = int(response.headers["Content-Range"].split("/")[-1])
                return total
            
            # Se chegou at aqui com status 200 mas sem Content-Range, retornar 0
            return 0
                
        except Exception as e:
            timestamp = datetime.datetime.now().isoformat()
            self.logger.error(
                f"[{timestamp}] Exceo ao buscar contagem de tickets: {str(e)} - "
                f"group_id: {group_id}, status_id: {status_id}, "
                f"start_date: {start_date}, end_date: {end_date}"
            )
            return 0
        
        return 0
    
    def get_metrics_by_level(self) -> Dict[str, Dict[str, int]]:
        """Retorna mtricas de tickets agrupadas por nvel de atendimento"""
        if not self._ensure_authenticated():
            return {}
            
        if not self.discover_field_ids():
            return {}
        
        return self._get_metrics_by_level_internal()
    
    def _get_metrics_by_level_internal(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Dict[str, int]]:
        """Mtodo interno para obter mtricas por nvel (sem autenticao/fechamento)"""
        metrics = {}
        
        for level_name, group_id in self.service_levels.items():
            level_metrics = {}
            
            for status_name, status_id in self.status_map.items():
                count = self.get_ticket_count(group_id, status_id, start_date, end_date)
                level_metrics[status_name] = count if count is not None else 0
            
            metrics[level_name] = level_metrics
        
        return metrics
    
    def get_general_metrics(self) -> Dict[str, int]:
        """Retorna mtricas gerais de todos os tickets (no apenas grupos N1-N4)"""
        if not self._ensure_authenticated():
            return {}
            
        if not self.discover_field_ids():
            return {}
        
        result = self._get_general_metrics_internal()
        return result
    
    def _get_general_metrics_internal(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, int]:
        """Mtodo interno para obter mtricas gerais (sem autenticao/fechamento)"""
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
            
            # Adicionar filtros de data se fornecidos (formato ISO funciona melhor)
            criteria_index = 1
            if start_date:
                # Usar formato ISO (YYYY-MM-DD) que funciona corretamente
                search_params[f"criteria[{criteria_index}][link]"] = "AND"
                search_params[f"criteria[{criteria_index}][field]"] = "15"  # Campo 15  o correto para data de criao
                search_params[f"criteria[{criteria_index}][searchtype]"] = "morethan"
                search_params[f"criteria[{criteria_index}][value]"] = start_date
                criteria_index += 1
                
            if end_date:
                # Usar formato ISO (YYYY-MM-DD) que funciona corretamente
                search_params[f"criteria[{criteria_index}][link]"] = "AND"
                search_params[f"criteria[{criteria_index}][field]"] = "15"  # Campo 15  o correto para data de criao
                search_params[f"criteria[{criteria_index}][searchtype]"] = "lessthan"
                search_params[f"criteria[{criteria_index}][value]"] = end_date
            
            try:
                response = self._make_authenticated_request(
                    'GET',
                    f"{self.glpi_url}/search/Ticket",
                    params=search_params
                )
                
                if response and "Content-Range" in response.headers:
                    count = int(response.headers["Content-Range"].split("/")[-1])
                    status_totals[status_name] = count
                else:
                    status_totals[status_name] = 0
                    
            except Exception as e:
                self.logger.error(f"Erro ao buscar contagem geral para {status_name}: {e}")
                status_totals[status_name] = 0
        
        return status_totals
    
    def get_dashboard_metrics(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, any]:
        """Retorna mtricas formatadas para o dashboard React usando o sistema unificado.
        
        Args:
            start_date: Data inicial no formato YYYY-MM-DD (opcional)
            end_date: Data final no formato YYYY-MM-DD (opcional)
        
        Retorna um dicionrio com as mtricas formatadas ou erro.
        """
        start_time = time.time()
        
        try:
            # Se parmetros de data foram fornecidos, usar o mtodo com filtro
            if start_date or end_date:
                return self.get_dashboard_metrics_with_date_filter(start_date, end_date)
            
            # Verificar cache primeiro
            if self._is_cache_valid('dashboard_metrics'):
                cached_data = self._get_cache_data('dashboard_metrics')
                if cached_data:
                    self.logger.info("Retornando mtricas do cache")
                    return cached_data
            
            # Autenticar uma nica vez
            if not self._ensure_authenticated():
                return ResponseFormatter.format_error_response("Falha na autenticao com GLPI", ["Erro de autenticao"])
            
            if not self.discover_field_ids():
                return ResponseFormatter.format_error_response("Falha ao descobrir IDs dos campos", ["Erro ao obter configurao"])
            
            # Obter totais gerais (todos os grupos) para mtricas principais
            general_totals = self._get_general_metrics_internal()
            self.logger.info(f"Totais gerais obtidos: {general_totals}")
            
            # Obter mtricas por nvel (grupos N1-N4)
            raw_metrics = self._get_metrics_by_level_internal()
            
            # Usar o mesmo formato da funo com filtros para consistncia
            # Calcular totais gerais
            general_novos = general_totals.get("Novo", 0)
            general_pendentes = general_totals.get("Pendente", 0)
            general_progresso = general_totals.get("Processando (atribudo)", 0) + general_totals.get("Processando (planejado)", 0)
            general_resolvidos = general_totals.get("Solucionado", 0) + general_totals.get("Fechado", 0)
            general_total = general_novos + general_pendentes + general_progresso + general_resolvidos
            
            # Mtricas por nvel
            level_metrics = {
                "n1": {"novos": 0, "progresso": 0, "pendentes": 0, "resolvidos": 0},
                "n2": {"novos": 0, "progresso": 0, "pendentes": 0, "resolvidos": 0},
                "n3": {"novos": 0, "progresso": 0, "pendentes": 0, "resolvidos": 0},
                "n4": {"novos": 0, "progresso": 0, "pendentes": 0, "resolvidos": 0}
            }
            
            for level_name, level_data in raw_metrics.items():
                level_key = level_name.lower()
                if level_key in level_metrics:
                    level_metrics[level_key]["novos"] = level_data.get("Novo", 0)
                    level_metrics[level_key]["progresso"] = level_data.get("Processando (atribudo)", 0) + level_data.get("Processando (planejado)", 0)
                    level_metrics[level_key]["pendentes"] = level_data.get("Pendente", 0)
                    level_metrics[level_key]["resolvidos"] = level_data.get("Solucionado", 0) + level_data.get("Fechado", 0)
            
            result = {
                "success": True,
                "data": {
                    "novos": general_novos,
                    "pendentes": general_pendentes,
                    "progresso": general_progresso,
                    "resolvidos": general_resolvidos,
                    "total": general_total,
                    "niveis": {
                        "geral": {
                            "novos": general_novos,
                            "pendentes": general_pendentes,
                            "progresso": general_progresso,
                            "resolvidos": general_resolvidos,
                            "total": general_total
                        },
                        "n1": level_metrics["n1"],
                        "n2": level_metrics["n2"],
                        "n3": level_metrics["n3"],
                        "n4": level_metrics["n4"]
                    },
                    "tendencias": self._calculate_trends(general_novos, general_pendentes, general_progresso, general_resolvidos)
                },
                "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                "tempo_execucao": (time.time() - start_time) * 1000
            }
            
            # Salvar no cache
            self._set_cache_data('dashboard_metrics', result, ttl=180)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao obter mtricas do dashboard: {e}")
            return ResponseFormatter.format_error_response(f"Erro interno: {str(e)}", [str(e)])
    
    def _get_general_totals_internal(self, start_date: str = None, end_date: str = None) -> dict:
        """Mtodo interno para obter totais gerais com filtro de data"""
        status_totals = {}
        
        # Buscar totais por status sem filtro de grupo (mesma lgica do _get_general_metrics_internal)
        for status_name, status_id in self.status_map.items():
            search_params = {
                "is_deleted": 0,
                "range": "0-0",
                "criteria[0][field]": self.field_ids["STATUS"],
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": status_id,
            }
            
            # Adicionar filtros de data se fornecidos (formato ISO funciona melhor)
            criteria_index = 1
            if start_date:
                # Usar formato ISO (YYYY-MM-DD) que funciona corretamente
                search_params[f"criteria[{criteria_index}][link]"] = "AND"
                search_params[f"criteria[{criteria_index}][field]"] = "15"  # Campo 15  o correto para data de criao
                search_params[f"criteria[{criteria_index}][searchtype]"] = "morethan"
                search_params[f"criteria[{criteria_index}][value]"] = start_date
                criteria_index += 1
                
            if end_date:
                # Usar formato ISO (YYYY-MM-DD) que funciona corretamente
                search_params[f"criteria[{criteria_index}][link]"] = "AND"
                search_params[f"criteria[{criteria_index}][field]"] = "15"  # Campo 15  o correto para data de criao
                search_params[f"criteria[{criteria_index}][searchtype]"] = "lessthan"
                search_params[f"criteria[{criteria_index}][value]"] = end_date
            
            try:
                response = self._make_authenticated_request(
                    'GET',
                    f"{self.glpi_url}/search/Ticket",
                    params=search_params
                )
                
                if response and "Content-Range" in response.headers:
                    count = int(response.headers["Content-Range"].split("/")[-1])
                    status_totals[status_name] = count
                else:
                    status_totals[status_name] = 0
                    
            except Exception as e:
                self.logger.error(f"Erro ao buscar contagem geral para {status_name}: {e}")
                status_totals[status_name] = 0
        
        return status_totals
    
    def get_dashboard_metrics_with_date_filter(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, any]:
        """Retorna mtricas formatadas para o dashboard React com filtro de data.
        
        Args:
            start_date: Data inicial no formato YYYY-MM-DD (opcional)
            end_date: Data final no formato YYYY-MM-DD (opcional)
        
        Retorna um dicionrio com as mtricas ou None em caso de falha.
        """
        # Criar chave de cache baseada nos parmetros de data
        cache_key = f"{start_date or 'none'}_{end_date or 'none'}"
        
        # Verificar se existe cache vlido para este filtro
        if self._is_cache_valid('dashboard_metrics_filtered', cache_key):
            cached_data = self._get_cache_data('dashboard_metrics_filtered', cache_key)
            if cached_data:
                self.logger.info(f"Retornando mtricas do cache para filtro: {cache_key}")
                return cached_data
        
        # Autenticar uma nica vez
        if not self._ensure_authenticated():
            return None
        
        if not self.discover_field_ids():
            return None
        
        # Obter totais gerais (todos os grupos) para mtricas principais com filtro de data
        general_totals = self._get_general_metrics_internal(start_date, end_date)
        self.logger.info(f"Totais gerais obtidos com filtro de data: {general_totals}")
        
        # Obter mtricas por nvel (grupos N1-N4) com filtro de data
        raw_metrics = self._get_metrics_by_level_internal(start_date, end_date)
        
        # Agregao dos totais por status (apenas para nveis)
        totals = {
            "novos": 0,
            "pendentes": 0,
            "progresso": 0,
            "resolvidos": 0
        }
        
        # Mtricas por nvel
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
            
            # Progresso (soma de Processando atribudo e planejado)
            processando_atribuido = level_data.get("Processando (atribudo)", 0)
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
        
        # Usar totais gerais para mtricas principais
        general_novos = general_totals.get("Novo", 0)
        general_pendentes = general_totals.get("Pendente", 0)
        general_progresso = general_totals.get("Processando (atribudo)", 0) + general_totals.get("Processando (planejado)", 0)
        general_resolvidos = general_totals.get("Solucionado", 0) + general_totals.get("Fechado", 0)
        general_total = general_novos + general_pendentes + general_progresso + general_resolvidos
        
        self.logger.info(f"Mtricas gerais calculadas com filtro: novos={general_novos}, pendentes={general_pendentes}, progresso={general_progresso}, resolvidos={general_resolvidos}, total={general_total}")
        
        result = {
            "success": True,
            "data": {
                "niveis": {
                    "geral": {
                        "novos": general_novos,
                        "pendentes": general_pendentes,
                        "progresso": general_progresso,
                        "resolvidos": general_resolvidos,
                        "total": general_total
                    },
                    "n1": level_metrics["n1"],
                    "n2": level_metrics["n2"],
                    "n3": level_metrics["n3"],
                    "n4": level_metrics["n4"]
                },
                "tendencias": self._get_trends_with_logging(general_novos, general_pendentes, general_progresso, general_resolvidos, start_date, end_date),
                "filtros_aplicados": {
                    "data_inicio": start_date,
                    "data_fim": end_date
                }
            },
            "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        }
        
        self.logger.info(f"Mtricas formatadas com filtro de data: {result}")
        
        # Salvar no cache com TTL de 3 minutos
        self._set_cache_data('dashboard_metrics_filtered', result, ttl=180, sub_key=cache_key)
        
        return result
    
    def _get_trends_with_logging(self, general_novos: int, general_pendentes: int, general_progresso: int, general_resolvidos: int, start_date: str, end_date: str) -> dict:
        """Funo auxiliar para fazer log e chamar _calculate_trends"""
        self.logger.info(f"Chamando _calculate_trends com start_date={start_date}, end_date={end_date}")
        return self._calculate_trends(general_novos, general_pendentes, general_progresso, general_resolvidos, start_date, end_date)
    
    def _calculate_trends(self, current_novos: int, current_pendentes: int, current_progresso: int, current_resolvidos: int, current_start_date: Optional[str] = None, current_end_date: Optional[str] = None) -> dict:
        """Calcula as tendncias comparando dados atuais com perodo anterior
        
        Args:
            current_novos: Nmero atual de tickets novos
            current_pendentes: Nmero atual de tickets pendentes
            current_progresso: Nmero atual de tickets em progresso
            current_resolvidos: Nmero atual de tickets resolvidos
            current_start_date: Data inicial do perodo atual (opcional)
            current_end_date: Data final do perodo atual (opcional)
        """
        self.logger.info(f"_calculate_trends chamada com: novos={current_novos}, pendentes={current_pendentes}, progresso={current_progresso}, resolvidos={current_resolvidos}, start_date={current_start_date}, end_date={current_end_date}")
        try:
            from datetime import datetime, timedelta
            
            # Se h filtros de data aplicados, calcular perodo anterior baseado neles
            if current_start_date and current_end_date:
                # Calcular a durao do perodo atual
                current_start = datetime.strptime(current_start_date, '%Y-%m-%d')
                current_end = datetime.strptime(current_end_date, '%Y-%m-%d')
                period_duration = (current_end - current_start).days
                
                # Calcular perodo anterior com a mesma durao
                end_date_previous = (current_start - timedelta(days=1)).strftime('%Y-%m-%d')
                start_date_previous = (current_start - timedelta(days=period_duration + 1)).strftime('%Y-%m-%d')
                
                self.logger.info(f"Calculando tendncias com filtro: perodo atual {current_start_date} a {current_end_date}, perodo anterior {start_date_previous} a {end_date_previous}")
            else:
                # Usar perodo padro de 7 dias
                end_date_previous = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                start_date_previous = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
                
                self.logger.info(f"Calculando tendncias sem filtro: perodo anterior {start_date_previous} a {end_date_previous}")
            
            # Obter mtricas do perodo anterior
            previous_general = self._get_general_totals_internal(start_date_previous, end_date_previous)
            
            # Calcular totais do perodo anterior
            previous_novos = previous_general.get("Novo", 0)
            previous_pendentes = previous_general.get("Pendente", 0)
            previous_progresso = previous_general.get("Processando (atribudo)", 0) + previous_general.get("Processando (planejado)", 0)
            previous_resolvidos = previous_general.get("Solucionado", 0) + previous_general.get("Fechado", 0)
            
            self.logger.info(f"Dados perodo anterior: novos={previous_novos}, pendentes={previous_pendentes}, progresso={previous_progresso}, resolvidos={previous_resolvidos}")
            self.logger.info(f"Dados perodo atual: novos={current_novos}, pendentes={current_pendentes}, progresso={current_progresso}, resolvidos={current_resolvidos}")
            
            # Calcular percentuais de variao
            def calculate_percentage_change(current: int, previous: int) -> str:
                if previous == 0:
                    return "+100%" if current > 0 else "0%"
                
                change = ((current - previous) / previous) * 100
                if change > 0:
                    return f"+{change:.1f}%"
                elif change < 0:
                    return f"{change:.1f}%"
                else:
                    return "0%"
            
            trends = {
                "novos": calculate_percentage_change(current_novos, previous_novos),
                "pendentes": calculate_percentage_change(current_pendentes, previous_pendentes),
                "progresso": calculate_percentage_change(current_progresso, previous_progresso),
                "resolvidos": calculate_percentage_change(current_resolvidos, previous_resolvidos)
            }
            
            self.logger.info(f"Tendncias calculadas: {trends}")
            return trends
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular tendncias: {e}")
            import traceback
            self.logger.error(f"Stack trace: {traceback.format_exc()}")
            # Retornar valores padro em caso de erro
            return {
                "novos": "0%",
                "pendentes": "0%",
                "progresso": "0%",
                "resolvidos": "0%"
            }
    
    def get_technician_ranking(self, limit: int = None) -> list:
        """Retorna ranking de t�cnicos por total de chamados seguindo a base de conhecimento
        
        Implementao otimizada que:
        1. Usa cache inteligente com TTL de 5 minutos
        2. Busca APENAS t�cnicos com perfil ID 6 (Tcnico)
        3. Usa consulta direta sem iterao por todos os usurios
        4. Segue exatamente a estrutura da base de conhecimento
        """
        self.logger.info("=== INICIANDO GET_TECHNICIAN_RANKING ===")
        
        # Log para arquivo para debug
        with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
            import datetime
            f.write(f"\n{datetime.datetime.now()} - INICIANDO GET_TECHNICIAN_RANKING\n")
            f.flush()
        
        # Temporariamente desabilitar cache para debug
        cache_key = 'technician_ranking'
        # cached_data = self._get_cached_data(cache_key)
        # if cached_data is not None:
        #     self.logger.info("Retornando ranking de t�cnicos do cache")
        #     return cached_data
        self.logger.info("Cache desabilitado para debug - sempre buscando dados frescos")
        
        self.logger.info("Iniciando busca otimizada de ranking de t�cnicos (sem iterao extensa)...")
        
        # Verificar autenticao
        self.logger.info("Verificando autenticao...")
        if not self._ensure_authenticated():
            self.logger.error("FALHA NA AUTENTICAO - retornando lista vazia")
            return []
        
        self.logger.info("Autenticao OK, prosseguindo...")
        
        try:
            # Implementao seguindo a base de conhecimento
            self.logger.info("Chamando _get_technician_ranking_knowledge_base()...")
            ranking = self._get_technician_ranking_knowledge_base()
            
            self.logger.info(f"Resultado da busca: {len(ranking) if ranking else 0} t�cnicos")
            
            # Armazenar no cache
            if ranking:
                self._set_cached_data(cache_key, ranking)
                self.logger.info("Dados armazenados no cache")
            
            self.logger.info(f"=== RANKING FINAL: {len(ranking)} t�cnicos encontrados (sem iterao extensa) ===")
            
            # Aplicar limite se especificado
            if limit and len(ranking) > limit:
                ranking = ranking[:limit]
                self.logger.info(f"Ranking limitado a {limit} t�cnicos")
            
            return ranking
            
        except Exception as e:
            self.logger.error(f"ERRO CRTICO ao buscar ranking de t�cnicos: {e}")
            import traceback
            self.logger.error(f"Stack trace: {traceback.format_exc()}")
            return []
    
    def _discover_tech_field_id(self) -> Optional[str]:
        """Descobre dinamicamente o field ID do t�cnico atribudo"""
        try:
            response = self._make_authenticated_request(
                'GET',
                f"{self.glpi_url}/listSearchOptions/Ticket"
            )
            if not response:
                return None
            search_options = response.json()
            
            # Procurar por campos relacionados ao t�cnico atribudo
            # Baseado no debug, o campo "5"  "T�cnico" e "95"  "T�cnico encarregado"
            tech_field_mapping = {
                "5": "T�cnico",
                "95": "T�cnico encarregado"
            }
            
            # Primeiro, tentar os campos conhecidos
            for field_id, expected_name in tech_field_mapping.items():
                if field_id in search_options:
                    field_data = search_options[field_id]
                    if isinstance(field_data, dict) and "name" in field_data:
                        field_name = field_data["name"]
                        if field_name == expected_name:
                            self.logger.info(f"Campo de t�cnico encontrado: {field_name} (ID: {field_id})")
                            return field_id
            
            # Fallback: procurar por nomes
            tech_field_names = ["T�cnico", "Atribu�do", "Assigned to", "Technician", "T�cnico encarregado"]
            
            for field_id, field_data in search_options.items():
                if isinstance(field_data, dict) and "name" in field_data:
                    field_name = field_data["name"]
                    if field_name in tech_field_names:
                        self.logger.info(f"Campo de t�cnico encontrado (fallback): {field_name} (ID: {field_id})")
                        return field_id
            
            self.logger.error("Campo de t�cnico atribudo no encontrado")
            return None
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro ao descobrir field ID do t�cnico: {e}")
            return None
    
    def _get_technician_ranking_knowledge_base(self) -> list:
        """Implementao seguindo exatamente a base de conhecimento fornecida
        
        Esta Implementao:
        1. Usa consulta direta de t�cnicos ativos com perfil ID 6
        2. Evita iterao por todos os usurios do sistema
        3. Usa forcedisplay para trazer apenas campos necessrios
        4. Segue a estrutura exata da base de conhecimento
        """
        try:
            self.logger.info("=== INICIANDO CONSULTA OTIMIZADA (BASE DE CONHECIMENTO) ===")
            self.logger.info("Mtodo _get_technician_ranking_knowledge_base foi chamado")
            
            # Log para arquivo para debug
            with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                import datetime
                f.write(f"{datetime.datetime.now()} - MTODO _get_technician_ranking_knowledge_base CHAMADO\n")
                f.flush()
            
            # 1.1 Consulta de Tcnicos Ativos (corrigida)
            # Primeiro, buscar usurios com perfil de t�cnico usando Profile_User
            profile_params = {
                "range": "0-999",
                "criteria[0][field]": "4",  # Campo Perfil na tabela Profile_User
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": "6",  # ID do perfil t�cnico
                "forcedisplay[0]": "2",  # ID do Profile_User
                "forcedisplay[1]": "5",  # Usurio (users_id)
                "forcedisplay[2]": "4",  # Perfil
                "forcedisplay[3]": "80"  # Entidade
            }
            
            self.logger.info(f"Buscando usurios com perfil ID 6 (parmetros: {profile_params})")
            
            # Log para arquivo para debug
            with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now()} - Iniciando busca Profile_User com parmetros: {profile_params}\n")
                f.flush()
            
            # Buscar relao Profile_User para obter IDs dos t�cnicos
            response = self._make_authenticated_request(
                'GET',
                f"{self.glpi_url}/search/Profile_User",
                params=profile_params
            )
            
            if not response:
                self.logger.error("Falha ao buscar usurios com perfil de t�cnico")
                with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.datetime.now()} - ERRO: Falha ao buscar usurios com perfil de t�cnico\n")
                    f.flush()
                return []
            
            profile_result = response.json()
            self.logger.info(f"Resposta da busca de Profile_User: {profile_result}")
            
            # Log para arquivo para debug
            with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now()} - Resposta Profile_User recebida: {str(profile_result)[:500]}...\n")
                f.flush()
            
            # A API do GLPI retorna um objeto com 'data', no uma lista direta
            if not isinstance(profile_result, dict):
                self.logger.error("Resposta invlida da busca de Profile_User")
                return []
            
            # Verificar se h dados
            total_count = profile_result.get('totalcount', 0)
            self.logger.info(f"Total de usurios com perfil ID 6: {total_count}")
            
            if total_count == 0:
                self.logger.warning("Nenhum usurio encontrado com perfil de t�cnico")
                return []
            
            # Extrair dados dos usurios
            profile_data = profile_result.get('data', [])
            if not profile_data:
                self.logger.error("Dados de Profile_User no encontrados na resposta")
                return []
            
            # Extrair IDs dos usurios
            tech_user_ids = []
            for profile_user in profile_data:
                if isinstance(profile_user, dict) and "5" in profile_user:  # Campo Usurio (users_id)
                    # O campo 5 pode retornar o nome do usurio, precisamos extrair o ID
                    user_info = profile_user["5"]
                    # Se for um string, pode ser o nome do usurio, precisamos buscar o ID
                    # Por enquanto, vamos tentar extrair o ID do campo 2 (ID do Profile_User)
                    if "2" in profile_user:
                        # Vamos usar uma abordagem diferente: buscar diretamente os usurios
                        # por enquanto, vamos pular esta extrao e usar uma busca direta
                        pass
            
            # Como a extrao do users_id  complexa, vamos usar uma abordagem alternativa
            # Buscar diretamente os usurios com perfil de t�cnico
            self.logger.info("Usando abordagem alternativa: busca direta de usurios")
            
            # Buscar usurios ativos (removendo filtro is_deleted por enquanto para testar)
            user_params = {
                'range': '0-999',
                'criteria[0][field]': '8',  # Campo is_active
                'criteria[0][searchtype]': 'equals',
                'criteria[0][value]': '1',
                'forcedisplay[0]': '2',  # ID
                'forcedisplay[1]': '1',  # Nome de usurio
                'forcedisplay[2]': '9',  # Primeiro nome (realname)
                'forcedisplay[3]': '34'  # Sobrenome (firstname)
            }
            
            # Log para arquivo para debug
            with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now()} - Iniciando busca de usurios ativos com parmetros: {user_params}\n")
                f.flush()
            
            user_response = self._make_authenticated_request(
                'GET',
                f"{self.glpi_url}/search/User",
                params=user_params
            )
            
            # Log para arquivo para debug
            with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now()} - Resposta da busca de usurios: {user_response is not None}\n")
                if user_response:
                    f.write(f"Status code: {user_response.status_code}\n")
                f.flush()
            
            if not user_response or not user_response.ok:
                self.logger.error(f"Falha ao buscar usurios ativos - Status: {user_response.status_code if user_response else 'None'}")
                with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.datetime.now()} - ERRO: Falha ao buscar usurios ativos\n")
                    f.flush()
                return []
            
            user_result = user_response.json()
            
            # Log para arquivo para debug
            with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now()} - Resultado da busca de usurios: totalcount={user_result.get('totalcount', 0)}\n")
                f.flush()
            
            if not isinstance(user_result, dict) or user_result.get('totalcount', 0) == 0:
                self.logger.warning("Nenhum usurio ativo encontrado")
                with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.datetime.now()} - AVISO: Nenhum usurio ativo encontrado\n")
                    f.flush()
                return []

            all_users = user_result.get('data', [])
            self.logger.info(f"Encontrados {len(all_users)} usurios ativos")
            
            # Log para arquivo para debug
            with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now()} - Encontrados {len(all_users)} usurios ativos\n")
                f.flush()
            
            # Usar os dados j obtidos dos usurios com perfil de t�cnico
            # Extrair IDs dos usurios que j sabemos que tm perfil de t�cnico
            tech_user_ids = set()  # Usar set para evitar duplicatas
            tech_users_data = {}
            
            # Processar dados dos usurios com perfil de t�cnico j obtidos
            profile_users_data = profile_result.get('data', [])
            
            # Log para arquivo para debug
            with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now()} - Processando {len(profile_users_data)} registros de Profile_User\n")
                f.flush()
            
            for profile_user in profile_users_data:
                if isinstance(profile_user, dict):
                    # Log para arquivo para debug - mostrar todos os campos disponveis
                    with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                        f.write(f"{datetime.datetime.now()} - Dados do Profile_User: {profile_user}\n")
                        f.flush()
                    
                    # O campo 5 contm o nome de usurio (username), no o ID
                    # Precisamos buscar o ID do usurio usando o username
                    if "5" in profile_user:
                        username = str(profile_user["5"])
                        # Armazenar o username para buscar o ID depois (usar set evita duplicatas)
                        tech_user_ids.add(username)
                        # Armazenar dados do usurio para uso posterior
                        tech_users_data[username] = profile_user
                        
                        # Log para arquivo para debug
                        with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                            f.write(f"{datetime.datetime.now()} - Username do t�cnico extrado: {username}\n")
                            f.flush()
            
            # Criar um mapa de usurios ativos para acesso rpido usando username
            active_users_map = {}
            for user in all_users:
                if isinstance(user, dict) and "1" in user:  # Campo 1  o username
                    username = str(user["1"])
                    active_users_map[username] = user
                    
                    # Log para arquivo para debug
                    with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                        f.write(f"{datetime.datetime.now()} - Usurio ativo mapeado: {username}\n")
                        f.flush()
            
            self.logger.info(f"Encontrados {len(tech_user_ids)} usurios com perfil ID 6")
            
            if not tech_user_ids:
                self.logger.warning("Nenhum usurio encontrado com perfil de t�cnico")
                return []
            
            # Descobrir field ID do t�cnico para contagem de tickets
            tech_field_id = self._discover_tech_field_id()
            if not tech_field_id:
                self.logger.error("Falha ao descobrir field ID do t�cnico")
                with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.datetime.now()} - ERRO: Falha ao descobrir field ID do t�cnico\n")
                    f.flush()
                return []
            
            self.logger.info(f"Field ID do t�cnico descoberto: {tech_field_id}")
            
            # Log para arquivo para debug
            with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now()} - Field ID do t�cnico descoberto: {tech_field_id}\n")
                f.flush()
            
            # Processar apenas os t�cnicos ativos usando os mapas otimizados
            ranking = []
            tech_user_ids_list = list(tech_user_ids)  # Converter set para lista
            self.logger.info(f"Processando {len(tech_user_ids_list)} t�cnicos: {tech_user_ids_list[:5]}...")
            self.logger.info(f"Usurios ativos disponveis: {len(active_users_map)} usurios")
            active_user_ids_sample = list(active_users_map.keys())[:10]
            self.logger.info(f"Amostra de IDs de usurios ativos: {active_user_ids_sample}")
            self.logger.info(f"Tipos de IDs - Tcnicos: {type(tech_user_ids_list[0]) if tech_user_ids_list else 'N/A'}, Ativos: {type(active_user_ids_sample[0]) if active_user_ids_sample else 'N/A'}")
            
            # Log para arquivo para debug
            with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now()} - Iniciando filtro de t�cnicos ativos\n")
                f.write(f"Total de t�cnicos: {len(tech_user_ids_list)}\n")
                f.write(f"Total de usurios ativos: {len(active_users_map)}\n")
                f.flush()
            
            # Filtrar apenas t�cnicos que esto ativos e no deletados usando usernames
            active_tech_usernames = [username for username in tech_user_ids_list if username in active_users_map]
            self.logger.info(f"Encontrados {len(active_tech_usernames)} t�cnicos ativos e no deletados de {len(tech_user_ids_list)} total")
            
            # Log para arquivo para debug
            with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now()} - Encontrados {len(active_tech_usernames)} t�cnicos ativos de {len(tech_user_ids)} total\n")
                f.write(f"Tcnicos ativos encontrados: {active_tech_usernames[:10]}\n")
                f.flush()
            
            if not active_tech_usernames:
                self.logger.warning("Nenhum t�cnico ativo e no deletado encontrado")
                with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.datetime.now()} - AVISO: Nenhum t�cnico ativo encontrado\n")
                    f.flush()
                return []
            
            self.logger.info(f"Processando {len(active_tech_usernames)} t�cnicos ativos")
            
            # Log para arquivo para debug
            with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now()} - Processando {len(active_tech_usernames)} t�cnicos ativos\n")
                f.flush()
            
            for username in active_tech_usernames:
                # Obter o ID do usurio dos dados ativos
                user_data_active = active_users_map.get(username)
                if not user_data_active or "2" not in user_data_active:
                    # Log para arquivo para debug
                    with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                        f.write(f"{datetime.datetime.now()} - ERRO: Dados do usurio ativo no encontrados para {username}\n")
                        f.flush()
                    continue
                
                user_id = str(user_data_active["2"])
                
                # Log para arquivo para debug
                with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.datetime.now()} - Processando t�cnico {username} (ID: {user_id})\n")
                    f.flush()
                
                # Buscar dados do t�cnico diretamente da API
                user_response = self._make_authenticated_request(
                    'GET',
                    f"{self.glpi_url}/User/{user_id}"
                )
                
                # Log para arquivo para debug
                with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.datetime.now()} - Resposta inicial para t�cnico {user_id}: {type(user_response)} - {user_response is not None}\n")
                    if user_response is not None:
                        f.write(f"Status code: {user_response.status_code}\n")
                        f.write(f"Response OK: {user_response.ok}\n")
                        f.write(f"Response type: {type(user_response)}\n")
                    else:
                        f.write(f"user_response  None desde o incio!\n")
                    f.flush()
                
                if not user_response or not user_response.ok:
                    with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                        if not user_response:
                            f.write(f"{datetime.datetime.now()} - ERRO: Resposta nula para t�cnico {user_id}\n")
                        else:
                            f.write(f"{datetime.datetime.now()} - ERRO: Status {user_response.status_code} para t�cnico {user_id} (usurio no encontrado ou inacessvel)\n")
                        f.flush()
                    continue
                
                try:
                    user_data = user_response.json()
                    # Log do contedo da resposta para debug
                    with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                        f.write(f"{datetime.datetime.now()} - Contedo JSON para t�cnico {user_id}: {str(user_data)[:200]}...\n")
                        f.flush()
                except Exception as e:
                    with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                        f.write(f"{datetime.datetime.now()} - ERRO JSON para t�cnico {user_id}: {e}\n")
                        f.flush()
                    continue
                
                if not user_data:
                    with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                        f.write(f"{datetime.datetime.now()} - ERRO: Dados vazios para t�cnico {user_id}\n")
                        f.flush()
                    continue
                    
                # Log para arquivo para debug
                with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.datetime.now()} - Dados do t�cnico {user_id} obtidos com sucesso\n")
                    f.flush()
                
                # user_data j foi obtido acima via user_response.json()
                if user_data:
                    user = user_data
                    try:
                        # Construir nome de exibio a partir dos dados da API
                        display_name = ""
                        if "realname" in user and "firstname" in user:  # Nome e Sobrenome
                            display_name = f"{user['firstname']} {user['realname']}"
                        elif "realname" in user:  # Apenas sobrenome
                            display_name = user["realname"]
                        elif "name" in user:  # Nome de usurio
                            display_name = user["name"]
                        elif "1" in user:  # Fallback para campo 1
                            display_name = user["1"]
                            
                        if not display_name or not display_name.strip():
                            self.logger.warning(f"Usurio {user_id} sem nome vlido")
                            # Log para debug
                            with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                                f.write(f"{datetime.datetime.now()} - ERRO: Usurio {user_id} sem nome vlido. Dados: {str(user)[:100]}...\n")
                                f.flush()
                            continue
                        
                        self.logger.info(f"Processando t�cnico: {display_name} (ID: {user_id})")
                        
                        # Contar tickets do t�cnico
                        total_tickets = self._count_tickets_by_technician_optimized(int(user_id), tech_field_id)
                        
                        if total_tickets is not None:
                            ranking.append({
                                "id": str(user_id),
                                "nome": display_name.strip(),
                                "name": display_name.strip(),
                                "total": total_tickets,
                                "level": "N1"  # Temporrio, ser atualizado aps ordenao
                            })
                            self.logger.info(f"Tcnico {display_name} (ID: {user_id}): {total_tickets} tickets")
                        
                    except Exception as e:
                        self.logger.error(f"Erro ao processar usurio {user_id}: {e}")
                        continue
            
            # Ordenar por total de tickets (decrescente)
            ranking.sort(key=lambda x: x["total"], reverse=True)
            
            # Atribuir nveis baseados no mapeamento manual dos grupos
            total_count = len(ranking)
            self.logger.info(f"Atribuindo nveis para {total_count} t�cnicos baseado no mapeamento manual")
            
            for idx, item in enumerate(ranking):
                user_id = int(item['id'])
                
                # Usar o mtodo _get_technician_level para determinar o nvel correto
                level = self._get_technician_level(user_id, item['total'], ranking)
                
                item["level"] = level
                item["rank"] = idx + 1
                
                self.logger.info(f"Tcnico {item['name']} (Rank {idx + 1}): {item['total']} tickets - Nvel: {level}")
            
            self.logger.info(f"=== RANKING FINALIZADO: {len(ranking)} t�cnicos processados ===")
            
            # Log para arquivo para debug
            with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now()} - RANKING FINALIZADO: {len(ranking)} t�cnicos processados\n")
                f.write(f"Ranking final: {ranking}\n")
                f.flush()
            
            return ranking
            
        except Exception as e:
            self.logger.error(f"Erro na Implementao da base de conhecimento: {e}")
            import traceback
            self.logger.error(f"Stack trace: {traceback.format_exc()}")
            
            # Log para arquivo para debug
            with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now()} - ERRO CRTICO: {e}\n")
                f.write(f"Stack trace: {traceback.format_exc()}\n")
                f.flush()
            
            return []
    
    def _get_technician_level(self, user_id: int, total_tickets: int = 0, all_technicians_data: list = None) -> str:
        """Atribui nvel do t�cnico baseado nos grupos do GLPI
        
        Mapeamento correto dos t�cnicos por grupos:
        - N1 (ID 89): Gabriel Andrade da Conceicao, Nicolas Fernando Muniz Nunez
        - N2 (ID 90): Alessandro Carbonera Vieira, Edson Joel dos Santos Silva, Luciano Marcelino da Silva, 
                      Jonathan Nascimento Moletta, Leonardo Trojan Repiso Riela, Thales Vinicius Paz Leite
        - N3 (ID 91): Jorge Antonio Vicente Junior, Anderson da Silva Morim de Oliveira, Miguelangelo Ferreira,
                      Silvio Godinho Valim, Pablo Hebling Guimaraes
        - N4 (ID 92): Paulo Cesar Pedo Nunes, Luciano de Araujo Silva, Wagner Mengue, 
                      Alexandre Rovinski Almoarqueg, Gabriel Silva Machado
        """
        try:
            # Buscar grupos do usurio
            response = self._make_authenticated_request(
                'GET',
                f"{self.glpi_url}/search/Group_User",
                params={
                    "range": "0-99",
                    "criteria[0][field]": "4",  # Campo users_id
                    "criteria[0][searchtype]": "equals",
                    "criteria[0][value]": str(user_id),
                    "forcedisplay[0]": "3",  # groups_id
                    "forcedisplay[1]": "4",  # users_id
                }
            )
            
            if response and response.ok:
                group_data = response.json()
                
                if group_data.get('data'):
                    for group_entry in group_data['data']:
                        if isinstance(group_entry, dict) and "3" in group_entry:
                            group_id = int(group_entry["3"])
                            
                            # Verificar se o grupo corresponde aos service_levels
                            for level, level_group_id in self.service_levels.items():
                                if group_id == level_group_id:
                                    self.logger.info(f"Tcnico {user_id} encontrado no grupo {group_id} -> {level}")
                                    return level
            
            # Se no encontrou nos grupos configurados, usar fallback baseado no nome do usurio
            # (para casos onde o t�cnico no est nos grupos mas est na lista fornecida)
            try:
                user_response = self._make_authenticated_request(
                    'GET',
                    f"{self.glpi_url}/User/{user_id}"
                )
                
                if user_response and user_response.ok:
                    user_data = user_response.json()
                    # Construir nome completo como no mtodo get_technician_ranking
                    display_name = ""
                    if "realname" in user_data and "firstname" in user_data:
                        display_name = f"{user_data['firstname']} {user_data['realname']}"
                    elif "realname" in user_data:
                        display_name = user_data["realname"]
                    elif "name" in user_data:
                        display_name = user_data["name"]
                    elif "1" in user_data:
                        display_name = user_data["1"]
                    
                    user_name = display_name.lower().strip()
                    
                    # Mapeamento manual baseado nos nomes exatos do GLPI
                    n1_names = ['gabriel andrade da conceicao', 'nicolas fernando muniz nunez']
                    n2_names = ['alessandro carbonera vieira', 'jonathan nascimento moletta', 'thales vinicius paz leite', 'leonardo trojan repiso riela', 'edson joel dos santos silva', 'luciano marcelino da silva']
                    n3_names = ['anderson da silva morim de oliveira', 'silvio godinho valim', 'jorge antonio vicente jnior', 'pablo hebling guimaraes', 'miguelangelo ferreira']
                    n4_names = ['gabriel silva machado', 'luciano de araujo silva', 'wagner mengue', 'paulo csar ped nunes', 'alexandre rovinski almoarqueg']
                    
                    if user_name in n4_names:
                        self.logger.info(f"Tcnico {user_id} ({user_name}) mapeado para N4 por nome")
                        return "N4"
                    elif user_name in n3_names:
                        self.logger.info(f"Tcnico {user_id} ({user_name}) mapeado para N3 por nome")
                        return "N3"
                    elif user_name in n2_names:
                        self.logger.info(f"Tcnico {user_id} ({user_name}) mapeado para N2 por nome")
                        return "N2"
                    elif user_name in n1_names:
                        self.logger.info(f"Tcnico {user_id} ({user_name}) mapeado para N1 por nome")
                        return "N1"
            except Exception as e:
                self.logger.warning(f"Erro ao buscar nome do usurio {user_id}: {e}")
            
            # Fallback final
            self.logger.warning(f"Tcnico {user_id} no encontrado nos grupos ou mapeamento - usando N1 como padro")
            return "N1"
                
        except Exception as e:
            self.logger.error(f"Erro ao determinar nvel do t�cnico {user_id}: {e}")
            return "N1"  # Nvel padro em caso de erro
    
    def _get_technician_ranking_fallback(self) -> list:
        """Mtodo de fallback usando a Implementao original mais robusta"""
        try:
            # Usar mtodo original como fallback
            active_techs = self._list_active_technicians_fallback()
            if not active_techs:
                return []
            
            tech_field_id = self._discover_tech_field_id()
            if not tech_field_id:
                return []
            
            ranking = []
            for tech_id, tech_name in active_techs:
                total_tickets = self._count_tickets_by_technician(tech_id, tech_field_id)
                if total_tickets is not None:
                    ranking.append({
                        "id": str(tech_id),
                        "nome": tech_name,
                        "name": tech_name,
                        "total": total_tickets
                    })
            
            # Ordenar e atribuir ranks
            ranking.sort(key=lambda x: x["total"], reverse=True)
            for idx, item in enumerate(ranking, start=1):
                item["rank"] = idx
            
            return ranking
            
        except Exception as e:
            self.logger.error(f"Erro no mtodo de fallback: {e}")
            return []
    
    def _list_active_technicians_fallback(self) -> list:
        """Mtodo de fallback para listar t�cnicos ativos (Implementao original)"""
        # Verificar cache primeiro
        cache_key = 'active_technicians'
        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            self.logger.info("Retornando lista de t�cnicos ativos do cache")
            return cached_data
        
        try:
            # Buscar usurios com perfil de t�cnico (ID 6)
            params = {
                "range": "0-9999",
                "criteria[0][field]": "profiles_id",
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": 6  # ID do perfil de t�cnico
            }
            
            response = self._make_authenticated_request(
                'GET',
                f"{self.glpi_url}/Profile_User",
                params=params
            )
            
            if not response:
                self.logger.error("Falha ao buscar usurios com perfil de t�cnico")
                return []
                
            profile_users = response.json()
            self.logger.info(f"Encontrados {len(profile_users)} registros de Profile_User com perfil de t�cnico")
            
            # Extrair IDs dos usurios
            tech_user_ids = []
            for profile_user in profile_users:
                if isinstance(profile_user, dict) and "users_id" in profile_user:
                    tech_user_ids.append(profile_user["users_id"])
            
            if not tech_user_ids:
                self.logger.warning("Nenhum usurio encontrado com perfil de t�cnico")
                return []
            
            # Buscar dados completos dos usurios em lotes para otimizar
            technicians = []
            batch_size = 10  # Processar em lotes de 10
            
            for i in range(0, len(tech_user_ids), batch_size):
                batch_ids = tech_user_ids[i:i + batch_size]
                self.logger.info(f"Processando lote {i//batch_size + 1}: IDs {batch_ids}")
                
                for user_id in batch_ids:
                    try:
                        user_response = self._make_authenticated_request(
                            'GET',
                            f"{self.glpi_url}/User/{user_id}"
                        )
                        
                        if user_response:
                            user_data = user_response.json()
                            
                            # Verificar se o usurio est ativo e no deletado
                            if (isinstance(user_data, dict) and 
                                user_data.get("is_active", 0) == 1 and 
                                user_data.get("is_deleted", 1) == 0):
                                
                                # Construir nome de exibio
                                display_name = ""
                                if user_data.get("realname") and user_data.get("firstname"):
                                    display_name = f"{user_data['firstname']} {user_data['realname']}"
                                elif user_data.get("realname"):
                                    display_name = user_data["realname"]
                                elif user_data.get("name"):
                                    display_name = user_data["name"]
                                
                                if display_name.strip():
                                    technicians.append((user_id, display_name.strip()))
                                    self.logger.info(f"Tcnico ativo encontrado: {display_name} (ID: {user_id})")
                            
                    except Exception as e:
                        self.logger.error(f"Erro ao processar usurio {user_id}: {e}")
                        continue
            
            # Armazenar no cache
            self._set_cached_data(cache_key, technicians)
            
            self.logger.info(f"Total de t�cnicos ativos vlidos encontrados: {len(technicians)}")
            return technicians
            
        except Exception as e:
            self.logger.error(f"Erro ao listar t�cnicos ativos (fallback): {e}")
            return []
    
    def _count_tickets_by_technician_optimized(self, tech_id: int, tech_field_id: str) -> Optional[int]:
        """Conta tickets por t�cnico seguindo a base de conhecimento
        
        Usa range 0-0 para retornar apenas contagem (otimizado)
        """
        try:
            # Parmetros seguindo a base de conhecimento
            params = {
                "criteria[0][field]": tech_field_id,  # Campo "T�cnico" (field 5)
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": tech_id,
                "range": "0-0"  # Retorna apenas contagem
            }
            
            self.logger.info(f"Contando tickets para t�cnico {tech_id} com field {tech_field_id}")
            
            response = self._make_authenticated_request(
                'GET',
                f"{self.glpi_url}/search/Ticket",
                params=params
            )
            
            if not response:
                self.logger.error(f"Falha na requisio para contar tickets do t�cnico {tech_id}")
                return None
            
            # Extrair total do cabealho Content-Range
            if "Content-Range" in response.headers:
                content_range = response.headers["Content-Range"]
                total = int(content_range.split("/")[-1])
                self.logger.info(f"Tcnico {tech_id}: {total} tickets encontrados")
                return total
            
            self.logger.warning(f"Content-Range no encontrado para t�cnico {tech_id}")
            return 0
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro ao contar tickets do t�cnico {tech_id}: {e}")
            return None
        except (ValueError, IndexError) as e:
            self.logger.error(f"Erro ao processar Content-Range para t�cnico {tech_id}: {e}")
            return None
    
    def _count_tickets_by_technician(self, tech_id: int, tech_field_id: str) -> Optional[int]:
        """Mtodo mantido para compatibilidade - redireciona para verso otimizada"""
        return self._count_tickets_by_technician_optimized(tech_id, tech_field_id)

    def close_session(self):
        """Encerra a sesso com a API do GLPI"""
        if self.session_token:
            try:
                response = self._make_authenticated_request(
                    'GET',
                    f"{self.glpi_url}/killSession"
                )
                if response:
                    self.logger.info("Sesso encerrada com sucesso")
                else:
                    self.logger.warning("Falha ao encerrar sesso, mas continuando")
            except Exception as e:
                self.logger.error(f"Erro ao encerrar sesso: {e}")
            finally:
                self.session_token = None
                self.token_created_at = None
                self.token_expires_at = None
    
    def _get_cached_data(self, cache_key: str):
        """Recupera dados do cache se ainda vlidos (TTL customizvel)"""
        if cache_key not in self._cache:
            return None
        
        cache_entry = self._cache[cache_key]
        if cache_entry['data'] is None or cache_entry['timestamp'] is None:
            return None
        
        # Verificar se o cache ainda  vlido
        current_time = time.time()
        ttl = cache_entry.get('ttl', 300)  # TTL padro de 5 minutos
        if current_time - cache_entry['timestamp'] > ttl:
            # Cache expirado
            cache_entry['data'] = None
            cache_entry['timestamp'] = None
            return None
        
        return cache_entry['data']
    
    def _set_cached_data(self, cache_key: str, data, ttl: int = None):
        """Armazena dados no cache com TTL customizvel
        
        Args:
            cache_key: Chave do cache
            data: Dados a serem armazenados
            ttl: Time to live em segundos (usa TTL padro do cache se None)
        """
        if cache_key in self._cache:
            self._cache[cache_key]['data'] = data
            self._cache[cache_key]['timestamp'] = time.time()
            if ttl is not None:
                self._cache[cache_key]['ttl'] = ttl
    
    def _get_user_name_by_id(self, user_id: str) -> str:
        """Busca o nome do usurio pelo ID"""
        if not user_id or user_id == 'no informado':
            return 'no informado'
            
        try:
            # Verificar cache primeiro
            cache_key = f'user_name_{user_id}'
            cached_name = self._get_cache_data('user_names', cache_key)
            if cached_name:
                return cached_name
                
            # Buscar usurio por ID
            response = self._make_authenticated_request(
                'GET',
                f"{self.glpi_url}/User/{user_id}"
            )
            
            if not response or not response.ok:
                self.logger.warning(f"Falha ao buscar usurio {user_id}")
                return f"Usurio {user_id}"
                
            user_data = response.json()
            
            # Construir nome de exibio
            display_name = "Usurio desconhecido"
            if isinstance(user_data, dict):
                if user_data.get("realname") and user_data.get("firstname"):
                    display_name = f"{user_data['firstname']} {user_data['realname']}"
                elif user_data.get("realname"):
                    display_name = user_data["realname"]
                elif user_data.get("name"):
                    display_name = user_data["name"]
                elif user_data.get("firstname"):
                    display_name = user_data["firstname"]
                    
            # Armazenar no cache por 1 hora
            self._set_cache_data('user_names', display_name, 3600, cache_key)
            
            return display_name
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar nome do usurio {user_id}: {e}")
            return f"Usurio {user_id}"
    
    def _get_priority_name_by_id(self, priority_id: str) -> str:
        """Converte ID de prioridade do GLPI para nome legvel"""
        if not priority_id:
            return 'Mdia'
            
        try:
            # Verificar cache primeiro
            cache_key = f'priority_name_{priority_id}'
            if self._is_cache_valid('priority_names', cache_key):
                cached_name = self._get_cache_data('priority_names', cache_key)
                if cached_name:
                    return cached_name
                
            # Mapeamento padro de prioridades do GLPI
            priority_map = {
                '1': 'Muito Baixa',
                '2': 'Baixa', 
                '3': 'Mdia',
                '4': 'Alta',
                '5': 'Muito Alta',
                '6': 'Crtica'
            }
            
            priority_name = priority_map.get(str(priority_id), 'Mdia')
            
            # Armazenar no cache por 1 hora
            self._set_cache_data('priority_names', priority_name, 3600, cache_key)
            
            return priority_name
            
        except Exception as e:
            self.logger.error(f"Erro ao converter prioridade {priority_id}: {e}")
            return 'Mdia'
    
    def get_new_tickets(self, limit: int = 10) -> List[Dict[str, any]]:
        """Busca tickets com status 'novo' com detalhes completos"""
        if not self._ensure_authenticated():
            return []
            
        if not self.discover_field_ids():
            return []
        
        try:
            # Buscar ID do status 'novo' (geralmente 1)
            status_id = self.status_map.get('novos', 1)
            
            # Parmetros para buscar tickets com status novo
            search_params = {
                "is_deleted": 0,
                "range": f"0-{limit-1}",  # Limitar resultados
                "criteria[0][field]": self.field_ids["STATUS"],
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": status_id,
                "sort": "19",  # Ordenar por data de criao (campo 19)
                "order": "DESC"  # Mais recentes primeiro
            }
            
            response = self._make_authenticated_request(
                'GET',
                f"{self.glpi_url}/search/Ticket",
                params=search_params
            )
            
            if not response or not response.ok:
                self.logger.error("Falha ao buscar tickets novos")
                return []
            
            data = response.json()
            tickets = []
            
            if 'data' in data and data['data']:
                for ticket_data in data['data']:
                    # Extrair ID do requerente e buscar o nome
                    requester_id = ticket_data.get('4', '')
                    requester_name = self._get_user_name_by_id(str(requester_id)) if requester_id else 'no informado'
                    
                    # Extrair ID da prioridade e converter para nome
                    priority_id = ticket_data.get('3', '3')  # Default para prioridade mdia (ID 3)
                    priority_name = self._get_priority_name_by_id(str(priority_id))
                    
                    # Extrair informaes do ticket
                    ticket_info = {
                        'id': str(ticket_data.get('2', '')),  # ID do ticket
                        'title': ticket_data.get('1', 'Sem ttulo'),  # Ttulo
                        'description': ticket_data.get('21', '')[:100] + '...' if len(ticket_data.get('21', '')) > 100 else ticket_data.get('21', ''),  # Descrio truncada
                        'date': ticket_data.get('15', ''),  # Data de abertura
                        'requester': requester_name,  # Nome do solicitante
                        'priority': priority_name,  # Nome da prioridade convertido
                        'status': 'Novo'
                    }
                    tickets.append(ticket_info)
            
            self.logger.info(f"Encontrados {len(tickets)} tickets novos")
            return tickets
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar tickets novos: {e}")
            return []
    
    def get_system_status(self) -> Dict[str, any]:
        """Retorna status do sistema GLPI"""
        try:
            # Tenta autenticao para verificar conectividade completa
            start_time = time.time()
            
            if self._ensure_authenticated():
                response_time = time.time() - start_time
                return {
                    "status": "online",
                    "message": "GLPI conectado e autenticado",
                    "response_time": response_time,
                    "token_valid": not self._is_token_expired()
                }
            else:
                response_time = time.time() - start_time
                return {
                    "status": "warning",
                    "message": "GLPI acessvel mas falha na autenticao",
                    "response_time": response_time,
                    "token_valid": False
                }
                
        except Exception as e:
            return {
                "status": "offline",
                "message": f"Erro de conexo: {str(e)}",
                "response_time": None,
                "token_valid": False
            }
    
    def get_dashboard_metrics_with_filters(self, start_date: str = None, end_date: str = None, 
                                         status: str = None, priority: str = None, 
                                         level: str = None, technician: str = None, 
                                         category: str = None) -> Dict[str, any]:
        """Obtm mtricas do dashboard com filtros avanados usando o sistema unificado"""
        start_time = time.time()
        
        try:
            if not self._ensure_authenticated():
                return ResponseFormatter.format_error_response("Falha na autenticao com GLPI", ["Erro de autenticao"])
                
            if not self.discover_field_ids():
                return ResponseFormatter.format_error_response("Falha ao descobrir IDs dos campos", ["Erro ao obter configurao"])
            
            # Combinar mtricas por nvel e gerais com filtros
            level_metrics = self._get_metrics_by_level_internal(start_date, end_date)
            general_metrics = self._get_general_metrics_internal(start_date, end_date)
            
            # Aplicar filtros adicionais se especificados
            if status or priority or level or technician or category:
                level_metrics = self._apply_additional_filters(
                    level_metrics, status, priority, level, technician, category
                )
            
            # Usar o formatador unificado
            execution_time = time.time() - start_time
            raw_data = {
                'by_level': level_metrics,
                'general': general_metrics
            }
            filters_data = {
                "start_date": start_date,
                "end_date": end_date,
                "status": status,
                "priority": priority,
                "level": level,
                "technician": technician,
                "category": category
            }
            result = ResponseFormatter.format_dashboard_response(
                raw_data,
                filters=filters_data,
                start_time=start_time
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao obter mtricas com filtros: {e}")
            return ResponseFormatter.format_error_response(f"Erro interno: {str(e)}", [str(e)])
    
    def get_technician_ranking_with_filters(self, start_date: str = None, end_date: str = None,
                                           level: str = None, limit: int = 10) -> List[Dict[str, any]]:
        """Obtm ranking de t�cnicos com filtros avanados"""
        if not self._ensure_authenticated():
            return []
            
        try:
            # Obter lista de t�cnicos ativos
            technicians = self.get_active_technicians()
            if not technicians:
                return []
            
            # Filtrar por nvel se especificado
            if level and level in self.service_levels:
                group_id = self.service_levels[level]
                technicians = [t for t in technicians if t.get('group_id') == group_id]
            
            ranking = []
            
            for tech in technicians:
                tech_id = tech['id']
                tech_name = tech['name']
                
                # Contar tickets com filtros de data
                ticket_count = self._count_tickets_with_date_filter(
                    tech_id, start_date, end_date
                )
                
                if ticket_count is not None:
                    ranking.append({
                        'id': tech_id,
                        'name': tech_name,
                        'ticket_count': ticket_count,
                        'level': level if level else 'Todos'
                    })
            
            # Ordenar por contagem de tickets (decrescente)
            ranking.sort(key=lambda x: x['ticket_count'], reverse=True)
            
            return ranking[:limit]
            
        except Exception as e:
            self.logger.error(f"Erro ao obter ranking com filtros: {e}")
            return []
    
    def get_new_tickets_with_filters(self, limit: int = 10, priority: str = None,
                                   category: str = None, technician: str = None,
                                   start_date: str = None, end_date: str = None) -> List[Dict[str, any]]:
        """Obtm tickets novos com filtros avanados"""
        if not self._ensure_authenticated():
            return []
            
        if not self.discover_field_ids():
            return []
        
        try:
            # Construir critrios de busca
            criteria = []
            criteria_index = 0
            
            # Status = Novo (sempre aplicado)
            criteria.append({
                f"criteria[{criteria_index}][field]": self.field_ids["STATUS"],
                f"criteria[{criteria_index}][searchtype]": "equals",
                f"criteria[{criteria_index}][value]": self.status_map.get('Novo', 1)
            })
            criteria_index += 1
            
            # Filtro de prioridade
            if priority:
                priority_id = self._get_priority_id_by_name(priority)
                if priority_id:
                    criteria.append({
                        f"criteria[{criteria_index}][link]": "AND",
                        f"criteria[{criteria_index}][field]": "3",  # Campo prioridade
                        f"criteria[{criteria_index}][searchtype]": "equals",
                        f"criteria[{criteria_index}][value]": priority_id
                    })
                    criteria_index += 1
            
            # Filtro de t�cnico
            if technician:
                criteria.append({
                    f"criteria[{criteria_index}][link]": "AND",
                    f"criteria[{criteria_index}][field]": "5",  # Campo t�cnico
                    f"criteria[{criteria_index}][searchtype]": "equals",
                    f"criteria[{criteria_index}][value]": technician
                })
                criteria_index += 1
            
            # Filtros de data
            if start_date:
                criteria.append({
                    f"criteria[{criteria_index}][link]": "AND",
                    f"criteria[{criteria_index}][field]": "15",  # Data de criao
                    f"criteria[{criteria_index}][searchtype]": "morethan",
                    f"criteria[{criteria_index}][value]": start_date
                })
                criteria_index += 1
                
            if end_date:
                criteria.append({
                    f"criteria[{criteria_index}][link]": "AND",
                    f"criteria[{criteria_index}][field]": "15",  # Data de criao
                    f"criteria[{criteria_index}][searchtype]": "lessthan",
                    f"criteria[{criteria_index}][value]": end_date
                })
                criteria_index += 1
            
            # Construir parmetros de busca
            search_params = {
                "is_deleted": 0,
                "range": f"0-{limit-1}",
                "sort": "19",  # Ordenar por data de criao
                "order": "DESC"
            }
            
            # Adicionar critrios aos parmetros
            for criterion in criteria:
                search_params.update(criterion)
            
            response = self._make_authenticated_request(
                'GET',
                f"{self.glpi_url}/search/Ticket",
                params=search_params
            )
            
            if not response or not response.ok:
                self.logger.error("Falha ao buscar tickets novos com filtros")
                return []
            
            data = response.json()
            tickets = []
            
            if 'data' in data and data['data']:
                for ticket_data in data['data']:
                    # Processar dados do ticket
                    requester_id = ticket_data.get('4', '')
                    requester_name = self._get_user_name_by_id(str(requester_id)) if requester_id else 'no informado'
                    
                    priority_id = ticket_data.get('3', '3')
                    priority_name = self._get_priority_name_by_id(str(priority_id))
                    
                    ticket_info = {
                        'id': str(ticket_data.get('2', '')),
                        'title': ticket_data.get('1', 'Sem ttulo'),
                        'description': ticket_data.get('21', '')[:100] + '...' if len(ticket_data.get('21', '')) > 100 else ticket_data.get('21', ''),
                        'date': ticket_data.get('15', ''),
                        'requester': requester_name,
                        'priority': priority_name,
                        'status': 'Novo',
                        'filters_applied': {
                            'priority': priority,
                            'category': category,
                            'technician': technician,
                            'start_date': start_date,
                            'end_date': end_date
                        }
                    }
                    tickets.append(ticket_info)
            
            self.logger.info(f"Encontrados {len(tickets)} tickets novos com filtros")
            return tickets
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar tickets novos com filtros: {e}")
            return []
    
    def _apply_additional_filters(self, metrics: Dict, status: str = None, priority: str = None,
                                level: str = None, technician: str = None, category: str = None) -> Dict:
        """Aplica filtros adicionais s mtricas"""
        # Por enquanto, retorna as mtricas sem modificao
        # Implementao completa requereria consultas adicionais  API
        return metrics
    
    def _count_tickets_with_date_filter(self, tech_id: int, start_date: str = None, end_date: str = None) -> Optional[int]:
        """Conta tickets de um t�cnico com filtro de data"""
        try:
            criteria = []
            criteria_index = 0
            
            # Filtro por t�cnico
            criteria.append({
                f"criteria[{criteria_index}][field]": "5",  # Campo t�cnico
                f"criteria[{criteria_index}][searchtype]": "equals",
                f"criteria[{criteria_index}][value]": tech_id
            })
            criteria_index += 1
            
            # Filtros de data
            if start_date:
                criteria.append({
                    f"criteria[{criteria_index}][link]": "AND",
                    f"criteria[{criteria_index}][field]": "15",  # Data de criao
                    f"criteria[{criteria_index}][searchtype]": "morethan",
                    f"criteria[{criteria_index}][value]": start_date
                })
                criteria_index += 1
                
            if end_date:
                criteria.append({
                    f"criteria[{criteria_index}][link]": "AND",
                    f"criteria[{criteria_index}][field]": "15",  # Data de criao
                    f"criteria[{criteria_index}][searchtype]": "lessthan",
                    f"criteria[{criteria_index}][value]": end_date
                })
            
            # Construir parmetros
            search_params = {
                "is_deleted": 0,
                "range": "0-0"  # Apenas contagem
            }
            
            # Adicionar critrios
            for criterion in criteria:
                search_params.update(criterion)
            
            response = self._make_authenticated_request(
                'GET',
                f"{self.glpi_url}/search/Ticket",
                params=search_params
            )
            
            if not response:
                return None
            
            if "Content-Range" in response.headers:
                total = int(response.headers["Content-Range"].split("/")[-1])
                return total
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Erro ao contar tickets com filtro de data: {e}")
            return None
    
    def _get_priority_id_by_name(self, priority_name: str) -> Optional[str]:
        """Converte nome de prioridade para ID do GLPI"""
        priority_reverse_map = {
            'Muito Baixa': '1',
            'Baixa': '2',
            'Mdia': '3',
            'Alta': '4',
            'Muito Alta': '5',
            'Crtica': '6'
        }
        return priority_reverse_map.get(priority_name)






    def discover_group_ids(self) -> bool:
        """Descobre dinamicamente os IDs dos grupos N1-N4 no GLPI"""
        try:
            if not self._ensure_authenticated():
                self.logger.error("Falha na autentica??o para descobrir IDs dos grupos")
                return False
            
            response = self._make_authenticated_request(
                'GET',
                f'{self.glpi_url}/search/Group',
                params={
                    'range': '0-999',
                    'criteria[0][field]': '17',
                    'criteria[0][searchtype]': 'equals',
                    'criteria[0][value]': '1',
                    'forcedisplay[0]': '2',
                    'forcedisplay[1]': '1',
                }
            )
            
            if not response or not response.ok:
                self.logger.error("Falha ao buscar grupos no GLPI")
                return False
            
            data = response.json()
            groups = data.get('data', [])
            
            # Mapear grupos N1-N4
            group_mapping = {}
            for group in groups:
                if isinstance(group, dict):
                    name = group.get('1', '')
                    group_id = group.get('2', '')
                    
                    for target in ['N1', 'N2', 'N3', 'N4']:
                        if target in name.upper():
                            group_mapping[target] = int(group_id)
                            self.logger.info(f"Grupo {target} encontrado: {name} (ID: {group_id})")
                            break
            
            # Atualizar service_levels com os IDs encontrados
            if len(group_mapping) == 4:  # Todos os grupos encontrados
                self.service_levels = {
                    'N1': group_mapping['N1'],
                    'N2': group_mapping['N2'], 
                    'N3': group_mapping['N3'],
                    'N4': group_mapping['N4']
                }
        
                self.logger.info(f"IDs dos grupos atualizados: {self.service_levels}")
                return True
            else:
                missing = set(['N1', 'N2', 'N3', 'N4']) - set(group_mapping.keys())
                self.logger.warning(f"Grupos n?o encontrados: {missing}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao descobrir IDs dos grupos: {e}")
            return False









