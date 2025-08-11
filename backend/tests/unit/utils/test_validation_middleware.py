import pytest
import json
from unittest.mock import Mock, AsyncMock
from fastapi import Request
from fastapi.responses import JSONResponse, Response
from utils.validation_middleware import ValidationMiddleware


class TestValidationMiddleware:
    @pytest.fixture
    def middleware(self):
        """Fixture para criar instancia do middleware"""
        return ValidationMiddleware()

    @pytest.fixture
    def mock_request(self):
        """Fixture para requisicao mockada"""
        request = Mock(spec=Request)
        request.url.path = "/api/metrics"
        request.method = "GET"
        return request

    @pytest.fixture
    def valid_metrics_response(self):
        """Fixture para resposta de metricas valida"""
        return {
            "success": True,
            "data": {
                "niveis": {
                    "N1": {"total": 10, "resolvidos": 8, "pendentes": 2, "tempo_medio": 2.5},
                    "N2": {"total": 5, "resolvidos": 4, "pendentes": 1, "tempo_medio": 4.0},
                    "N3": {"total": 2, "resolvidos": 1, "pendentes": 1, "tempo_medio": 8.0}
                },
                "total_tickets": 17,
                "tickets_resolvidos": 13,
                "tickets_pendentes": 4,
                "tempo_medio_resolucao": 3.5,
                "satisfacao_cliente": 4.2
            }
        }

    @pytest.mark.asyncio
    async def test_valid_metrics_response_passes_through(self, middleware, mock_request, valid_metrics_response):
        """Testa que uma resposta de metricas valida passa sem modificacao"""
        # Mock da funcao call_next
        async def mock_call_next(request):
            response = JSONResponse(content=valid_metrics_response)
            return response

        # Executa o middleware
        result = await middleware(mock_request, mock_call_next)

        # Verifica que a resposta passou sem modificacao
        assert result.status_code == 200
        response_data = json.loads(result.body)
        assert response_data == valid_metrics_response

    @pytest.mark.asyncio
    async def test_non_api_endpoint_passes_through(self, middleware):
        """Testa que endpoints nao-API passam sem validacao"""
        request = Mock(spec=Request)
        request.url.path = "/docs"
        request.method = "GET"

        async def mock_call_next(request):
            return Response(content="Documentation", status_code=200)

        result = await middleware(request, mock_call_next)
        assert result.status_code == 200

    @pytest.mark.asyncio
    async def test_post_request_passes_through(self, middleware):
        """Testa que requisicoes POST passam sem validacao"""
        request = Mock(spec=Request)
        request.url.path = "/api/tickets"
        request.method = "POST"

        async def mock_call_next(request):
            return JSONResponse(content={"id": 1, "status": "created"}, status_code=201)

        result = await middleware(request, mock_call_next)
        assert result.status_code == 201

    def test_get_fallback_data_metrics(self, middleware):
        """Testa geracao de dados de fallback para metricas"""
        fallback = middleware._get_fallback_data("/api/metrics")
        assert fallback["success"] == True
        assert "data" in fallback
        assert "niveis" in fallback["data"]
        assert "N1" in fallback["data"]["niveis"]
        assert fallback["data"]["total_tickets"] >= 0

    def test_get_fallback_data_unknown_endpoint(self, middleware):
        """Testa fallback para endpoint desconhecido"""
        fallback = middleware._get_fallback_data("/api/unknown")
        assert fallback["success"] == False
        assert "Dados" in fallback["message"]
        assert fallback["data"] is None

    def test_get_fallback_data_ranking(self, middleware):
        """Testa geracao de dados de fallback para ranking"""
        fallback = middleware._get_fallback_data("/api/ranking")
        assert fallback["success"] == True
        assert "data" in fallback
        assert isinstance(fallback["data"], list)

    def test_get_fallback_data_status(self, middleware):
        """Testa geracao de dados de fallback para status"""
        fallback = middleware._get_fallback_data("/api/status")
        assert fallback["success"] == True
        assert "data" in fallback
        assert "api_status" in fallback["data"]

    def test_validation_stats_initialization(self, middleware):
        """Testa inicializacao das estatisticas de validacao"""
        stats = middleware.get_validation_stats()
        assert "total_requests" in stats
        assert "validation_successes" in stats
        assert "validation_errors" in stats
        assert "fallback_used" in stats
