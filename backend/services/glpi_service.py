# -*- coding: utf-8 -*-
import logging
from typing import Dict, Optional, Tuple, List
import requests
import time
from datetime import datetime, timedelta
from backend.config.settings import active_config
from backend.utils.response_formatter import ResponseFormatter
from backend.utils.structured_logger import create_glpi_logger, log_api_call


class GLPIService:
    """Serviço para integração com a API do GLPI com autenticação robusta"""
    
    def __init__(self):
        try:
            # Validar configurações obrigatórias
            config_obj = active_config()
            if not hasattr(config_obj, 'GLPI_URL') or not config_obj.GLPI_URL:
                raise ValueError("GLPI_URL não está configurado")
            if not hasattr(config_obj, 'GLPI_APP_TOKEN') or not config_obj.GLPI_APP_TOKEN:
                raise ValueError("GLPI_APP_TOKEN não está configurado")
            if not hasattr(config_obj, 'GLPI_USER_TOKEN') or not config_obj.GLPI_USER_TOKEN:
                raise ValueError("GLPI_USER_TOKEN não está configurado")
            
            self.glpi_url = config_obj.GLPI_URL.rstrip('/')  # Remove trailing slash
            self.app_token = config_obj.GLPI_APP_TOKEN
            self.user_token = config_obj.GLPI_USER_TOKEN
            
            # Validar formato da URL
            if not self.glpi_url.startswith(('http://', 'https://')):
                raise ValueError(f"GLPI_URL deve começar com http:// ou https://, recebido: {self.glpi_url}")
            
            # Inicializar loggers com tratamento de erro
            try:
                self.structured_logger = create_glpi_logger(getattr(config_obj, 'LOG_LEVEL', 'INFO'))
            except Exception as e:
                # Fallback para logger padrão se structured_logger falhar
                self.structured_logger = None
                logging.warning(f"Falha ao criar structured_logger: {e}")
            
            self.logger = logging.getLogger("glpi_service")
            self.logger.info("GLPIService inicializado com sucesso")
            
        except Exception as e:
            error_msg = f"Erro na inicialização do GLPIService: {e}"
            logging.error(error_msg)
            raise RuntimeError(error_msg) from e
        
        # Mapeamento de status dos tickets
        self.status_map = {
            "Novo": 1,
            "Processando (atribuído)": 2,
            "Processando (planejado)": 3,
            "Pendente": 4,
            "Solucionado": 5,
            "Fechado": 6,
        }
        
        # Níveis de atendimento (grupos técnicos específicos)
        # Cada nível tem seu próprio grupo no GLPI
        self.service_levels = {
            "N1": 89,  # CC-SE-SUBADM-DTIC > N1
            "N2": 90,  # CC-SE-SUBADM-DTIC > N2
            "N3": 91,  # CC-SE-SUBADM-DTIC > N3
            "N4": 92,  # CC-SE-SUBADM-DTIC > N4
        }
        
        self.field_ids = {}
        self.session_token = None
        self.token_created_at = None
        self.token_expires_at = None
        self.max_retries = 3
        self.retry_delay_base = 2  # Base para backoff exponencial
        self.session_timeout = 3600  # 1 hora em segundos
        
        # Sistema de cache para evitar consultas repetitivas
        self._cache = {
            'technician_ranking': {'data': None, 'timestamp': None, 'ttl': 300},  # 5 minutos
            'active_technicians': {'data': None, 'timestamp': None, 'ttl': 600},  # 10 minutos
            'field_ids': {'data': None, 'timestamp': None, 'ttl': 1800},  # 30 minutos
            'dashboard_metrics': {'data': None, 'timestamp': None, 'ttl': 180},  # 3 minutos
            'dashboard_metrics_filtered': {},  # Cache dinâmico para filtros de data
            'priority_names': {}  # Cache para nomes de prioridade
        }
    
    def _is_cache_valid(self, cache_key: str, sub_key: str = None) -> bool:
        """Verifica se o cache é válido com validações robustas"""
        try:
            # Validar parâmetros de entrada
            if not isinstance(cache_key, str) or not cache_key.strip():
                self.logger.warning("cache_key deve ser uma string não vazia")
                return False
            
            if sub_key is not None and (not isinstance(sub_key, str) or not sub_key.strip()):
                self.logger.warning("sub_key deve ser uma string não vazia ou None")
                return False
            
            # Verificar se o cache existe
            if not hasattr(self, '_cache') or not isinstance(self._cache, dict):
                self.logger.warning("Cache não inicializado corretamente")
                return False
            
            if sub_key:
                cache_data = self._cache.get(cache_key, {}).get(sub_key)
            else:
                cache_data = self._cache.get(cache_key)
            
            if not cache_data or not isinstance(cache_data, dict):
                return False
            
            timestamp = cache_data.get('timestamp')
            if timestamp is None or not isinstance(timestamp, (int, float)):
                self.logger.warning(f"Timestamp inválido no cache para {cache_key}")
                return False
            
            current_time = time.time()
            ttl = cache_data.get('ttl', 300)  # Default 5 minutos
            
            if not isinstance(ttl, (int, float)) or ttl <= 0:
                self.logger.warning(f"TTL inválido no cache para {cache_key}: {ttl}")
                return False
            
            is_valid = (current_time - timestamp) < ttl
            if not is_valid:
                self.logger.debug(f"Cache expirado para {cache_key}: idade={current_time - timestamp:.1f}s, TTL={ttl}s")
            
            return is_valid
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar cache para {cache_key}: {e}")
            return False
    
    def _get_cache_data(self, cache_key: str, sub_key: str = None):
        """Obtém dados do cache com validações robustas"""
        try:
            # Validar parâmetros de entrada
            if not isinstance(cache_key, str) or not cache_key.strip():
                self.logger.warning("cache_key deve ser uma string não vazia")
                return None
            
            if sub_key is not None and (not isinstance(sub_key, str) or not sub_key.strip()):
                self.logger.warning("sub_key deve ser uma string não vazia ou None")
                return None
            
            # Verificar se o cache existe
            if not hasattr(self, '_cache') or not isinstance(self._cache, dict):
                self.logger.warning("Cache não inicializado corretamente")
                return None
            
            if sub_key:
                cache_entry = self._cache.get(cache_key, {}).get(sub_key, {})
            else:
                cache_entry = self._cache.get(cache_key, {})
            
            if not isinstance(cache_entry, dict):
                self.logger.warning(f"Entrada de cache inválida para {cache_key}")
                return None
            
            return cache_entry.get('data')
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dados do cache para {cache_key}: {e}")
            return None
    
    def _set_cache_data(self, cache_key: str, data, ttl: int = 300, sub_key: str = None):
        """Define dados no cache com validações robustas"""
        try:
            # Validar parâmetros de entrada
            if not isinstance(cache_key, str) or not cache_key.strip():
                self.logger.warning("cache_key deve ser uma string não vazia")
                return
            
            if sub_key is not None and (not isinstance(sub_key, str) or not sub_key.strip()):
                self.logger.warning("sub_key deve ser uma string não vazia ou None")
                return
            
            if not isinstance(ttl, (int, float)) or ttl <= 0:
                self.logger.warning(f"TTL deve ser um número positivo, recebido: {ttl}")
                ttl = 300  # Fallback para 5 minutos
            
            # Verificar se o cache existe
            if not hasattr(self, '_cache'):
                self._cache = {}
            elif not isinstance(self._cache, dict):
                self.logger.warning("Cache corrompido, reinicializando")
                self._cache = {}
            
            cache_entry = {
                'data': data,
                'timestamp': time.time(),
                'ttl': ttl
            }
            
            if sub_key:
                if cache_key not in self._cache:
                    self._cache[cache_key] = {}
                elif not isinstance(self._cache[cache_key], dict):
                    self.logger.warning(f"Entrada de cache corrompida para {cache_key}, reinicializando")
                    self._cache[cache_key] = {}
                
                self._cache[cache_key][sub_key] = cache_entry
                self.logger.debug(f"Cache definido para {cache_key}[{sub_key}] com TTL {ttl}s")
            else:
                self._cache[cache_key] = cache_entry
                self.logger.debug(f"Cache definido para {cache_key} com TTL {ttl}s")
                
        except Exception as e:
            self.logger.error(f"Erro ao definir dados do cache para {cache_key}: {e}")
    
    def _is_token_expired(self) -> bool:
        """Verifica se o token de sessão está expirado com validações robustas"""
        try:
            # Verificar se o timestamp de criação existe e é válido
            if not self.token_created_at or not isinstance(self.token_created_at, (int, float)):
                self.logger.debug("Timestamp de criação do token não existe ou é inválido")
                return True
            
            # Verificar se o session_timeout é válido
            if not hasattr(self, 'session_timeout') or not isinstance(self.session_timeout, (int, float)) or self.session_timeout <= 0:
                self.logger.warning("session_timeout inválido, usando padrão de 3600s")
                self.session_timeout = 3600
            
            current_time = time.time()
            
            # Verificar se o timestamp não é futuro (proteção contra clock skew)
            if self.token_created_at > current_time:
                self.logger.warning("Timestamp do token está no futuro, considerando expirado")
                return True
            
            token_age = current_time - self.token_created_at
            is_expired = token_age >= self.session_timeout
            
            if is_expired:
                self.logger.debug(f"Token expirado (idade: {token_age:.0f}s, timeout: {self.session_timeout}s)")
            else:
                self.logger.debug(f"Token válido (idade: {token_age:.0f}s, timeout: {self.session_timeout}s)")
            
            return is_expired
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar expiração do token: {e}")
            return True  # Em caso de erro, considerar expirado por segurança
    
    def _ensure_authenticated(self) -> bool:
        """Garante que temos um token válido, re-autenticando se necessário com validações robustas"""
        try:
            # Verificar se o token existe e é válido
            if not self.session_token or not isinstance(self.session_token, str) or not self.session_token.strip():
                self.logger.info("Token de sessão não existe ou é inválido, autenticando...")
                return self._authenticate_with_retry()
            
            # Verificar se o token está expirado
            if self._is_token_expired():
                self.logger.info("Token expirado, re-autenticando...")
                return self._authenticate_with_retry()
            
            self.logger.debug("Token válido, não é necessário re-autenticar")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao garantir autenticação: {e}")
            # Limpar token inválido
            self.session_token = None
            self.token_created_at = None
            self.token_expires_at = None
            return False
    
    def _authenticate_with_retry(self) -> bool:
        """Autentica com retry automático e backoff exponencial com validações robustas"""
        try:
            # Validar configurações de retry
            if not hasattr(self, 'max_retries') or not isinstance(self.max_retries, int) or self.max_retries <= 0:
                self.logger.warning("max_retries inválido, usando padrão de 3")
                self.max_retries = 3
            
            if not hasattr(self, 'retry_delay_base') or not isinstance(self.retry_delay_base, (int, float)) or self.retry_delay_base <= 0:
                self.logger.warning("retry_delay_base inválido, usando padrão de 2")
                self.retry_delay_base = 2
            
            for attempt in range(self.max_retries):
                try:
                    self.logger.info(f"Tentativa de autenticação {attempt + 1}/{self.max_retries}")
                    
                    if self._perform_authentication():
                        self.logger.info(f"Autenticação bem-sucedida na tentativa {attempt + 1}")
                        return True
                    
                    if attempt < self.max_retries - 1:
                        delay = min(self.retry_delay_base ** attempt, 30)  # Máximo de 30 segundos
                        self.logger.warning(f"Tentativa {attempt + 1} falhou, aguardando {delay}s antes da próxima tentativa...")
                        time.sleep(delay)
                        
                except requests.exceptions.Timeout as e:
                    self.logger.error(f"Timeout na tentativa {attempt + 1}: {e}")
                    if attempt < self.max_retries - 1:
                        delay = min(self.retry_delay_base ** attempt, 30)
                        time.sleep(delay)
                        
                except requests.exceptions.ConnectionError as e:
                    self.logger.error(f"Erro de conexão na tentativa {attempt + 1}: {e}")
                    if attempt < self.max_retries - 1:
                        delay = min(self.retry_delay_base ** attempt, 30)
                        time.sleep(delay)
                        
                except Exception as e:
                    self.logger.error(f"Erro na tentativa {attempt + 1} de autenticação: {e}")
                    if attempt < self.max_retries - 1:
                        delay = min(self.retry_delay_base ** attempt, 30)
                        time.sleep(delay)
            
            self.logger.error(f"Falha na autenticação após {self.max_retries} tentativas")
            return False
            
        except Exception as e:
            self.logger.error(f"Erro crítico no processo de autenticação com retry: {e}")
            return False
    
    def _perform_authentication(self) -> bool:
        """Executa o processo de autenticação com validações robustas"""
        try:
            # Validar tokens de autenticação
            if not self.app_token or not isinstance(self.app_token, str) or not self.app_token.strip():
                self.logger.error("GLPI_APP_TOKEN não está configurado ou é inválido")
                return False
                
            if not self.user_token or not isinstance(self.user_token, str) or not self.user_token.strip():
                self.logger.error("GLPI_USER_TOKEN não está configurado ou é inválido")
                return False
            
            # Validar URL do GLPI
            if not self.glpi_url or not isinstance(self.glpi_url, str) or not self.glpi_url.strip():
                self.logger.error("GLPI_URL não está configurado ou é inválido")
                return False
            
            # Validar session_timeout
            if not hasattr(self, 'session_timeout') or not isinstance(self.session_timeout, (int, float)) or self.session_timeout <= 0:
                self.logger.warning("session_timeout inválido, usando padrão de 3600s")
                self.session_timeout = 3600
            
            session_headers = {
                "Content-Type": "application/json",
                "App-Token": self.app_token,
                "Authorization": f"user_token {self.user_token}",
            }
            
            auth_url = f"{self.glpi_url.rstrip('/')}/initSession"
            self.logger.info(f"Autenticando na API do GLPI: {auth_url}")
            
            response = requests.get(
                auth_url,
                headers=session_headers,
                timeout=15  # Timeout mais generoso para autenticação
            )
            
            # Verificar status code
            if response.status_code != 200:
                self.logger.error(f"Falha na autenticação - Status: {response.status_code}, Resposta: {response.text}")
                return False
            
            # Validar resposta JSON
            try:
                response_data = response.json()
            except ValueError as e:
                self.logger.error(f"Resposta de autenticação não é JSON válido: {e}")
                return False
            
            # Validar presença do session_token
            if not response_data or "session_token" not in response_data:
                self.logger.error(f"session_token não encontrado na resposta: {response_data}")
                return False
            
            session_token = response_data["session_token"]
            if not session_token or not isinstance(session_token, str) or not session_token.strip():
                self.logger.error(f"session_token inválido: {session_token}")
                return False
            
            # Definir dados da sessão
            self.session_token = session_token
            self.token_created_at = time.time()
            self.token_expires_at = self.token_created_at + self.session_timeout
            
            self.logger.info(f"Autenticação bem-sucedida! Token expira em {self.session_timeout}s")
            return True
            
        except requests.exceptions.Timeout as e:
            self.logger.error(f"Timeout na autenticação: {e}")
            return False
            
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Erro de conexão na autenticação: {e}")
            return False
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro de requisição na autenticação: {e}")
            return False
            
        except Exception as e:
            self.logger.error(f"Erro inesperado na autenticação: {e}")
            return False
    
    def authenticate(self) -> bool:
        """Método público para autenticação (mantido para compatibilidade)"""
        return self._authenticate_with_retry()
    
    def get_api_headers(self) -> Optional[Dict[str, str]]:
        """Retorna os headers necessários para as requisições da API com validações robustas"""
        try:
            # Garantir autenticação
            if not self._ensure_authenticated():
                self.logger.error("Não foi possível obter headers - falha na autenticação")
                return None
            
            # Validar tokens necessários
            if not self.app_token or not isinstance(self.app_token, str) or not self.app_token.strip():
                self.logger.error("app_token não está disponível ou é inválido")
                return None
                
            if not self.session_token or not isinstance(self.session_token, str) or not self.session_token.strip():
                self.logger.error("session_token não está disponível ou é inválido")
                return None
            
            headers = {
                "Session-Token": self.session_token,
                "App-Token": self.app_token
            }
            
            self.logger.debug("Headers da API gerados com sucesso")
            return headers
            
        except Exception as e:
            self.logger.error(f"Erro ao obter headers da API: {e}")
            return None
    
    def _make_authenticated_request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """Faz uma requisição autenticada com retry automático e validações robustas"""
        try:
            # Validar parâmetros de entrada
            if not method or not isinstance(method, str) or method.strip().upper() not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                self.logger.error(f"Método HTTP inválido: {method}")
                return None
            
            if not url or not isinstance(url, str) or not url.strip():
                self.logger.error("URL não pode ser vazia")
                return None
            
            method = method.strip().upper()
            url = url.strip()
            
            # Validar configurações de retry
            if not hasattr(self, 'max_retries') or not isinstance(self.max_retries, int) or self.max_retries <= 0:
                self.logger.warning("max_retries inválido, usando padrão de 3")
                self.max_retries = 3
            
            if not hasattr(self, 'retry_delay_base') or not isinstance(self.retry_delay_base, (int, float)) or self.retry_delay_base <= 0:
                self.logger.warning("retry_delay_base inválido, usando padrão de 2")
                self.retry_delay_base = 2
            
            # Usar timeout configurado se não fornecido
            if 'timeout' not in kwargs:
                try:
                    config_obj = active_config()
                    kwargs['timeout'] = config_obj.API_TIMEOUT
                except (AttributeError, NameError):
                    kwargs['timeout'] = 30  # Fallback
                    self.logger.warning("API_TIMEOUT não configurado, usando 30s")
            
            # Validar timeout
            if not isinstance(kwargs['timeout'], (int, float)) or kwargs['timeout'] <= 0:
                kwargs['timeout'] = 30
                self.logger.warning("Timeout inválido, usando 30s")
                
            for attempt in range(self.max_retries):
                try:
                    headers = self.get_api_headers()
                    if not headers:
                        self.logger.error(f"Falha ao obter headers de autenticação (tentativa {attempt + 1})")
                        if attempt < self.max_retries - 1:
                            delay = min(self.retry_delay_base ** attempt, 30)
                            time.sleep(delay)
                            continue
                        return None
                    
                    # Adicionar headers customizados se fornecidos
                    if 'headers' in kwargs and isinstance(kwargs['headers'], dict):
                        headers.update(kwargs['headers'])
                    kwargs['headers'] = headers
                    
                    self.logger.debug(f"Fazendo requisição {method} para {url} (tentativa {attempt + 1})")
                    start_time = time.time()
                    response = requests.request(method, url, **kwargs)
                    response_time = time.time() - start_time
                    
                    # Log de performance para requisições lentas
                    if response_time > 5.0:
                        self.logger.warning(f"Requisição lenta detectada: {response_time:.2f}s para {method} {url}")
                    else:
                        self.logger.debug(f"Requisição completada em {response_time:.2f}s")
                    
                    # Se recebemos 401 ou 403, token pode estar expirado
                    if response.status_code in [401, 403]:
                        self.logger.warning(f"Recebido status {response.status_code}, token pode estar expirado")
                        # Limpar token para forçar re-autenticação
                        self.session_token = None
                        self.token_created_at = None
                        self.token_expires_at = None
                        
                        if attempt < self.max_retries - 1:
                            self.logger.info("Tentando re-autenticar...")
                            delay = min(self.retry_delay_base ** attempt, 10)
                            time.sleep(delay)
                            continue
                    
                    # Log de status codes problemáticos
                    if response.status_code >= 500:
                        self.logger.error(f"Erro do servidor GLPI: {response.status_code} - {response.text[:200]}")
                    elif response.status_code >= 400:
                        self.logger.warning(f"Erro na requisição: {response.status_code} - {response.text[:200]}")
                    elif response.status_code >= 200 and response.status_code < 300:
                        self.logger.debug(f"Requisição bem-sucedida: {response.status_code}")
                    
                    return response
                    
                except requests.exceptions.Timeout as e:
                    self.logger.warning(f"Timeout na requisição (tentativa {attempt + 1}): {e}")
                    if attempt < self.max_retries - 1:
                        delay = min(self.retry_delay_base ** attempt, 30)
                        time.sleep(delay)
                        continue
                    
                except requests.exceptions.ConnectionError as e:
                    self.logger.error(f"Erro de conexão (tentativa {attempt + 1}): {e}")
                    if attempt < self.max_retries - 1:
                        delay = min(self.retry_delay_base ** attempt, 30)
                        time.sleep(delay)
                        continue
                    
                except requests.exceptions.RequestException as e:
                    self.logger.error(f"Erro na requisição (tentativa {attempt + 1}): {e}")
                    if attempt < self.max_retries - 1:
                        delay = min(self.retry_delay_base ** attempt, 30)
                        time.sleep(delay)
                        continue
                    
                except Exception as e:
                    self.logger.error(f"Erro inesperado na requisição (tentativa {attempt + 1}): {e}")
                    if attempt < self.max_retries - 1:
                        delay = min(self.retry_delay_base ** attempt, 30)
                        time.sleep(delay)
                        continue
            
            self.logger.error(f"Todas as {self.max_retries} tentativas falharam para {method} {url}")
            return None
            
        except Exception as e:
            self.logger.error(f"Erro crítico no método _make_authenticated_request: {e}")
            return None
    
    def discover_field_ids(self) -> bool:
        """Descobre dinamicamente os IDs dos campos do GLPI com validações robustas"""
        try:
            # Validar estado da instância
            if not hasattr(self, 'field_ids') or not isinstance(self.field_ids, dict):
                self.field_ids = {}
                self.logger.warning("field_ids não inicializado, criando novo dicionário")
            
            if not hasattr(self, 'glpi_url') or not self.glpi_url:
                self.logger.error("glpi_url não configurado")
                self._apply_fallback_field_ids()
                return False
            
            # Verificar autenticação
            if not self._ensure_authenticated():
                self.logger.error("Falha na autenticação para descobrir field IDs")
                self._apply_fallback_field_ids()
                return False
                
            try:
                self.logger.debug("Iniciando descoberta de IDs de campos")
                response = self._make_authenticated_request(
                    'GET', 
                    f"{self.glpi_url}/listSearchOptions/Ticket"
                )
                
                if not response:
                    self.logger.error("Resposta nula ao descobrir field IDs")
                    self._apply_fallback_field_ids()
                    return True  # Retorna True porque fallbacks foram aplicados
                
                if not response.ok:
                    self.logger.error(f"Falha ao descobrir field IDs: HTTP {response.status_code}")
                    self._apply_fallback_field_ids()
                    return True
                
                # Validar resposta JSON
                try:
                    search_options = response.json()
                except ValueError as e:
                    self.logger.error(f"Resposta JSON inválida ao descobrir field IDs: {e}")
                    self._apply_fallback_field_ids()
                    return True
                
                if not isinstance(search_options, dict):
                    self.logger.error("Formato de resposta inválido para search options")
                    self._apply_fallback_field_ids()
                    return True
                
                # Mapear nomes de campos para IDs com maior precisão
                tech_group_field_names = [
                    "Grupo técnico", "Technical group", "Grupo tecnico", 
                    "Assigned group", "Group", "Grupo", "Grupo atribuído",
                    "Grupo responsável", "Responsible group"
                ]
                
                status_field_names = [
                    "Status", "Estado", "State", "Situação", "Condition"
                ]
                
                # Descobrir campo TECH com mais opções
                tech_field_names = [
                    "Técnico", "Technician", "Tecnico", "Assigned technician",
                    "Técnico encarregado", "Assigned to", "Atribuído para",
                    "Técnico responsável", "Responsável", "Assignee", "Atribuído",
                    "Assigned user", "Usuario atribuído"
                ]
                
                fields_found = {"GROUP": False, "STATUS": False, "TECH": False}
                
                for field_id, field_info in search_options.items():
                    try:
                        if not isinstance(field_info, dict) or 'name' not in field_info:
                            continue
                        
                        field_name = str(field_info['name']).strip()
                        if not field_name:
                            continue
                        
                        # Buscar campo de grupo técnico
                        if not fields_found["GROUP"] and any(name.lower() in field_name.lower() for name in tech_group_field_names):
                            self.field_ids["GROUP"] = str(field_id)
                            fields_found["GROUP"] = True
                            self.logger.info(f"Campo GROUP encontrado: ID {field_id} - {field_name}")
                        
                        # Buscar campo de status
                        elif not fields_found["STATUS"] and any(name.lower() in field_name.lower() for name in status_field_names):
                            self.field_ids["STATUS"] = str(field_id)
                            fields_found["STATUS"] = True
                            self.logger.info(f"Campo STATUS encontrado: ID {field_id} - {field_name}")
                        
                        # Buscar campo de técnico
                        elif not fields_found["TECH"] and any(name.lower() in field_name.lower() for name in tech_field_names):
                            self.field_ids["TECH"] = str(field_id)
                            fields_found["TECH"] = True
                            self.logger.info(f"Campo TECH encontrado: ID {field_id} - {field_name}")
                        
                        # Parar se todos os campos foram encontrados
                        if all(fields_found.values()):
                            break
                            
                    except Exception as e:
                        self.logger.warning(f"Erro ao processar campo {field_id}: {e}")
                        continue
                
                # Forçar ID 15 para data de criação (padrão GLPI)
                self.field_ids["DATE_CREATION"] = "15"
                self.logger.info("Campo DATE_CREATION definido como ID 15 (padrão GLPI)")
                
                # Aplicar fallbacks para campos não encontrados
                self._apply_fallback_field_ids()
                
                # Verificar se todos os campos essenciais estão presentes
                required_fields = ["GROUP", "STATUS", "DATE_CREATION", "TECH"]
                missing_fields = [field for field in required_fields if field not in self.field_ids or not self.field_ids[field]]
                
                if missing_fields:
                    self.logger.error(f"Campos críticos ainda ausentes: {missing_fields}")
                    return False
                
                self.logger.info(f"IDs de campos descobertos com sucesso: {self.field_ids}")
                return True
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Erro de requisição ao descobrir IDs dos campos: {e}")
                self._apply_fallback_field_ids()
                return True
                
            except Exception as e:
                self.logger.error(f"Erro inesperado ao descobrir IDs dos campos: {e}")
                self._apply_fallback_field_ids()
                return True
                
        except Exception as e:
            self.logger.error(f"Erro crítico no método discover_field_ids: {e}")
            # Tentar aplicar fallbacks mesmo em caso de erro crítico
            try:
                self._apply_fallback_field_ids()
            except Exception as fallback_error:
                self.logger.error(f"Erro ao aplicar fallbacks: {fallback_error}")
                return False
            return True
    
    def _apply_fallback_field_ids(self):
        """Aplica IDs de fallback para campos não encontrados com validações robustas"""
        try:
            # Validar se field_ids existe e é um dicionário
            if not hasattr(self, 'field_ids'):
                self.field_ids = {}
                self.logger.warning("field_ids não existe, criando novo dicionário")
            elif not isinstance(self.field_ids, dict):
                self.logger.error(f"field_ids tem tipo inválido: {type(self.field_ids)}, recriando")
                self.field_ids = {}
            
            # Definir fallbacks padrão do GLPI
            fallbacks = {
                "GROUP": "8",      # Campo padrão para grupo técnico
                "STATUS": "12",    # Campo padrão para status
                "TECH": "5",       # Campo padrão para técnico atribuído
                "DATE_CREATION": "15"  # Campo padrão para data de criação
            }
            
            # Validar e aplicar fallbacks
            for field_name, fallback_id in fallbacks.items():
                try:
                    # Verificar se o campo não existe ou está vazio
                    if field_name not in self.field_ids or not self.field_ids[field_name] or not str(self.field_ids[field_name]).strip():
                        self.field_ids[field_name] = str(fallback_id)
                        self.logger.warning(f"Campo {field_name} não encontrado ou vazio, usando fallback ID {fallback_id}")
                    else:
                        # Validar se o ID existente é válido
                        existing_id = str(self.field_ids[field_name]).strip()
                        if not existing_id.isdigit():
                            self.logger.warning(f"ID inválido para campo {field_name}: '{existing_id}', usando fallback {fallback_id}")
                            self.field_ids[field_name] = str(fallback_id)
                        else:
                            self.logger.debug(f"Campo {field_name} já configurado com ID {existing_id}")
                            
                except Exception as e:
                    self.logger.error(f"Erro ao processar fallback para campo {field_name}: {e}")
                    # Em caso de erro, aplicar o fallback mesmo assim
                    self.field_ids[field_name] = str(fallback_id)
            
            # Verificar integridade final
            required_fields = ["GROUP", "STATUS", "TECH", "DATE_CREATION"]
            for field in required_fields:
                if field not in self.field_ids or not self.field_ids[field]:
                    self.logger.error(f"Campo crítico {field} ainda não configurado após fallbacks")
                    if field in fallbacks:
                        self.field_ids[field] = str(fallbacks[field])
                        self.logger.warning(f"Forçando fallback para campo crítico {field}: {fallbacks[field]}")
            
            self.logger.debug(f"Fallbacks aplicados. field_ids final: {self.field_ids}")
            
        except Exception as e:
            self.logger.error(f"Erro crítico ao aplicar fallbacks: {e}")
            # Em caso de erro crítico, tentar configuração mínima
            try:
                self.field_ids = {
                    "GROUP": "8",
                    "STATUS": "12", 
                    "TECH": "5",
                    "DATE_CREATION": "15"
                }
                self.logger.warning("Aplicada configuração mínima de fallbacks devido a erro crítico")
            except Exception as critical_error:
                self.logger.error(f"Falha crítica ao aplicar configuração mínima: {critical_error}")
                raise
    
    def _get_technician_name(self, tech_id: str) -> str:
        """Obtém o nome de um técnico com validações robustas e tratamento de erros"""
        try:
            # Validar parâmetros de entrada
            if not tech_id:
                self.logger.warning("tech_id vazio fornecido")
                return "Técnico Desconhecido"
            
            # Converter para string e limpar
            tech_id = str(tech_id).strip()
            if not tech_id:
                self.logger.warning("tech_id vazio após limpeza")
                return "Técnico Desconhecido"
            
            # Se não for um ID numérico, retornar o nome baseado no ID
            if not tech_id.isdigit():
                self.logger.debug(f"tech_id não numérico: {tech_id}, retornando nome baseado no ID")
                return f"Técnico {tech_id}"
            
            # Verificar configurações necessárias
            if not hasattr(self, 'glpi_url') or not self.glpi_url:
                self.logger.error("glpi_url não configurado")
                return f"Técnico {tech_id}"
            
            try:
                self.logger.debug(f"Buscando dados do técnico {tech_id}")
                user_response = self._make_authenticated_request(
                    'GET',
                    f"{self.glpi_url}/User/{tech_id}"
                )
                
                if not user_response:
                    self.logger.warning(f"Resposta nula ao buscar usuário {tech_id}")
                    return f'Técnico {tech_id}'
                
                if not user_response.ok:
                    self.logger.warning(f"Falha ao obter dados do usuário {tech_id}: HTTP {user_response.status_code}")
                    return f'Técnico {tech_id}'
                
                # Validar resposta JSON
                try:
                    user_data = user_response.json()
                except ValueError as e:
                    self.logger.error(f"Resposta JSON inválida para usuário {tech_id}: {e}")
                    return f'Técnico {tech_id}'
                
                if not user_data:
                    self.logger.warning(f"Dados vazios para usuário {tech_id}")
                    return f'Técnico {tech_id}'
                
                # Verificar se user_data é uma lista ou dicionário
                user_info = None
                if isinstance(user_data, list):
                    if user_data and isinstance(user_data[0], dict):
                        user_info = user_data[0]
                    else:
                        self.logger.warning(f"Lista de dados inválida para usuário {tech_id}")
                        return f'Técnico {tech_id}'
                elif isinstance(user_data, dict):
                    user_info = user_data
                else:
                    self.logger.warning(f"Formato de dados inválido para usuário {tech_id}: {type(user_data)}")
                    return f'Técnico {tech_id}'
                
                if not user_info or not isinstance(user_info, dict):
                    self.logger.warning(f"user_info inválido para usuário {tech_id}")
                    return f'Técnico {tech_id}'
                
                # Tentar diferentes campos de nome em ordem de prioridade
                name_fields = [
                    'completename',  # Nome completo (preferido)
                    'realname',      # Nome real
                    'name',          # Nome de usuário
                    'firstname',     # Primeiro nome
                    'lastname'       # Sobrenome
                ]
                
                for field in name_fields:
                    try:
                        if field in user_info and user_info[field]:
                            name = str(user_info[field]).strip()
                            if name and name.lower() not in ['null', 'none', '']:
                                self.logger.debug(f"Nome encontrado para técnico {tech_id}: {name} (campo: {field})")
                                return name
                    except Exception as e:
                        self.logger.warning(f"Erro ao processar campo {field} para usuário {tech_id}: {e}")
                        continue
                
                # Tentar combinar firstname + lastname
                try:
                    firstname = str(user_info.get('firstname', '')).strip()
                    lastname = str(user_info.get('lastname', '')).strip()
                    
                    if firstname and lastname:
                        combined_name = f"{firstname} {lastname}".strip()
                        if combined_name:
                            self.logger.debug(f"Nome combinado para técnico {tech_id}: {combined_name}")
                            return combined_name
                    elif firstname:
                        self.logger.debug(f"Apenas primeiro nome para técnico {tech_id}: {firstname}")
                        return firstname
                    elif lastname:
                        self.logger.debug(f"Apenas sobrenome para técnico {tech_id}: {lastname}")
                        return lastname
                except Exception as e:
                    self.logger.warning(f"Erro ao combinar nomes para usuário {tech_id}: {e}")
                
                # Fallback final
                self.logger.warning(f"Nenhum nome válido encontrado para técnico {tech_id}")
                return f'Técnico {tech_id}'
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Erro de requisição ao buscar técnico {tech_id}: {e}")
                return f'Técnico {tech_id}'
                
            except Exception as e:
                self.logger.error(f"Erro inesperado ao buscar técnico {tech_id}: {e}")
                return f'Técnico {tech_id}'
                
        except Exception as e:
            self.logger.error(f"Erro crítico no método _get_technician_name para {tech_id}: {e}")
            return f'Técnico {tech_id if tech_id else "Desconhecido"}'
    
    def get_ticket_count_by_hierarchy(self, level: str, status_id: int, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Optional[int]:
        """Busca o total de tickets para um nível hierárquico e status específicos usando campo 8"""
        import datetime
        
        try:
            # Validações de entrada
            if not isinstance(level, str) or not level.strip():
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] level inválido: {level}")
                return 0
                
            if not isinstance(status_id, (int, str)) or (isinstance(status_id, str) and not status_id.strip()):
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] status_id inválido: {status_id}")
                return 0
                
            # Converter status_id para int se necessário
            try:
                status_id = int(status_id)
            except (ValueError, TypeError) as e:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro ao converter status_id para int: {e}")
                return 0
                
            # Validar datas se fornecidas
            if start_date and not isinstance(start_date, str):
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] start_date deve ser string: {type(start_date)}")
                return 0
                
            if end_date and not isinstance(end_date, str):
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] end_date deve ser string: {type(end_date)}")
                return 0
                
            # Verificar configuração básica
            if not hasattr(self, 'glpi_url') or not self.glpi_url:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] GLPI URL não configurada")
                return 0
                
            # Garantir autenticação
            if not self._ensure_authenticated():
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Falha na autenticação")
                return 0
        
            if not self.field_ids:
                if not self.discover_field_ids():
                    timestamp = datetime.datetime.now().isoformat()
                    self.logger.error(
                        f"[{timestamp}] Falha ao descobrir field_ids - "
                        f"level: {level}, status_id: {status_id}, "
                        f"start_date: {start_date}, end_date: {end_date}"
                    )
                    return 0
                    
            # Verificar se field_ids necessários estão disponíveis
            if not self.field_ids.get("STATUS"):
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Field ID STATUS não encontrado: {self.field_ids.get('STATUS')}")
                return 0
            
            # Usar campo 8 para estrutura hierárquica em vez do campo GROUP (71)
            search_params = {
                "is_deleted": 0,
                "range": "0-0",
                "criteria[0][field]": "8",  # Campo 8 contém a estrutura hierárquica
                "criteria[0][searchtype]": "contains",
                "criteria[0][value]": level,  # Ex: "N1", "N2", "N3", "N4"
                "criteria[1][link]": "AND",
                "criteria[1][field]": self.field_ids["STATUS"],
                "criteria[1][searchtype]": "equals",
                "criteria[1][value]": status_id,
            }
            
            # Adicionar filtros de data se fornecidos
            criteria_index = 2
            if start_date:
                search_params[f"criteria[{criteria_index}][link]"] = "AND"
                search_params[f"criteria[{criteria_index}][field]"] = self.field_ids.get("DATE_CREATION", "15")
                search_params[f"criteria[{criteria_index}][searchtype]"] = "morethan"
                search_params[f"criteria[{criteria_index}][value]"] = start_date
                criteria_index += 1
                
            if end_date:
                search_params[f"criteria[{criteria_index}][link]"] = "AND"
                search_params[f"criteria[{criteria_index}][field]"] = self.field_ids.get("DATE_CREATION", "15")
                search_params[f"criteria[{criteria_index}][searchtype]"] = "lessthan"
                search_params[f"criteria[{criteria_index}][value]"] = end_date
                
            headers = self.get_api_headers()
            url = f"{self.glpi_url}/search/Ticket"
            
            self.logger.info(f"[{datetime.datetime.now().isoformat()}] Buscando tickets por hierarquia - level: {level}, status: {status_id}")
            
            response = requests.get(url, params=search_params, headers=headers, timeout=30)
            
            if response.status_code in [200, 206]:
                # Tentar extrair contagem do cabeçalho Content-Range
                content_range = response.headers.get('Content-Range')
                if content_range:
                    try:
                        total_count = int(content_range.split('/')[-1])
                        self.logger.info(f"[{datetime.datetime.now().isoformat()}] Contagem extraída do Content-Range: {total_count}")
                        return total_count
                    except (ValueError, IndexError) as e:
                        self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Erro ao extrair contagem do Content-Range: {e}")
                 
                # Tentar extrair do corpo da resposta
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        # Verificar campo 'content-range'
                        if 'content-range' in data:
                            try:
                                total_count = int(data['content-range'].split('/')[-1])
                                self.logger.info(f"[{datetime.datetime.now().isoformat()}] Contagem extraída do content-range no JSON: {total_count}")
                                return total_count
                            except (ValueError, IndexError) as e:
                                self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Erro ao extrair contagem do content-range JSON: {e}")
                        
                        # Verificar campo 'totalcount'
                        if 'totalcount' in data:
                            total_count = int(data['totalcount'])
                            self.logger.info(f"[{datetime.datetime.now().isoformat()}] Contagem extraída do totalcount: {total_count}")
                            return total_count
                            
                        # Se data é uma lista, retornar o comprimento
                        if 'data' in data and isinstance(data['data'], list):
                            count = len(data['data'])
                            self.logger.info(f"[{datetime.datetime.now().isoformat()}] Contagem baseada no tamanho da lista de dados: {count}")
                            return count
                    
                    # Se a resposta é uma lista diretamente
                    elif isinstance(data, list):
                        count = len(data)
                        self.logger.info(f"[{datetime.datetime.now().isoformat()}] Contagem baseada no tamanho da lista: {count}")
                        return count
                        
                except ValueError as e:
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro ao decodificar JSON: {e}")
                    
                self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Resposta sem Content-Range ou totalcount válidos")
                return 0
            else:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro na requisição: {response.status_code} - {response.text}")
                return 0
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro de requisição: {e}")
            return 0
        except Exception as e:
            self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro inesperado: {e}")
            return 0

    def get_ticket_count(self, group_id: int, status_id: int, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Optional[int]:
        """Busca o total de tickets para um grupo e status específicos, com filtro de data opcional"""
        import datetime
        
        try:
            # Validações de entrada
            if not isinstance(group_id, (int, str)) or (isinstance(group_id, str) and not group_id.strip()):
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] group_id inválido: {group_id}")
                return 0
                
            if not isinstance(status_id, (int, str)) or (isinstance(status_id, str) and not status_id.strip()):
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] status_id inválido: {status_id}")
                return 0
                
            # Converter para int se necessário
            try:
                group_id = int(group_id)
                status_id = int(status_id)
            except (ValueError, TypeError) as e:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro ao converter IDs para int: {e}")
                return 0
                
            # Validar datas se fornecidas
            if start_date and not isinstance(start_date, str):
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] start_date deve ser string: {type(start_date)}")
                return 0
                
            if end_date and not isinstance(end_date, str):
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] end_date deve ser string: {type(end_date)}")
                return 0
                
            # Verificar configuração básica
            if not hasattr(self, 'glpi_url') or not self.glpi_url:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] GLPI URL não configurada")
                return 0
                
            # Garantir autenticação
            if not self._ensure_authenticated():
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Falha na autenticação")
                return 0
        
            if not self.field_ids:
                if not self.discover_field_ids():
                    timestamp = datetime.datetime.now().isoformat()
                    self.logger.error(
                        f"[{timestamp}] Falha ao descobrir field_ids - "
                        f"group_id: {group_id}, status_id: {status_id}, "
                        f"start_date: {start_date}, end_date: {end_date}"
                    )
                    return 0
                    
            # Verificar se field_ids necessários estão disponíveis
            if not self.field_ids.get("GROUP") or not self.field_ids.get("STATUS"):
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Field IDs críticos não encontrados: GROUP={self.field_ids.get('GROUP')}, STATUS={self.field_ids.get('STATUS')}")
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
            if start_date and start_date.strip():
                try:
                    # Validar formato da data
                    datetime.datetime.strptime(start_date.strip(), '%Y-%m-%d')
                    search_params[f"criteria[{criteria_index}][link]"] = "AND"
                    search_params[f"criteria[{criteria_index}][field]"] = "15"  # Campo 15 é o correto para data de criação
                    search_params[f"criteria[{criteria_index}][searchtype]"] = "morethan"
                    search_params[f"criteria[{criteria_index}][value]"] = start_date.strip()
                    criteria_index += 1
                except ValueError as e:
                    self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Formato de start_date inválido '{start_date}': {e}")
                
            if end_date and end_date.strip():
                try:
                    # Validar formato da data
                    datetime.datetime.strptime(end_date.strip(), '%Y-%m-%d')
                    search_params[f"criteria[{criteria_index}][link]"] = "AND"
                    search_params[f"criteria[{criteria_index}][field]"] = "15"  # Campo 15 é o correto para data de criação
                    search_params[f"criteria[{criteria_index}][searchtype]"] = "lessthan"
                    search_params[f"criteria[{criteria_index}][value]"] = end_date.strip()
                except ValueError as e:
                    self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Formato de end_date inválido '{end_date}': {e}")
        
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
                
                # Verificar se o status code é válido (200 OK ou 206 Partial Content)
                if response.status_code not in [200, 206]:
                    timestamp = datetime.datetime.now().isoformat()
                    self.logger.error(
                        f"[{timestamp}] API GLPI retornou status {response.status_code} - "
                        f"group_id: {group_id}, status_id: {status_id}, "
                        f"start_date: {start_date}, end_date: {end_date}"
                    )
                    return 0
                
                # Verificar se há cabeçalho Content-Range
                if "Content-Range" in response.headers:
                    try:
                        content_range = response.headers["Content-Range"]
                        if not content_range or "/" not in content_range:
                            self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Content-Range inválido: {content_range}")
                            return 0
                            
                        total_str = content_range.split("/")[-1]
                        if not total_str.isdigit():
                            self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Total não numérico no Content-Range: {total_str}")
                            return 0
                            
                        total = int(total_str)
                        self.logger.debug(f"[{datetime.datetime.now().isoformat()}] Contagem de tickets encontrada no cabeçalho: {total}")
                        return total
                    except (ValueError, IndexError) as e:
                        self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro ao processar Content-Range '{response.headers.get('Content-Range', '')}': {e}")
                        return 0
                
                # Verificar se há content-range no corpo da resposta JSON
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and "content-range" in response_data:
                        content_range = response_data["content-range"]
                        if content_range and "/" in content_range:
                            total_str = content_range.split("/")[-1]
                            if total_str.isdigit():
                                total = int(total_str)
                                self.logger.debug(f"[{datetime.datetime.now().isoformat()}] Contagem de tickets encontrada no JSON: {total}")
                                return total
                            else:
                                self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Total não numérico no content-range JSON: {total_str}")
                        else:
                            self.logger.warning(f"[{datetime.datetime.now().isoformat()}] content-range JSON inválido: {content_range}")
                    
                    # Verificar se há totalcount no JSON (alternativa)
                    if isinstance(response_data, dict) and "totalcount" in response_data:
                        total = response_data["totalcount"]
                        if isinstance(total, int):
                            self.logger.debug(f"[{datetime.datetime.now().isoformat()}] Contagem de tickets encontrada via totalcount: {total}")
                            return total
                        
                except (ValueError, KeyError) as e:
                    self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Erro ao processar JSON da resposta: {e}")
                
                # Se chegou até aqui com status 200 mas sem Content-Range, retornar 0
                self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Resposta sem Content-Range válido - assumindo 0 tickets")
                return 0
                    
            except requests.exceptions.Timeout as e:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Timeout ao buscar contagem de tickets: {e}")
                return 0
            except requests.exceptions.ConnectionError as e:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro de conexão ao buscar contagem de tickets: {e}")
                return 0
            except requests.exceptions.RequestException as e:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro de requisição ao buscar contagem de tickets: {e}")
                return 0
            except Exception as e:
                timestamp = datetime.datetime.now().isoformat()
                self.logger.error(
                    f"[{timestamp}] Exceção inesperada ao buscar contagem de tickets: {str(e)} - "
                    f"group_id: {group_id}, status_id: {status_id}, "
                    f"start_date: {start_date}, end_date: {end_date}"
                )
                return 0
                
        except Exception as e:
            self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro geral no get_ticket_count: {e}")
            return 0
    
    def get_metrics_by_level(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Dict[str, int]]:
        """Retorna métricas de tickets agrupadas por nível de atendimento"""
        import datetime
        
        try:
            # Verificar configuração básica
            if not hasattr(self, 'service_levels') or not self.service_levels:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] service_levels não configurado")
                return {}
                
            if not hasattr(self, 'status_map') or not self.status_map:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] status_map não configurado")
                return {}
                
            if not hasattr(self, 'glpi_url') or not self.glpi_url:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] GLPI URL não configurada")
                return {}
                
            # Garantir autenticação
            if not self._ensure_authenticated():
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Falha na autenticação")
                return {}
                
            # Descobrir field_ids se necessário
            if not self.discover_field_ids():
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Falha ao descobrir field_ids")
                return {}
            
            return self._get_metrics_by_level_internal_hierarchy(start_date, end_date)
            
        except Exception as e:
            self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro geral no get_metrics_by_level: {e}")
            return {}
    
    def _get_metrics_by_level_internal(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Dict[str, int]]:
        """Método interno para obter métricas por nível (sem autenticação/fechamento)"""
        import datetime
        
        try:
            # Validações de entrada
            if start_date and not isinstance(start_date, str):
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] start_date deve ser string: {type(start_date)}")
                return {}
                
            if end_date and not isinstance(end_date, str):
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] end_date deve ser string: {type(end_date)}")
                return {}
                
            # Validar formato das datas se fornecidas
            if start_date and start_date.strip():
                try:
                    datetime.datetime.strptime(start_date.strip(), '%Y-%m-%d')
                except ValueError as e:
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Formato de start_date inválido '{start_date}': {e}")
                    return {}
                    
            if end_date and end_date.strip():
                try:
                    datetime.datetime.strptime(end_date.strip(), '%Y-%m-%d')
                except ValueError as e:
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Formato de end_date inválido '{end_date}': {e}")
                    return {}
                    
            # Verificar se as configurações necessárias estão disponíveis
            if not hasattr(self, 'service_levels') or not isinstance(self.service_levels, dict):
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] service_levels inválido: {getattr(self, 'service_levels', None)}")
                return {}
                
            if not hasattr(self, 'status_map') or not isinstance(self.status_map, dict):
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] status_map inválido: {getattr(self, 'status_map', None)}")
                return {}
                
            if not self.service_levels:
                self.logger.warning(f"[{datetime.datetime.now().isoformat()}] service_levels está vazio")
                return {}
                
            if not self.status_map:
                self.logger.warning(f"[{datetime.datetime.now().isoformat()}] status_map está vazio")
                return {}
        
            metrics = {}
            
            for level_name, group_id in self.service_levels.items():
                try:
                    # Validar level_name e group_id
                    if not level_name or not isinstance(level_name, str):
                        self.logger.warning(f"[{datetime.datetime.now().isoformat()}] level_name inválido: {level_name}")
                        continue
                        
                    if not isinstance(group_id, (int, str)) or (isinstance(group_id, str) and not group_id.strip()):
                        self.logger.warning(f"[{datetime.datetime.now().isoformat()}] group_id inválido para {level_name}: {group_id}")
                        continue
                        
                    level_metrics = {}
                    
                    for status_name, status_id in self.status_map.items():
                        try:
                            # Validar status_name e status_id
                            if not status_name or not isinstance(status_name, str):
                                self.logger.warning(f"[{datetime.datetime.now().isoformat()}] status_name inválido: {status_name}")
                                continue
                                
                            if not isinstance(status_id, (int, str)) or (isinstance(status_id, str) and not status_id.strip()):
                                self.logger.warning(f"[{datetime.datetime.now().isoformat()}] status_id inválido para {status_name}: {status_id}")
                                continue
                                
                            count = self.get_ticket_count(group_id, status_id, start_date, end_date)
                            level_metrics[status_name] = count if count is not None else 0
                            
                        except Exception as e:
                            self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro ao obter contagem para {level_name}/{status_name}: {e}")
                            level_metrics[status_name] = 0
                    
                    metrics[level_name] = level_metrics
                    
                except Exception as e:
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro ao processar nível {level_name}: {e}")
                    metrics[level_name] = {}
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro geral no _get_metrics_by_level_internal: {e}")
            return {}
    
    def _get_metrics_by_level_internal_hierarchy(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Dict[str, int]]:
        """Método interno para obter métricas por nível usando estrutura hierárquica (campo 8)"""
        import datetime
        
        try:
            # Validações de entrada
            if start_date and not isinstance(start_date, str):
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] start_date deve ser string: {type(start_date)}")
                return {}
                
            if end_date and not isinstance(end_date, str):
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] end_date deve ser string: {type(end_date)}")
                return {}
                
            # Validar formato das datas se fornecidas
            if start_date and start_date.strip():
                try:
                    datetime.datetime.strptime(start_date.strip(), '%Y-%m-%d')
                except ValueError as e:
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Formato de start_date inválido '{start_date}': {e}")
                    return {}
                    
            if end_date and end_date.strip():
                try:
                    datetime.datetime.strptime(end_date.strip(), '%Y-%m-%d')
                except ValueError as e:
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Formato de end_date inválido '{end_date}': {e}")
                    return {}
                    
            # Verificar se as configurações necessárias estão disponíveis
            if not hasattr(self, 'status_map') or not isinstance(self.status_map, dict):
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] status_map inválido: {getattr(self, 'status_map', None)}")
                return {}
                
            if not self.status_map:
                self.logger.warning(f"[{datetime.datetime.now().isoformat()}] status_map está vazio")
                return {}
        
            # Definir níveis hierárquicos diretamente
            hierarchy_levels = ['N1', 'N2', 'N3', 'N4']
            metrics = {}
            
            for level in hierarchy_levels:
                try:
                    level_metrics = {}
                    
                    for status_name, status_id in self.status_map.items():
                        try:
                            # Validar status_name e status_id
                            if not status_name or not isinstance(status_name, str):
                                self.logger.warning(f"[{datetime.datetime.now().isoformat()}] status_name inválido: {status_name}")
                                continue
                                
                            if not isinstance(status_id, (int, str)) or (isinstance(status_id, str) and not status_id.strip()):
                                self.logger.warning(f"[{datetime.datetime.now().isoformat()}] status_id inválido para {status_name}: {status_id}")
                                continue
                                
                            # Usar o novo método baseado em hierarquia
                            count = self.get_ticket_count_by_hierarchy(level, status_id, start_date, end_date)
                            level_metrics[status_name] = count if count is not None else 0
                            
                        except Exception as e:
                            self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro ao obter contagem para {level}/{status_name}: {e}")
                            level_metrics[status_name] = 0
                    
                    metrics[level] = level_metrics
                    
                except Exception as e:
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro ao processar nível {level}: {e}")
                    metrics[level] = {}
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro geral no _get_metrics_by_level_internal_hierarchy: {e}")
            return {}
    
    def get_general_metrics(self) -> Dict[str, int]:
        """Retorna métricas gerais de todos os tickets (não apenas grupos N1-N4)"""
        import datetime
        
        try:
            # Verificar configuração básica
            if not hasattr(self, 'status_map') or not self.status_map:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] status_map não configurado")
                return {}
                
            if not hasattr(self, 'glpi_url') or not self.glpi_url:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] GLPI URL não configurada")
                return {}
                
            # Garantir autenticação
            if not self._ensure_authenticated():
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Falha na autenticação")
                return {}
                
            # Descobrir field_ids se necessário
            if not self.discover_field_ids():
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Falha ao descobrir field_ids")
                return {}
            
            result = self._get_general_metrics_internal()
            return result
            
        except Exception as e:
            self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro geral no get_general_metrics: {e}")
            return {}
    
    def _get_general_metrics_internal(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, int]:
        """Método interno para obter métricas gerais (sem autenticação/fechamento)"""
        import datetime
        
        try:
            # Validações de entrada
            if start_date and not isinstance(start_date, str):
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] start_date deve ser string: {type(start_date)}")
                return {}
                
            if end_date and not isinstance(end_date, str):
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] end_date deve ser string: {type(end_date)}")
                return {}
                
            # Validar formato das datas se fornecidas
            if start_date and start_date.strip():
                try:
                    datetime.datetime.strptime(start_date.strip(), '%Y-%m-%d')
                except ValueError as e:
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Formato de start_date inválido '{start_date}': {e}")
                    return {}
                    
            if end_date and end_date.strip():
                try:
                    datetime.datetime.strptime(end_date.strip(), '%Y-%m-%d')
                except ValueError as e:
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Formato de end_date inválido '{end_date}': {e}")
                    return {}
                    
            # Verificar configurações necessárias
            if not hasattr(self, 'status_map') or not isinstance(self.status_map, dict):
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] status_map inválido: {getattr(self, 'status_map', None)}")
                return {}
                
            if not hasattr(self, 'field_ids') or not isinstance(self.field_ids, dict):
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] field_ids inválido: {getattr(self, 'field_ids', None)}")
                return {}
                
            if not self.status_map:
                self.logger.warning(f"[{datetime.datetime.now().isoformat()}] status_map está vazio")
                return {}
                
            if not self.field_ids.get("STATUS"):
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Field ID STATUS não encontrado: {self.field_ids}")
                return {}
                
            if not hasattr(self, 'glpi_url') or not self.glpi_url:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] GLPI URL não configurada")
                return {}
        
            status_totals = {}
            
            # Buscar totais por status sem filtro de grupo
            for status_name, status_id in self.status_map.items():
                try:
                    # Validar status_name e status_id
                    if not status_name or not isinstance(status_name, str):
                        self.logger.warning(f"[{datetime.datetime.now().isoformat()}] status_name inválido: {status_name}")
                        continue
                        
                    if not isinstance(status_id, (int, str)) or (isinstance(status_id, str) and not status_id.strip()):
                        self.logger.warning(f"[{datetime.datetime.now().isoformat()}] status_id inválido para {status_name}: {status_id}")
                        continue
                        
                    # Converter status_id para int se necessário
                    try:
                        status_id_int = int(status_id)
                    except (ValueError, TypeError) as e:
                        self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro ao converter status_id para int '{status_id}': {e}")
                        status_totals[status_name] = 0
                        continue
                        
                    search_params = {
                        "is_deleted": 0,
                        "range": "0-0",
                        "criteria[0][field]": self.field_ids["STATUS"],
                        "criteria[0][searchtype]": "equals",
                        "criteria[0][value]": status_id_int,
                    }
                    
                    # Adicionar filtros de data se fornecidos (formato ISO funciona melhor)
                    criteria_index = 1
                    if start_date and start_date.strip():
                        try:
                            # Validar formato da data novamente
                            datetime.datetime.strptime(start_date.strip(), '%Y-%m-%d')
                            search_params[f"criteria[{criteria_index}][link]"] = "AND"
                            search_params[f"criteria[{criteria_index}][field]"] = "15"  # Campo 15 é o correto para data de criação
                            search_params[f"criteria[{criteria_index}][searchtype]"] = "morethan"
                            search_params[f"criteria[{criteria_index}][value]"] = start_date.strip()
                            criteria_index += 1
                        except ValueError as e:
                            self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Formato de start_date inválido '{start_date}': {e}")
                        
                    if end_date and end_date.strip():
                        try:
                            # Validar formato da data novamente
                            datetime.datetime.strptime(end_date.strip(), '%Y-%m-%d')
                            search_params[f"criteria[{criteria_index}][link]"] = "AND"
                            search_params[f"criteria[{criteria_index}][field]"] = "15"  # Campo 15 é o correto para data de criação
                            search_params[f"criteria[{criteria_index}][searchtype]"] = "lessthan"
                            search_params[f"criteria[{criteria_index}][value]"] = end_date.strip()
                        except ValueError as e:
                            self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Formato de end_date inválido '{end_date}': {e}")
                    
                    try:
                        response = self._make_authenticated_request(
                            'GET',
                            f"{self.glpi_url}/search/Ticket",
                            params=search_params
                        )
                        
                        if not response:
                            self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Resposta vazia para status {status_name}")
                            status_totals[status_name] = 0
                            continue
                            
                        if response.status_code not in [200, 206]:
                            self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Status code inválido {response.status_code} para status {status_name}")
                            status_totals[status_name] = 0
                            continue
                            
                        if "Content-Range" in response.headers:
                            try:
                                content_range = response.headers["Content-Range"]
                                if not content_range or "/" not in content_range:
                                    self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Content-Range inválido para {status_name}: {content_range}")
                                    status_totals[status_name] = 0
                                    continue
                                    
                                total_str = content_range.split("/")[-1]
                                if not total_str.isdigit():
                                    self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Total não numérico para {status_name}: {total_str}")
                                    status_totals[status_name] = 0
                                    continue
                                    
                                count = int(total_str)
                                status_totals[status_name] = count
                                self.logger.debug(f"[{datetime.datetime.now().isoformat()}] Contagem para {status_name}: {count}")
                            except (ValueError, IndexError) as e:
                                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro ao processar Content-Range para {status_name}: {e}")
                                status_totals[status_name] = 0
                        else:
                            self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Sem Content-Range para {status_name}")
                            status_totals[status_name] = 0
                            
                    except requests.exceptions.Timeout as e:
                        self.logger.error(f"[{datetime.datetime.now().isoformat()}] Timeout ao buscar {status_name}: {e}")
                        status_totals[status_name] = 0
                    except requests.exceptions.ConnectionError as e:
                        self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro de conexão ao buscar {status_name}: {e}")
                        status_totals[status_name] = 0
                    except requests.exceptions.RequestException as e:
                        self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro de requisição ao buscar {status_name}: {e}")
                        status_totals[status_name] = 0
                    except Exception as e:
                        self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro inesperado ao buscar contagem geral para {status_name}: {e}")
                        status_totals[status_name] = 0
                        
                except Exception as e:
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro ao processar status {status_name}: {e}")
                    status_totals[status_name] = 0
            
            return status_totals
            
        except Exception as e:
            self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro geral no _get_general_metrics_internal: {e}")
            return {}
    
    def get_dashboard_metrics(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, any]:
        """Retorna métricas formatadas para o dashboard React usando o sistema unificado.
        
        Args:
            start_date: Data inicial no formato YYYY-MM-DD (opcional)
            end_date: Data final no formato YYYY-MM-DD (opcional)
        
        Retorna um dicionário com as métricas formatadas ou erro.
        """
        import datetime
        start_time = time.time()
        
        try:
            # Validações de entrada
            if start_date and not isinstance(start_date, str):
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] start_date deve ser string: {type(start_date)}")
                return ResponseFormatter.format_error_response("Parâmetro start_date inválido", ["start_date deve ser uma string"])
                
            if end_date and not isinstance(end_date, str):
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] end_date deve ser string: {type(end_date)}")
                return ResponseFormatter.format_error_response("Parâmetro end_date inválido", ["end_date deve ser uma string"])
                
            # Validar formato das datas se fornecidas
            if start_date and start_date.strip():
                try:
                    datetime.datetime.strptime(start_date.strip(), '%Y-%m-%d')
                except ValueError as e:
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Formato de start_date inválido '{start_date}': {e}")
                    return ResponseFormatter.format_error_response("Formato de data inválido", [f"start_date deve estar no formato YYYY-MM-DD: {start_date}"])
                    
            if end_date and end_date.strip():
                try:
                    datetime.datetime.strptime(end_date.strip(), '%Y-%m-%d')
                except ValueError as e:
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Formato de end_date inválido '{end_date}': {e}")
                    return ResponseFormatter.format_error_response("Formato de data inválido", [f"end_date deve estar no formato YYYY-MM-DD: {end_date}"])
                    
            # Verificar configurações básicas
            if not hasattr(self, 'glpi_url') or not self.glpi_url:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] GLPI URL não configurada")
                return ResponseFormatter.format_error_response("Configuração inválida", ["GLPI URL não configurada"])
                
            if not hasattr(self, 'status_map') or not self.status_map:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] status_map não configurado")
                return ResponseFormatter.format_error_response("Configuração inválida", ["Mapeamento de status não configurado"])
                
            if not hasattr(self, 'service_levels') or not self.service_levels:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] service_levels não configurado")
                return ResponseFormatter.format_error_response("Configuração inválida", ["Níveis de serviço não configurados"])
            
            # Se parâmetros de data foram fornecidos, usar o método com filtro
            if start_date or end_date:
                try:
                    return self.get_dashboard_metrics_with_date_filter(start_date, end_date)
                except Exception as e:
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro no método com filtro de data: {e}")
                    return ResponseFormatter.format_error_response("Erro ao obter métricas com filtro", [str(e)])
            
            # Verificar cache primeiro
            try:
                if self._is_cache_valid('dashboard_metrics'):
                    cached_data = self._get_cache_data('dashboard_metrics')
                    if cached_data:
                        self.logger.info(f"[{datetime.datetime.now().isoformat()}] Retornando métricas do cache")
                        return cached_data
            except Exception as e:
                self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Erro ao verificar cache: {e}")
            
            # Autenticar uma única vez
            if not self._ensure_authenticated():
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Falha na autenticação")
                return ResponseFormatter.format_error_response("Falha na autenticação com GLPI", ["Erro de autenticação"])
            
            if not self.discover_field_ids():
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Falha ao descobrir field_ids")
                return ResponseFormatter.format_error_response("Falha ao descobrir IDs dos campos", ["Erro ao obter configuração"])
            
            # Obter totais gerais (todos os grupos) para métricas principais
            try:
                general_totals = self._get_general_metrics_internal()
                if not isinstance(general_totals, dict):
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] general_totals inválido: {type(general_totals)}")
                    return ResponseFormatter.format_error_response("Erro ao obter métricas gerais", ["Dados inválidos retornados"])
                    
                self.logger.info(f"[{datetime.datetime.now().isoformat()}] Totais gerais obtidos: {general_totals}")
            except Exception as e:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro ao obter totais gerais: {e}")
                return ResponseFormatter.format_error_response("Erro ao obter métricas gerais", [str(e)])
            
            # Obter métricas por nível (grupos N1-N4)
            try:
                raw_metrics = self._get_metrics_by_level_internal_hierarchy()
                if not isinstance(raw_metrics, dict):
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] raw_metrics inválido: {type(raw_metrics)}")
                    return ResponseFormatter.format_error_response("Erro ao obter métricas por nível", ["Dados inválidos retornados"])
                    
                self.logger.debug(f"[{datetime.datetime.now().isoformat()}] Métricas por nível obtidas: {raw_metrics}")
            except Exception as e:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro ao obter métricas por nível: {e}")
                return ResponseFormatter.format_error_response("Erro ao obter métricas por nível", [str(e)])
            
            # Usar o mesmo formato da função com filtros para consistência
            # Calcular totais gerais com validação
            try:
                general_novos = general_totals.get("Novo", 0) if general_totals else 0
                general_pendentes = general_totals.get("Pendente", 0) if general_totals else 0
                general_progresso = (general_totals.get("Processando (atribuído)", 0) + 
                                   general_totals.get("Processando (planejado)", 0)) if general_totals else 0
                general_resolvidos = (general_totals.get("Solucionado", 0) + 
                                    general_totals.get("Fechado", 0)) if general_totals else 0
                general_total = general_novos + general_pendentes + general_progresso + general_resolvidos
                
                # Validar se os valores são numéricos
                for name, value in [("novos", general_novos), ("pendentes", general_pendentes), 
                                  ("progresso", general_progresso), ("resolvidos", general_resolvidos)]:
                    if not isinstance(value, (int, float)) or value < 0:
                        self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Valor inválido para {name}: {value}")
                        
            except Exception as e:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro ao calcular totais gerais: {e}")
                return ResponseFormatter.format_error_response("Erro ao calcular totais", [str(e)])
            
            # Métricas por nível com validação
            try:
                level_metrics = {
                    "n1": {"novos": 0, "progresso": 0, "pendentes": 0, "resolvidos": 0},
                    "n2": {"novos": 0, "progresso": 0, "pendentes": 0, "resolvidos": 0},
                    "n3": {"novos": 0, "progresso": 0, "pendentes": 0, "resolvidos": 0},
                    "n4": {"novos": 0, "progresso": 0, "pendentes": 0, "resolvidos": 0}
                }
                
                if raw_metrics and isinstance(raw_metrics, dict):
                    for level_name, level_data in raw_metrics.items():
                        try:
                            if not level_name or not isinstance(level_name, str):
                                self.logger.warning(f"[{datetime.datetime.now().isoformat()}] level_name inválido: {level_name}")
                                continue
                                
                            if not isinstance(level_data, dict):
                                self.logger.warning(f"[{datetime.datetime.now().isoformat()}] level_data inválido para {level_name}: {type(level_data)}")
                                continue
                                
                            level_key = level_name.lower()
                            if level_key in level_metrics:
                                # Validar e extrair valores com fallback para 0
                                novos = level_data.get("Novo", 0)
                                progresso_atribuido = level_data.get("Processando (atribuído)", 0)
                                progresso_planejado = level_data.get("Processando (planejado)", 0)
                                pendentes = level_data.get("Pendente", 0)
                                solucionado = level_data.get("Solucionado", 0)
                                fechado = level_data.get("Fechado", 0)
                                
                                # Validar tipos numéricos
                                for name, value in [("novos", novos), ("progresso_atribuido", progresso_atribuido),
                                                  ("progresso_planejado", progresso_planejado), ("pendentes", pendentes),
                                                  ("solucionado", solucionado), ("fechado", fechado)]:
                                    if not isinstance(value, (int, float)):
                                        self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Valor não numérico para {level_key}.{name}: {value}")
                                        
                                level_metrics[level_key]["novos"] = max(0, int(novos) if isinstance(novos, (int, float)) else 0)
                                level_metrics[level_key]["progresso"] = max(0, 
                                    (int(progresso_atribuido) if isinstance(progresso_atribuido, (int, float)) else 0) +
                                    (int(progresso_planejado) if isinstance(progresso_planejado, (int, float)) else 0))
                                level_metrics[level_key]["pendentes"] = max(0, int(pendentes) if isinstance(pendentes, (int, float)) else 0)
                                level_metrics[level_key]["resolvidos"] = max(0,
                                    (int(solucionado) if isinstance(solucionado, (int, float)) else 0) +
                                    (int(fechado) if isinstance(fechado, (int, float)) else 0))
                            else:
                                self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Nível desconhecido: {level_key}")
                        except Exception as e:
                            self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro ao processar nível {level_name}: {e}")
                            continue
                            
            except Exception as e:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro ao processar métricas por nível: {e}")
                return ResponseFormatter.format_error_response("Erro ao processar métricas por nível", [str(e)])
            
            # Construir resultado final
            try:
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
                        "tendencias": self._calculate_trends(general_novos, general_pendentes, general_progresso, general_resolvidos)
                    },
                    "timestamp": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "tempo_execucao": (time.time() - start_time) * 1000
                }
                
                # Validar resultado final
                if not isinstance(result, dict) or "success" not in result or "data" not in result:
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Resultado final inválido: {type(result)}")
                    return ResponseFormatter.format_error_response("Erro na construção do resultado", ["Estrutura de dados inválida"])
                    
                self.logger.info(f"[{datetime.datetime.now().isoformat()}] Métricas do dashboard construídas com sucesso")
                
            except Exception as e:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro ao construir resultado final: {e}")
                return ResponseFormatter.format_error_response("Erro ao construir resultado", [str(e)])
            
            # Salvar no cache
            try:
                self._set_cache_data('dashboard_metrics', result, ttl=180)
                self.logger.debug(f"[{datetime.datetime.now().isoformat()}] Resultado salvo no cache")
            except Exception as e:
                self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Erro ao salvar no cache: {e}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro geral ao obter métricas do dashboard: {e}")
            return ResponseFormatter.format_error_response(f"Erro interno: {str(e)}", [str(e)])
    
    def _get_general_totals_internal(self, start_date: str = None, end_date: str = None) -> dict:
        """Método interno para obter totais gerais com filtro de data"""
        import datetime
        
        # Validações de entrada
        try:
            if start_date and not isinstance(start_date, str):
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] start_date deve ser string: {type(start_date)}")
                return {}
                
            if end_date and not isinstance(end_date, str):
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] end_date deve ser string: {type(end_date)}")
                return {}
                
            # Validar formato das datas
            if start_date and start_date.strip():
                try:
                    datetime.datetime.strptime(start_date.strip(), '%Y-%m-%d')
                except ValueError as e:
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Formato de start_date inválido '{start_date}': {e}")
                    return {}
                    
            if end_date and end_date.strip():
                try:
                    datetime.datetime.strptime(end_date.strip(), '%Y-%m-%d')
                except ValueError as e:
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Formato de end_date inválido '{end_date}': {e}")
                    return {}
                    
            # Verificar configurações necessárias
            if not hasattr(self, 'status_map') or not self.status_map:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] status_map não configurado")
                return {}
                
            if not isinstance(self.status_map, dict):
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] status_map deve ser dict: {type(self.status_map)}")
                return {}
                
            if not hasattr(self, 'field_ids') or not self.field_ids:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] field_ids não configurado")
                return {}
                
            if not isinstance(self.field_ids, dict) or "STATUS" not in self.field_ids:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] field_ids inválido ou STATUS ausente")
                return {}
                
            self.logger.debug(f"[{datetime.datetime.now().isoformat()}] Iniciando busca de totais gerais com filtro de data")
            
        except Exception as e:
            self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro na validação de entrada: {e}")
            return {}
        
        status_totals = {}
        
        # Buscar totais por status sem filtro de grupo (mesma lógica do _get_general_metrics_internal)
        for status_name, status_id in self.status_map.items():
            try:
                # Validar status_name e status_id
                if not status_name or not isinstance(status_name, str):
                    self.logger.warning(f"[{datetime.datetime.now().isoformat()}] status_name inválido: {status_name}")
                    continue
                    
                if not isinstance(status_id, (int, str)) or (isinstance(status_id, str) and not status_id.strip()):
                    self.logger.warning(f"[{datetime.datetime.now().isoformat()}] status_id inválido para {status_name}: {status_id}")
                    continue
                
                search_params = {
                    "is_deleted": 0,
                    "range": "0-0",
                    "criteria[0][field]": self.field_ids["STATUS"],
                    "criteria[0][searchtype]": "equals",
                    "criteria[0][value]": status_id,
                }
                
                # Adicionar filtros de data se fornecidos (formato ISO funciona melhor)
                criteria_index = 1
                if start_date and start_date.strip():
                    # Usar formato ISO (YYYY-MM-DD) que funciona corretamente
                    search_params[f"criteria[{criteria_index}][link]"] = "AND"
                    search_params[f"criteria[{criteria_index}][field]"] = "15"  # Campo 15 é o correto para data de criação
                    search_params[f"criteria[{criteria_index}][searchtype]"] = "morethan"
                    search_params[f"criteria[{criteria_index}][value]"] = start_date.strip()
                    criteria_index += 1
                    
                if end_date and end_date.strip():
                    # Usar formato ISO (YYYY-MM-DD) que funciona corretamente
                    search_params[f"criteria[{criteria_index}][link]"] = "AND"
                    search_params[f"criteria[{criteria_index}][field]"] = "15"  # Campo 15 é o correto para data de criação
                    search_params[f"criteria[{criteria_index}][searchtype]"] = "lessthan"
                    search_params[f"criteria[{criteria_index}][value]"] = end_date.strip()
                
                try:
                    response = self._make_authenticated_request(
                        'GET',
                        f"{self.glpi_url}/search/Ticket",
                        params=search_params
                    )
                    
                    if not response:
                        self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Resposta vazia para {status_name}")
                        status_totals[status_name] = 0
                        continue
                        
                    if response.status_code not in [200, 206]:
                        self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Status HTTP inválido para {status_name}: {response.status_code}")
                        status_totals[status_name] = 0
                        continue
                    
                    if "Content-Range" in response.headers:
                        try:
                            content_range = response.headers["Content-Range"]
                            if not content_range or "/" not in content_range:
                                self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Content-Range mal formatado para {status_name}: {content_range}")
                                status_totals[status_name] = 0
                                continue
                                
                            count = int(content_range.split("/")[-1])
                            status_totals[status_name] = max(0, count)
                            self.logger.debug(f"[{datetime.datetime.now().isoformat()}] Contagem para {status_name}: {count}")
                        except (ValueError, IndexError) as e:
                            self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro ao parsear Content-Range para {status_name}: {e}")
                            status_totals[status_name] = 0
                    else:
                        self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Content-Range ausente para {status_name}")
                        status_totals[status_name] = 0
                        
                except requests.exceptions.Timeout as e:
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Timeout ao buscar {status_name}: {e}")
                    status_totals[status_name] = 0
                except requests.exceptions.ConnectionError as e:
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro de conexão ao buscar {status_name}: {e}")
                    status_totals[status_name] = 0
                except requests.exceptions.RequestException as e:
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro de requisição ao buscar {status_name}: {e}")
                    status_totals[status_name] = 0
                except Exception as e:
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro inesperado ao buscar {status_name}: {e}")
                    status_totals[status_name] = 0
                    
            except Exception as e:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro ao processar status {status_name}: {e}")
                status_totals[status_name] = 0
        
        self.logger.info(f"[{datetime.datetime.now().isoformat()}] Totais gerais obtidos: {status_totals}")
        return status_totals
    
    def get_dashboard_metrics_with_date_filter(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, any]:
        """Retorna métricas formatadas para o dashboard React com filtro de data.
        
        Args:
            start_date: Data inicial no formato YYYY-MM-DD (opcional)
            end_date: Data final no formato YYYY-MM-DD (opcional)
        
        Retorna um dicionário com as métricas ou None em caso de falha.
        """
        start_time = time.time()
        self.logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando get_dashboard_metrics_with_date_filter com start_date={start_date}, end_date={end_date}")
        
        try:
            # Validar formato das datas se fornecidas
            if start_date:
                if not isinstance(start_date, str):
                    self.logger.error(f"start_date deve ser string, recebido: {type(start_date)}")
                    return None
                try:
                    datetime.strptime(start_date, '%Y-%m-%d')
                except ValueError as e:
                    self.logger.error(f"Formato inválido para start_date '{start_date}': {e}")
                    return None
            
            if end_date:
                if not isinstance(end_date, str):
                    self.logger.error(f"end_date deve ser string, recebido: {type(end_date)}")
                    return None
                try:
                    datetime.strptime(end_date, '%Y-%m-%d')
                except ValueError as e:
                    self.logger.error(f"Formato inválido para end_date '{end_date}': {e}")
                    return None
            
            # Validar configurações essenciais
            if not hasattr(self, 'glpi_url') or not self.glpi_url:
                self.logger.error("glpi_url não configurado")
                return None
            
            if not hasattr(self, 'status_map') or not isinstance(self.status_map, dict) or not self.status_map:
                self.logger.error("status_map não configurado ou inválido")
                return None
            
            # Criar chave de cache baseada nos parâmetros de data
            cache_key = f"{start_date or 'none'}_{end_date or 'none'}"
            
            # Verificar se existe cache válido para este filtro
            try:
                if self._is_cache_valid('dashboard_metrics_filtered', cache_key):
                    cached_data = self._get_cache_data('dashboard_metrics_filtered', cache_key)
                    if cached_data:
                        self.logger.info(f"Retornando métricas do cache para filtro: {cache_key}")
                        return cached_data
            except Exception as e:
                self.logger.warning(f"Erro ao verificar cache: {e}")
            
            # Autenticar uma única vez
            try:
                if not self._ensure_authenticated():
                    self.logger.error("Falha na autenticação")
                    return None
            except Exception as e:
                self.logger.error(f"Erro durante autenticação: {e}")
                return None
            
            try:
                if not self.discover_field_ids():
                    self.logger.error("Falha na descoberta de field_ids")
                    return None
            except Exception as e:
                self.logger.error(f"Erro durante descoberta de field_ids: {e}")
                return None
        
            # Obter totais gerais (todos os grupos) para métricas principais com filtro de data
            try:
                general_totals = self._get_general_metrics_internal(start_date, end_date)
                if not isinstance(general_totals, dict):
                    self.logger.error(f"general_totals deve ser dict, recebido: {type(general_totals)}")
                    return None
                self.logger.info(f"Totais gerais obtidos com filtro de data: {general_totals}")
            except Exception as e:
                self.logger.error(f"Erro ao obter totais gerais: {e}")
                return None
            
            # Obter métricas por nível (grupos N1-N4) com filtro de data
            try:
                raw_metrics = self._get_metrics_by_level_internal_hierarchy(start_date, end_date)
                if not isinstance(raw_metrics, dict):
                    self.logger.error(f"raw_metrics deve ser dict, recebido: {type(raw_metrics)}")
                    return None
                self.logger.info(f"Métricas por nível obtidas: {len(raw_metrics)} níveis")
            except Exception as e:
                self.logger.error(f"Erro ao obter métricas por nível: {e}")
                return None
        
            # Agregação dos totais por status (apenas para níveis)
            try:
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
                    try:
                        if not isinstance(level_data, dict):
                            self.logger.warning(f"level_data para {level_name} não é dict: {type(level_data)}")
                            continue
                        
                        level_key = level_name.lower()
                        if level_key not in level_metrics:
                            self.logger.warning(f"Nível desconhecido: {level_key}")
                            continue
                        
                        # Novo
                        novo_count = level_data.get("Novo", 0)
                        if not isinstance(novo_count, (int, float)):
                            self.logger.warning(f"Valor inválido para 'Novo' em {level_name}: {novo_count}")
                            novo_count = 0
                        level_metrics[level_key]["novos"] = int(novo_count)
                        totals["novos"] += level_metrics[level_key]["novos"]
                        
                        # Progresso (soma de Processando atribuído e planejado)
                        processando_atribuido = level_data.get("Processando (atribuído)", 0)
                        processando_planejado = level_data.get("Processando (planejado)", 0)
                        if not isinstance(processando_atribuido, (int, float)):
                            self.logger.warning(f"Valor inválido para 'Processando (atribuído)' em {level_name}: {processando_atribuido}")
                            processando_atribuido = 0
                        if not isinstance(processando_planejado, (int, float)):
                            self.logger.warning(f"Valor inválido para 'Processando (planejado)' em {level_name}: {processando_planejado}")
                            processando_planejado = 0
                        level_metrics[level_key]["progresso"] = int(processando_atribuido) + int(processando_planejado)
                        totals["progresso"] += level_metrics[level_key]["progresso"]
                        
                        # Pendente
                        pendente_count = level_data.get("Pendente", 0)
                        if not isinstance(pendente_count, (int, float)):
                            self.logger.warning(f"Valor inválido para 'Pendente' em {level_name}: {pendente_count}")
                            pendente_count = 0
                        level_metrics[level_key]["pendentes"] = int(pendente_count)
                        totals["pendentes"] += level_metrics[level_key]["pendentes"]
                        
                        # Resolvidos (soma de Solucionado e Fechado)
                        solucionado = level_data.get("Solucionado", 0)
                        fechado = level_data.get("Fechado", 0)
                        if not isinstance(solucionado, (int, float)):
                            self.logger.warning(f"Valor inválido para 'Solucionado' em {level_name}: {solucionado}")
                            solucionado = 0
                        if not isinstance(fechado, (int, float)):
                            self.logger.warning(f"Valor inválido para 'Fechado' em {level_name}: {fechado}")
                            fechado = 0
                        level_metrics[level_key]["resolvidos"] = int(solucionado) + int(fechado)
                        totals["resolvidos"] += level_metrics[level_key]["resolvidos"]
                        
                    except Exception as e:
                        self.logger.error(f"Erro ao processar métricas para nível {level_name}: {e}")
                        continue
                
                self.logger.info(f"Agregação concluída - totais: {totals}")
                
            except Exception as e:
                self.logger.error(f"Erro durante agregação de métricas: {e}")
                return None
        
            # Usar totais gerais para métricas principais
            try:
                general_novos = general_totals.get("Novo", 0)
                general_pendentes = general_totals.get("Pendente", 0)
                general_progresso_atribuido = general_totals.get("Processando (atribuído)", 0)
                general_progresso_planejado = general_totals.get("Processando (planejado)", 0)
                general_solucionado = general_totals.get("Solucionado", 0)
                general_fechado = general_totals.get("Fechado", 0)
                
                # Validar tipos dos valores
                for name, value in [("Novo", general_novos), ("Pendente", general_pendentes), 
                                   ("Processando (atribuído)", general_progresso_atribuido),
                                   ("Processando (planejado)", general_progresso_planejado),
                                   ("Solucionado", general_solucionado), ("Fechado", general_fechado)]:
                    if not isinstance(value, (int, float)):
                        self.logger.warning(f"Valor inválido para '{name}': {value}, usando 0")
                        if name == "Novo":
                            general_novos = 0
                        elif name == "Pendente":
                            general_pendentes = 0
                        elif name == "Processando (atribuído)":
                            general_progresso_atribuido = 0
                        elif name == "Processando (planejado)":
                            general_progresso_planejado = 0
                        elif name == "Solucionado":
                            general_solucionado = 0
                        elif name == "Fechado":
                            general_fechado = 0
                
                general_progresso = int(general_progresso_atribuido) + int(general_progresso_planejado)
                general_resolvidos = int(general_solucionado) + int(general_fechado)
                general_total = int(general_novos) + int(general_pendentes) + general_progresso + general_resolvidos
                
                self.logger.info(f"Métricas gerais calculadas com filtro: novos={general_novos}, pendentes={general_pendentes}, progresso={general_progresso}, resolvidos={general_resolvidos}, total={general_total}")
                
            except Exception as e:
                self.logger.error(f"Erro ao calcular métricas gerais: {e}")
                return None
            
            # Construir resultado final
            try:
                # Calcular tendências
                try:
                    tendencias = self._get_trends_with_logging(general_novos, general_pendentes, general_progresso, general_resolvidos, start_date, end_date)
                    if not isinstance(tendencias, dict):
                        self.logger.warning(f"Tendências inválidas: {type(tendencias)}, usando valores padrão")
                        tendencias = {"novos": "0%", "pendentes": "0%", "progresso": "0%", "resolvidos": "0%"}
                except Exception as e:
                    self.logger.error(f"Erro ao calcular tendências: {e}")
                    tendencias = {"novos": "0%", "pendentes": "0%", "progresso": "0%", "resolvidos": "0%"}
                
                result = {
                    "success": True,
                    "data": {
                        "niveis": {
                            "geral": {
                                "novos": int(general_novos),
                                "pendentes": int(general_pendentes),
                                "progresso": int(general_progresso),
                                "resolvidos": int(general_resolvidos),
                                "total": int(general_total)
                            },
                            "n1": level_metrics["n1"],
                            "n2": level_metrics["n2"],
                            "n3": level_metrics["n3"],
                            "n4": level_metrics["n4"]
                        },
                        "tendencias": tendencias,
                        "filtros_aplicados": {
                            "data_inicio": start_date,
                            "data_fim": end_date
                        }
                    },
                    "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "tempo_execucao": round(time.time() - start_time, 2)
                }
                
                # Validar resultado final
                if not isinstance(result.get("data"), dict):
                    self.logger.error("Resultado final inválido: data não é dict")
                    return None
                
                self.logger.info(f"Métricas formatadas com filtro de data: sucesso=True, tempo={result['tempo_execucao']}s")
                
            except Exception as e:
                self.logger.error(f"Erro ao construir resultado final: {e}")
                return None
            
            # Salvar no cache com TTL de 3 minutos
            try:
                self._set_cache_data('dashboard_metrics_filtered', result, ttl=180, sub_key=cache_key)
                self.logger.info(f"Resultado salvo no cache com chave: {cache_key}")
            except Exception as e:
                self.logger.warning(f"Erro ao salvar no cache: {e}")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Erro geral em get_dashboard_metrics_with_date_filter após {execution_time:.2f}s: {e}")
            import traceback
            self.logger.error(f"Stack trace: {traceback.format_exc()}")
            return None
    
    def _get_trends_with_logging(self, general_novos: int, general_pendentes: int, general_progresso: int, general_resolvidos: int, start_date: str, end_date: str) -> dict:
        """Função auxiliar para fazer log e chamar _calculate_trends"""
        self.logger.info(f"Chamando _calculate_trends com start_date={start_date}, end_date={end_date}")
        return self._calculate_trends(general_novos, general_pendentes, general_progresso, general_resolvidos, start_date, end_date)
    
    def _calculate_trends(self, current_novos: int, current_pendentes: int, current_progresso: int, current_resolvidos: int, current_start_date: Optional[str] = None, current_end_date: Optional[str] = None) -> dict:
        """Calcula as tendências comparando dados atuais com período anterior
        
        Args:
            current_novos: Número atual de tickets novos
            current_pendentes: Número atual de tickets pendentes
            current_progresso: Número atual de tickets em progresso
            current_resolvidos: Número atual de tickets resolvidos
            current_start_date: Data inicial do período atual (opcional)
            current_end_date: Data final do período atual (opcional)
        """
        self.logger.info(f"_calculate_trends chamada com: novos={current_novos}, pendentes={current_pendentes}, progresso={current_progresso}, resolvidos={current_resolvidos}, start_date={current_start_date}, end_date={current_end_date}")
        try:
            from datetime import datetime, timedelta
            
            # Se há filtros de data aplicados, calcular período anterior baseado neles
            if current_start_date and current_end_date:
                # Calcular a duração do período atual
                current_start = datetime.strptime(current_start_date, '%Y-%m-%d')
                current_end = datetime.strptime(current_end_date, '%Y-%m-%d')
                period_duration = (current_end - current_start).days
                
                # Calcular período anterior com a mesma duração
                end_date_previous = (current_start - timedelta(days=1)).strftime('%Y-%m-%d')
                start_date_previous = (current_start - timedelta(days=period_duration + 1)).strftime('%Y-%m-%d')
                
                self.logger.info(f"Calculando tendências com filtro: período atual {current_start_date} a {current_end_date}, período anterior {start_date_previous} a {end_date_previous}")
            else:
                # Usar período padrão de 7 dias
                end_date_previous = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                start_date_previous = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
                
                self.logger.info(f"Calculando tendências sem filtro: período anterior {start_date_previous} a {end_date_previous}")
            
            # Obter métricas do período anterior
            previous_general = self._get_general_totals_internal(start_date_previous, end_date_previous)
            
            # Calcular totais do período anterior
            previous_novos = previous_general.get("Novo", 0)
            previous_pendentes = previous_general.get("Pendente", 0)
            previous_progresso = previous_general.get("Processando (atribuído)", 0) + previous_general.get("Processando (planejado)", 0)
            previous_resolvidos = previous_general.get("Solucionado", 0) + previous_general.get("Fechado", 0)
            
            self.logger.info(f"Dados período anterior: novos={previous_novos}, pendentes={previous_pendentes}, progresso={previous_progresso}, resolvidos={previous_resolvidos}")
            self.logger.info(f"Dados período atual: novos={current_novos}, pendentes={current_pendentes}, progresso={current_progresso}, resolvidos={current_resolvidos}")
            
            # Calcular percentuais de variação
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
            
            self.logger.info(f"Tendências calculadas: {trends}")
            return trends
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular tendências: {e}")
            import traceback
            self.logger.error(f"Stack trace: {traceback.format_exc()}")
            # Retornar valores padrão em caso de erro
            return {
                "novos": "0%",
                "pendentes": "0%",
                "progresso": "0%",
                "resolvidos": "0%"
            }
    
    def get_technician_ranking(self, limit: int = None) -> list:
        """Retorna ranking de técnicos por total de chamados seguindo a base de conhecimento
        
        Implementação otimizada que:
        1. Usa cache inteligente com TTL de 5 minutos
        2. Busca APENAS técnicos com perfil ID 6 (Técnico)
        3. Usa consulta direta sem iteração por todos os usuários
        4. Segue exatamente a estrutura da base de conhecimento
        """
        import datetime
        start_time = time.time()
        
        try:
            # Validações de entrada
            if limit is not None:
                if not isinstance(limit, int):
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] limit deve ser int: {type(limit)}")
                    return []
                if limit <= 0:
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] limit deve ser positivo: {limit}")
                    return []
            
            # Validar configurações essenciais
            if not hasattr(self, 'glpi_url') or not self.glpi_url:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] glpi_url não configurado")
                return []
            
            self.logger.info(f"[{datetime.datetime.now().isoformat()}] Iniciando get_technician_ranking com limit={limit}")
            
            # Verificar cache
            cache_key = 'technician_ranking'
            try:
                cached_data = self._get_cache_data(cache_key)
                if cached_data is not None:
                    self.logger.info(f"[{datetime.datetime.now().isoformat()}] Retornando ranking de técnicos do cache")
                    if limit and len(cached_data) > limit:
                        return cached_data[:limit]
                    return cached_data
            except Exception as e:
                self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Erro ao verificar cache: {e}")
            
            # Verificar autenticação
            try:
                if not self._ensure_authenticated():
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Falha na autenticação")
                    return []
            except Exception as e:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro na autenticação: {e}")
                return []
            
            # Implementação seguindo a base de conhecimento
            try:
                self.logger.info(f"[{datetime.datetime.now().isoformat()}] Chamando _get_technician_ranking_knowledge_base")
                ranking = self._get_technician_ranking_knowledge_base()
                
                if not isinstance(ranking, list):
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] ranking inválido: {type(ranking)}")
                    return []
                
                self.logger.info(f"[{datetime.datetime.now().isoformat()}] Resultado da busca: {len(ranking)} técnicos")
            except Exception as e:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro ao obter ranking: {e}")
                return []
            
            # Armazenar no cache
            try:
                if ranking:
                    self._set_cache_data(cache_key, ranking, ttl=300)
                    self.logger.info(f"[{datetime.datetime.now().isoformat()}] Dados armazenados no cache")
            except Exception as e:
                self.logger.warning(f"[{datetime.datetime.now().isoformat()}] Erro ao salvar no cache: {e}")
            
            # Aplicar limite se especificado
            try:
                if limit and len(ranking) > limit:
                    ranking = ranking[:limit]
                    self.logger.info(f"[{datetime.datetime.now().isoformat()}] Ranking limitado a {limit} técnicos")
            except Exception as e:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro ao aplicar limite: {e}")
                return []
            
            execution_time = time.time() - start_time
            self.logger.info(f"[{datetime.datetime.now().isoformat()}] Ranking obtido com sucesso em {execution_time:.2f}s: {len(ranking)} técnicos")
            return ranking
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro geral em get_technician_ranking após {execution_time:.2f}s: {e}")
            import traceback
            self.logger.error(f"Stack trace: {traceback.format_exc()}")
            return []
    
    def _discover_tech_field_id(self) -> Optional[str]:
        """Descobre dinamicamente o field ID do técnico atribuído"""
        try:
            response = self._make_authenticated_request(
                'GET',
                f"{self.glpi_url}/listSearchOptions/Ticket"
            )
            if not response:
                return None
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
    
    def _get_technician_ranking_knowledge_base(self) -> list:
        """Implementação seguindo exatamente a base de conhecimento fornecida
        
        Esta implementação:
        1. Usa consulta direta de técnicos ativos com perfil ID 6
        2. Evita iteração por todos os usuários do sistema
        3. Usa forcedisplay para trazer apenas campos necessários
        4. Segue a estrutura exata da base de conhecimento
        """
        import datetime
        start_time = time.time()
        
        try:
            # Validar configurações essenciais
            if not hasattr(self, 'glpi_url') or not self.glpi_url:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] glpi_url não configurado")
                return []
            
            self.logger.info(f"[{datetime.datetime.now().isoformat()}] Iniciando consulta otimizada de ranking de técnicos")
            
            # 1.1 Consulta de Técnicos Ativos (corrigida)
            # Primeiro, buscar usuários com perfil de técnico usando Profile_User
            profile_params = {
                "range": "0-999",
                "criteria[0][field]": "4",  # Campo Perfil na tabela Profile_User
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": "6",  # ID do perfil técnico
                "forcedisplay[0]": "2",  # ID do Profile_User
                "forcedisplay[1]": "5",  # Usuário (users_id)
                "forcedisplay[2]": "4",  # Perfil
                "forcedisplay[3]": "80"  # Entidade
            }
            
            self.logger.info(f"[{datetime.datetime.now().isoformat()}] Buscando usuários com perfil ID 6")
            
            # Buscar relação Profile_User para obter IDs dos técnicos
            try:
                response = self._make_authenticated_request(
                    'GET',
                    f"{self.glpi_url}/search/Profile_User",
                    params=profile_params
                )
                
                if not response:
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Falha ao buscar usuários com perfil de técnico")
                    return []
                
                if not response.ok:
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro HTTP ao buscar Profile_User: {response.status_code}")
                    return []
                    
            except requests.exceptions.Timeout:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Timeout ao buscar Profile_User")
                return []
            except requests.exceptions.ConnectionError:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro de conexão ao buscar Profile_User")
                return []
            except requests.exceptions.RequestException as e:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro de requisição ao buscar Profile_User: {e}")
                return []
            
            # Processar resposta
            try:
                profile_result = response.json()
                if not isinstance(profile_result, dict):
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Resposta inválida da busca de Profile_User: {type(profile_result)}")
                    return []
                    
                self.logger.info(f"[{datetime.datetime.now().isoformat()}] Resposta da busca de Profile_User recebida")
            except ValueError as e:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro ao decodificar JSON da resposta Profile_User: {e}")
                return []
            
            # A API do GLPI retorna um objeto com 'data', não uma lista direta
            if not isinstance(profile_result, dict):
                self.logger.error("Resposta inválida da busca de Profile_User")
                return []
            
            # Verificar se há dados
            total_count = profile_result.get('totalcount', 0)
            self.logger.info(f"Total de usuários com perfil ID 6: {total_count}")
            
            if total_count == 0:
                self.logger.warning("Nenhum usuário encontrado com perfil de técnico")
                return []
            
            # Extrair dados dos usuários
            profile_data = profile_result.get('data', [])
            if not profile_data:
                self.logger.error("Dados de Profile_User não encontrados na resposta")
                return []
            
            # Extrair IDs dos usuários
            tech_user_ids = []
            for profile_user in profile_data:
                if isinstance(profile_user, dict) and "5" in profile_user:  # Campo Usuário (users_id)
                    # O campo 5 pode retornar o nome do usuário, precisamos extrair o ID
                    user_info = profile_user["5"]
                    # Se for um string, pode ser o nome do usuário, precisamos buscar o ID
                    # Por enquanto, vamos tentar extrair o ID do campo 2 (ID do Profile_User)
                    if "2" in profile_user:
                        # Vamos usar uma abordagem diferente: buscar diretamente os usuários
                        # por enquanto, vamos pular esta extração e usar uma busca direta
                        pass
            
            # Como a extração do users_id é complexa, vamos usar uma abordagem alternativa
            # Buscar diretamente os usuários com perfil de técnico
            self.logger.info("Usando abordagem alternativa: busca direta de usuários")
            
            # Buscar usuários ativos (removendo filtro is_deleted por enquanto para testar)
            user_params = {
                'range': '0-999',
                'criteria[0][field]': '8',  # Campo is_active
                'criteria[0][searchtype]': 'equals',
                'criteria[0][value]': '1',
                'forcedisplay[0]': '2',  # ID
                'forcedisplay[1]': '1',  # Nome de usuário
                'forcedisplay[2]': '9',  # Primeiro nome (realname)
                'forcedisplay[3]': '34'  # Sobrenome (firstname)
            }
            
            # Log para arquivo para debug
            with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now()} - Iniciando busca de usuários ativos com parâmetros: {user_params}\n")
                f.flush()
            
            try:
                user_response = self._make_authenticated_request(
                    'GET',
                    f"{self.glpi_url}/search/User",
                    params=user_params
                )
            except requests.exceptions.Timeout:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Timeout na busca de usuários ativos")
                return []
            except requests.exceptions.ConnectionError:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro de conexão na busca de usuários ativos")
                return []
            except requests.exceptions.RequestException as e:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro na requisição de usuários ativos: {e}")
                return []
            
            # Log para arquivo para debug
            with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now()} - Resposta da busca de usuários: {user_response is not None}\n")
                if user_response:
                    f.write(f"Status code: {user_response.status_code}\n")
                f.flush()
            
            if not user_response or not user_response.ok:
                self.logger.error(f"Falha ao buscar usuários ativos - Status: {user_response.status_code if user_response else 'None'}")
                with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.datetime.now()} - ERRO: Falha ao buscar usuários ativos\n")
                    f.flush()
                return []
            
            try:
                user_result = user_response.json()
            except ValueError as e:
                self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro ao decodificar JSON da resposta de usuários: {e}")
                return []
            
            # Log para arquivo para debug
            with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now()} - Resultado da busca de usuários: totalcount={user_result.get('totalcount', 0) if isinstance(user_result, dict) else 'N/A'}\n")
                f.flush()
            
            if not isinstance(user_result, dict) or user_result.get('totalcount', 0) == 0:
                self.logger.warning("Nenhum usuário ativo encontrado")
                with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.datetime.now()} - AVISO: Nenhum usuário ativo encontrado\n")
                    f.flush()
                return []

            all_users = user_result.get('data', [])
            self.logger.info(f"Encontrados {len(all_users)} usuários ativos")
            
            # Log para arquivo para debug
            with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now()} - Encontrados {len(all_users)} usuários ativos\n")
                f.flush()
            
            # Usar os dados já obtidos dos usuários com perfil de técnico
            # Extrair IDs dos usuários que já sabemos que têm perfil de técnico
            tech_user_ids = set()  # Usar set para evitar duplicatas
            tech_users_data = {}
            
            # Processar dados dos usuários com perfil de técnico já obtidos
            profile_users_data = profile_result.get('data', [])
            
            # Log para arquivo para debug
            with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now()} - Processando {len(profile_users_data)} registros de Profile_User\n")
                f.flush()
            
            for profile_user in profile_users_data:
                if isinstance(profile_user, dict):
                    # Log para arquivo para debug - mostrar todos os campos disponíveis
                    with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                        f.write(f"{datetime.datetime.now()} - Dados do Profile_User: {profile_user}\n")
                        f.flush()
                    
                    # O campo 5 contém o nome de usuário (username), não o ID
                    # Precisamos buscar o ID do usuário usando o username
                    if "5" in profile_user:
                        username = str(profile_user["5"])
                        # Armazenar o username para buscar o ID depois (usar set evita duplicatas)
                        tech_user_ids.add(username)
                        # Armazenar dados do usuário para uso posterior
                        tech_users_data[username] = profile_user
                        
                        # Log para arquivo para debug
                        with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                            f.write(f"{datetime.datetime.now()} - Username do técnico extraído: {username}\n")
                            f.flush()
            
            # Criar um mapa de usuários ativos para acesso rápido usando username
            active_users_map = {}
            for user in all_users:
                if isinstance(user, dict) and "1" in user:  # Campo 1 é o username
                    username = str(user["1"])
                    active_users_map[username] = user
                    
                    # Log para arquivo para debug
                    with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                        f.write(f"{datetime.datetime.now()} - Usuário ativo mapeado: {username}\n")
                        f.flush()
            
            self.logger.info(f"Encontrados {len(tech_user_ids)} usuários com perfil ID 6")
            
            if not tech_user_ids:
                self.logger.warning("Nenhum usuário encontrado com perfil de técnico")
                return []
            
            # Descobrir field ID do técnico para contagem de tickets
            tech_field_id = self._discover_tech_field_id()
            if not tech_field_id:
                self.logger.error("Falha ao descobrir field ID do técnico")
                with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.datetime.now()} - ERRO: Falha ao descobrir field ID do técnico\n")
                    f.flush()
                return []
            
            self.logger.info(f"Field ID do técnico descoberto: {tech_field_id}")
            
            # Log para arquivo para debug
            with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now()} - Field ID do técnico descoberto: {tech_field_id}\n")
                f.flush()
            
            # Processar apenas os técnicos ativos usando os mapas otimizados
            ranking = []
            tech_user_ids_list = list(tech_user_ids)  # Converter set para lista
            self.logger.info(f"Processando {len(tech_user_ids_list)} técnicos: {tech_user_ids_list[:5]}...")
            self.logger.info(f"Usuários ativos disponíveis: {len(active_users_map)} usuários")
            active_user_ids_sample = list(active_users_map.keys())[:10]
            self.logger.info(f"Amostra de IDs de usuários ativos: {active_user_ids_sample}")
            self.logger.info(f"Tipos de IDs - Técnicos: {type(tech_user_ids_list[0]) if tech_user_ids_list else 'N/A'}, Ativos: {type(active_user_ids_sample[0]) if active_user_ids_sample else 'N/A'}")
            
            # Log para arquivo para debug
            with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now()} - Iniciando filtro de técnicos ativos\n")
                f.write(f"Total de técnicos: {len(tech_user_ids_list)}\n")
                f.write(f"Total de usuários ativos: {len(active_users_map)}\n")
                f.flush()
            
            # Filtrar apenas técnicos que estão ativos e não deletados usando usernames
            active_tech_usernames = [username for username in tech_user_ids_list if username in active_users_map]
            self.logger.info(f"Encontrados {len(active_tech_usernames)} técnicos ativos e não deletados de {len(tech_user_ids_list)} total")
            
            # Log para arquivo para debug
            with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now()} - Encontrados {len(active_tech_usernames)} técnicos ativos de {len(tech_user_ids)} total\n")
                f.write(f"Técnicos ativos encontrados: {active_tech_usernames[:10]}\n")
                f.flush()
            
            if not active_tech_usernames:
                self.logger.warning("Nenhum técnico ativo e não deletado encontrado")
                with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.datetime.now()} - AVISO: Nenhum técnico ativo encontrado\n")
                    f.flush()
                return []
            
            self.logger.info(f"Processando {len(active_tech_usernames)} técnicos ativos")
            
            # Log para arquivo para debug
            with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now()} - Processando {len(active_tech_usernames)} técnicos ativos\n")
                f.flush()
            
            for username in active_tech_usernames:
                # Obter o ID do usuário dos dados ativos
                user_data_active = active_users_map.get(username)
                if not user_data_active or "2" not in user_data_active:
                    # Log para arquivo para debug
                    with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                        f.write(f"{datetime.datetime.now()} - ERRO: Dados do usuário ativo não encontrados para {username}\n")
                        f.flush()
                    continue
                
                user_id = str(user_data_active["2"])
                
                # Log para arquivo para debug
                with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.datetime.now()} - Processando técnico {username} (ID: {user_id})\n")
                    f.flush()
                
                # Buscar dados do técnico diretamente da API
                try:
                    user_response = self._make_authenticated_request(
                        'GET',
                        f"{self.glpi_url}/User/{user_id}"
                    )
                except requests.exceptions.Timeout:
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Timeout ao buscar dados do técnico {user_id}")
                    continue
                except requests.exceptions.ConnectionError:
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro de conexão ao buscar dados do técnico {user_id}")
                    continue
                except requests.exceptions.RequestException as e:
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro na requisição do técnico {user_id}: {e}")
                    continue
                
                # Log para arquivo para debug
                with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.datetime.now()} - Resposta inicial para técnico {user_id}: {type(user_response)} - {user_response is not None}\n")
                    if user_response is not None:
                        f.write(f"Status code: {user_response.status_code}\n")
                        f.write(f"Response OK: {user_response.ok}\n")
                        f.write(f"Response type: {type(user_response)}\n")
                    else:
                        f.write(f"user_response é None desde o início!\n")
                    f.flush()
                
                if not user_response or not user_response.ok:
                    with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                        if not user_response:
                            f.write(f"{datetime.datetime.now()} - ERRO: Resposta nula para técnico {user_id}\n")
                        else:
                            f.write(f"{datetime.datetime.now()} - ERRO: Status {user_response.status_code} para técnico {user_id} (usuário não encontrado ou inacessível)\n")
                        f.flush()
                    continue
                
                try:
                    user_data = user_response.json()
                    # Log do conteúdo da resposta para debug
                    with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                        f.write(f"{datetime.datetime.now()} - Conteúdo JSON para técnico {user_id}: {str(user_data)[:200]}...\n")
                        f.flush()
                except ValueError as e:
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Erro ao decodificar JSON do técnico {user_id}: {e}")
                    with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                        f.write(f"{datetime.datetime.now()} - ERRO JSON para técnico {user_id}: {e}\n")
                        f.flush()
                    continue
                
                if not user_data or not isinstance(user_data, dict):
                    self.logger.error(f"[{datetime.datetime.now().isoformat()}] Dados inválidos para técnico {user_id}: {type(user_data)}")
                    with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                        f.write(f"{datetime.datetime.now()} - ERRO: Dados vazios ou inválidos para técnico {user_id}\n")
                        f.flush()
                    continue
                    
                # Log para arquivo para debug
                with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.datetime.now()} - Dados do técnico {user_id} obtidos com sucesso\n")
                    f.flush()
                
                # user_data já foi obtido acima via user_response.json()
                if user_data:
                    user = user_data
                    try:
                        # Construir nome de exibição a partir dos dados da API
                        display_name = ""
                        if "realname" in user and "firstname" in user:  # Nome e Sobrenome
                            display_name = f"{user['firstname']} {user['realname']}"
                        elif "realname" in user:  # Apenas sobrenome
                            display_name = user["realname"]
                        elif "name" in user:  # Nome de usuário
                            display_name = user["name"]
                        elif "1" in user:  # Fallback para campo 1
                            display_name = user["1"]
                            
                        if not display_name or not display_name.strip():
                            self.logger.warning(f"Usuário {user_id} sem nome válido")
                            # Log para debug
                            with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                                f.write(f"{datetime.datetime.now()} - ERRO: Usuário {user_id} sem nome válido. Dados: {str(user)[:100]}...\n")
                                f.flush()
                            continue
                        
                        self.logger.info(f"Processando técnico: {display_name} (ID: {user_id})")
                        
                        # Contar tickets do técnico com validação
                        try:
                            total_tickets = self._count_tickets_by_technician_optimized(int(user_id), tech_field_id)
                            
                            if total_tickets is not None and isinstance(total_tickets, int) and total_tickets >= 0:
                                ranking.append({
                                    "id": str(user_id),
                                    "nome": display_name.strip(),
                                    "name": display_name.strip(),
                                    "total": total_tickets,
                                    "level": "N1"  # Temporário, será atualizado após ordenação
                                })
                                self.logger.info(f"Técnico {display_name} (ID: {user_id}): {total_tickets} tickets")
                            else:
                                self.logger.warning(f"Contagem de tickets inválida para técnico {display_name} (ID: {user_id}): {total_tickets}")
                        except Exception as count_error:
                            self.logger.error(f"Erro ao contar tickets para técnico {display_name} (ID: {user_id}): {count_error}")
                            continue
                        
                    except Exception as e:
                        self.logger.error(f"Erro ao processar usuário {user_id}: {e}")
                        continue
            
            # Validar e ordenar ranking
            if not ranking:
                self.logger.warning("Nenhum técnico encontrado para o ranking")
                return []
            
            try:
                # Ordenar por total de tickets (decrescente)
                ranking.sort(key=lambda x: x.get("total", 0), reverse=True)
                
                # Atribuir níveis baseados no mapeamento manual dos grupos
                total_count = len(ranking)
                self.logger.info(f"Atribuindo níveis para {total_count} técnicos baseado no mapeamento manual")
                
                for idx, item in enumerate(ranking):
                    try:
                        user_id = int(item['id'])
                        
                        # Usar o método _get_technician_level para determinar o nível correto
                        level = self._get_technician_level(user_id, item['total'], ranking)
                        
                        item["level"] = level
                        item["rank"] = idx + 1
                        
                        self.logger.info(f"Técnico {item['name']} (Rank {idx + 1}): {item['total']} tickets - Nível: {level}")
                    except Exception as level_error:
                        self.logger.error(f"Erro ao atribuir nível para técnico {item.get('name', 'Desconhecido')}: {level_error}")
                        # Atribuir valores padrão em caso de erro
                        item["level"] = "N1"
                        item["rank"] = idx + 1
            except Exception as sort_error:
                self.logger.error(f"Erro ao processar ranking final: {sort_error}")
                return []
            
            self.logger.info(f"=== RANKING FINALIZADO: {len(ranking)} técnicos processados ===")
            
            # Log para arquivo para debug
            with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now()} - RANKING FINALIZADO: {len(ranking)} técnicos processados\n")
                f.write(f"Ranking final: {ranking}\n")
                f.flush()
            
            return ranking
            
        except Exception as e:
            self.logger.error(f"Erro na implementação da base de conhecimento: {e}")
            import traceback
            self.logger.error(f"Stack trace: {traceback.format_exc()}")
            
            # Log para arquivo para debug
            with open('debug_technician_ranking.log', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now()} - ERRO CRÍTICO: {e}\n")
                f.write(f"Stack trace: {traceback.format_exc()}\n")
                f.flush()
            
            return []
    
    def _get_technician_level(self, user_id: int, total_tickets: int = 0, all_technicians_data: list = None) -> str:
        """Atribui nível do técnico baseado nos grupos do GLPI
        
        Mapeamento correto dos técnicos por grupos:
        - N1 (ID 89): Gabriel Andrade da Conceicao, Nicolas Fernando Muniz Nunez
        - N2 (ID 90): Alessandro Carbonera Vieira, Edson Joel dos Santos Silva, Luciano Marcelino da Silva, 
                      Jonathan Nascimento Moletta, Leonardo Trojan Repiso Riela, Thales Vinicius Paz Leite
        - N3 (ID 91): Jorge Antonio Vicente Junior, Anderson da Silva Morim de Oliveira, Miguelangelo Ferreira,
                      Silvio Godinho Valim, Pablo Hebling Guimaraes
        - N4 (ID 92): Paulo Cesar Pedo Nunes, Luciano de Araujo Silva, Wagner Mengue, 
                      Alexandre Rovinski Almoarqueg, Gabriel Silva Machado
        """
        try:
            # Validar configuração
            if not self.glpi_url:
                self.logger.error("URL do GLPI não configurada")
                return "N1"
            
            # Buscar grupos do usuário com tratamento de erros
            try:
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
                    },
                    timeout=10
                )
                
                if response and response.ok:
                    try:
                        group_data = response.json()
                        
                        if group_data and isinstance(group_data, dict) and group_data.get('data'):
                            for group_entry in group_data['data']:
                                if isinstance(group_entry, dict) and "3" in group_entry:
                                    try:
                                        group_id = int(group_entry["3"])
                                        
                                        # Verificar se o grupo corresponde aos service_levels
                                        for level, level_group_id in self.service_levels.items():
                                            if group_id == level_group_id:
                                                self.logger.info(f"Técnico {user_id} encontrado no grupo {group_id} -> {level}")
                                                return level
                                    except (ValueError, TypeError) as parse_error:
                                        self.logger.warning(f"Erro ao processar group_id para usuário {user_id}: {parse_error}")
                                        continue
                    except ValueError as json_error:
                        self.logger.error(f"Erro ao decodificar JSON da resposta de grupos para usuário {user_id}: {json_error}")
                else:
                    self.logger.warning(f"Falha na busca de grupos para usuário {user_id}: {response.status_code if response else 'Sem resposta'}")
            except requests.exceptions.Timeout:
                self.logger.error(f"Timeout na busca de grupos para usuário {user_id}")
            except requests.exceptions.ConnectionError:
                self.logger.error(f"Erro de conexão na busca de grupos para usuário {user_id}")
            except requests.exceptions.RequestException as req_error:
                self.logger.error(f"Erro na requisição de grupos para usuário {user_id}: {req_error}")
            except Exception as groups_error:
                self.logger.error(f"Erro inesperado na busca de grupos para usuário {user_id}: {groups_error}")
            
            # Se não encontrou nos grupos configurados, usar fallback baseado no nome do usuário
            # (para casos onde o técnico não está nos grupos mas está na lista fornecida)
            try:
                user_response = self._make_authenticated_request(
                    'GET',
                    f"{self.glpi_url}/User/{user_id}",
                    timeout=10
                )
                
                if user_response and user_response.ok:
                    try:
                        user_data = user_response.json()
                        
                        if user_data and isinstance(user_data, dict):
                            # Construir nome completo como no método get_technician_ranking
                            display_name = ""
                            if "realname" in user_data and "firstname" in user_data:
                                display_name = f"{user_data['firstname']} {user_data['realname']}"
                            elif "realname" in user_data:
                                display_name = user_data["realname"]
                            elif "name" in user_data:
                                display_name = user_data["name"]
                            elif "1" in user_data:
                                display_name = user_data["1"]
                            
                            if display_name and display_name.strip():
                                user_name = display_name.lower().strip()
                                
                                # Mapeamento manual baseado nos nomes exatos do GLPI
                                n1_names = ['gabriel andrade da conceicao', 'nicolas fernando muniz nunez']
                                n2_names = ['alessandro carbonera vieira', 'jonathan nascimento moletta', 'thales vinicius paz leite', 'leonardo trojan repiso riela', 'edson joel dos santos silva', 'luciano marcelino da silva']
                                n3_names = ['anderson da silva morim de oliveira', 'silvio godinho valim', 'jorge antonio vicente júnior', 'pablo hebling guimaraes', 'miguelangelo ferreira']
                                n4_names = ['gabriel silva machado', 'luciano de araujo silva', 'wagner mengue', 'paulo césar pedó nunes', 'alexandre rovinski almoarqueg']
                                
                                if user_name in n4_names:
                                    self.logger.info(f"Técnico {user_id} ({user_name}) mapeado para N4 por nome")
                                    return "N4"
                                elif user_name in n3_names:
                                    self.logger.info(f"Técnico {user_id} ({user_name}) mapeado para N3 por nome")
                                    return "N3"
                                elif user_name in n2_names:
                                    self.logger.info(f"Técnico {user_id} ({user_name}) mapeado para N2 por nome")
                                    return "N2"
                                elif user_name in n1_names:
                                    self.logger.info(f"Técnico {user_id} ({user_name}) mapeado para N1 por nome")
                                    return "N1"
                            else:
                                self.logger.warning(f"Nome de usuário vazio ou inválido para usuário {user_id}")
                        else:
                            self.logger.warning(f"Dados de usuário inválidos para usuário {user_id}")
                    except ValueError as json_error:
                        self.logger.error(f"Erro ao decodificar JSON dos dados do usuário {user_id}: {json_error}")
                else:
                    self.logger.warning(f"Falha na busca de dados do usuário {user_id}: {user_response.status_code if user_response else 'Sem resposta'}")
            except requests.exceptions.Timeout:
                self.logger.error(f"Timeout na busca de dados do usuário {user_id}")
            except requests.exceptions.ConnectionError:
                self.logger.error(f"Erro de conexão na busca de dados do usuário {user_id}")
            except requests.exceptions.RequestException as req_error:
                self.logger.error(f"Erro na requisição de dados do usuário {user_id}: {req_error}")
            except Exception as user_error:
                self.logger.error(f"Erro inesperado na busca de dados do usuário {user_id}: {user_error}")
            
            # Fallback final
            self.logger.warning(f"Técnico {user_id} não encontrado nos grupos ou mapeamento - usando N1 como padrão")
            return "N1"
                
        except Exception as e:
            self.logger.error(f"Erro ao determinar nível do técnico {user_id}: {e}")
            return "N1"  # Nível padrão em caso de erro
    
    def _get_technician_level_by_name(self, tech_name: str) -> str:
        """Determina o nível do técnico baseado apenas no nome (fallback)"""
        try:
            # Mapeamento completo atualizado de técnicos por nível
            # Gerado automaticamente em 2025-08-16 23:27:01
            n1_names = {
                'gabriel andrade da conceicao',
                'nicolas fernando muniz nunez',
                # Mapeamento legado mantido para compatibilidade
                "Jonathan Moletta", "Thales Lemos", "Leonardo Riela",
                "Luciano Silva", "Thales Leite",
                "jonathan-moletta", "thales-leite", "leonardo-riela",
                "luciano-silva"
            }
            
            n2_names = {
                'alessandro carbonera vieira',
                'edson joel dos santos silva',
                'jonathan nascimento moletta',
                'leonardo trojan repiso riela',
                'luciano marcelino da silva',
                'thales vinicius paz leite',
                # Mapeamento legado mantido para compatibilidade
                "Gabriel Conceição", "Luciano Araújo", "Alice Dutra", "Luan Medeiros",
                "gabriel-conceicao", "luciano-araujo", "alice-dutra", "luan-medeiros"
            }
            
            n3_names = {
                'anderson da silva morim de oliveira',
                'jorge antonio vicente júnior',
                'miguelangelo ferreira',
                'pablo hebling guimaraes',
                'silvio godinho valim',
                # Mapeamento legado mantido para compatibilidade
                "Gabriel Machado", "Luciano Marcelino", "Jorge Swift",
                "Anderson Morim", "Davi Freitas", "Lucas Sergio",
                "gabriel-machado", "luciano-marcelino", "jorge-swift",
                "anderson-morim", "davi-freitas", "lucas-sergio-t1"
            }
            
            n4_names = {
                'alexandre rovinski almoarqueg',
                'gabriel silva machado',
                'luciano de araujo silva',
                'paulo césar pedó nunes',
                'wagner mengue',
                # Mapeamento legado mantido para compatibilidade
                "Anderson Oliveira", "Silvio Godinho", "Edson Joel", "Paulo Pedro", 
                "Pablo Hebling", "Leonardo Riela", "Alessandro Carbonera", 
                "Miguel Angelo", "José Barros", "Nicolas Nunez", "Wagner Mengue", "Silvio Valim",
                "anderson-oliveira", "silvio-godinho", "edson-joel", "paulo-pedo", "pablo-hebling",
                "leonardo-rielaantigo", "alessandro-carbonera", "miguelangelo-old",
                "jose-barros", "nicolas-nunez", "wagner-mengue", "silvio-valim"
            }
            
            # Limpar o nome se vier no formato "Técnico nome-id"
            clean_name = tech_name
            if tech_name.startswith("Técnico "):
                clean_name = tech_name.replace("Técnico ", "").strip()
            
            # Verificar correspondência exata primeiro
            if clean_name in n4_names or tech_name in n4_names:
                self.logger.info(f"Técnico {tech_name} mapeado para N4 por nome")
                return "N4"
            elif clean_name in n3_names or tech_name in n3_names:
                self.logger.info(f"Técnico {tech_name} mapeado para N3 por nome")
                return "N3"
            elif clean_name in n2_names or tech_name in n2_names:
                self.logger.info(f"Técnico {tech_name} mapeado para N2 por nome")
                return "N2"
            elif clean_name in n1_names or tech_name in n1_names:
                self.logger.info(f"Técnico {tech_name} mapeado para N1 por nome")
                return "N1"
            
            # Fallback para correspondência parcial (case-insensitive)
            tech_name_lower = tech_name.lower()
            
            for name in n4_names:
                if name.lower() in tech_name_lower or tech_name_lower in name.lower():
                    self.logger.info(f"Técnico {tech_name} mapeado para N4 por correspondência parcial com {name}")
                    return "N4"
            
            for name in n3_names:
                if name.lower() in tech_name_lower or tech_name_lower in name.lower():
                    self.logger.info(f"Técnico {tech_name} mapeado para N3 por correspondência parcial com {name}")
                    return "N3"
            
            for name in n2_names:
                if name.lower() in tech_name_lower or tech_name_lower in name.lower():
                    self.logger.info(f"Técnico {tech_name} mapeado para N2 por correspondência parcial com {name}")
                    return "N2"
            
            for name in n1_names:
                if name.lower() in tech_name_lower or tech_name_lower in name.lower():
                    self.logger.info(f"Técnico {tech_name} mapeado para N1 por correspondência parcial com {name}")
                    return "N1"
            
            # Fallback final
            self.logger.warning(f"Técnico {tech_name} não encontrado no mapeamento por nome - usando N1 como padrão")
            return "N1"
            
        except Exception as e:
            self.logger.error(f"Erro ao determinar nível do técnico por nome {tech_name}: {e}")
            return "N1"  # Nível padrão em caso de erro
    
    def _get_technician_ranking_fallback(self) -> list:
        """Método de fallback usando a implementação original mais robusta"""
        try:
            # Validar configuração
            if not self.glpi_url:
                self.logger.error("URL do GLPI não configurada para fallback")
                return []
            
            # Usar método original como fallback
            try:
                active_techs = self._list_active_technicians_fallback()
                if not active_techs:
                    self.logger.warning("Nenhum técnico ativo encontrado no fallback")
                    return []
            except Exception as techs_error:
                self.logger.error(f"Erro ao buscar técnicos ativos no fallback: {techs_error}")
                return []
            
            try:
                tech_field_id = self._discover_tech_field_id()
                if not tech_field_id:
                    self.logger.error("ID do campo de técnico não encontrado no fallback")
                    return []
            except Exception as field_error:
                self.logger.error(f"Erro ao descobrir ID do campo de técnico no fallback: {field_error}")
                return []
            
            ranking = []
            for tech_id, tech_name in active_techs:
                try:
                    if not tech_name or not tech_name.strip():
                        self.logger.warning(f"Nome de técnico inválido para ID {tech_id}")
                        continue
                    
                    total_tickets = self._count_tickets_by_technician(tech_id, tech_field_id)
                    if total_tickets is not None and isinstance(total_tickets, int) and total_tickets >= 0:
                        ranking.append({
                            "id": str(tech_id),
                            "nome": tech_name.strip(),
                            "name": tech_name.strip(),
                            "total": total_tickets
                        })
                    else:
                        self.logger.warning(f"Contagem de tickets inválida para técnico {tech_name} (ID: {tech_id}): {total_tickets}")
                except Exception as ticket_error:
                    self.logger.error(f"Erro ao contar tickets para técnico {tech_name} (ID: {tech_id}): {ticket_error}")
                    continue
            
            if not ranking:
                self.logger.warning("Nenhum técnico válido encontrado no fallback")
                return []
            
            try:
                # Ordenar e atribuir ranks
                ranking.sort(key=lambda x: x.get("total", 0), reverse=True)
                for idx, item in enumerate(ranking, start=1):
                    item["rank"] = idx
                    # Atribuir nível usando o método existente
                    try:
                        user_id = int(item["id"])
                        level = self._get_technician_level(user_id, item["total"], ranking)
                        item["level"] = level
                    except Exception as level_error:
                        self.logger.error(f"Erro ao atribuir nível para técnico {item.get('name', 'Desconhecido')}: {level_error}")
                        item["level"] = "N1"
            except Exception as sort_error:
                self.logger.error(f"Erro ao processar ranking final no fallback: {sort_error}")
                return []
            
            self.logger.info(f"Fallback concluído com {len(ranking)} técnicos")
            return ranking
            
        except Exception as e:
            self.logger.error(f"Erro crítico no método de fallback: {e}")
            import traceback
            self.logger.error(f"Stack trace do fallback: {traceback.format_exc()}")
            return []
    
    def _list_active_technicians_fallback(self) -> list:
        """Método de fallback para listar técnicos ativos (implementação original)"""
        # Verificar cache primeiro
        cache_key = 'active_technicians'
        try:
            cached_data = self._get_cached_data(cache_key)
            if cached_data is not None:
                self.logger.info("Retornando lista de técnicos ativos do cache")
                return cached_data
        except Exception as cache_error:
            self.logger.warning(f"Erro ao verificar cache de técnicos ativos: {cache_error}")
        
        try:
            # Validar configuração
            if not self.glpi_url:
                self.logger.error("URL do GLPI não configurada para fallback")
                return []
            
            # Buscar usuários com perfil de técnico (ID 6)
            params = {
                "range": "0-9999",
                "criteria[0][field]": "profiles_id",
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": 6  # ID do perfil de técnico
            }
            
            try:
                response = self._make_authenticated_request(
                    'GET',
                    f"{self.glpi_url}/Profile_User",
                    params=params,
                    timeout=30
                )
                
                if not response or not response.ok:
                    self.logger.error(f"Falha ao buscar usuários com perfil de técnico: {response.status_code if response else 'Sem resposta'}")
                    return []
                
                try:
                    profile_users = response.json()
                    if not profile_users or not isinstance(profile_users, list):
                        self.logger.warning("Resposta inválida da busca de Profile_User")
                        return []
                except ValueError as json_error:
                    self.logger.error(f"Erro ao decodificar JSON da resposta de Profile_User: {json_error}")
                    return []
                    
            except requests.exceptions.Timeout:
                self.logger.error("Timeout na busca de usuários com perfil de técnico")
                return []
            except requests.exceptions.ConnectionError:
                self.logger.error("Erro de conexão na busca de usuários com perfil de técnico")
                return []
            except requests.exceptions.RequestException as req_error:
                self.logger.error(f"Erro na requisição de usuários com perfil de técnico: {req_error}")
                return []
            
            self.logger.info(f"Encontrados {len(profile_users)} registros de Profile_User com perfil de técnico")
            
            # Extrair IDs dos usuários com validação
            tech_user_ids = []
            for profile_user in profile_users:
                if isinstance(profile_user, dict) and "users_id" in profile_user:
                    try:
                        user_id = int(profile_user["users_id"])
                        if user_id > 0:
                            tech_user_ids.append(user_id)
                    except (ValueError, TypeError) as parse_error:
                        self.logger.warning(f"ID de usuário inválido em Profile_User: {profile_user.get('users_id', 'N/A')} - {parse_error}")
                        continue
            
            if not tech_user_ids:
                self.logger.warning("Nenhum usuário válido encontrado com perfil de técnico")
                return []
            
            # Buscar dados completos dos usuários em lotes para otimizar
            technicians = []
            batch_size = 10  # Processar em lotes de 10
            
            for i in range(0, len(tech_user_ids), batch_size):
                batch_ids = tech_user_ids[i:i + batch_size]
                self.logger.info(f"Processando lote {i//batch_size + 1}: IDs {batch_ids}")
                
                for user_id in batch_ids:
                    try:
                        user_response = self._make_authenticated_request(
                            'GET',
                            f"{self.glpi_url}/User/{user_id}",
                            timeout=10
                        )
                        
                        if user_response and user_response.ok:
                            try:
                                user_data = user_response.json()
                                
                                if not user_data or not isinstance(user_data, dict):
                                    self.logger.warning(f"Dados de usuário inválidos para ID {user_id}")
                                    continue
                                
                                # Verificar se o usuário está ativo e não deletado
                                try:
                                    is_active = user_data.get("is_active", 0)
                                    is_deleted = user_data.get("is_deleted", 1)
                                    
                                    # Validar valores
                                    if isinstance(is_active, str):
                                        is_active = int(is_active) if is_active.isdigit() else 0
                                    if isinstance(is_deleted, str):
                                        is_deleted = int(is_deleted) if is_deleted.isdigit() else 1
                                    
                                    if is_active == 1 and is_deleted == 0:
                                        # Construir nome de exibição com validação
                                        display_name = ""
                                        try:
                                            if user_data.get("realname") and user_data.get("firstname"):
                                                display_name = f"{user_data['firstname']} {user_data['realname']}"
                                            elif user_data.get("realname"):
                                                display_name = user_data["realname"]
                                            elif user_data.get("name"):
                                                display_name = user_data["name"]
                                            else:
                                                display_name = f"Usuário {user_id}"
                                            
                                            # Validar e limpar nome
                                            if display_name and isinstance(display_name, str):
                                                display_name = display_name.strip()
                                                if display_name:
                                                    technicians.append((user_id, display_name))
                                                    self.logger.info(f"Técnico ativo encontrado: {display_name} (ID: {user_id})")
                                                else:
                                                    self.logger.warning(f"Nome de exibição vazio para usuário {user_id}")
                                            else:
                                                self.logger.warning(f"Nome de exibição inválido para usuário {user_id}: {display_name}")
                                                
                                        except Exception as name_error:
                                            self.logger.error(f"Erro ao construir nome de exibição para usuário {user_id}: {name_error}")
                                            continue
                                    else:
                                        self.logger.debug(f"Usuário {user_id} não está ativo ou foi deletado (ativo: {is_active}, deletado: {is_deleted})")
                                        
                                except (ValueError, TypeError) as validation_error:
                                    self.logger.error(f"Erro ao validar status do usuário {user_id}: {validation_error}")
                                    continue
                                    
                            except ValueError as json_error:
                                self.logger.error(f"Erro ao decodificar JSON do usuário {user_id}: {json_error}")
                                continue
                        else:
                            self.logger.warning(f"Resposta inválida para usuário {user_id}: {user_response.status_code if user_response else 'Sem resposta'}")
                            
                    except requests.exceptions.Timeout:
                        self.logger.error(f"Timeout na busca do usuário {user_id}")
                        continue
                    except requests.exceptions.ConnectionError:
                        self.logger.error(f"Erro de conexão na busca do usuário {user_id}")
                        continue
                    except requests.exceptions.RequestException as req_error:
                        self.logger.error(f"Erro na requisição do usuário {user_id}: {req_error}")
                        continue
                    except Exception as user_error:
                        self.logger.error(f"Erro inesperado ao processar usuário {user_id}: {user_error}")
                        continue
            
            # Armazenar no cache com tratamento de erro
            try:
                self._set_cached_data(cache_key, technicians)
                self.logger.info(f"Lista de técnicos armazenada no cache com sucesso")
            except Exception as cache_error:
                self.logger.warning(f"Erro ao armazenar técnicos no cache: {cache_error}")
            
            self.logger.info(f"Total de técnicos ativos válidos encontrados: {len(technicians)}")
            return technicians
            
        except Exception as e:
            self.logger.error(f"Erro geral ao listar técnicos ativos (fallback): {e}")
            return []
    
    def _count_tickets_by_technician_optimized(self, tech_id: int, tech_field_id: str) -> Optional[int]:
        """Conta tickets por técnico seguindo a base de conhecimento
        
        Usa range 0-0 para retornar apenas contagem (otimizado)
        """
        try:
            # Validar parâmetros de entrada
            if not tech_id or not isinstance(tech_id, int) or tech_id <= 0:
                self.logger.error(f"ID de técnico inválido: {tech_id}")
                return None
                
            if not tech_field_id or not isinstance(tech_field_id, str):
                self.logger.error(f"ID do campo de técnico inválido: {tech_field_id}")
                return None
                
            if not self.glpi_url:
                self.logger.error("URL do GLPI não configurada para contagem de tickets")
                return None
            
            # Parâmetros seguindo a base de conhecimento
            params = {
                "criteria[0][field]": tech_field_id,  # Campo "Técnico" (field 5)
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": str(tech_id),  # Garantir que seja string
                "range": "0-0"  # Retorna apenas contagem
            }
            
            self.logger.info(f"Contando tickets para técnico {tech_id} com field {tech_field_id}")
            
            try:
                response = self._make_authenticated_request(
                    'GET',
                    f"{self.glpi_url}/search/Ticket",
                    params=params,
                    timeout=30
                )
                
                if not response:
                    self.logger.error(f"Falha na requisição para contar tickets do técnico {tech_id}")
                    return None
                    
                if not response.ok:
                    self.logger.error(f"Erro HTTP na contagem de tickets do técnico {tech_id}: {response.status_code}")
                    return None
                
            except requests.exceptions.Timeout:
                self.logger.error(f"Timeout na contagem de tickets do técnico {tech_id}")
                return None
            except requests.exceptions.ConnectionError:
                self.logger.error(f"Erro de conexão na contagem de tickets do técnico {tech_id}")
                return None
            except requests.exceptions.RequestException as req_error:
                self.logger.error(f"Erro na requisição de contagem de tickets do técnico {tech_id}: {req_error}")
                return None
            
            # Extrair total do cabeçalho Content-Range com validação
            try:
                if "Content-Range" in response.headers:
                    content_range = response.headers["Content-Range"]
                    
                    if not content_range or not isinstance(content_range, str):
                        self.logger.warning(f"Content-Range inválido para técnico {tech_id}: {content_range}")
                        return 0
                    
                    # Formato esperado: "items 0-0/total" ou "items */total"
                    if "/" in content_range:
                        total_str = content_range.split("/")[-1].strip()
                        if total_str.isdigit():
                            total = int(total_str)
                            if total >= 0:
                                self.logger.info(f"Técnico {tech_id}: {total} tickets encontrados")
                                return total
                            else:
                                self.logger.warning(f"Total de tickets negativo para técnico {tech_id}: {total}")
                                return 0
                        else:
                            self.logger.warning(f"Total de tickets não numérico para técnico {tech_id}: {total_str}")
                            return 0
                    else:
                        self.logger.warning(f"Formato de Content-Range inválido para técnico {tech_id}: {content_range}")
                        return 0
                else:
                    self.logger.warning(f"Content-Range não encontrado para técnico {tech_id}")
                    return 0
                    
            except (ValueError, IndexError, AttributeError) as parse_error:
                self.logger.error(f"Erro ao processar Content-Range para técnico {tech_id}: {parse_error}")
                return 0
            
        except Exception as e:
            self.logger.error(f"Erro geral ao contar tickets do técnico {tech_id}: {e}")
            return None
    
    def _count_tickets_by_technician(self, tech_id: int, tech_field_id: str) -> Optional[int]:
        """Método mantido para compatibilidade - redireciona para versão otimizada"""
        return self._count_tickets_by_technician_optimized(tech_id, tech_field_id)

    def close_session(self):
        """Encerra a sessão com a API do GLPI"""
        if self.session_token:
            try:
                response = self._make_authenticated_request(
                    'GET',
                    f"{self.glpi_url}/killSession"
                )
                if response:
                    self.logger.info("Sessão encerrada com sucesso")
                else:
                    self.logger.warning("Falha ao encerrar sessão, mas continuando")
            except Exception as e:
                self.logger.error(f"Erro ao encerrar sessão: {e}")
            finally:
                self.session_token = None
                self.token_created_at = None
                self.token_expires_at = None
    
    def _get_cached_data(self, cache_key: str):
        """Recupera dados do cache se ainda válidos (TTL customizável)"""
        if cache_key not in self._cache:
            return None
        
        cache_entry = self._cache[cache_key]
        if cache_entry['data'] is None or cache_entry['timestamp'] is None:
            return None
        
        # Verificar se o cache ainda é válido
        current_time = time.time()
        ttl = cache_entry.get('ttl', 300)  # TTL padrão de 5 minutos
        if current_time - cache_entry['timestamp'] > ttl:
            # Cache expirado
            cache_entry['data'] = None
            cache_entry['timestamp'] = None
            return None
        
        return cache_entry['data']
    
    def _set_cached_data(self, cache_key: str, data, ttl: int = None):
        """Armazena dados no cache com TTL customizável
        
        Args:
            cache_key: Chave do cache
            data: Dados a serem armazenados
            ttl: Time to live em segundos (usa TTL padrão do cache se None)
        """
        if cache_key in self._cache:
            self._cache[cache_key]['data'] = data
            self._cache[cache_key]['timestamp'] = time.time()
            if ttl is not None:
                self._cache[cache_key]['ttl'] = ttl
    
    def _get_user_name_by_id(self, user_id: str) -> str:
        """Busca o nome do usuário pelo ID"""
        if not user_id or user_id == 'Não informado':
            return 'Não informado'
            
        try:
            # Verificar cache primeiro
            cache_key = f'user_name_{user_id}'
            cached_name = self._get_cache_data('user_names', cache_key)
            if cached_name:
                return cached_name
                
            # Buscar usuário por ID
            response = self._make_authenticated_request(
                'GET',
                f"{self.glpi_url}/User/{user_id}"
            )
            
            if not response or not response.ok:
                self.logger.warning(f"Falha ao buscar usuário {user_id}")
                return f"Usuário {user_id}"
                
            user_data = response.json()
            
            # Construir nome de exibição
            display_name = "Usuário desconhecido"
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
            self.logger.error(f"Erro ao buscar nome do usuário {user_id}: {e}")
            return f"Usuário {user_id}"
    
    def _get_priority_name_by_id(self, priority_id: str) -> str:
        """Converte ID de prioridade do GLPI para nome legível"""
        if not priority_id:
            return 'Média'
            
        try:
            # Verificar cache primeiro
            cache_key = f'priority_name_{priority_id}'
            if self._is_cache_valid('priority_names', cache_key):
                cached_name = self._get_cache_data('priority_names', cache_key)
                if cached_name:
                    return cached_name
                
            # Mapeamento padrão de prioridades do GLPI
            priority_map = {
                '1': 'Muito Baixa',
                '2': 'Baixa', 
                '3': 'Média',
                '4': 'Alta',
                '5': 'Muito Alta',
                '6': 'Crítica'
            }
            
            priority_name = priority_map.get(str(priority_id), 'Média')
            
            # Armazenar no cache por 1 hora
            self._set_cache_data('priority_names', priority_name, 3600, cache_key)
            
            return priority_name
            
        except Exception as e:
            self.logger.error(f"Erro ao converter prioridade {priority_id}: {e}")
            return 'Média'
    
    def get_new_tickets(self, limit: int = 10) -> List[Dict[str, any]]:
        """Busca tickets com status 'novo' com detalhes completos"""
        if not self._ensure_authenticated():
            return []
            
        if not self.discover_field_ids():
            return []
        
        try:
            # Buscar ID do status 'novo' (geralmente 1)
            status_id = self.status_map.get('novos', 1)
            
            # Parâmetros para buscar tickets com status novo
            search_params = {
                "is_deleted": 0,
                "range": f"0-{limit-1}",  # Limitar resultados
                "criteria[0][field]": self.field_ids["STATUS"],
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": status_id,
                "sort": "19",  # Ordenar por data de criação (campo 19)
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
                    requester_name = self._get_user_name_by_id(str(requester_id)) if requester_id else 'Não informado'
                    
                    # Extrair ID da prioridade e converter para nome
                    priority_id = ticket_data.get('3', '3')  # Default para prioridade média (ID 3)
                    priority_name = self._get_priority_name_by_id(str(priority_id))
                    
                    # Extrair informações do ticket
                    ticket_info = {
                        'id': str(ticket_data.get('2', '')),  # ID do ticket
                        'title': ticket_data.get('1', 'Sem título'),  # Título
                        'description': ticket_data.get('21', '')[:100] + '...' if len(ticket_data.get('21', '')) > 100 else ticket_data.get('21', ''),  # Descrição truncada
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
            # Tenta autenticação para verificar conectividade completa
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
                    "message": "GLPI acessível mas falha na autenticação",
                    "response_time": response_time,
                    "token_valid": False
                }
                
        except Exception as e:
            return {
                "status": "offline",
                "message": f"Erro de conexão: {str(e)}",
                "response_time": None,
                "token_valid": False
            }
    
    def get_dashboard_metrics_with_filters(self, start_date: str = None, end_date: str = None, 
                                         status: str = None, priority: str = None, 
                                         level: str = None, technician: str = None, 
                                         category: str = None) -> Dict[str, any]:
        """Obtém métricas do dashboard com filtros avançados usando o sistema unificado"""
        start_time = time.time()
        
        try:
            if not self._ensure_authenticated():
                return ResponseFormatter.format_error_response("Falha na autenticação com GLPI", ["Erro de autenticação"])
                
            if not self.discover_field_ids():
                return ResponseFormatter.format_error_response("Falha ao descobrir IDs dos campos", ["Erro ao obter configuração"])
            
            # Combinar métricas por nível e gerais com filtros
            level_metrics = self._get_metrics_by_level_internal_hierarchy(start_date, end_date)
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
            self.logger.error(f"Erro ao obter métricas com filtros: {e}")
            return ResponseFormatter.format_error_response(f"Erro interno: {str(e)}", [str(e)])
    
    def get_technician_ranking_with_filters(self, start_date: str = None, end_date: str = None,
                                           level: str = None, limit: int = 10) -> List[Dict[str, any]]:
        """Obtém ranking de técnicos com filtros avançados"""
        if not self._ensure_authenticated():
            return []
            
        try:
            self.logger.info(f"Iniciando ranking com filtros - start_date: {start_date}, end_date: {end_date}, level: {level}, limit: {limit}")
            
            # Obter técnicos usando a mesma lógica do método original
            # Buscar usuários com perfil de técnico (ID 6)
            profile_params = {
                "range": "0-999",
                "criteria[0][field]": "4",  # Campo Perfil na tabela Profile_User
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": "6",  # ID do perfil técnico
                "forcedisplay[0]": "2",  # ID do Profile_User
                "forcedisplay[1]": "5",  # Usuário (users_id)
                "forcedisplay[2]": "4",  # Perfil
                "forcedisplay[3]": "80"  # Entidade
            }
            
            # Buscar relação Profile_User para obter IDs dos técnicos
            response = self._make_authenticated_request(
                'GET',
                f"{self.glpi_url}/search/Profile_User",
                params=profile_params
            )
            
            if not response:
                self.logger.error("Falha ao buscar usuários com perfil de técnico")
                return []
            
            profile_result = response.json()
            
            if 'data' not in profile_result or not profile_result['data']:
                self.logger.warning("Nenhum técnico encontrado")
                return []
            
            # Extrair IDs dos técnicos
            technician_ids = []
            for item in profile_result['data']:
                if '5' in item:  # Campo users_id
                    technician_ids.append(item['5'])
            
            if not technician_ids:
                self.logger.warning("Nenhum ID de técnico extraído")
                return []
            
            self.logger.info(f"Encontrados {len(technician_ids)} técnicos: {technician_ids}")
            
            ranking = []
            
            # Para cada técnico, contar tickets com filtros de data
            for tech_id in technician_ids:
                try:
                    # Obter nome do técnico de forma mais eficiente
                    tech_name = self._get_technician_name(tech_id)
                    
                    # Contar tickets com filtros de data
                    ticket_count = self._count_tickets_with_date_filter(
                        tech_id, start_date, end_date
                    )
                    
                    # Se ticket_count for None, usar 0
                    if ticket_count is None:
                        ticket_count = 0
                    
                    # Determinar o nível real do técnico
                    # Tentar converter tech_id para int, se falhar usar o método alternativo
                    try:
                        tech_id_int = int(tech_id)
                        tech_level = self._get_technician_level(tech_id_int, ticket_count)
                    except (ValueError, TypeError):
                        # Se tech_id não for numérico, usar nome para determinar nível
                        self.logger.debug(f"tech_id não numérico: {tech_id}, usando nome para determinar nível")
                        self.logger.debug(f"Nome do técnico obtido: {tech_name}")
                        tech_level = self._get_technician_level_by_name(tech_name)
                        self.logger.debug(f"Nível determinado para {tech_name}: {tech_level}")
                    
                    # Se um filtro de nível foi especificado, verificar se o técnico corresponde
                    if level and tech_level != level:
                        self.logger.debug(f"Técnico {tech_name} (nível {tech_level}) filtrado - não corresponde ao filtro {level}")
                        continue  # Pular este técnico se não corresponder ao filtro de nível
                    
                    ranking.append({
                        'id': tech_id,
                        'name': tech_name,
                        'total': ticket_count,  # Usar 'total' para compatibilidade
                        'level': tech_level,  # Usar o nível real do técnico
                        'rank': 0  # Será definido após ordenação
                    })
                        
                except Exception as e:
                    self.logger.error(f"Erro ao processar técnico {tech_id}: {e}")
                    import traceback
                    self.logger.error(f"Traceback completo: {traceback.format_exc()}")
                    continue
            
            # Ordenar por contagem de tickets (decrescente)
            ranking.sort(key=lambda x: x['total'], reverse=True)
            
            # Definir ranks
            for i, tech in enumerate(ranking):
                tech['rank'] = i + 1
            
            result = ranking[:limit]
            self.logger.info(f"Ranking com filtros concluído: {len(result)} técnicos")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao obter ranking com filtros: {e}")
            return []
    
    def get_new_tickets_with_filters(self, limit: int = 10, priority: str = None,
                                   category: str = None, technician: str = None,
                                   start_date: str = None, end_date: str = None) -> List[Dict[str, any]]:
        """Obtém tickets novos com filtros avançados de forma robusta"""
        # Validações de entrada
        try:
            # Validar limite
            if not isinstance(limit, int) or limit < 1:
                limit = 10
            limit = max(1, min(limit, 100))  # Entre 1 e 100
            
            # Validar formato das datas
            if start_date:
                try:
                    datetime.strptime(start_date, '%Y-%m-%d')
                except ValueError:
                    self.logger.warning(f"Formato de data de início inválido: {start_date}")
                    start_date = None
                    
            if end_date:
                try:
                    datetime.strptime(end_date, '%Y-%m-%d')
                except ValueError:
                    self.logger.warning(f"Formato de data de fim inválido: {end_date}")
                    end_date = None
                    
            # Validar se data de início não é posterior à data de fim
            if start_date and end_date:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                if start_dt > end_dt:
                    self.logger.warning("Data de início posterior à data de fim")
                    start_date, end_date = None, None
                    
        except Exception as e:
            self.logger.error(f"Erro na validação de parâmetros: {e}")
            return []
        
        if not self._ensure_authenticated():
            self.logger.warning("Falha na autenticação para buscar tickets novos")
            return []
            
        if not self.discover_field_ids():
            self.logger.warning("Falha ao descobrir field_ids para buscar tickets novos")
            return []
        
        try:
            
            # Construir parâmetros de busca de forma mais eficiente
            search_params = {
                "is_deleted": 0,
                "range": f"0-{limit-1}",
                "sort": "15",  # Ordenar por data de criação
                "order": "DESC",
                "criteria[0][field]": self.field_ids.get("STATUS", "12"),
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": self.status_map.get('Novo', 1)
            }
            
            criteria_index = 1
            
            # Adicionar filtros opcionais
            if priority:
                priority_id = self._get_priority_id_by_name(priority)
                if priority_id:
                    search_params.update({
                        f"criteria[{criteria_index}][link]": "AND",
                        f"criteria[{criteria_index}][field]": "3",  # Campo prioridade
                        f"criteria[{criteria_index}][searchtype]": "equals",
                        f"criteria[{criteria_index}][value]": priority_id
                    })
                    criteria_index += 1
            
            if technician:
                tech_field = self.field_ids.get("TECH", "5")
                search_params.update({
                    f"criteria[{criteria_index}][link]": "AND",
                    f"criteria[{criteria_index}][field]": tech_field,
                    f"criteria[{criteria_index}][searchtype]": "equals",
                    f"criteria[{criteria_index}][value]": technician
                })
                criteria_index += 1
            
            # Filtros de data
            if start_date:
                search_params.update({
                    f"criteria[{criteria_index}][link]": "AND",
                    f"criteria[{criteria_index}][field]": "15",  # Data de criação
                    f"criteria[{criteria_index}][searchtype]": "morethan",
                    f"criteria[{criteria_index}][value]": start_date
                })
                criteria_index += 1
                
            if end_date:
                search_params.update({
                    f"criteria[{criteria_index}][link]": "AND",
                    f"criteria[{criteria_index}][field]": "15",  # Data de criação
                    f"criteria[{criteria_index}][searchtype]": "lessthan",
                    f"criteria[{criteria_index}][value]": end_date
                })
            
            self.logger.debug(f"Buscando tickets novos com filtros: priority={priority}, technician={technician}, dates={start_date}-{end_date}")
            
            response = self._make_authenticated_request(
                'GET',
                f"{self.glpi_url}/search/Ticket",
                params=search_params,
                timeout=active_config().API_TIMEOUT
            )
            
            if not response:
                self.logger.error("Falha na comunicação com o GLPI")
                return []
                
            if not response.ok:
                self.logger.warning(f"Erro na requisição GLPI: {response.status_code} - {response.text[:200]}")
                return []
            
            try:
                data = response.json()
                if not isinstance(data, dict):
                    self.logger.warning("Resposta da API não é um objeto JSON válido")
                    return []
            except Exception as e:
                self.logger.error(f"Erro ao processar JSON da resposta: {e}")
                return []
            
            tickets = []
            
            if isinstance(data, dict) and 'data' in data and data['data']:
                for ticket_data in data['data']:
                    try:
                        # Processar dados do ticket de forma segura
                        ticket_id = str(ticket_data.get('2', ''))
                        title = ticket_data.get('1', 'Sem título')
                        description = ticket_data.get('21', '')
                        
                        # Truncar descrição se muito longa
                        if len(description) > 100:
                            description = description[:100] + '...'
                        
                        # Obter informações do solicitante
                        requester_id = ticket_data.get('4', '')
                        requester_name = 'Não informado'
                        if requester_id:
                            try:
                                requester_name = self._get_user_name_by_id(str(requester_id))
                            except Exception:
                                pass  # Manter fallback
                        
                        # Obter prioridade
                        priority_id = ticket_data.get('3', '3')
                        priority_name = self._get_priority_name_by_id(str(priority_id))
                        
                        ticket_info = {
                            'id': ticket_id,
                            'title': title,
                            'description': description,
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
                        
                    except Exception as e:
                        self.logger.warning(f"Erro ao processar ticket individual: {e}")
                        continue
            
            # Adicionar informações de filtros aplicados na resposta
            result = {
                'tickets': tickets,
                'total_found': len(tickets),
                'filters_applied': {
                    'limit': limit,
                    'priority': priority,
                    'category': category,
                    'technician': technician,
                    'start_date': start_date,
                    'end_date': end_date
                }
            }
            
            self.logger.info(f"Encontrados {len(tickets)} tickets novos com filtros aplicados")
            return tickets  # Manter compatibilidade retornando apenas os tickets
            
        except requests.exceptions.Timeout:
            self.logger.error("Timeout na requisição para buscar tickets novos")
            return []
        except requests.exceptions.ConnectionError:
            self.logger.error("Erro de conexão ao buscar tickets novos")
            return []
        except Exception as e:
            self.logger.error(f"Erro inesperado ao buscar tickets novos com filtros: {e}")
            return []
    
    def _apply_additional_filters(self, metrics: Dict, status: str = None, priority: str = None,
                                level: str = None, technician: str = None, category: str = None) -> Dict:
        """Aplica filtros adicionais às métricas"""
        # Por enquanto, retorna as métricas sem modificação
        # Implementação completa requereria consultas adicionais à API
        return metrics
    
    def _count_tickets_with_date_filter(self, tech_id: int, start_date: str = None, end_date: str = None) -> Optional[int]:
        """Conta tickets de um técnico com filtro de data de forma robusta"""
        try:
            # Descobrir field_ids se não existirem
            if not self.field_ids:
                if not self.discover_field_ids():
                    self.logger.warning("Falha ao descobrir field_ids, usando fallbacks")
                    return 0
            
            # Usar campo de técnico descoberto ou fallback
            tech_field = self.field_ids.get("TECH", "5")
            
            # Construir parâmetros de busca
            search_params = {
                "is_deleted": 0,
                "range": "0-0",  # Apenas contagem
                "criteria[0][field]": tech_field,
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": tech_id
            }
            
            criteria_index = 1
            
            # Adicionar filtros de data se fornecidos
            if start_date:
                search_params.update({
                    f"criteria[{criteria_index}][link]": "AND",
                    f"criteria[{criteria_index}][field]": "15",  # Data de criação
                    f"criteria[{criteria_index}][searchtype]": "morethan",
                    f"criteria[{criteria_index}][value]": start_date
                })
                criteria_index += 1
                
            if end_date:
                search_params.update({
                    f"criteria[{criteria_index}][link]": "AND",
                    f"criteria[{criteria_index}][field]": "15",  # Data de criação
                    f"criteria[{criteria_index}][searchtype]": "lessthan",
                    f"criteria[{criteria_index}][value]": end_date
                })
            
            self.logger.debug(f"Contando tickets para técnico {tech_id} com filtros: start={start_date}, end={end_date}")
            
            response = self._make_authenticated_request(
                'GET',
                f"{self.glpi_url}/search/Ticket",
                params=search_params
            )
            
            if not response or not response.ok:
                self.logger.warning(f"Falha na requisição para contar tickets do técnico {tech_id}")
                return 0
            
            # Extrair total do header Content-Range
            if "Content-Range" in response.headers:
                try:
                    content_range = response.headers["Content-Range"]
                    total = int(content_range.split("/")[-1])
                    self.logger.debug(f"Técnico {tech_id}: {total} tickets encontrados")
                    return total
                except (ValueError, IndexError) as e:
                    self.logger.error(f"Erro ao parsear Content-Range: {e}")
                    return 0
            
            # Fallback: tentar extrair do JSON
            try:
                result = response.json()
                if isinstance(result, dict) and 'totalcount' in result:
                    return result['totalcount']
                elif isinstance(result, dict) and 'data' in result:
                    return len(result['data'])
            except Exception as e:
                self.logger.warning(f"Erro ao processar resposta JSON: {e}")
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Erro ao contar tickets do técnico {tech_id}: {e}")
            return 0
    
    def _get_priority_id_by_name(self, priority_name: str) -> Optional[str]:
        """Converte nome de prioridade para ID do GLPI"""
        priority_reverse_map = {
            'Muito Baixa': '1',
            'Baixa': '2',
            'Média': '3',
            'Alta': '4',
            'Muito Alta': '5',
            'Crítica': '6'
        }
        return priority_reverse_map.get(priority_name)
    
    def get_dashboard_metrics_with_modification_date_filter(self, start_date: str, end_date: str) -> dict:
        """Obtém métricas do dashboard com filtro por data de modificação.
        
        Args:
            start_date: Data de início (YYYY-MM-DD)
            end_date: Data de fim (YYYY-MM-DD)
        
        Returns:
            dict: Métricas formatadas para o dashboard
        """
        import datetime
        
        # Validar parâmetros
        if not start_date or not end_date:
            return self.get_dashboard_metrics()
        
        # Criar chave de cache específica
        cache_key = f"dashboard_metrics_modification_filter_{start_date}_{end_date}"
        
        # Verificar cache
        if self._is_cache_valid(cache_key):
            cached_data = self._get_cache_data(cache_key)
            if cached_data:
                timestamp = datetime.datetime.now().isoformat()
                self.logger.info(f"[{timestamp}] Cache hit para métricas com filtro de modificação: {start_date} a {end_date}")
                return cached_data
        
        try:
            # Garantir autenticação
            if not self._ensure_authenticated():
                raise Exception("Falha na autenticação com GLPI")
            
            # Descobrir field_ids se necessário
            if not self.discover_field_ids():
                raise Exception("Falha ao descobrir field_ids")
            
            timestamp = datetime.datetime.now().isoformat()
            self.logger.info(f"[{timestamp}] Obtendo métricas com filtro de modificação: {start_date} a {end_date}")
            
            # Obter métricas por data de modificação
            totals = self._get_general_metrics_by_modification_date(start_date, end_date)
            metrics_by_level = self._get_metrics_by_level_by_modification_date(start_date, end_date)
            
            # Agregar totais por status
            total_novos = sum(level_data.get("Novo", 0) for level_data in metrics_by_level.values())
            total_pendentes = sum(level_data.get("Pendente", 0) for level_data in metrics_by_level.values())
            total_progresso = sum(
                level_data.get("Processando (atribuído)", 0) + level_data.get("Processando (planejado)", 0)
                for level_data in metrics_by_level.values()
            )
            total_resolvidos = sum(
                level_data.get("Solucionado", 0) + level_data.get("Fechado", 0)
                for level_data in metrics_by_level.values()
            )
            
            # Calcular tendências (simplificado para filtros)
            trends = {
                "novos": 0,
                "pendentes": 0,
                "progresso": 0,
                "resolvidos": 0
            }
            
            # Formatar resultado
            result = {
                "totals": {
                    "novos": total_novos,
                    "pendentes": total_pendentes,
                    "progresso": total_progresso,
                    "resolvidos": total_resolvidos
                },
                "trends": trends,
                "levels": {
                    "N1": {
                        "novos": metrics_by_level.get("N1", {}).get("Novo", 0),
                        "pendentes": metrics_by_level.get("N1", {}).get("Pendente", 0),
                        "progresso": (
                            metrics_by_level.get("N1", {}).get("Processando (atribuído)", 0) +
                            metrics_by_level.get("N1", {}).get("Processando (planejado)", 0)
                        ),
                        "resolvidos": (
                            metrics_by_level.get("N1", {}).get("Solucionado", 0) +
                            metrics_by_level.get("N1", {}).get("Fechado", 0)
                        )
                    },
                    "N2": {
                        "novos": metrics_by_level.get("N2", {}).get("Novo", 0),
                        "pendentes": metrics_by_level.get("N2", {}).get("Pendente", 0),
                        "progresso": (
                            metrics_by_level.get("N2", {}).get("Processando (atribuído)", 0) +
                            metrics_by_level.get("N2", {}).get("Processando (planejado)", 0)
                        ),
                        "resolvidos": (
                            metrics_by_level.get("N2", {}).get("Solucionado", 0) +
                            metrics_by_level.get("N2", {}).get("Fechado", 0)
                        )
                    },
                    "N3": {
                        "novos": metrics_by_level.get("N3", {}).get("Novo", 0),
                        "pendentes": metrics_by_level.get("N3", {}).get("Pendente", 0),
                        "progresso": (
                            metrics_by_level.get("N3", {}).get("Processando (atribuído)", 0) +
                            metrics_by_level.get("N3", {}).get("Processando (planejado)", 0)
                        ),
                        "resolvidos": (
                            metrics_by_level.get("N3", {}).get("Solucionado", 0) +
                            metrics_by_level.get("N3", {}).get("Fechado", 0)
                        )
                    },
                    "N4": {
                        "novos": metrics_by_level.get("N4", {}).get("Novo", 0),
                        "pendentes": metrics_by_level.get("N4", {}).get("Pendente", 0),
                        "progresso": (
                            metrics_by_level.get("N4", {}).get("Processando (atribuído)", 0) +
                            metrics_by_level.get("N4", {}).get("Processando (planejado)", 0)
                        ),
                        "resolvidos": (
                            metrics_by_level.get("N4", {}).get("Solucionado", 0) +
                            metrics_by_level.get("N4", {}).get("Fechado", 0)
                        )
                    }
                },
                "filter_info": {
                    "type": "modification",
                    "start_date": start_date,
                    "end_date": end_date,
                    "description": "Tickets modificados no período (inclui mudanças de status)"
                }
            }
            
            # Salvar no cache
            self._set_cache_data(cache_key, result, ttl_minutes=3)
            
            timestamp = datetime.datetime.now().isoformat()
            self.logger.info(f"[{timestamp}] Métricas obtidas com sucesso - Filtro modificação, Total: {sum(result['totals'].values())}")
            
            return result
            
        except Exception as e:
            timestamp = datetime.datetime.now().isoformat()
            self.logger.error(f"[{timestamp}] Erro ao obter métricas com filtro de modificação: {e}")
            # Retornar métricas sem filtro em caso de erro
            return self.get_dashboard_metrics()
    
    def _get_general_metrics_by_modification_date(self, start_date: str, end_date: str) -> dict:
        """Obtém métricas gerais filtradas por data de modificação."""
        totals = {}
        
        for status_name, status_id in self.status_map.items():
            search_params = {
                "is_deleted": 0,
                "range": "0-0",
                "criteria[0][field]": "12",  # Status
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": str(status_id),
                "criteria[1][link]": "AND",
                "criteria[1][field]": "19",  # Data de modificação
                "criteria[1][searchtype]": "morethan",
                "criteria[1][value]": start_date,
                "criteria[2][link]": "AND",
                "criteria[2][field]": "19",
                "criteria[2][searchtype]": "lessthan",
                "criteria[2][value]": end_date
            }
            
            response = self._make_authenticated_request(
                'GET',
                f"{self.glpi_url}/search/Ticket",
                params=search_params
            )
            
            if response and response.status_code in [200, 206]:
                if "Content-Range" in response.headers:
                    count = int(response.headers["Content-Range"].split("/")[-1])
                    totals[status_name] = count
                else:
                    totals[status_name] = 0
            else:
                totals[status_name] = 0
        
        return totals
    
    def _get_metrics_by_level_by_modification_date(self, start_date: str, end_date: str) -> dict:
        """Obtém métricas por nível filtradas por data de modificação."""
        metrics = {}
        
        for level_name, group_id in self.service_levels.items():
            level_metrics = {}
            
            for status_name, status_id in self.status_map.items():
                search_params = {
                    "is_deleted": 0,
                    "range": "0-0",
                    "criteria[0][field]": self.field_ids["GROUP"],
                    "criteria[0][searchtype]": "equals",
                    "criteria[0][value]": str(group_id),
                    "criteria[1][link]": "AND",
                    "criteria[1][field]": "12",  # Status
                    "criteria[1][searchtype]": "equals",
                    "criteria[1][value]": str(status_id),
                    "criteria[2][link]": "AND",
                    "criteria[2][field]": "19",  # Data de modificação
                    "criteria[2][searchtype]": "morethan",
                    "criteria[2][value]": start_date,
                    "criteria[3][link]": "AND",
                    "criteria[3][field]": "19",
                    "criteria[3][searchtype]": "lessthan",
                    "criteria[3][value]": end_date
                }
                
                response = self._make_authenticated_request(
                    'GET',
                    f"{self.glpi_url}/search/Ticket",
                    params=search_params
                )
                
                if response and response.status_code in [200, 206]:
                    if "Content-Range" in response.headers:
                        count = int(response.headers["Content-Range"].split("/")[-1])
                        level_metrics[status_name] = count
                    else:
                        level_metrics[status_name] = 0
                else:
                    level_metrics[status_name] = 0
            
            metrics[level_name] = level_metrics
        
        return metrics
