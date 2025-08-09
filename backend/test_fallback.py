#!/usr/bin/env python3
"""
Teste simples para verificar o tratamento de erro com fallback gracioso
no método get_ticket_count do GLPIService.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from unittest.mock import Mock, patch
from services.glpi_service import GLPIService


def test_fallback_gracioso():
    """Testa se o método get_ticket_count retorna 0 em casos de erro"""
    print("Testando tratamento de erro com fallback gracioso...")

    # Configurar o serviço (usa configurações do active_config)
    service = GLPIService()

    # Teste 1: Falha na descoberta de field_ids
    print("\n1. Testando falha na descoberta de field_ids...")
    service.field_ids = {}
    with patch.object(service, "discover_field_ids", return_value=False):
        result = service.get_ticket_count(group_id=89, status_id=1)
        assert result == 0, f"Esperado 0, obtido {result}"
        print("✓ Retornou 0 quando field_ids falhou")

    # Teste 2: Resposta vazia da API
    print("\n2. Testando resposta vazia da API...")
    service.field_ids = {"GROUP": "8", "STATUS": "12"}
    with patch.object(service, "_make_authenticated_request", return_value=None):
        result = service.get_ticket_count(group_id=89, status_id=1)
        assert result == 0, f"Esperado 0, obtido {result}"
        print("✓ Retornou 0 quando API retornou resposta vazia")

    # Teste 3: Status code diferente de 200
    print("\n3. Testando status code diferente de 200...")
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.headers = {}

    with patch.object(
        service, "_make_authenticated_request", return_value=mock_response
    ):
        result = service.get_ticket_count(group_id=89, status_id=1)
        assert result == 0, f"Esperado 0, obtido {result}"
        print("✓ Retornou 0 quando API retornou status 500")

    # Teste 4: Exceção durante a requisição
    print("\n4. Testando exceção durante a requisição...")
    with patch.object(
        service, "_make_authenticated_request", side_effect=Exception("Erro de rede")
    ):
        result = service.get_ticket_count(group_id=89, status_id=1)
        assert result == 0, f"Esperado 0, obtido {result}"
        print("✓ Retornou 0 quando ocorreu exceção")

    # Teste 5: Sucesso com Content-Range
    print("\n5. Testando sucesso com Content-Range...")
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Range": "tickets 0-0/42"}

    with patch.object(
        service, "_make_authenticated_request", return_value=mock_response
    ):
        result = service.get_ticket_count(group_id=89, status_id=1)
        assert result == 42, f"Esperado 42, obtido {result}"
        print("✓ Retornou 42 quando API funcionou corretamente")

    # Teste 6: Status 200 sem Content-Range
    print("\n6. Testando status 200 sem Content-Range...")
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {}

    with patch.object(
        service, "_make_authenticated_request", return_value=mock_response
    ):
        result = service.get_ticket_count(group_id=89, status_id=1)
        assert result == 0, f"Esperado 0, obtido {result}"
        print("✓ Retornou 0 quando status 200 mas sem Content-Range")

    print("\n🎉 Todos os testes de fallback gracioso passaram!")
    print("\n📝 Resumo da implementação:")
    print("   - Retorna 0 em vez de None em todos os casos de erro")
    print("   - Logs detalhados com timestamp incluem contexto da chamada")
    print("   - Assinatura pública do método mantida inalterada")
    print("   - Tratamento específico para diferentes tipos de erro")


if __name__ == "__main__":
    test_fallback_gracioso()
