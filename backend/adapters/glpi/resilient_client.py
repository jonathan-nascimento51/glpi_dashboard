# -*- coding: utf-8 -*-
"""Cliente GLPI resiliente com circuit breaker, retry e timeouts configuráveis"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from contextlib import asynccontextmanager

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from utils.metrics import get_metrics, OperationType, MetricEvent, measure_operation

from utils.structured_logger import create_glpi_logger
from config.settings import active_config


class CircuitBreakerState(Enum):
    """Estados do Circuit Breaker"""
    CLOSED = "closed"  # Funcionando normalmente
    OPEN = "open"      # Falhas detectadas, bloqueando requisições
    HALF_OPEN = "half_open"  # Testando se o serviço voltou


@dataclass
class CircuitBreakerConfig:
    """Configuração do Circuit Breaker"""
    failure_threshold: int = 5  # Número de falhas para abrir
    recovery_timeout: int = 60  # Tempo em segundos para tentar recovery
    success_threshold: int = 3  # Sucessos necessários para fechar
    timeout: float = 30.0  # Timeout por requisição


@dataclass
class RetryConfig:
    """Configuração de retry"""
    max_attempts: int = 3
    min_wait: float = 1.0
    max_wait: float = 10.0
    multiplier: float = 2.0
    jitter: bool = True


@dataclass
class GLPIClientConfig:
    """Configuração completa do cliente GLPI"""
    base_url: str
    app_token: str
    user_token: str
    circuit_breaker: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)
    session_timeout: int = 3600  # 1 hora
    pool_limits: httpx.Limits = field(default_factory=lambda: httpx.Limits(
        max_keepalive_connections=20,
        max_connections=100,
        keepalive_expiry=30.0
    ))


class CircuitBreakerError(Exception):
    """Erro quando circuit breaker está aberto"""
    pass


class SessionExpiredError(Exception):
    """Erro quando sessão GLPI expirou"""
    pass


class CircuitBreaker:
    """Implementação do Circuit Breaker pattern"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.logger = create_glpi_logger()
    
    def can_execute(self) -> bool:
        """Verifica se pode executar uma requisição"""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                self.success_count = 0
                self.logger.info("Circuit breaker mudou para HALF_OPEN")
                return True
            return False
        
        # HALF_OPEN state
        return True
    
    def record_success(self):
        """Registra uma operação bem-sucedida"""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self._reset()
        elif self.state == CircuitBreakerState.CLOSED:
            self.failure_count = 0
    
    def record_failure(self):
        """Registra uma falha"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self._trip()
        elif (
            self.state == CircuitBreakerState.CLOSED and 
            self.failure_count >= self.config.failure_threshold
        ):
            self._trip()
    
    def _should_attempt_reset(self) -> bool:
        """Verifica se deve tentar resetar o circuit breaker"""
        if not self.last_failure_time:
            return True
        
        return (time.time() - self.last_failure_time) >= self.config.recovery_timeout
    
    def _trip(self):
        """Abre o circuit breaker"""
        old_state = self.state
        self.state = CircuitBreakerState.OPEN
        self.logger.warning(
            f"Circuit breaker ABERTO após {self.failure_count} falhas"
        )
        
        # Registrar mudança de estado e falha
        metrics = get_metrics()
        metrics.record_circuit_breaker_state(OperationType.CIRCUIT_BREAKER, 'open')
        metrics.record_circuit_breaker_failure(OperationType.CIRCUIT_BREAKER)
    
    def _reset(self):
        """Fecha o circuit breaker"""
        old_state = self.state
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.logger.info("Circuit breaker FECHADO - serviço recuperado")
        
        # Registrar mudança de estado
        metrics = get_metrics()
        metrics.record_circuit_breaker_state(OperationType.CIRCUIT_BREAKER, 'closed')
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Retorna métricas do circuit breaker"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
        }


class SessionManager:
    """Gerenciador de sessão GLPI com renovação automática"""
    
    def __init__(self, config: GLPIClientConfig):
        self.config = config
        self.session_token: Optional[str] = None
        self.token_created_at: Optional[float] = None
        self.logger = create_glpi_logger()
        self._lock = asyncio.Lock()
    
    async def get_valid_token(self, client: httpx.AsyncClient) -> str:
        """Obtém um token válido, renovando se necessário"""
        metrics = get_metrics()
        
        async with self._lock:
            if self._is_token_valid():
                return self.session_token
            
            # Registrar renovação de sessão
            start_time = time.time()
            try:
                await self._authenticate(client)
                
                duration = time.time() - start_time
                event = MetricEvent(
                    operation=OperationType.SESSION_RENEWAL,
                    status='success',
                    duration_seconds=duration
                )
                metrics.record_request(event)
                
                # Atualizar contador de sessões ativas
                metrics.set_active_sessions(1)
                
                return self.session_token
                
            except Exception as e:
                duration = time.time() - start_time
                event = MetricEvent(
                    operation=OperationType.SESSION_RENEWAL,
                    status='error',
                    duration_seconds=duration,
                    error_type=type(e).__name__
                )
                metrics.record_request(event)
                
                # Atualizar contador de sessões ativas
                metrics.set_active_sessions(0)
                
                raise
    
    def _is_token_valid(self) -> bool:
        """Verifica se o token atual é válido"""
        if not self.session_token or not self.token_created_at:
            return False
        
        age = time.time() - self.token_created_at
        return age < (self.config.session_timeout - 300)  # Renova 5min antes
    
    async def _authenticate(self, client: httpx.AsyncClient):
        """Autentica com o GLPI"""
        metrics = get_metrics()
        start_time = time.time()
        
        headers = {
            "Content-Type": "application/json",
            "App-Token": self.config.app_token,
            "Authorization": f"user_token {self.config.user_token}",
        }
        
        try:
            response = await client.get(
                f"{self.config.base_url}/initSession",
                headers=headers,
                timeout=self.config.circuit_breaker.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            self.session_token = data["session_token"]
            self.token_created_at = time.time()
            
            self.logger.info("Autenticação GLPI realizada com sucesso")
            
            # Registrar métrica de sucesso
            duration = time.time() - start_time
            event = MetricEvent(
                operation=OperationType.AUTHENTICATION,
                status='success',
                duration_seconds=duration
            )
            metrics.record_request(event)
            
        except Exception as e:
            self.logger.error(f"Falha na autenticação GLPI: {e}")
            
            # Registrar métrica de erro
            duration = time.time() - start_time
            event = MetricEvent(
                operation=OperationType.AUTHENTICATION,
                status='error',
                duration_seconds=duration,
                error_type=type(e).__name__
            )
            metrics.record_request(event)
            
            raise SessionExpiredError(f"Falha na autenticação: {e}")
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Retorna headers de autenticação"""
        if not self.session_token:
            raise SessionExpiredError("Token de sessão não disponível")
        
        return {
            "Session-Token": self.session_token,
            "App-Token": self.config.app_token,
        }


class GLPIResilientClient:
    """Cliente GLPI resiliente com circuit breaker, retry e métricas"""
    
    def __init__(self, config: GLPIClientConfig):
        self.config = config
        self.circuit_breaker = CircuitBreaker(config.circuit_breaker)
        self.session_manager = SessionManager(config)
        self.logger = create_glpi_logger()
        
        # Métricas
        self.metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_failed": 0,
            "circuit_breaker_trips": 0,
            "session_renewals": 0,
            "avg_response_time": 0.0,
        }
        
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Context manager entry"""
        self._client = httpx.AsyncClient(
            limits=self.config.pool_limits,
            timeout=httpx.Timeout(self.config.circuit_breaker.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self._client:
            await self._client.aclose()
    
    async def request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> httpx.Response:
        """Faz uma requisição resiliente ao GLPI"""
        metrics = get_metrics()
        
        if not self.circuit_breaker.can_execute():
            self.metrics["circuit_breaker_trips"] += 1
            
            # Registrar métrica de circuit breaker
            event = MetricEvent(
                operation=OperationType.API_REQUEST,
                status='error',
                duration_seconds=0.0,
                error_type='circuit_breaker_open'
            )
            metrics.record_request(event)
            
            raise CircuitBreakerError("Circuit breaker está aberto")
        
        # Wrapper para registrar retries
        retry_count = 0
        
        async def _make_request_with_retry():
            nonlocal retry_count
            start_time = time.time()
            self.metrics["requests_total"] += 1
            
            try:
                # Obter token válido
                token = await self.session_manager.get_valid_token(self._client)
                
                # Preparar headers
                headers = self.session_manager.get_auth_headers()
                if "headers" in kwargs:
                    headers.update(kwargs["headers"])
                kwargs["headers"] = headers
                
                # Fazer requisição
                url = f"{self.config.base_url}/{endpoint.lstrip('/')}"
                response = await self._client.request(method, url, **kwargs)
                
                # Verificar se token expirou
                if response.status_code in [401, 403]:
                    self.session_manager.session_token = None
                    self.metrics["session_renewals"] += 1
                    raise SessionExpiredError("Token expirado")
                
                response.raise_for_status()
                
                # Registrar sucesso
                self.circuit_breaker.record_success()
                self.metrics["requests_success"] += 1
                
                # Atualizar métricas de tempo
                response_time = time.time() - start_time
                self._update_avg_response_time(response_time)
                
                # Registrar métrica de sucesso
                event = MetricEvent(
                    operation=OperationType.API_REQUEST,
                    status='success',
                    duration_seconds=response_time,
                    labels={'endpoint': endpoint, 'method': method, 'retry_count': str(retry_count)}
                )
                metrics.record_request(event)
                
                return response
                
            except Exception as e:
                self.circuit_breaker.record_failure()
                self.metrics["requests_failed"] += 1
                duration = time.time() - start_time
                
                # Registrar retry se não for a primeira tentativa
                if retry_count > 0:
                    metrics.record_retry(
                        OperationType.API_REQUEST,
                        type(e).__name__,
                        duration
                    )
                
                # Registrar métrica de erro
                event = MetricEvent(
                    operation=OperationType.API_REQUEST,
                    status='error',
                    duration_seconds=duration,
                    error_type=type(e).__name__,
                    labels={'endpoint': endpoint, 'method': method, 'retry_count': str(retry_count)}
                )
                metrics.record_request(event)
                
                retry_count += 1
                self.logger.error(f"Erro na requisição {method} {endpoint} (tentativa {retry_count}): {e}")
                raise
        
        # Aplicar retry manualmente para ter controle sobre as métricas
        for attempt in range(3):
            try:
                return await _make_request_with_retry()
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                if attempt == 2:  # Última tentativa
                    raise
                
                # Calcular delay exponencial
                delay = min(10, 1 * (2 ** attempt))
                self.logger.warning(f"Tentativa {attempt + 1} falhou, tentando novamente em {delay}s")
                await asyncio.sleep(delay)
            except Exception:
                # Para outros tipos de erro, não fazer retry
                raise
    
    def _update_avg_response_time(self, response_time: float):
        """Atualiza tempo médio de resposta"""
        current_avg = self.metrics["avg_response_time"]
        total_requests = self.metrics["requests_total"]
        
        if total_requests == 1:
            self.metrics["avg_response_time"] = response_time
        else:
            # Média móvel simples
            self.metrics["avg_response_time"] = (
                (current_avg * (total_requests - 1) + response_time) / total_requests
            )
    
    async def get(self, endpoint: str, **kwargs) -> httpx.Response:
        """GET request"""
        return await self.request("GET", endpoint, **kwargs)
    
    async def post(self, endpoint: str, **kwargs) -> httpx.Response:
        """POST request"""
        return await self.request("POST", endpoint, **kwargs)
    
    async def put(self, endpoint: str, **kwargs) -> httpx.Response:
        """PUT request"""
        return await self.request("PUT", endpoint, **kwargs)
    
    async def delete(self, endpoint: str, **kwargs) -> httpx.Response:
        """DELETE request"""
        return await self.request("DELETE", endpoint, **kwargs)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do cliente"""
        return {
            **self.metrics,
            "circuit_breaker": self.circuit_breaker.metrics,
            "session_valid": self.session_manager._is_token_valid(),
        }


# Factory function para criar cliente configurado
def create_glpi_client() -> GLPIResilientClient:
    """Cria cliente GLPI com configuração padrão"""
    config = GLPIClientConfig(
        base_url=active_config.GLPI_URL,
        app_token=active_config.GLPI_APP_TOKEN,
        user_token=active_config.GLPI_USER_TOKEN,
    )
    return GLPIResilientClient(config)