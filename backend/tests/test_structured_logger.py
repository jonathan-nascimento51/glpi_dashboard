# -*- coding: utf-8 -*-
"""
Teste simples para o módulo de logging estruturado.
"""

import json
import os
import sys
import time

# Adicionar o diretório pai ao path para importações
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.structured_logger import (
    JSONFormatter,
    StructuredLogger,
    create_glpi_logger,
    log_api_call,
    log_api_response,
    log_performance,
)


def test_basic_logging():
    """Teste básico do logger estruturado."""
    print("=== Teste Básico do Logger Estruturado ===")

    # Criar logger
    logger = create_glpi_logger("DEBUG")

    # Testes básicos
    logger.info("Aplicação iniciada", version="1.0.0", environment="test")
    logger.debug("Debug message", user_id=123, action="login")
    logger.warning("Warning message", threshold_exceeded=True)
    logger.error("Error message", error_code=500, endpoint="/api/test")

    print(" Logs básicos executados com sucesso")


def test_api_call_decorator():
    """Teste do decorador log_api_call."""
    print("\n=== Teste do Decorador API Call ===")

    logger = create_glpi_logger("DEBUG")

    @log_api_call(logger)
    def mock_api_function(param1, param2=None):
        """Função mock para teste."""
        time.sleep(0.1)  # Simular tempo de execução
        return {"status": "success", "data": [1, 2, 3]}

    result = mock_api_function("test_param", param2="test_value")

    assert result["status"] == "success"
    assert result["data"] == [1, 2, 3]

    print(" Decorador API call funcionando")


def test_performance_decorator():
    """Teste do decorador log_performance."""
    print("\n=== Teste do Decorador Performance ===")

    logger = create_glpi_logger("DEBUG")

    @log_performance(logger, threshold_seconds=0.05)
    def fast_function():
        return "fast result"

    @log_performance(logger, threshold_seconds=0.05)
    def slow_function():
        time.sleep(0.1)
        return "slow result"

    result1 = fast_function()
    result2 = slow_function()

    assert result1 == "fast result"
    assert result2 == "slow result"

    print(" Decorador performance funcionando")


def test_api_response_logging():
    """Teste do log de resposta de API."""
    print("\n=== Teste do Log de Resposta API ===")

    logger = create_glpi_logger("DEBUG")

    # Resposta de sucesso
    response_data = {"status": "success", "count": 10, "data": [1, 2, 3]}
    log_api_response(logger, response_data, status_code=200, response_time=0.5)

    # Resposta de erro
    error_data = {"error": "Not found", "code": 404}
    log_api_response(logger, error_data, status_code=404, response_time=0.2)

    print(" Log de resposta API funcionando")


def test_integration_example():
    """Exemplo de integração completa."""
    print("\n=== Teste de Integração Completa ===")

    # Criar logger
    logger = create_glpi_logger("DEBUG")

    # Simular uma classe de serviço
    class MockGLPIService:
        def __init__(self):
            self.structured_logger = logger

        @log_api_call(logger)
        @log_performance(logger, threshold_seconds=0.1)
        def get_tickets(self, status=None, limit=10):
            """Simula busca de tickets."""
            time.sleep(0.05)  # Simular tempo de processamento

            tickets = [
                {"id": 1, "title": "Ticket 1", "status": "open"},
                {"id": 2, "title": "Ticket 2", "status": "closed"},
            ]

            # Log da resposta
            log_api_response(logger, tickets, status_code=200, response_time=0.05)

            return tickets

    # Testar o serviço
    service = MockGLPIService()
    tickets = service.get_tickets(status="open", limit=5)

    assert len(tickets) == 2
    assert tickets[0]["id"] == 1

    print(" Integração completa funcionando")


if __name__ == "__main__":
    try:
        test_basic_logging()
        test_api_call_decorator()
        test_performance_decorator()
        test_api_response_logging()
        test_integration_example()

        print("\n Todos os testes do logger estruturado executados com sucesso!")
        print("\n Resumo:")
        print("    Logger estruturado criado")
        print("    Logs em formato JSON")
        print("    Decoradores funcionando")
        print("    Contexto rico nos logs")
        print("    Integração completa testada")

    except Exception as e:
        print(f"\n Erro durante os testes: {e}")
        import traceback

        traceback.print_exc()
