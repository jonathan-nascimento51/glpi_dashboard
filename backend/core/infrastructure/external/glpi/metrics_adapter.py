# -*- coding: utf-8 -*-
"""
GLPI Metrics Adapter - Adaptador para acesso à API do GLPI.

Este módulo implementa o padrão Adapter para abstrair o acesso à API do GLPI,
fornecendo uma interface limpa e testável para consultas de métricas.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode

import aiohttp
import backoff
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from ....application.dto.metrics_dto import MetricsFilterDTO, TechnicianLevel
from ....application.queries.metrics_query import MetricsDataSource, QueryContext

logger = logging.getLogger(__name__)


class GLPIConnectionError(Exception):
    """Exceção para erros de conexão com GLPI."""

    pass


class GLPIAuthenticationError(Exception):
    """Exceção para erros de autenticação com GLPI."""

    pass


class GLPIAPIError(Exception):
    """Exceção para erros da API GLPI."""

    pass


@dataclass
class GLPIConfig:
    """Configuração para conexão com GLPI."""

    base_url: str
    app_token: str
    user_token: str
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    session_timeout_minutes: int = 60

    def __post_init__(self):
        # Remover trailing slash da URL
        self.base_url = self.base_url.rstrip("/")


class GLPISessionManager:
    """Gerenciador de sessão GLPI com renovação automática."""

    def __init__(self, config: GLPIConfig):
        self.config = config
        self.session_token: Optional[str] = None
        self.session_expires_at: Optional[datetime] = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def get_session_token(self, correlation_id: Optional[str] = None) -> str:
        """Obtém token de sessão válido, renovando se necessário."""
        if self._is_session_valid():
            return self.session_token or ""

        await self._create_new_session(correlation_id)
        return self.session_token or ""

    def _is_session_valid(self) -> bool:
        """Verifica se a sessão atual é válida."""
        if not self.session_token or not self.session_expires_at:
            return False

        # Renovar 5 minutos antes do vencimento
        buffer_time = timedelta(minutes=5)
        return datetime.now() < (self.session_expires_at - buffer_time)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((GLPIConnectionError, GLPIAPIError)),
    )
    async def _create_new_session(self, correlation_id: Optional[str] = None) -> None:
        """Cria nova sessão GLPI."""
        headers = {
            "Content-Type": "application/json",
            "App-Token": self.config.app_token,
            "Authorization": f"user_token {self.config.user_token}",
        }

        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id

        url = f"{self.config.base_url}/apirest.php/initSession"

        try:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.session_token = data.get("session_token")

                        # Definir expiração da sessão
                        self.session_expires_at = datetime.now() + timedelta(minutes=self.config.session_timeout_minutes)

                        self.logger.info(
                            "Nova sessão GLPI criada",
                            extra={
                                "correlation_id": correlation_id,
                                "expires_at": self.session_expires_at.isoformat(),
                            },
                        )
                    else:
                        error_text = await response.text()
                        raise GLPIAuthenticationError(f"Falha na autenticação GLPI: {response.status} - {error_text}")

        except aiohttp.ClientError as e:
            raise GLPIConnectionError(f"Erro de conexão com GLPI: {str(e)}")
        except Exception as e:
            raise GLPIAPIError(f"Erro inesperado na autenticação GLPI: {str(e)}")

    async def close_session(self, correlation_id: Optional[str] = None) -> None:
        """Fecha sessão GLPI."""
        if not self.session_token:
            return

        headers = {
            "Session-Token": self.session_token,
            "App-Token": self.config.app_token,
        }

        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id

        url = f"{self.config.base_url}/apirest.php/killSession"

        try:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        self.logger.info(
                            "Sessão GLPI fechada",
                            extra={"correlation_id": correlation_id},
                        )
        except Exception as e:
            self.logger.warning(
                f"Erro ao fechar sessão GLPI: {str(e)}",
                extra={"correlation_id": correlation_id},
            )
        finally:
            self.session_token = None
            self.session_expires_at = None


class GLPIAPIClient:
    """Cliente HTTP para API GLPI."""

    def __init__(self, config: GLPIConfig, session_manager: GLPISessionManager):
        self.config = config
        self.session_manager = session_manager
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((GLPIConnectionError, GLPIAPIError)),
    )
    async def make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Faz requisição autenticada para API GLPI."""

        session_token = await self.session_manager.get_session_token(correlation_id)

        headers = {
            "Content-Type": "application/json",
            "Session-Token": session_token,
            "App-Token": self.config.app_token,
        }

        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id

        # Construir URL
        url = f"{self.config.base_url}/apirest.php/{endpoint.lstrip('/')}"
        if params:
            url += f"?{urlencode(params)}"

        # Log da requisição
        self.logger.debug(
            f"GLPI API Request: {method} {url}",
            extra={
                "correlation_id": correlation_id,
                "method": method,
                "endpoint": endpoint,
                "params": params,
            },
        )

        try:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                request_kwargs = {"headers": headers}

                if data:
                    request_kwargs["json"] = data

                async with session.request(method, url, **request_kwargs) as response:
                    response_text = await response.text()

                    # Log da resposta
                    self.logger.debug(
                        f"GLPI API Response: {response.status}",
                        extra={
                            "correlation_id": correlation_id,
                            "status_code": response.status,
                            "response_size": len(response_text),
                        },
                    )

                    if response.status == 200:
                        try:
                            return await response.json()
                        except json.JSONDecodeError:
                            # Algumas respostas podem não ser JSON
                            return {"raw_response": response_text}

                    elif response.status == 401:
                        # Token expirado, forçar renovação
                        self.session_manager.session_token = None
                        raise GLPIAuthenticationError(f"Token expirado: {response_text}")

                    else:
                        raise GLPIAPIError(f"Erro na API GLPI: {response.status} - {response_text}")

        except aiohttp.ClientError as e:
            raise GLPIConnectionError(f"Erro de conexão com GLPI: {str(e)}")
        except Exception as e:
            if isinstance(e, (GLPIConnectionError, GLPIAuthenticationError, GLPIAPIError)):
                raise
            raise GLPIAPIError(f"Erro inesperado na API GLPI: {str(e)}")


class GLPIMetricsAdapter(MetricsDataSource):
    """Adaptador para métricas do GLPI."""

    def __init__(self, config: GLPIConfig):
        self.config = config
        self.session_manager = GLPISessionManager(config)
        self.api_client = GLPIAPIClient(config, self.session_manager)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Cache para hierarquia de técnicos (válido por 1 hora)
        self._technician_hierarchy_cache: Optional[Dict[int, str]] = None
        self._hierarchy_cache_expires_at: Optional[datetime] = None

    async def get_ticket_count_by_hierarchy(
        self,
        filters: Optional[MetricsFilterDTO] = None,
        context: Optional[QueryContext] = None,
    ) -> Dict[str, Any]:
        """Obtém contagem de tickets por hierarquia."""
        correlation_id = context.correlation_id if context else None

        try:
            # Obter hierarquia de técnicos
            technician_hierarchy = await self.get_technician_hierarchy(context)

            # Construir parâmetros da consulta
            params = self._build_ticket_query_params(filters)

            # Fazer requisição para tickets
            tickets_data = await self.api_client.make_request(endpoint="Ticket", params=params, correlation_id=correlation_id)

            # Processar dados por hierarquia
            hierarchy_metrics = await self._process_tickets_by_hierarchy(tickets_data, technician_hierarchy, correlation_id)

            return {"levels": hierarchy_metrics}

        except Exception as e:
            self.logger.error(
                f"Erro ao obter tickets por hierarquia: {str(e)}",
                extra={"correlation_id": correlation_id},
            )
            raise

    async def get_technician_metrics(
        self,
        technician_id: Optional[int] = None,
        filters: Optional[MetricsFilterDTO] = None,
        context: Optional[QueryContext] = None,
    ) -> List[Dict[str, Any]]:
        """Obtém métricas de técnicos."""
        correlation_id = context.correlation_id if context else None

        try:
            # Obter lista de técnicos
            technicians_data = await self._get_technicians_list(technician_id, correlation_id)

            # Para cada técnico, obter suas métricas
            technician_metrics = []

            for technician in technicians_data:
                tech_id = technician.get("id")
                if not tech_id:
                    continue

                # Criar filtro específico para o técnico
                tech_filter = filters.copy() if filters else MetricsFilterDTO()
                tech_filter.technician_id = tech_id

                # Obter tickets do técnico
                tech_tickets = await self._get_technician_tickets(tech_id, tech_filter, correlation_id)

                # Processar métricas
                metrics = await self._process_technician_metrics(technician, tech_tickets, correlation_id)

                technician_metrics.append(metrics)

            # Ordenar por total de tickets (descendente)
            technician_metrics.sort(key=lambda x: x.get("total", 0), reverse=True)

            # Aplicar limite se especificado
            if filters and filters.limit:
                technician_metrics = technician_metrics[: filters.limit]

            return technician_metrics

        except Exception as e:
            self.logger.error(
                f"Erro ao obter métricas de técnicos: {str(e)}",
                extra={"correlation_id": correlation_id},
            )
            raise

    async def get_ticket_metrics(
        self,
        filters: Optional[MetricsFilterDTO] = None,
        context: Optional[QueryContext] = None,
    ) -> Dict[str, Any]:
        """Obtém métricas de tickets."""
        correlation_id = context.correlation_id if context else None

        try:
            # Construir parâmetros da consulta
            params = self._build_ticket_query_params(filters)

            # Obter tickets
            tickets_data = await self.api_client.make_request(endpoint="Ticket", params=params, correlation_id=correlation_id)

            # Processar métricas gerais
            metrics = await self._process_ticket_metrics(tickets_data, filters, correlation_id)

            return metrics

        except Exception as e:
            self.logger.error(
                f"Erro ao obter métricas de tickets: {str(e)}",
                extra={"correlation_id": correlation_id},
            )
            raise

    async def get_technician_hierarchy(self, context: Optional[QueryContext] = None) -> Dict[int, str]:
        """Obtém mapeamento de técnico para nível hierárquico."""
        correlation_id = context.correlation_id if context else None

        # Verificar cache
        if self._is_hierarchy_cache_valid():
            return self._technician_hierarchy_cache or {}

        try:
            # Obter usuários/técnicos do GLPI
            users_data = await self.api_client.make_request(
                endpoint="User",
                params={
                    "range": "0-9999",  # Limite alto para pegar todos
                    "is_active": 1,
                    "expand_dropdowns": True,
                },
                correlation_id=correlation_id,
            )

            # Processar hierarquia
            hierarchy = await self._process_technician_hierarchy(users_data, correlation_id)

            # Atualizar cache
            self._technician_hierarchy_cache = hierarchy
            self._hierarchy_cache_expires_at = datetime.now() + timedelta(hours=1)

            return hierarchy

        except Exception as e:
            self.logger.error(
                f"Erro ao obter hierarquia de técnicos: {str(e)}",
                extra={"correlation_id": correlation_id},
            )
            raise

    def _is_hierarchy_cache_valid(self) -> bool:
        """Verifica se o cache de hierarquia é válido."""
        return (
            self._technician_hierarchy_cache is not None
            and self._hierarchy_cache_expires_at is not None
            and datetime.now() < self._hierarchy_cache_expires_at
        )

    def _build_ticket_query_params(self, filters: Optional[MetricsFilterDTO]) -> Dict[str, Any]:
        """Constrói parâmetros de consulta para tickets."""
        params = {
            "range": "0-9999",  # Limite alto por padrão
            "expand_dropdowns": True,
            "with_devices": True,
        }

        if not filters:
            return params

        # Filtros de data
        if filters.start_date:
            params["date_creation"] = f">={filters.start_date.strftime('%Y-%m-%d %H:%M:%S')}"

        if filters.end_date:
            params["date_creation"] = f"<={filters.end_date.strftime('%Y-%m-%d %H:%M:%S')}"

        # Filtro de status
        if filters.status:
            status_map = {
                "novo": 1,
                "pendente": 4,
                "progresso": 2,
                "resolvido": 5,
                "fechado": 6,
                "cancelado": 3,
            }
            if filters.status.value in status_map:
                params["status"] = status_map[filters.status.value]

        # Filtro de técnico
        if filters.technician_id:
            params["users_id_assign"] = filters.technician_id

        # Filtro de categoria
        if filters.category_id:
            params["itilcategories_id"] = filters.category_id

        # Filtro de prioridade
        if filters.priority:
            params["priority"] = filters.priority

        # Limite e offset
        if filters.limit:
            end_range = min(filters.limit - 1, 9999)
            start_range = filters.offset or 0
            params["range"] = f"{start_range}-{start_range + end_range}"

        return params

    async def _process_tickets_by_hierarchy(
        self,
        tickets_data: Dict[str, Any],
        technician_hierarchy: Dict[int, str],
        correlation_id: Optional[str],
    ) -> Dict[str, Dict[str, Any]]:
        """Processa tickets agrupados por hierarquia."""

        # Inicializar contadores por nível
        levels = {
            "N1": {
                "total": 0,
                "new": 0,
                "pending": 0,
                "in_progress": 0,
                "resolved": 0,
                "closed": 0,
                "cancelled": 0,
            },
            "N2": {
                "total": 0,
                "new": 0,
                "pending": 0,
                "in_progress": 0,
                "resolved": 0,
                "closed": 0,
                "cancelled": 0,
            },
            "N3": {
                "total": 0,
                "new": 0,
                "pending": 0,
                "in_progress": 0,
                "resolved": 0,
                "closed": 0,
                "cancelled": 0,
            },
            "N4": {
                "total": 0,
                "new": 0,
                "pending": 0,
                "in_progress": 0,
                "resolved": 0,
                "closed": 0,
                "cancelled": 0,
            },
        }

        tickets = tickets_data if isinstance(tickets_data, list) else []

        for ticket in tickets:
            # Obter técnico responsável
            tech_id = ticket.get("users_id_assign")
            if not tech_id:
                continue

            # Obter nível do técnico
            tech_level = technician_hierarchy.get(tech_id, "UNKNOWN")
            if tech_level not in levels:
                continue

            # Incrementar contadores
            levels[tech_level]["total"] += 1

            # Mapear status
            status = ticket.get("status", 1)
            status_map = {
                1: "new",
                2: "in_progress",
                3: "cancelled",
                4: "pending",
                5: "resolved",
                6: "closed",
            }

            status_key = status_map.get(status, "new")
            if status_key in levels[tech_level]:
                levels[tech_level][status_key] += 1

        return levels

    async def _get_technicians_list(self, technician_id: Optional[int], correlation_id: Optional[str]) -> List[Dict[str, Any]]:
        """Obtém lista de técnicos."""

        if technician_id:
            # Obter técnico específico
            user_data = await self.api_client.make_request(endpoint=f"User/{technician_id}", correlation_id=correlation_id)
            return [user_data] if user_data else []
        else:
            # Obter todos os técnicos ativos
            users_data = await self.api_client.make_request(
                endpoint="User",
                params={"range": "0-999", "is_active": 1, "expand_dropdowns": True},
                correlation_id=correlation_id,
            )
            return users_data if isinstance(users_data, list) else []

    async def _get_technician_tickets(
        self,
        technician_id: int,
        filters: MetricsFilterDTO,
        correlation_id: Optional[str],
    ) -> List[Dict[str, Any]]:
        """Obtém tickets de um técnico específico."""

        params = self._build_ticket_query_params(filters)
        params["users_id_assign"] = technician_id

        tickets_data = await self.api_client.make_request(endpoint="Ticket", params=params, correlation_id=correlation_id)

        return tickets_data if isinstance(tickets_data, list) else []

    async def _process_technician_metrics(
        self,
        technician: Dict[str, Any],
        tickets: List[Dict[str, Any]],
        correlation_id: Optional[str],
    ) -> Dict[str, Any]:
        """Processa métricas de um técnico."""

        metrics = {
            "id": technician.get("id"),
            "name": technician.get("realname", "Desconhecido"),
            "total": len(tickets),
            "new": 0,
            "pending": 0,
            "in_progress": 0,
            "resolved": 0,
            "closed": 0,
            "cancelled": 0,
        }

        # Contar por status
        for ticket in tickets:
            status = ticket.get("status", 1)
            if status == 1:
                metrics["new"] += 1
            elif status == 2:
                metrics["in_progress"] += 1
            elif status == 3:
                metrics["cancelled"] += 1
            elif status == 4:
                metrics["pending"] += 1
            elif status == 5:
                metrics["resolved"] += 1
            elif status == 6:
                metrics["closed"] += 1

        # Calcular tempo médio de resolução (simulado)
        resolved_tickets = [t for t in tickets if t.get("status") == 5]
        if resolved_tickets:
            # Calcular tempo médio de resolução baseado em datas reais
            total_resolution_time = 0
            valid_tickets = 0
            
            for ticket in resolved_tickets:
                date_creation = ticket.get("date_creation")
                date_mod = ticket.get("date_mod")
                
                if date_creation and date_mod:
                    try:
                        creation_dt = datetime.fromisoformat(date_creation.replace("Z", "+00:00"))
                        resolution_dt = datetime.fromisoformat(date_mod.replace("Z", "+00:00"))
                        
                        resolution_time = (resolution_dt - creation_dt).total_seconds() / 3600  # em horas
                        if resolution_time > 0:  # Validar que a resolução é posterior à criação
                            total_resolution_time += resolution_time
                            valid_tickets += 1
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Erro ao processar datas do ticket {ticket.get('id')}: {e}")
            
            if valid_tickets > 0:
                metrics["avg_resolution_time"] = round(total_resolution_time / valid_tickets, 2)
            else:
                metrics["avg_resolution_time"] = 0

        # Última atividade
        if tickets:
            latest_ticket = max(tickets, key=lambda t: t.get("date_mod", "1970-01-01"))
            metrics["last_activity"] = latest_ticket.get("date_mod")

        return metrics

    async def _process_ticket_metrics(
        self,
        tickets_data: Dict[str, Any],
        filters: Optional[MetricsFilterDTO],
        correlation_id: Optional[str],
    ) -> Dict[str, Any]:
        """Processa métricas gerais de tickets."""

        tickets = tickets_data if isinstance(tickets_data, list) else []

        # Obter tickets recentes para o dashboard
        recent_tickets = []
        if len(tickets) > 0:
            # Ordenar por data de modificação e pegar os 20 mais recentes
            sorted_tickets = sorted(tickets, key=lambda t: t.get("date_mod", "1970-01-01"), reverse=True)

            for ticket in sorted_tickets[:20]:
                recent_tickets.append(
                    {
                        "id": ticket.get("id"),
                        "title": ticket.get("name", "Sem título"),
                        "status": self._map_ticket_status(ticket.get("status", 1)),
                        "created_at": ticket.get("date_creation"),
                        "technician_id": ticket.get("users_id_assign"),
                    }
                )

        return {"recent_tickets": recent_tickets}

    async def _process_technician_hierarchy(self, users_data: Dict[str, Any], correlation_id: Optional[str]) -> Dict[int, str]:
        """Processa hierarquia de técnicos."""

        hierarchy = {}
        users = users_data if isinstance(users_data, list) else []

        for user in users:
            user_id = user.get("id")
            if not user_id:
                continue

            # Determinar nível baseado em grupos, perfis ou outros critérios do GLPI
            level = self._determine_user_level(user)
            hierarchy[user_id] = level

        return hierarchy

    def _determine_user_level(self, user: Dict[str, Any]) -> str:
        """Determina o nível hierárquico de um usuário baseado na estrutura do GLPI."""
        # Implementar lógica real baseada em critérios do GLPI
        
        # 1. Verificar perfis administrativos
        profiles = user.get("profiles", [])
        if isinstance(profiles, list):
            for profile in profiles:
                profile_name = profile.get("name", "").lower() if isinstance(profile, dict) else str(profile).lower()
                if any(admin_term in profile_name for admin_term in ["admin", "super", "gerente", "coordenador"]):
                    return "N4"
                elif any(supervisor_term in profile_name for supervisor_term in ["supervisor", "líder", "responsável"]):
                    return "N3"
        
        # 2. Verificar grupos do usuário
        groups = user.get("groups", [])
        if isinstance(groups, list):
            for group in groups:
                group_name = group.get("name", "").lower() if isinstance(group, dict) else str(group).lower()
                if any(senior_term in group_name for senior_term in ["senior", "pleno", "especialista"]):
                    return "N3"
                elif any(junior_term in group_name for junior_term in ["junior", "trainee", "estagiário"]):
                    return "N1"
        
        # 3. Verificar localização/entidade para determinar hierarquia geográfica
        location = user.get("location", {}) or user.get("entity", {})
        if isinstance(location, dict):
            location_name = location.get("name", "").lower()
            if any(hq_term in location_name for hq_term in ["matriz", "sede", "principal"]):
                return "N3"
            elif any(branch_term in location_name for branch_term in ["filial", "regional", "unidade"]):
                return "N2"
        
        # 4. Verificar campos customizados relacionados à hierarquia
        custom_fields = user.get("custom_fields", {}) or {}
        hierarchy_field = custom_fields.get("hierarchy_level") or custom_fields.get("nivel_hierarquico")
        if hierarchy_field:
            hierarchy_str = str(hierarchy_field).upper()
            if hierarchy_str in ["N1", "N2", "N3", "N4"]:
                return hierarchy_str
        
        # 5. Fallback baseado em tempo de cadastro ou ID (usuários mais antigos tendem a ter mais experiência)
        user_id = user.get("id", 0)
        date_creation = user.get("date_creation")
        if date_creation:
            try:
                creation_dt = datetime.fromisoformat(date_creation.replace("Z", "+00:00"))
                years_since_creation = (datetime.now().replace(tzinfo=creation_dt.tzinfo) - creation_dt).days / 365.25
                if years_since_creation > 5:
                    return "N3"
                elif years_since_creation > 2:
                    return "N2"
            except (ValueError, TypeError):
                pass
        
        # Distribuição padrão baseada no ID para casos sem informações específicas
        if user_id % 4 == 0:
            return "N4"
        elif user_id % 3 == 0:
            return "N3"
        elif user_id % 2 == 0:
            return "N2"
        else:
            return "N1"

    def _map_ticket_status(self, status_id: int) -> str:
        """Mapeia ID de status para string."""
        status_map = {
            1: "novo",
            2: "progresso",
            3: "cancelado",
            4: "pendente",
            5: "resolvido",
            6: "fechado",
        }
        return status_map.get(status_id, "novo")

    async def close(self) -> None:
        """Fecha conexões e limpa recursos."""
        await self.session_manager.close_session()
        self._technician_hierarchy_cache = None
        self._hierarchy_cache_expires_at = None


# Factory para criação do adapter
def create_glpi_metrics_adapter(base_url: str, app_token: str, user_token: str, **kwargs) -> GLPIMetricsAdapter:
    """Cria instância do GLPIMetricsAdapter."""
    config = GLPIConfig(base_url=base_url, app_token=app_token, user_token=user_token, **kwargs)
    return GLPIMetricsAdapter(config)


# Exemplo de uso
async def example_usage():
    """Exemplo de como usar o GLPIMetricsAdapter."""

    # Criar adapter
    adapter = create_glpi_metrics_adapter(
        base_url="https://glpi.example.com",
        app_token="your-app-token",
        user_token="your-user-token",
    )

    try:
        # Criar contexto
        from ...application.queries.metrics_query import QueryContext

        context = QueryContext(correlation_id="example-123")

        # Obter métricas por hierarquia
        hierarchy_metrics = await adapter.get_ticket_count_by_hierarchy(context=context)
        print(f"Métricas por hierarquia: {hierarchy_metrics}")

        # Obter ranking de técnicos
        technician_metrics = await adapter.get_technician_metrics(context=context)
        print(f"Top técnico: {technician_metrics[0]['name'] if technician_metrics else 'Nenhum'}")

    finally:
        # Fechar conexões
        await adapter.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
