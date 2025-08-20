#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes unitários para queries de métricas.

Este módulo testa execução de queries, factory functions,
mocks e tratamento de erros.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest

from backend.core.application.dto import (
    DashboardMetricsDTO,
    MetricsDTO,
    MetricsFilterDTO,
    TechnicianLevel,
    TechnicianMetricsDTO,
    TicketStatus,
)
from backend.core.application.queries import (
    BaseMetricsQuery,
    DashboardMetricsQuery,
    DataValidationError,
    GeneralMetricsQuery,
    MetricsDataSource,
    MetricsQueryFactory,
    MockMetricsDataSource,
    QueryContext,
    QueryExecutionError,
    TechnicianRankingQuery,
)


class TestQueryContext:
    """Testes para QueryContext."""

    def test_context_creation(self):
        """Testa criação de contexto."""
        context = QueryContext(user_id="user123", request_id="req456", timeout=30.0)

        assert context.user_id == "user123"
        assert context.request_id == "req456"
        assert context.timeout == 30.0
        assert isinstance(context.created_at, datetime)

    def test_context_defaults(self):
        """Testa valores padrão do contexto."""
        context = QueryContext()

        assert context.user_id is None
        assert context.request_id is not None  # UUID gerado
        assert context.timeout == 30.0
        assert context.cache_enabled is True

    def test_context_metadata(self):
        """Testa metadados do contexto."""
        metadata = {"source": "dashboard", "version": "1.0"}
        context = QueryContext(metadata=metadata)

        assert context.metadata["source"] == "dashboard"
        assert context.metadata["version"] == "1.0"

    def test_context_string_representation(self):
        """Testa representação string do contexto."""
        context = QueryContext(user_id="test", request_id="123")
        str_repr = str(context)

        assert "test" in str_repr
        assert "123" in str_repr


class TestQueryExceptions:
    """Testes para exceções de query."""

    def test_query_execution_error(self):
        """Testa QueryExecutionError."""
        context = QueryContext(request_id="test123")

        error = QueryExecutionError(
            "Falha na execução",
            context=context,
            original_error=ValueError("Erro original"),
        )

        assert str(error) == "Falha na execução"
        assert error.context.request_id == "test123"
        assert isinstance(error.original_error, ValueError)

    def test_data_validation_error(self):
        """Testa DataValidationError."""
        validation_errors = ["Campo 'total' é obrigatório", "Valor 'status' inválido"]

        error = DataValidationError("Dados inválidos", validation_errors=validation_errors)

        assert str(error) == "Dados inválidos"
        assert len(error.validation_errors) == 2
        assert "Campo 'total' é obrigatório" in error.validation_errors


class TestMockMetricsDataSource:
    """Testes para MockMetricsDataSource."""

    def test_mock_data_source_creation(self):
        """Testa criação do mock data source."""
        mock_ds = MockMetricsDataSource()

        assert mock_ds.name == "mock"
        assert mock_ds.connected is True
        assert len(mock_ds.mock_data) > 0

    @pytest.mark.asyncio
    async def test_mock_execute_query(self):
        """Testa execução de query no mock."""
        mock_ds = MockMetricsDataSource()
        context = QueryContext()

        # Query de métricas gerais
        result = await mock_ds.execute_query("SELECT COUNT(*) FROM tickets", context=context)

        assert isinstance(result, list)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_mock_get_metrics(self):
        """Testa obtenção de métricas do mock."""
        mock_ds = MockMetricsDataSource()
        filter_dto = MetricsFilterDTO()

        metrics = await mock_ds.get_metrics(filter_dto)

        assert isinstance(metrics, dict)
        assert "total" in metrics
        assert "novos" in metrics
        assert metrics["total"] >= 0

    @pytest.mark.asyncio
    async def test_mock_get_technicians(self):
        """Testa obtenção de técnicos do mock."""
        mock_ds = MockMetricsDataSource()
        filter_dto = MetricsFilterDTO(limit=5)

        technicians = await mock_ds.get_technicians(filter_dto)

        assert isinstance(technicians, list)
        assert len(technicians) <= 5

        if technicians:
            tech = technicians[0]
            assert "id" in tech
            assert "name" in tech
            assert "level" in tech

    def test_mock_add_custom_data(self):
        """Testa adição de dados customizados ao mock."""
        mock_ds = MockMetricsDataSource()

        custom_data = {"custom_metric": 42, "custom_list": [1, 2, 3]}

        mock_ds.add_mock_data("custom", custom_data)

        assert "custom" in mock_ds.mock_data
        assert mock_ds.mock_data["custom"]["custom_metric"] == 42

    @pytest.mark.asyncio
    async def test_mock_connection_simulation(self):
        """Testa simulação de conexão do mock."""
        mock_ds = MockMetricsDataSource()

        # Simular desconexão
        mock_ds.connected = False

        with pytest.raises(QueryExecutionError):
            await mock_ds.execute_query("SELECT 1", QueryContext())

        # Reconectar
        mock_ds.connected = True
        result = await mock_ds.execute_query("SELECT 1", QueryContext())
        assert result is not None


class TestBaseMetricsQuery:
    """Testes para BaseMetricsQuery."""

    def test_base_query_creation(self):
        """Testa criação de query base."""
        data_source = MockMetricsDataSource()

        query = BaseMetricsQuery(data_source=data_source)

        assert query.data_source == data_source
        assert query.cache_enabled is True
        assert query.cache_ttl == 300  # 5 minutos

    def test_base_query_validation(self):
        """Testa validação da query base."""
        data_source = MockMetricsDataSource()
        query = BaseMetricsQuery(data_source=data_source)

        # Filtro válido
        valid_filter = MetricsFilterDTO()
        context = QueryContext()

        # Não deve lançar exceção
        query._validate_input(valid_filter, context)

    def test_base_query_validation_errors(self):
        """Testa erros de validação da query base."""
        data_source = MockMetricsDataSource()
        query = BaseMetricsQuery(data_source=data_source)

        # Filtro inválido (None)
        with pytest.raises(DataValidationError):
            query._validate_input(None, QueryContext())

        # Contexto inválido (None)
        with pytest.raises(DataValidationError):
            query._validate_input(MetricsFilterDTO(), None)

    @pytest.mark.asyncio
    async def test_base_query_execution_with_cache(self):
        """Testa execução com cache."""
        data_source = MockMetricsDataSource()
        query = BaseMetricsQuery(data_source=data_source, cache_enabled=True)

        filter_dto = MetricsFilterDTO()
        context = QueryContext()

        # Primeira execução (cache miss)
        with patch.object(query, "_execute_query") as mock_execute:
            mock_execute.return_value = {"total": 100}

            result1 = await query.execute(filter_dto, context)
            assert mock_execute.call_count == 1

        # Segunda execução (cache hit)
        with patch.object(query, "_execute_query") as mock_execute:
            result2 = await query.execute(filter_dto, context)
            assert mock_execute.call_count == 0  # Não deve chamar novamente
            assert result1 == result2

    @pytest.mark.asyncio
    async def test_base_query_execution_without_cache(self):
        """Testa execução sem cache."""
        data_source = MockMetricsDataSource()
        query = BaseMetricsQuery(data_source=data_source, cache_enabled=False)

        filter_dto = MetricsFilterDTO()
        context = QueryContext()

        with patch.object(query, "_execute_query") as mock_execute:
            mock_execute.return_value = {"total": 100}

            # Duas execuções devem chamar o método
            await query.execute(filter_dto, context)
            await query.execute(filter_dto, context)

            assert mock_execute.call_count == 2

    def test_cache_key_generation(self):
        """Testa geração de chave de cache."""
        data_source = MockMetricsDataSource()
        query = BaseMetricsQuery(data_source=data_source)

        filter1 = MetricsFilterDTO(status=TicketStatus.NOVO)
        filter2 = MetricsFilterDTO(status=TicketStatus.PENDENTE)

        key1 = query._generate_cache_key(filter1)
        key2 = query._generate_cache_key(filter2)

        assert key1 != key2
        assert isinstance(key1, str)
        assert len(key1) > 0


class TestGeneralMetricsQuery:
    """Testes para GeneralMetricsQuery."""

    @pytest.mark.asyncio
    async def test_general_metrics_execution(self):
        """Testa execução de métricas gerais."""
        data_source = MockMetricsDataSource()
        query = GeneralMetricsQuery(data_source=data_source)

        filter_dto = MetricsFilterDTO()
        context = QueryContext()

        result = await query.execute(filter_dto, context)

        assert isinstance(result, MetricsDTO)
        assert result.total >= 0
        assert result.novos >= 0
        assert result.pendentes >= 0
        assert result.resolvidos >= 0
        assert len(result.niveis) > 0

    @pytest.mark.asyncio
    async def test_general_metrics_with_filter(self):
        """Testa métricas gerais com filtro."""
        data_source = MockMetricsDataSource()
        query = GeneralMetricsQuery(data_source=data_source)

        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()

        filter_dto = MetricsFilterDTO(start_date=start_date, end_date=end_date, status=TicketStatus.NOVO)

        context = QueryContext(user_id="test_user")

        result = await query.execute(filter_dto, context)

        assert isinstance(result, MetricsDTO)
        assert result.period_start == start_date
        assert result.period_end == end_date

    @pytest.mark.asyncio
    async def test_general_metrics_error_handling(self):
        """Testa tratamento de erros em métricas gerais."""
        # Mock data source que falha
        data_source = Mock(spec=MetricsDataSource)
        data_source.get_metrics.side_effect = Exception("Erro de conexão")

        query = GeneralMetricsQuery(data_source=data_source)
        filter_dto = MetricsFilterDTO()
        context = QueryContext()

        with pytest.raises(QueryExecutionError) as exc_info:
            await query.execute(filter_dto, context)

        assert "Erro de conexão" in str(exc_info.value.original_error)


class TestTechnicianRankingQuery:
    """Testes para TechnicianRankingQuery."""

    @pytest.mark.asyncio
    async def test_technician_ranking_execution(self):
        """Testa execução de ranking de técnicos."""
        data_source = MockMetricsDataSource()
        query = TechnicianRankingQuery(data_source=data_source)

        filter_dto = MetricsFilterDTO(limit=10)
        context = QueryContext()

        result = await query.execute(filter_dto, context)

        assert isinstance(result, list)
        assert len(result) <= 10

        if result:
            tech = result[0]
            assert isinstance(tech, TechnicianMetricsDTO)
            assert tech.id > 0
            assert len(tech.name) > 0
            assert tech.rank >= 1

    @pytest.mark.asyncio
    async def test_technician_ranking_sorting(self):
        """Testa ordenação do ranking."""
        data_source = MockMetricsDataSource()
        query = TechnicianRankingQuery(data_source=data_source)

        filter_dto = MetricsFilterDTO(limit=5)
        context = QueryContext()

        result = await query.execute(filter_dto, context)

        if len(result) > 1:
            # Verifica se está ordenado por rank
            for i in range(len(result) - 1):
                assert result[i].rank <= result[i + 1].rank

    @pytest.mark.asyncio
    async def test_technician_ranking_with_level_filter(self):
        """Testa ranking com filtro de nível."""
        data_source = MockMetricsDataSource()
        query = TechnicianRankingQuery(data_source=data_source)

        filter_dto = MetricsFilterDTO(level=TechnicianLevel.N1, limit=5)
        context = QueryContext()

        result = await query.execute(filter_dto, context)

        # Todos os técnicos devem ser N1
        for tech in result:
            assert tech.level == TechnicianLevel.N1

    @pytest.mark.asyncio
    async def test_technician_ranking_empty_result(self):
        """Testa ranking com resultado vazio."""
        # Mock que retorna lista vazia
        data_source = Mock(spec=MetricsDataSource)
        data_source.get_technicians.return_value = []

        query = TechnicianRankingQuery(data_source=data_source)
        filter_dto = MetricsFilterDTO()
        context = QueryContext()

        result = await query.execute(filter_dto, context)

        assert isinstance(result, list)
        assert len(result) == 0


class TestDashboardMetricsQuery:
    """Testes para DashboardMetricsQuery."""

    @pytest.mark.asyncio
    async def test_dashboard_metrics_execution(self):
        """Testa execução de métricas de dashboard."""
        data_source = MockMetricsDataSource()
        query = DashboardMetricsQuery(data_source=data_source)

        filter_dto = MetricsFilterDTO()
        context = QueryContext()

        result = await query.execute(filter_dto, context)

        assert isinstance(result, DashboardMetricsDTO)
        assert isinstance(result.metrics, MetricsDTO)
        assert isinstance(result.technicians, list)
        assert isinstance(result.top_performers, list)
        assert result.response_time_ms > 0

    @pytest.mark.asyncio
    async def test_dashboard_metrics_performance_tracking(self):
        """Testa rastreamento de performance do dashboard."""
        data_source = MockMetricsDataSource()
        query = DashboardMetricsQuery(data_source=data_source)

        filter_dto = MetricsFilterDTO()
        context = QueryContext()

        start_time = datetime.now()
        result = await query.execute(filter_dto, context)
        end_time = datetime.now()

        execution_time = (end_time - start_time).total_seconds() * 1000

        # O tempo de resposta deve ser razoável
        assert result.response_time_ms <= execution_time + 100  # Margem de erro
        assert result.response_time_ms > 0

    @pytest.mark.asyncio
    async def test_dashboard_metrics_top_performers(self):
        """Testa seleção de top performers."""
        data_source = MockMetricsDataSource()
        query = DashboardMetricsQuery(data_source=data_source)

        filter_dto = MetricsFilterDTO()
        context = QueryContext()

        result = await query.execute(filter_dto, context)

        # Top performers deve ser subconjunto de technicians
        assert len(result.top_performers) <= len(result.technicians)

        if result.top_performers:
            # Deve estar ordenado por performance
            for i in range(len(result.top_performers) - 1):
                current = result.top_performers[i]
                next_tech = result.top_performers[i + 1]

                # Critério: efficiency_score ou resolvidos
                current_score = current.efficiency_score or current.metrics.resolvidos
                next_score = next_tech.efficiency_score or next_tech.metrics.resolvidos

                assert current_score >= next_score

    @pytest.mark.asyncio
    async def test_dashboard_metrics_cache_behavior(self):
        """Testa comportamento de cache do dashboard."""
        data_source = MockMetricsDataSource()
        query = DashboardMetricsQuery(data_source=data_source, cache_enabled=True)

        filter_dto = MetricsFilterDTO()
        context = QueryContext()

        # Primeira execução
        result1 = await query.execute(filter_dto, context)

        # Segunda execução (deve usar cache)
        result2 = await query.execute(filter_dto, context)

        # Cache hit deve ser True na segunda execução
        assert result2.cache_hit is True
        assert result1.metrics.total == result2.metrics.total


class TestMetricsQueryFactory:
    """Testes para MetricsQueryFactory."""

    def test_factory_creation(self):
        """Testa criação da factory."""
        data_source = MockMetricsDataSource()
        factory = MetricsQueryFactory(data_source=data_source)

        assert factory.data_source == data_source
        assert factory.cache_enabled is True

    def test_create_general_metrics_query(self):
        """Testa criação de query de métricas gerais."""
        data_source = MockMetricsDataSource()
        factory = MetricsQueryFactory(data_source=data_source)

        query = factory.create_general_metrics_query()

        assert isinstance(query, GeneralMetricsQuery)
        assert query.data_source == data_source

    def test_create_technician_ranking_query(self):
        """Testa criação de query de ranking."""
        data_source = MockMetricsDataSource()
        factory = MetricsQueryFactory(data_source=data_source)

        query = factory.create_technician_ranking_query()

        assert isinstance(query, TechnicianRankingQuery)
        assert query.data_source == data_source

    def test_create_dashboard_metrics_query(self):
        """Testa criação de query de dashboard."""
        data_source = MockMetricsDataSource()
        factory = MetricsQueryFactory(data_source=data_source)

        query = factory.create_dashboard_metrics_query()

        assert isinstance(query, DashboardMetricsQuery)
        assert query.data_source == data_source

    def test_create_query_by_type(self):
        """Testa criação de query por tipo."""
        data_source = MockMetricsDataSource()
        factory = MetricsQueryFactory(data_source=data_source)

        # Teste tipos válidos
        general_query = factory.create_query("general")
        assert isinstance(general_query, GeneralMetricsQuery)

        ranking_query = factory.create_query("ranking")
        assert isinstance(ranking_query, TechnicianRankingQuery)

        dashboard_query = factory.create_query("dashboard")
        assert isinstance(dashboard_query, DashboardMetricsQuery)

    def test_create_query_invalid_type(self):
        """Testa criação de query com tipo inválido."""
        data_source = MockMetricsDataSource()
        factory = MetricsQueryFactory(data_source=data_source)

        with pytest.raises(ValueError) as exc_info:
            factory.create_query("invalid_type")

        assert "Tipo de query não suportado" in str(exc_info.value)

    def test_factory_with_custom_config(self):
        """Testa factory com configuração customizada."""
        data_source = MockMetricsDataSource()
        factory = MetricsQueryFactory(data_source=data_source, cache_enabled=False, cache_ttl=600)

        query = factory.create_general_metrics_query()

        assert query.cache_enabled is False
        assert query.cache_ttl == 600


class TestQueryIntegration:
    """Testes de integração entre queries."""

    @pytest.mark.asyncio
    async def test_complete_dashboard_flow(self):
        """Testa fluxo completo do dashboard."""
        data_source = MockMetricsDataSource()
        factory = MetricsQueryFactory(data_source=data_source)

        # Criar queries
        general_query = factory.create_general_metrics_query()
        ranking_query = factory.create_technician_ranking_query()
        dashboard_query = factory.create_dashboard_metrics_query()

        filter_dto = MetricsFilterDTO()
        context = QueryContext(user_id="integration_test")

        # Executar queries individuais
        general_metrics = await general_query.execute(filter_dto, context)
        technician_ranking = await ranking_query.execute(filter_dto, context)

        # Executar dashboard completo
        dashboard_result = await dashboard_query.execute(filter_dto, context)

        # Verificar consistência
        assert dashboard_result.metrics.total == general_metrics.total
        assert len(dashboard_result.technicians) >= len(technician_ranking)

    @pytest.mark.asyncio
    async def test_concurrent_query_execution(self):
        """Testa execução concorrente de queries."""
        data_source = MockMetricsDataSource()
        factory = MetricsQueryFactory(data_source=data_source)

        # Criar múltiplas queries
        queries = [
            factory.create_general_metrics_query(),
            factory.create_technician_ranking_query(),
            factory.create_dashboard_metrics_query(),
        ]

        filter_dto = MetricsFilterDTO()
        contexts = [QueryContext(request_id=f"req_{i}") for i in range(len(queries))]

        # Executar concorrentemente
        tasks = [query.execute(filter_dto, context) for query, context in zip(queries, contexts)]

        results = await asyncio.gather(*tasks)

        # Verificar que todas as queries retornaram resultados
        assert len(results) == 3
        assert all(result is not None for result in results)

    @pytest.mark.asyncio
    async def test_query_timeout_handling(self):
        """Testa tratamento de timeout em queries."""
        # Mock data source com delay
        data_source = Mock(spec=MetricsDataSource)

        async def slow_get_metrics(*args, **kwargs):
            await asyncio.sleep(2)  # 2 segundos de delay
            return {"total": 100}

        data_source.get_metrics = slow_get_metrics

        query = GeneralMetricsQuery(data_source=data_source)
        filter_dto = MetricsFilterDTO()
        context = QueryContext(timeout=1.0)  # Timeout de 1 segundo

        with pytest.raises(QueryExecutionError) as exc_info:
            await query.execute(filter_dto, context)

        assert "timeout" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_query_retry_mechanism(self):
        """Testa mecanismo de retry em queries."""
        # Mock data source que falha nas primeiras tentativas
        data_source = Mock(spec=MetricsDataSource)
        call_count = 0

        async def failing_get_metrics(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Falha temporária")
            return {"total": 100}

        data_source.get_metrics = failing_get_metrics

        query = GeneralMetricsQuery(data_source=data_source)
        query.max_retries = 3

        filter_dto = MetricsFilterDTO()
        context = QueryContext()

        # Deve conseguir executar após retries
        result = await query.execute(filter_dto, context)

        assert isinstance(result, MetricsDTO)
        assert call_count == 3  # Falhou 2 vezes, sucesso na 3ª
