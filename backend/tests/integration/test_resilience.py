# -*- coding: utf-8 -*-
"""Testes de integração para resiliência do cliente GLPI"""

import pytest
import asyncio
from unittest.mock import patch
from datetime import datetime, timedelta
import json
from typing import Dict, Any

from adapters.glpi.resilient_client import (
    GLPIResilientClient, CircuitBreakerError, GLPIClientConfig, RetryConfig, CircuitBreakerConfig
)
from adapters.glpi.pagination import (
    ServiceLevel, PaginationParams
)
from usecases.aggregated_metrics import AggregatedMetricsUseCase


class MockHTTPResponse:
    """Mock para resposta HTTP"""
    
    def __init__(self, status_code: int, json_data: Dict[str, Any] = None, headers: Dict[str, str] = None):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.headers = headers or {}
        self.text = json.dumps(self._json_data)
    
    async def json(self):
        return self._json_data
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


class MockSession:
    """Mock para sessão HTTP"""
    
    def __init__(self):
        self.responses = []
        self.call_count = 0
        self.request_history = []
    
    def add_response(self, status_code: int, json_data: Dict[str, Any] = None, headers: Dict[str, str] = None):
        """Adiciona resposta mockada"""
        self.responses.append(MockHTTPResponse(status_code, json_data, headers))
    
    async def request(self, method: str, url: str, **kwargs):
        """Mock do método request"""
        self.request_history.append({
            'method': method,
            'url': url,
            'kwargs': kwargs
        })
        
        if self.call_count < len(self.responses):
            response = self.responses[self.call_count]
        else:
            # Resposta padrão se não houver mais respostas configuradas
            response = MockHTTPResponse(200, {'success': True})
        
        self.call_count += 1
        return response
    
    async def get(self, url: str, **kwargs):
        return await self.request('GET', url, **kwargs)
    
    async def post(self, url: str, **kwargs):
        return await self.request('POST', url, **kwargs)
    
    async def delete(self, url: str, **kwargs):
        return await self.request('DELETE', url, **kwargs)
    
    async def close(self):
        pass
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


@pytest.fixture
def mock_session():
    """Fixture para sessão mockada"""
    return MockSession()


@pytest.fixture
def glpi_config():
    """Configuração do cliente GLPI para testes"""
    return GLPIClientConfig(
        base_url="http://test-glpi.local",
        app_token="test_app_token",
        user_token="test_user_token",
        retry_config=RetryConfig(
            max_attempts=3,
            min_wait=0.1,
            max_wait=1.0,
            exponential_base=2.0
        ),
        circuit_breaker_config=CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=1.0,
            expected_exception_types=[Exception]
        ),
        session_timeout=300
    )


@pytest.fixture
def resilient_client(glpi_config, mock_session):
    """Cliente resiliente para testes"""
    with patch('aiohttp.ClientSession', return_value=mock_session):
        client = GLPIResilientClient(glpi_config)
        client._session = mock_session
        return client


class TestCircuitBreaker:
    """Testes do Circuit Breaker"""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_failures(self, resilient_client, mock_session):
        """Testa se o circuit breaker abre após falhas consecutivas"""
        # Configurar respostas de erro
        for _ in range(4):  # Mais que o threshold (3)
            mock_session.add_response(500, {'error': 'Internal Server Error'})
        
        # Primeira chamada deve funcionar (circuit fechado)
        with pytest.raises(Exception):
            await resilient_client.authenticate()
        
        # Após 3 falhas, circuit deve abrir
        with pytest.raises(CircuitBreakerError):
            await resilient_client.authenticate()
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_recovery(self, resilient_client, mock_session):
        """Testa recuperação do circuit breaker"""
        # Forçar abertura do circuit
        for _ in range(3):
            mock_session.add_response(500, {'error': 'Internal Server Error'})
            try:
                await resilient_client.authenticate()
            except Exception:
                pass
        
        # Aguardar timeout de recuperação
        await asyncio.sleep(1.1)
        
        # Adicionar resposta de sucesso
        mock_session.add_response(200, {'session_token': 'test_token'})
        
        # Deve permitir uma tentativa (half-open)
        result = await resilient_client.authenticate()
        assert result['session_token'] == 'test_token'
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_closes_after_success(self, resilient_client, mock_session):
        """Testa fechamento do circuit após sucesso"""
        # Configurar falhas seguidas de sucesso
        for _ in range(2):
            mock_session.add_response(500, {'error': 'Error'})
        mock_session.add_response(200, {'session_token': 'test_token'})
        mock_session.add_response(200, {'session_token': 'test_token'})
        
        # Primeiras tentativas falham
        for _ in range(2):
            try:
                await resilient_client.authenticate()
            except Exception:
                pass
        
        # Terceira tentativa sucede
        result = await resilient_client.authenticate()
        assert result['session_token'] == 'test_token'
        
        # Circuit deve estar fechado novamente
        result = await resilient_client.authenticate()
        assert result['session_token'] == 'test_token'


class TestRetryMechanism:
    """Testes do mecanismo de retry"""
    
    @pytest.mark.asyncio
    async def test_retry_on_transient_errors(self, resilient_client, mock_session):
        """Testa retry em erros transitórios"""
        # Configurar falhas seguidas de sucesso
        mock_session.add_response(503, {'error': 'Service Unavailable'})
        mock_session.add_response(503, {'error': 'Service Unavailable'})
        mock_session.add_response(200, {'session_token': 'test_token'})
        
        result = await resilient_client.authenticate()
        assert result['session_token'] == 'test_token'
        assert mock_session.call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_exhaustion(self, resilient_client, mock_session):
        """Testa esgotamento de tentativas de retry"""
        # Configurar apenas falhas
        for _ in range(5):
            mock_session.add_response(503, {'error': 'Service Unavailable'})
        
        with pytest.raises(Exception):
            await resilient_client.authenticate()
        
        # Deve ter tentado max_retries + 1 vezes
        assert mock_session.call_count == 4  # 1 + 3 retries
    
    @pytest.mark.asyncio
    async def test_no_retry_on_client_errors(self, resilient_client, mock_session):
        """Testa que não há retry em erros de cliente (4xx)"""
        mock_session.add_response(400, {'error': 'Bad Request'})
        
        with pytest.raises(Exception):
            await resilient_client.authenticate()
        
        # Deve ter tentado apenas uma vez
        assert mock_session.call_count == 1


class TestSessionManagement:
    """Testes de gerenciamento de sessão"""
    
    @pytest.mark.asyncio
    async def test_session_renewal_on_401(self, resilient_client, mock_session):
        """Testa renovação de sessão em erro 401"""
        # Simular sessão expirada
        resilient_client.session_manager.session_token = 'expired_token'
        
        # Configurar respostas: 401 seguido de nova autenticação e sucesso
        mock_session.add_response(401, {'error': 'Unauthorized'})
        mock_session.add_response(200, {'session_token': 'new_token'})
        mock_session.add_response(200, {'data': [{'id': 1, 'title': 'Test Ticket'}]})
        
        result = await resilient_client.search_tickets({})
        assert 'data' in result
        assert resilient_client.session_manager.session_token == 'new_token'
    
    @pytest.mark.asyncio
    async def test_session_timeout_handling(self, resilient_client):
        """Testa tratamento de timeout de sessão"""
        # Simular sessão expirada por tempo
        resilient_client.session_manager.session_token = 'test_token'
        resilient_client.session_manager.session_expires_at = datetime.now() - timedelta(minutes=1)
        
        assert resilient_client.session_manager.is_session_expired()
    
    @pytest.mark.asyncio
    async def test_concurrent_session_renewal(self, resilient_client, mock_session):
        """Testa renovação de sessão em requisições concorrentes"""
        # Configurar respostas para múltiplas tentativas
        for _ in range(3):
            mock_session.add_response(401, {'error': 'Unauthorized'})
        mock_session.add_response(200, {'session_token': 'new_token'})
        for _ in range(3):
            mock_session.add_response(200, {'data': []})
        
        # Executar múltiplas requisições concorrentes
        tasks = [
            resilient_client.search_tickets({})
            for _ in range(3)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Todas devem ter sucesso
        for result in results:
            assert not isinstance(result, Exception)
            assert 'data' in result


class TestRateLimitHandling:
    """Testes de tratamento de rate limiting"""
    
    @pytest.mark.asyncio
    async def test_rate_limit_429_handling(self, resilient_client, mock_session):
        """Testa tratamento de erro 429 (Too Many Requests)"""
        # Configurar resposta 429 com Retry-After header
        mock_session.add_response(
            429,
            {'error': 'Too Many Requests'},
            {'Retry-After': '1'}
        )
        mock_session.add_response(200, {'data': []})
        
        start_time = datetime.now()
        result = await resilient_client.search_tickets({})
        end_time = datetime.now()
        
        # Deve ter aguardado pelo menos 1 segundo
        assert (end_time - start_time).total_seconds() >= 1.0
        assert 'data' in result
    
    @pytest.mark.asyncio
    async def test_rate_limit_without_retry_after(self, resilient_client, mock_session):
        """Testa tratamento de 429 sem header Retry-After"""
        mock_session.add_response(429, {'error': 'Too Many Requests'})
        mock_session.add_response(200, {'data': []})
        
        start_time = datetime.now()
        result = await resilient_client.search_tickets({})
        end_time = datetime.now()
        
        # Deve ter aguardado o delay padrão
        assert (end_time - start_time).total_seconds() >= 0.1
        assert 'data' in result


class TestPaginationResilience:
    """Testes de resiliência em paginação longa"""
    
    @pytest.mark.asyncio
    async def test_long_pagination_with_intermittent_failures(self, resilient_client, mock_session):
        """Testa paginação longa com falhas intermitentes"""
        # Configurar respostas para múltiplas páginas com algumas falhas
        responses = [
            (200, {'data': [{'id': i} for i in range(1, 51)]}),  # Página 1
            (503, {'error': 'Service Unavailable'}),  # Falha
            (200, {'data': [{'id': i} for i in range(51, 101)]}),  # Página 2 (retry)
            (200, {'data': [{'id': i} for i in range(101, 151)]}),  # Página 3
            (500, {'error': 'Internal Server Error'}),  # Falha
            (200, {'data': [{'id': i} for i in range(151, 201)]}),  # Página 4 (retry)
            (200, {'data': []}),  # Fim da paginação
        ]
        
        for status, data in responses:
            mock_session.add_response(status, data)
        
        all_items = []
        pagination = PaginationParams(page=1, page_size=50)
        
        for page in range(1, 5):
            pagination.page = page
            try:
                result = await resilient_client.search_tickets({})
                items = result.get('data', [])
                if not items:
                    break
                all_items.extend(items)
            except Exception:
                # Em caso de falha, tentar novamente
                result = await resilient_client.search_tickets({})
                items = result.get('data', [])
                if not items:
                    break
                all_items.extend(items)
        
        # Deve ter coletado todos os itens
        assert len(all_items) == 200
    
    @pytest.mark.asyncio
    async def test_pagination_circuit_breaker_recovery(self, resilient_client, mock_session):
        """Testa recuperação do circuit breaker durante paginação"""
        # Configurar falhas para abrir o circuit
        for _ in range(3):
            mock_session.add_response(500, {'error': 'Internal Server Error'})
        
        # Tentar paginação que deve falhar
        with pytest.raises(CircuitBreakerError):
            await resilient_client.search_tickets({})
        
        # Aguardar recuperação
        await asyncio.sleep(1.1)
        
        # Configurar resposta de sucesso
        mock_session.add_response(200, {'data': [{'id': 1}]})
        
        # Deve conseguir paginar novamente
        result = await resilient_client.search_tickets({})
        assert 'data' in result


class TestAggregatedMetricsResilience:
    """Testes de resiliência para métricas agregadas"""
    
    @pytest.fixture
    def metrics_use_case(self, resilient_client):
        return AggregatedMetricsUseCase(resilient_client)
    
    @pytest.mark.asyncio
    async def test_partial_failure_in_metrics_aggregation(self, metrics_use_case, mock_session):
        """Testa falha parcial na agregação de métricas"""
        # Configurar respostas: sucesso para N1, falha para N2, sucesso para N3 e N4
        responses = [
            # N1 - sucesso
            (200, {'data': [{'id': i} for i in range(1, 11)]}),  # NOVO
            (200, {'data': [{'id': i} for i in range(11, 16)]}),  # PROCESSANDO_ATRIBUIDO
            (200, {'data': [{'id': i} for i in range(16, 21)]}),  # PROCESSANDO_PLANEJADO
            (200, {'data': [{'id': i} for i in range(21, 26)]}),  # PENDENTE
            (200, {'data': [{'id': i} for i in range(26, 31)]}),  # SOLUCIONADO
            (200, {'data': [{'id': i} for i in range(31, 36)]}),  # FECHADO
            (200, {'data': []}),  # Backlog
            
            # N2 - falhas
            (500, {'error': 'Internal Server Error'}),
            (500, {'error': 'Internal Server Error'}),
            (500, {'error': 'Internal Server Error'}),
            (500, {'error': 'Internal Server Error'}),
            (500, {'error': 'Internal Server Error'}),
            (500, {'error': 'Internal Server Error'}),
            (500, {'error': 'Internal Server Error'}),
            
            # N3 - sucesso
            (200, {'data': [{'id': i} for i in range(1, 6)]}),
            (200, {'data': [{'id': i} for i in range(6, 11)]}),
            (200, {'data': [{'id': i} for i in range(11, 16)]}),
            (200, {'data': [{'id': i} for i in range(16, 21)]}),
            (200, {'data': [{'id': i} for i in range(21, 26)]}),
            (200, {'data': [{'id': i} for i in range(26, 31)]}),
            (200, {'data': []}),
            
            # N4 - sucesso
            (200, {'data': [{'id': i} for i in range(1, 3)]}),
            (200, {'data': [{'id': i} for i in range(3, 5)]}),
            (200, {'data': [{'id': i} for i in range(5, 7)]}),
            (200, {'data': [{'id': i} for i in range(7, 9)]}),
            (200, {'data': [{'id': i} for i in range(9, 11)]}),
            (200, {'data': [{'id': i} for i in range(11, 13)]}),
            (200, {'data': []}),
        ]
        
        for status, data in responses:
            mock_session.add_response(status, data)
        
        # Obter métricas diárias
        metrics = await metrics_use_case.get_daily_metrics()
        
        # Deve ter métricas para N1, N3 e N4, mas N2 deve ter valores zerados
        assert ServiceLevel.N1 in metrics.metrics_by_level
        assert ServiceLevel.N2 in metrics.metrics_by_level
        assert ServiceLevel.N3 in metrics.metrics_by_level
        assert ServiceLevel.N4 in metrics.metrics_by_level
        
        # N1 deve ter dados
        n1_metrics = metrics.metrics_by_level[ServiceLevel.N1]
        assert n1_metrics.total_tickets > 0
        
        # N2 deve ter valores zerados devido à falha
        n2_metrics = metrics.metrics_by_level[ServiceLevel.N2]
        assert n2_metrics.total_tickets == 0
        
        # N3 e N4 devem ter dados
        n3_metrics = metrics.metrics_by_level[ServiceLevel.N3]
        n4_metrics = metrics.metrics_by_level[ServiceLevel.N4]
        assert n3_metrics.total_tickets > 0
        assert n4_metrics.total_tickets > 0
    
    @pytest.mark.asyncio
    async def test_metrics_with_circuit_breaker_recovery(self, metrics_use_case, mock_session):
        """Testa obtenção de métricas com recuperação do circuit breaker"""
        # Configurar falhas para abrir circuit
        for _ in range(3):
            mock_session.add_response(500, {'error': 'Internal Server Error'})
        
        # Primeira tentativa deve falhar
        with pytest.raises(Exception):
            await metrics_use_case.get_daily_metrics()
        
        # Aguardar recuperação
        await asyncio.sleep(1.1)
        
        # Configurar respostas de sucesso
        for _ in range(28):  # 4 níveis × 7 status cada
            mock_session.add_response(200, {'data': [{'id': 1}]})
        
        # Deve conseguir obter métricas
        metrics = await metrics_use_case.get_daily_metrics()
        assert metrics.total_metrics.total_tickets > 0


class TestErrorRecoveryScenarios:
    """Testes de cenários de recuperação de erro"""
    
    @pytest.mark.asyncio
    async def test_network_timeout_recovery(self, resilient_client, mock_session):
        """Testa recuperação de timeout de rede"""
        # Simular timeout seguido de sucesso
        mock_session.add_response(408, {'error': 'Request Timeout'})
        mock_session.add_response(200, {'data': []})
        
        result = await resilient_client.search_tickets({})
        assert 'data' in result
    
    @pytest.mark.asyncio
    async def test_server_overload_recovery(self, resilient_client, mock_session):
        """Testa recuperação de sobrecarga do servidor"""
        # Simular sobrecarga seguida de recuperação
        mock_session.add_response(503, {'error': 'Service Unavailable'})
        mock_session.add_response(503, {'error': 'Service Unavailable'})
        mock_session.add_response(200, {'data': []})
        
        result = await resilient_client.search_tickets({})
        assert 'data' in result
    
    @pytest.mark.asyncio
    async def test_database_connection_recovery(self, resilient_client, mock_session):
        """Testa recuperação de falha de conexão com banco"""
        # Simular falha de banco seguida de recuperação
        mock_session.add_response(502, {'error': 'Bad Gateway'})
        mock_session.add_response(200, {'data': []})
        
        result = await resilient_client.search_tickets({})
        assert 'data' in result


# Testes de performance e stress
class TestPerformanceResilience:
    """Testes de resiliência de performance"""
    
    @pytest.mark.asyncio
    async def test_high_concurrency_resilience(self, resilient_client, mock_session):
        """Testa resiliência com alta concorrência"""
        # Configurar muitas respostas
        for _ in range(100):
            mock_session.add_response(200, {'data': [{'id': 1}]})
        
        # Executar muitas requisições concorrentes
        tasks = [
            resilient_client.search_tickets({})
            for _ in range(50)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Todas devem ter sucesso
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        assert success_count >= 45  # Permitir algumas falhas
    
    @pytest.mark.asyncio
    async def test_memory_efficiency_long_running(self, resilient_client, mock_session):
        """Testa eficiência de memória em operações longas"""
        # Simular operação longa com muitas páginas
        for page in range(100):
            if page < 50:
                mock_session.add_response(200, {'data': [{'id': i} for i in range(page*10, (page+1)*10)]})
            else:
                mock_session.add_response(200, {'data': []})  # Fim da paginação
        
        total_items = 0
        for page in range(1, 51):
            try:
                result = await resilient_client.search_tickets({})
                items = result.get('data', [])
                if not items:
                    break
                total_items += len(items)
            except Exception:
                break
        
        assert total_items == 500


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
